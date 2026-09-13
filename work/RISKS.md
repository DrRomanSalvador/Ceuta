# CeutIA — Risks Register

**Document class:** Persistent risk register
**Authority:** Must be updated only with observed or demonstrated risks.

---

## Status values

- `OPEN`
- `MITIGATED`
- `ACCEPTED`
- `CLOSED`

## Severity values

- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`

---

## Current risks

### RISK-0001 — Unvalidated CI state

- Status: OPEN
- Severity: HIGH
- Description: Cycle 1 implementation exists but no recorded clean CI run against current HEAD has been observed.
- Impact: Cannot claim validated or production-ready status.
- Mitigation path: Execute and permanently record clean CI (pytest + security-control-plane).

### RISK-0002 — Historical documentation drift

- Status: OPEN
- Severity: MEDIUM
- Description: Older documents still contain claims about metrics.py that contradict the live file.
- Impact: Agents or humans may act on obsolete information.
- Mitigation path: Reconcile or explicitly mark residual historical claims as HISTORICAL.

---

## Rules

1. Record only observed or demonstrated risks.
2. Do not invent risks from speculation.
3. Link related tasks or issues when useful.
4. Do not close a risk without verification evidence.
