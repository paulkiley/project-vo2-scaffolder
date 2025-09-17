#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
W_BACKLOG = ROOT / ".work" / "backlog.yaml"
W_DECISIONS = ROOT / ".work" / "decisions.yaml"
S_BACKLOG = ROOT / ".work" / "schema" / "backlog.schema.json"
S_DECISIONS = ROOT / ".work" / "schema" / "decisions.schema.json"


def load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def cmd_list(_: argparse.Namespace) -> None:
    data = load_yaml(W_BACKLOG)
    for wi in data.get("work_items", []):
        print(
            f"{wi['id']}\t{wi.get('priority','')}\t{wi.get('status','')}\t{wi['title']}"
        )


def cmd_show(args: argparse.Namespace) -> None:
    data = load_yaml(W_BACKLOG)
    found = next((w for w in data.get("work_items", []) if w["id"] == args.id), None)
    print(yaml.safe_dump(found or {"error": "not found"}, sort_keys=False))


def validate_one(doc: dict, schema: dict) -> list[str]:
    try:
        import jsonschema
    except Exception:
        return ["jsonschema not installed; pip install jsonschema pyyaml"]
    try:
        jsonschema.validate(doc, schema)
        return []
    except Exception as e:
        return [str(e)]


def cmd_validate(_: argparse.Namespace) -> None:
    errs: list[str] = []
    bl = load_yaml(W_BACKLOG)
    dc = load_yaml(W_DECISIONS)
    sbl = json.loads(S_BACKLOG.read_text(encoding="utf-8"))
    sdc = json.loads(S_DECISIONS.read_text(encoding="utf-8"))
    errs += validate_one(bl, sbl)
    errs += validate_one(dc, sdc)
    if errs:
        print("Validation failed:")
        for e in errs:
            print(" -", e)
        raise SystemExit(1)
    print("Validation OK")


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(required=True)

    s1 = sub.add_parser("list")
    s1.set_defaults(func=cmd_list)

    s2 = sub.add_parser("show")
    s2.add_argument("id")
    s2.set_defaults(func=cmd_show)

    s3 = sub.add_parser("validate")
    s3.set_defaults(func=cmd_validate)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
