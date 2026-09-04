# Codex WIP Plugin

`codex-wip` packages the `$wip` continuity skill for Codex Plugin/Marketplace installation.

It helps preserve and recover long-running coding work across usage-limit exhaustion, provider/account changes, inaccessible conversations, crashes, context loss, and machine migration.

## Install from this marketplace

```bash
codex plugin marketplace add MuzhiCoder/codex-wip-skill --ref main
codex plugin add codex-wip@codex-wip-skill
```

Start a new Codex thread after installation, then try:

```text
$wip status
```

Core modes:

- `$wip checkpoint`
- `$wip handoff`
- `$wip recover`
- `$wip resume`
- `$wip status`

Homepage: https://muzhicoder.github.io/codex-wip-skill/
