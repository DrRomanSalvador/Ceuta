# BIBLIOGRAPHY-DEEP-EXTRACTION-001

**Status:** ACTIVE — INITIAL DEEP EXTRACTION
**Owner:** ESPÍA
**Scope:** CeutIA + SERPIENTE
**Purpose:** canonical, auditable extraction of recoverable scientific sources into operational scientific knowledge. This document is an extraction ledger, not a bibliography dump.

## 0. Coverage boundary

The repository currently contains a scientific normative layer and several scientific audit/handoff documents, but no single machine-readable bibliography manifest containing all external literature. Therefore this first ledger records the externally recoverable sources already material to the scientific architecture and the primary/authoritative sources recovered during this audit. It does **not** claim that the external literature universe is exhausted.

The absence of a bibliography manifest is itself a `PROVENANCE / EPISTEMOLOGICAL DEBT` item. Future bibliographic inputs MUST enter this ledger or an explicitly superseding versioned registry.

## 1. Source registry

| ID | Source | Type | Scientific role | Current integration state |
|---|---|---|---|---|
| BIB-001 | Collins et al., TRIPOD+AI, BMJ 2024;385:e078378, DOI 10.1136/bmj-2023-078378 | GUIDELINE | transparent reporting of prediction-model studies using regression/ML | PARTIALLY INTEGRATED through prediction-validation requirements; not a quality score |
| BIB-002 | Moons et al., PROBAST Explanation and Elaboration, Ann Intern Med 2019;170:1, DOI 10.7326/M18-1377 | METHOD / GUIDANCE | risk of bias and applicability of prediction-model studies | PARTIALLY INTEGRATED; domains must remain separate from reporting and validation |
| BIB-003 | W3C PROV-O Recommendation, 2013 | STANDARD | interoperable provenance model | PARTIALLY INTEGRATED conceptually through provenance/version/derivation requirements; ontology mapping not established |
| BIB-004 | Scheffer et al., Early-warning signals for critical transitions, Nature 2009;461:53–59, DOI 10.1038/nature08227 | THEORETICAL / SYNTHESIS | generic precursor signals for critical transitions | SCIENTIFIC REFERENCE; not an operational predictive claim |
| BIB-005 | Dakos et al., Methods for detecting early warnings of critical transitions, PLOS ONE 2012;7:e41010, DOI 10.1371/journal.pone.0041010 | METHOD | estimation/testing of early-warning indicators in time series | SCIENTIFIC REFERENCE; real-time/generalization validation absent |
| BIB-006 | Early warning signals of infectious disease transitions: a review, 2021, PMCID PMC8479360, PMID 34583561 | SECONDARY SYNTHESIS | disease-transition EWS, data-poor limitations, synthetic/historical validation before real-time use | SCIENTIFIC REFERENCE; directly relevant to epidemiological Ceuta use |
| BIB-007 | Gneiting, Balabdaoui & Raftery, Probabilistic forecasts, calibration and sharpness, JRSS-B 2007;69:243–268, DOI 10.1111/j.1467-9868.2007.00587.x | THEORETICAL / METHOD | proper probabilistic forecast evaluation, calibration and sharpness | PARTIALLY INTEGRATED in forecast calibration semantics |
| BIB-008 | Vickers & Elkin, Decision curve analysis, Med Decis Making 2006;26:565–574, DOI 10.1177/0272989X06295361 | METHOD | decision-analytic evaluation of predictive models | NOT YET IMPLEMENTED as a decision-validity layer |
| BIB-009 | Heath et al., Simulating Study Data to Support EVSI Calculations, Med Decis Making 2022;42:2, DOI 10.1177/0272989X211026292 | METHOD | expected value of sample information for research prioritization/design | SCIENTIFIC CANDIDATE; no autonomous VOI computation established |

## 2. Deep extraction: BIB-001 TRIPOD+AI

### Scientific question
How should prediction-model studies using regression or machine learning be reported so that model development/evaluation, transparency, fairness, applicability and reproducibility can be assessed?

### Design / evidentiary status
Reporting guideline, not an empirical validation study and not a quality score. It specifies reporting content; it does not demonstrate that a model is valid merely because the items are reported.

### Mathematical/statistical content relevant to CeutIA/SERPIENTE
The source is not a new forecasting estimator. Its operational value is the explicit decomposition of a prediction study into target, population/context, predictors, model/development procedure, evaluation design, performance, subgroup/fairness considerations, limitations and transparency/open-science information.

### Operational consequence
SERPIENTE prediction records should be able to reconstruct, where applicable:
- target/outcome definition and version;
- intended population/context;
- predictor/input manifest;
- model/protocol version;
- development/evaluation design;
- comparator/baseline;
- evaluation population and eligibility;
- subgroup performance/applicability;
- discrimination, calibration and probabilistic scoring;
- missingness/censoring/selection handling;
- limitations and unresolved bias;
- provenance/derivation chain.

### Failure modes
Reporting completeness can be mistaken for scientific validity. TRIPOD+AI does not establish prospective validity, causal validity, external validity or effectiveness.

### Falsification test
Attempt to construct a fully reported prediction record whose prospective performance is nevertheless poor. Expected result: reporting completeness remains compatible with predictive failure; therefore reporting status cannot promote validation state.

### CeutIA/SERPIENTE mapping
`SOURCE -> PREDICTION_EVALUATION_RECORD -> CLAIM/VALIDATION_STATE`.

### Current gap
A versioned prediction-evaluation record is not yet established as the complete canonical cross-repository contract. Existing protocol and PIT contracts cover parts of this requirement.

## 3. Deep extraction: BIB-002 PROBAST

### Scientific question
What risk of bias and applicability concerns can compromise prediction-model study results?

### Design
Structured methodological appraisal framework covering participants, predictors, outcome and analysis domains, with signaling questions and judgments of risk of bias/applicability.

### Operational consequence
Bias assessment must remain multidimensional. It must not be collapsed into a single scientific score that hides which domain failed.

### Key system risks exposed
- inappropriate participant selection;
- predictor definition/measurement problems;
- outcome definition/measurement problems;
- analysis problems including overfitting and handling of missing data;
- mismatch between study population/context and intended use.

### Falsification test
For any apparently strong forecast result, independently inspect each PROBAST domain. A favorable metric with a high-risk domain must not be promoted to general validity.

### CeutIA/SERPIENTE mapping
`MODEL/PREDICTION -> BIAS/APPLICABILITY ASSESSMENT -> VALIDATION BOUNDARY`.

### Limitation
PROBAST is an appraisal framework; it is not prospective validation, calibration, decision utility, causal identification or effectiveness evidence.

## 4. Deep extraction: BIB-003 W3C PROV-O

### Scientific question
How can provenance be represented and exchanged across heterogeneous systems?

### Formal structure
PROV-O represents provenance using `Entity`, `Activity`, and `Agent`, with relations including derivation, generation, attribution, usage, timing and association. The model can be specialized for domain-specific provenance.

### Operational consequence
CeutIA/SERPIENTE should be able to represent not only a source URL but the provenance chain of derived artifacts: source/version -> acquisition activity -> observation/data entity -> transformation -> evidence/model/prediction artifact -> agent/process.

### Important distinction
PROV-O is a provenance representation standard, not evidence that a scientific claim is true. Provenance improves traceability and reproducibility but does not establish validity.

### Falsification test
Create two analytically identical outputs derived from different source versions or transformation paths. If provenance cannot distinguish them, provenance integrity is insufficient.

### Current gap
The repositories have explicit provenance requirements and source/version identity but no demonstrated complete PROV-O-compatible cross-repository serialization contract.

## 5. Deep extraction: BIB-004 Scheffer et al. 2009

### Scientific question
Can generic dynamical changes provide warning that a complex system is approaching a critical transition?

### Mechanistic concept
Near some critical transitions, recovery from perturbations can slow. Statistical manifestations can include increasing variance and lag-1 autocorrelation, among other system-dependent indicators. These are conditional early-warning mechanisms, not universal catastrophe predictors.

### Formal implication
For a scalar series x_t, candidate indicators include rolling variance `Var_w(x)` and lag-1 autocorrelation `AC1_w(x_t, x_{t-1})`. Their interpretation depends on the underlying dynamical regime, sampling, noise and filtering.

### Critical assumptions
- a relevant critical transition exists;
- the measured variable reflects the changing system state;
- sampling is adequate;
- observation noise/process does not dominate the signal;
- the indicator-response relationship is applicable to the system under study.

### Alternative explanations
1. changing surveillance/measurement variance can mimic increasing variance;
2. changing sampling frequency can alter autocorrelation;
3. common external forcing can create apparent persistence;
4. finite-window/statistical noise can create apparent trends;
5. ordinary nonstationarity can resemble a critical-transition precursor.

### Falsification task
Before accepting rising variance/AC1 as a precursor, test observation-process stability, sampling changes, exogenous forcing and matched null/baseline simulations.

### Product boundary
Supports possible `CHANGE_DETECTION / REGIME_DETECTION / EARLY_WARNING` research. It does not establish `FORECAST_OF_CATASTROPHE`, `CAUSAL_EXPLANATION` or `INTERVENTION_EFFECTIVENESS`.

## 6. Deep extraction: BIB-005 Dakos et al. 2012

### Scientific question
How can early-warning indicators be estimated from time series and how should their trends be assessed?

### Methodological content
The work operationalizes time-series early-warning indicators using moving windows and tests their trends. The method is illustrated on simulated ecological systems, making the distinction between method demonstration and real-world prospective performance essential.

### Statistical hazards
Window length, detrending, smoothing, autocorrelation structure, noise, sampling density and finite series length affect indicator behavior. A significant trend in an indicator is not equivalent to a validated warning rule.

### Required validation
Synthetic recovery -> historical backtest -> temporal holdout -> prospective accruing data -> external systems, with false-alarm and lead-time characterization.

### Current consequence
SERPIENTE should not expose generic critical-transition indicators as production catastrophe alerts until the target transition, reference class, baseline/null, lead time and false-alarm behavior are predeclared and prospectively evaluated.

## 7. Deep extraction: BIB-006 infectious-disease EWS review

### Scientific question
What early-warning signals have been studied for infectious-disease transitions, and under what conditions might they be useful?

### Important evidence boundary
The review emphasizes that exact EWS trajectories depend on the transition and that methods should be validated with synthetic and historical datasets before use with accruing real-time data. It also highlights data-poor settings as a major challenge.

### Ceuta translation
For epidemiological signals, candidate EWS must carry:
- surveillance-process state;
- reporting intensity;
- case-definition/version;
- denominator/exposed population;
- testing/diagnostic intensity where available;
- missingness/revision;
- lead time;
- false-alarm rate;
- target transition definition.

### Falsification
If EWS trend disappears after adjustment for surveillance intensity or reporting process, the original interpretation must be downgraded to measurement-process change rather than disease-transition evidence.

## 8. Deep extraction: BIB-007 Gneiting et al. 2007

### Scientific question
How should probabilistic forecasts be evaluated so that calibration and concentration/sharpness are distinguished?

### Mathematical content
A probabilistic forecast is a predictive distribution `F_t` for future outcome `Y_t`. Calibration concerns statistical consistency between predictive distributions and realized observations. Sharpness concerns concentration of the predictive distributions and is a property of the forecasts themselves.

Proper scoring rules provide coherent forecast evaluation; the paper discusses probability integral transform diagnostics and related calibration tools.

### Operational consequence
SERPIENTE must not optimize sharpness alone. A narrow forecast that is systematically miscalibrated is not scientifically superior to a broader calibrated forecast.

### Falsification
Construct a forecast family with increasingly narrow intervals but biased probabilities. If the evaluation rewards concentration without calibration, the evaluation contract is scientifically defective.

### Current gap
Current SERPIENTE calibration/scoring semantics are stronger than raw probability output but do not establish prospective calibration under future regime/measurement-process change.

## 9. Deep extraction: BIB-008 Vickers & Elkin 2006

### Scientific question
Can prediction models be evaluated by the clinical/decision consequences of using their outputs rather than accuracy alone?

### Core concept
Decision curve analysis evaluates net benefit across decision thresholds, incorporating the relative consequences of false positives and false negatives. In generic form, net benefit for threshold `p_t` can be written as:

`NB(p_t) = TP/N - FP/N * p_t/(1-p_t)`

under the assumptions of the decision-curve framework.

### Translation to institutional decision support
A predictive improvement can be operationally irrelevant if it does not improve the decisions that matter. Conversely, a modest predictive improvement can matter when error costs are asymmetric. The system therefore needs a decision-utility layer distinct from forecast performance.

### Limitations
Decision curves do not themselves prove causal effectiveness of acting on a model. Thresholds, utilities and decision contexts must be explicitly specified and may not transport between institutions.

### Current gap
No validated general CeutIA/SERPIENTE decision-utility evaluator is established. This should remain a candidate capability, not a production claim.

## 10. Deep extraction: BIB-009 EVSI

### Scientific question
What is the expected value of collecting additional information before making a decision?

### Formal decision-theoretic structure
For decision `a` and uncertain state/parameters `theta`, current optimal expected utility is:

`V_current = max_a E_theta[U(a, theta)]`.

If future information `X` is observed and knowledge is updated, the expected value with sample information is:

`V_X = E_X[max_a E_{theta|X}[U(a, theta)]]`.

The expected value of sample information is:

`EVSI = V_X - V_current`.

A research action is not justified by information gain alone: collection cost, delay, feasibility and decision consequences matter. Net benefit of sampling can incorporate research cost.

### Ceuta/SERPIENTE consequence
Candidate research tasks should be able to state which unresolved uncertainty could change a decision and what observation would discriminate between plausible hypotheses. This supports the requested `DISCOVERY -> ALTERNATIVE EXPLANATIONS -> FALSIFICATION -> UPDATE` architecture.

### Important restriction
EVSI is decision-context dependent. It cannot be converted into a universal scientific-value score across unrelated missions without an explicit utility model.

### Current gap
No validated autonomous EVSI/VOI engine exists. The architecture should initially preserve VOI dimensions and auditable rationale rather than inventing a scalar score.

## 11. Cross-source synthesis

### Independent corroboration
BIB-001/002/007 address prediction methodology from different angles but are not independent empirical evidence about Ceuta. BIB-004/005/006 are related early-warning literature and share conceptual lineage; they should not be counted as independent corroboration merely because they are separate publications.

### Convergent knowledge
A convergent methodological principle appears across sources: prediction claims require explicit target/context, temporal integrity, uncertainty evaluation, appropriate baselines, adversarial assessment and a clear boundary between predictive and causal interpretation.

### Contradiction / limitation
Early-warning literature supports existence of conditional precursor behavior in some dynamical systems but does not establish universal real-time catastrophe prediction. This limitation is material and must remain explicit in product claims.

### Dataset dependence
No claim of empirical independence is made across these sources without tracing their datasets. Methodological agreement is not empirical replication.

## 12. Source limitation -> system risk mapping

| Source limitation | System risk | Detection | Mitigation | Residual risk |
|---|---|---|---|---|
| Reporting guideline is not validation | overpromotion of documented model | validation-state gate | typed closure states | prospective/external uncertainty |
| Appraisal framework is not outcome evidence | false assurance from low bias | domain-level appraisal | separate validation layers | applicability uncertainty |
| Provenance model does not prove truth | traceable but false claim | evidence/claim separation | provenance + epistemic state | epistemic uncertainty |
| EWS often demonstrated in models/specific systems | generic catastrophe claims | target/system-specific validation | nulls, baselines, prospective tests | transfer uncertainty |
| Probabilistic sharpness can reward overconfidence | false precision | calibration/proper scoring | calibration + coverage/sharpness | future distribution shift |
| Decision utility depends on costs/context | institutionally invalid threshold | explicit utility/context | decision-specific analysis | utility uncertainty |
| EVSI depends on decision model | arbitrary task prioritization | inspect utility and state model | bounded VOI dimensions | model/utility uncertainty |

## 13. Scientific debt revealed by this audit

- **Bibliographic/provenance debt:** no single complete external-source manifest.
- **Measurement debt:** observation-process variables are not uniformly acquired across domains.
- **Validation debt:** prospective and external evidence remains absent for key predictive capabilities.
- **Decision debt:** forecast evaluation is more developed than decision-utility/effectiveness evaluation.
- **Model debt:** generic critical-transition and multisystem models remain scientifically unvalidated for Ceuta.
- **Epistemological debt:** the source-to-claim-to-hypothesis-to-model-to-prediction chain is represented conceptually but not yet uniformly materialized for every source.

## 14. Derived work

1. Build a versioned bibliographic/source manifest and provenance chain; do not treat this as a coding request until the existing repository source/reference surfaces have been exhaustively inventoried.
2. Extend prediction evaluation records with TRIPOD+AI/PROBAST-derived fields without creating a duplicate contract.
3. Reconcile provenance representation with the existing source/version/derivation model; evaluate whether PROV-O serialization adds interoperability value before implementing it.
4. Preserve EWS as experimental/scientific capabilities until target-specific prospective validation exists.
5. Add decision-utility/VOI semantics only after the decision objects, utility/error-cost structure and authorized decision context are explicit.
6. Add an adversarial EWS test family: phenomenon change vs observation-process change, sampling change, external forcing, denominator drift, finite-window artifact and regime shift.
7. Continue the existing PIT/outcome/prospective-validation work in SERPIENTE; do not create a parallel validation framework.

## 15. Non-derived work

The following are explicitly **not** justified by this corpus alone:
- universal catastrophe prediction;
- causal interpretation of EWS trends;
- automatic high-dimensional interaction expansion;
- a universal scientific-value score;
- autonomous promotion of hypotheses to established knowledge;
- replacement of prospective validation with historical backtesting;
- decision recommendations without an explicit authorized decision context and utility structure.

## 16. Canonical status

This ledger is subordinate to `docs/scientific/SCIENTIFIC_NORMATIVE_STANDARD_001.md` and does not itself change constitutional authority, scientific validation state, or production capability claims. Material changes to the normative standard must be versioned separately.
