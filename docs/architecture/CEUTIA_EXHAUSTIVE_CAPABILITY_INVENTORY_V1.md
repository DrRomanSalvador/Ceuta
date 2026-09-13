# CeutIA — Exhaustive Capability Inventory V1

Status: MASTER ARCHITECTURAL INVENTORY — implementation target
Date: 2026-09-13

## Purpose

This is the master capability inventory for CeutIA. It reconciles the project objectives, Repository Gap Audits V1/V2, the Integrated Dynamic System Core checkpoint, and the additional robustness blocks identified during the current architectural review.

It is the authoritative checklist for architectural completeness. A capability is not considered complete because a file, class, contract, formula, score, or documentation section exists. Each capability must eventually be classified by implementation maturity and scientific validity.

## Status vocabulary

- ABSENT: no meaningful capability exists.
- SCAFFOLD: contracts, placeholders, or thin deterministic plumbing exist.
- PARTIAL: a meaningful subset exists but important requirements remain.
- SCIENTIFICALLY INSUFFICIENT: executable or contractual elements exist but do not support the scientific claim implied by the capability.
- INTEGRATED: connected to the canonical state/evidence spine with explicit assumptions and provenance.
- VALIDATED: integrated capability with demonstrated scientific validation appropriate to its claim.
- OPERATIONAL: validated capability permitted by governance for its defined use.

The repository's present state must not be upgraded merely by naming a capability.

## Scope boundary

CeutIA is the general complex-systems inference, anticipation, causal-reasoning, resilience and decision-intelligence platform. It is not a clinical-only system.

OMNI-NET remains a separate preventive-medicine system. Clinical concepts may contribute generic primitives to CeutIA, but OMNI-NET's clinical taxonomy, 30-node architecture, RFR/LMR/IVO/CRS formulas, clinical DAG and clinical variable tiers must not become CeutIA's ontology.

## A — System ontology and representation

A1 multi-domain entities, agents, populations, institutions, infrastructures and environments
A2 canonical system identity and entity resolution
A3 observable variables versus latent variables versus proxies
A4 nested and hierarchical systems
A5 component/subsystem/system/supersystem relationships
A6 state vectors and multidimensional state
A7 current state versus historical trajectory
A8 time scales from high-frequency to long-term
A9 spatial scales from local to global
A10 regime representation and regime uncertainty
A11 transition states and candidate phase changes
A12 thresholds and validity domains
A13 endogenous versus exogenous drivers/shocks
A14 intervention versus observation semantics
A15 system boundaries and boundary uncertainty
A16 system membership and changing membership
A17 compositionality
A18 emergence
A19 equifinality and multifinality
A20 observability
A21 identifiability
A22 partial identification / multiple compatible states
A23 structural constraints and feasibility bounds
A24 conservation/balance constraints where applicable
A25 state-dependent transition pathways

## B — Observation, data-generating and evidence architecture

B1 streaming and batch observations
B2 event time versus ingestion/availability time
B3 observation windows and cutoff semantics
B4 longitudinal identity
B5 entity resolution and identity uncertainty
B6 source reliability
B7 source dependency and common-origin detection
B8 provenance to raw source
B9 provenance through every transformation
B10 dataset and schema versioning
B11 schema drift
B12 historical reconstruction
B13 replayability
B14 observation conflict preservation
B15 contradiction representation
B16 missingness representation
B17 MCAR/MAR/MNAR classification where applicable
B18 measurement error
B19 sensor uncertainty
B20 sampling mechanisms
B21 selection mechanisms
B22 survivorship bias
B23 collider/selection structures
B24 temporal leakage prevention
B25 observation-process change detection
B26 source availability/change detection
B27 measurement-process metadata
B28 data quality separate from truth probability
B29 negative evidence / expected-but-not-observed events
B30 evidence independence/dependence
B31 evidence contamination/laundering
B32 evidence aggregation without false independence
B33 transformation and preprocessing lineage
B34 reproducible historical snapshots
B35 evidence validity windows

## C — Canonical dynamic state and longitudinal estimation

C1 canonical SystemStateContract integration
C2 current state snapshot
C3 append-only trajectory
C4 state lineage
C5 uncertainty attached to state
C6 latent-state estimation
C7 Bayesian filtering
C8 Bayesian smoothing
C9 state-space models
C10 time-varying parameters
C11 observation models
C12 process models
C13 individual/entity trajectories
C14 population trajectories
C15 conditional baselines
C16 deviation-from-baseline
C17 context-dependent reference states
C18 derivative/velocity
C19 acceleration/deceleration
C20 change-point detection
C21 regime-switching state estimation
C22 missing-observation prediction
C23 uncertainty propagation
C24 correlated uncertainty
C25 state observability status
C26 state identifiability status
C27 measurement-versus-state separation
C28 trajectory segmentation
C29 trajectory comparison
C30 trajectory similarity under context
C31 state reconstruction from incomplete evidence
C32 state transition semantics
C33 state memory
C34 state history relevant to future response

## D — Causal intelligence

D1 explicit DAG representation
D2 structural causal models
D3 potential outcomes
D4 temporal causal graphs
D5 backdoor identification
D6 frontdoor identification
D7 time-varying confounding
D8 marginal structural models/reasoning
D9 collider protection
D10 mediator handling
D11 unmeasured-confounding sensitivity
D12 negative controls
D13 falsification tests
D14 causal discovery as hypothesis generation
D15 competing causal graphs
D16 mechanistic constraints on graphs
D17 intervention/do semantics
D18 state-conditioned counterfactuals
D19 mediation
D20 moderation/effect modification
D21 heterogeneous effects
D22 dose-response
D23 nonlinear causal effects
D24 delayed causal effects
D25 exposure windows
D26 feedback/simultaneous causality
D27 cross-domain causal chains
D28 regime-dependent causal effects
D29 causal transportability
D30 external validity
D31 positivity/overlap
D32 consistency/SUTVA-like assumptions where applicable
D33 model-misspecification sensitivity
D34 causal model ensembles
D35 causal disagreement preservation
D36 active causal learning
D37 intervention design
D38 intervention feasibility constraints
D39 intervention attribution
D40 post-intervention causal evaluation
D41 prospective causal validation
D42 causal identification versus estimation separation
D43 causal uncertainty decomposition
D44 observational equivalence of causal explanations
D45 discriminating observations/interventions

## E — Complex-system dynamics, resilience and transitions

E1 dynamic graph topology
E2 node state evolution
E3 edge state evolution
E4 changing centrality/influence
E5 community formation
E6 fragmentation
E7 propagation
E8 contagion
E9 cascades
E10 percolation/branching thresholds where justified
E11 feedback amplification
E12 feedback damping
E13 adaptive capacity
E14 reserve/capacity/load
E15 resilience reserve
E16 recovery trajectory
E17 recovery rate/capacity
E18 perturbation-response-recovery-adaptation cycle
E19 critical slowing down
E20 variance early warnings
E21 autocorrelation early warnings
E22 distributional early warnings
E23 recovery-time early warnings
E24 hysteresis
E25 memory
E26 path dependence
E27 multistability
E28 alternative attractors/regimes
E29 nonlinearity
E30 saturation
E31 amplification/damping thresholds
E32 higher-order interactions
E33 cross-scale coupling
E34 synchronization
E35 shock absorption versus amplification
E36 bottlenecks
E37 queues
E38 arrival/service flows
E39 constrained flow networks
E40 failure propagation
E41 state-dependent transition pathways
E42 reversibility/degradation
E43 transition distance
E44 threshold uncertainty
E45 early-warning false-positive control

## F — Forecasting and anticipation

F1 point forecasts
F2 probabilistic forecasts
F3 full predictive distributions
F4 calibrated predictive intervals
F5 multi-horizon forecasts
F6 scenario generation
F7 competing scenarios
F8 ensemble models
F9 model disagreement
F10 structural disagreement
F11 parameter disagreement
F12 calibration
F13 calibration drift
F14 distribution shift
F15 forecast validity windows
F16 triggered reforecasting
F17 rare-event forecasting
F18 tail-risk estimation
F19 asymmetric tail loss
F20 forecasts under missing observations
F21 forecasts under manipulated/adversarial observations
F22 endogenous/exogenous driver decomposition
F23 forecast decomposition by mechanism
F24 temporal backtesting
F25 prospective backtesting
F26 conformal/equivalent coverage where appropriate
F27 forecast abstention
F28 forecast failure registry
F29 forecast revision lineage
F30 scenario sensitivity

## G — Decision intelligence

G1 formal decision context
G2 action space
G3 objectives
G4 utility
G5 constraints
G6 resource budgets
G7 multi-objective optimisation
G8 Pareto trade-offs
G9 risk-sensitive utility
G10 regret
G11 opportunity cost
G12 robust decision making under deep uncertainty
G13 worst-case analysis
G14 minimax/regret-style robustness where appropriate
G15 value of information
G16 active sensing
G17 decision-specific causal identification
G18 counterfactual policy comparison
G19 policy simulation
G20 decision abstention
G21 human review
G22 prohibited autonomous interventions
G23 re-evaluation triggers
G24 action-conditional calibration
G25 outcome feedback
G26 longitudinal decision audit
G27 intervention feasibility
G28 reversibility of decisions
G29 resource allocation under uncertainty
G30 simulation-to-reality monitoring

## H — Adversarial, information and epistemic robustness

H1 source manipulation indicators
H2 coordinated information-operation hypotheses
H3 coordinated/bot behaviour indicators where justified
H4 narrative propagation
H5 narrative competition
H6 perception-versus-event separation
H7 source-dependency adversarial analysis
H8 data poisoning detection
H9 evidence laundering detection
H10 strategic deception hypotheses
H11 selection/deception effects
H12 provenance contamination
H13 unsupported-claim barriers
H14 hallucination containment
H15 LLM evidence boundary
H16 LLM state-mutation prohibition
H17 red-team alternative explanations
H18 adversarial causal hypotheses
H19 adversarial scenario generation
H20 adversarial stress testing
H21 epistemic-status preservation
H22 model-output versus evidence separation
H23 manipulation confidence versus event probability separation
H24 public versus OWNER epistemic boundaries

## I — Spatial, mobility and environmental intelligence

I1 geospatial coordinates
I2 coordinate reference systems
I3 geodesic distance
I4 GIS-grade spatial representation
I5 dynamic spatial graphs
I6 spatial trajectories
I7 mobility trajectories
I8 origin-destination flows
I9 spatial spillovers
I10 spatial causal effects
I11 geographic bottlenecks
I12 infrastructure dependencies
I13 environmental exposure trajectories
I14 climate/weather perturbations
I15 cross-border propagation
I16 spatial heterogeneity
I17 spatial intervention effects
I18 spatial-temporal interaction
I19 spatial regime changes
I20 environmental observation-process uncertainty

## J — Human, behavioural, institutional and population systems

J1 individual behavioural state
J2 group behavioural state
J3 institutional behavioural state
J4 adaptation to intervention
J5 strategic adaptation
J6 social contagion
J7 collective behaviour
J8 trust
J9 legitimacy
J10 polarisation dynamics
J11 collective action
J12 cooperation/competition
J13 resource competition
J14 vulnerability
J15 unequal exposure
J16 policy-perception feedback
J17 perception-behaviour feedback
J18 institutional capacity
J19 population composition dynamics
J20 migration/population shocks where relevant
J21 human-rights constraints
J22 sustainability constraints
J23 heterogeneous response
J24 behavioural nonstationarity

## K — Simulation, digital twins and generative system models

K1 executable transition models
K2 synchronized digital-twin state
K3 state-to-simulation initialization
K4 parameter calibration
K5 parameter uncertainty
K6 model discrepancy
K7 agent-based simulation
K8 network simulation
K9 intervention simulation
K10 counterfactual policy simulation
K11 scenario stress testing
K12 Monte Carlo uncertainty propagation
K13 stochastic simulation
K14 rare-event simulation
K15 sensitivity analysis
K16 structural uncertainty across simulations
K17 simulation validity domain
K18 simulation-to-real monitoring
K19 safe intervention sandbox
K20 simulation lineage/reproducibility

## L — Learning, adaptation and scientific memory

L1 prospective learning loops
L2 outcome-linked updates
L3 model versioning
L4 model governance
L5 champion/challenger models
L6 rollback
L7 drift detection
L8 calibration monitoring
L9 causal hypothesis lifecycle
L10 hypothesis creation/update/retirement
L11 evidence accumulation
L12 failed-hypothesis memory
L13 negative-result memory
L14 prediction-error memory
L15 intervention-response memory
L16 model-induced-data contamination control
L17 temporal separation of training and evaluation
L18 post-intervention learning boundaries
L19 model selection leakage prevention
L20 learning under distribution shift
L21 learning under regime change
L22 learning from non-occurrence
L23 active-learning query selection
L24 scientific knowledge versioning

## M — Epistemology, uncertainty and inference discipline

M1 observation versus measurement
M2 measurement versus inference
M3 inference versus explanation
M4 explanation versus causality
M5 causality versus prediction
M6 prediction versus recommendation
M7 recommendation versus intervention
M8 intervention outcome versus observational evidence
M9 epistemic-status transitions
M10 uncertainty taxonomy
M11 aleatory uncertainty
M12 epistemic uncertainty
M13 measurement uncertainty
M14 parameter uncertainty
M15 structural/model uncertainty
M16 regime uncertainty
M17 scenario uncertainty
M18 observability uncertainty
M19 identifiability uncertainty
M20 dependent uncertainty
M21 calibration status
M22 validity status
M23 evidence sufficiency
M24 insufficient-evidence output
M25 abstention
M26 contradiction preservation
M27 alternative explanation preservation
M28 observational equivalence
M29 mechanism discrimination
M30 falsifiability
M31 prospective prediction commitments
M32 confidence versus probability separation

## N — Governance, safety, security and accountability

N1 complete audit trail
N2 immutable provenance
N3 public/internal/OWNER/restricted separation
N4 data access boundaries
N5 privacy-preserving aggregation
N6 differential privacy where actually implemented
N7 security controls
N8 incident ledger
N9 emergency degradation
N10 checkpointing
N11 failover
N12 recovery
N13 external root of trust
N14 cryptographic integrity
N15 runtime enforcement
N16 model/assumption cards
N17 decision records
N18 intervention records
N19 prohibited inference classes
N20 prohibited autonomous actions
N21 human accountability
N22 human review escalation
N23 liability/audit ownership
N24 policy versioning
N25 governance-change lineage
N26 safety-case evidence
N27 dual-use controls
N28 adversarial security testing

## O — Validation and scientific evidence

O1 unit tests
O2 contract tests
O3 integration tests
O4 end-to-end tests
O5 temporal leakage tests
O6 synthetic causal benchmarks
O7 known-DAG recovery benchmarks
O8 confounding benchmarks
O9 intervention-effect benchmarks
O10 counterfactual benchmarks
O11 distribution-shift benchmarks
O12 adversarial benchmarks
O13 rare-event benchmarks
O14 calibration benchmarks
O15 prospective validation harness
O16 external validation
O17 cross-seed reproducibility
O18 sensitivity analysis
O19 ablation studies
O20 error taxonomy
O21 failure-mode catalogue
O22 scientific claims registry
O23 evidence-threshold registry
O24 insufficient-evidence test cases
O25 negative-result benchmarks
O26 model-disagreement benchmarks
O27 observational-equivalence benchmarks
O28 intervention-feedback contamination benchmarks
O29 simulation-to-real benchmarks
O30 spatial/geodesic benchmarks
O31 behavioural/adaptation benchmarks
O32 resilience/early-warning benchmarks
O33 measurement-process-change benchmarks
O34 missingness-mechanism benchmarks
O35 source-dependency benchmarks

## P — Operational ingestion and evidence lifecycle

P1 source discovery
P2 source allowlisting
P3 source health
P4 source availability monitoring
P5 ingestion orchestration
P6 event resolution
P7 deduplication
P8 replay
P9 schema-drift handling
P10 source-version tracking
P11 cutoff-aware ingestion
P12 evidence packaging
P13 evidence-to-state mapping
P14 ingestion failure handling
P15 ingestion provenance
P16 operational backpressure
P17 rate/queue control
P18 late-arriving data handling
P19 correction/retraction handling
P20 source retirement

## Q — Information architecture, semantics and knowledge representation

Q1 canonical terminology
Q2 semantic contracts
Q3 ontology versioning
Q4 entity identity semantics
Q5 relation semantics
Q6 temporal relation semantics
Q7 spatial relation semantics
Q8 causal relation semantics
Q9 epistemic relation semantics
Q10 evidence graph
Q11 semantic graph
Q12 claim/evidence linkage
Q13 hypothesis/evidence linkage
Q14 model/assumption linkage
Q15 decision/evidence linkage
Q16 intervention/outcome linkage
Q17 knowledge versioning
Q18 semantic migration
Q19 backward compatibility
Q20 contradiction semantics
Q21 provenance semantics
Q22 public/private information semantics

## R — Model lifecycle and reproducible computation

R1 model identity
R2 model version
R3 parameter version
R4 data version
R5 feature/preprocessing version
R6 dependency/environment version
R7 reproducible execution context
R8 deterministic replay where possible
R9 stochastic seed lineage
R10 model approval
R11 model retirement
R12 rollback
R13 champion/challenger
R14 model performance history
R15 calibration history
R16 drift history
R17 validity-domain history
R18 assumption changes
R19 model comparison
R20 model provenance

## S — Human-machine interaction and decision usability

S1 uncertainty-readable outputs
S2 evidence traceability for users
S3 alternative explanations visible
S4 contradiction visibility
S5 abstention visibility
S6 rationale traceability
S7 decision-option comparison
S8 intervention consequences visibility
S9 warning severity separation from certainty
S10 public/OWNER presentation boundaries
S11 human override recording
S12 review responsibility assignment
S13 escalation pathways
S14 cognitive-load control
S15 alert fatigue management
S16 explanation proportionality to evidence
S17 user feedback capture
S18 feedback provenance

## T — System resilience and operational continuity

T1 health monitoring
T2 graceful degradation
T3 failover
T4 checkpoint/recovery
T5 incident detection
T6 incident classification
T7 incident response
T8 recovery verification
T9 dependency failure isolation
T10 partial-service operation
T11 evidence backlog preservation
T12 state continuity across restart
T13 provenance continuity across recovery
T14 degraded epistemic status under missing dependencies
T15 emergency human escalation

## U — Cross-domain integration and scale transfer

U1 domain-agnostic core primitives
U2 domain-specific adapters
U3 domain ontology isolation
U4 cross-domain observation links
U5 cross-domain causal hypotheses
U6 cross-domain temporal alignment
U7 cross-domain spatial alignment
U8 scale translation
U9 cross-domain uncertainty propagation
U10 cross-domain intervention effects
U11 domain-specific validity boundaries
U12 transferability assessment
U13 transportability assessment
U14 domain-shift detection
U15 prohibition of silent domain assumptions

## V — Scientific search, sensing and experimental design

V1 information-gap detection
V2 value-of-information estimation
V3 active sensing
V4 observation prioritisation
V5 discriminating observation design
V6 discriminating intervention design
V7 experiment feasibility
V8 experiment cost
V9 experiment risk
V10 expected information gain
V11 expected decision improvement
V12 uncertainty-reduction attribution
V13 experiment outcome lineage
V14 experiment stopping rules
V15 sequential experimentation

## W — Failure, contradiction and adversarial learning memory

W1 failed predictions
W2 failed hypotheses
W3 failed interventions
W4 rejected causal graphs
W5 rejected model structures
W6 known confounders
W7 known proxy risks
W8 known source contamination
W9 known data-quality failures
W10 known regime failures
W11 model blind spots
W12 recurrent failure patterns
W13 negative evidence
W14 contradictory evidence
W15 unresolved contradictions
W16 historical decision mistakes
W17 postmortem learning
W18 anti-repeat mechanisms

## X — Integrated scientific lifecycle

X1 Observation → State
X2 State → Trajectory
X3 Trajectory → Dynamics
X4 Dynamics → Hypotheses
X5 Hypotheses → Causal models
X6 Causal models → Predictions
X7 Predictions → Decisions
X8 Decisions → Interventions
X9 Interventions → Responses
X10 Responses → Learning
X11 Learning → updated State
X12 lineage preserved across every transition
X13 uncertainty preserved across every transition
X14 epistemic status preserved across every transition
X15 alternative explanations preserved across every transition
X16 contradictions preserved across every transition
X17 intervention contamination controlled across every transition
X18 model/version/data lineage preserved across every transition

## Exhaustiveness rule

This inventory is exhaustive at the architectural capability level currently defined for CeutIA. It is deliberately broader than the existing A–O gap register because it includes the integration, semantic, operational, lifecycle, human-factors and second-order scientific requirements that can otherwise remain invisible when auditing modules individually.

It is not legitimate to declare the system complete by counting implemented files. Completeness requires that every applicable item have a defined status, owner/module boundary, assumptions, evidence requirements and dependency relationship.

Items that are domain-inapplicable must be explicitly marked NOT_APPLICABLE with a reason; they must not disappear from the inventory.

## Mandatory maturity matrix

For every item, future implementation records must distinguish:

`CONCEPT → CONTRACT → CODE → INTEGRATED → EXECUTABLE → VERIFIED → SCIENTIFICALLY VALIDATED → CALIBRATED → OPERATIONAL`

The first seven stages must never be inferred from the existence of a later document. Operational status requires all applicable preceding gates.

## Canonical architecture dependency order

The inventory must be implemented through the following dependency spine:

`Observation/Evidence → Canonical State → Latent State → Trajectory → Dynamics/Regimes/Resilience → Hypotheses → Causal Models → Forecasts/Scenarios → Decisions → Interventions → Responses → Learning → updated State`

Cross-cutting layers are:

`Provenance + Uncertainty + Epistemology + Semantics + Governance + Security + Human Review + Reproducibility + Failure Memory`

No specialist module should establish a competing canonical state representation.

## Explicit exclusions

- OMNI-NET clinical node taxonomy is excluded from the CeutIA ontology.
- OMNI-NET-specific clinical formulas are excluded from CeutIA's generic state model.
- A current scalar Kalman filter is not the complete latent-state solution.
- Current recovery metrics are descriptive primitives, not causal or predictive proof.
- Existing forecast-shaped objects are not automatically calibrated predictive distributions.
- A transition function is not automatically a digital twin.
- A governance contract is not automatically runtime enforcement.
- A CI pass is not scientific validation.

## Immediate implementation consequence

The next implementation work must use this inventory to close the architectural spine and its missing cross-links, rather than creating another isolated collection of specialist modules.

Final CI, validation, calibration and operational promotion remain deferred until the implementation cycle is complete, as explicitly required by the project workflow.
