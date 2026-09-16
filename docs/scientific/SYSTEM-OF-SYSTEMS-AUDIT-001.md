# SYSTEM-OF-SYSTEMS-AUDIT-001 — CeutIA + SERPIENTE

**Status:** IMPLEMENTED / PARTIALLY VALIDATED
**Scope:** second-order prediction architecture: interacting systems, propagation, feedback, regime change and incremental predictive value.
**Scientific boundary:** no claim of prospective multisystem predictive effectiveness or causal interaction identification is made by this artifact.

## 1. Scientific conclusion

The repositories now contain the minimum architectural separation needed to represent cross-system dependencies without equating prediction with causality:

- CeutIA semantic graph explicitly distinguishes observation, prediction, acquisition, reporting, revision, intervention, modification, conditioning, confounding and feedback relations.
- `PREDICTS` edges require prediction identity, origin time and horizon and cannot carry an embedded causal claim.
- SERPIENTE now contains a bounded interaction-validation contract that compares a target-only baseline with an interaction-augmented forecast using paired, strictly ordered, point-in-time-valid prediction records.
- The interaction evaluator is exposed through `SerpienteRuntime.evaluate_interaction` and reports incremental Brier and log-loss improvement without assigning causal meaning to predictive gain.
- Existing SERPIENTE forecast PIT binding remains the temporal gate for actual forecast matrices; the interaction evaluator does not weaken or replace it.

This is **not** equivalent to a production multisystem forecasting engine. The repositories still lack prospective evidence showing that any particular Ceuta interaction improves real-world prediction, and they do not yet establish a validated dynamic interaction graph or joint latent-state model.

## 2. System inventory

The following domains are retained because their state can plausibly influence another relevant Ceuta system and because observations can be operationally or scientifically meaningful:

| System | State / observables | Latent or process variables | Principal temporal scale | Relevant interactions | Current repository acquisition status |
|---|---|---|---|---|---|
| Health | mortality, morbidity proxies, service demand | population health burden | days-years | epidemiology, migration, weather, capacity | INE mortality; broader health acquisition incomplete |
| Epidemiology | disease observations, surveillance signals | transmission state, susceptible/exposed burden | days-weeks | mobility, migration, health capacity, weather | ECDC surveillance cataloged |
| Migration / border | arrivals, departures, population under temporary protection/care | flow pressure, transient population | hours-months | health, housing, services, security, mobility | official acquisition exists but not yet continuously cataloged |
| Demography | resident population, births/deaths, migration | age/sex/origin structure | months-years | health, labour, housing, education | INE population/migration datasets verified externally |
| Mobility | passenger/vehicle flows, routes | movement demand and network state | hours-days | migration, weather, port, health | partial official sources verified |
| Environment | environmental observations | exposure/background conditions | hours-years | health, weather, air quality | partial |
| Climate | temperature, precipitation, seasonal anomalies | climatic baseline / trend | days-years | health, water, energy, mobility | AEMET acquisition cataloged |
| Weather | hourly meteorological observations | immediate hazard forcing | minutes-days | mobility, maritime, health, emergencies | AEMET acquisition cataloged |
| Maritime / port | passengers, vessels, Ro-Ro cargo, bunkering, cruises | port throughput / connectivity | hours-months | mobility, trade, air quality, emergencies | official port source verified externally |
| Healthcare capacity | beds, occupancy, emergency demand, staffing/reforcements | operational reserve and bottlenecks | hours-days | migration, epidemiology, health, emergencies | INGESA official daily reporting verified externally |
| Emergency services | ambulance activity, emergency responses | operational load / response capacity | hours-days | health, weather, migration, disasters | partial official reporting |
| Social services | service demand and placements | welfare/service pressure | days-months | migration, housing, labour, health | acquisition incomplete |
| Infrastructure | transport, utilities, critical assets | resilience / bottleneck state | hours-years | weather, mobility, emergencies, economy | acquisition incomplete |
| Housing | occupancy, availability, temporary accommodation | housing pressure | days-years | migration, demography, labour, services | acquisition incomplete |
| Economic activity | trade, business activity, demand | local economic state | weeks-years | mobility, port, migration, labour | partial |
| Labour | employment, vacancies, sectoral demand | labour-market pressure | weeks-years | migration, economy, services | partial |
| Education | enrolment, attendance, capacity | service/population pressure | days-years | demography, migration, health | acquisition incomplete |
| Public administration | service load, processing, interventions | institutional capacity | days-years | all service systems | acquisition incomplete |
| Security / public order | incidents, deployments, border/security load | operational pressure | hours-days | migration, mobility, humanitarian pressure | acquisition incomplete |
| Humanitarian pressure | arrivals, accommodation, food/medical demand | unmet needs / vulnerability | hours-weeks | migration, health, social services, security | partial |
| Energy | demand, generation, supply status | reserve / vulnerability | minutes-years | weather, infrastructure, economy | acquisition incomplete |
| Water | supply, demand, quality | resource/security state | hours-years | weather, demography, infrastructure, health | MITECO water data verified; Ceuta-specific continuous contract incomplete |
| Air quality | NO2, SO2, O3, PM10, PM2.5 and related measurements | exposure field | hours-days | weather, port, mobility, health | official MITECO data verified externally |
| Transport | road/air/maritime passenger and freight flows | network accessibility | hours-days | weather, port, migration, economy | partial; Aena/port sources verified externally |
| Communication / information environment | publication/reporting volume, source process changes | information/measurement process | hours-days | public administration, migration, security, health | no production acquisition contract |

## 3. Boundary discipline

Every candidate interaction must separate:

`INTERNAL_STATE` / `EXOGENOUS_INPUT` / `ENDOGENOUS_DYNAMICS` / `EXTERNAL_SHOCK` / `MEASUREMENT_PROCESS`.

An observed change is not accepted as a latent-state change without considering reporting, acquisition, revision, access, policy and measurement-process changes. This is especially important for healthcare demand, migration counts, emergency activity and information-environment signals.

## 4. Interaction graph — scientifically justified candidate edges

The following are candidate relations for representation and validation, not claims that all are causal or production-useful.

| Edge | Mechanism class | Plausible lag | Evidence state | Current validation requirement |
|---|---|---|---|---|
| Migration → healthcare demand | service-demand / exposure | hours-weeks | E2-E4 depending target | paired PIT baseline vs interaction model |
| Healthcare capacity → healthcare demand observed process | access / admission / reporting | hours-days | E2-E3 | distinguish latent morbidity from care-seeking and policy |
| Epidemiology → healthcare demand | disease burden | days-weeks | E6 | disease-specific outcome ascertainment |
| Mobility → epidemiology | contact/movement network | days-weeks | E6 | population denominator + mobility exposure |
| Migration → epidemiology | exposure / composition / access | days-weeks | E4-E6, disease-specific | avoid population-wide generalisation |
| Weather → mobility | operational forcing | minutes-days | E6 | route-specific observations |
| Weather → emergency demand | exposure / hazard | hours-days | E6 | event-type-specific validation |
| Weather → health | heat/cold/exposure pathways | hours-weeks | E6 | outcome-specific and age/risk stratification |
| Weather → air quality | atmospheric transport / dispersion | hours-days | E6 | pollutant-specific observation process |
| Port/maritime traffic → mobility | network flow | hours-days | E3-E6 | synchronized flow denominators |
| Port/maritime traffic → air quality | emissions / activity | hours-days | E3-E6 | meteorology and source attribution |
| Mobility → healthcare demand | access/contact/service use | hours-days | E3 | distinguish causality from common seasonal drivers |
| Healthcare capacity ↔ service demand | congestion/adaptation | hours-days | E2-E4 | explicit feedback and intervention records |
| Migration → housing pressure → social services | demand cascade | days-months | E3-E4 | capacity/occupancy observations |
| Migration → labour → economic activity | population/labour supply and demand | weeks-months | E3-E6 | sector and denominator controls |
| Weather → infrastructure → mobility | disruption cascade | hours-days | E6 | asset-level outage and route data |
| Weather → water → health | resource/exposure pathway | days-months | E4-E6 | water quality/availability and health outcomes |
| Energy ↔ infrastructure | supply-demand / dependency | minutes-days | E6 | network topology and outage data |
| Public intervention → measurement process | policy/reactivity | hours-months | E2-E6 | intervention identity and observation-process state |

The important confounding pattern `A ← C → B` must remain distinct from `A → B`. A shared weather, seasonal, policy or population driver is a first-class competing explanation.

## 5. Interaction evidence ladder

Interaction evidence is preserved separately from edge existence:

- **E0:** unknown
- **E1:** raw observation
- **E2:** verified observation
- **E3:** independent corroboration
- **E4:** convergent multidomain evidence
- **E5:** strong empirical evidence
- **E6:** established scientific knowledge
- **E7:** causally supported
- **E8:** operationally validated prediction

A graph edge, coefficient, feature importance value or predictive gain does not automatically upgrade an interaction to E7 or E8.

## 6. Temporal and spatial requirements

Interactions require compatible observation windows, not merely common dates. The acquisition layer must preserve event, observation, publication, acquisition/availability and revision times. Daily/monthly mixing, interpolation, aggregation and publication latency must be explicit.

Spatial interaction is currently a requirement rather than a production capability. Relevant future resolutions include city, neighbourhood, border/port, maritime approach, healthcare catchment and mobility corridor, but no granularity should be introduced unless source resolution and denominator integrity support it.

## 7. State-space requirement

A future joint model may require:

`Z(t+1) = F(Z(t), U(t), A(t), G(t), epsilon)`

`Y(t) = H(Z(t), M(t), eta)`

where `Z` is latent joint state, `U` exogenous input, `A` intervention, `G` interaction structure and `M` measurement process.

This is a scientific requirement for a future joint dynamical model, not an implementation claim. The current production forecaster remains a binary longitudinal target forecaster with calibration and model disagreement; it does not yet estimate a validated joint latent state or dynamic coupling matrix.

## 8. Incremental predictive-value gate

A candidate interaction enters production only if a PIT-valid comparison demonstrates incremental value over a target-only baseline. Required measures include Brier/log loss at minimum, with calibration, discrimination, lead time, robustness and decision utility evaluated when applicable.

The new SERPIENTE evaluator enforces:

- directed source/target identity;
- explicit lag and mechanism;
- separate causal status;
- binary outcome domain;
- strict prediction-origin order;
- availability no later than origin;
- outcome after origin;
- paired baseline/interaction origins and outcome times;
- incremental Brier and log-loss comparison.

No causal inference is produced by this evaluator.

## 9. Feedback, propagation and regime change

CeutIA can now encode feedback and process relations explicitly in the semantic graph. This supports representation of `A → B → A` and longer chains as scientific relations, but does not itself estimate propagation kernels, network flows or dynamic interaction coefficients.

The current SERPIENTE architecture has trajectory/regime fields and non-stationarity governance, but a validated interaction-change detector (coefficient/lag/direction/nonlinearity change) and a joint regime model remain open scientific capabilities.

## 10. Multisystem emergent-state requirement

The current system can represent multiple observations/signals and a trajectory, but there is no validated production component that estimates a joint abnormal configuration while each marginal remains normal. This is a genuine second-order capability gap.

Required future validation:

`P(joint_state abnormal | marginal states individually normal)`

against an appropriate multivariate null/baseline, with control for common drivers, measurement dependence and multiple testing. No arbitrary high-dimensional anomaly detector is justified until the target and reference class are specified.

## 11. Second-order adversarial test

Required scenario:

- each subsystem forecast is individually calibrated and PIT-valid;
- source authenticity and provenance are intact;
- marginal forecasts remain accurate;
- the interaction structure changes after an intervention/shock;
- the joint forecast fails because the historical coupling no longer applies.

The current architecture can detect related distribution/regime instability and can preserve interaction identity, but it does not yet prove detection of a changing coupling matrix. This remains an explicit validation target.

## 12. Capability matrix — current final repositories

| Capability | CeutIA + SERPIENTE status |
|---|---|
| Individual observed state | IMPLEMENTED |
| Longitudinal state | IMPLEMENTED |
| Individual trajectory | IMPLEMENTED |
| Individual probabilistic forecast | IMPLEMENTED / runtime validated |
| PIT feature binding | IMPLEMENTED / runtime validated |
| Observation / measurement-process semantics | IMPLEMENTED in CeutIA graph; broader acquisition incomplete |
| Directed interaction representation | IMPLEMENTED in CeutIA semantic graph |
| Prediction-vs-causality separation | IMPLEMENTED |
| Feedback relation representation | IMPLEMENTED |
| Interaction incremental predictive-value evaluator | IMPLEMENTED / unit + adversarial behavior verified; repository CI revalidation pending |
| Runtime exposure of interaction evaluator | IMPLEMENTED |
| Validated lag-distribution / interaction kernel | NOT_ESTABLISHED |
| Dynamic coupling-strength estimation | NOT_ESTABLISHED |
| Interaction-change detection | NOT_ESTABLISHED |
| Joint latent multisystem state | NOT_ESTABLISHED |
| Multivariate emergent-state detector | NOT_ESTABLISHED |
| Spatial propagation model | NOT_ESTABLISHED |
| Network propagation model | NOT_ESTABLISHED |
| Cross-timescale joint dynamics | NOT_ESTABLISHED |
| Dynamic regime-dependent coupling | PARTIALLY_SUPPORTED; no prospective validation |
| Uncertainty propagation through interaction graph | PARTIALLY_SUPPORTED at component level; joint propagation NOT_ESTABLISHED |
| Multisystem ensemble forecast | NOT_ESTABLISHED |
| Model disagreement as interaction diagnostic | PARTIALLY_SUPPORTED; current disagreement is forecast-model disagreement, not structural interaction disagreement |
| Prospective multisystem validation | NOT_ESTABLISHED |
| Operational multisystem effectiveness | NOT_ESTABLISHED |

## 13. Scientific data findings

Authoritative external evidence confirms that Ceuta has usable inputs across several domains. AEMET provides hourly and seasonal meteorological observations with explicit provisional/revision semantics. INE provides annual population and migration tables covering Ceuta. ECDC provides infectious-disease surveillance and migrant-health evidence. Official port reporting exposes passenger, vessel and Ro-Ro activity. INGESA publishes high-frequency healthcare activity/capacity observations. MITECO publishes air-quality and water information.

These sources establish acquisition opportunities, not interaction validity. Their different cadences, revisions, denominators and observation processes must be reconciled before interaction estimation.

## 14. Remaining high-value scientific frontier

1. Build synchronized interaction-ready observation frames with explicit denominators and source/process dependence.
2. Add lagged interaction features only under declared mechanisms and pre-specified lag windows.
3. Compare target-only versus interaction models prospectively and PIT-validly.
4. Add joint-state / emergent-configuration validation only after a scientifically defined target exists.
5. Add interaction-change detection only with enough repeated observations to distinguish structural change from sampling noise.
6. Add spatial/network coupling only where source resolution supports it.
7. Propagate state, parameter, observation, interaction and model uncertainty through joint forecasts.
8. Validate intervention-induced interaction changes separately from ordinary regime drift.

## 15. Closure condition

The system-of-systems architecture is **partially implemented but not scientifically validated as a multisystem predictor**. The current implementation now has explicit interaction semantics and an incremental predictive-value gate, so the remaining work is empirical: interaction-ready acquisition, prospective PIT-valid comparisons, joint-state validation, dynamic coupling/regime tests and outcome ascertainment.

No additional interaction domain is added here without evidence that it can materially influence an already relevant Ceuta system and without a feasible measurement contract.
