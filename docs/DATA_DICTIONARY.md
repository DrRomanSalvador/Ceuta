# CeutIA — Data Dictionary

**Document class:** Controlled vocabulary and field definitions
**Status:** REQUIRES VALIDATION (to be populated from live code and contracts)

---

## Principle

Every field that crosses a system boundary or appears in a contract must be defined here with:

- Name
- Type
- Allowed values / range
- Epistemic notes
- PUBLIC / OWNER classification
- Source of truth (code or contract)

---

## Current entries (seed)

| Name | Type | Notes |
|------|------|-------|
| epistemic_state | enum | Closed set defined in spec/estados-epistemologicos.md |
| sample_size | integer ≥ 0 | Used by ProxyGateAssessment |
| causal_claim | boolean | Must be false in proxy-gate outputs |

Further entries must be derived from live code and JSON schemas under `/contracts`, not invented.
