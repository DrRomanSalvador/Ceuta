# SCIENTIFIC CAPABILITY IMPLEMENTATION STATUS

This registry records executable integration status for the scientific capability layer. It deliberately distinguishes engineering evidence from scientific, prospective, operational, and client validation.

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
| Calibration diagnostics | UNIT_TESTED | reliability curve, calibration slope diagnostic, mean absolute calibration error, sharpness | Real forecast calibration and calibration validation on locked data |
| Incremental value | UNIT_TESTED | baseline-vs-candidate delta object | End-to-end benchmark with real information increments |
| Decision utility | UNIT_TESTED | expected binary loss and recorded decision/outcome primitive | Real intervention/outcome utility evaluation |
| Scientific reproducibility | INTEGRATION_TESTED | immutable execution metadata, canonical digests, PIT cutoff checks | Complete production model registry/environment capture across all forecast producers |
| Scientific persistence/replay | INTEGRATION_TESTED | `SCIENTIFIC_EXECUTION` events on canonical hash-chained event log; exact retry idempotency and replay tests | Cross-repository production deployment and long-running operational replay |
| Causal identification boundary | UNIT_TESTED | explicit estimand/design/assumption assessment; `NOT_IDENTIFIABLE` preserved | Identified real-world estimands with adequate design/data |
| Digital-twin boundary | UNIT_TESTED | simulation remains `SIMULATION` until state/synchronization/bidirectionality/parameter-update/validation/outcome requirements are present | Any scientifically validated digital twin |
| Alert governance | INTEGRATION_TESTED | `AlertGovernance`; external delivery fails closed until governance/response/appeal/anti-stigma/simulation controls are satisfied | Operational validation and real response-capacity evidence |
| Response coupling | INTEGRATION_TESTED | response binding/sink tests and explicit decision boundary | Causal effectiveness |
| Closed-loop learning | FORMALIZED | response/outcome boundary and utility primitives exist; prospective outcome path exists in SERPIENTE | Verified intervention → outcome → evaluation → model update runtime loop |
| Advanced ML/deep learning | FORMALIZED | baseline-before-complexity boundary | A real baseline-defeating dataset/model result |
| Public automated alerts | FORMALIZED + FAIL-CLOSED | governance boundary blocks external delivery by default | Operational validation, drills, appeal mechanism deployment |
| Cross-domain propagation | INTEGRATION_TESTED | SERPIENTE `TrajectoryEngine` now requires explicit `PropagationLink` evidence; no domain-combination shortcut | Empirical validation that links represent real propagation rather than shared cause/measurement process |

## Important semantic correction

SERPIENTE previously derived cross-domain propagation by constructing a complete graph whenever multiple domains were present. That conflated co-occurrence/domain diversity with interaction or propagation. The runtime now requires explicit signal-to-signal propagation evidence with a declared lag and evidence identity. Without such links, propagation and cascade are zero rather than inferred.

## Status semantics

`UNIT_TESTED` means the executable primitive has tests. `INTEGRATION_TESTED` means the primitive is connected to an existing runtime or persistence boundary and tested there. Neither status implies scientific validity.

`SCIENTIFICALLY_VALIDATED`, `PROSPECTIVELY_VALIDATED`, `OPERATIONALLY_VALIDATED`, `CLIENT_VALIDATED`, and `ESTABLISHED` are not assigned merely because software exists or CI passes.

## Current engineering boundary

The internally executable scientific subset now includes temporal eligibility/vintage representation, observation-process representation, dynamic denominator binding, denominator-bound rate uncertainty, identifiability preservation, rolling-origin baselines, probabilistic scoring/calibration diagnostics, incremental comparison, decision-loss computation, explicit scientific execution provenance, canonical persistence/replay, causal non-identifiability boundaries, digital-twin boundaries, and fail-closed alert governance.

The remaining scientific frontier is not safely fabricable: empirical parameter identification, real historical vintages, validated population/mobility denominators, real outcome definitions, prospective outcomes, identified causal estimands, intervention utility, operational alert validation, and client validation require appropriate data, design, authority, or real-world operation. They remain explicitly unvalidated rather than being promoted by engineering status.

## Verified engineering checkpoint

The branch was at `b3af7d8e3169547b45ab3dcef9baa08fa0e03901` when CeutIA CI run `35125790123` completed SUCCESS. That run verified compileall, direct-CAS audit, canonical event replay audit, 168-unit-test execution including the scientific suites, and authoritative bootstrap. SERPIENTE CI run `35125274186` also completed SUCCESS, including runtime tests, PostgreSQL persistence integration, security checks, dependency audit, Compose validation, and runtime image build.

This checkpoint is technical evidence only. It does not promote any scientific capability to `SCIENTIFICALLY_VALIDATED`, `PROSPECTIVELY_VALIDATED`, `OPERATIONALLY_VALIDATED`, `CLIENT_VALIDATED`, or `ESTABLISHED`.
