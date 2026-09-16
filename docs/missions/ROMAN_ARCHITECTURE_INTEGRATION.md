# ROMÁN — Mission Architecture Integration Amendment

**Supersedes:** any earlier prose that enumerates only fourteen scientific missions.
**Canonical registry:** `docs/missions/MISSION_REGISTRY.json`

ROMÁN is a peer mission in the common control plane. It is not nested under INGENIERO, ESPÍA or a global agent.

`MISSION CONTROL PLANE → ROMAN`

ROMÁN's domain is authorial/intellectual forensics. The common control plane owns discovery, authority checks, coordination and persistence protocol; ROMÁN owns its domain analysis.

## Canonical integration

- Identity: `ROMAN / ROMÁN`
- Type: `AUTHORIAL_INTELLECTUAL_FORENSIC`
- State: `docs/missions/roman/ROMAN_MISSION_STATE.json`
- Invocation: `docs/missions/roman/ROMAN_INVOCATION_CONTRACT.json`
- Bootstrap: `docs/missions/roman/ROMAN_BOOTSTRAP.md`
- Capabilities: `docs/missions/roman/ROMAN_CAPABILITY_MATRIX.json`
- Handoffs: `docs/missions/roman/ROMAN_HANDOFF_CONTRACT.json`
- Authority: `docs/missions/roman/ROMAN_AUTHORITY_SCOPE.json`
- Validation: `docs/missions/roman/ROMAN_VALIDATION_RESULTS.json`
- Adversarial tests: `docs/missions/roman/ROMAN_ADVERSARIAL_TESTS.json`
- Integration status: `docs/missions/roman/ROMAN_INTEGRATION_STATUS.json`

The existing fourteen-mission scientific decomposition remains valid for its original scope; ROMÁN is an additional orthogonal mission whose method is authorial/intellectual rather than a scientific subsystem specialization.

## Control-plane invariant

No ROMÁN invocation may alter another mission's identity, global voice, authority, or state without that mission's explicit authorized interface. No generated text produced by ROMÁN is admissible as authentic authorial evidence merely because ROMÁN produced it.
