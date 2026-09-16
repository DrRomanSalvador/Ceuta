# SCIENTIFIC FRONTIER CLOSURE 001

**Mission:** `SCIENTIFIC-AUDIT-CLOSURE`

**Active chain:** `CROSSREPO-PIT-BINDING-001` → `CROSSREPO-OUTCOME-ASCERTAINMENT-001` → `CROSSREPO-PROSPECTIVE-EVALUATION-001`

**Repository snapshot audited:** CeutIA `scientific-traceability-crossrepo` at PR #30 head `cf0ba13e0e52e17f5d1cd5429954f695d3c2c487`; SERPIENTE `main` at the inspected runtime files.

## 1. PIT semantic binding — closure at maximum supportable degree

### Scientific question
Does the forecast prove that the actual model input `X_t` was generated exclusively from the information set `H_t` available at the forecast origin?

### Invariant
`X_t = φ(H_t, θ_t, c_t)` where `H_t` is the exact visible information set, `φ` is a versioned derivation, `θ_t` its configuration/version, and `c_t` the source/feature visibility constraints.

### Repository evidence
SERPIENTE `PointInTimeStore.history_at(as_of)` filters observations by `known_at(as_of)` and `event_time <= as_of`, resolves revisions, and `fingerprint(as_of)` hashes the resulting serialized history. `LongitudinalForecaster.forecast(...)` accepts `X` independently and receives `point_in_time_fingerprint` as an opaque argument. The canonical v1.1 contract transports that fingerprint and protects the resulting payload with an integrity hash.

### Scientific result
The current architecture establishes **PIT_ATTESTATION**, not **PIT_SEMANTICALLY_VERIFIED**. Because `X` is independently supplied to the forecaster, a truthful fingerprint can coexist with a feature matrix containing future information. Cryptographic integrity of the fingerprint/payload cannot identify the provenance of the actual matrix.

### Identifiability result
Cases A, B, D, E and F can be represented by hashes/manifests if such artifacts are supplied; Case C/G cannot be rejected from the current v1.1 fingerprint alone because the producer does not bind the actual model-input derivation to `H_t`. Therefore semantic PIT validity is **NOT ESTABLISHED** under v1.1.

### Exact engineering handoff
A versioned extension is required unless existing producer lineage can bind the actual `X_t`. Minimum fields: `information_set_as_of`, `observation_manifest_hash`, `feature_manifest_hash`, derivation method/version, derivation configuration hash, source/revision visibility rule, feature availability cutoff, and reconstructible input lineage. Fail closed on future feature timestamps, unavailable source/revision, missing derivation identity, manifest mismatch, unknown transformation lineage, or unreconstructible eligibility. Required adversarial tests: valid derivation accepted; alternate derivation distinguished; future-information matrix rejected; tampered matrix rejected; wrong derivation version rejected; changed source revision distinguished; same fingerprint with different model input must never receive semantic-verification status.

**Status:** `SCIENTIFICALLY_CLOSED` for the *current scientific question as supportable from current architecture*, with the limitation retained and executable repair handoff required. **PIT_SEMANTICALLY_VERIFIED remains NOT ESTABLISHED.**

## 2. Outcome ascertainment — scientific closure assessment

### Scientific question
Can a persisted observed outcome be interpreted as the outcome corresponding to the forecast target and horizon, rather than merely an observed binary value that happens to be linkable to the prediction?

### Current verified controls
CeutIA requires prediction/decision/action/outcome identity, exact target match, timezone-aware outcome time, prediction availability before outcome, outcome time at or after the target horizon, persistence integrity, and one-to-one outcome identity. Future outcomes are rejected. Missing outcomes are excluded rather than imputed by the predeclared protocol.

### Material limitations
The current outcome table stores `outcome_id`, `target`, `outcome_time`, `observed`, provenance and recording time, but does not separately encode: ascertainment time, outcome source/version, revision identity, measurement process, censoring state, selection mechanism, competing-outcome status, or explicit outcome-definition version. Consequently `outcome_time` is not equivalent to complete outcome ascertainment. The evaluator cannot distinguish a stable measurement from a later revised/selected observation using the persisted outcome record alone.

### Adversarial cases
- Delayed ascertainment: **not distinguishable** from ordinary ascertainment when only `outcome_time` is stored.
- Revised outcome: **not separately represented**.
- Duplicate outcome: identity collision is protected.
- Missing outcome: excluded; no imputation.
- Partial observation/censoring: **not represented as a distinct state**.
- Source disagreement: **not represented as a structured competing-source relation**.
- Post-hoc correction: **not separately represented**.
- Outcome available only after evaluation: temporal eligibility can reject premature records, but availability/ascertainment is not independently persisted.
- Selection because outcome was observable: **not identified by the current schema**.
- Intervention-affected outcome: linkage to action exists, but causal contamination is not identified by the outcome schema.
- Outcome definition drift: **not separately versioned**.

### Exact engineering handoff: `CROSSREPO-OUTCOME-ASCERTAINMENT-001`
Affected repository: `DrRomanSalvador/Ceuta`.
Affected component: `backend/app/core/scientific/prediction_outcome_evaluation.py` and downstream aggregate evaluation.
Invariant: an eligible outcome must identify not only the measured target/time but also the ascertainment process and revision state needed to establish comparability with the forecast target.
Required fields: `outcome_definition_version`, `source_id`, `source_version`, `observation_time`, `availability_time`, `ascertainment_time`, `revision_id/version`, `measurement_process_id/version`, `censoring_status`, `missingness_status`, `selection_status`, `transformation_id/version`, and provenance/integrity identity.
Forbidden behavior: treating `outcome_time` as proof of ascertainment completeness; imputing missing outcomes as observed; silently selecting a convenient source; using revised information to retroactively alter an earlier evaluation without recording revision semantics.
Acceptance tests: delayed availability rejected for an evaluation time before availability; revision creates a distinct version and does not silently rewrite historical eligibility; duplicate identity rejected; missing/censored state remains unevaluated rather than imputed; conflicting sources remain distinguishable; changed outcome definition fails target comparability; post-intervention outcome is marked as intervention-exposed rather than ordinary untreated outcome.
Scientific claim affected: **prospective predictive validity**.

**Status:** `REPAIR_REQUIRED` / `HANDOFF_REQUIRED`. Outcome ascertainment is **NOT ESTABLISHED** beyond basic temporal/identity eligibility.

## 3. Prospective evaluation — closure assessment

### Scientific question
What evidence would establish `PROSPECTIVE_PREDICTIVE_VALIDITY` rather than functional or retrospective coherence?

### Existing protocol
`CEUTIA-SERPIENTE-PREDICTIVE-EVAL-1` is predeclared. It requires canonical v1.1 integrity, availability-before-replay, exact target/horizon matching and point-in-time fingerprint presence. It explicitly states that retrospective replay and fixtures do not establish prospective validity. Primary metrics are Brier score and log loss; aggregate output is descriptive; missing outcomes are excluded; repeated forecasts are not assumed independent; causal validity is explicitly not established.

### Scientific requirement
Prospective validity requires a locked evaluation window in which forecasts are generated before outcomes, the prospective information set is reconstructible, target/horizon are predeclared, outcomes are prospectively ascertained with revision semantics, the evaluation procedure is frozen, and comparator/baseline rules are fixed before observing the evaluation outcomes.

### Current limitations
1. No real prospective outcome population is available in the repository evidence.
2. Current endpoint has no matched baseline forecast channel transported without retrospective leakage.
3. Repeated forecasts are evaluable descriptively but no dependence-aware inferential procedure is implemented.
4. Distribution/regime shift and intervention feedback are monitored only partially; no prospective validation across intervention regimes is established.
5. Calibration is computed/ reported descriptively, but prospective calibration validation requires the same prospective evaluation population.

### Required prospective falsification
A prospective evaluation must pre-register the forecast population, origin/horizon, target, model/code/configuration versions, PIT eligibility artifact, outcome ascertainment rules, baseline/comparator, scoring rules and missing/censoring policy. During the locked window, predictions must be immutable after origin. Evaluation must fail closed if a forecast uses information unavailable at origin, if the outcome was unavailable before the evaluation decision point, if target definition changed, or if model/version metadata cannot be reconstructed.

### Baseline integrity
The baseline must be generated at the same forecast origin using only information available at that origin. Retrospective construction from realized outcomes is forbidden. If the cross-repository contract cannot transport the baseline identity/output, comparative predictive utility remains **NOT ESTABLISHED**.

### Repeated forecasts
Evaluation unit is the forecast-origin/target/horizon tuple, but repeated forecasts can share observations, outcomes and rolling-window inputs. Naive standard errors, confidence intervals or hypothesis tests are forbidden until a dependence-aware method is specified and validated.

### Intervention feedback
A forecast that triggers a decision/action changes the data-generating process potentially through both the target state and the measurement/reporting process. Post-action outcomes therefore cannot automatically be interpreted as untreated predictive outcomes. Predictive performance and intervention effectiveness remain separate estimands. Causal effectiveness is **NOT ESTABLISHED**.

### Exact engineering/scientific handoff: `CROSSREPO-PROSPECTIVE-EVALUATION-001`
Required artifact: immutable prospective evaluation-window manifest plus locked forecast registry, PIT lineage references, outcome ascertainment references, baseline references, model/code/configuration versions and evaluation procedure hash.
Acceptance criteria: no forecast can be scored if eligibility is not reconstructible; no outcome can be scored if ascertainment/version semantics are incomplete; baseline is origin-time valid; repeated-forecast dependence is disclosed and no unsupported inferential claim is emitted; intervention-exposed outcomes are stratified or excluded from untreated predictive estimands; calibration and proper scoring are reported only for the predeclared prospective population.

**Status:** `BLOCKED_EXTERNAL` for empirical prospective validity because the required real prospective outcome population does not exist in the repository/evidence available to this mission. The software can prepare the evaluation, but it cannot manufacture the missing real-world prospective outcomes.

## 4. Calibration, baseline, dependence and feedback closure

- **Calibration:** protocol and model-side calibration machinery exist; prospective calibration is `NOT_ESTABLISHED` until a real prospective population is observed under the locked protocol.
- **Baseline integrity:** baseline methods exist inside SERPIENTE, but the cross-repository endpoint does not transport a paired predeclared baseline output. Comparative utility is `NOT_ESTABLISHED`.
- **Repeated forecast dependence:** explicitly documented; descriptive evaluation is permitted, inferential claims are not.
- **Intervention feedback:** explicitly documented as a separate estimand problem; causal effectiveness is `NOT_ESTABLISHED`.

## 5. Scientific claim governance

| Claim | Status |
|---|---|
| Cross-repository transport functions | VERIFIED by repository tests |
| Canonical contract integrity | VERIFIED |
| PIT fingerprint represents a point-in-time history | EMPIRICALLY SUPPORTED by producer implementation/tests |
| Exact model-input semantic PIT binding | NOT ESTABLISHED |
| Basic outcome temporal eligibility | VERIFIED |
| Complete outcome ascertainment semantics | NOT ESTABLISHED |
| Retrospective/descriptive prediction evaluation | VERIFIED / DESCRIPTIVE |
| Prospective predictive validity | NOT ESTABLISHED |
| Prospective calibration validity | NOT ESTABLISHED |
| Comparative utility vs baseline | NOT ESTABLISHED |
| Dependence-aware inferential validity | NOT ESTABLISHED |
| Causal effectiveness | NOT ESTABLISHED |

## 6. Mission stop condition

The finite scientific closure chain is **not fully closed** because a genuine external blocker remains: a real prospective outcome population is absent. The repository-side scientific work is closed to the maximum supportable degree for the currently inspectable surfaces, and exact engineering handoffs are persisted for the remaining repairable defects. No stronger scientific claim is authorized.
