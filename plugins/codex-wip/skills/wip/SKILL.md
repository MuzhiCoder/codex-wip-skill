---
name: wip
description: Preserve continuity for long-running coding work across Codex usage-limit exhaustion, provider or account switches, inaccessible conversations, machine changes, crashes, and context loss. Use when the user asks to checkpoint, hand off, recover, resume, reconstruct, or continue interrupted repository work, especially when the previous Codex thread cannot be opened.
---

# WIP Continuity

Use this skill to make repository work recoverable without depending on a single Codex conversation.

## Invocation

Interpret the first argument as a mode when present:

- `$wip checkpoint` — persist a lightweight checkpoint while the current session is healthy.
- `$wip handoff` — prepare a provider/machine/session handoff.
- `$wip recover` — reconstruct state after a hard interruption or inaccessible prior conversation.
- `$wip resume` — validate the saved checkpoint against the current repository and continue.
- `$wip status` — report checkpoint freshness and repository drift without changing business code.

If no mode is supplied, infer the safest mode from the repository:
- prior WIP state + user wants to continue -> `resume`;
- modified worktree + no usable WIP state -> `recover`;
- active healthy session + user wants durability -> `checkpoint`;
- imminent provider/machine/session switch -> `handoff`.

Read `references/recovery-protocol.md` before `recover` or `resume`.
Read `references/handoff-protocol.md` before `handoff`.
Read `references/wip-contract.md` whenever creating or updating `current.md`.

## Durable state

Store project-local continuity data under:

```text
.codex/wip/
├── current.md
├── state.json
└── checkpoints/
    └── <timestamp>.json
```

Treat Git as the source of truth for code. Treat `current.md` as the source of truth for recovered intent, decisions, verification state, and next actions.

Do not store:
- access tokens, API keys, cookies, passwords, private environment-variable values;
- full environment dumps;
- raw credential files;
- entire conversation transcripts;
- large raw diffs unless the user explicitly requests a patch artifact.

## Safety rules

1. During `recover`, do not modify business code until recovery is complete.
2. Never run `git reset --hard`, `git clean`, destructive checkout, force push, or history rewrite as part of this skill.
3. Never commit or push unless the user explicitly asks for it.
4. Never assume an inaccessible cloud conversation can be reopened after switching authentication/provider. Recover from repository artifacts instead.
5. Preserve all pre-existing uncommitted changes.
6. If repository instructions such as `AGENTS.md` exist, read and follow them before recovery or continuation.
7. If a command may reveal secrets, prefer metadata-only output.
8. Mark uncertain conclusions explicitly rather than presenting them as facts.

## Common first step

From the repository root, run:

```bash
python <skill-dir>/scripts/wip_snapshot.py --repo . --write
```

On Windows, use the Python launcher if needed:

```powershell
py <skill-dir>\scripts\wip_snapshot.py --repo . --write
```

The script is metadata-only: it records Git identity, branch/HEAD, changed paths, diff statistics, recent commits, and a worktree fingerprint. It does not persist raw file contents, raw diffs, or environment-variable values.

Then read `.codex/wip/state.json`.

## Mode: checkpoint

1. Read repository instructions and current task artifacts.
2. Run `wip_snapshot.py --write`.
3. Inspect current work, tests, plans, and relevant changed files.
4. Create or update `.codex/wip/current.md` using `references/wip-contract.md`.
5. Record:
   - current goal;
   - confirmed decisions;
   - completed and partial work;
   - tests/build status;
   - blockers and risks;
   - exact next actions;
   - evidence/confidence for each important claim.
6. Run:

```bash
python <skill-dir>/scripts/wip_validate.py --repo .
```

7. Report the checkpoint path and whether it is safe to resume from a new session.

A checkpoint is not a commit. If the user needs cross-machine continuity, explain that code and `.codex/wip/` must also be transferred, normally by an explicitly approved WIP commit/branch or other user-selected sync method.

## Mode: handoff

1. Perform all `checkpoint` steps.
2. Read `references/handoff-protocol.md`.
3. Determine whether the destination is:
   - same machine, new provider/account/session;
   - another machine;
   - another branch/worktree.
4. Produce a handoff readiness report with:
   - repository root;
   - current branch and HEAD;
   - dirty/staged/untracked state;
   - checkpoint timestamp;
   - destination assumptions;
   - what must be synchronized.
5. For another machine, require a durable transport for code changes. Prefer:
   - a user-approved WIP branch/commit and push; or
   - a user-approved patch/archive when Git remote transport is not available.
6. Do not push automatically.
7. Include the exact bootstrap prompt from `references/handoff-protocol.md` for the receiving Codex session.

## Mode: recover

Use this when the old conversation is unavailable, exhausted, crashed, or belongs to another provider identity.

1. Freeze business-code edits.
2. Read repository instructions.
3. Run `wip_snapshot.py --write`.
4. If `.codex/wip/current.md` exists, treat it as evidence, not unquestionable truth.
5. Inspect:
   - `git status`;
   - changed/staged/untracked paths;
   - `git diff --stat`;
   - `git diff --name-status`;
   - recent Git history;
   - changed tests;
   - task/plan/ADR files;
   - TODO/FIXME markers in changed areas;
   - compile/test failures relevant to changed code.
6. Use available code-intelligence tools such as CodeGraph when present to validate symbols, callers, callees, and dependency boundaries. Do not require them if unavailable.
7. Reconstruct intent from strongest evidence first:
   1. passing/failing tests and executable behavior;
   2. code and call graph;
   3. Git history and diff structure;
   4. repository plans/ADRs;
   5. saved WIP notes;
   6. user recollection or screenshots.
8. Classify each significant work item:
   - `VERIFIED_DONE`
   - `IMPLEMENTED_UNVERIFIED`
   - `PARTIAL`
   - `BLOCKED`
   - `NOT_STARTED`
   - `UNKNOWN`
9. Write `.codex/wip/current.md`.
10. Validate it with `wip_validate.py`.
11. Present a recovery report that clearly separates:
   - verified facts;
   - strong inferences;
   - unresolved uncertainty.
12. Stop before business implementation unless the user invoked `resume` or explicitly asked to continue after recovery.

## Mode: resume

1. Read `current.md`, `state.json`, repository instructions, and `references/recovery-protocol.md`.
2. Run a fresh snapshot without overwriting first:

```bash
python <skill-dir>/scripts/wip_snapshot.py --repo .
```

3. Compare current HEAD/worktree fingerprint with saved state.
4. If drift is material, run `recover` before implementation.
5. Verify the first pending `Exact Next Action` against current code.
6. Continue from the smallest verified next step.
7. After every meaningful milestone, update the WIP checkpoint.
8. Before context compaction, provider switching, machine switching, or a long risky operation, checkpoint again.

## Mode: status

Run a fresh snapshot without business-code changes and report:
- saved checkpoint timestamp;
- saved vs current HEAD;
- saved vs current worktree fingerprint;
- changed/staged/untracked counts;
- whether `current.md` passes validation;
- whether `resume` is safe or `recover` is required.

## Milestone checkpoint policy

For long agentic tasks, checkpoint after any of these:
- a RED test establishes target behavior;
- a GREEN implementation passes;
- an architectural decision changes;
- a blocker is removed;
- a migration phase completes;
- a large refactor crosses a stable boundary;
- before expected context compaction;
- before switching ChatGPT account/provider/API-key mode;
- before changing machines;
- before the remaining usage limit becomes operationally risky.

Do not checkpoint every trivial edit. Prefer stable, meaningful milestones.
