#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("wip_snapshot.py")
spec = importlib.util.spec_from_file_location("wip_snapshot", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, stdout=subprocess.PIPE)


class SnapshotTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        git(root, "init")
        git(root, "config", "user.email", "wip@example.invalid")
        git(root, "config", "user.name", "WIP Test")
        (root / "tracked.txt").write_text("base\n", encoding="utf-8")
        git(root, "add", "tracked.txt")
        git(root, "commit", "-m", "base")
        return root

    def test_collects_metadata_without_contents(self):
        root = self.make_repo()
        secret = "SUPER_SECRET_TEST_VALUE_123"
        (root / "tracked.txt").write_text(f"changed {secret}\n", encoding="utf-8")
        (root / "new.txt").write_text(f"untracked {secret}\n", encoding="utf-8")

        payload = mod.collect(str(root))
        serialized = json.dumps(payload)

        self.assertIn("tracked.txt", serialized)
        self.assertIn("new.txt", serialized)
        self.assertNotIn(secret, serialized)
        self.assertEqual(payload["counts"]["tracked_modified"], 1)
        self.assertEqual(payload["counts"]["untracked"], 1)

    def test_write_creates_state_and_history(self):
        root = self.make_repo()
        (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
        payload = mod.collect(str(root))
        state, history = mod.write_snapshot(payload)

        self.assertTrue(state.exists())
        self.assertTrue(history.exists())
        self.assertTrue((root / ".codex" / "wip" / "current.md").exists())

    def test_fingerprint_changes_with_worktree(self):
        root = self.make_repo()
        before = mod.collect(str(root))["worktree_fingerprint"]
        (root / "tracked.txt").write_text("different\n", encoding="utf-8")
        after = mod.collect(str(root))["worktree_fingerprint"]
        self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()
