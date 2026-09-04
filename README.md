# Codex WIP Skill

Durable checkpoint, handoff, forensic recovery, and resume workflow for OpenAI Codex coding sessions.

This repository contains a Codex Skill named `$wip` for preserving engineering continuity when a coding task is interrupted by usage-limit exhaustion, provider/account switching, inaccessible conversations, crashes, context loss, or machine migration.

## What it solves

A long-running Codex session may hold valuable context that is not fully represented in the repository. When the original conversation becomes inaccessible—for example after switching from ChatGPT-account Codex to an API-key/custom provider—the code may still be present but the task state, verified decisions, unfinished work, test status, and next actions can be lost.

`$wip` makes that state durable in the repository itself.

## Modes

- `$wip checkpoint` — persist a lightweight checkpoint while the current session is healthy.
- `$wip handoff` — prepare for a provider/account/machine/session handoff.
- `$wip recover` — reconstruct state after a hard interruption or inaccessible prior conversation.
- `$wip resume` — validate the saved checkpoint against the current repository and continue.
- `$wip status` — report checkpoint freshness and repository drift without changing business code.

## Durable project state

The skill stores continuity metadata under:

```text
.codex/wip/
├── current.md
├── state.json
└── checkpoints/
    └── <timestamp>.json
```

Git remains the source of truth for code. `current.md` is the source of truth for recovered intent, decisions, verification state, blockers, and exact next actions.

## Install

Copy this repository into your Codex skills directory:

```text
%USERPROFILE%\.codex\skills\wip
```

On Windows you can also run:

```powershell
.\scripts\install.ps1
```

If `CODEX_HOME` is set, the installer uses `$env:CODEX_HOME\skills\wip`; otherwise it uses `$HOME\.codex\skills\wip`.

## Typical interrupted-session recovery

Suppose a ChatGPT-account Codex session is interrupted after the usage limit is exhausted, and the same thread cannot be opened after switching to CC Switch/API-key mode.

Start a new Codex session in the same repository and run:

```text
$wip recover
```

The skill will first freeze business-code changes, inspect Git state, changed tests, recent history, code relationships, project instructions, existing WIP notes, and targeted test/build evidence. It will classify work as `VERIFIED_DONE`, `IMPLEMENTED_UNVERIFIED`, `PARTIAL`, `BLOCKED`, `NOT_STARTED`, or `UNKNOWN`, then create `.codex/wip/current.md`.

After reviewing the recovery report, continue with:

```text
$wip resume
```

## Cross-provider / cross-machine handoff

Before switching provider, account, or machine:

```text
$wip handoff
```

For another machine, both the code state and `.codex/wip/` state must be transferred. Prefer a user-approved WIP Git branch/commit when practical. The skill never commits, pushes, resets, cleans, force-pushes, or rewrites history automatically.

## Evidence model

Important claims in `current.md` are labeled as:

- `VERIFIED` — supported by tests, executable behavior, code, or authoritative project docs.
- `INFERRED` — strongly suggested by the code/diff/call graph but not fully proven.
- `REPORTED` — supplied by a previous agent, user, or screenshot and not independently verified.
- `UNKNOWN` — insufficient evidence.

This prevents a recovered session from blindly trusting a stale handoff or an interrupted agent's last message.

## Security

The snapshot script is metadata-only. It does not persist raw diff contents, file contents, environment-variable values, API keys, access tokens, cookies, passwords, or authorization headers.

The validator also checks for several common secret markers in `current.md`.

## Repository layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── handoff-protocol.md
│   ├── recovery-protocol.md
│   └── wip-contract.md
└── scripts/
    ├── install.ps1
    ├── wip_snapshot.py
    ├── wip_validate.py
    ├── test_wip_snapshot.py
    └── test_wip_validate.py
```

## Philosophy

Conversation identity is not the continuity boundary. The repository plus durable WIP artifacts are.

The goal is not to reconstruct private model reasoning; it is to reconstruct enough verifiable engineering state that a fresh Codex session can continue safely and efficiently.
