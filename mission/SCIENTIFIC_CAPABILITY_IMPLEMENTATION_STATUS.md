# SCIENTIFIC CAPABILITY IMPLEMENTATION STATUS

This registry records executable integration status for the scientific capability gates. It deliberately distinguishes engineering evidence from scientific or prospective validation.

| Capability | Current state | Executable evidence | Not established |
|---|---|---|---|
| Point-in-time / vintage integrity | UNIT_TESTED | `ObservationRecord`, `knowledge_time`, `vintage_id`, `point_in_time_filter`, revision-vintage tests | Full historical vintage reconstruction across production sources; prospective validation |
| Existing canonical temporal eligibility | INTEGRATION_TESTED | `EvidenceContract.available_at`, `TemporalEligibility`, existing control-plane CI | Complete source-specific revision history |
| Observation process | UNIT_TESTED | `ObservationProcess`, forward observation operator and guarded inversion | Empirical estimation of detection/reporting/coverage parameters |
| Dynamic denominator | INTEGRATION_TESTED | `DynamicDenominator` integrated into `RiskCalculator`; numerator-only rate blocked | Validated population/mobility denominator feeds |
| Rate uncertainty | UNIT_TESTED | Wilson interval implemented for denominator-bound integer event counts | Outcome-specific statistical validation beyond binomial assumptions |
| Latent-state identifiability | UNIT_TESTED | explicit identifiability state; non-identifiability requires equivalent alternatives | Domain-specific latent-state estimators and empirical identification |
| Baselines | UNIT_TESTED | persistence and rolling-origin baseline primitives | Full outcome-specific benchmark registry and external/historical benchmark |
| Probabilistic forecasting metrics | UNIT_TESTED | Brier, log score, normal CRPS, calibration-in-the-large | Real SERPIENTE forecast streams and locked prospective evaluation |
| Incremental value | UNIT_TESTED | baseline-vs-candidate delta object | End-to-end benchmark with real information increments |
| Decision utility | UNIT_TESTED | expected binary loss and recorded decision/outcome primitive | Real intervention/outcome utility evaluation |
| Alert governance | INTEGRATION_TESTED | `AlertGovernance`; external delivery fails closed until governance/response/appeal/anti-stigma/simulation controls are satisfied | Operational validation and real response-capacity evidence |
| Response coupling | INTEGRATION_TESTED | existing response binding/sink tests and scientific decision boundary | Causal effectiveness |
| Causal identification | FORMALIZED | epistemic boundary and explicit causal statuses | Identified estimands with adequate design/data |
| Closed-loop learning | FORMALIZED | response/outcome boundary and utility primitives exist | Verified intervention → outcome → evaluation → update runtime loop |
| Digital twin | FORMALIZED | explicit simulation/twin distinction in scientific gates | Identifiable state, calibrated parameters, synchronization and outcome validation |
| Advanced ML/deep learning | FORMALIZED | baseline-before-complexity gate | A real baseline-defeating dataset/model result |
| Public automated alerts | FORMALIZED + FAIL-CLOSED | governance boundary blocks external delivery by default | Operational validation, drills, appeal mechanism deployment |

## Status semantics

`UNIT_TESTED` means the executable primitive has tests. `INTEGRATION_TESTED` means the primitive is connected to an existing runtime boundary and tested there. Neither status implies scientific validity.

`SCIENTIFICALLY_VALIDATED`, `PROSPECTIVELY_VALIDATED`, `OPERATIONALLY_VALIDATED`, and `ESTABLISHED` are not assigned merely because software exists or CI passes.

## Current engineering boundary

The immediately executable scientific subset now includes temporal eligibility/vintage representation, explicit observation-process representation, dynamic denominator binding, denominator-bound rate uncertainty, identifiability preservation, rolling-origin persistence baselines, probabilistic scoring/calibration primitives, baseline incremental comparison, decision-loss computation, and fail-closed alert governance.

The remaining scientific frontier is not a software omission that can safely be fabricated away: empirical parameter identification, real historical vintages, real outcome definitions, prospective outcomes, causal estimands/designs, real intervention utility, and operational alert validation require appropriate data, design, or external authority. They remain explicitly unvalidated rather than being promoted by engineering status.
