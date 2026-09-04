#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_ROOT = ROOT / "plugins" / "codex-wip"
MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "wip"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON at {path}: {exc}")


def resolve_plugin_path(value: str) -> Path:
    if not value.startswith("./"):
        fail(f"plugin asset/component path must begin with ./: {value}")
    return PLUGIN_ROOT / value[2:]


def main() -> int:
    marketplace = read_json(MARKETPLACE)
    manifest = read_json(MANIFEST)

    if marketplace.get("name") != "codex-wip-skill":
        fail("unexpected marketplace name")

    plugins = marketplace.get("plugins") or []
    if len(plugins) != 1:
        fail("marketplace must contain exactly one plugin")

    entry = plugins[0]
    if entry.get("name") != "codex-wip":
        fail("marketplace plugin name must be codex-wip")
    if entry.get("source") != {"source": "local", "path": "./plugins/codex-wip"}:
        fail("marketplace source must point at ./plugins/codex-wip")
    if entry.get("policy", {}).get("installation") != "AVAILABLE":
        fail("plugin must be AVAILABLE")
    if entry.get("policy", {}).get("authentication") not in {"ON_INSTALL", "ON_USE"}:
        fail("invalid authentication policy")

    if manifest.get("name") != "codex-wip":
        fail("manifest name must be codex-wip")
    version = str(manifest.get("version", ""))
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version):
        fail(f"manifest version is not SemVer-like: {version}")
    if manifest.get("license") != "MIT":
        fail("manifest license must be MIT")
    if not (ROOT / "LICENSE").is_file():
        fail("repository LICENSE file is missing")
    if manifest.get("skills") != "./skills/":
        fail("manifest skills path must be ./skills/")
    if not (SKILL_ROOT / "SKILL.md").is_file():
        fail("packaged wip skill is missing SKILL.md")

    interface = manifest.get("interface") or {}
    for key in ("logo", "composerIcon"):
        value = interface.get(key)
        if not isinstance(value, str) or not value:
            fail(f"manifest interface.{key} is required")
        asset = resolve_plugin_path(value)
        if not asset.is_file():
            fail(f"manifest interface.{key} asset is missing: {value}")

    screenshots = interface.get("screenshots") or []
    if len(screenshots) < 2:
        fail("manifest must include at least two Plugin Directory screenshots")
    for value in screenshots:
        if not isinstance(value, str) or not value.endswith(".png"):
            fail(f"screenshot must be a PNG path: {value}")
        asset = resolve_plugin_path(value)
        if asset.parent != PLUGIN_ROOT / "assets":
            fail(f"screenshot must live directly under ./assets/: {value}")
        if not asset.is_file():
            fail(f"screenshot asset is missing: {value}")
        if asset.stat().st_size < 10_000:
            fail(f"screenshot asset looks unexpectedly small: {value}")

    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill_text.startswith("---\n") or "\nname: wip\n" not in skill_text[:500]:
        fail("packaged SKILL.md frontmatter must declare name: wip")

    required = [
        "agents/openai.yaml",
        "references/wip-contract.md",
        "references/recovery-protocol.md",
        "references/handoff-protocol.md",
        "scripts/wip_snapshot.py",
        "scripts/wip_validate.py",
    ]
    for rel in required:
        if not (SKILL_ROOT / rel).is_file():
            fail(f"packaged skill missing {rel}")

    # The repository root remains a legacy direct-skill distribution surface.
    # Keep it byte-identical to the canonical plugin skill for deterministic releases.
    mirrors = {
        ROOT / "SKILL.md": SKILL_ROOT / "SKILL.md",
        ROOT / "agents" / "openai.yaml": SKILL_ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "wip-contract.md": SKILL_ROOT / "references" / "wip-contract.md",
        ROOT / "references" / "recovery-protocol.md": SKILL_ROOT / "references" / "recovery-protocol.md",
        ROOT / "references" / "handoff-protocol.md": SKILL_ROOT / "references" / "handoff-protocol.md",
        ROOT / "scripts" / "wip_snapshot.py": SKILL_ROOT / "scripts" / "wip_snapshot.py",
        ROOT / "scripts" / "wip_validate.py": SKILL_ROOT / "scripts" / "wip_validate.py",
    }
    for legacy, canonical in mirrors.items():
        if legacy.read_bytes() != canonical.read_bytes():
            fail(f"legacy mirror drift: {legacy.relative_to(ROOT)} != {canonical.relative_to(ROOT)}")

    print("OK: Codex plugin package, assets, license, and marketplace are internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
