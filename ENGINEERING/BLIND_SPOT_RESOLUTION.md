# CeutIA — blind-spot resolution ledger

## Resolution principle

The 45 meta-audit findings and 10 deeper blind spots are treated as manifestations of a smaller number of architectural capabilities. The authoritative implementation target is capability completeness, not ticket count.

## Architectural clusters

| Cluster | Findings absorbed | Resolution state |
|---|---|---|
| Partially observable territorial state | latent state, state uncertainty, observability, identifiability, DGP, measurement error, competing explanations | Implemented as typed state hypotheses, covariance, linear observability/identifiability analysis and explicit observation-process contracts. Linear state-space prediction/update is available as a defensible baseline; nonlinear/particle methods remain model-specific rather than fabricated. |
| Observation/data-generating process | ascertainment, selection, reporting, missingness, coding/revision changes, phenomenon-vs-measurement change | Implemented as ObservationProcess, Measurement, MissingnessMechanism and ChangeAttributionEngine. Phenomenon claims are blocked when measurement-process explanations remain unresolved. |
| Multiscale territorial representation | individual→international scales, aggregation, ecological effects, spatial heterogeneity, mobility | Existing runtime multiscale/spatiotemporal infrastructure retained. New ScaleMapping, SpatialUnit and MobilityFlow contracts make scale semantics explicit without duplicating runtime aggregation. |
| Spatial/network dynamics | spillovers, topology, propagation, cascades, bottlenecks, network resilience | Existing DynamicNetwork and complex-system interaction algebra retained. NetworkAnalyzer adds explicit cascade/topology checks; spatial relations and normalized spatial lag are representable. No causal meaning is inferred from topology. |
| Cross-domain dynamics | feedback, delays, coupling, regimes, path dependence, resilience | Existing interaction algebra and resilience infrastructure retained. DomainCoupling and Regime contracts make mechanism/lag/regime assumptions explicit. State-space dynamics provide a mathematically constrained baseline. |
| Predictability and model multiplicity | predictability limits, model disagreement, regime drift, structural uncertainty | ForecastObject preserves target/issue/horizon/information-set/model identity. PredictabilityAnalyzer and ModelDisagreementAnalyzer provide explicit abstention/degradation signals. |
| Decision/intervention lifecycle | policy feedback, asymmetric loss, resources, reversibility, outcomes, learning | Existing decision/action/feedback lifecycle retained. Intervention and OutcomeRecord provide explicit intervention-state/outcome objects without claiming causal attribution. |
| Information contribution | redundancy, mutual information, conditional information, synergy | InformationAnalyzer provides entropy/MI primitives. These are descriptive information measures; causal or predictive value must still be validated empirically. |
| Uncertainty architecture | aleatoric, measurement, sampling, parameter, model, structural, state, DGP, transport, adversarial, dependence | UncertaintyVector preserves components rather than collapsing them prematurely. Conservative scalar gating remains available downstream. |
| System-level safety gate | insufficient observability, non-identifiability, model disagreement, measurement-process risk, regime change | SystemIntelligence and SystemIntelligenceGate convert structural epistemic limitations into explicit allow/degraded/abstain states. |

## Ten systemic blind spots

1. **Latent territorial state** — no longer represented only as observed indicators; StateHypothesis and StateEstimator explicitly separate underlying state from measurement.
2. **Observer/measurement process** — ObservationProcess and ChangeAttribution prevent observed breaks from automatically becoming phenomenon breaks.
3. **Observability/identifiability** — rank-based structural checks can return an explicit inability to distinguish state or parameter dimensions.
4. **Spatial/network boundary** — spatial units, relations, mobility and dynamic network/cascade representations are explicit and time-compatible with existing runtime infrastructure.
5. **Cross-domain coupling** — DomainCoupling carries relation type, lag, mechanism and evidence references; causal/mechanistic links require explicit mechanisms.
6. **Dynamic regimes/predictability limits** — RegimeDetector, PredictabilityAnalyzer and model disagreement can degrade or abstain instead of forcing a forecast.
7. **Uncertainty collapse** — uncertainty components are preserved in a typed vector; the scalar maximum is a downstream conservative policy, not the scientific representation.
8. **Human/intervention feedback** — Intervention and OutcomeRecord are explicit lifecycle objects; attribution remains separate from outcome observation.
9. **Information redundancy** — information primitives permit assessment of whether additional variables carry information rather than assuming that more data is better.
10. **System-boundary uncertainty** — the system gate treats missing observability, non-identifiability, DGP risk, regime change and model disagreement as first-class reasons for abstention.

## Reconciliation with pre-existing implementation

The audit was not treated as a claim that every named capability was absent. Existing modules already provide substantial capability in bitemporal evidence, replay, multiscale state, dynamic networks, spatiotemporal relations, causal inference, forecasting, resilience, source governance and decision lifecycle. The new layer therefore adds missing semantics and gates rather than replacing those implementations.

## Scientific boundary

These contracts do not constitute empirical validation. In particular, they do not establish that a proposed latent-state model is identifiable for a real Ceuta dataset, that a network mechanism is causal, that a regime detector is operationally calibrated, that information measures improve forecasting, or that an intervention caused an observed outcome. Those claims require point-in-time data, preregistered estimands where appropriate, temporal/out-of-sample validation and domain-specific evidence.

## Invariants

- Observation, evidence, signal, state, inference, hypothesis, prediction, scenario, decision and outcome remain distinct.
- Association, prediction and causation remain distinct.
- State uncertainty is not measurement certainty.
- Measurement-process change cannot silently become phenomenon change.
- Competing models remain representable and disagreement cannot be silently discarded.
- Forecasts carry immutable issue time and information-set identity.
- Structural non-identifiability is a valid result, not an error to be hidden.
- No component creates causal claims from graph topology alone.
- No numerical confidence is invented where the evidence does not support calibration.

## Resume point

Next autonomous work should focus on integrating the system gate with the canonical decision runtime without weakening existing provenance/control-plane contracts, then on empirical validation infrastructure for real official Ceuta data and temporal replay. Global validation remains intentionally deferred until the integrated engineering chain is substantially complete.
