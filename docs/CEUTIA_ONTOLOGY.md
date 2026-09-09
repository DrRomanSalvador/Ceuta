
# CEUTIA Ontology
## 1. Purpose
This document defines the formal ontology of CEUTIA PUBLIC.
The ontology establishes what kinds of entities, observations, evidence, claims, mechanisms, states, events, trajectories, signals, risks, scenarios and interventions CEUTIA is allowed to represent, how they relate to one another, and which conceptual distinctions must never be collapsed.
The ontology is normative.
It is not merely a database schema. It defines the semantic layer upon which data ingestion, epistemological evaluation, dynamic-system modelling, mathematical analysis, intelligence generation, citizen interaction and decision support operate.
The central principle is:
> CEUTIA must represent reality as an evolving system of observations, states, relationships, processes and uncertainties rather than as a collection of isolated facts.
The ontology must therefore preserve:
- what was observed;
- how it was observed;
- when and where it was observed;
- who or what generated the observation;
- what evidence supports an interpretation;
- which interpretations are hypotheses;
- how independent the evidence is;
- what remains uncertain;
- how the system evolves over time;
- which mechanisms may connect variables;
- what signals emerge from the system;
- what predictions are made;
- what actually happens afterwards.
---
# 2. Ontological principles
## 2.1 Reality, observation and interpretation are different layers
CEUTIA SHALL distinguish at minimum:
```text
REALITY
    ↓
EVENT / STATE / PROCESS
    ↓
OBSERVATION
    ↓
DATA
    ↓
EVIDENCE
    ↓
CLAIM
    ↓
INFERENCE
    ↓
HYPOTHESIS
    ↓
MODEL
    ↓
PREDICTION
    ↓
DECISION / INTERVENTION
    ↓
OUTCOME
    ↓
NEW OBSERVATION

No layer may be silently substituted for another.

An observation is not a claim.

A claim is not a fact merely because it is stored.

A hypothesis is not an established explanation.

A prediction is not an observation.

A scenario is not a forecast.

An intervention is not an outcome.

⸻

3. Core entity taxonomy

The CEUTIA ontology contains the following primary entity classes.

3.1 World entities

Entity
├── Person
├── Population
├── Organization
├── Institution
├── Actor
├── Territory
├── GeographicUnit
├── Infrastructure
├── Resource
├── Service
├── System
├── Subsystem
├── Network
└── Environment

These represent entities existing independently of CEUTIA’s interpretation of them.

⸻

4. Person

A Person represents an individual human being.

A person SHALL NOT automatically be represented as:

* a threat;
* a risk;
* a criminal;
* a migrant;
* a patient;
* a sensor;
* an anomaly;
* an intelligence object.

Those are contextual classifications that require explicit evidence and semantic justification.

The ontology SHALL enforce:

Person ≠ Threat
Person ≠ Risk
Person ≠ Sensor
Person ≠ Event
Person ≠ Evidence
Person ≠ Claim

Where individual-level data is unnecessary for a system-level inference, CEUTIA SHOULD prefer aggregated or anonymized representations.

⸻

5. Population

A Population is a defined set of persons sharing one or more explicit inclusion criteria.

A population SHALL have:

* definition;
* inclusion criteria;
* exclusion criteria;
* temporal validity;
* spatial scope;
* denominator;
* estimation method;
* uncertainty where applicable.

Examples:

Population:
    residents of Ceuta
Population:
    healthcare workers in Ceuta
Population:
    people attending emergency services during interval T
Population:
    arrivals recorded during interval T

Population definitions SHALL NOT be inferred solely from labels.

⸻

6. Territory

A Territory represents a spatially bounded or conceptually defined geographic domain.

Examples include:

* Ceuta;
* districts;
* neighborhoods;
* healthcare catchment areas;
* border zones;
* maritime areas;
* transport corridors.

Territorial entities SHALL support hierarchical and overlapping relationships.

Ceuta
├── Administrative units
├── Healthcare areas
├── Transport areas
├── Population areas
├── Infrastructure areas
└── Risk/exposure areas

Different territorial partitions SHALL be allowed to coexist.

⸻

7. System

A System is a set of interacting components whose collective behaviour cannot be adequately described by considering each component independently.

A system SHALL contain:

* components;
* boundaries;
* state variables;
* flows;
* interactions;
* constraints;
* feedback mechanisms;
* external inputs;
* outputs;
* temporal dynamics.

Examples:

Healthcare system
Social system
Economic system
Migration system
Transport system
Information ecosystem
Environmental system
Energy system
Geopolitical system

CEUTIA SHALL NOT assume that these systems are independent.

⸻

8. Subsystem

A Subsystem is a functionally or analytically distinguishable component of a larger system.

Example:

Healthcare system
├── Primary care
├── Emergency care
├── Hospital capacity
├── Ambulance system
├── Workforce
├── Supply chain
└── Pharmaceutical availability

A subsystem may itself contain additional systems and subsystems.

⸻

9. Variable

A Variable represents a measurable, estimated or modelled property that may change over time.

Variables SHALL have:

* semantic definition;
* unit;
* domain;
* measurement method;
* temporal resolution;
* spatial resolution;
* source;
* uncertainty;
* validity interval.

Examples:

population
arrival_rate
hospital_occupancy
waiting_time
staff_absence
energy_price
air_temperature
consultation_volume
information_velocity

A variable is not equivalent to its current value.

Variable ≠ DataPoint

⸻

10. DataPoint

A DataPoint is a time- and context-specific value associated with a variable.

Minimum semantic structure:

DataPoint
├── variable
├── value
├── unit
├── observed_at
├── spatial_scope
├── source
├── measurement_method
├── quality
└── uncertainty

Example:

hospital_occupancy = 87%
observed_at = T
location = Ceuta
source = X

The value SHALL NOT be interpreted without its temporal and contextual metadata.

⸻

11. Observation

An Observation records that something was observed or measured.

An observation SHALL preserve the distinction between:

what was observed

and

what someone believes the observation means

An observation may generate one or more DataPoints.

One observation may also contribute to multiple competing hypotheses.

⸻

12. Event

An Event represents an occurrence bounded in time.

Events may be:

* planned;
* observed;
* reported;
* detected;
* inferred;
* confirmed;
* disputed.

Examples:

hospital outage
border crossing episode
extreme weather event
cyber incident
mass gathering
policy change
price shock
transport disruption

An event SHALL NOT automatically be treated as the cause of subsequent changes.

Event ≠ Cause

Causality requires additional analysis.

⸻

13. Process

A Process represents an evolving transformation occurring over time.

Examples:

population displacement
disease transmission
resource depletion
polarization
economic deterioration
recovery
institutional adaptation
information diffusion

Processes are particularly important because CEUTIA is designed to detect trajectories rather than merely catalogue events.

⸻

14. State

A State represents the condition of a system or subsystem at a given time.

A state may be represented by a vector:

S(t) = [x₁(t), x₂(t), ..., xₙ(t)]

where each xᵢ(t) represents a relevant state variable.

The same numerical value may have different implications depending on:

* previous state;
* trajectory;
* rate of change;
* accumulated load;
* reserve;
* coupling;
* environmental conditions;
* recovery capacity.

Therefore:

State(t) ≠ isolated measurement

⸻

15. Trajectory

A Trajectory represents the temporal evolution of one or more variables or states.

Conceptually:

T = {S(t₀), S(t₁), ..., S(tₙ)}

CEUTIA SHALL analyse at minimum:

* level;
* direction;
* rate of change;
* acceleration/deceleration;
* persistence;
* volatility;
* reversibility;
* divergence;
* convergence;
* synchronization;
* regime change.

A static value without trajectory context SHALL be considered epistemically incomplete whenever temporal information is available.

⸻

16. Flow

A Flow represents movement through a system.

Examples:

* people;
* patients;
* vehicles;
* goods;
* energy;
* money;
* information;
* healthcare demand.

Flows SHALL be characterized by:

* origin;
* destination;
* volume;
* rate;
* duration;
* direction;
* temporal concentration;
* capacity;
* bottlenecks.

The ontology explicitly distinguishes:

volume ≠ rate
rate ≠ acceleration
total demand ≠ instantaneous demand

For example:

1,000 people / 30 days

is not equivalent to:

1,000 people / 3 hours

even when cumulative volume is identical.

⸻

17. Capacity

Capacity represents the theoretical or nominal ability of a system or subsystem to perform a function.

Examples:

hospital beds
ambulances
staff
ICU places
housing units
transport capacity
energy generation
information-processing capacity

CEUTIA SHALL distinguish:

Global Capacity
Effective Capacity
Available Capacity
Accessible Capacity
Deployable Capacity
Remaining Capacity

These concepts MUST NOT be collapsed.

A system can have substantial theoretical capacity while having little operational capacity.

⸻

18. Load

Load represents the demand imposed on a system or subsystem.

Load may be:

* instantaneous;
* cumulative;
* sustained;
* intermittent;
* concentrated;
* distributed.

Examples:

patient load
traffic load
information load
economic load
staff workload

The relationship between load and capacity is dynamic.

⸻

19. Pressure

Pressure represents the relative demand imposed upon available system resources.

A basic conceptual representation is:

Pressure(t) = Load(t) / EffectiveCapacity(t)

The operational implementation may use more complex formulations.

Pressure SHALL NOT be interpreted solely from absolute demand.

⸻

20. Reserve

Reserve represents the remaining adaptive margin available to a system before meaningful degradation or failure.

Conceptually:

Reserve(t) = EffectiveCapacity(t) - CurrentLoad(t)

More advanced implementations may incorporate:

* recovery time;
* redundancy;
* workforce flexibility;
* supply availability;
* substitution capacity;
* spatial redistribution;
* latent capacity.

A system with positive reserve may nevertheless be fragile if reserve is declining rapidly.

⸻

21. Shock

A Shock is an exogenous or endogenous perturbation that changes one or more system variables substantially relative to baseline.

A shock SHALL be characterized by:

* magnitude;
* duration;
* onset;
* rate of onset;
* affected subsystems;
* propagation;
* recovery;
* reversibility.

The ontology distinguishes:

Shock magnitude
Shock velocity
Shock duration
Shock persistence

These are separate properties.

⸻

22. Constraint

A Constraint limits the range of states or actions available to a system.

Examples:

* geography;
* infrastructure;
* staffing;
* budget;
* law;
* logistics;
* time;
* energy;
* communication;
* institutional authority.

Constraints may interact and create bottlenecks.

⸻

23. Bottleneck

A Bottleneck is a component whose limited capacity materially constrains system-level throughput or resilience.

The bottleneck may not be the component with the greatest absolute load.

CEUTIA SHALL therefore distinguish:

most loaded component

from

system-controlling bottleneck

A bottleneck may migrate between subsystems over time.

⸻

24. Threshold

A Threshold is a state boundary beyond which system behaviour changes qualitatively or operationally.

Thresholds may be:

* physical;
* biological;
* organizational;
* social;
* economic;
* informational;
* operational;
* model-derived.

Thresholds SHALL carry uncertainty.

CEUTIA SHALL avoid treating estimated thresholds as exact natural constants unless independently established.

⸻

25. Tipping Point

A TippingPoint represents a transition region in which small additional perturbations may produce disproportionate changes in system behaviour.

It SHALL be distinguished from an ordinary threshold.

A tipping point may involve:

* loss of resilience;
* increasing variance;
* critical slowing down;
* altered correlations;
* positive feedback;
* regime shift.

⸻

26. Feedback

A Feedback represents a causal or hypothesized causal loop in which system outputs influence subsequent system states.

Two primary types:

Positive feedback
Negative feedback

Positive feedback amplifies deviations.

Negative feedback counteracts deviations.

Feedback relationships SHALL specify whether they are:

* empirically established;
* strongly supported;
* plausible;
* hypothetical.

⸻

27. Cascade

A Cascade represents propagation of effects across multiple connected components.

Conceptual structure:

Perturbation
    ↓
Subsystem A
    ↓
Subsystem B
    ↓
Subsystem C
    ↓
System-level effect

A cascade may cross domains.

Example:

geopolitical shock
→ energy price
→ logistics
→ food price
→ household stress
→ health behaviour
→ healthcare demand
→ system pressure

Each arrow is a candidate mechanism unless independently established.

⸻

28. Signal

A Signal is a statistically, temporally or structurally meaningful deviation or emerging pattern that warrants attention.

Signals may arise from:

* trend change;
* acceleration;
* anomaly;
* persistence;
* synchronized changes;
* correlation changes;
* network propagation;
* threshold proximity;
* contradiction;
* source convergence;
* source divergence.

A signal is not automatically an alarm.

⸻

29. Anomaly

An Anomaly represents a deviation from an explicitly defined baseline, expectation or model.

Anomaly detection SHALL specify:

baseline
comparison window
detection method
sensitivity
uncertainty

An anomaly is not necessarily a threat, error or causal event.

Anomaly ≠ Threat
Anomaly ≠ Causality

⸻

30. Alert

An Alert is an operational classification generated when a signal satisfies predefined criteria requiring attention.

Alerts SHALL include:

* trigger;
* evidence;
* confidence;
* severity;
* uncertainty;
* affected domain;
* temporal horizon;
* recommended next analytical action.

An alert MUST preserve its evidentiary basis.

⸻

31. Source

A Source identifies the origin of information.

Sources may include:

* official institutions;
* scientific literature;
* public datasets;
* media;
* organizations;
* sensors;
* APIs;
* expert statements;
* citizen reports;
* aggregated interaction data.

A source is not itself evidence.

Source ≠ Evidence

The same underlying information repeated by multiple outlets does not constitute independent corroboration.

⸻

32. Evidence

Evidence represents information used to support, weaken or distinguish between claims or hypotheses.

Evidence SHALL preserve:

* provenance;
* source;
* acquisition time;
* observation time;
* methodological quality;
* independence;
* uncertainty;
* relevance;
* direction of support;
* possible bias.

Evidence may support or contradict a hypothesis.

⸻

33. Claim

A Claim is a proposition that can be evaluated as true, false, uncertain, disputed or unresolved.

Examples:

Hospital occupancy increased during interval T.
Demand exceeded effective capacity in subsystem X.
Information about event Y propagated unusually rapidly.
Variable A preceded variable B.

Claims SHALL NOT be stored merely as unqualified textual statements.

A claim must have epistemic metadata.

⸻

34. Inference

An Inference is a conclusion derived from observations, evidence, models or previously established claims.

Every inference SHALL identify:

premises
method
assumptions
conclusion
uncertainty

The system must be able to reconstruct why an inference was generated.

⸻

35. Hypothesis

A Hypothesis is a provisional explanatory proposition.

A hypothesis SHALL contain:

* statement;
* mechanism;
* supporting evidence;
* contradicting evidence;
* assumptions;
* competing hypotheses;
* falsification criteria;
* predicted observations;
* confidence;
* uncertainty;
* temporal validity.

CEUTIA SHALL maintain competing hypotheses rather than prematurely selecting a single narrative.

⸻

36. Mechanism

A Mechanism represents a proposed process through which one state or variable affects another.

Example:

A → B

must not be interpreted as causal merely because A precedes B.

Mechanisms require evidence proportional to the strength of the causal claim.

⸻

37. Prediction

A Prediction is a quantitative or probabilistic statement about a future or currently unobserved state.

Predictions SHALL contain:

* target variable/event;
* forecast horizon;
* probability or expected value;
* uncertainty interval where appropriate;
* model;
* timestamp;
* calibration status.

Predictions SHALL later be compared with observed outcomes.

⸻

38. Scenario

A Scenario is a coherent conditional representation of how the system could evolve under specified assumptions.

A scenario is not a probability by itself.

Scenarios may be:

baseline
favourable
adverse
stress
extreme
alternative
counterfactual

Scenario assumptions SHALL be explicit.

⸻

39. Risk

Risk represents the possibility of an adverse outcome under specified conditions.

A conceptual risk representation may combine:

Probability × Consequence × Exposure × Vulnerability

The exact mathematical implementation belongs to the mathematical and intelligence models.

Risk SHALL NOT be assigned solely because a population or category is associated with an event.

⸻

40. Vulnerability

Vulnerability represents susceptibility to harm under specified exposure and system conditions.

It may arise from:

* limited resources;
* reduced adaptive capacity;
* geographic isolation;
* infrastructure dependence;
* social determinants;
* biological susceptibility;
* institutional constraints.

Vulnerability is contextual and dynamic.

⸻

41. Resilience

Resilience represents the capacity of a system to absorb perturbation, maintain essential functions, adapt and recover.

CEUTIA SHALL distinguish:

resistance
adaptation
recovery
transformation

A system that does not fail immediately is not necessarily resilient.

⸻

42. Exposure

Exposure represents contact with an environmental, social, biological, informational, economic or geopolitical factor.

Exposure SHALL include:

* intensity;
* duration;
* frequency;
* timing;
* spatial scope;
* affected population;
* uncertainty.

⸻

43. Intervention

An Intervention is an action intended to modify a system state, trajectory, exposure, risk or outcome.

Interventions SHALL specify:

* target;
* mechanism;
* expected effect;
* unintended-effect hypotheses;
* time horizon;
* constraints;
* reversibility;
* evaluation criteria.

An intervention may itself modify system dynamics.

⸻

44. Outcome

An Outcome is an observed result following an event, process, intervention or trajectory.

Outcomes are used to evaluate:

* predictions;
* hypotheses;
* interventions;
* models;
* assumptions.

The ontology therefore supports continuous learning.

⸻

45. Information

Information is itself a system variable.

CEUTIA SHALL represent information flows because:

Information
    ↓
Perception
    ↓
Behaviour
    ↓
System state
    ↓
New information

Information may therefore modify the system it describes.

This creates a potential feedback loop.

⸻

46. Narrative

A Narrative is a structured interpretation of multiple observations or claims.

Narratives SHALL NOT be treated as evidence merely because they are coherent.

A compelling narrative may be:

* correct;
* incomplete;
* misleading;
* unfalsifiable;
* contradicted by evidence.

CEUTIA SHALL prioritize evidence and mechanisms over narrative coherence.

⸻

47. Contradiction

A Contradiction exists when two or more claims, observations or evidence items cannot simultaneously be accepted under the same assumptions.

Contradictions SHALL be preserved.

The system MUST NOT automatically eliminate conflicting information merely to produce a coherent output.

Contradictions may indicate:

* measurement error;
* temporal difference;
* spatial difference;
* methodological difference;
* source dependence;
* genuine uncertainty;
* model failure;
* regime change.

⸻

48. Uncertainty

Uncertainty represents incomplete knowledge about a value, claim, mechanism, state or prediction.

CEUTIA SHALL distinguish:

measurement uncertainty
model uncertainty
parameter uncertainty
epistemic uncertainty
aleatory uncertainty
source uncertainty
structural uncertainty

Unknown SHALL remain unknown.

The system MUST NOT transform absence of evidence into evidence of absence.

⸻

49. Confidence

Confidence represents the system’s evaluated degree of support for a proposition.

Confidence SHALL NOT be equivalent to:

* truth;
* source count;
* narrative coherence;
* model complexity.

Confidence must depend on the relevant epistemological model.

⸻

50. Provenance

Every important piece of information SHALL have provenance.

Minimum provenance:

origin
source
acquisition method
acquired_at
observed_at
published_at
processed_at
transformation history
analytical method

Derived information SHALL maintain links to its upstream inputs.

CEUTIA must support lineage:

Prediction
    ↓
Model
    ↓
Inference
    ↓
Claims
    ↓
Evidence
    ↓
Observations
    ↓
Sources

⸻

51. Independence

Independence represents the degree to which evidence items provide genuinely independent information.

Ten publications repeating the same official statement are not equivalent to ten independent observations.

CEUTIA SHALL therefore model:

source independence
measurement independence
methodological independence
institutional independence
information lineage

Corroboration SHALL be weighted by independence.

⸻

52. Temporal semantics

Every temporally relevant entity SHALL distinguish, where applicable:

observed_at
occurred_at
published_at
acquired_at
detected_at
inferred_at
valid_from
valid_to
superseded_at

These timestamps MUST NOT be collapsed.

A report published today may describe an event from yesterday.

A model inference generated today may concern a process that began months ago.

⸻

53. Spatial semantics

Every spatially relevant entity SHALL preserve:

location
spatial_resolution
territorial_definition
geographic_uncertainty

The system SHALL distinguish:

where an event occurred
where it was detected
where its effects were observed
where the population affected resides

These may be different locations.

⸻

54. Relationship ontology

Core relationships include:

OBSERVED_BY
MEASURED_BY
LOCATED_IN
PART_OF
CONTAINS
AFFECTS
EXPOSES
EXPOSED_TO
INTERACTS_WITH
DEPENDS_ON
CONSTRAINS
SUPPORTS
CONTRADICTS
DERIVED_FROM
CORROBORATES
SHARES_SOURCE_WITH
CAUSES
MAY_CAUSE
PRECEDES
FOLLOWS
AMPLIFIES
ATTENUATES
PROPAGATES_TO
FEEDS_BACK_TO
TRIGGERS
THRESHOLDS
PREDICTS
INVALIDATES
UPDATES
INTERVENES_ON
RESULTS_IN
RECOVERS_FROM

Causal relationships SHALL be semantically stronger than temporal relationships.

⸻

55. Mandatory semantic distinctions

CEUTIA SHALL enforce the following distinctions.

Observation ≠ Interpretation
Measurement ≠ Meaning
Source ≠ Evidence
Evidence ≠ Claim
Claim ≠ Fact
Hypothesis ≠ Fact
Hypothesis ≠ Prediction
Prediction ≠ Scenario
Scenario ≠ Forecast
Event ≠ Trajectory
Anomaly ≠ Threat
Risk ≠ Person
Suffering ≠ Threat
Migration ≠ Criminality
Population ≠ Homogeneous Actor
Correlation ≠ Causation
Temporal Precedence ≠ Causation
Narrative ≠ Evidence
Capacity ≠ Availability
Capacity ≠ Accessibility
Demand ≠ Flow Rate
Volume ≠ Velocity
Shock ≠ Cause
Signal ≠ Alert
Alert ≠ Emergency
Uncertainty ≠ Ignorance
Absence of Evidence ≠ Evidence of Absence

These are core safety and epistemological constraints.

⸻

56. Dynamic-system representation

A CEUTIA system state may be represented conceptually as:

S(t) =
[
    demand(t),
    capacity(t),
    reserve(t),
    pressure(t),
    population(t),
    flows(t),
    exposures(t),
    information(t),
    behaviour(t),
    health(t),
    infrastructure(t),
    economic_state(t),
    environmental_state(t),
    geopolitical_exposure(t)
]

The actual implementation SHALL use domain-specific state vectors rather than forcing all domains into one undifferentiated vector.

The objective is to represent interactions among state variables while preserving domain semantics.

⸻

57. State transition

A simplified system representation is:

S(t+Δt) = F(S(t), U(t), E(t), N(t), θ) + ε

where:

* S(t) = system state;
* U(t) = endogenous interventions/actions;
* E(t) = exogenous inputs/shocks;
* N(t) = network interactions;
* θ = model parameters;
* ε = uncertainty/unmodelled effects.

The ontology does not prescribe one mathematical model.

It provides the semantic structure required by multiple models.

⸻

58. Multi-scale representation

CEUTIA SHALL support multiple temporal scales:

seconds
minutes
hours
days
weeks
months
years

and multiple spatial scales:

person
household
neighbourhood
district
city
border
region
country
international network

A phenomenon may propagate across scales.

For example:

individual stress
→ household behaviour
→ population behaviour
→ service demand
→ institutional pressure
→ system trajectory

⸻

59. Cross-domain ontology

The same abstract entities may appear across different domains.

Example:

Pressure
├── healthcare pressure
├── economic pressure
├── migration pressure
├── infrastructure pressure
├── information pressure
└── geopolitical pressure

The ontology therefore separates:

abstract semantic type

from

domain-specific implementation

This allows CEUTIA to detect interactions without erasing domain-specific meaning.

⸻

60. Health-system ontology

Health SHALL be represented as a dynamic trajectory rather than a static state.

Relevant entities include:

HealthState
HealthTrajectory
Exposure
AllostaticLoad
HealthcareDemand
HealthcareCapacity
HealthcareAccess
Workload
WaitingTime
TreatmentDelay
PopulationHealth
RecoveryCapacity

The ontology SHALL support interactions among:

biology
behaviour
environment
social conditions
economy
geopolitics
healthcare systems

This does not imply that every association is causal.

⸻

61. Information-system ontology

The information ecosystem SHALL include:

InformationItem
Source
Claim
Narrative
PropagationEvent
Audience
Reach
Velocity
Amplification
Correction
Contradiction
Sentiment
Polarization
Uncertainty

The system SHALL distinguish information about a phenomenon from the phenomenon itself.

A rise in reporting is not necessarily a rise in incidence.

A rise in perceived risk is not necessarily a rise in objective risk.

⸻

62. Geopolitical ontology

Geopolitical phenomena SHALL be represented as networks of actors, relationships, events and exposures rather than isolated headlines.

Core entities:

Actor
Alliance
Conflict
Tension
Policy
Sanction
TradeFlow
EnergyFlow
SupplyChain
MigrationFlow
SecurityEvent
DiplomaticEvent
InformationOperation

A geopolitical event may affect Ceuta indirectly through multiple mechanisms.

The ontology SHALL support:

GeopoliticalEvent
→ Exposure
→ IntermediateVariable
→ LocalSystem
→ Population
→ Outcome

Each link requires appropriate evidentiary status.

⸻

63. Migration ontology

Migration-related data SHALL be represented neutrally.

Relevant variables may include:

arrival_volume
arrival_rate
route
origin
destination
duration
age_distribution
service_demand
housing_demand
healthcare_demand

The ontology MUST NOT encode migration itself as a threat.

Threat classification requires separate evidence concerning a specific phenomenon.

Migration ≠ Threat
Migration ≠ Criminality
Migration ≠ Security Incident

This distinction is mandatory.

⸻

64. Citizen interaction ontology

A citizen interaction is represented separately from system intelligence.

Citizen
    ↓
Interaction
    ↓
Question / Concern / Request
    ↓
Response
    ↓
Optional Feedback

The system may derive aggregate, privacy-preserving signals from interactions only when permitted by governance rules.

Individual suffering SHALL NOT automatically become an intelligence signal about the individual.

The ontology therefore separates:

Citizen wellbeing interaction

from:

System-level intelligence observation

⸻

65. Privacy boundary

The ontology supports explicit data classifications.

Minimum classes:

PUBLIC
SENSITIVE_PUBLIC
RESTRICTED
PRIVATE
HIGHLY_RESTRICTED

The PUBLIC system SHALL only process data authorized for PUBLIC use.

No ontology relationship may be used to circumvent access control.

A semantic relationship does not imply permission to retrieve the linked object.

⸻

66. Public/Owner semantic boundary

PUBLIC and OWNER may share compatible conceptual ontology while maintaining separate data domains.

COMMON SEMANTICS
       │
       ├── PUBLIC DATA DOMAIN
       │
       └── OWNER DATA DOMAIN

The existence of the same entity type in both domains does not imply shared records.

PUBLIC-derived signals may be transmitted to OWNER only through explicitly governed interfaces.

OWNER-private information SHALL never be reconstructed from PUBLIC outputs.

⸻

67. Epistemic lifecycle

Every important proposition should be capable of moving through:

Observed
    ↓
Recorded
    ↓
Validated
    ↓
Corroborated
    ↓
Interpreted
    ↓
Hypothesized
    ↓
Modelled
    ↓
Predicted
    ↓
Evaluated
    ↓
Confirmed / weakened / rejected / unresolved

The ontology SHALL preserve historical epistemic states.

A claim changing status must not erase its previous status.

⸻

68. Versioning and evolution

Entities, claims, hypotheses and models evolve.

CEUTIA SHALL therefore support:

version
created_at
updated_at
supersedes
superseded_by
revision_reason
revision_authority
revision_evidence

A new interpretation must not overwrite the historical record of the previous interpretation.

⸻

69. Epistemic state machine

Claims may transition between states:

UNASSESSED
    ↓
OBSERVED
    ↓
SUPPORTED
    ↓
CORROBORATED
    ↓
HIGH_CONFIDENCE

Alternative paths include:

SUPPORTED → CONTRADICTED
SUPPORTED → WEAKENED
CORROBORATED → REVISED
HIGH_CONFIDENCE → REJECTED
ANY_STATE → UNRESOLVED

No state transition is permanent.

New evidence can update previous assessments.

⸻

70. Bayesian compatibility

The ontology SHALL be compatible with probabilistic belief revision.

For a hypothesis H and evidence E:

P(H | E)
=
P(E | H) P(H)
/
P(E)

CEUTIA does not require every epistemic operation to be Bayesian, but its ontology must preserve the variables necessary for Bayesian updating where appropriate.

Evidence independence and dependence must be represented explicitly because repeated dependent observations can otherwise produce artificial confidence inflation.

⸻

71. Hypothesis competition

Multiple hypotheses SHALL be allowed to explain the same observation.

Example:

Observation:
    healthcare demand increases.
Hypothesis A:
    population increase.
Hypothesis B:
    seasonal effect.
Hypothesis C:
    delayed care accumulation.
Hypothesis D:
    behavioural change.
Hypothesis E:
    measurement artefact.

The system must compare predictions generated by competing hypotheses.

It must not select the most narratively attractive explanation merely because it is coherent.

⸻

72. Causal humility

The ontology SHALL explicitly encode causal status.

Minimum values:

OBSERVATIONAL
TEMPORALLY_ASSOCIATED
MECHANISTICALLY_PLAUSIBLE
CAUSALLY_SUPPORTED
CAUSALLY_ESTABLISHED
UNKNOWN
CONTRADICTED

The strongest causal classification requires evidence appropriate to the domain.

⸻

73. Weak signals

A WeakSignal is an early, low-confidence indication that may become meaningful if persistent, corroborated or structurally connected to other changes.

Weak signals SHALL preserve low confidence rather than being artificially promoted.

However, multiple weak signals may become significant when:

* they are independent;
* they converge;
* they share a plausible mechanism;
* they persist;
* they synchronize;
* they approach a threshold;
* they propagate through the network.

This enables early-warning analysis without equating weak evidence with certainty.

⸻

74. Systemic risk representation

A systemic risk should be represented as a network rather than a single score.

Conceptually:

Risk
├── Exposure
├── Vulnerability
├── Hazard
├── Capacity
├── Reserve
├── Coupling
├── Propagation
├── Feedback
├── Threshold
├── Recovery
└── Uncertainty

A risk score without its components SHALL be considered insufficient for high-consequence interpretation.

⸻

75. Cascading-risk representation

CEUTIA SHALL support chains such as:

Shock
  ↓
Pressure
  ↓
Capacity depletion
  ↓
Bottleneck
  ↓
Service degradation
  ↓
Behavioural response
  ↓
Additional demand
  ↓
Feedback
  ↓
Threshold
  ↓
Cascade

The chain represents a model, not automatically an established fact.

Each relationship must carry epistemic status.

⸻

76. Recovery ontology

Recovery SHALL be represented explicitly.

Relevant variables:

recovery_time
recovery_rate
residual_damage
adaptive_capacity
resource_replenishment
workforce_recovery
demand_normalization
institutional_learning

Two systems with identical peak stress may have radically different outcomes because their recovery dynamics differ.

Therefore:

Peak load alone ≠ systemic resilience

⸻

77. Learning from reality

CEUTIA SHALL maintain a closed analytical loop:

Observe
   ↓
Model
   ↓
Hypothesize
   ↓
Predict
   ↓
Observe outcome
   ↓
Compare
   ↓
Calibrate
   ↓
Update model

Predictions that fail SHALL remain in the historical record.

Model performance must not be evaluated only from successful predictions.

⸻

78. Anti-hallucination semantic rules

CEUTIA-generated outputs SHALL NOT:

1. convert hypotheses into facts;
2. infer causality from temporal order alone;
3. infer threat from population category;
4. infer incidence from media volume alone;
5. infer certainty from source count alone;
6. discard contradictory evidence without recording why;
7. conceal uncertainty;
8. fabricate missing measurements;
9. imply access to data that was not actually accessed;
10. present model outputs as direct observations;
11. confuse scenario analysis with prediction;
12. confuse prediction with certainty;
13. treat correlation as causal proof;
14. erase historical revisions.

⸻

79. Semantic integrity rules

Every derived proposition SHOULD be traceable to:

source
→ observation
→ evidence
→ claim
→ inference
→ hypothesis/model
→ output

Every high-consequence output SHALL expose sufficient provenance for independent review.

Every uncertainty-sensitive output SHALL retain uncertainty metadata.

Every causal statement SHALL retain causal-status metadata.

⸻

80. Ontological invariants

The following invariants are mandatory.

Invariant 1

A Person cannot become a Threat solely through demographic classification.

Invariant 2

A Source cannot become Evidence without an information object derived from that source.

Invariant 3

A Claim cannot become Fact solely because confidence exceeds an arbitrary threshold.

Invariant 4

A Hypothesis cannot become established solely because no competing hypothesis currently exists.

Invariant 5

A Prediction must remain distinguishable from an observed outcome.

Invariant 6

A Scenario must remain distinguishable from a probability forecast.

Invariant 7

A Correlation cannot automatically create a CAUSES relationship.

Invariant 8

A Signal cannot automatically create an Alert.

Invariant 9

An Alert cannot automatically create an assertion of imminent harm.

Invariant 10

A DataPoint without temporal context cannot be treated as a trajectory.

Invariant 11

A theoretical capacity cannot automatically be treated as operational capacity.

Invariant 12

Repeated dependent sources cannot be counted as independent corroboration.

Invariant 13

Unknown values must remain explicitly unknown.

Invariant 14

Historical epistemic states cannot be silently overwritten.

Invariant 15

PUBLIC semantic outputs cannot be used to infer access to OWNER-private records.

⸻

81. Minimal canonical object model

A canonical CEUTIA object SHOULD be conceptually representable as:

Object
├── id
├── type
├── domain
├── status
├── created_at
├── updated_at
├── valid_from
├── valid_to
├── observed_at
├── spatial_scope
├── provenance
├── epistemic_status
├── uncertainty
├── confidence
├── relationships
├── version
└── access_classification

Not every entity requires every field, but every implementation SHALL preserve the semantics necessary for temporal, spatial, epistemic and security analysis.

⸻

82. Ontology and mathematical layer

The ontology defines meaning.

The mathematical layer defines operations over that meaning.

Therefore:

Ontology
    ↓
Semantic representation
    ↓
Mathematical representation
    ↓
Dynamic models
    ↓
Inference
    ↓
Prediction

Mathematics must not redefine semantics implicitly.

For example, if capacity means effective deployable capacity, a mathematical model cannot silently substitute nominal capacity without explicitly declaring the transformation.

⸻

83. Ontology and intelligence layer

The intelligence layer consumes semantically validated objects.

Its outputs may include:

Signal
Alert
Risk assessment
Hypothesis ranking
Trajectory assessment
Scenario
Prediction
Counterfactual
Systemic explanation
Decision support

Each output must retain provenance and epistemic status.

⸻

84. Ontology and citizen layer

The citizen-facing layer consumes a restricted semantic subset.

It may use:

public evidence
general health information
prevention information
system status
validated resources
non-diagnostic guidance

It must not expose:

private intelligence
restricted sources
individual intelligence assessments
sensitive operational information
OWNER-only data

Citizen-facing communication must distinguish:

what is known
what is uncertain
what is being monitored
what the citizen can reasonably do
when human/professional support is appropriate

⸻

85. Ontology as machine-readable foundation

This ontology SHALL eventually be expressible through machine-readable schemas.

Potential implementation layers include:

JSON Schema
Pydantic models
SQLAlchemy models
Graph representations
Knowledge graph relations
Event schemas
Vector/document metadata

The implementation technology must not alter the semantic definitions established here.

⸻

86. Canonical semantic graph

At the highest level, CEUTIA can be represented as:

                ┌──────────────┐
                │    SOURCE    │
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │ OBSERVATION  │
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │   EVIDENCE   │
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │    CLAIM     │
                └──────┬───────┘
                       ↓
              ┌──────────────────┐
              │     INFERENCE    │
              └────────┬─────────┘
                       ↓
              ┌──────────────────┐
              │    HYPOTHESIS    │
              └────────┬─────────┘
                       ↓
              ┌──────────────────┐
              │      MODEL       │
              └────────┬─────────┘
                       ↓
        ┌──────────────────────────────┐
        │ PREDICTION / SCENARIO / RISK │
        └──────────────┬───────────────┘
                       ↓
                  OBSERVED OUTCOME
                       ↓
                  MODEL EVALUATION
                       ↓
                    REVISION

Around this epistemic graph exists the dynamic system:

        PEOPLE
           │
           ▼
       POPULATIONS
           │
           ▼
       SUBSYSTEMS
           │
           ▼
         SYSTEM
      ↙    ↓     ↘
   FLOWS  STATES  EXPOSURES
      ↘    ↓     ↙
       INTERACTIONS
           ↓
       FEEDBACK
           ↓
       TRAJECTORY
           ↓
       THRESHOLDS
           ↓
        CASCADE
           ↓
        OUTCOME

The two graphs interact continuously.

Reality changes the evidence.

Evidence changes the model.

The model changes the interpretation.

Interpretation can change behaviour.

Behaviour changes the system.

The resulting system produces new observations.

This closed loop is fundamental to CEUTIA.

⸻

87. Final ontological principle

CEUTIA is not designed to answer only:

“What happened?”

It is designed to represent:

What is happening, how fast it is changing, where it is changing, what preceded it, what may be interacting with it, what evidence supports each interpretation, what remains unknown, what competing explanations exist, how resilient the affected system is, what may happen next, and how well previous predictions corresponded with reality.

The ontology therefore treats intelligence as a continuously revised representation of a changing system.

Its purpose is not to manufacture certainty.

Its purpose is to make uncertainty structured, observable, comparable and progressively reducible where reality permits.

The governing semantic principle is:

Observe without prematurely interpreting.
Interpret without confusing interpretation with fact.
Hypothesize without abandoning alternatives.
Predict without pretending certainty.
Act without forgetting feedback.
Learn from what actually happens.

