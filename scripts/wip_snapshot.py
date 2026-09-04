#!/usr/bin/env python3
"""Create a metadata-only WIP snapshot for a Git repository.

No raw diff contents, file contents, or environment-variable values are persisted.
Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


def run_git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.rstrip("\n")


def repo_root(repo: Path) -> Path:
    out = run_git(repo, "rev-parse", "--show-toplevel")
    return Path(out).resolve()


def lines(value: str) -> list[str]:
    return [line for line in value.splitlines() if line.strip()]


def _exclude_wip(paths: list[str]) -> list[str]:
    # The checkpoint must not fingerprint itself; otherwise each snapshot would
    # create artificial drift.
    return [p for p in paths if not p.replace("\\", "/").startswith(".codex/wip/")]


def changed_paths(repo: Path) -> dict[str, list[str]]:
    tracked = _exclude_wip(lines(run_git(repo, "diff", "--name-only")))
    staged = _exclude_wip(lines(run_git(repo, "diff", "--cached", "--name-only")))
    untracked = _exclude_wip(
        lines(run_git(repo, "ls-files", "--others", "--exclude-standard"))
    )
    return {
        "tracked_modified": sorted(set(tracked)),
        "staged": sorted(set(staged)),
        "untracked": sorted(set(untracked)),
    }


def worktree_fingerprint(repo: Path, paths: dict[str, list[str]]) -> str:
    """Fingerprint Git metadata plus changed-file bytes without storing contents."""
    h = hashlib.sha256()

    head = run_git(repo, "rev-parse", "HEAD", check=False)
    h.update(head.encode("utf-8", "replace"))

    # Hash the categorized path sets instead of raw `git status`, because the
    # checkpoint artifacts under .codex/wip/ are intentionally excluded.
    h.update(json.dumps(paths, sort_keys=True).encode("utf-8", "replace"))

    all_paths = sorted(
        set(paths["tracked_modified"]) | set(paths["staged"]) | set(paths["untracked"])
    )
    for rel in all_paths:
        h.update(rel.encode("utf-8", "replace"))
        p = repo / rel
        if p.is_file():
            try:
                with p.open("rb") as fh:
                    while True:
                        chunk = fh.read(1024 * 1024)
                        if not chunk:
                            break
                        h.update(chunk)
            except OSError:
                h.update(b"<unreadable>")
        else:
            h.update(b"<missing-or-nonfile>")

    return h.hexdigest()


def collect(repo_arg: str) -> dict[str, Any]:
    root = repo_root(Path(repo_arg))
    paths = changed_paths(root)

    branch = run_git(root, "branch", "--show-current", check=False) or "(detached)"
    head = run_git(root, "rev-parse", "HEAD", check=False)
    upstream = run_git(
        root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False
    )

    diff_stat = lines(run_git(root, "diff", "--stat", "--compact-summary", check=False))
    staged_stat = lines(
        run_git(root, "diff", "--cached", "--stat", "--compact-summary", check=False)
    )
    recent = lines(
        run_git(
            root,
            "log",
            "-10",
            "--pretty=format:%h%x09%ad%x09%s",
            "--date=iso-strict",
            check=False,
        )
    )

    payload: dict[str, Any] = {
        "schema_version": 1,
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository_root": str(root),
        "repository_name": root.name,
        "branch": branch,
        "head": head,
        "upstream": upstream or None,
        "paths": paths,
        "counts": {k: len(v) for k, v in paths.items()},
        "diff_stat": diff_stat,
        "staged_diff_stat": staged_stat,
        "recent_commits": recent,
    }
    payload["worktree_fingerprint"] = worktree_fingerprint(root, paths)
    return payload


def write_snapshot(payload: dict[str, Any]) -> tuple[Path, Path]:
    root = Path(payload["repository_root"])
    wip_dir = root / ".codex" / "wip"
    checkpoints = wip_dir / "checkpoints"
    checkpoints.mkdir(parents=True, exist_ok=True)

    state = wip_dir / "state.json"
    stamp = (
        payload["captured_at"]
        .replace(":", "")
        .replace("-", "")
        .replace("+00:00", "Z")
        .replace(".", "_")
    )
    history = checkpoints / f"{stamp}.json"

    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    state.write_text(text, encoding="utf-8")
    history.write_text(text, encoding="utf-8")

    current = wip_dir / "current.md"
    if not current.exists():
        current.write_text(
            "# WIP — recovery pending\n\n"
            "> Generated placeholder. Use `$wip checkpoint` or `$wip recover` "
            "to replace this with a validated continuity record.\n",
            encoding="utf-8",
        )
    return state, history


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write .codex/wip/state.json and a checkpoint history file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print compact JSON instead of a human summary",
    )
    args = parser.parse_args()

    try:
        payload = collect(args.repo)
        written = None
        if args.write:
            written = write_snapshot(payload)

        if args.json:
            print(json.dumps(payload, ensure_ascii=False))
        else:
            print(f"repo: {payload['repository_root']}")
            print(f"branch: {payload['branch']}")
            print(f"head: {payload['head']}")
            print(f"fingerprint: {payload['worktree_fingerprint']}")
            for key, count in payload["counts"].items():
                print(f"{key}: {count}")
            if written:
                print(f"state: {written[0]}")
                print(f"checkpoint: {written[1]}")
        return 0
    except Exception as exc:
        print(f"wip_snapshot: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
