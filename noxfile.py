"""
Minimal nox sessions for Project VO2 scaffolder.

Requires: nox (pipx install nox)
Run: nox -s validate_manifest
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import nox
import hashlib


ROOT = Path(__file__).resolve().parent
DB = ROOT / "file_contents.jsonl"


@nox.session
def validate_manifest(session: nox.Session) -> None:
    """Validate JSONL entries and base64 contents.

    Checks:
    - Each line is valid JSON with required keys: path, content
    - Optional encoding == "base64" decodes without error
    - Paths are relative, normalized, and cannot escape the workspace
    """

    if not DB.exists():
        session.error(f"Missing manifest: {DB}")

    # No deps needed; pure-stdlib validation
    total = 0
    with DB.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception as exc:  # noqa: BLE001
                session.error(f"Invalid JSON on line {i}: {exc}")

            for k in ("path", "content"):
                if k not in obj:
                    session.error(f"Line {i}: missing required key '{k}'")

            path_str = obj["path"]
            if not isinstance(path_str, str) or not path_str:
                session.error(f"Line {i}: invalid path")

            # Path safety: must be relative and normalized within repo
            p = Path(path_str)
            if p.is_absolute() or ".." in p.parts:
                session.error(f"Line {i}: unsafe path '{path_str}'")

            content = obj["content"]
            if obj.get("encoding") == "base64":
                try:
                    decoded = base64.b64decode(content)
                except Exception as exc:  # noqa: BLE001
                    session.error(f"Line {i}: invalid base64 content: {exc}")
            else:
                if not isinstance(content, str):
                    session.error(
                        f"Line {i}: content must be a string when not base64-encoded"
                    )
                decoded = content.encode("utf-8")

            # Optional integrity fields
            if "size_bytes" in obj:
                try:
                    size = int(obj["size_bytes"])
                except Exception:  # noqa: BLE001
                    session.error(f"Line {i}: size_bytes must be an integer")
                if size != len(decoded):
                    session.error(
                        f"Line {i}: size_bytes mismatch (expected {size}, got {len(decoded)})"
                    )
            if "sha256" in obj:
                expect = str(obj["sha256"]).lower()
                got = hashlib.sha256(decoded).hexdigest()
                if expect != got:
                    session.error(
                        f"Line {i}: sha256 mismatch (expected {expect}, got {got})"
                    )

            # Optional mode/executable sanity
            if "mode" in obj:
                m = str(obj["mode"]).strip()
                if not m or any(ch not in "01234567" for ch in m) or len(m) not in (3, 4):
                    session.error(f"Line {i}: invalid mode '{obj['mode']}' (expect octal like 0644)")
                # Check exec flag consistency if provided
                if "executable" in obj and isinstance(obj["executable"], bool):
                    perm = int(m if len(m) == 4 else "0" + m, 8)
                    exec_bit = bool(perm & 0o111)
                    if exec_bit != obj["executable"]:
                        session.error(
                            f"Line {i}: executable flag inconsistent with mode {m}"
                        )

            total += 1

    session.log(f"Validated {total} manifest entries: OK")
