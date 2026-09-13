# CeutIA — Implementation Remainder V1

This checkpoint records the implementation completed after the exhaustive capability inventory.

## Implemented foundational gaps

1. Canonical integrated system context: `backend/app/core/integration/system_context.py`
   - current state + trajectory
   - observations
   - evidence and contradiction references
   - competing hypotheses
   - model/version/validity metadata
   - interventions and concurrent interventions
   - regimes/scales
   - structural constraints
   - observation-process version

2. Missingness and observation-process semantics: `backend/app/core/evidence/missingness.py`
   - MCAR/MAR/MNAR/censoring/truncation/unknown
   - expected-but-not-observed events
   - observation-process change records

3. Dependency-aware uncertainty aggregation: `backend/app/core/uncertainty/aggregation.py`
   - explicit uncertainty kinds
   - independent versus dependent groups
   - conservative aggregation for dependent uncertainty
   - covariance requirements

4. Decision-specific value of information: `backend/app/core/decision/value_of_information.py`
   - expected value with information
   - expected value without information
   - gross and net VoI
   - explicit acquisition cost
   - explicit posterior/signal model

5. Forecast calibration: `backend/app/core/forecasting/calibration.py`
   - prospective interval coverage
   - coverage error
   - interval width
   - calibration status only after outcome observations

6. Forecast interval semantics: `backend/app/core/forecasting/forecast_distribution.py`
   - existing mean-confidence interval explicitly labelled
   - empirical predictive interval added
   - no automatic calibration claim

7. Geospatial correctness: `backend/app/core/spatial/spatial_engine.py`
   - geographic validation
   - haversine great-circle distance in metres
   - radius semantics therefore no longer depend on degree units

8. Evidence-source dependency: `backend/app/core/evidence/dependency.py`
   - origin grouping
   - duplicated-source detection
   - evidence contamination flags

9. Early-warning dynamics: `backend/app/core/state/early_warning.py`
   - variance
   - lag-1 autocorrelation
   - recovery-time summaries
   - variance change
   - explicit warning indicators without universal tipping thresholds

10. Scientific red-team/falsification: `backend/app/core/science/falsification.py`
    - falsification targets
    - unresolved outcomes
    - falsified/support/inconclusive status
    - alternative explanations and required discriminators

11. Integrated architecture documentation now points to the exhaustive capability inventory.

## Still intentionally not declared complete

The following remain scientific/operational gates rather than documentation gaps:

- full multivariate latent-state estimation and smoothing;
- time-varying parameter/state-space model families;
- change-point and regime inference beyond descriptive indicators;
- complete causal identification and estimation for time-varying confounding;
- quantitative sensitivity to unmeasured confounding;
- negative-control implementations;
- calibrated probabilistic forecasting across real prospective datasets;
- rare-event/tail calibration;
- synchronized digital twin;
- model updating/champion-challenger production lifecycle;
- intervention-effect estimation and interference-aware analysis;
- population/behavioural adaptation models;
- runtime privacy enforcement and formally demonstrated differential privacy;
- full adversarial/information-operation inference;
- production active sensing/VoI integration into the decision engine;
- comprehensive scientific benchmark suite;
- prospective and external validation.

These are not being represented as solved merely because supporting contracts now exist.

## Workflow rule

Final CI and scientific validation remain deferred until the implementation cycle is complete.
