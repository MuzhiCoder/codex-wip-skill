#!/usr/bin/env python3
"""Validate a repository-local .codex/wip checkpoint.

Standard library only. It reports checkpoint drift but never modifies the repo.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


REQUIRED_SECTIONS = [
    "# WIP",
    "## Snapshot",
    "## Original Goal",
    "## Confirmed Decisions",
    "## Changed Areas",
    "## Tests and Verification",
    "## Exact Next Actions",
]


def run_git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout.strip()


def load_snapshot_module():
    script = Path(__file__).with_name("wip_snapshot.py")
    spec = importlib.util.spec_from_file_location("wip_snapshot_for_validate", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load wip_snapshot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()

    try:
        repo = Path(run_git(Path(args.repo), "rev-parse", "--show-toplevel")).resolve()
        wip_dir = repo / ".codex" / "wip"
        state_path = wip_dir / "state.json"
        current_path = wip_dir / "current.md"

        errors: list[str] = []
        warnings: list[str] = []

        if not state_path.exists():
            errors.append("missing .codex/wip/state.json")
            state = {}
        else:
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"invalid state.json: {exc}")
                state = {}

        for key in [
            "schema_version",
            "captured_at",
            "repository_root",
            "branch",
            "head",
            "worktree_fingerprint",
            "paths",
        ]:
            if state and key not in state:
                errors.append(f"state.json missing key: {key}")

        if not current_path.exists():
            errors.append("missing .codex/wip/current.md")
            current = ""
        else:
            current = current_path.read_text(encoding="utf-8", errors="replace")
            if "recovery pending" in current.lower():
                errors.append("current.md is still the generated placeholder")

        for section in REQUIRED_SECTIONS:
            if current and section not in current:
                errors.append(f"current.md missing section: {section}")

        forbidden_markers = [
            "GITHUB_PERSONAL_ACCESS_TOKEN=",
            "OPENAI_API_KEY=",
            "MYSQL_PASSWORD=",
            "Authorization: Bearer ",
        ]
        for marker in forbidden_markers:
            if marker in current:
                errors.append(f"current.md may contain a secret marker: {marker}")

        if state:
            snapshot = load_snapshot_module().collect(str(repo))
            if state.get("branch") != snapshot.get("branch"):
                warnings.append(
                    f"checkpoint branch drift: saved={state.get('branch')} current={snapshot.get('branch')}"
                )
            if state.get("head") != snapshot.get("head"):
                warnings.append(
                    f"checkpoint HEAD drift: saved={state.get('head')} current={snapshot.get('head')}"
                )
            if state.get("worktree_fingerprint") != snapshot.get("worktree_fingerprint"):
                warnings.append("checkpoint worktree fingerprint drift")

        print(f"repo: {repo}")
        for item in warnings:
            print(f"WARNING: {item}")
        if errors:
            for item in errors:
                print(f"ERROR: {item}")
            return 1
        if warnings:
            print("OK_WITH_DRIFT: WIP structure is valid but recovery is recommended")
        else:
            print("OK: WIP checkpoint structure is valid and matches the current worktree")
        return 0
    except Exception as exc:
        print(f"wip_validate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
