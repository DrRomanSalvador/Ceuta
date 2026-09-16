# APOYO — Zero-Context Bootstrap

A fresh execution must reconstruct APOYO from persistent artifacts, not conversation history.

## Bootstrap order

`IDENTITY → CONSTITUTION → CONTRACT → AUTHORITY → REGISTRY → MEETING_POINT → MEMORY → ACTIVE_COLLABORATIONS → CHECKPOINT → CURRENT_STATE`

Canonical artifacts:

- Identity and contract: `docs/missions/apoyo/APOYO_INVOCATION_CONTRACT.json`
- Registry: `docs/missions/MISSION_REGISTRY.json`
- Universal execution constitution: `docs/missions/UNIVERSAL_EXECUTION_CONSTITUTION.md`
- Persistent APOYO state: `docs/missions/apoyo/APOYO_MISSION_STATE.json`
- Account authorization source: `docs/missions/apoyo/APOYO_ACCOUNT_AUTHORIZATION.json`
- Runtime: `backend/app/missions/apoyo.py`

A conversation is auxiliary context only.

If persistent state is unreadable, identity/authority checks fail, or account authorization is unavailable, APOYO fails closed and must not invent state or permissions.
