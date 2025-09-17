#!/usr/bin/env python3
"""
Agent State & Intent Audit

Generates a reproducible snapshot of the current environment, toolchain, and
repository status to `.agent_workdir/agent_audit_YYYYMMDD.yaml` and writes the
provided strategic pivot JSONL directive to `.agent_workdir/directives/`.

This script uses only the Python standard library.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
import platform
import shutil
import subprocess
from typing import Dict, List, Tuple


def run(
    cmd: List[str], cwd: Path | None = None, timeout: int = 15
) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return 127, "", "not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def which_version(cmd: List[str], parse: str = "stdout") -> Dict[str, str | bool]:
    bin_name = cmd[0]
    path = shutil.which(bin_name)
    if not path:
        return {"present": False, "version": "", "path": ""}
    code, out, err = run(cmd)
    src = out if parse == "stdout" else err
    # Normalize first line only; many tools print multiple lines
    version_line = (src.splitlines() or [""])[0]
    return {"present": True, "version": version_line, "path": path}


def gather_repo_info(root: Path) -> Dict[str, str | int]:
    info: Dict[str, str | int] = {}
    code, top, _ = run(["git", "rev-parse", "--show-toplevel"], cwd=root)
    if code != 0:
        return {"git": "not a git repo"}
    info["toplevel"] = top
    code, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root)
    info["branch"] = branch
    code, commit, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd=root)
    info["commit"] = commit
    code, remote, _ = run(["git", "remote", "get-url", "origin"], cwd=root)
    info["remote_origin"] = remote
    code, stat, _ = run(["git", "status", "--porcelain"], cwd=root)
    lines = [ln for ln in stat.splitlines() if ln.strip()]
    info["changes_count"] = len(lines)
    info["is_clean"] = len(lines) == 0
    return info


def file_counts(root: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    # Prefer ripgrep if available
    if shutil.which("rg"):
        code, out, _ = run(
            ["rg", "--files", "--hidden", "--glob", "!**/.git/**"], cwd=root
        )
        files = out.splitlines() if code == 0 else []
        counts["files_total"] = len(files)
    else:
        files = [
            str(p) for p in root.rglob("*") if p.is_file() and ".git" not in str(p)
        ]
        counts["files_total"] = len(files)
    counts["adrs"] = len(list((root / "docs/adr").glob("[0-9][0-9][0-9][0-9]-*.md")))
    return counts


def gather_os_info() -> Dict[str, str]:
    info: Dict[str, str] = {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "python": platform.python_version(),
    }
    code, sw, _ = run(["sw_vers"], cwd=None)
    if code == 0 and sw:
        info["sw_vers"] = sw
    code, un, _ = run(["uname", "-a"], cwd=None)
    if code == 0:
        info["uname"] = un
    return info


def gather_tools() -> Dict[str, Dict[str, str | bool]]:
    checks = {
        "git": (["git", "--version"], "stdout"),
        "just": (["just", "--version"], "stdout"),
        "nox": (["nox", "--version"], "stdout"),
        "copier": (["copier", "--version"], "stdout"),
        "jq": (["jq", "--version"], "stdout"),
        "yq": (["yq", "--version"], "stdout"),
        "pre-commit": (["pre-commit", "--version"], "stdout"),
        "ruff": (["ruff", "--version"], "stdout"),
        "black": (["black", "--version"], "stdout"),
        "pytest": (["pytest", "--version"], "stdout"),
        "tox": (["tox", "--version"], "stdout"),
        "poetry": (["poetry", "--version"], "stdout"),
        "uv": (["uv", "--version"], "stdout"),
        "hatch": (["hatch", "--version"], "stdout"),
        "pipx": (["pipx", "--version"], "stdout"),
        "pip": (["pip", "--version"], "stdout"),
        "python3": (["python3", "--version"], "stdout"),
        "rg": (["rg", "--version"], "stdout"),
        "node": (["node", "-v"], "stdout"),
        "npm": (["npm", "-v"], "stdout"),
        "pnpm": (["pnpm", "-v"], "stdout"),
        "bun": (["bun", "--version"], "stdout"),
        "go": (["go", "version"], "stdout"),
        "rustc": (["rustc", "--version"], "stdout"),
        "cargo": (["cargo", "--version"], "stdout"),
        "java": (["java", "-version"], "stderr"),
        "ruby": (["ruby", "-v"], "stdout"),
    }
    return {name: which_version(cmd, parse) for name, (cmd, parse) in checks.items()}


def read_text(path: Path, max_chars: int = 4000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + "\n... [truncated]"
        return text
    except FileNotFoundError:
        return ""


def write_audit_yaml(out_path: Path, data: Dict[str, object]) -> None:
    # Minimal YAML writer for our structured dict; avoid external deps
    def dump_scalar(val: object) -> str:
        if val is True:
            return "true"
        if val is False:
            return "false"
        if val is None:
            return "null"
        s = str(val)
        if any(ch in s for ch in ":#\n\"'{}[]") or s.strip() == "" or s.strip() != s:
            # Quote and escape
            return json.dumps(s)
        return s

    def dump_block(text: str, indent: int = 2) -> str:
        pad = " " * indent
        lines = text.splitlines() or [""]
        return "|\n" + "\n".join(pad + ln for ln in lines)

    lines: List[str] = []
    lines.append("audit_version: 1")
    lines.append(f"timestamp_utc: {dump_scalar(data['timestamp_utc'])}")
    lines.append(f"workspace_root: {dump_scalar(data['workspace_root'])}")
    lines.append(f"chat_title_protocol: {dump_scalar(data['chat_title_protocol'])}")
    # OS
    lines.append("os:")
    for k, v in data["os"].items():
        if k in ("sw_vers", "uname") and v:
            lines.append(f"  {k}: {dump_block(v, indent=4)[1:]}")
        else:
            lines.append(f"  {k}: {dump_scalar(v)}")
    # Repo
    lines.append("repo:")
    for k, v in data["repo"].items():
        lines.append(f"  {k}: {dump_scalar(v)}")
    # Files
    lines.append("files:")
    for k, v in data["files"].items():
        lines.append(f"  {k}: {dump_scalar(v)}")
    # Tools
    lines.append("tools:")
    for name, meta in sorted(data["tools"].items()):
        lines.append(f"  {name}:")
        for mk in ("present", "version", "path"):
            mv = meta.get(mk, "")
            lines.append(f"    {mk}: {dump_scalar(mv)}")
    # Just list
    lines.append("just_tasks:")
    lines.append("  list:" + ("" if data["just_list"] else " []"))
    if data["just_list"]:
        lines.append(dump_block(data["just_list"], indent=4))
    # State manifest snapshot
    sms = data.get("state_manifest_snapshot", "")
    lines.append("state_manifest_snapshot:")
    if sms:
        lines.append(dump_block(sms, indent=2))
    else:
        lines.append("  null")
    # Intent notes
    lines.append("intent:")
    lines.append(f"  phase: {dump_scalar(data['intent']['phase'])}")
    lines.append(f"  notes: {dump_block(data['intent']['notes'], indent=4)[1:]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_directive_jsonl(out_path: Path) -> None:
    # Content provided by user; preserve wording exactly
    content_markdown = (
        "A strategic review has revealed that our interaction model has been inefficient. "
        "We will now pivot to a new strategy that leverages your built-in capabilities. "
        "This message contains the new three-phase plan.\n\n---\n\n## The Strategic Pivot: Leverage, Don't Re-Invent\n\n"
        "Our new strategy is to maximize the use of your native features, such as `@workspace`, "
        "`@terminal`, and slash commands (`/fix`), to provide you with context and execute tasks. "
        "We will no longer build custom solutions for problems that your core tooling already solves.\n\n"
        "## The New Three-Phase Plan\n\n"
        "1.  **Phase 1 (Audit):** Your immediate task is to perform the 'Agent State & Intent Audit' to establish a clean baseline.\n"
        "2.  **Phase 2 (Optimize):** We will develop and codify new protocols for using your built-in features.\n"
        "3.  **Phase 3 (Re-evaluate):** We will review our existing custom framework and simplify it based on these new capabilities.\n\n"
        "## Your Immediate Task\n\n"
        "Execute **Phase 1** of the new plan. You are to immediately perform the **'Agent State & Intent Audit'** as defined in our previous discussions. This is your only active task."
    )
    payload_yaml = (
        "new_stories:\n"
        "  - id: STORY-1006\n"
        "    epic_id: EPIC-10 # Reflexive Governance\n"
        "    title: 'ADR: Optimal Usage of VS Code AI Agent Features'\n"
        "    narrative: As a framework architect, I want to define and document the standard operating procedures for using the agent's built-in context features (@workspace, @terminal) and commands (/fix) so that our interactions are efficient and reliable.\n"
        "    priority: P0\n"
        "  - id: STORY-1007\n"
        "    epic_id: EPIC-10 # Reflexive Governance\n"
        "    title: Re-evaluate Custom Agent Framework Against Native Capabilities\n"
        "    narrative: As a founder, I want to critically review our custom-built agent solutions (State Manifest, Sentinel Loop) and identify opportunities for simplification or replacement by leveraging the agent's native features, so that we reduce maintenance overhead and complexity.\n"
        "    priority: P1\n"
    )
    obj = {
        "content_markdown": content_markdown,
        "status": "SUCCESS_WITH_ACTION_REQUIRED",
        "action": "initiate_strategic_pivot",
        "payload_type": "yaml",
        "payload": payload_yaml,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        # JSONL: one JSON object per line
        json.dump(obj, f, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    today = _dt.datetime.utcnow().strftime("%Y-%m-%d")

    # Gather data
    os_info = gather_os_info()
    repo_info = gather_repo_info(repo_root)
    counts = file_counts(repo_root)
    tools = gather_tools()
    code, just_list, _ = run(["just", "--list"], cwd=repo_root)
    # Read optional state manifest
    sm_path = repo_root / ".agent_workdir/state_manifest.yaml"
    sm_text = read_text(sm_path) if sm_path.exists() else ""

    audit = {
        "timestamp_utc": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "workspace_root": str(repo_root),
        "chat_title_protocol": "YYYY-MM-DD | Agent Task: <WI-ID> - <Brief Description>",
        "os": os_info,
        "repo": repo_info,
        "files": counts,
        "tools": tools,
        "just_list": just_list if code == 0 else "",
        "state_manifest_snapshot": sm_text,
        "intent": {
            "phase": "Phase 1: Agent State & Intent Audit",
            "notes": (
                "Pivot acknowledged. Establishing a clean baseline of environment, tooling, "
                "and repo state before codifying usage patterns (Phase 2) and rationalizing the "
                "custom framework (Phase 3)."
            ),
        },
    }

    # Write audit YAML
    audit_out = repo_root / ".agent_workdir" / f"agent_audit_{today}.yaml"
    write_audit_yaml(audit_out, audit)

    # Persist directive JSONL for new sessions
    dir_out = (
        repo_root
        / ".agent_workdir"
        / "directives"
        / f"{today}_initiate_strategic_pivot.jsonl"
    )
    write_directive_jsonl(dir_out)

    print(f"Wrote audit: {audit_out}")
    print(f"Wrote directive: {dir_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
