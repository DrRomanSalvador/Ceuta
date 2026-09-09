# CEUTIA — PRINCIPIO ARQUITECTÓNICO SUPERIOR

## 0. Arquitectura dinámica por responsabilidades

CeutIA se construye como un sistema de capas con responsabilidades separadas.

La arquitectura no debe entenderse como una cadena lineal de simples filtros, sino como un sistema de transformación controlada del conocimiento:

    DATOS
       ↓
    ESTADO
       ↓
    MÉTRICAS
       ↓
    MODELOS DINÁMICOS
       ↓
    HIPÓTESIS / PREDICCIONES / ESCENARIOS
       ↓
    VALIDACIÓN ADVERSARIAL
       ↓
    SEÑAL CUALIFICADA
       ↓
    INFORMATION BOUNDARY
       ↓
    SALIDA AUTORIZADA

Cada capa debe poder determinar:

1. qué recibe;
2. qué transforma;
3. qué produce;
4. qué incertidumbre conserva;
5. qué información no puede producir;
6. qué capa tiene autoridad para utilizar su salida.

## 0.1. `metrics.py` — matemática

`metrics.py` constituye la capa matemática fundamental.

Su responsabilidad es calcular métricas, índices, funciones y primitivas matemáticas formalmente definidas.

No debe decidir qué significa una métrica en un contexto estratégico concreto.

No debe convertir automáticamente una métrica en una alerta.

No debe realizar decisiones de seguridad.

Principio:

    MÉTRICA = transformación matemática definida

## 0.2. `models.py` — integración dinámica

`models.py` integra las métricas en modelos de estado y evolución.

Debe representar:

- estado;
- trayectoria;
- carga;
- reserva;
- capacidad;
- sensibilidad;
- perturbaciones;
- acoplamiento;
- propagación;
- cascadas;
- recuperación;
- resiliencia;
- territorio;
- dimensión temporal;
- información;
- señales agregadas de tensión social;
- hipótesis;
- predicciones;
- escenarios;
- incertidumbre.

Principio:

    MODELO = estructura de interacción y evolución

No deberá confundirse modelo con verdad.

## 0.3. `adversarial_validation.py` — intento de refutación

La validación adversarial intenta encontrar razones por las que una conclusión, señal o modelo podría estar equivocado.

Debe comprobar, cuando corresponda:

- procedencia;
- independencia;
- corroboración;
- contradicciones;
- leakage;
- deriva;
- estabilidad temporal;
- estabilidad espacial;
- robustez;
- sensibilidad;
- dependencia de umbral;
- dependencia del denominador;
- dependencia del modelo;
- dependencia del prior;
- confusión causal;
- selección;
- eventos raros;
- retroalimentación;
- contaminación por intervención;
- escenarios extremos;
- hipótesis competidoras;
- falsabilidad;
- seguridad;
- privacidad;
- automatización indebida.

Principio:

    VALIDACIÓN = intento sistemático de encontrar por qué el resultado podría fallar

La supervivencia de una prueba adversarial no convierte automáticamente una conclusión en verdadera.

## 0.4. `information_boundary.py` — control de circulación

`information_boundary.py` controla qué información puede cruzar las fronteras PUBLIC, INTERNAL, OWNER y RESTRICTED.

PUBLIC no debe poder leer directamente inteligencia interna, privada o restringida. La información interna no puede convertirse en información pública mediante serialización implícita. Las degradaciones de clasificación requieren autorización explícita y las transformaciones que crucen fronteras deben ser auditables. metrics.py

El límite actual ya establece, entre otras invariantes, que el riesgo individual y la inteligencia estratégica no constituyen salidas públicas directas y que una salida pública requiere comprobaciones explícitas de privacidad, seguridad, epistemología y reidentificación. metrics.py

Principio:

    INFORMATION BOUNDARY = control de qué conocimiento puede llegar a qué actor

## 0.5. `security/` — seguridad técnica

La capa `security/` protege la infraestructura y sus recursos.

Debe mantenerse diferenciada de:

- epistemología;
- modelización;
- validación científica;
- clasificación de información;
- interpretación estratégica.

Seguridad técnica y seguridad epistemológica son complementarias, pero no equivalentes.

## 0.6. Separación PUBLIC / PRIVATE

PUBLIC y PRIVATE no son simplemente dos interfaces del mismo conjunto de datos.

Son dominios con diferentes permisos, información disponible y reglas de salida.

La inteligencia privada puede utilizar información que no puede exponerse públicamente.

La salida pública debe ser una transformación explícitamente autorizada, no una copia de la inteligencia interna.

## 0.7. Separación entre persona y sistema

La arquitectura podrá recibir información procedente de interacciones individuales, pero deberá distinguir:

    persona
    ↓
    interacción individual
    ↓
    señal de bienestar / necesidad
    ↓
    agregación o análisis poblacional legítimo
    ↓
    señal sistémica

No se utilizará una interacción individual como mecanismo encubierto de vigilancia.

La información individual de bienestar y la inteligencia territorial deberán mantener fronteras explícitas.

## 0.8. Seguridad operacional

CeutIA puede generar una señal cualificada que requiera revisión humana.

La cadena correcta será:

    CeutIA
       ↓
    señal
       ↓
    validación
       ↓
    interpretación humana
       ↓
    autoridad competente

CeutIA no ejecutará autónomamente acciones coercitivas, policiales o de seguridad sobre personas.

## 0.9. Regla de no contradicción arquitectónica

Todo nuevo módulo deberá ser compatible con:

- la ontología de CeutIA;
- el modelo dinámico;
- la política de evidencia;
- la validación adversarial;
- la separación PUBLIC/PRIVATE;
- la seguridad técnica;
- la protección de datos;
- la supervisión humana.

Cuando una nueva funcionalidad contradiga una invariante existente, deberá detenerse su integración hasta resolver explícitamente la contradicción.

La arquitectura debe crecer por integración coherente, no por acumulación de funcionalidades.

## 0.10. Principio de mínima complejidad suficiente

CeutIA no debe multiplicar módulos cuando una responsabilidad puede pertenecer legítimamente a un componente existente.

La complejidad debe residir principalmente en los modelos y estructuras internas, no en una proliferación innecesaria de archivos y capas.

Cada nuevo módulo requiere una justificación arquitectónica independiente.

## 0.11. Principio final

La arquitectura de CeutIA debe permitir que el sistema diga:

    esto se observa;
    esto se deriva;
    esto se interpreta;
    esto se plantea como hipótesis;
    esto se predice;
    esto constituye un escenario;
    esto es incierto;
    esto contradice otra evidencia;
    esto no ha sido validado;
    esto requiere revisión humana;
    esto no puede salir de PRIVATE.

La capacidad de distinguir estas categorías es una propiedad fundamental del sistema, no una característica secundaria de presentación.

# CEUTIA — SYSTEM ARCHITECTURE
Version: 1.0
Status: Normative architecture
Scope: CEUTIA PUBLIC
Path: `docs/SYSTEM_ARCHITECTURE.md`
---
## 1. Purpose
CEUTIA is an intelligence, knowledge and dynamic-systems platform designed to transform heterogeneous observations about Ceuta into an auditable representation of system state, trajectory, interactions, risks, hypotheses, scenarios, signals and calibrated predictions.
CEUTIA is not primarily a dashboard.
A dashboard displays information.
CEUTIA constructs and continuously updates a model of a complex socio-environmental system.
The architectural objective is therefore not merely to collect data or produce visualizations, but to establish a computational chain:
```text
WORLD
  ↓
OBSERVATIONS
  ↓
DATA
  ↓
EVIDENCE
  ↓
CLAIMS
  ↓
SYSTEM STATE
  ↓
TRAJECTORIES
  ↓
RELATIONSHIPS
  ↓
SIGNALS
  ↓
HYPOTHESES
  ↓
SCENARIOS
  ↓
PREDICTIONS
  ↓
DECISION-SUPPORT SIGNALS
  ↓
HUMAN INTERPRETATION / ACTION
  ↓
OUTCOME
  ↓
CALIBRATION
  ↓
MODEL REVISION

The system must preserve the distinction between every layer.

An observation is not a conclusion.

A correlation is not a causal mechanism.

A hypothesis is not a fact.

A scenario is not a prediction.

A prediction is not a certainty.

An anomaly is not automatically a threat.

Human suffering is not equivalent to systemic threat.

Migration is not equivalent to criminality.

⸻

2. Architectural principles

2.1 Dynamic-system principle

CEUTIA represents the territory as a dynamic system whose state changes over time.

For a system state:

[
X_t =
[x_1(t),x_2(t),…,x_n(t)]
]

the relevant object is not only:

[
X_t
]

but:

[
\frac{dX}{dt}
]

and, where meaningful:

[
\frac{d^2X}{dt^2}
]

The architecture must therefore support:

* absolute levels;
* rates of change;
* acceleration or deceleration;
* persistence;
* volatility;
* accumulated exposure;
* recovery;
* capacity;
* pressure;
* interactions;
* feedback;
* thresholds;
* shocks;
* propagation;
* cascades.

A single observation may be low-information.

A trajectory can be highly informative.

⸻

2.2 Temporal principle

Every relevant object must have temporal semantics.

At minimum:

observed_at
published_at
valid_from
valid_to
detected_at
ingested_at
inferred_at
superseded_at

CEUTIA must never silently treat information published today as if it described today’s state.

The system must distinguish:

time of event
time of observation
time of publication
time of ingestion
time of inference
time of prediction

This distinction is fundamental to retrospective validation.

⸻

2.3 Epistemic principle

Every substantive proposition must carry information describing:

* provenance;
* source;
* source type;
* independence;
* observation/evidence status;
* confidence;
* uncertainty;
* temporal validity;
* corroboration;
* contradiction;
* inference level;
* model version.

The architecture must permit a proposition to remain unresolved.

Uncertainty is data.

Contradiction is data.

Absence of evidence is not automatically evidence of absence.

⸻

3. High-level architecture

CEUTIA PUBLIC is divided into logical planes.

┌─────────────────────────────────────────────────────────────┐
│                     CEUTIA PUBLIC                           │
├─────────────────────────────────────────────────────────────┤
│  CITIZEN / PUBLIC INTERACTION PLANE                         │
│  Information · Prevention · Wellbeing · De-escalation       │
├─────────────────────────────────────────────────────────────┤
│  PRESENTATION / API PLANE                                   │
│  Dashboards · Maps · Timelines · Reports · APIs             │
├─────────────────────────────────────────────────────────────┤
│  INTELLIGENCE PLANE                                         │
│  Signals · Alerts · Hypotheses · Scenarios · Predictions    │
├─────────────────────────────────────────────────────────────┤
│  DYNAMIC SYSTEMS PLANE                                      │
│  State · Trajectory · Capacity · Pressure · Networks        │
├─────────────────────────────────────────────────────────────┤
│  EPISTEMIC / KNOWLEDGE PLANE                                │
│  Claims · Evidence · Provenance · Contradictions            │
├─────────────────────────────────────────────────────────────┤
│  DATA / TEMPORAL / SPATIAL PLANE                            │
│  Raw · Normalized · Time-series · Spatial · Graph           │
├─────────────────────────────────────────────────────────────┤
│  INGESTION / OBSERVATION PLANE                              │
│  Sources · Connectors · Acquisition · Validation            │
├─────────────────────────────────────────────────────────────┤
│  GOVERNANCE / SECURITY / AUDIT PLANE                        │
│  Identity · Permissions · Privacy · Audit · Safety          │
└─────────────────────────────────────────────────────────────┘

The planes are logically separated even where they may later share physical infrastructure.

⸻

4. Architectural domains

4.1 Observation domain

Responsible for representing what has been observed.

Examples:

* official statistics;
* meteorological observations;
* epidemiological observations;
* hospital activity;
* transport activity;
* energy data;
* economic indicators;
* demographic data;
* environmental measurements;
* public communications;
* verified reports;
* geospatial observations.

The observation layer must not contain conclusions disguised as observations.

⸻

4.2 Data domain

Transforms observations into normalized machine-readable data.

Responsibilities:

* schema normalization;
* units;
* timestamps;
* geographic normalization;
* missing-value handling;
* quality checks;
* deduplication;
* versioning;
* lineage.

⸻

4.3 Knowledge domain

Transforms data and evidence into explicit knowledge objects.

Core objects:

Source
Observation
Measurement
Evidence
Claim
Inference
Hypothesis
Mechanism
Variable
Relationship

Knowledge must remain traceable to its underlying evidence.

⸻

4.4 Dynamic-system domain

Represents the evolving state of Ceuta.

Core concepts:

State
Trajectory
Flow
Stock
Capacity
Effective Capacity
Accessible Capacity
Pressure
Load
Reserve
Shock
Constraint
Threshold
Feedback
Cascade
Recovery
Adaptation

The same variable may have different interpretations depending on system state.

For example:

[
Demand = 1000
]

is insufficient information.

The system must additionally ask:

* over what period?
* concentrated where?
* against what capacity?
* with what reserve?
* with what baseline?
* with what trend?
* with what competing demand?
* with what recovery time?

⸻

5. Intelligence domain

The intelligence plane converts system representations into decision-relevant signals.

Its main components are:

Signal Engine
Alert Engine
Hypothesis Engine
Scenario Engine
Prediction Engine
Causal Analysis Engine
Risk Aggregator
Calibration Engine

These components must remain logically independent.

An alert must not automatically become a hypothesis.

A hypothesis must not automatically become a prediction.

A prediction must not automatically become an alert.

⸻

6. Signal Engine

The Signal Engine detects meaningful changes in system behaviour.

Signals may originate from:

Level anomalies

[
x_t \not\approx baseline
]

Rate anomalies

[
\Delta x_t
]

Acceleration anomalies

[
\Delta^2 x_t
]

Persistence

A deviation continues beyond an expected duration.

Correlation changes

[
Corr(X,Y)_t
]

changes materially relative to historical behaviour.

Synchronization changes

Previously independent variables begin changing together.

Network changes

Connectivity, centrality, propagation or clustering changes.

Capacity-pressure divergence

[
Pressure_t > Capacity_t
]

or:

[
\frac{Demand_t}{EffectiveCapacity_t}
]

moves toward a critical region.

Recovery deterioration

The system takes progressively longer to return toward baseline after perturbation.

⸻

7. Alert Engine

Alerts represent operationally relevant signals.

A signal does not automatically constitute an alert.

A simplified alert function can be represented as:

[
A =
f(S,
M,
P,
C,
U,
T)
]

where:

* (S) = signal strength;
* (M) = persistence;
* (P) = potential impact;
* (C) = corroboration;
* (U) = uncertainty;
* (T) = threshold proximity.

Alerts must include an explanation of why they were generated.

Example:

ALERT
────────────────────────
Domain: Health
Signal: Emergency demand acceleration
Persistence: 14 h
Capacity ratio: 0.87
Trend: increasing
Corroboration: 3 independent sources
Confidence: 0.81
Uncertainty: moderate
Threshold proximity: elevated
Primary hypothesis: H03
Alternative hypotheses: H07, H11
Expected next observation: within 6–12 h

No alert should be presented as certainty about future events.

⸻

8. Hypothesis Engine

The Hypothesis Engine generates and evaluates competing explanations.

For an observation (E):

[
H_1,H_2,…,H_n
]

must be considered where appropriate.

The system should avoid:

Observation → single explanation

and instead support:

Observation
    ↓
Candidate explanations
    ↓
Evidence comparison
    ↓
Bayesian / probabilistic updating
    ↓
Competing hypotheses
    ↓
Disconfirming evidence search
    ↓
Posterior assessment

A conceptual Bayesian update is:

[
P(H|E)

\frac{P(E|H)P(H)}
{P(E)}
]

The system must retain:

* prior;
* evidence;
* likelihood assumptions;
* posterior;
* uncertainty;
* competing hypotheses;
* evidence against the hypothesis;
* model version.

The hypothesis engine must actively search for disconfirming evidence.

⸻

9. Scenario Engine

Scenarios describe possible future trajectories under explicit assumptions.

A scenario is not a forecast.

Example:

Scenario S1:
Demand continues increasing
+
capacity remains constant
+
recovery time increases
→ progressive saturation

versus:

Scenario S2:
Demand continues increasing
+
temporary capacity increase
+
pressure redistributes
→ delayed threshold crossing

versus:

Scenario S3:
External shock
+
simultaneous subsystem stress
+
reduced reserve
→ nonlinear cascade

Each scenario must contain:

* assumptions;
* initial state;
* drivers;
* affected variables;
* mechanisms;
* uncertainties;
* expected trajectory;
* threshold conditions;
* potential outcomes;
* disconfirming observations.

⸻

10. Prediction Engine

Predictions must be explicit, probabilistic and time-bounded whenever possible.

Example:

Prediction:
Probability of threshold crossing within 72 h = 0.34
Prediction horizon:
72 h
Reference time:
T0
Conditions:
Current trajectory persists
Confidence:
Moderate
Main uncertainty:
Recovery capacity estimate
Alternative trajectory:
Capacity increase ≥ X

Predictions must be stored.

When reality subsequently becomes observable, the prediction must be scored.

This enables:

[
Prediction \rightarrow Outcome \rightarrow Calibration
]

Without this loop, CEUTIA cannot objectively determine whether its predictive machinery improves.

⸻

11. Calibration Engine

The Calibration Engine evaluates whether predicted probabilities correspond to observed frequencies.

For predictions with probability (p), the system should evaluate:

[
ObservedFrequency(p) \approx p
]

It must support metrics such as:

* Brier score;
* log loss;
* calibration curves;
* reliability diagrams;
* discrimination metrics where appropriate;
* false-positive rate;
* false-negative rate;
* lead time;
* detection latency;
* alert fatigue;
* prediction stability.

The objective is not to maximize the number of predictions.

The objective is to improve calibrated predictive performance.

⸻

12. Dynamic state model

CEUTIA should maintain a continuously updated system state.

Conceptually:

[
X_{t+1}

F(X_t,U_t,E_t,\epsilon_t)
]

where:

* (X_t) = current system state;
* (U_t) = interventions/actions;
* (E_t) = exogenous inputs;
* (\epsilon_t) = unexplained variation.

The system should represent both observed and estimated state.

For every estimated variable:

value
estimate_type
uncertainty
confidence
timestamp
model_version
source_dependencies

⸻

13. Capacity architecture

Capacity must never be represented as a single scalar when the system requires multidimensional capacity.

At minimum:

[
C_{global}
\neq
C_{effective}
\neq
C_{accessible}
]

Possible dimensions:

physical capacity
human capacity
financial capacity
logistical capacity
geographical capacity
temporal capacity
institutional capacity
clinical capacity
communication capacity
recovery capacity

Effective capacity may be represented conceptually as:

[
C_{effective}

C_{nominal}
\cdot
A
\cdot
R
\cdot
Q
]

where:

* (A) = availability;
* (R) = operational reserve;
* (Q) = quality/functionality factor.

The actual implementation must use domain-specific definitions rather than assuming this equation is universally valid.

⸻

14. Pressure architecture

Pressure is contextual.

A basic representation is:

[
P_t =
\frac{Demand_t}{EffectiveCapacity_t}
]

but CEUTIA must support more sophisticated formulations incorporating:

* temporal concentration;
* spatial concentration;
* competing demand;
* severity;
* duration;
* recovery time;
* coupling between subsystems.

Therefore:

[
P_t \neq f(Demand_t)
]

alone.

⸻

15. Shock architecture

External shocks must be represented explicitly.

A shock object should contain:

shock_id
start_time
duration
magnitude
affected_subsystems
geographic_scope
expected_origin
observed_origin
propagation_path
uncertainty
recovery_trajectory

A shock may be:

* environmental;
* epidemiological;
* economic;
* logistical;
* geopolitical;
* demographic;
* infrastructural;
* informational;
* technological;
* social.

The system must distinguish:

shock
response
consequence
secondary consequence
feedback

⸻

16. Network architecture

Complex phenomena cannot always be represented as independent variables.

CEUTIA therefore requires graph representations.

Nodes may represent:

territories
institutions
infrastructures
populations
events
resources
systems
subsystems
actors
information sources
transport routes
supply chains

Edges may represent:

dependency
flow
communication
trade
transport
causal hypothesis
correlation
exposure
competition
cooperation
propagation

Each edge must have an explicit semantic type.

A correlation edge must never be represented as causal merely because the graph contains a connection.

⸻

17. Cascading failure architecture

The system must support nonlinear propagation.

Conceptually:

Shock
 ↓
Subsystem A stressed
 ↓
Reserve decreases
 ↓
Subsystem B receives additional load
 ↓
Capacity falls
 ↓
Pressure increases
 ↓
Feedback amplification
 ↓
Threshold crossing
 ↓
Cascade

The architecture must detect the possibility that:

[
Impact_{system}

\sum Impact_{individual\ shocks}
]

because interactions may generate emergent effects.

⸻

18. Weak-signal architecture

Weak signals should not be discarded because they are individually small.

A weak signal becomes potentially important when combined with:

* persistence;
* acceleration;
* independent corroboration;
* spatial spread;
* cross-domain convergence;
* network propagation;
* proximity to a threshold.

CEUTIA should therefore support:

weak signal
+
weak signal
+
weak signal
→
convergent pattern

without prematurely converting convergence into certainty.

⸻

19. Contradiction architecture

Contradictions must remain visible.

If:

Source A → Claim X
Source B → Claim not-X

the system must not simply overwrite one with the other.

It should create:

Contradiction C1
├── Claim A
├── Claim B
├── source independence
├── temporal compatibility
├── methodological differences
├── confidence
└── unresolved status

Contradiction resolution should occur only when evidence justifies it.

⸻

20. Provenance architecture

Every consequential output must be traceable backwards.

The minimum provenance chain is:

Output
 ↓
Model / algorithm
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

A user should be able to ask:

Why does CEUTIA believe this?

and receive an auditable chain rather than a generated explanation disconnected from the actual computation.

⸻

21. PUBLIC / OWNER separation

The PUBLIC and OWNER architectures are separate security domains.

                    ┌────────────────────┐
                    │   PUBLIC DOMAIN    │
                    └─────────┬──────────┘
                              │
                   qualified signals only
                              │
                              ▼
                    ┌────────────────────┐
                    │   OWNER GATEWAY    │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │   OWNER DOMAIN     │
                    └────────────────────┘

PUBLIC must never obtain unrestricted access to OWNER data.

OWNER must not be reconstructed from PUBLIC outputs through accidental leakage.

The boundary must enforce:

* authentication;
* authorization;
* data classification;
* minimization;
* output filtering;
* audit;
* rate limits;
* schema validation;
* explicit transmission contracts.

⸻

22. PUBLIC intelligence boundary

PUBLIC may perform sophisticated analysis.

The fact that the data are public does not imply that every inference should be public.

The system must distinguish:

publicly observable data
        ↓
public analytical representation
        ↓
public signal
        ↓
restricted intelligence signal

A signal may be generated publicly while a deeper interpretation remains restricted.

⸻

23. Citizen interaction plane

The citizen interface is architecturally separate from the intelligence engine.

It may provide:

* contextual information;
* prevention;
* health promotion;
* evidence-informed wellbeing resources;
* crisis/de-escalation information;
* curated educational material;
* explanations of uncertainty;
* links to appropriate professional or institutional resources.

It must not automatically:

* diagnose;
* prescribe;
* determine criminality;
* classify a person as a threat;
* infer malicious intent from distress;
* convert personal suffering into an intelligence signal.

⸻

24. Person-level / system-level separation

The architecture must distinguish:

PERSON

from:

SYSTEM SENSOR

A citizen interaction is not automatically an observation of territorial threat.

A person expressing fear is not evidence that an external threat exists.

A large number of similar interactions may, under controlled privacy-preserving aggregation, constitute an aggregate social signal.

The transformation must be explicit:

individual interactions
        ↓
privacy-preserving aggregation
        ↓
aggregate indicator
        ↓
uncertainty assessment
        ↓
possible system signal

⸻

25. De-escalation architecture

The citizen layer should support stabilization rather than amplification.

The system must avoid feedback loops such as:

uncertainty
 ↓
alarmist output
 ↓
fear
 ↓
behavioural change
 ↓
more incidents
 ↓
more alarmist output

A safer architecture is:

uncertainty
 ↓
context
 ↓
proportionate information
 ↓
available options
 ↓
individual agency
 ↓
reduced unnecessary escalation

De-escalation must never depend on deception or manipulation.

⸻

26. Information as a system variable

Information is not external to the system.

It can alter:

[
Perception
\rightarrow
Behaviour
\rightarrow
System
\rightarrow
NewInformation
]

Therefore CEUTIA must model informational feedback.

This is particularly important for:

* misinformation;
* disinformation;
* rumours;
* perceived insecurity;
* panic;
* polarization;
* institutional communication;
* media amplification.

An increase in reported incidents may reflect:

1. increase in actual incidents;
2. increase in observation;
3. increase in reporting;
4. increase in media attention;
5. increase in vigilance;
6. changes in measurement methodology;
7. some combination.

CEUTIA must preserve these competing explanations.

⸻

27. Multi-domain architecture

The system should not isolate domains unnecessarily.

Relevant domains may include:

health
epidemiology
environment
climate
water
energy
food
economy
employment
housing
migration
mobility
transport
education
social cohesion
public safety
infrastructure
digital environment
geopolitics
logistics
institutional capacity

The analytical layer must allow cross-domain interactions.

For example:

geopolitical instability
 ↓
energy price
 ↓
food price
 ↓
household stress
 ↓
nutrition / sleep / mental wellbeing
 ↓
health demand
 ↓
health-system pressure

This is a hypothesis chain until empirically supported.

⸻

28. Geopolitical architecture

Geopolitical events must be represented as external drivers and network structures.

A geopolitical event can influence Ceuta through:

trade
energy
food
migration
logistics
tourism
financial conditions
information environment
security posture
social stress
institutional demand

CEUTIA should model indirect pathways rather than requiring geographical proximity.

A conflict occurring far from Ceuta may still alter local system state.

The system must distinguish:

geopolitical fact
geopolitical interpretation
causal hypothesis
predicted local effect
observed local effect

⸻

29. Health architecture

Health is represented longitudinally.

The core representation is:

[
Health_t = f(B_t,H_t,E_t,S_t,C_t,…)
]

where domains may include:

* biological;
* behavioural;
* environmental;
* social;
* economic;
* clinical;
* institutional.

The system should prioritize trajectories over isolated measurements.

Relevant concepts include:

baseline
trajectory
rate of change
cumulative exposure
allostatic load
reserve
recovery
threshold
demand
capacity
delay

The architecture must not reduce health to a single score.

⸻

30. Food and resource security

Food insecurity should be represented as a dynamic system.

Potential variables include:

availability
access
price
supply-chain reliability
dependency
household purchasing power
distribution capacity
storage
import exposure
shock sensitivity

The system should distinguish:

food exists

from:

food is accessible

and:

food is affordable

and:

food distribution remains operational

These are different states.

⸻

31. War-risk architecture

CEUTIA must not claim that a war will occur simply because risk indicators rise.

Instead:

observations
 ↓
risk factors
 ↓
competing hypotheses
 ↓
scenario trajectories
 ↓
probabilistic assessment
 ↓
prediction
 ↓
calibration

Potential precursor classes may include:

* military posture;
* diplomatic deterioration;
* economic measures;
* supply-chain disruption;
* cyber incidents;
* information operations;
* mobilization indicators;
* infrastructure stress;
* alliance changes.

Each must have provenance and uncertainty.

A war prediction requires substantially stronger evidence than an anomaly detection signal.

⸻

32. Disease-risk architecture

Disease emergence or outbreak risk may be represented as:

[
R_{disease}

f(
exposure,
susceptibility,
transmission,
mobility,
environment,
health\ capacity,
detection
)
]

The architecture should detect changes in:

* incidence;
* syndromic signals;
* laboratory signals;
* environmental conditions;
* mobility;
* healthcare demand;
* unusual clusters.

Detection must not automatically equal diagnosis.

⸻

33. Hunger-risk architecture

A potential food crisis may emerge from interaction among:

[
Supply
\times
Access
\times
Price
\times
Distribution
\times
Resilience
]

The system should therefore monitor trajectories and interactions rather than waiting for a formal crisis declaration.

⸻

34. Cross-domain early-warning matrix

CEUTIA should maintain a matrix similar to:

                 HEALTH ENV FOOD ECON MIGRATION ENERGY GEO
HEALTH             ·     X    X    X      X        X     X
ENVIRONMENT        X     ·    X    X      X        X     X
FOOD               X     X    ·    X      X        X     X
ECONOMY            X     X    X    ·      X        X     X
MIGRATION          X     X    X    X      ·        X     X
ENERGY             X     X    X    X      X        ·     X
GEOPOLITICS        X     X    X    X      X        X     ·

An X means that an interaction is analytically possible.

It does not mean that causality exists.

Causal status must be separately established.

⸻

35. Event-driven architecture

The platform should use event-driven processing where appropriate.

Conceptually:

Source Event
    ↓
Ingestion Event
    ↓
Validation Event
    ↓
Normalization Event
    ↓
Evidence Event
    ↓
Claim Update Event
    ↓
State Update Event
    ↓
Signal Evaluation Event
    ↓
Hypothesis Update Event
    ↓
Scenario Update Event
    ↓
Prediction Event
    ↓
Calibration Event

Each event should be:

* immutable where possible;
* timestamped;
* identifiable;
* attributable;
* replayable;
* auditable.

⸻

36. Idempotency

Every ingestion and processing operation that can be retried must support idempotency.

Repeated delivery of the same event must not create duplicate analytical reality.

The system should use:

event_id
source_id
content_hash
observation_time
ingestion_time
version

to identify duplicate or revised information.

⸻

37. Failure architecture

CEUTIA must assume components will fail.

Failure modes include:

* source unavailable;
* corrupted data;
* delayed data;
* model failure;
* database failure;
* network failure;
* API failure;
* incorrect schema;
* contradictory sources;
* model drift;
* hallucinated LLM output;
* security incident.

The system should implement:

timeouts
retries
circuit breakers
dead-letter queues
graceful degradation
health checks
fallbacks
event replay
audit trails

A missing source must not silently become a zero.

⸻

38. Graceful degradation

If an analytical subsystem fails, CEUTIA should continue operating at a reduced capability.

Example:

Prediction Engine unavailable
        ↓
Signals remain available
        ↓
Raw observations remain available
        ↓
Public information remains available

The user must be informed about degraded analytical capability.

⸻

39. LLM architecture

Large language models may assist with:

* semantic extraction;
* document classification;
* entity resolution;
* summarization;
* hypothesis generation;
* natural-language interfaces;
* explanation of already-computed results.

LLMs must not become the authoritative epistemic layer.

The architecture must prevent:

LLM statement
→
automatically accepted fact

Instead:

LLM output
 ↓
structured candidate
 ↓
validation
 ↓
provenance
 ↓
epistemic evaluation
 ↓
accepted / rejected / unresolved

The model must never fabricate provenance.

⸻

40. Mathematical computation

Numerical computation should occur in deterministic or explicitly stochastic analytical services rather than being delegated implicitly to natural-language generation.

Examples:

* time-series analysis;
* Bayesian updating;
* anomaly detection;
* survival analysis;
* state-space models;
* change-point detection;
* network analysis;
* differential-equation models;
* agent-based models;
* Monte Carlo simulation;
* sensitivity analysis;
* causal inference;
* optimization;
* forecasting.

Every model must have:

model_id
version
inputs
parameters
assumptions
outputs
uncertainty
validation
calibration
limitations

⸻

41. Model registry

All production models must be versioned.

Model
├── identifier
├── version
├── owner
├── purpose
├── mathematical specification
├── training data
├── validation data
├── assumptions
├── known failure modes
├── performance
├── calibration
├── deployment status
└── retirement status

A prediction must always identify the model version that produced it.

⸻

42. Data stores

The architecture should support different storage classes.

Conceptually:

Object Store
 └── raw documents / source artifacts
Relational Store
 └── structured entities / metadata
Time-Series Store
 └── temporal observations
Geospatial Store
 └── geographic objects
Graph Store
 └── networks / relationships
Evidence Store
 └── evidence / provenance / claims
Model Store
 └── models / parameters / versions
Event Store
 └── immutable processing events
Audit Store
 └── security / governance / analytical audit

The exact technologies are implementation decisions and must not be hard-coded into this architectural specification.

⸻

43. API architecture

APIs should expose typed objects rather than arbitrary database access.

Examples:

/sources
/observations
/evidence
/claims
/hypotheses
/states
/trajectories
/signals
/alerts
/scenarios
/predictions
/outcomes
/calibration

Access must be authorization-controlled.

The public API must never expose internal storage indiscriminately.

⸻

44. Query architecture

A query such as:

"Is Ceuta becoming less resilient?"

must not be answered by a simple text search.

The system should decompose it into:

Define resilience
 ↓
Identify relevant subsystems
 ↓
Retrieve trajectories
 ↓
Estimate capacity
 ↓
Estimate pressure
 ↓
Measure recovery
 ↓
Detect cross-domain coupling
 ↓
Compare baseline
 ↓
Quantify uncertainty
 ↓
Evaluate competing explanations
 ↓
Produce conclusion

The natural-language layer is therefore an interface to the analytical architecture, not a replacement for it.

⸻

45. Explainability architecture

Every important output should support several explanation levels.

Level 1 — Summary

What is happening?

Level 2 — Evidence

What observations support it?

Level 3 — Mechanism

What mechanism is proposed?

Level 4 — Uncertainty

What remains unknown?

Level 5 — Alternatives

What competing explanations exist?

Level 6 — Mathematics

Which model generated the estimate?

Level 7 — Provenance

Which original sources support the underlying observations?

⸻

46. Observability

CEUTIA itself must be observable.

Operational metrics should include:

ingestion latency
processing latency
source availability
pipeline failures
data freshness
missingness
duplicate rate
model latency
prediction volume
alert volume
false-positive rate
false-negative rate
calibration
API latency
security events

The platform should monitor not only the territory but also its own reliability.

⸻

47. Data quality

Every dataset must have quality metadata.

Potential dimensions:

completeness
accuracy
timeliness
consistency
uniqueness
validity
methodological quality
source independence
revision history

Quality must not be reduced to one universal score.

⸻

48. Security architecture integration

Security is cross-cutting.

The architecture must integrate:

authentication
authorization
least privilege
secret management
encryption
input validation
output filtering
rate limiting
audit
security monitoring
tenant isolation
data classification
incident response

Security controls must operate at API, service, data and model levels.

⸻

49. Privacy architecture

Privacy must be enforced before analytical aggregation where necessary.

The architecture should support:

data minimization
purpose limitation
pseudonymization
aggregation
access controls
retention limits
de-identification
privacy-preserving statistics

Individual-level data must not be retained merely because they could theoretically become useful.

⸻

50. Human-in-the-loop architecture

High-impact outputs must support human review.

Examples:

high-impact alert
        ↓
analytical review
        ↓
human validation
        ↓
decision-support output

Human review does not mean manually reviewing every observation.

It means placing human judgment at the points where automated inference could materially alter decisions.

⸻

51. Anti-patterns

The following architectural patterns are prohibited.

Dashboard-first architecture

Collecting indicators without an underlying ontology or state model.

LLM-as-database

Using a language model’s latent knowledge as the authoritative knowledge store.

LLM-as-truth-engine

Treating generated prose as verified evidence.

Correlation-as-causality

Representing statistical association as causal mechanism without justification.

Alert inflation

Generating alerts for every anomaly.

Single-score governance

Reducing complex system state to one opaque risk number.

Person-as-sensor

Treating individual suffering or communication as direct evidence of threat.

Migration-as-threat

Encoding migration itself as a threat variable.

Source counting

Assuming ten dependent sources provide ten independent confirmations.

Silent contradiction resolution

Overwriting conflicting evidence without preserving the conflict.

Data leakage across domains

Allowing PUBLIC and OWNER information to mix without explicit authorization.

Hidden model changes

Changing predictive models without versioning.

Uncalibrated prediction

Producing probabilities without subsequent outcome comparison.

⸻

52. End-to-end execution

A complete CEUTIA analytical cycle is:

1. SOURCE DISCOVERY
       ↓
2. ACQUISITION
       ↓
3. AUTHENTICATION / VALIDATION
       ↓
4. RAW STORAGE
       ↓
5. NORMALIZATION
       ↓
6. ENTITY / TEMPORAL / SPATIAL RESOLUTION
       ↓
7. OBSERVATION CREATION
       ↓
8. EVIDENCE EVALUATION
       ↓
9. CLAIM CONSTRUCTION
       ↓
10. PROVENANCE / INDEPENDENCE
       ↓
11. CONTRADICTION DETECTION
       ↓
12. STATE UPDATE
       ↓
13. TRAJECTORY ANALYSIS
       ↓
14. CAPACITY / PRESSURE ANALYSIS
       ↓
15. NETWORK / INTERACTION ANALYSIS
       ↓
16. SIGNAL DETECTION
       ↓
17. COMPETING HYPOTHESES
       ↓
18. SCENARIO GENERATION
       ↓
19. PROBABILISTIC PREDICTION
       ↓
20. ALERT / DECISION SIGNAL
       ↓
21. PUBLIC OR OWNER ROUTING
       ↓
22. HUMAN INTERPRETATION
       ↓
23. OBSERVED OUTCOME
       ↓
24. PREDICTION SCORING
       ↓
25. CALIBRATION
       ↓
26. MODEL REVISION
       ↓
27. REPROCESSING / LEARNING

This cycle must be persistent rather than executed only once.

⸻

53. Architecture of anticipation

The central objective is early recognition of trajectory deterioration.

CEUTIA should seek the transition:

NORMAL VARIABILITY
        ↓
EARLY DEVIATION
        ↓
PERSISTENT SIGNAL
        ↓
MULTI-DOMAIN CONVERGENCE
        ↓
CAPACITY DETERIORATION
        ↓
THRESHOLD PROXIMITY
        ↓
AMPLIFICATION
        ↓
CASCADE

The architecture is specifically designed to intervene analytically before the final visible manifestation.

Therefore:

Disease

is not the first object of interest.

The preceding trajectory is.

Likewise:

hunger

is not necessarily the first observable.

Supply stress, affordability, logistics and reserve may deteriorate earlier.

Likewise:

war

is not necessarily the first observable.

The system may detect preceding changes in diplomatic, military, economic, informational and infrastructural trajectories.

The existence of precursor signals does not guarantee the final event.

⸻

54. Fundamental architectural loop

CEUTIA ultimately operates as a closed learning system:

[
Observation
\rightarrow
Model
\rightarrow
Prediction
\rightarrow
Reality
\rightarrow
Evaluation
\rightarrow
Model\ Revision
]

The platform must therefore learn not merely from more data, but from the relationship between its predictions and what subsequently happened.

That distinction is essential.

A system that continuously generates explanations without measuring whether those explanations predict reality is not an intelligence system.

It is a narrative generator.

CEUTIA must be architected to become progressively more falsifiable, measurable and calibrated.

⸻

55. Final architectural invariant

The central invariant of CEUTIA is:

No important conclusion should exist without a traceable path from observation to evidence, from evidence to inference, from inference to model, and from model to measurable outcome.

And the reciprocal invariant is:

No observation should be discarded merely because its significance is not yet known.

The architecture must therefore preserve both knowledge and uncertainty.

Its purpose is not to eliminate uncertainty.

Its purpose is to make uncertainty explicit, quantify it where possible, update it when new evidence arrives, and detect when a complex system is moving toward a state in which intervention becomes increasingly difficult.


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

