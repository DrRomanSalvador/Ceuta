# CeutIA — Requirements

**Document class:** Requirements register
**Status:** PARTIALLY IMPLEMENTED — REQUIRES VALIDATION

---

## Core non-functional requirements (binding)

1. Epistemic separation is mandatory (see EPISTEMIC_MODEL.md).
2. Fail-closed behaviour is mandatory for insufficient or invalid data.
3. Association must never be presented as causation.
4. Proxy-gate results must never alone authorise operational promotion.
5. PUBLIC / OWNER boundary must be enforced.
6. No secret material may be committed.
7. All status claims must use the closed vocabulary defined in CURRENT_STATUS.md.

---

## Functional requirements — Cycle 1 (implemented, not yet validated)

- Auditable spatial proxy screening.
- Explicit sample-size and method reporting.
- Fail-closed on insufficient observations / constant vectors / incompatible inputs.
- Explicit PROXY_RISK classification.

---

## Open requirement gaps

- Recorded clean CI validation of Cycle 1.
- Live, reproducible inventory of metrics.py.
- Full reconciliation of residual historical documentation.
