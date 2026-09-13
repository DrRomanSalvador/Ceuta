# CeutIA — Repository Gap Audit V1

Status: BOUNDED AUDIT CHECKPOINT — FAMILIES A–E + OMNI-NET CROSSWALK
Base commit audited: ef09ab69e53bd8c1dcc231fc4bd4b71c8b15b61f

This is a repository inspection, not a design proposal. Classification is based on actual files and implementation evidence in the repository. A module/file is not considered implemented merely because its name exists. `scaffold` means contracts or thin deterministic plumbing exist; `partially implemented` means a meaningful subset works but important scientific/operational requirements are absent; `scientifically insufficient` means code may execute but cannot support the scientific claim implied by the capability.

## 0. OMNI-NET integration rule added by this audit

OMNI-NET vFINAL is a domain-specific clinical instantiation of several CeutIA primitives, not a replacement ontology for CeutIA.

OMNI-NET contributes a precise example of the general pattern:

exposure/stressor -> latent physiological state -> reserve -> temporal dynamics/recovery -> threshold/failure -> clinical outcome.

Its 7-layer hierarchy, RFR, IVO and CRS must remain in a separate clinical domain model. They must not be inserted into CeutIA as universal variables. Conversely, CeutIA should provide generic primitives capable of representing the same structural concepts: latent state, reserve/capacity, heterogeneous response, trajectories, perturbations, thresholds, recovery, causal mechanisms and intervention feedback.

The health-sphere framework should therefore be represented as a cross-domain observation/interaction layer in OMNI-NET and as a general multi-domain ontology in CeutIA. Biological, psychological, behavioural, relational/social, environmental, technological and contextual/exogenous influences may interact, but they must not be collapsed into a single undifferentiated score.

## A. System ontology and representation

A1 Multi-domain entities/agents/populations/institutions/environments/infrastructure — **partially implemented**. Entity-resolution and graph primitives exist, but no demonstrated canonical ontology unifying these entity classes with explicit system semantics.

A2 Observable versus latent state variables — **scaffold**. `TemporalStateStore` stores observations; no general latent-state object/estimator exists.

A3 Nested/hierarchical systems — **absent** as a demonstrated executable abstraction. Some domain structures exist, but no general nested-system semantics were found.

A4 Time scales from milliseconds to decades — **partially implemented**. Temporal contracts and timestamps exist, but no explicit multi-scale state/dynamics abstraction. OMNI-NET's high-frequency biosignals and decade-scale ageing would require this.

A5 Spatial scales individual/network/territory/global — **partially implemented** through spatial modules, but no unified scale semantics.

A6 Dynamic regimes/regime transitions — **scaffold**. `serpiente/regime_detection.py` exists but is a thin module; no demonstrated statistical regime-switching/state-transition engine.

A7 Feedback/circular causality — **scaffold / partially implemented**. `FeedbackAnalyzer` requires lagged feedback and can represent an assessment, but it does not infer or quantify feedback from data.

A8 Delays/memory/hysteresis/path dependence — **scaffold**. Data contracts carry time and causal loop contracts expose lag/hysteresis flags, but no actual memory/hysteresis dynamics engine was found.

A9 Thresholds/tipping points/critical transitions — **scaffold**. Threshold fields and cascade modules exist; no validated detection/estimation of tipping points was demonstrated.

A10 Resources/capacity/bottlenecks — **partially implemented**. Spatial flow/resource/decision modules exist, but capacity queues and bottleneck dynamics are not a unified system model.

A11 Endogenous versus exogenous shocks — **scaffold**. The concept appears in architecture, but no canonical shock object and causal classification pipeline was found.

A12 Intervention versus observation semantics — **partially implemented**. Shadow mode and causal intervention gates are real and useful; a general intervention object linked to state transitions/outcomes remains incomplete.

**Family A verdict: PARTIALLY IMPLEMENTED at best.** The repository contains many named primitives but does not yet have the central system ontology required by the project thesis.

## B. Data and observation architecture

B1 Streaming/batch — **partially implemented**. Pipeline/source abstractions exist, but no demonstrated production-grade streaming ingestion path.

B2 Event-time versus ingestion-time — **existing real** at the contract/state-store level. Temporal contracts explicitly distinguish event and availability/cutoff semantics; this was validated in prior phase work.

B3 Longitudinal identity/entity resolution — **scaffold / partial**. Entity-resolution modules exist, but longitudinal identity governance is not a demonstrated end-to-end capability.

B4 Source reliability/dependency — **partially implemented**. Source-health and source-dependency graph modules exist; their scientific/operational depth is limited.

B5 Schema drift — **scaffold**. A dedicated module exists but is small and does not constitute comprehensive schema-evolution governance.

B6 MCAR/MAR/MNAR missingness — **absent** as a statistical missingness mechanism framework.

B7 Measurement error/sensor uncertainty — **absent / scientifically insufficient** as a general measurement-error model.

B8 Sampling/selection bias — **absent** as a general selection-mechanism model.

B9 Survivorship/collider risks — **scaffold** through causal contracts/guards; no complete data-selection bias engine.

B10 Temporal leakage prevention — **existing real** for the implemented temporal observation/shadow contracts; coverage across all modelling paths is not yet proven.

B11 Dataset/version lineage — **partially implemented** via knowledge versioning and provenance lineage.

B12 Historical reconstruction — **scaffold**. Replay exists, but historical reconstruction from raw/versioned sources is not demonstrated.

B13 Replayability — **partially implemented**. Replay module exists; full deterministic end-to-end replay across every subsystem is not established.

B14 Observation conflict reconciliation — **scaffold**. Event resolution exists, but no general evidence conflict-resolution semantics equivalent to competing observations/models.

B15 Raw-source + transformation provenance — **partially implemented**. Provenance/lineage/traceability modules exist, but end-to-end propagation through every computation is not demonstrated.

B16 Data quality versus truth probability — **partially implemented**. `epistemic.py` explicitly separates evidence confidence from event probability, which is a strong architectural element; the separation is not yet enforced universally.

**Family B verdict: PARTIALLY IMPLEMENTED.** Temporal availability semantics are unusually strong relative to the rest, but observation quality, missingness, measurement error, selection, and complete provenance remain major gaps.

## C. State estimation and longitudinal modelling

C1 Dynamic latent-state estimation — **absent**.

C2 Bayesian filtering/smoothing — **absent** as an actual estimator.

C3 State-space models — **absent** as an implemented model. The repository has state storage, not state-space inference.

C4 Time-varying parameter models — **absent**.

C5 Change-point detection — **absent** as a demonstrated estimator.

C6 Regime-switching models — **scaffold** only.

C7 Individual versus population trajectories — **absent** as a formal trajectory model.

C8 Personal baselines/deviation-from-baseline — **absent**.

C9 Context-dependent reference ranges — **absent**.

C10 Trajectory derivatives/acceleration/deceleration — **absent**.

C11 Early-warning indicators — **scaffold** through weak-signal modules, but no validated dynamical early-warning statistics.

C12 Uncertainty propagation through state estimation — **absent**, because the underlying state estimator is absent.

**Family C verdict: ABSENT.** This is the single largest architectural gap relative to the user's recovered thesis. `TemporalStateStore` is not a latent-state estimator; it is an append-only observation store with cutoff semantics.

This gap is also the critical bridge to OMNI-NET. OMNI-NET's RFR(t), IVO, recovery time and ageing velocity cannot be correctly implemented on the present CeutIA state architecture without first introducing a rigorous longitudinal state-estimation substrate.

## D. Causal intelligence

D1 Explicit DAG/SCM — **partially implemented / scaffold**. Causal graph/contracts exist, but no mature SCM execution layer.

D2 Potential outcomes — **scaffold**. Causal-effect/counterfactual contracts exist; no estimator.

D3 Temporal causal graphs — **partially implemented** at contract level; no complete temporal causal inference engine.

D4 Time-varying confounding — **absent / scientifically insufficient**.

D5 Marginal structural reasoning — **absent**.

D6 Backdoor/frontdoor identification — **scaffold**. Identification module exists, but must not be treated as a complete identification engine without auditing its implementation and assumptions.

D7 Collider/mediator protection — **partially implemented**. Confounding/collider warnings exist; no universal enforcement.

D8 Unmeasured-confounding sensitivity — **absent**.

D9 Negative controls — **absent** as a dedicated implemented framework.

D10 Falsification tests — **scaffold**. Falsification contracts exist, but the advanced stress tester currently generates challenges rather than executing statistical falsification tests.

D11 Causal discovery as hypothesis generation — **scaffold**. Discovery module exists; no evidence that it performs validated discovery algorithms.

D12 Competing causal graphs — **partially implemented**. `CausalModelEnsemble` preserves structural disagreement and normalizes weights.

D13 Mechanistic constraints — **absent** as an executable constraint layer.

D14 do-operator/interventional semantics — **scaffold**. Intervention gates exist; no structural causal execution semantics.

D15 Counterfactuals/potential outcomes — **scaffold**. The advanced counterfactual engine computes a supplied factual/counterfactual difference after an identification gate; it does not estimate counterfactuals from data.

D16 Mediation — **absent** as a dedicated estimator.

D17 Moderation/effect modification — **scaffold** through interaction contracts.

D18 Heterogeneous effects — **scaffold** through `HeterogeneousEffect`; no estimator.

D19 Dose-response/nonlinear effects — **absent**.

D20 Delayed causal effects — **scaffold** through lag fields; no estimator.

D21 Feedback/simultaneous causality — **scaffold**; lagged feedback contract exists but no simultaneous-equation/feedback identification.

D22 Cross-domain causal chains — **scaffold / partially implemented**. `CrossDomainCausalEngine.connect` validates explicit cross-domain edge tuples but does not infer or estimate chains.

D23 Regime-dependent causal effects — **scaffold**. Regime comparison groups supplied effects; it does not estimate regime-specific causal effects.

D24 Transportability/generalisation — **absent**.

D25 External validity — **absent** as a formal framework.

D26 Positivity/overlap — **absent**.

D27 Consistency/SUTVA-like assumptions — **absent** as formal validation contracts.

D28 Model misspecification sensitivity — **scaffold**. Stress-testing contracts exist; no quantitative sensitivity analysis.

D29 Causal model ensembles — **partially implemented**.

D30 Causal disagreement preservation — **existing real at contract level**. Structural disagreement is explicitly retained.

D31 Active causal learning — **scaffold**. Query ranking by expected information gain/cost/feasibility exists; no actual experimental/observation design loop.

D32 Intervention design/feasibility — **partially implemented** in decision/governance contracts; causal design remains incomplete.

D33 Post-intervention causal attribution — **absent / scientifically insufficient**.

D34 Prospective causal validation — **scaffold**. `ProspectiveCausalValidator` compares predicted and observed values against tolerance; this is not a full prospective causal validation design.

**Family D verdict: PARTIALLY IMPLEMENTED AS CONTRACT/REASONING SCAFFOLDING; SCIENTIFICALLY INSUFFICIENT FOR CAUSAL CLAIMS.** The recent advanced causal layer is useful architecture, but it must not be mistaken for an operational causal inference system.

## E. Complex-systems dynamics

E1 Dynamic graphs — **scaffold / partial**. `serpiente/dynamic_graph.py` exists but is small.

E2 Node/edge state evolution — **absent / scaffold**; no demonstrated dynamic state transition engine.

E3 Centrality/changing influence — **absent** as a robust dynamic metric layer.

E4 Community formation/fragmentation — **absent**.

E5 Contagion/propagation — **scaffold** through propagation modules; no validated propagation model.

E6 Cascades — **scaffold**. Cascading-risk module exists but is not a full dynamical cascade simulator.

E7 Percolation thresholds — **absent**.

E8 Feedback amplification/damping — **scaffold**.

E9 Adaptive capacity — **scaffold**.

E10 Resilience reserve — **absent as a quantified state variable**. This is particularly important given the user's central thesis and OMNI-NET RFR analogy.

E11 Critical slowing down — **absent**.

E12 Variance/autocorrelation early warnings — **absent** as an implemented statistical detector.

E13 Hysteresis — **scaffold only**.

E14 Nonlinear response — **absent** as a general estimator.

E15 Multi-stability/alternative attractors — **absent**.

E16 Path dependence — **absent** as a formal state/dynamics construct.

E17 Emergence — **absent** as an operational measurable construct.

E18 Synchronisation — **absent**.

E19 Cross-scale coupling — **absent**.

E20 Shock absorption/amplification — **scaffold** through resilience/cascade concepts, not quantitatively modelled.

E21 Bottleneck detection — **partially implemented** via resource/spatial concepts, but not unified with dynamic system state.

E22 Capacity queues/flow constraints — **scaffold / partial** through spatial flow and resource modules.

E23 Failure propagation through coupled networks — **scaffold** only.

**Family E verdict: SCAFFOLD / PARTIALLY IMPLEMENTED, with most scientifically meaningful complex-dynamics capabilities still absent.** This is the second major gap after state estimation.

## Crosswalk: OMNI-NET vFINAL versus CeutIA substrate

OMNI-NET requirement -> present CeutIA support:

- 7-layer causal hierarchy -> **absent as a clinical domain model**.
- Genomic substrate / PRS / DunedinPACE -> **absent**.
- Exogenous exposure vector U(t) -> **generic shock/exposure semantics only; absent as a clinical implementation**.
- Regulatory systems -> **absent**.
- Amplifier mechanisms -> **absent**.
- Five-domain functional reserve -> **absent**.
- RFR_i(t) -> **absent**.
- IVO = argmin RFR -> **absent**.
- CRS with empirically learned Cox weights -> **absent**.
- Bayesian state-space X(t+1)=AX(t)+BU(t)+epsilon -> **absent**.
- Observation model Y(t)=CX(t)+eta -> **absent**.
- Explicit Δt and temporal unrolling of feedback -> **generic temporal contracts exist; model absent**.
- Core/Extended/Research/Moderator variable governance -> **absent**.
- Pre-analytic protocols -> **absent**.
- Prospective validation sequence Studies 0–4 -> **absent as an OMNI-NET implementation/registry**.
- Explicit prohibition on projected C-statistics / premature clinical use -> **generic governance principle exists; OMNI-specific enforcement absent**.

Important interpretation: this does not mean CeutIA is supposed to implement OMNI-NET. It means the current CeutIA repository does not yet contain the generic longitudinal-state substrate that OMNI-NET would eventually need to reuse safely.

## First architectural conclusion

The repository is substantially stronger in contracts, temporal availability semantics, epistemic separation, governance scaffolding and module boundaries than in the actual scientific engines required to model trajectories.

The most important missing layer is not another specialist module. It is a canonical dynamic-state substrate connecting:

observation -> latent state -> trajectory -> interactions/causal model -> regime/reserve -> forecast -> intervention -> outcome -> prospective learning.

Until that substrate exists, the repository remains a sophisticated collection of partially implemented analytical primitives rather than the full system described by the project objectives.
