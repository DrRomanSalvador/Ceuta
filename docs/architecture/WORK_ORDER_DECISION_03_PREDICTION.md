# Decision-system work order 03 — Calibrated prediction and tail risk

## Objective
Turn forecasting from a prediction contract into a calibrated prospective probabilistic forecasting engine.

## Required implementation
- Proper predictive distributions, not confidence intervals relabeled as prediction.
- Prospective rolling-origin evaluation with leakage controls and temporal embargo where needed.
- Calibration diagnostics for probabilities, intervals and full distributions.
- Conformal/distribution-free coverage where assumptions permit.
- Rare-event and tail-risk modelling, including extreme-value methods where appropriate.
- Distribution-shift detection and model-validity diagnostics.
- Dependence-aware scoring and block/time-series evaluation.
- Brier, log score, CRPS and interval scores with pre-specified evaluation protocols.
- Model averaging/champion-challenger comparison under structural uncertainty.
- Explicit forecast horizon, target estimand, reference information set and prediction timestamp.

## Acceptance criteria
A prediction reaching the decision layer must carry calibrated uncertainty, prospective evaluation evidence, model identity, information-set timestamp, shift diagnostics and an explicit validity/abstention state.
