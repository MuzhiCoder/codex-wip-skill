# WIP — Replace per-object existence checks with prefix scan

## Snapshot
- Updated: 2026-09-04T09:00:00Z
- Repository: example-repo
- Branch: feature/storage-scan
- HEAD: deadbeef
- Worktree fingerprint: example-only
- Recovery mode: forensic-recovery

## Original Goal
Remove the O(N) remote existence-check pattern from a storage migration planner and replace it with a bounded-memory prefix listing plus merge algorithm.

## Current Scope
In scope: collision detection, planner integration, targeted tests, cancellation boundaries.
Out of scope: UI redesign and unrelated storage adapters.

## Confirmed Decisions
| Decision | Status | Evidence |
|---|---|---|
| Use one paginated target-prefix scan instead of one remote HEAD per source object | VERIFIED | changed tests + production implementation |
| Keep memory bounded with sorted chunks / streaming merge | INFERRED | code structure and temp-file helpers; large-scale test not yet run |
| Cancellation must be checked between scan and plan-generation phases | REPORTED | previous-session handoff; not independently verified |

## Changed Areas
| Path / Symbol | Why it changed | State |
|---|---|---|
| `src/collision.py` | Replace per-object remote checks | IMPLEMENTED_UNVERIFIED |
| `tests/test_collision.py` | Specify prefix-scan behavior | VERIFIED_DONE |
| `src/planner.py` | Wire collision result into planning | PARTIAL |

## Completed Work
- [x] Added a regression test that fails if collision detection performs one remote HEAD per source object.
- [x] Added paginated target-prefix listing abstraction.

## Partially Completed Work
- [ ] Planner cancellation checks are present in one phase but not all phase boundaries.

## Tests and Verification
### Passed
- `python -m unittest tests.test_collision`

### Failing
- None currently known.

### Not Run
- Full repository test suite.
- Large synthetic source-list test.

## Current Blockers
- Need to determine whether planner cancellation should return a partial result or a dedicated cancelled state.

## Risks / Uncertain Assumptions
- `INFERRED`: temporary sorted chunks are always cleaned up after failure.
- `UNKNOWN`: behavior when the remote listing changes during a long scan.

## Do Not Repeat
- Do not restore the previous per-source-object remote HEAD loop; the regression test exists specifically to prevent it.

## Exact Next Actions
1. Verify cancellation semantics from existing planner contracts and callers.
2. Add cancellation checks at remaining safe phase boundaries.
3. Run targeted planner tests.
4. Refresh `$wip checkpoint` before broader refactoring.

## Resume Guardrails
- Do not revert the prefix-scan regression test.
- Preserve bounded-memory behavior.
- Re-verify remote-call counts before declaring the collision work complete.
