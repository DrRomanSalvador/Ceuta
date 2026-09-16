# Mission Collaboration Graph — CeutIA + SERPIENTE

The graph defines default scientific information flow. It is not a command hierarchy.

## Core flow

`BIBLIOTECARIO → ESPÍA → INGENIERO`

`BIBLIOTECARIO → NOTARIO → ESPÍA`

`GROK → all mission owners`

`FORJA ↔ CRONOS ↔ ATLAS ↔ NEXO ↔ ORÁCULO ↔ CENTINELA ↔ ESTRATEGA`

`MÉDICO ↔ ESPÍA / ATLAS / CRONOS / CENTINELA`

`ABISMO ↔ FORJA / NEXO / ORÁCULO / CENTINELA`

`NOTARIO ↔ all missions`

## Required collaboration interfaces

| From | To | Purpose | Expected artifact |
|---|---|---|---|
| BIBLIOTECARIO | ESPÍA | deliver discovered scientific evidence | Evidence Retrieval Packet |
| BIBLIOTECARIO | NOTARIO | expose source/provenance for verification | Source Provenance Packet |
| ESPÍA | INGENIERO | translate science into executable requirement | Scientific Engineering Handoff |
| GROK | any owner | falsification and repair | Adversarial Finding |
| FORJA | ORÁCULO | estimands, uncertainty, calibration, scoring | Forecast Statistical Contract |
| CRONOS | ORÁCULO | point-in-time origin/horizon and temporal leakage control | Temporal Forecast Contract |
| ATLAS | ESPÍA | spatial/population interpretation | Spatial-Population Constraint |
| ATLAS | ORÁCULO | spatial denominators and dependence | Spatial Forecast Constraint |
| NEXO | ORÁCULO | dynamic coupling features/models | Coupled Forecast Specification |
| NEXO | CENTINELA | propagation/cascade signals | Propagation Warning Contract |
| ORÁCULO | CENTINELA | predictive distributions and uncertainty | Forecast-to-Warning Packet |
| CENTINELA | ESTRATEGA | warning performance and lead-time consequences | Warning Decision Packet |
| ORÁCULO | ESTRATEGA | predictive distributions and decision value | Forecast Decision Packet |
| MÉDICO | ESPÍA | health-domain interpretation and case/outcome definitions | Health Interpretation Packet |
| MÉDICO | CENTINELA | clinically meaningful event definitions | Health Warning Contract |
| ABISMO | NEXO | tail dependence and cascade stress | Tail-Coupling Packet |
| ABISMO | CENTINELA | extreme-event warning requirements | Extreme Warning Contract |
| NOTARIO | all | evidence/provenance status | Evidence/Claim Ledger |
| ESTRATEGA | INGENIERO | explicit decision/utility requirements | Decision Implementation Contract |
| INGENIERO | all | runtime/test evidence and implementation state | Runtime Evidence Packet |

## Conflict protocol

When two missions disagree:

1. State the exact proposition in dispute.
2. Separate data disagreement from methodological disagreement.
3. Identify each mission's assumptions and evidence.
4. Ask GROK for adversarial reproduction when material.
5. Ask NOTARIO to classify evidence status.
6. Ask ESPÍA to integrate the scientific conclusion.
7. Ask INGENIERO only for implementation consequences, not scientific arbitration.
8. Persist the disagreement if unresolved.

## No circular authority

No mission may validate its own claim solely because it produced it. Where feasible, validation is separated from generation:

- BIBLIOTECARIO discovers → NOTARIO verifies provenance → ESPÍA interprets.
- FORJA formulates → GROK attacks → ORÁCULO/CRONOS validate predictive/temporal implications.
- ORÁCULO predicts → CENTINELA evaluates warning use → ESTRATEGA evaluates decision value.
- NEXO proposes coupling → FORJA checks identifiability → GROK attacks → prospective evaluation tests performance.
- INGENIERO implements → tests/CI/runtime verify execution → ESPÍA/NOTARIO verify scientific meaning.

## Persistence rule

Every collaboration artifact must carry:

`source_mission, target_mission, timestamp, proposition, evidence_level, assumptions, artifact/repository_reference, validation_status, unresolved_uncertainty, next_action`.

This graph is intentionally sparse. New edges require a recurring scientific need, a differentiated method, and a measurable reduction in blind spots.
