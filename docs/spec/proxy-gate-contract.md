# Proxy Gate Contract (Cycle 1)

**Status:** IMPLEMENTED — NOT YET VALIDATED
**Code authority:** `backend/app/core/system_integrator.py`
**Test authority:** `tests/core/test_system_integrator.py`

---

## Purpose

Provide an auditable, fail-closed screening of whether an observed signal is likely acting as a proxy for composition rather than for the target phenomenon.

---

## Required behaviour (already present in code)

- Compute association signal ↔ composition.
- Compute association signal ↔ outcome (when available).
- Compute partial correlation signal ↔ outcome controlling for composition (when data permit).
- Fail closed on insufficient observations, constant vectors or incompatible inputs.
- Emit explicit epistemic state (`PROXY_RISK`, `NO_VERIFICADO`, `BLOQUEADO`, etc.).
- Never claim causality.
- Never authorise operational promotion solely from a proxy-gate result.

---

## Forbidden claims

- “This pass proves the signal is causal.”
- “This pass proves absence of bias.”
- “This pass authorises operational use.”
