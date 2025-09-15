#!/usr/bin/env python3

"""
Render Jinja2 templates into an output directory.

Defaults to the repo's template directory:
  src/project_vo2_scaffolder/data_files/templates

Usage examples:
  python3 render.py --context copier-defaults.yaml
  python3 render.py --context context.json --out-dir ./build --strict

Requires: jinja2. For YAML contexts, requires PyYAML. JSON works with stdlib.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


def fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_context(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text) or {}
    except ModuleNotFoundError as e:
        fail(
            "PyYAML is required for non-JSON contexts. Install with: pip install pyyaml\n"
            f"Tried to load: {path}"
        )


@dataclass
class Options:
    in_dir: Path
    out_dir: Path
    context: Path
    strict: bool
    dry_run: bool
    overwrite: bool


def discover_templates(in_dir: Path) -> list[Path]:
    return sorted(p for p in in_dir.rglob("*") if p.is_file() and p.suffix == ".j2")


def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def render_all(opts: Options) -> int:
    try:
        from jinja2 import (
            Environment,
            FileSystemLoader,
            StrictUndefined,
            Undefined,
            select_autoescape,
        )
    except ModuleNotFoundError:
        fail("Jinja2 is required. Install with: pip install jinja2")

    # Enable autoescape only for HTML/XML-like outputs to mitigate XSS issues.
    # Markdown/text templates render without autoescape by default.
    env = Environment(
        loader=FileSystemLoader(str(opts.in_dir)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "htm", "xml", "xhtml"),
            default_for_string=False,
        ),
        undefined=StrictUndefined if opts.strict else Undefined,
        keep_trailing_newline=True,
        lstrip_blocks=False,
        trim_blocks=False,
    )

    ctx = load_context(opts.context)
    total = 0
    for tpl_path in discover_templates(opts.in_dir):
        rel = tpl_path.relative_to(opts.in_dir)
        out_rel = rel.with_suffix("")  # drop .j2 suffix
        dest = opts.out_dir / out_rel

        if not opts.overwrite and dest.exists():
            print(f"[INFO] Skip existing: {dest}")
            continue

        if opts.dry_run:
            print(f"[DRY] Would render {rel} -> {dest}")
            total += 1
            continue

        tmpl = env.get_template(str(rel))
        rendered = tmpl.render(**ctx)
        ensure_parent(dest)
        dest.write_text(rendered, encoding="utf-8")
        print(f"[OK] {rel} -> {dest}")
        total += 1
    return total


def default_in_dir() -> Path:
    here = Path(__file__).resolve().parent
    return here / "src" / "project_vo2_scaffolder" / "data_files" / "templates"


def parse_args(argv: list[str]) -> Options:
    parser = argparse.ArgumentParser(description="Render .j2 templates with a context")
    parser.add_argument(
        "--in-dir",
        type=Path,
        default=default_in_dir(),
        help="Template directory (default: repo data_files/templates)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--context",
        type=Path,
        required=True,
        help="Context file (YAML or JSON)",
    )
    parser.add_argument("--strict", action="store_true", help="Fail on undefined variables")
    parser.add_argument("--dry-run", action="store_true", help="List actions without writing files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")

    args = parser.parse_args(argv)
    return Options(
        in_dir=args.in_dir,
        out_dir=args.out_dir,
        context=args.context,
        strict=args.strict,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )


def main() -> None:
    opts = parse_args(sys.argv[1:])
    if not opts.in_dir.exists():
        fail(f"Template directory not found: {opts.in_dir}")
    if not opts.context.exists():
        fail(f"Context file not found: {opts.context}")
    count = render_all(opts)
    print(f"[SUCCESS] Rendered {count} templates")


if __name__ == "__main__":
    main()
