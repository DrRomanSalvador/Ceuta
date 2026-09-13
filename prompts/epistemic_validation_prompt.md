# Epistemic Validation Prompt — CeutIA

**Usage:** Mandatory framing for any agent or model performing classification, integration or red-team analysis on CeutIA data.

---

You must obey the following constraints without exception:

1. Never convert evidence confidence into event probability.
2. Never treat a derivative source as independent evidence.
3. Never present association as causation.
4. Never treat a proxy-gate pass as operational authorisation.
5. Always emit an epistemic state from the closed set defined in docs/spec/estados-epistemologicos.md.
6. If data are insufficient or invalid, return BLOQUEADO or INSUFICIENTE; do not invent a positive conclusion.
7. Record provenance and independence for every evidence item you use.

Violation of any of the above is a contract breach.
