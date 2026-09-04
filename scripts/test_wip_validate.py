#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / "wip_snapshot.py"
VALIDATE = HERE / "wip_validate.py"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def git(repo: Path, *args: str) -> None:
    p = run("git", "-C", str(repo), *args)
    if p.returncode:
        raise RuntimeError(p.stdout)


VALID_CURRENT = """# WIP — test

## Snapshot
- test

## Original Goal
Test.

## Confirmed Decisions
None.

## Changed Areas
None.

## Completed Work
None.

## Partially Completed Work
None.

## Tests and Verification
### Passed
- test

## Current Blockers
None.

## Risks / Uncertain Assumptions
None.

## Do Not Repeat
None.

## Exact Next Actions
1. Continue.

## Resume Guardrails
- Preserve work.
"""


class ValidateTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        git(root, "init")
        git(root, "config", "user.email", "wip@example.invalid")
        git(root, "config", "user.name", "WIP Test")
        (root / "a.txt").write_text("a\n", encoding="utf-8")
        git(root, "add", "a.txt")
        git(root, "commit", "-m", "base")
        return root

    def snapshot_and_fill(self, root: Path) -> None:
        p = run(sys.executable, str(SNAPSHOT), "--repo", str(root), "--write")
        self.assertEqual(p.returncode, 0, p.stdout)
        (root / ".codex" / "wip" / "current.md").write_text(VALID_CURRENT, encoding="utf-8")

    def test_valid_checkpoint_matches(self):
        root = self.make_repo()
        self.snapshot_and_fill(root)
        p = run(sys.executable, str(VALIDATE), "--repo", str(root))
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("matches the current worktree", p.stdout)

    def test_detects_drift(self):
        root = self.make_repo()
        self.snapshot_and_fill(root)
        (root / "a.txt").write_text("changed\n", encoding="utf-8")
        p = run(sys.executable, str(VALIDATE), "--repo", str(root))
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("worktree fingerprint drift", p.stdout)


if __name__ == "__main__":
    unittest.main()
