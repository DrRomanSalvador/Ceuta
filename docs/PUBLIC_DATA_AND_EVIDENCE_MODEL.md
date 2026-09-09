# CeutIA — PUBLIC DATA AND EVIDENCE MODEL
## Modelo de datos, evidencia, procedencia, incertidumbre y trazabilidad del sistema PUBLIC
Versión: 1.0
Estado: Arquitectura normativa
Ámbito: PUBLIC
Proyecto: CeutIA
---
# 1. Propósito
Este documento define cómo CeutIA PUBLIC transforma información procedente del mundo real en objetos de conocimiento computables sin perder:
- procedencia;
- contexto;
- temporalidad;
- espacialidad;
- incertidumbre;
- calidad;
- independencia;
- contradicción;
- trazabilidad;
- granularidad;
- privacidad;
- limitaciones;
- estado epistemológico.
El objetivo no es simplemente almacenar datos.
El objetivo es preservar la cadena:
mundo real
→ fuente
→ artefacto
→ observación
→ medición o evento
→ afirmación
→ evidencia
→ señal
→ inferencia
→ hipótesis
→ predicción
→ alerta
→ evaluación posterior.
Cada transformación debe poder reconstruirse.
CeutIA no debe convertir automáticamente información en verdad.
Una fuente puede ser fiable y estar equivocada respecto de una afirmación concreta.
Una afirmación puede proceder de una fuente de alta calidad y continuar siendo incierta.
Una observación puede ser correcta sin demostrar causalidad.
Una coincidencia temporal puede ser informativa sin constituir una relación causal.
Una publicación viral demuestra que determinado contenido circula; no demuestra que sus afirmaciones sean verdaderas.
---
# 2. Principio fundamental
## Ningún dato debe perder su historia epistemológica al entrar en CeutIA
Toda pieza de información relevante debe conservar, como mínimo:
1. de dónde procede;
2. qué representa;
3. cuándo ocurrió;
4. cuándo fue observado;
5. cuándo fue publicado;
6. cuándo fue incorporado;
7. en qué espacio se produjo;
8. qué incertidumbre contiene;
9. qué transformaciones sufrió;
10. qué otras evidencias la corroboran;
11. qué evidencias la contradicen;
12. qué fuentes dependen de ella;
13. qué inferencias se construyeron sobre ella;
14. qué versión del sistema la procesó;
15. quién o qué proceso realizó cada transformación.
La pérdida de cualquiera de estos elementos puede alterar el significado del dato.
---
# 3. Principio de separación epistemológica
CeutIA debe distinguir explícitamente:
```text
DATA
OBSERVATION
MEASUREMENT
EVENT
TESTIMONY
CLAIM
EVIDENCE
SIGNAL
INFERENCE
HYPOTHESIS
PREDICTION
SCENARIO
ALERT
DECISION
OUTCOME

Estos objetos no son intercambiables.

3.1 Data

Representación almacenada de información.

No implica por sí misma que la información sea verdadera.

3.2 Observation

Registro de algo observado mediante una fuente o mecanismo concreto.

3.3 Measurement

Observación cuantificada mediante un procedimiento definido.

Toda medición debe conservar, cuando sea posible:

* unidad;
* método;
* instrumento;
* precisión;
* resolución;
* incertidumbre;
* calibración;
* rango válido.

3.4 Event

Suceso situado temporal y espacialmente.

Ejemplos:

* aumento de demanda asistencial;
* interrupción de suministro;
* episodio meteorológico;
* concentración extraordinaria de personas;
* cambio administrativo;
* brote epidemiológico;
* incidente violento.

3.5 Testimony

Declaración realizada por una persona.

Debe conservarse como testimonio, no transformarse automáticamente en hecho.

Puede ser:

* verdadera;
* falsa;
* parcialmente verdadera;
* imprecisa;
* incompleta;
* descontextualizada;
* imposible de verificar.

Su valor puede ser factual, contextual o señalético.

3.6 Claim

Afirmación sobre el mundo.

Ejemplo:

"El tiempo de espera aumentó durante el periodo X."

Una afirmación debe poder apuntar a las evidencias que la sostienen y a las que la contradicen.

3.7 Evidence

Información utilizada para aumentar, disminuir o contextualizar la plausibilidad de una afirmación, hipótesis o explicación.

La evidencia no tiene un peso universal.

Su peso depende de:

* la pregunta;
* el contexto;
* la calidad;
* la independencia;
* la temporalidad;
* la validez del método;
* la representatividad;
* la consistencia con otras observaciones.

3.8 Signal

Patrón detectado que merece evaluación.

Una señal no equivale a un hecho causal.

Puede proceder de:

* cambio de nivel;
* cambio de pendiente;
* aceleración;
* anomalía;
* persistencia;
* cambio de variabilidad;
* cambio de correlación;
* sincronización;
* divergencia;
* concentración espacial;
* concentración temporal;
* interacción entre variables.

3.9 Inference

Conclusión derivada de observaciones mediante una regla, modelo o razonamiento explícito.

Debe conservar:

* premisas;
* método;
* versión del modelo;
* incertidumbre;
* supuestos.

3.10 Hypothesis

Explicación posible que compite con otras explicaciones.

Toda hipótesis relevante debe poder:

* formularse explícitamente;
* recibir evidencia a favor;
* recibir evidencia en contra;
* actualizar su plausibilidad;
* ser sustituida si aparece una explicación mejor.

3.11 Prediction

Estimación sobre un estado futuro.

Debe incluir:

* horizonte temporal;
* variable objetivo;
* probabilidad o distribución;
* intervalo de incertidumbre;
* condiciones;
* modelo;
* fecha de generación.

3.12 Scenario

Descripción condicional de una posible evolución del sistema.

Un escenario no debe presentarse como predicción cierta.

3.13 Alert

Salida operacional generada cuando determinadas condiciones justifican revisión, comunicación o actuación humana.

3.14 Decision

Decisión tomada por una persona u organización competente.

No debe confundirse con la alerta de CeutIA.

3.15 Outcome

Resultado observado después de una alerta, decisión o intervención.

Los outcomes permiten evaluar retrospectivamente el sistema.

⸻

4. Cadena canónica de datos

La arquitectura PUBLIC utilizará como flujo conceptual:

SOURCE
  ↓
RAW ARTIFACT
  ↓
INGESTION
  ↓
OBSERVATION
  ↓
NORMALIZATION
  ↓
EVENT / MEASUREMENT / TESTIMONY
  ↓
CLAIM
  ↓
EVIDENCE
  ↓
EVIDENCE BUNDLE
  ↓
SIGNAL
  ↓
MODEL INPUT
  ↓
INFERENCE / HYPOTHESIS
  ↓
PREDICTION / SCENARIO
  ↓
ALERT
  ↓
HUMAN REVIEW
  ↓
DECISION
  ↓
OUTCOME
  ↓
RETROSPECTIVE EVALUATION

No todos los datos deben recorrer todas las etapas.

Por ejemplo:

AEMET observation
→ measurement
→ anomaly
→ signal

mientras que:

citizen testimony
→ testimony
→ claim
→ corroboration search
→ signal

puede seguir otra trayectoria.

⸻

5. Modelo de Source

Una fuente representa el origen de la información.

source:
  source_id:
  source_type:
  organization:
  name:
  authority_domain:
  geographic_scope:
  temporal_scope:
  publication_channel:
  collection_method:
  known_dependencies:
  reliability_profile:
  access_date:
  provenance:
  status:

5.1 Tipos de fuente

CeutIA debe soportar como mínimo:

PRIMARY_INSTITUTIONAL
SCIENTIFIC
INTERNATIONAL_ORGANIZATION
PROFESSIONAL
JUDICIAL
MEDIA
SOCIAL_MEDIA
CITIZEN
SENSOR
DEVICE
DATABASE
ADMINISTRATIVE
MODEL
DERIVED

No existe una jerarquía absoluta de verdad basada únicamente en source_type.

La calidad de una fuente es contextual.

⸻

6. Reliability Profile

La fiabilidad no debe almacenarse como un único número global.

Debe descomponerse.

reliability_profile:
  accuracy:
  completeness:
  timeliness:
  methodological_quality:
  representativeness:
  consistency:
  transparency:
  reproducibility:
  historical_performance:
  known_biases:
  domain_validity:

Una fuente puede tener:

alta autoridad institucional
+
alta calidad metodológica
+
baja resolución temporal

y otra:

baja autoridad factual
+
alta velocidad
+
alta sensibilidad como señal temprana.

Ambas pueden ser útiles para funciones diferentes.

⸻

7. Source quality ≠ claim truth

CeutIA nunca debe utilizar una regla equivalente a:

fuente prestigiosa → afirmación verdadera

Debe utilizar:

calidad de fuente
+
calidad específica de la observación
+
contexto
+
método
+
corroboración
+
independencia
+
consistencia temporal
+
contradicciones
→ peso epistemológico contextual.

⸻

8. Raw Artifact

El artefacto bruto conserva la información original antes de transformaciones.

raw_artifact:
  artifact_id:
  source_id:
  acquired_at:
  original_timestamp:
  format:
  content_hash:
  storage_reference:
  language:
  encoding:
  extraction_method:
  extraction_version:
  integrity_status:

El artefacto original no debe modificarse silenciosamente.

Las transformaciones posteriores generan nuevas versiones.

⸻

9. Observation

observation:
  observation_id:
  source_id:
  artifact_id:
  observed_at:
  observation_type:
  variable:
  value:
  unit:
  method:
  location:
  uncertainty:
  quality:
  transformation_history:

La observación debe conservar el vínculo con el artefacto original.

⸻

10. Temporalidad

CeutIA debe evitar utilizar un único timestamp.

Cuando sea posible, debe distinguir:

event_time
observation_time
publication_time
ingestion_time
processing_time
effective_from
effective_to

Ejemplo:

Un evento ocurre a las 10:00.

Se observa a las 10:15.

Se publica a las 11:00.

CeutIA lo ingiere a las 11:02.

El sistema no debe confundir ninguno de estos tiempos.

⸻

11. Espacialidad

Toda observación espacialmente relevante debe conservar su granularidad.

Ejemplos:

territory
municipality
district
neighborhood
facility
service
geographic grid
coordinates
route
unknown

La precisión espacial debe almacenarse separadamente de la localización.

No debe inventarse precisión inexistente.

⸻

12. Measurement

measurement:
  measurement_id:
  variable:
  value:
  unit:
  reference_range:
  instrument:
  method:
  calibration:
  precision:
  uncertainty:
  observed_at:
  location:
  operator:
  quality_flags:

Las medidas incompatibles no deben fusionarse automáticamente.

⸻

13. Event

event:
  event_id:
  event_type:
  start_time:
  end_time:
  location:
  magnitude:
  affected_systems:
  source_ids:
  evidence_ids:
  confidence:
  status:

Los eventos pueden ser:

OBSERVED
REPORTED
INFERRED
ESTIMATED
PREDICTED
HYPOTHETICAL

Nunca deben mezclarse estos estados.

⸻

14. Testimony

testimony:
  testimony_id:
  source_type: CITIZEN
  submitted_at:
  event_time:
  location_precision:
  statement:
  observed_directly:
  emotional_context:
  corroboration_status:
  factual_claims:
  signal_value:
  safety_classification:
  publication_status:

El contenido emocional no determina la veracidad.

Tampoco debe eliminarse automáticamente.

Una persona puede equivocarse sobre el hecho y aun así proporcionar una señal válida sobre:

* miedo;
* percepción de inseguridad;
* deterioro de confianza;
* conflicto;
* sufrimiento;
* cambio conductual;
* exposición a determinados acontecimientos.

⸻

15. Claim

claim:
  claim_id:
  subject:
  predicate:
  object:
  scope:
  temporal_scope:
  spatial_scope:
  source_ids:
  evidence_ids:
  contradiction_ids:
  status:

Estados:

UNASSESSED
SUPPORTED
PARTIALLY_SUPPORTED
CONTESTED
CONTRADICTED
REFUTED
UNVERIFIABLE
EXPIRED

Una afirmación puede pasar de un estado a otro.

La evolución debe quedar registrada.

⸻

16. Evidence

La evidencia debe tener dirección epistemológica.

evidence:
  evidence_id:
  target_id:
  evidence_type:
  direction:
    - SUPPORT
    - REFUTE
    - CONTEXTUALIZE
    - NEUTRAL
  strength:
  independence:
  quality:
  temporal_fit:
  spatial_fit:
  methodological_fit:
  representativeness:
  uncertainty:
  source_id:
  provenance:

El campo direction es esencial.

La evidencia no debe reducirse a:

evidence = true

Debe poder representar:

evidence → supports H
evidence → weakens H
evidence → does not discriminate between H1/H2

⸻

17. Evidence Bundle

Las afirmaciones complejas deben evaluarse mediante conjuntos de evidencia.

evidence_bundle:
  bundle_id:
  target_id:
  evidence_ids:
  independent_sources:
  dependent_sources:
  supporting_evidence:
  contradicting_evidence:
  unresolved_evidence:
  aggregate_assessment:
  uncertainty:
  generated_at:

La cantidad de fuentes no equivale a cantidad de evidencia independiente.

⸻

18. Independencia de fuentes

CeutIA debe construir un grafo de dependencia entre fuentes.

Ejemplo:

SOURCE A
   ↓
MEDIA B
   ↓
SOCIAL C
   ↓
SOCIAL D

No deben contabilizarse A, B, C y D como cuatro evidencias independientes.

El sistema debe detectar:

* copia;
* sindicación;
* reutilización;
* misma fuente primaria;
* misma base de datos;
* mismo comunicado;
* misma imagen;
* mismo vídeo;
* misma agencia;
* misma narrativa derivada.

⸻

19. Corroboración

La corroboración debe considerar independencia.

Conceptualmente:

Corroboration ≠ number_of_sources

Una formulación más apropiada es:

effective_corroboration
=
f(
  independent_sources,
  methodological_quality,
  temporal_consistency,
  spatial_consistency,
  measurement_quality,
  contradiction_level
)

⸻

20. Contradicción

Las contradicciones no deben eliminarse automáticamente.

contradiction:
  contradiction_id:
  claim_a:
  claim_b:
  variable:
  nature:
  temporal_relation:
  spatial_relation:
  source_dependence:
  resolution:
  status:

Tipos:

DIRECT_CONTRADICTION
TEMPORAL_CONTRADICTION
SPATIAL_CONTRADICTION
DEFINITIONAL_CONTRADICTION
MEASUREMENT_DISCREPANCY
SAMPLING_DISCREPANCY
METHOD_DISCREPANCY
APPARENT_CONTRADICTION
UNRESOLVED

Una contradicción puede revelar:

* error;
* sesgo;
* heterogeneidad;
* cambio temporal;
* diferencia metodológica;
* fenómeno espacialmente localizado;
* fenómeno no estacionario.

Por tanto:

contradiction ≠ data failure

Puede ser información sobre el sistema.

⸻

21. Incertidumbre

CeutIA debe representar incertidumbre explícitamente.

No utilizar:

confidence = 0.87

sin indicar qué significa.

Debe diferenciarse:

measurement_uncertainty
sampling_uncertainty
model_uncertainty
parameter_uncertainty
structural_uncertainty
epistemic_uncertainty
aleatory_uncertainty
temporal_uncertainty
spatial_uncertainty
classification_uncertainty

⸻

22. Missingness

Los datos ausentes no deben tratarse automáticamente como cero.

Tipos:

NOT_COLLECTED
NOT_AVAILABLE
NOT_REPORTED
NOT_APPLICABLE
UNKNOWN
WITHHELD
DELAYED
LOST
CENSORED

Debe considerarse el mecanismo de ausencia:

MCAR
MAR
MNAR
UNKNOWN

Especialmente cuando la ausencia pueda depender del propio fenómeno.

Ejemplo:

Si durante una crisis disminuyen los registros porque el sistema sanitario está saturado, la reducción de registros no significa necesariamente reducción de enfermedad.

⸻

23. Baseline

Ninguna anomalía debe interpretarse sin referencia cuando exista una base razonable.

CeutIA debe conservar:

baseline:
  baseline_id:
  variable:
  population:
  spatial_scope:
  temporal_scope:
  reference_period:
  method:
  seasonality:
  trend:
  expected_distribution:
  uncertainty:

El baseline puede ser:

* histórico;
* estacional;
* móvil;
* estructural;
* contrafactual;
* comparativo;
* estratificado.

⸻

24. Contexto temporal

El mismo valor puede tener significados diferentes según:

* hora;
* día;
* estación;
* duración;
* velocidad de cambio;
* estado previo;
* capacidad disponible.

Por ello:

state ≠ trajectory

y:

level ≠ rate_of_change

y:

rate_of_change ≠ acceleration

⸻

25. Dinámica

Para una variable X:

X(t)

CeutIA debe poder analizar:

X(t)
ΔX/Δt
d²X/dt²

además de:

variance
autocorrelation
persistence
change_points
seasonality
trend
volatility
cross_correlation
lagged_correlation
synchronization

Esto permite detectar cambios en el comportamiento del sistema antes de que aparezca un cambio extremo en el nivel absoluto.

⸻

26. Signal

Una señal debe especificar su mecanismo de detección.

signal:
  signal_id:
  target_variable:
  signal_type:
  detection_method:
  baseline_id:
  observed_value:
  expected_value:
  deviation:
  velocity:
  acceleration:
  persistence:
  spatial_pattern:
  temporal_pattern:
  interacting_variables:
  uncertainty:
  evidence_ids:
  generated_at:

Tipos:

LEVEL_SHIFT
RATE_SHIFT
ACCELERATION
ANOMALY
CHANGE_POINT
PERSISTENCE
VOLATILITY_CHANGE
CORRELATION_CHANGE
SYNCHRONIZATION
DIVERGENCE
SPATIAL_CLUSTER
TEMPORAL_CLUSTER
MULTIVARIATE_PATTERN
NETWORK_PATTERN
CAPACITY_STRESS
CROSS_DOMAIN_SIGNAL

⸻

27. Señales débiles

Una señal débil no debe ignorarse simplemente porque no alcance todavía el umbral de alerta.

Debe poder almacenarse como:

WEAK_SIGNAL

con:

* baja intensidad;
* alta incertidumbre;
* posible relevancia futura;
* evolución temporal;
* relación con otras señales.

Varias señales débiles pueden adquirir relevancia cuando convergen.

⸻

28. Interacciones entre variables

CeutIA no debe analizar exclusivamente variables aisladas.

Debe representar:

X1 → X2
X1 ↔ X2
X1 × X2 → X3

Ejemplo conceptual:

demand ↑
+
capacity ↓
+
waiting_time ↑
+
staff_fatigue ↑
→
systemic_stress ↑

La interacción puede ser no lineal.

⸻

29. Capacidad

La capacidad debe distinguir:

GLOBAL_CAPACITY
EFFECTIVE_CAPACITY
ACCESSIBLE_CAPACITY
AVAILABLE_CAPACITY
RECOVERABLE_CAPACITY
SUSTAINABLE_CAPACITY

Ejemplo:

Un hospital puede disponer de capacidad física global pero no de capacidad efectiva si:

* falta personal;
* existe saturación logística;
* aumenta el tiempo de respuesta;
* existen cuellos de botella;
* determinadas áreas no pueden utilizarse.

⸻

30. Queueing data

Cuando una variable representa demanda de servicios, CeutIA debe poder conservar:

queue_state:
  arrival_rate:
  service_rate:
  queue_length:
  waiting_time:
  abandonment_rate:
  utilization:
  capacity:
  burst_intensity:
  recovery_time:

Debe distinguirse:

steady demand

de:

transient pulse

Una entrada de 1.000 personas repartidas durante 30 días no es equivalente a 1.000 personas concentradas en tres horas.

La intensidad temporal forma parte del fenómeno.

⸻

31. Provenance Graph

Todo objeto derivado debe mantener un grafo de procedencia.

SOURCE
  ↓
ARTIFACT
  ↓
OBSERVATION
  ↓
CLAIM
  ↓
EVIDENCE
  ↓
SIGNAL
  ↓
MODEL
  ↓
PREDICTION
  ↓
ALERT

Cada arista debe representar una relación:

DERIVED_FROM
SUPPORTED_BY
CONTRADICTED_BY
TRANSFORMED_FROM
AGGREGATED_FROM
INFERRED_FROM
PREDICTED_FROM
VALIDATED_BY
INVALIDATED_BY

⸻

32. Lineage

Toda transformación debe ser reproducible.

lineage:
  operation_id:
  input_ids:
  output_ids:
  operation_type:
  algorithm:
  software_version:
  model_version:
  parameters:
  operator:
  timestamp:
  deterministic:
  reproducibility_status:

Si un resultado no puede reconstruirse, debe registrarse como limitación.

⸻

33. Transformaciones

CeutIA debe distinguir:

RAW
CLEANED
NORMALIZED
STANDARDIZED
AGGREGATED
IMPUTED
INTERPOLATED
DERIVED
MODELED
PREDICTED

Nunca debe ocultarse una imputación o transformación relevante.

⸻

34. Imputación

Los valores imputados deben conservar:

imputation:
  method:
  original_missingness:
  model:
  uncertainty:
  sensitivity_analysis:
  generated_at:

Un valor imputado no debe representarse como observación directa.

⸻

35. Agregación

Cuando se agreguen datos:

individual
→ subgroup
→ geographic aggregate
→ temporal aggregate
→ system aggregate

deben conservarse:

* tamaño de muestra;
* denominador;
* método;
* pérdida de resolución;
* incertidumbre;
* criterios de inclusión.

⸻

36. Individual vs system-level data

CeutIA debe mantener dos planos conceptuales.

PERSON-LEVEL
SYSTEM-LEVEL

La información personal puede utilizarse para prestar apoyo cuando exista base legítima y finalidad adecuada.

El sistema de inteligencia territorial debe trabajar preferentemente con:

aggregated
de-identified
privacy-preserving
purpose-limited

information.

Una persona no debe convertirse en un sensor permanente del territorio.

⸻

37. Prohibición de inferencias identitarias indebidas

CeutIA no debe utilizar:

nationality
ethnicity
religion
protected characteristic
migration status

como sustitutos de:

criminal propensity
dangerousness
violence propensity
disease diagnosis
individual threat

La arquitectura puede utilizar contexto poblacional para determinar qué fenómenos conviene vigilar, pero no para atribuir características individuales sin evidencia directa y válida.

⸻

38. Health screening data

Cuando una persona solicite apoyo preventivo, sus respuestas pueden generar:

self-reported observation

y no automáticamente:

diagnosis

Ejemplo:

sleep disturbance = reported

no equivale a:

sleep disorder = diagnosed

La interacción adaptativa puede seleccionar preguntas posteriores.

Ejemplo:

sleep disturbance
      ↓
nightmares?
      ↓
trauma exposure?
      ↓
functional impairment?
      ↓
professional support recommendation

No deben realizarse todas las preguntas a todas las personas si la información previa no las hace pertinentes.

⸻

39. Privacy-preserving aggregation

Cuando una respuesta individual pueda aportar información útil para el sistema, CeutIA debe utilizar, cuando proceda:

aggregation
de-identification
pseudonymization
minimum necessary data
privacy-preserving statistics
thresholding
suppression

La agregación nunca debe utilizarse para ocultar incertidumbre.

⸻

40. Sensitive data

Los datos especialmente sensibles deben tener:

purpose
legal_basis
access_class
retention_policy
auditability

No deben recogerse únicamente porque técnicamente sea posible.

⸻

41. Retention

La retención no se define mediante un número universal.

Debe depender de:

* finalidad;
* categoría de datos;
* base jurídica;
* necesidad operacional;
* riesgo;
* obligaciones legales;
* valor científico;
* necesidad de auditoría.

Debe existir:

retention:
  policy_id:
  purpose:
  retention_period:
  legal_basis:
  deletion_method:
  archival_status:

⸻

42. Access control

Cada objeto debe poder clasificarse según:

PUBLIC
INTERNAL
RESTRICTED
SENSITIVE
HIGHLY_RESTRICTED

El acceso debe depender de:

role
purpose
authorization
data sensitivity
operational necessity

⸻

43. Public presentation

La información utilizada internamente para detectar señales no tiene por qué mostrarse íntegramente al ciudadano.

Debe existir una separación:

INTERNAL EVIDENCE LAYER
        ↓
PUBLIC COMMUNICATION LAYER

La capa pública debe minimizar:

* amplificación de rumores;
* exposición de datos personales;
* reproducción innecesaria de violencia;
* estigmatización;
* información operacional sensible;
* inferencias no verificadas.

Pero no debe falsear deliberadamente la realidad.

⸻

44. Harmful content

El contenido violento, extremista, xenófobo o potencialmente dañino debe someterse a:

ingestion
→ classification
→ epistemic evaluation
→ risk classification
→ secure storage
→ signal extraction
→ public-display decision

La moderación del contenido y su valor epistemológico son dimensiones diferentes.

Un contenido puede ser:

unsafe to amplify

y simultáneamente:

valuable as a signal

⸻

45. Social media

Una publicación social debe poder aportar:

perception signal
behavioral signal
mobilization signal
misinformation signal
event lead

pero no debe considerarse automáticamente:

verified fact

La viralidad no equivale a veracidad.

⸻

46. Citizen reports

Los testimonios ciudadanos deben poder alimentar sistemas de detección temprana.

La lógica será:

testimony
→ classify
→ extract claims
→ compare with existing evidence
→ search corroboration
→ detect spatial/temporal clustering
→ estimate signal value

No:

testimony
→ fact

⸻

47. Bayesian evidence updating

Cuando sea apropiado, las hipótesis pueden actualizarse mediante:

P(H | E)

y posteriormente:

P(H | E1, E2, ..., En)

La actualización debe considerar dependencia entre evidencias.

No debe realizarse:

E1 + E2 + E3 + E4

como si fueran independientes cuando proceden del mismo origen.

⸻

48. Hypothesis competition

CeutIA debe almacenar hipótesis competidoras.

hypothesis:
  hypothesis_id:
  statement:
  prior:
  evidence_for:
  evidence_against:
  posterior:
  assumptions:
  falsifiers:
  competing_hypotheses:
  uncertainty:
  status:

Ejemplo conceptual:

H1: aumento de demanda explicado principalmente por shock poblacional.
H2: aumento de demanda explicado principalmente por cambio de acceso.
H3: aumento de demanda explicado principalmente por modificación de comportamiento.
H4: interacción de H1 + H2 + H3.

La arquitectura debe permitir que H4 termine siendo más plausible que cualquiera de las explicaciones simples.

⸻

49. Causal inference

CeutIA debe diferenciar:

correlation
temporal precedence
association
causal hypothesis
causal evidence
causal identification

No debe inferir causalidad únicamente porque:

A ocurrió antes que B

ni porque:

A correlaciona con B.

Los modelos causales deben especificar:

* supuestos;
* variables;
* posibles confusores;
* método;
* identificación;
* sensibilidad;
* incertidumbre.

⸻

50. Model input

Antes de introducir datos en un modelo debe generarse una representación explícita.

model_input:
  input_id:
  model_id:
  source_objects:
  transformations:
  feature_definitions:
  temporal_window:
  spatial_window:
  missingness:
  uncertainty:
  normalization:
  version:

El modelo nunca debe recibir una variable cuyo significado no pueda reconstruirse.

⸻

51. Data quality gates

Antes de que un dato alcance una función crítica:

GATE 1 — integrity
GATE 2 — schema
GATE 3 — temporal validity
GATE 4 — spatial validity
GATE 5 — range plausibility
GATE 6 — provenance
GATE 7 — duplication
GATE 8 — dependency
GATE 9 — missingness
GATE 10 — contextual validity

El fallo de un gate no implica necesariamente eliminación.

Puede producir:

REJECT
QUARANTINE
DEGRADE
FLAG
ACCEPT_WITH_LIMITATIONS
ACCEPT

⸻

52. Data quarantine

Los datos sospechosos deben poder aislarse sin destruirlos.

quarantine:
  object_id:
  reason:
  detected_at:
  detected_by:
  impact:
  investigation_status:
  resolution:

Esto permite investigar posteriormente errores de ingestión, manipulación o anomalías genuinas.

⸻

53. Anomaly vs error

CeutIA debe distinguir:

DATA_ERROR

de:

REAL_ANOMALY

Una observación extrema puede ser:

* error de sensor;
* error de transcripción;
* duplicado;
* cambio metodológico;
* evento extraordinario real.

Por tanto:

anomaly ≠ invalid data

⸻

54. Data drift

CeutIA debe monitorizar:

DATA DRIFT
CONCEPT DRIFT
SOURCE DRIFT
MEASUREMENT DRIFT
BEHAVIORAL DRIFT

Ejemplos:

* cambia el método de recogida;
* cambia la población observada;
* cambia el comportamiento;
* cambia la definición de una variable;
* cambia la cobertura de una fuente.

Una serie temporal puede parecer cambiar porque cambió el instrumento.

⸻

55. Concept drift

El significado funcional de una relación puede cambiar.

Ejemplo conceptual:

X → Y

puede ser cierto durante un periodo y dejar de serlo posteriormente.

Los modelos no deben asumir estacionariedad indefinida.

⸻

56. Versionado

Todo objeto crítico debe poder relacionarse con:

schema_version
data_version
source_version
transformation_version
model_version
ontology_version
policy_version

Una alerta histórica debe poder reconstruirse con las versiones existentes en el momento en que fue generada.

⸻

57. Reproducibilidad

Toda salida importante debe responder:

¿Qué datos utilizó?
¿Qué versión tenían?
¿Qué modelo utilizó?
¿Qué parámetros utilizó?
¿Qué transformaciones se realizaron?
¿Qué evidencia existía en ese momento?
¿Qué incertidumbre tenía?

⸻

58. Alert eligibility

No toda señal genera una alerta.

Conceptualmente:

signal
+
relevance
+
magnitude
+
trajectory
+
persistence
+
uncertainty
+
potential impact
+
capacity
+
evidence quality
→
alert eligibility

La arquitectura detallada de alertas se encuentra en:

docs/PUBLIC_ALERT_AND_ESCALATION_MODEL.md

⸻

59. Alert provenance

Toda alerta debe apuntar a sus fundamentos.

alert_provenance:
  alert_id:
  evidence_ids:
  signal_ids:
  model_outputs:
  hypotheses:
  assumptions:
  uncertainty:
  generation_time:
  model_version:
  reviewer:

Una alerta sin trazabilidad suficiente debe degradarse o no emitirse.

⸻

60. Alert explainability

La explicación debe poder responder:

WHAT changed?
WHY is it relevant?
COMPARED WITH WHAT?
HOW fast?
FOR HOW LONG?
WHERE?
WHICH systems are involved?
WHAT evidence supports it?
WHAT evidence contradicts it?
HOW independent are the sources?
HOW uncertain is the assessment?
WHAT could explain it alternatively?
WHAT is unknown?

⸻

61. Prediction registry

Todas las predicciones relevantes deben registrarse.

prediction:
  prediction_id:
  target:
  forecast_time:
  horizon:
  probability:
  interval:
  assumptions:
  model:
  model_version:
  generated_at:
  evidence:
  realized_outcome:
  calibration_status:

Una predicción no evaluada posteriormente no permite saber si CeutIA está aprendiendo.

⸻

62. Retrospective calibration

CeutIA debe comparar:

prediction
vs
observed outcome

y evaluar:

accuracy
precision
recall
false_positive_rate
false_negative_rate
calibration
Brier_score
log_loss
coverage
lead_time

Las métricas deben elegirse según el tipo de problema.

No existe una única métrica universal.

⸻

63. False positives / false negatives

CeutIA debe registrar ambos.

TRUE POSITIVE
FALSE POSITIVE
TRUE NEGATIVE
FALSE NEGATIVE

Pero el coste de cada error debe modelarse según contexto.

Una alerta sanitaria temprana y una falsa acusación individual no tienen la misma estructura de daño.

⸻

64. Cost-sensitive inference

Cuando sea apropiado:

Expected Loss
=
P(false positive) × Cost(FP)
+
P(false negative) × Cost(FN)

La función de coste debe ser explícita.

Nunca debe ocultarse dentro de un algoritmo sin documentación.

⸻

65. Human review

Las salidas de alto impacto deben estar sujetas a revisión humana cuando corresponda.

La revisión debe poder:

accept
reject
downgrade
upgrade
request_more_evidence
mark_uncertain
mark_false
request_investigation

El resultado humano debe quedar registrado.

⸻

66. Human disagreement

El desacuerdo humano también es información.

review:
  reviewer_id:
  assessment:
  confidence:
  disagreement_with_model:
  disagreement_reason:
  timestamp:

Si varios expertos discrepan, CeutIA no debe ocultarlo mediante un promedio automático si la discrepancia es epistemológicamente relevante.

⸻

67. Evidence-to-signal rule

Una señal debe poder reconstruirse:

Evidence E1
Evidence E2
Evidence E3
       ↓
Detection method M
       ↓
Signal S

No:

LLM said there is a risk

El LLM puede ayudar a extraer, clasificar o resumir.

No debe convertirse en autoridad epistemológica independiente.

⸻

68. LLM governance

Los modelos lingüísticos pueden utilizarse para:

* extracción;
* clasificación;
* normalización semántica;
* detección de entidades;
* resumen;
* traducción;
* agrupación;
* generación de hipótesis candidatas;
* búsqueda de contradicciones;
* explicación.

No deben:

* inventar evidencia;
* crear fuentes;
* rellenar datos ausentes como hechos;
* convertir testimonios en hechos;
* ocultar contradicciones;
* atribuir causalidad sin fundamento;
* producir perfiles de peligrosidad basados en identidad;
* generar alertas críticas sin trazabilidad.

⸻

69. LLM output

Toda salida generada por un LLM debe conservar:

llm_output:
  model:
  model_version:
  prompt_version:
  input_ids:
  output:
  generated_at:
  uncertainty:
  validation_status:
  human_review:

El texto generado por IA no debe confundirse con evidencia primaria.

⸻

70. Data contamination

CeutIA debe detectar cuando información generada por modelos pueda volver a introducirse como si fuera evidencia original.

Debe marcar:

HUMAN_GENERATED
MACHINE_GENERATED
MACHINE_TRANSFORMED
MACHINE_INFERRED
MIXED

Los datos sintéticos o generados por IA no deben mezclarse silenciosamente con observaciones reales.

⸻

71. Information loops

El propio CeutIA puede modificar el sistema que observa.

Debe poder representar:

INFORMATION
→ PERCEPTION
→ BEHAVIOR
→ SYSTEM STATE
→ NEW INFORMATION

Esto es especialmente importante para:

* comunicación pública;
* rumores;
* miedo;
* vigilancia;
* redes sociales;
* polarización;
* movilización;
* respuesta institucional.

CeutIA debe evitar interpretar como fenómeno exógeno aquello que puede haber sido parcialmente producido por información previa del propio sistema.

⸻

72. Feedback loops

Las variables pueden formar bucles:

A → B → C → A

Ejemplo conceptual:

incidente percibido
→ miedo
→ vigilancia
→ mayor detección/reporting
→ mayor número de incidentes percibidos
→ mayor miedo

El aumento observado puede reflejar simultáneamente:

real incidence
+
detection intensity
+
reporting intensity

Estas componentes deben distinguirse cuando sea posible.

⸻

73. Counterfactual data

Cuando CeutIA utilice escenarios o inferencia causal:

counterfactual:
  intervention:
  reference_state:
  alternative_state:
  assumptions:
  model:
  uncertainty:

Los escenarios contrafactuales no deben presentarse como hechos observados.

⸻

74. Data contracts

Toda fuente operacional debe disponer de un contrato.

data_contract:
  source_id:
  variables:
  schema:
  units:
  frequency:
  latency:
  geographic_resolution:
  temporal_resolution:
  quality_requirements:
  failure_modes:
  validation_rules:
  version:

Esto permite detectar cambios silenciosos de una fuente.

⸻

75. Failure modes

Cada fuente debe documentar, cuando sea posible:

missing data
duplicate data
late data
incorrect units
schema changes
coverage changes
measurement errors
sampling bias
reporting bias
outages
revision policy

⸻

76. Revisions

Los datos oficiales o científicos pueden ser revisados.

CeutIA debe conservar:

original version
revised version
revision date
revision reason
impact

No debe sobrescribirse la historia sin dejar rastro.

⸻

77. Historical state reconstruction

Para cualquier instante t, CeutIA debe poder reconstruir, dentro de los límites técnicos:

what was known at t
what evidence existed at t
what evidence was unavailable at t
what hypotheses existed at t
what predictions were made at t
what alerts were generated at t

No debe utilizarse retrospectivamente información posterior para evaluar decisiones como si hubiera estado disponible en ese momento.

⸻

78. Epistemic time vs world time

CeutIA debe distinguir:

WORLD TIME

de:

KNOWLEDGE TIME

El sistema puede conocer hoy que algo ocurrió ayer.

Eso no significa que pudiera haberlo sabido ayer.

Esta distinción es esencial para evaluar correctamente:

* alertas tempranas;
* predicciones;
* decisiones;
* fallos;
* tiempo de reacción.

⸻

79. Evidence maturity

Cada evidencia puede tener un estado:

RAW
INITIAL
PARTIALLY_CORROBORATED
CORROBORATED
STRONGLY_CORROBORATED
CONTESTED
REFUTED
EXPIRED

El estado debe poder evolucionar.

⸻

80. Evidence expiration

Una evidencia puede perder validez temporal sin haber sido falsa.

Ejemplo:

capacity_available = 20

puede ser cierto a las 10:00 y dejar de representar la situación a las 14:00.

Por tanto:

truth_at_t

no equivale necesariamente a:

truth_for_all_t

⸻

81. Spatial heterogeneity

Los agregados territoriales pueden ocultar fenómenos locales.

CeutIA debe poder distinguir:

territorial_average

de:

local_distribution

Un sistema puede parecer estable en promedio y presentar un cuello de botella crítico en un área concreta.

⸻

82. Simpson-type effects

Cuando sea relevante, CeutIA debe comprobar si una relación observada a nivel agregado desaparece o se invierte al estratificar.

aggregate relationship
vs
stratified relationship

Las conclusiones territoriales no deben basarse exclusivamente en promedios.

⸻

83. Ecological fallacy

Una relación entre variables agregadas no debe atribuirse automáticamente a individuos.

population-level association
≠
individual-level property

Esto es especialmente importante en:

* migración;
* violencia;
* salud;
* epidemiología;
* comportamiento;
* vulnerabilidad.

⸻

84. Person ≠ population signal

Una respuesta individual puede contribuir a una señal poblacional agregada.

Pero:

individual observation
≠
population conclusion

y:

population pattern
≠
individual diagnosis

⸻

85. Security-relevant signals

Cuando CeutIA detecte señales potencialmente relevantes para seguridad:

CeutIA
→ qualified alert
→ human interpretation
→ competent authority

Nunca:

CeutIA
→ autonomous enforcement

La alerta debe describir:

* qué se observó;
* qué patrón se detectó;
* qué evidencia existe;
* qué incertidumbre permanece;
* qué explicaciones alternativas existen.

No debe declarar automáticamente que una persona o grupo es peligroso.

⸻

86. Alert content minimization

Una alerta debe contener únicamente la información necesaria para la finalidad correspondiente.

Especialmente cuando implique:

* personas;
* menores;
* salud;
* migración;
* violencia;
* localización;
* datos sensibles.

⸻

87. System-level aggregation

Para inteligencia territorial, CeutIA debe priorizar variables agregadas como:

demand
capacity
waiting_time
incidence
mortality
mobility
environment
weather
infrastructure
economic stress
social stress
information dynamics
health indicators
service utilization
resource depletion
recovery capacity

La lista concreta de variables dependerá de la ontología y de las fuentes disponibles.

⸻

88. Mathematical state representation

El sistema puede representar el estado dinámico:

X(t)

mediante variables observadas, estimadas o latentes.

Modelo general:

X(t+1)
=
F(
  X(t),
  U(t),
  E(t),
  Θ(t)
)
+
ε(t)

donde:

X(t) = estado del sistema
U(t) = acciones/intervenciones
E(t) = perturbaciones externas
Θ(t) = parámetros
ε(t) = incertidumbre/residuo

La función F no tiene que ser única.

⸻

89. Model ensemble

CeutIA debe poder utilizar modelos complementarios.

statistical models
+
time-series models
+
Bayesian models
+
queueing models
+
network models
+
epidemiological models
+
causal models
+
agent-based models
+
system dynamics
+
machine learning

Ningún modelo individual debe convertirse en representación absoluta del territorio.

⸻

90. Model disagreement

Cuando diferentes modelos produzcan resultados diferentes:

model_comparison:
  models:
  outputs:
  disagreement:
  likely_causes:
  structural_uncertainty:
  decision_implication:

El desacuerdo puede revelar incertidumbre estructural.

No debe ocultarse mediante una media automática si los modelos representan hipótesis distintas.

⸻

91. Uncertainty propagation

La incertidumbre debe propagarse:

raw observation uncertainty
→ derived variable uncertainty
→ model uncertainty
→ prediction uncertainty
→ alert uncertainty

No debe aparecer una probabilidad final con más precisión aparente que los datos que la originaron.

⸻

92. Precision discipline

CeutIA debe evitar:

12.3847%

cuando la evidencia solo permite afirmar aproximadamente:

≈12%

La precisión numérica debe reflejar la precisión epistemológica.

⸻

93. Data ethics

CeutIA debe aplicar:

data minimization
purpose limitation
proportionality
privacy
security
traceability
accountability
fairness
contestability
human oversight

La arquitectura debe diseñarse para reducir daño, no únicamente para maximizar capacidad predictiva.

⸻

94. Evidence hierarchy

La arquitectura operativa puede priorizar:

A — primary institutional / direct measurement
B — peer-reviewed scientific evidence
C — professional/international organizations
D — reputable media
E — social media
F — citizen testimony

Pero la jerarquía no implica:

A = always true
F = useless

Una fuente secundaria puede detectar antes un fenómeno que una fuente institucional.

Una fuente institucional puede contener errores.

Un ciudadano puede detectar un evento antes que cualquier sistema formal.

La función de cada fuente debe determinar su utilidad.

⸻

95. Evidence matrix

Para cada afirmación relevante puede calcularse una matriz:

                QUALITY
                  ↑
                  |
       strong     |     strong
       weak       |     strong
------------------+----------------→ INDEPENDENCE
       weak       |     strong
       weak       |     strong

Pero ninguna puntuación debe sustituir al razonamiento contextual.

⸻

96. Minimum evidence record

Todo objeto de evidencia crítico debe poder responder:

WHAT?
WHO/WHAT SOURCE?
WHEN?
WHERE?
HOW OBSERVED?
HOW CERTAIN?
HOW INDEPENDENT?
WHAT SUPPORTS IT?
WHAT CONTRADICTS IT?
WHAT TRANSFORMATIONS OCCURRED?
WHAT IS UNKNOWN?

Si no puede responderse, la evidencia debe degradarse.

⸻

97. Audit log

Todo cambio relevante debe producir:

audit_event:
  event_id:
  actor:
  action:
  object_id:
  previous_state:
  new_state:
  timestamp:
  reason:
  authorization:

No deben existir modificaciones críticas sin trazabilidad.

⸻

98. Immutable provenance

La procedencia histórica crítica debe ser inmutable o contar con mecanismos equivalentes de integridad.

Los cambios posteriores deben generar nuevos estados.

No deben reescribir silenciosamente el pasado epistemológico del sistema.

⸻

99. Quality status

Cada objeto importante debe tener:

QUALITY_UNKNOWN
QUALITY_LOW
QUALITY_MODERATE
QUALITY_HIGH
QUALITY_CRITICAL

Pero quality nunca debe confundirse con:

truth

⸻

100. Confidence

La confianza debe estar asociada a una afirmación concreta.

Nunca:

source_confidence = universal truth score

Preferir:

confidence_in_claim
confidence_in_measurement
confidence_in_model
confidence_in_prediction

⸻

101. Epistemic state machine

Las afirmaciones pueden evolucionar:

UNASSESSED
    ↓
OBSERVED
    ↓
SUPPORTED
    ↓
CORROBORATED
    ↓
MODELLED
    ↓
PREDICTED

o:

UNASSESSED
    ↓
CONTESTED
    ↓
REFUTED

o:

SUPPORTED
    ↓
CONTESTED
    ↓
REVISED

El sistema debe permitir retrocesos.

⸻

102. Core object identifiers

Todos los objetos deben tener identificadores estables:

source_id
artifact_id
observation_id
measurement_id
event_id
testimony_id
claim_id
evidence_id
bundle_id
signal_id
hypothesis_id
prediction_id
scenario_id
alert_id
decision_id
outcome_id

⸻

103. Generic object envelope

Todos los objetos PUBLIC pueden compartir:

object:
  id:
  type:
  created_at:
  updated_at:
  observed_at:
  valid_from:
  valid_to:
  source_ids:
  provenance_ids:
  version:
  quality:
  uncertainty:
  sensitivity:
  access_class:
  status:

⸻

104. Example — verified institutional measurement

measurement:
  measurement_id: MEAS-001
  variable: emergency_department_wait_time
  value: 143
  unit: minutes
  observed_at: "2026-09-09T10:00:00+02:00"
  source_id: SRC-HOSPITAL-001
  method: administrative_record
  uncertainty:
    type: measurement
    value: known_methodological_range
  quality:
    status: HIGH
  provenance:
    artifact_id: ART-001

⸻

105. Example — citizen testimony

testimony:
  testimony_id: TEST-001
  event_time: "2026-09-09T08:30:00+02:00"
  statement: "He observado una espera excepcionalmente larga."
  observed_directly: true
  corroboration_status: UNASSESSED
  signal_value:
    type: POSSIBLE_EARLY_SIGNAL
  factual_status: UNVERIFIED
  publication_status: INTERNAL

No se transforma automáticamente en:

"las esperas son excepcionalmente largas"

⸻

106. Example — conflicting evidence

claim:
  claim_id: CLAIM-001
  statement: "La demanda asistencial ha aumentado."
evidence:
  - EVIDENCE-001
  - EVIDENCE-002
  - EVIDENCE-003
assessment:
  supporting:
    - EVIDENCE-001
    - EVIDENCE-002
  contradicting:
    - EVIDENCE-003
  status: CONTESTED
  uncertainty: MODERATE

La contradicción permanece visible.

⸻

107. Example — weak signal

signal:
  signal_id: SIG-001
  signal_type: RATE_SHIFT
  target_variable: emergency_demand
  detection_method: change_point_detection
  persistence: 6_hours
  uncertainty: MODERATE
  status: WEAK_SIGNAL

No genera automáticamente una alerta operacional.

Puede acumular evidencia posteriormente.

⸻

108. Example — cross-domain signal

signal:
  signal_id: SIG-002
  signal_type: CROSS_DOMAIN_SIGNAL
  components:
    - health_demand_increase
    - staff_fatigue_increase
    - waiting_time_increase
    - environmental_stress
  hypothesis:
    - increasing_systemic_pressure
  uncertainty: HIGH
  status: UNDER_REVIEW

La función de CeutIA es detectar la interacción, no declarar causalidad sin evidencia suficiente.

⸻

109. Example — prediction

prediction:
  prediction_id: PRED-001
  target: emergency_wait_time
  horizon: 24h
  probability:
    exceed_threshold: 0.72
  interval:
    lower: 90
    upper: 180
    unit: minutes
  model: state_space_model
  model_version: MODEL-2026-09
  generated_at: "2026-09-09T11:00:00+02:00"
  uncertainty: MODERATE

⸻

110. Example — complete lineage

SRC-001
  ↓
ART-001
  ↓
OBS-001
  ↓
MEAS-001
  ↓
CLAIM-001
  ↓
EVIDENCE-001
  ↓
SIG-001
  ↓
MODEL-001
  ↓
PRED-001
  ↓
ALERT-001

Cada paso debe ser auditable.

⸻

111. Minimum viable data architecture

La primera implementación no necesita construir inmediatamente todos los objetos avanzados.

Debe garantizar como mínimo:

Source
Artifact
Observation
Event
Claim
Evidence
Signal
Alert
Provenance
Timestamp
Quality
Uncertainty
Version

Estos constituyen el núcleo irreducible.

⸻

112. Evolution path

Posteriormente pueden añadirse:

Hypothesis
Prediction
Scenario
CausalGraph
NetworkState
Counterfactual
Outcome
Calibration
ModelComparison
PopulationAggregate
PrivacyPreservingAggregate

sin modificar el núcleo conceptual.

⸻

113. Relationship with CeutIA ontology

Este documento no sustituye:

docs/CeutIA_ONTOLOGY.md

La ontología define qué entidades y relaciones existen.

Este documento define cómo esas entidades se materializan operacionalmente como datos y evidencia.

ONTOLOGY
    ↓
semantic structure
DATA & EVIDENCE MODEL
    ↓
operational representation

⸻

114. Relationship with operational pipeline

Este documento tampoco sustituye:

docs/OPERATIONAL_PIPELINE.md

La relación es:

DATA & EVIDENCE MODEL
        ↓
defines objects and evidence semantics
OPERATIONAL PIPELINE
        ↓
defines processing sequence

⸻

115. Relationship with alert architecture

Las alertas utilizan este modelo como fundamento.

DATA
→ EVIDENCE
→ SIGNAL
→ ALERT

La lógica específica de severidad, urgencia, escalado, revisión y comunicación se define en:

docs/PUBLIC_ALERT_AND_ESCALATION_MODEL.md

⸻

116. Quality gates before alerting

Antes de permitir que una señal alimente una alerta crítica, debe verificarse:

[ ] provenance exists
[ ] timestamp valid
[ ] spatial context valid
[ ] source known
[ ] transformation traceable
[ ] uncertainty represented
[ ] dependencies evaluated
[ ] contradictions evaluated
[ ] baseline defined when appropriate
[ ] alternative explanations considered
[ ] data quality acceptable
[ ] model version known
[ ] human review requirements determined

⸻

117. Epistemic failure modes

CeutIA debe detectar explícitamente:

SOURCE COLLAPSE
DUPLICATE EVIDENCE
FALSE CORROBORATION
TEMPORAL LEAKAGE
SPATIAL LEAKAGE
DATA LEAKAGE
SELECTION BIAS
REPORTING BIAS
MEASUREMENT BIAS
SURVIVORSHIP BIAS
MISSINGNESS BIAS
CONFOUNDING
ECOLOGICAL FALLACY
PROXY DISCRIMINATION
MODEL DRIFT
CONCEPT DRIFT
DATA DRIFT
AUTOMATION BIAS
OVERCONFIDENCE
FALSE PRECISION
NARRATIVE LOCK-IN

⸻

118. Narrative lock-in

CeutIA debe evitar construir una explicación inicial y posteriormente reinterpretar todos los datos para confirmarla.

El sistema debe conservar:

alternative hypotheses
contradicting evidence
uncertainty
disconfirming observations

Una hipótesis debe poder perder.

⸻

119. Unknown state

CeutIA debe permitir explícitamente:

UNKNOWN

No debe forzar:

YES / NO

cuando la evidencia no permite determinarlo.

En determinados casos:

unknown

es la salida epistemológicamente correcta.

⸻

120. Knowledge boundary

Cada módulo debe poder declarar:

knowledge_boundary:
  known:
  uncertain:
  unknown:
  unsupported_inferences:

Esto impide que la interfaz produzca una falsa sensación de omnisciencia.

⸻

121. Final invariant

La arquitectura PUBLIC debe mantener siempre la siguiente separación:

WHAT WAS OBSERVED
        ≠
WHAT IS INFERRED
        ≠
WHAT IS SUSPECTED
        ≠
WHAT IS PREDICTED
        ≠
WHAT COULD HAPPEN
        ≠
WHAT SHOULD BE DONE

Esta separación constituye una propiedad fundamental de seguridad epistemológica de CeutIA.

⸻

122. Final architecture

El modelo completo puede resumirse como:

                    REAL WORLD
                        │
                        ▼
                     SOURCES
                        │
                        ▼
                  RAW ARTIFACTS
                        │
                        ▼
                   OBSERVATIONS
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
          MEASUREMENT  EVENT   TESTIMONY
              │         │         │
              └─────────┼─────────┘
                        ▼
                      CLAIMS
                        │
                ┌───────┴───────┐
                ▼               ▼
             SUPPORT         REFUTE
                │               │
                └───────┬───────┘
                        ▼
                     EVIDENCE
                        │
                        ▼
                  EVIDENCE BUNDLE
                        │
                        ▼
                      SIGNAL
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
        INFERENCE   HYPOTHESIS   MODEL
            │           │           │
            └───────────┼───────────┘
                        ▼
                 PREDICTION / SCENARIO
                        │
                        ▼
                      ALERT
                        │
                        ▼
                  HUMAN REVIEW
                        │
                        ▼
                     DECISION
                        │
                        ▼
                     OUTCOME
                        │
                        ▼
                RETROSPECTIVE
                 CALIBRATION
                        │
                        └──────────────→ LEARNING

⸻

123. Principio final

CeutIA no debe intentar convertir la complejidad del territorio en una colección de números aparentemente objetivos.

Debe construir una representación computable del conocimiento disponible, incluyendo sus límites.

La arquitectura correcta no es:

más datos
→ más certeza

sino:

mejor procedencia
+
mejor contextualización
+
mayor independencia
+
mejor corroboración
+
contradicciones explícitas
+
incertidumbre cuantificada
+
modelos adecuados
+
trazabilidad
→
mejor conocimiento operativo.

Y:

mejor conocimiento
≠
certeza absoluta

La finalidad de CeutIA es reducir la distancia entre lo que ocurre, lo que podemos observar, lo que creemos que ocurre y lo que finalmente decidimos hacer.

La arquitectura debe permitir detectar esa distancia antes de que se convierta en un error operacional.

⸻

124. Referencias metodológicas principales

1. World Health Organization. Early warning alert and response (EWAR) in emergencies: an operational guide. WHO; 2023.
2. World Health Organization. Early Warning, Alert and Response System (EWARS). WHO.
3. Tabassi E. Artificial Intelligence Risk Management Framework (AI RMF 1.0). NIST AI 100-1. National Institute of Standards and Technology; 2023. doi:10.6028/NIST.AI.100-1.
4. National Institute of Standards and Technology. AI Risk Management Framework Playbook. NIST.
5. Scheffer M, Carpenter SR, Lenton TM, Bascompte J, Brock W, Dakos V, et al. Anticipating critical transitions. Science. 2012;338(6105):344-348. doi:10.1126/science.1225244.
6. Guidi J, Lucente M, Sonino N, Fava GA. Allostatic load and its impact on health: a systematic review. Psychother Psychosom. 2021;90(1):11-27. doi:10.1159/000510696.
7. Christensen DS, Zachariae R, Amidi A, Wu LM. Sleep and allostatic load: a systematic review and meta-analysis. Sleep Med Rev. 2022;64:101650. doi:10.1016/j.smrv.2022.101650.
8. Lenart-Bugla M, Szcześniak D, Bugla B, Kowalski K, Niwa S, Rymaszewska J, et al. The association between allostatic load and brain: a systematic review. Psychoneuroendocrinology. 2022;145:105917. doi:10.1016/j.psyneuen.2022.105917.
9. Parker HW, Abreu AM, Sullivan MC, Vadiveloo M. Allostatic load and mortality: a systematic review and meta-analysis. Am J Prev Med. 2022;63(1):131-140. doi:10.1016/j.amepre.2022.02.003.

⸻

125. Architectural invariant

CeutIA debe conservar siempre la historia de cómo llegó a saber
lo que cree saber.

Si una salida no puede reconstruirse desde sus datos, evidencias,
transformaciones, modelos y supuestos, esa salida no posee trazabilidad
suficiente para una función crítica del sistema.