# Changelog

All notable changes to Codex WIP will be documented in this file.

The project follows Semantic Versioning.

## [0.1.0] - 2026-09-04

### Added

- Public Codex Plugin Marketplace packaging under `.agents/plugins/marketplace.json`.
- Native Codex plugin manifest at `plugins/codex-wip/.codex-plugin/plugin.json`.
- `$wip checkpoint`, `$wip handoff`, `$wip recover`, `$wip resume`, and `$wip status` workflows.
- Metadata-only Git worktree snapshots and deterministic worktree fingerprints.
- Forensic recovery protocol with `VERIFIED`, `INFERRED`, `REPORTED`, and `UNKNOWN` evidence labels.
- Recovery work-item states: `VERIFIED_DONE`, `IMPLEMENTED_UNVERIFIED`, `PARTIAL`, `BLOCKED`, `NOT_STARTED`, and `UNKNOWN`.
- Cross-provider/account/session/machine handoff guidance.
- Formal Codex WIP logo and composer icon.
- Plugin Directory and recovery-workflow preview screenshots.
- Reproducible SVG-to-PNG asset build workflow.
- GitHub Pages interactive demo.
- Cross-platform CI on Windows and Linux with Python 3.11–3.13.
- MIT License.

### Safety

- Recovery freezes business-code edits until state reconstruction is complete.
- Snapshotting does not persist raw diffs, business file contents, environment-variable values, API keys, tokens, cookies, passwords, or authorization headers by default.
- The skill does not automatically run destructive Git operations, force push, history rewrites, commit, or push.

### Community

- Public marketplace installation is available from `MuzhiCoder/codex-wip-skill`.
- OpenAI Codex curated marketplace review request: `openai/codex#42725`.

[0.1.0]: https://github.com/MuzhiCoder/codex-wip-skill/releases/tag/v0.1.0
