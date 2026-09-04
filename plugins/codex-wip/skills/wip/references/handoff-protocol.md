# Handoff Protocol

Use this when moving between ChatGPT-account Codex and API-key/custom-provider Codex, between machines, or between sessions that cannot share the original conversation.

## Key principle

Conversation identity is not the continuity boundary. The repository plus WIP artifacts are.

## Same machine, provider/account switch

Required:
- unchanged repository worktree;
- `.codex/wip/current.md`;
- `.codex/wip/state.json`;
- same project tools/configuration where practical.

The receiving session should not attempt to reopen the inaccessible cloud thread. Start a new session in the same repository and run `$wip resume`.

## Different machine

Transfer both:
1. code state; and
2. WIP state.

Preferred transport is a user-approved WIP Git branch/commit because it preserves the exact tree and is easy to verify. Do not commit or push automatically.

If uncommitted changes must be transported without a WIP commit, ask the user to choose an explicit patch/archive workflow. Warn that patches may contain secrets present in source files.

Re-create machine-specific runtime configuration rather than blindly copying caches, named pipes, temporary runtime paths, or generated local plugin directories.

## Receiving-session bootstrap prompt

Use this text in the new Codex session:

> Use `$wip resume` for this repository. The previous Codex session may be inaccessible because authentication/provider or machine context changed. Treat `.codex/wip/current.md`, `.codex/wip/state.json`, Git history, current worktree, tests, and code intelligence as the continuity sources. Do not try to recover the old cloud conversation. Verify checkpoint freshness first; if repository drift is material, switch to forensic recovery before changing business code. Continue from the first verified Exact Next Action and checkpoint again after the next meaningful milestone.

## Handoff readiness checklist

- [ ] Current repository root recorded.
- [ ] Branch and HEAD recorded.
- [ ] Dirty/staged/untracked paths recorded.
- [ ] `current.md` validated.
- [ ] `state.json` refreshed.
- [ ] Code changes have a transport path to the destination.
- [ ] Destination can restore required build/test dependencies.
- [ ] Secrets are not embedded in WIP metadata.
- [ ] Machine-specific runtime paths are not treated as portable state.
