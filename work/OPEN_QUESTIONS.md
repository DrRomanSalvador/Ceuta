# CeutIA — Open Questions

**Document class:** Persistent open-questions register
**Authority:** Questions remain open until resolved with evidence.

---

## Current open questions

### OQ-0001 — Live metrics.py inventory

- Status: OPEN
- Question: What is the exact, reproducible inventory of symbols and potential semantic duplicates in the current live `backend/app/core/metrics.py`?
- Why it matters: Historical inventory is non-authoritative. Structural decisions require current evidence.
- Resolution condition: Generate inventory from the live file and record it.

### OQ-0002 — CI validation of Cycle 1

- Status: OPEN
- Question: Does the current HEAD produce a clean PASS on the full pytest suite and security-control-plane workflow?
- Why it matters: Without recorded PASS, status remains IMPLEMENTED — NOT YET VALIDATED.
- Resolution condition: Recorded clean CI run against current HEAD.

---

## Rules

1. Do not close a question without evidence.
2. Do not convert an open question into an assumed answer.
3. Prefer recording the question over inventing a resolution.
