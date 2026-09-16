# CONTROL PLANE EXECUTION CHECKPOINT 016

## Authoritative branch state

- Branch: `maximum-knowledge-to-capability`
- HEAD at checkpoint creation: `3b9afb46d2db8b0512840a20b31709c1c22dc4e8`
- PR: #65 remains open.
- No merge or scientific-validation promotion is claimed.

## Executed changes

1. Materialized-state CAS was made canonical event-backed; legacy unlogged CAS invocation is no longer part of the callable contract.
2. Materialized-state recovery was added from canonical `MATERIALIZED_STATE_CAS` events with contiguous revision enforcement.
3. Materialized-state tests now cover concurrency, stale writers, missing event identity, interrupted projection persistence, corrupted event chains, revision jumps and malformed state.
4. A repository-wide executable CAS call-site audit was added and wired into CI; direct CAS call sites must provide `event_log`, `actor` and `timestamp`.
5. The systemic susceptibility formula syntax defect found by CI was repaired and regression-tested.
6. The risk calculator was reconciled with the canonical `EvidenceContract`; UNKNOWN/UNVERIFIED evidence can no longer be silently treated as verified risk input.
7. Runtime `requests` was declared in `pyproject.toml` and CI now installs declared runtime dependencies before control-plane tests.
8. Event-log appends now call `fsync` before returning; a durability regression test was added.
9. Lifecycle mutations (admission, retirement, recovery, contradiction) now require canonical event lineage.
10. Work-claim acquisition/release now require canonical event lineage.
11. Contribution registry mutations now require mission identity and canonical event lineage.
12. CI concurrency was changed to cancel obsolete branch runs so validation targets the latest executable frontier rather than accumulating stale queued runs.

## Verification state

- GitHub Actions has been observed executing the branch workflow and previously exposed concrete defects that were repaired in subsequent commits.
- The latest post-repair HEAD still requires final current-HEAD CI execution; no green result is asserted here.
- Local clone/test execution remains unavailable because the local environment cannot resolve/connect to GitHub.

## Open internal verification frontier

- Current-head CI execution and any resulting repair loop.
- Re-audit of all event-backed writers after lifecycle/work-claim/contribution migrations.
- Reconcile replay and bootstrap against the newly mandatory writer contracts.
- Continue adversarial, recovery, concurrency and authority checks where applicable.
- Reconcile the autonomous queue with the actual branch evidence.

`INTERNAL_WORK_EXHAUSTED = FALSE`
