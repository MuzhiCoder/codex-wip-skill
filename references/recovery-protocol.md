# Recovery Protocol

Use this protocol when a previous Codex thread is inaccessible or its context cannot be trusted.

## Goal

Recover enough durable context to continue safely without pretending to reconstruct hidden chain-of-thought. Recover engineering state, not private reasoning.

## Recovery order

1. Repository instructions (`AGENTS.md`, contribution docs).
2. Saved `.codex/wip/current.md` and `state.json`, when present.
3. Git status and history.
4. Changed tests and executable specifications.
5. Changed production code.
6. Call graph / code intelligence.
7. Build and targeted tests.
8. Plans, ADRs, issue references, TODO/FIXME.
9. User-provided screenshots or recollections as `REPORTED` evidence.

## Forensic rules

- Do not modify business code while reconstructing.
- Do not assume every diff hunk belongs to the interrupted task; identify unrelated pre-existing changes.
- Do not assume newly added tests are correct; compare them to existing contracts.
- Prefer targeted tests over full-suite runs at first.
- Avoid expensive repository-wide scans when changed paths and call-graph neighbors are sufficient.
- If a tool such as CodeGraph is available, use it to validate dependency boundaries and symbol relationships.
- If it is unavailable, fall back to repository search and language-native tooling.

## Drift detection

A saved checkpoint is stale when any of the following materially changed:
- `HEAD`;
- branch;
- tracked/staged/untracked path sets;
- worktree fingerprint;
- repository identity in a way not explained by an intentional machine/worktree handoff.

A filesystem-path change alone is not material when branch, HEAD, and worktree fingerprint still match.

Minor timestamp-only changes are not material.

If stale, preserve the old checkpoint as evidence and rebuild `current.md` from the current repository.

## Minimum recovery output

Before resuming implementation, state:
- what is definitely complete;
- what exists but is unverified;
- what is partial;
- what is blocked;
- what is unknown;
- the exact next action.

If uncertainty could cause destructive or architectural rework, stop and ask the user rather than guessing.
