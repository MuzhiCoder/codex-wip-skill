# WIP Contract

`current.md` is a compact, durable reconstruction of engineering intent. It must be useful to a new Codex session that cannot access the prior conversation.

Use this structure:

```markdown
# WIP — <task title>

## Snapshot
- Updated: <ISO-8601 timestamp>
- Repository: <repo>
- Branch: <branch>
- HEAD: <sha>
- Worktree fingerprint: <fingerprint>
- Recovery mode: checkpoint | handoff | forensic-recovery | resume

## Original Goal
<What outcome is being built or fixed.>

## Current Scope
<What is in scope now, and what is explicitly out of scope.>

## Confirmed Decisions
| Decision | Status | Evidence |
|---|---|---|
| ... | VERIFIED / INFERRED / REPORTED | tests/code/ADR/user |

## Changed Areas
| Path / Symbol | Why it changed | State |
|---|---|---|
| ... | ... | VERIFIED_DONE / PARTIAL / ... |

## Completed Work
- [x] ...

## Partially Completed Work
- [ ] ...

## Tests and Verification
### Passed
- ...

### Failing
- ...

### Not Run
- ...

## Current Blockers
- ...

## Risks / Uncertain Assumptions
- `INFERRED`: ...
- `UNKNOWN`: ...

## Do Not Repeat
- <failed approaches or rejected designs, only when evidence exists>

## Exact Next Actions
1. <single concrete next action>
2. <next>
3. <next>

## Resume Guardrails
- Do not revert ...
- Preserve ...
- Re-verify ... before ...
```

## Evidence labels

Use one of:
- `VERIFIED`: directly supported by tests, executable behavior, code, or authoritative project docs.
- `INFERRED`: strongly suggested by code/diff/call graph but not yet proven.
- `REPORTED`: supplied by a previous agent/user/screenshot and not independently verified.
- `UNKNOWN`: insufficient evidence.

## Work-item states

Use one of:
- `VERIFIED_DONE`
- `IMPLEMENTED_UNVERIFIED`
- `PARTIAL`
- `BLOCKED`
- `NOT_STARTED`
- `UNKNOWN`

Do not describe partial work as complete merely because code exists. A changed file is evidence of activity, not proof of correctness.
