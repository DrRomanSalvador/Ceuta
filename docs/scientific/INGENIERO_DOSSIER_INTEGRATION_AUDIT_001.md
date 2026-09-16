# INGENIERO — Dossier-to-Capability Integration Audit 001

## Scope

This audit is the first persistent reconciliation pass for the 2026-09-16 INGENIERO integration contract. It audits the current CeutIA branch `scientific-traceability-crossrepo` and the current SERPIENTE `main` repository surface. The contract itself is not treated as empirical evidence.

## CeutIA: verified existing capability surfaces

- `backend/app/core/scientific/scientific_traceability.py` provides a durable source/claim/constraint/mechanism/method/data/implementation/runtime/governance/provenance/cross-repo/output/outcome/validation trace graph.
- `backend/app/core/scientific/scientific_runtime_contract.py` provides reference-class, novelty/OOD, causal and robustness gates plus an integrity-chained runtime assessment ledger.
- `backend/app/core/scientific/scientific_method_registry.py` provides versioned method releases with assumptions, applicability boundaries, source IDs and code/configuration identity.
- `backend/app/core/scientific/cross_repo_contract.py` provides the canonical CeutIA-side SERPIENTE prediction message and integrity hash.
- `backend/app/core/scientific/cross_repo_consumer.py` enforces transport, decision-time temporal eligibility, OOD, calibration and source-independence constraints.
- The repository contains decision persistence/lifecycle, causal contracts and prospective-evaluation infrastructure.
- Mission memory already records PIT, temporal semantics, source-process intelligence, interaction drift, emergent joint anomalies, incremental predictive value, regime change, response lineage, VOI and four-plane monitoring as accumulated scientific knowledge with explicit implementation limits.

## SERPIENTE: verified existing capability surfaces

- `backend/app/contracts.py` already distinguishes observations, events, signals, forecasts and alerts and preserves event/publication/acquisition times, provenance, uncertainty components and PIT fingerprint.
- `backend/app/pit_binding.py` and the documented runtime implement point-in-time and revision-aware forecast history.
- `backend/app/prediction.py` provides forecasting infrastructure; README states chronological holdout, calibration, baseline comparison, model comparison, leakage checks and distribution-drift testing.
- `backend/app/ceutia_boundary.py` emits a versioned CeutIA prediction envelope with provenance, uncertainty, regime and PIT identity.
- `backend/app/outcomes.py` provides prospective outcome capture.
- Source registry/catalogue, ingestion, mapping, longitudinal state, interactions and security controls are present.
- README explicitly states that repository engineering/prospective infrastructure does not establish real-world predictive effectiveness, deployment calibration, intervention effectiveness or causal benefit.

## Newly implemented by this integration pass

1. CeutIA `epistemic_contracts.py` now makes E0-E8, non-monotonic epistemic states, multidimensional evidence, explicit temporal semantics, observation-process modelling, claim/hypothesis/prediction/decision/intervention/outcome/model contracts and adjacent promotion gates executable.
2. CeutIA `governance_contracts.py` now makes VOI identifiability, research-task stopping criteria, variable semantics, scientific debt and validation-layer evidence contracts executable.
3. CeutIA `PERPLEXITY_SCIENTIFIC_INTEGRATION_LEDGER.json` now provides cumulative reconciliation state and forbids silent replacement of earlier propositions.
4. CeutIA `SCIENTIFIC_CAPABILITY_MATRIX_CEUTIA_SERPIENTE.json` now separates implementation state from software/scientific/prospective/external/operational validation.
5. SERPIENTE `scientific_integration_contracts.py` now preserves point-in-time prediction identity, benchmark applicability/exclusion, metric meaning, model change-control and observation-process metadata.
6. SERPIENTE tests cover these new contracts.

## Explicit gaps discovered

### A. Evidence/epistemology

- The existing trace graph is generic and durable, but a complete runtime blast-radius/revalidation engine is not yet demonstrated.
- Existing scientific runtime gates do not by themselves implement the full E0-E8 promotion lifecycle or claim demotion/expiry workflow; the new contracts are the first executable boundary.
- Contradictory evidence is represented in mission memory and claim surfaces, but a complete claim-review engine that automatically identifies all affected downstream objects remains pending.

### B. Observation process

- SERPIENTE observations carry source/dataset/variable/temporal/provenance fields, but a universal observation-process object that formally separates latent territorial state from ascertainment/reporting/denominator changes across all domains is not yet implemented.
- The new `ObservationProcessModel` and `ObservationProcessDescriptor` are design/contract capabilities, not evidence that all source adapters expose the required metadata.

### C. Prediction

- PIT and revision controls are implemented, but the new contract requires explicit `information_cutoff`, `observation_vintage`, per-feature availability, target/outcome definitions and model identity as a unified prediction record. Existing cross-repo v1.1 already contains several of these semantics but not all in one typed contract.
- Prospective predictive validity remains external and unestablished.

### D. Decision/intervention/outcome

- Decision lifecycle and outcome capture exist, but the complete warning -> decision -> intervention -> outcome -> dual evaluation chain is not yet demonstrated as one cross-repository persistent runtime lineage.
- Prediction validity, decision validity, effectiveness and prevention remain distinct claims.

### E. VOI/research prioritisation

- VOI is correctly constrained to a framework until utility, research cost, delay cost and risk are identifiable. No numeric NVOI is fabricated.
- Full VOI computation therefore remains `DESIGNED_PENDING_DATA`.

### F. Model change/continual learning

- SERPIENTE has versioning, calibration and evaluation surfaces. The complete observe -> assess -> propose -> validate -> approve -> deploy -> monitor -> rollback state machine is not yet demonstrated as a single enforced runtime gate.

### G. Cross-repository validation

- CeutIA↔SERPIENTE prediction transport is implemented and adversarially tested on the existing contract.
- The current integration pass adds richer contracts but does not silently claim that the transport schema has been upgraded to those richer fields.

## Validation boundary

`CI_GREEN` remains software evidence only. No repository test establishes prospective real-world predictive validity, causal effect, intervention effectiveness, prevention or equity outcomes.

The current CeutIA branch has an outstanding control-plane CI failure at the latest observed commit during this integration pass. The scientific workflow was still running when this audit was persisted. Therefore this document is an intermediate audit checkpoint, not a fixed-point declaration.
