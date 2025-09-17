#!/usr/bin/env python3

"""
@project: Project VO2 Bootstrapper
@file:    02-populate-files.py
@brief:   Reads file_contents.jsonl and writes files to the scaffold tree.

This script expects a JSON Lines file named file_contents.jsonl located
in the same directory as this script. Each line is a JSON object with:
  { "path": "relative/path/to/file", "content": "file contents" }
"""

from __future__ import annotations

import ast
import base64
import hashlib
import json
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "file_contents.jsonl"


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def success(msg: str) -> None:
    print(f"[SUCCESS] {msg}")


def error(msg: str) -> None:
    raise SystemExit(f"[ERROR] {msg}")


@dataclass
class FileEntry:
    path: Path
    content: str
    sha256: str | None = None
    size_bytes: int | None = None
    mode: str | None = None
    executable: bool | None = None
    mime_type: str | None = None
    schema_version: int | None = None

    @staticmethod
    def from_json(obj: dict) -> "FileEntry":
        if not isinstance(obj, dict):
            raise ValueError("Invalid entry; expected JSON object")
        if "path" not in obj or "content" not in obj:
            raise ValueError("Entry missing required keys: 'path' and 'content'")
        content: str
        if obj.get("encoding") == "base64":
            try:
                content = base64.b64decode(obj["content"]).decode("utf-8")
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"Invalid base64 content: {exc}")
        else:
            content = str(obj["content"])
        return FileEntry(
            path=Path(obj["path"]),
            content=content,
            sha256=obj.get("sha256"),
            size_bytes=obj.get("size_bytes"),
            mode=obj.get("mode"),
            executable=obj.get("executable"),
            mime_type=obj.get("mime_type"),
            schema_version=obj.get("schema_version"),
        )


def _parse_line_forgiving(raw: str) -> FileEntry:
    # Fallback parser for over-escaped JSONL produced by heredoc.
    # Extract path via regex and content via string slicing to the last "}".
    m = re.search(r'"path"\s*:\s*"([^"]*)"', raw)
    if not m:
        error("Entry missing 'path' key")
    path = m.group(1)
    k = re.search(r'"content"\s*:\s*"', raw)
    if not k:
        error("Entry missing 'content' key")
    start = k.end()
    # Walk forward to find the matching, unescaped closing quote of the content string.
    end = None
    j = start
    while j < len(raw):
        ch = raw[j]
        if ch == '"':
            # Count number of consecutive backslashes immediately before j
            b = 0
            k2 = j - 1
            while k2 >= start and raw[k2] == "\\":
                b += 1
                k2 -= 1
            if b % 2 == 0:  # even -> quote is not escaped
                end = j
                break
        j += 1
    if end is None:
        error("Could not locate end of content string")
    content_escaped = raw[start:end]
    # Interpret common escapes by evaluating as a Python string literal.
    try:
        content = ast.literal_eval('"' + content_escaped + '"')
    except Exception:
        # As a last resort, replace escaped newlines and tabs manually.
        content = (
            content_escaped.replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace("\\r", "\r")
        )
    # Remove stray backslashes that precede quotes introduced by over-escaping.
    content = content.replace('"', '"')
    return FileEntry(path=Path(path), content=content)


def read_entries(lines: Iterable[str]) -> list[FileEntry]:
    entries: list[FileEntry] = []
    for i, raw in enumerate(lines, start=1):
        s = raw.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
            entries.append(FileEntry.from_json(obj))
        except Exception:
            # Fallback to forgiving parser for legacy/over-escaped lines.
            try:
                entries.append(_parse_line_forgiving(s))
            except Exception as exc:  # noqa: BLE001
                error(f"Invalid entry on line {i}: {exc}")
    return entries


def ensure_parent(path: Path) -> None:
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def apply_mode(path: Path, entry: FileEntry) -> None:
    # If mode is specified, apply it; otherwise default to making scripts executable.
    if entry.mode:
        try:
            m = entry.mode
            if isinstance(m, str):
                # Accept 3 or 4-digit octal strings
                if len(m) == 3:
                    m = "0" + m
                path.chmod(int(m, 8))
            else:
                # Unexpected type; ignore
                return
        except (OSError, ValueError):
            # Ignore mode errors but proceed
            return
    else:
        if path.suffix == ".sh" or entry.content.startswith("#!"):
            try:
                mode = path.stat().st_mode
                path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except FileNotFoundError:
                return


def within_dir(root: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def write_files(entries: list[FileEntry]) -> int:
    count = 0
    cwd = Path.cwd()
    for entry in entries:
        # Path safety checks
        if entry.path.is_absolute() or any(part == ".." for part in entry.path.parts):
            error(f"Unsafe path: {entry.path}")
        dest = entry.path
        if not within_dir(cwd, cwd / dest):
            error(f"Path escapes workspace: {dest}")

        # Integrity checks
        content_bytes = entry.content.encode("utf-8")
        if entry.size_bytes is not None and entry.size_bytes != len(content_bytes):
            error(
                f"Size mismatch for {dest}: expected {entry.size_bytes}, got {len(content_bytes)}"
            )
        if entry.sha256 is not None:
            digest = hashlib.sha256(content_bytes).hexdigest()
            if digest != entry.sha256:
                error(
                    f"SHA256 mismatch for {dest}: expected {entry.sha256}, got {digest}"
                )

        ensure_parent(dest)
        # Write exactly as provided; do not add extra newline unless present.
        dest.write_text(entry.content, encoding="utf-8")
        apply_mode(dest, entry)
        info(f"Wrote: {dest}")
        count += 1
    return count


def main() -> None:
    info("Populating files from file_contents.jsonl...")
    if not DB_PATH.exists():
        error(f"Database not found: {DB_PATH}")
    with DB_PATH.open("r", encoding="utf-8") as f:
        entries = read_entries(f)
    total = write_files(entries)
    success(f"Populated {total} files.")


if __name__ == "__main__":
    main()
