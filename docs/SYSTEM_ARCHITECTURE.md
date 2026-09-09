Continuamos con el siguiente archivo, sin modificar ninguno de los anteriores:

docs/SYSTEM_ARCHITECTURE.md

# CEUTIA PUBLIC — System Architecture
## 1. Purpose
This document defines the technical and functional architecture of CEUTIA PUBLIC.
CEUTIA PUBLIC is a public intelligence, knowledge, dynamic-systems and citizen-support platform designed to observe, integrate, analyse and communicate information about Ceuta and the systems that influence it.
It is not a conventional dashboard, document repository, chatbot or static monitoring platform.
Its architecture must support the complete analytical lifecycle:
```text
Observe
  ↓
Ingest
  ↓
Normalize
  ↓
Validate
  ↓
Preserve provenance
  ↓
Represent semantically
  ↓
Corroborate / contradict
  ↓
Model
  ↓
Analyse dynamics
  ↓
Generate signals
  ↓
Evaluate hypotheses
  ↓
Estimate risks
  ↓
Generate scenarios / predictions
  ↓
Communicate
  ↓
Observe outcomes
  ↓
Calibrate
  ↓
Learn

The architecture is designed around five simultaneous requirements:

1. epistemic integrity;
2. dynamic-system modelling;
3. intelligence generation;
4. strict PUBLIC/OWNER separation;
5. responsible citizen interaction.

⸻

2. Architectural principles

2.1 Reality-first architecture

The platform SHALL distinguish the real-world phenomenon from:

* its observation;
* its measurement;
* its representation;
* its interpretation;
* its model;
* its prediction;
* its communication.

No presentation-layer object may silently become a source of truth.

⸻

2.2 Provenance-first architecture

Every consequential analytical object SHALL be traceable to its upstream information.

Output
  ↓
Analysis
  ↓
Model
  ↓
Inference
  ↓
Claim
  ↓
Evidence
  ↓
Observation
  ↓
Source

The system SHALL preserve this lineage.

⸻

2.3 Temporal-first architecture

CEUTIA is fundamentally a dynamic system.

The architecture therefore SHALL preserve:

* observation time;
* publication time;
* acquisition time;
* processing time;
* inference time;
* validity interval;
* revision history.

Current values must not erase historical trajectories.

⸻

2.4 Separation of concerns

The architecture SHALL separate:

Data
Semantic representation
Epistemology
Mathematics
Dynamic-system modelling
Intelligence
Citizen interaction
Security
Presentation

A component should not silently perform responsibilities belonging to another layer.

⸻

3. High-level architecture

                           ┌─────────────────────────┐
                           │     PUBLIC SOURCES      │
                           │                         │
                           │ APIs · datasets · RSS   │
                           │ scientific literature   │
                           │ institutions · media    │
                           │ sensors · public data   │
                           └────────────┬────────────┘
                                        │
                                        ▼
                           ┌─────────────────────────┐
                           │      INGESTION LAYER     │
                           └────────────┬────────────┘
                                        │
                                        ▼
                           ┌─────────────────────────┐
                           │  VALIDATION & NORMALIZE  │
                           └────────────┬────────────┘
                                        │
                                        ▼
                           ┌─────────────────────────┐
                           │    KNOWLEDGE LAYER       │
                           │                         │
                           │ entities · observations │
                           │ evidence · claims       │
                           │ provenance · relations  │
                           └────────────┬────────────┘
                                        │
                                        ▼
                 ┌────────────────────────────────────────────┐
                 │              ANALYTICAL CORE                │
                 │                                            │
                 │ epistemology                                │
                 │ dynamic systems                             │
                 │ mathematics                                 │
                 │ causal inference                            │
                 │ hypothesis engine                           │
                 │ scenario engine                             │
                 │ prediction                                  │
                 │ risk / resilience                           │
                 │ signals / alerts                            │
                 └───────────────────┬────────────────────────┘
                                     │
                    ┌────────────────┼─────────────────┐
                    │                │                 │
                    ▼                ▼                 ▼
             ┌────────────┐   ┌────────────┐   ┌──────────────┐
             │ INTELLIGENCE│   │  CITIZEN   │   │  GOVERNANCE  │
             │   OUTPUT    │   │ INTERFACE  │   │ / AUDIT      │
             └──────┬─────┘   └──────┬─────┘   └──────────────┘
                    │                │
                    ▼                ▼
              OWNER SIGNALS     PUBLIC USERS

The architecture is modular.

No single component should contain the complete system logic.

⸻

4. Architectural domains

CEUTIA PUBLIC SHALL be organized into the following principal domains:

backend/
├── ingestion/
├── normalization/
├── validation/
├── epistemology/
├── ontology/
├── knowledge/
├── dynamics/
├── mathematics/
├── intelligence/
├── hypotheses/
├── scenarios/
├── causal/
├── signals/
├── decisions/
├── citizen/
├── health/
├── governance/
├── security/
├── storage/
├── api/
└── observability/

The exact implementation may evolve.

The semantic responsibilities SHALL remain stable.

⸻

5. Layer 0 — External world

CEUTIA does not control the systems it observes.

The external world contains:

Population
Environment
Healthcare
Economy
Infrastructure
Information ecosystem
Migration flows
Geopolitical environment
Public institutions
Private organizations
Natural events
Social processes

The external world produces observations.

CEUTIA does not assume that all relevant variables are directly observable.

⸻

6. Layer 1 — Source and ingestion

The ingestion layer acquires authorized public information.

Potential source classes include:

Official APIs
Public datasets
Scientific publications
Institutional reports
Open statistical databases
Public websites
RSS / feeds
Public sensor data
Public announcements
Citizen-provided reports

Each ingestion operation SHALL generate metadata.

Minimum metadata:

source_id
acquired_at
source_timestamp
retrieval_method
retrieval_status
content_hash
source_version
parser_version

The raw input SHOULD be preserved when legally and technically appropriate.

⸻

7. Raw-data preservation

The architecture SHOULD maintain a raw immutable layer.

Conceptually:

RAW
 ↓
NORMALIZED
 ↓
VALIDATED
 ↓
SEMANTIC
 ↓
ANALYTICAL

Raw material SHALL NOT be silently modified during normalization.

Transformations must create new representations.

This permits:

* reproducibility;
* auditing;
* parser debugging;
* historical reconstruction;
* detection of transformation errors.

⸻

8. Layer 2 — Normalization

Different sources describe the same phenomenon using different:

* names;
* units;
* timestamps;
* geographic definitions;
* denominators;
* classifications;
* frequencies.

Normalization converts them into compatible representations without destroying source-specific information.

Examples:

"Hospital occupancy: 82%"
"Beds occupied: 41 / 50"

may be normalized into a common semantic representation while retaining the original values and methods.

Normalization SHALL NOT imply equivalence when equivalence has not been established.

⸻

9. Layer 3 — Validation

Validation occurs before analytical use.

Validation includes:

Schema validation
Type validation
Unit validation
Temporal validation
Spatial validation
Range validation
Consistency validation
Duplicate detection
Source integrity
Missingness detection

A technically valid datum is not necessarily epistemically reliable.

Therefore:

Technical validity ≠ Truth

⸻

10. Layer 4 — Ontology and semantic representation

The ontology defined in:

docs/CEUTIA_ONTOLOGY.md

provides the semantic contract.

This layer transforms normalized information into canonical entities such as:

Observation
DataPoint
Evidence
Claim
Hypothesis
Variable
State
Trajectory
Flow
Capacity
Pressure
Shock
Signal
Alert
Scenario
Prediction
Risk
Intervention
Outcome

The semantic layer is the bridge between raw information and analytical models.

⸻

11. Layer 5 — Knowledge layer

The knowledge layer stores relationships among entities.

Conceptually it forms a graph:

Source
  │
  ▼
Observation ─────► Variable
  │                  │
  ▼                  ▼
Evidence ────────► State
  │                  │
  ▼                  ▼
Claim ───────────► Trajectory
  │                  │
  ▼                  ▼
Hypothesis ──────► Mechanism
  │                  │
  └────────────┬─────┘
               ▼
             Model

The graph must preserve provenance and temporal validity.

⸻

12. Polyglot storage architecture

CEUTIA should not force every data type into one database paradigm.

Different workloads require different storage models.

Conceptually:

Relational database
    ↓
structured entities / metadata / transactions
Time-series database
    ↓
temporal measurements / trajectories
Object storage
    ↓
raw documents / datasets / immutable artifacts
Search index
    ↓
full-text retrieval
Vector index
    ↓
semantic retrieval
Graph representation
    ↓
relationships / provenance / dependency networks
Cache
    ↓
frequently accessed derived state

The authoritative semantic model SHALL remain independent of the storage technology.

⸻

13. Layer 6 — Epistemological engine

The epistemological engine evaluates information quality.

It SHALL handle:

Provenance
Source quality
Source independence
Corroboration
Contradiction
Uncertainty
Confidence
Temporal validity
Evidence strength
Claim status
Belief revision

It must answer questions such as:

What supports this claim?
How independent are the sources?
What contradicts it?
When was the evidence observed?
How uncertain is the measurement?
Has the claim changed?

The engine must never manufacture confidence merely because information is abundant.

⸻

14. Layer 7 — Dynamic-system engine

The dynamic-system engine models how variables evolve and interact.

Core concepts:

State
Trajectory
Flow
Pressure
Capacity
Reserve
Shock
Feedback
Bottleneck
Threshold
Cascade
Recovery

It may implement multiple mathematical approaches.

Possible families include:

Differential equations
Difference equations
State-space models
Compartment models
Queueing models
Network models
Agent-based models
System dynamics
Time-series models
Survival/hazard models
Markov processes
Stochastic processes
Nonlinear dynamics

No single modelling paradigm should be assumed to describe all CEUTIA phenomena.

⸻

15. Layer 8 — Mathematical engine

The mathematical layer operates on semantically defined variables.

It may calculate:

rates of change
acceleration
moving averages
variance
volatility
entropy
correlations
partial correlations
lags
cross-correlations
network centrality
flow concentration
capacity utilization
reserve
pressure
threshold proximity
change-point probability
anomaly scores
propagation velocity
recovery rate

Advanced methods may include:

Bayesian inference
Monte Carlo simulation
Kalman filtering
particle filtering
optimization
sensitivity analysis
uncertainty propagation
causal estimation
counterfactual simulation

Mathematical sophistication SHALL NOT compensate for poor epistemology.

⸻

16. Layer 9 — Causal inference

The causal layer evaluates candidate mechanisms.

It SHALL distinguish:

association
temporal precedence
mechanistic plausibility
causal identification
causal estimation
counterfactual effect

Potential methods include:

Directed acyclic graphs
Structural causal models
Interrupted time series
Difference-in-differences
Synthetic controls
Instrumental variables
Regression discontinuity
Natural experiments
Longitudinal models

The method selected must match the causal question and available data.

⸻

17. Layer 10 — Hypothesis engine

The hypothesis engine maintains competing explanations.

Architecture:

Observation
     ↓
Candidate explanations
     ├── H1
     ├── H2
     ├── H3
     └── H4
          ↓
Predicted observations
          ↓
New evidence
          ↓
Update
          ↓
Rank / weaken / reject / preserve

The engine SHALL prevent premature convergence on a single explanation.

A hypothesis with high current probability can still be wrong.

⸻

18. Layer 11 — Scenario engine

The scenario engine explores possible system trajectories.

It SHALL distinguish:

Forecast
Scenario
Stress test
Counterfactual
Sensitivity analysis

A scenario must contain explicit assumptions.

Example:

Scenario:
    sustained demand increase
Assumptions:
    effective capacity remains constant
    inflow persists
    recovery rate declines
Outputs:
    pressure trajectory
    reserve depletion
    bottleneck probability
    threshold proximity

⸻

19. Layer 12 — Signal detection

Signal detection transforms system observations into early indicators.

Potential signal classes:

Trend signal
Acceleration signal
Persistence signal
Anomaly signal
Correlation-break signal
Synchronization signal
Network-propagation signal
Threshold signal
Capacity-depletion signal
Contradiction signal
Information-distortion signal

Signal generation SHALL preserve:

input variables
baseline
method
threshold
uncertainty
confidence
timestamp

⸻

20. Layer 13 — Alerting

Signals become alerts only after operational criteria are satisfied.

Observation
   ↓
Pattern
   ↓
Signal
   ↓
Validation
   ↓
Alert criteria
   ↓
Alert

The system SHALL avoid alert inflation.

Too many alerts reduce attention and may increase perceived instability.

Alert thresholds should therefore be evaluated empirically.

⸻

21. Layer 14 — Intelligence synthesis

The intelligence layer combines:

Evidence
State
Trajectory
Hypotheses
Models
Signals
Risks
Scenarios
Predictions
Uncertainty

It generates structured intelligence products such as:

Situation assessment
Trajectory assessment
Early-warning signal
Risk assessment
Hypothesis assessment
Scenario assessment
Systemic interaction analysis
Prediction

Every intelligence product must expose its epistemic status.

⸻

22. Layer 15 — Decision support

CEUTIA PUBLIC may generate decision-support information.

It SHALL NOT silently convert analytical outputs into autonomous high-consequence decisions.

Decision-support outputs should contain:

Problem
Current state
Trajectory
Relevant evidence
Competing explanations
Uncertainty
Potential consequences
Available options
Expected effects
Potential unintended effects
Monitoring variables

Where appropriate, the system should recommend collecting additional information rather than acting on insufficient evidence.

⸻

23. Layer 16 — Citizen interaction

The citizen layer is separate from the intelligence core.

Citizen Interface
       ↓
Public Knowledge
       ↓
Evidence-informed Guidance
       ↓
Optional Interaction
       ↓
Privacy-preserving Aggregate Signal
       ↓
Analytical Core

The citizen interface may provide:

* public information;
* explanations;
* prevention guidance;
* wellbeing resources;
* contextualized system information;
* links to appropriate services;
* de-escalation support;
* optional questions.

It SHALL NOT expose restricted intelligence.

⸻

24. Citizen support architecture

The citizen support subsystem SHALL prioritize:

Safety
Dignity
Autonomy
Clarity
Evidence
Uncertainty transparency
Human escalation

It SHALL avoid:

diagnosis without clinical evaluation
automated prescribing
coercion
fear amplification
targeted manipulation
stigma
group-based threat attribution
false reassurance

When an interaction indicates that automated support is insufficient, the system should direct the person toward an appropriate human or professional resource.

⸻

25. Information-to-behaviour feedback loop

Citizen communication can change the system being observed.

Therefore:

System state
   ↓
CEUTIA information
   ↓
Public perception
   ↓
Behaviour
   ↓
System state

The architecture SHALL model this as a potential feedback loop.

Examples:

Alert
→ increased vigilance
→ increased reporting
→ apparent incident increase
→ higher perceived risk

The increase in reports must not automatically be interpreted as an equivalent increase in underlying incidence.

⸻

26. Health and wellbeing subsystem

The public health layer SHALL operate as a prevention and information component.

It may monitor aggregate indicators involving:

healthcare demand
population wellbeing
environmental exposures
service pressure
behavioural indicators
social determinants
recovery capacity

It must preserve the distinction between:

individual health support

and:

population-level intelligence

No person should become an intelligence target merely because they request support.

⸻

27. Public system monitoring

CEUTIA PUBLIC SHALL monitor multiple interacting domains.

Minimum domain families:

Health
Population
Migration
Environment
Climate
Infrastructure
Transport
Economy
Energy
Food
Information
Social dynamics
Geopolitics
Public services
Emergency systems

The architecture must permit new domains without redesigning the entire platform.

⸻

28. Cross-domain coupling

Domains are represented independently but connected through explicit relationships.

Example:

Geopolitics
      ↓
Energy
      ↓
Economy
      ↓
Household pressure
      ↓
Behaviour
      ↓
Health
      ↓
Healthcare demand
      ↓
System capacity

Each transition SHALL have an epistemic status.

The existence of a plausible chain is not proof that the entire chain is active in reality.

⸻

29. Network architecture

Many CEUTIA phenomena are network phenomena.

The platform SHALL support:

nodes
edges
edge direction
edge weight
edge uncertainty
temporal validity
community structure
centrality
dependency
propagation
feedback

Networks may represent:

* actors;
* infrastructure;
* supply chains;
* information propagation;
* geopolitical relationships;
* healthcare dependencies;
* transport;
* population flows.

⸻

30. Event-driven architecture

CEUTIA should support event-driven processing.

Conceptually:

New source
   ↓
Ingestion event
   ↓
Validation event
   ↓
Observation created
   ↓
Knowledge update
   ↓
Model recalculation
   ↓
Signal evaluation
   ↓
Alert evaluation
   ↓
Output update

Not every event must trigger the complete analytical pipeline.

The system should use dependency-aware recomputation.

⸻

31. Batch and streaming computation

CEUTIA requires both.

Streaming or near-real-time processing is appropriate for:

alerts
rapid flows
weather
infrastructure incidents
information propagation
operational pressure

Batch processing is appropriate for:

longitudinal analysis
model retraining
historical reconstruction
calibration
deep causal analysis
scenario generation

The architecture SHALL support both without confusing their epistemic properties.

⸻

32. Model registry

Every production analytical model SHALL have a registry entry containing:

model_id
name
version
purpose
inputs
outputs
assumptions
training_data
validation_data
method
parameters
limitations
uncertainty
performance
calibration
deployment_status
created_at
updated_at

Models SHALL be versioned.

A new model version must not erase the performance history of previous versions.

⸻

33. Feature and variable registry

The platform SHALL maintain a canonical registry of analytical variables.

Each variable should define:

variable_id
name
definition
domain
unit
spatial_resolution
temporal_resolution
source_classes
transformation
missing-data policy
quality requirements
privacy classification

This prevents semantically identical variables from being independently implemented under incompatible definitions.

⸻

34. Data quality architecture

Data quality SHALL be multidimensional.

At minimum:

Completeness
Accuracy
Timeliness
Consistency
Validity
Granularity
Representativeness
Independence
Provenance quality
Measurement uncertainty

A dataset can be highly complete and still be systematically biased.

⸻

35. Missing data

Missingness SHALL be represented explicitly.

The system should distinguish:

not measured
not available
not reported
temporarily unavailable
structurally unavailable
unknown
not applicable
suppressed for privacy

These states have different meanings.

Missing values must not automatically become zero.

⸻

36. Data lineage

Every transformed analytical object should be traceable.

Example:

Raw document
   ↓
Parser v1.3
   ↓
Normalized record
   ↓
Validation
   ↓
Observation O-123
   ↓
DataPoint D-456
   ↓
Trajectory T-789
   ↓
Signal S-101
   ↓
Alert A-202

A user with appropriate permissions must be able to reconstruct the chain.

⸻

37. Security architecture integration

Security is not a presentation-layer feature.

It operates across all layers.

Identity
 ↓
Authentication
 ↓
Authorization
 ↓
Data classification
 ↓
Access policy
 ↓
Processing
 ↓
Output filtering
 ↓
Audit

Every layer must respect the security boundary.

⸻

38. PUBLIC / OWNER boundary

The architecture SHALL enforce an actual technical boundary between PUBLIC and OWNER.

                         CEUTIA
                           │
              ┌────────────┴────────────┐
              │                         │
           PUBLIC                     OWNER
              │                         │
       public datasets           private datasets
       public intelligence       restricted intelligence
       citizen interface         private analysis
       public outputs            owner outputs

The boundary SHALL exist at:

data
storage
authentication
authorization
API
processing
model inputs
model outputs
logs
exports

PUBLIC must not be able to query OWNER-private data.

OWNER may consume explicitly approved PUBLIC outputs.

⸻

39. PUBLIC-to-OWNER signal interface

The preferred communication path is:

PUBLIC analytical core
        ↓
Signal qualification
        ↓
Privacy/security filter
        ↓
OWNER ingestion boundary
        ↓
OWNER analytical environment

Only explicitly authorized objects may cross the boundary.

Examples:

aggregate signal
system trajectory
public anomaly
public risk indicator
public evidence package

Individual citizen information SHALL NOT cross merely because it could be analytically useful.

⸻

40. Output architecture

CEUTIA outputs should be represented as typed objects.

Output
├── Information
├── Signal
├── Alert
├── Assessment
├── Hypothesis assessment
├── Prediction
├── Scenario
├── Risk assessment
└── Citizen guidance

Every output SHALL contain:

timestamp
scope
epistemic status
confidence
uncertainty
provenance
model version
validity

⸻

41. API architecture

The API should expose semantic operations rather than raw database structures.

Conceptual endpoints:

/api/v1/observations
/api/v1/evidence
/api/v1/claims
/api/v1/hypotheses
/api/v1/variables
/api/v1/trajectories
/api/v1/signals
/api/v1/alerts
/api/v1/scenarios
/api/v1/predictions
/api/v1/risks
/api/v1/citizen

The actual API design SHALL be defined separately.

Internal services must not expose unrestricted persistence-layer access.

⸻

42. Query architecture

Queries should support several modes:

Descriptive
Temporal
Spatial
Relational
Epistemic
Causal
Dynamic
Predictive
Scenario

Examples:

What happened?
How fast is it changing?
Where is it changing?
What variables are moving together?
What evidence supports this?
What contradicts it?
Which hypotheses explain it?
What could happen next?
What happens under scenario X?
What has the model predicted before?

⸻

43. Observability architecture

CEUTIA SHALL observe itself.

Internal observability should include:

ingestion latency
source failures
parser failures
data freshness
pipeline latency
model execution
model errors
alert volume
false-positive rate
false-negative indicators where measurable
API latency
system availability
security events

A platform designed to detect systemic instability must itself be monitored as a system.

⸻

44. Audit architecture

Important actions SHALL generate audit records.

Examples:

source added
source modified
model deployed
model changed
claim revised
hypothesis updated
alert generated
alert suppressed
data accessed
data exported
permission changed
security policy changed

Audit records SHALL be tamper-resistant according to the security architecture.

⸻

45. Failure architecture

Failure must be expected.

Potential failures include:

source outage
API outage
corrupted data
stale data
parser failure
model failure
storage failure
network failure
false alarm
missed signal
epistemic error
security breach

The system should degrade gracefully.

Critical failures must not silently produce apparently valid intelligence.

⸻

46. Epistemic degradation

When data quality deteriorates, the system should degrade epistemically before degrading semantically.

Example:

Fresh data unavailable
        ↓
Confidence decreases
        ↓
Prediction interval widens
        ↓
Alert threshold may change
        ↓
Output explicitly marked stale

The system must not continue presenting stale information with normal confidence.

⸻

47. Computational reproducibility

Important analyses SHALL be reproducible.

A reproducible analytical result requires:

input versions
source versions
code version
model version
parameters
configuration
timestamp
random seed where relevant
environment

Where deterministic reproducibility is impossible, the source of stochastic variation SHALL be recorded.

⸻

48. Model calibration

Predictions must be evaluated against outcomes.

For probabilistic predictions, CEUTIA should evaluate:

calibration
discrimination
sharpness
Brier score
log loss
reliability
prediction interval coverage

Metrics SHALL be selected according to prediction type.

Model performance must be monitored over time because calibration may drift.

⸻

49. Concept drift

The system must assume that relationships can change.

Possible causes:

policy change
population change
climate change
infrastructure change
economic regime change
technological change
geopolitical change
behavioural adaptation
measurement change

Therefore a model trained under one regime may become invalid under another.

CEUTIA SHALL support drift detection and model re-evaluation.

⸻

50. Regime detection

The system should support detection of changes in system behaviour.

Potential indicators:

change points
variance shifts
correlation changes
autocorrelation changes
distribution shifts
network restructuring
response-function changes
critical slowing down

A regime change should trigger model review.

⸻

51. Computational efficiency

The system SHALL distinguish:

real-time calculations
near-real-time calculations
scheduled calculations
on-demand deep analysis

Expensive models should not be executed unnecessarily after every low-impact update.

Dependency graphs should determine which models require recalculation.

⸻

52. Scalability

The architecture must scale across:

data volume
number of sources
number of variables
number of models
temporal resolution
geographic scope
concurrent users
analytical complexity

Scaling must not weaken semantic integrity.

⸻

53. Extensibility

A new domain should be introducible by adding:

domain ontology
variables
sources
validators
models
signals
visualizations
API resources

without rewriting the core epistemological architecture.

⸻

54. Configuration over hardcoding

Operational parameters SHOULD be configurable.

Examples:

thresholds
time windows
source priorities
refresh intervals
alert sensitivity
model selection
confidence criteria
data-quality requirements

However, epistemological invariants and security invariants must not be casually configurable.

⸻

55. Architecture of trust

CEUTIA’s trust model is cumulative.

Data integrity
      +
Provenance
      +
Independence
      +
Corroboration
      +
Methodological validity
      +
Temporal validity
      +
Calibration
      +
Transparent uncertainty
      ↓
Analytical reliability

No single component guarantees truth.

Trust emerges from the integrity of the complete chain.

⸻

56. Architecture against disinformation

CEUTIA should not attempt merely to identify “false information.”

It should model the information environment.

Relevant dimensions include:

claim propagation
source lineage
source independence
velocity
amplification
repetition
contradiction
correction latency
audience exposure
temporal coincidence
network structure
uncertainty

The architecture should permit questions such as:

Where did a claim originate?
How quickly did it propagate?
Which sources independently corroborate it?
Which sources merely repeat it?
What evidence contradicts it?
How long did correction take?
Did the information change behaviour?
Did behaviour subsequently alter the measured system?

The objective is epistemic resilience rather than censorship.

⸻

57. Architecture against escalation

The system must distinguish:

monitoring
warning
communication
intervention

Information intended to reduce escalation should be:

accurate
proportionate
contextualized
uncertainty-aware
non-stigmatizing
non-inflammatory

The architecture SHALL not optimize communication for maximum emotional engagement when that conflicts with public safety.

⸻

58. Human oversight

High-consequence analytical outputs SHOULD support human review.

Human oversight is especially important when outputs concern:

public safety
health
security
large populations
vulnerable groups
high uncertainty
potential escalation
major interventions

The system should make its reasoning inspectable rather than asking users to trust an opaque score.

⸻

59. Explainability architecture

For important outputs, the system should be able to answer:

Why was this detected?
Which variables changed?
Compared with what baseline?
Which sources support it?
How independent are they?
What contradicts it?
Which model produced the result?
What assumptions were used?
How uncertain is the result?
Which alternative hypotheses remain plausible?

This is analytical explainability, not merely natural-language explanation.

⸻

60. Security and privacy by architecture

Security controls SHALL be implemented before data reaches sensitive analytical components.

The system should follow:

least privilege
least data
purpose limitation
data minimization
segmentation
encryption
auditing
revocation
defence in depth

Public availability of information does not automatically justify unlimited processing or retention.

⸻

61. Data lifecycle

Every data object follows a controlled lifecycle:

Acquire
  ↓
Validate
  ↓
Normalize
  ↓
Classify
  ↓
Store
  ↓
Analyse
  ↓
Publish / retain
  ↓
Update
  ↓
Supersede
  ↓
Archive / delete according to policy

Retention requirements are governed separately by data governance and privacy policies.

⸻

62. Architecture of uncertainty propagation

Uncertainty should propagate through analytical transformations.

Conceptually:

Measurement uncertainty
        ↓
Variable uncertainty
        ↓
State uncertainty
        ↓
Trajectory uncertainty
        ↓
Model uncertainty
        ↓
Prediction uncertainty
        ↓
Decision uncertainty

A highly uncertain input cannot legitimately produce an artificially precise final output without an explicit justification.

⸻

63. Architecture of contradiction

Contradictory information enters the system as an object rather than an error to be automatically removed.

Claim A
   ↕
Contradiction
   ↕
Claim B

The system evaluates:

source independence
measurement quality
temporal validity
methodological differences
possible reconciliation

If the contradiction cannot be resolved, it remains unresolved.

⸻

64. Architecture of knowledge evolution

Knowledge evolves through revision.

Version 1
   ↓
New evidence
   ↓
Version 2
   ↓
Contradictory evidence
   ↓
Version 3

Historical versions remain available for audit and retrospective analysis.

This allows CEUTIA to study not only what it currently believes, but how and why its beliefs changed.

⸻

65. Core computational loop

The complete operational loop is:

┌───────────────────────────────┐
│         EXTERNAL WORLD        │
└───────────────┬───────────────┘
                ↓
         PUBLIC SOURCES
                ↓
            INGESTION
                ↓
          NORMALIZATION
                ↓
           VALIDATION
                ↓
          OBSERVATIONS
                ↓
       EPISTEMOLOGICAL LAYER
                ↓
          KNOWLEDGE GRAPH
                ↓
       DYNAMIC SYSTEM STATE
                ↓
       MATHEMATICAL ANALYSIS
                ↓
      CAUSAL / HYPOTHESIS MODELS
                ↓
       SIGNALS / RISK / SCENARIOS
                ↓
          INTELLIGENCE
                ↓
       ┌────────┴────────┐
       ↓                 ↓
 PUBLIC COMMUNICATION   OWNER SIGNAL
       ↓
  CITIZEN RESPONSE
       ↓
  SYSTEM FEEDBACK
       ↓
 NEW OBSERVATIONS
       └───────────────→ LOOP

⸻

66. Fundamental architectural rule

CEUTIA must never become a system that merely accumulates data.

Its architecture must transform:

data

into:

structured knowledge

then:

dynamic understanding

then:

testable hypotheses

then:

calibrated predictions and scenarios

while preserving uncertainty and provenance at every step.

⸻

67. Final architectural principle

The system is not organized around screens.

It is organized around reality.

The primary unit is therefore not the dashboard widget but the semantically defined observation and its position within an evolving system.

The architecture exists to reconstruct trajectories, interactions and mechanisms from fragmented observations without confusing the reconstruction with reality itself.

Its fundamental loop is:

OBSERVE
→ REPRESENT
→ VERIFY
→ CONNECT
→ MODEL
→ CHALLENGE
→ PREDICT
→ OBSERVE AGAIN
→ CALIBRATE
→ LEARN

CEUTIA PUBLIC SHALL therefore be designed as a continuously learning epistemic and dynamic-system infrastructure, not as a static information portal.

The ultimate architectural requirement is:

The system must be able to say not only what it believes, but why it believes it, how strongly it believes it, what could prove it wrong, what it predicted previously, what actually happened, and how that changed its model of the system.

