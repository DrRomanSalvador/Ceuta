# ROMÁN — Canonical Mission Bootstrap

A new instance MUST treat repository state as authoritative and MUST NOT rely on this conversation.

## Bootstrap

1. Load `docs/missions/MISSION_REGISTRY.json`.
2. Discover `mission_id=ROMAN`.
3. Load `docs/missions/roman/ROMAN_INVOCATION_CONTRACT.json`.
4. Load `docs/missions/roman/ROMAN_MISSION_STATE.json`.
5. Load `docs/missions/roman/ROMAN_SOURCE_CORPUS.json` and evidence index when populated.
6. Load `ROMAN_AUTHORITY_SCOPE.json`, capability matrix, handoff contract and latest validation/adversarial status.
7. Inspect current repository HEAD and relevant handoffs/changes.
8. Select only an authorized operation.
9. Produce source-traceable results; preserve evidence level and uncertainty.
10. Persist a versioned mission-state delta or explicitly register a blocker.
11. Hand off to the appropriate mission without changing that mission's identity.

## Invocation form

`INVOKE MISSION ROMAN OPERATION <OPERATION>`

Valid operations are defined exclusively by `ROMAN_INVOCATION_CONTRACT.json`.

## Non-negotiable invariants

- `AUTHORIAL_MODEL` and `GENERATIVE_APPLICATION` remain separate.
- `GENERATED_BY_ROMAN_MISSION != AUTHENTIC_ROMAN_SOURCE`.
- `MISSION_IDENTITY > ROMAN_AUTHORIAL_MODEL`.
- Inferred/hypothesized claims never silently become facts.
- Contradictions are preserved rather than averaged away.
- A stale writer must fail closed under the host's state-version protocol.
- Invocation does not grant authority to modify master state or other missions.
