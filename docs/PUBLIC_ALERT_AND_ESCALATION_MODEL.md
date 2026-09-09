Sí. Lo haría como un documento nuclear de la arquitectura PUBLIC, no como un simple protocolo de alertas. Tiene que unir inteligencia epidemiológica, sistemas dinámicos, epistemología, detección temprana, apoyo sanitario/psicosocial, gestión de información, evaluación de riesgo y supervisión humana.

He incorporado evidencia de OMS/EWAR, NIST AI RMF, normativa europea de IA, literatura sobre transiciones críticas, carga alostática, sueño, migración y salud, evaluación del riesgo de violencia, comunicación de riesgos e infodemia. Por ejemplo, la OMS estructura EWAR precisamente alrededor de la detección temprana, evaluación y respuesta; NIST exige validez, seguridad, explicabilidad, privacidad, trazabilidad y gestión del sesgo; y el AI Act europeo establece límites especialmente relevantes para sistemas que pretendan inferir riesgo criminal de personas. 

El archivo quedaría así:

docs/PUBLIC_ALERT_AND_ESCALATION_MODEL.md

# CeutIA — PUBLIC ALERT AND ESCALATION MODEL
## Modelo de detección, evaluación, alerta, intervención preventiva y escalamiento humano
**Sistema:** CeutIA  
**Dominio:** PUBLIC  
**Estado:** Arquitectura normativa y epistemológica  
**Ámbito:** Crisis compleja de Ceuta  
**Propósito:** detección temprana, comprensión dinámica, prevención, apoyo a la población, reducción de escalada y generación de alertas cualificadas para interpretación humana.
---
# 1. Propósito
CeutIA PUBLIC debe ser capaz de observar un sistema complejo sometido a perturbaciones, identificar cambios relevantes respecto de su estado previo, integrar señales heterogéneas, evaluar su calidad epistemológica, detectar interacciones entre subsistemas y producir alertas explicables que puedan ser interpretadas por un humano cualificado.
El sistema no debe limitarse a detectar eventos.
Debe detectar:
- cambios de estado;
- cambios de trayectoria;
- cambios de velocidad;
- aceleraciones;
- persistencia;
- acumulación;
- pérdida de capacidad adaptativa;
- aparición de cuellos de botella;
- desacoplamientos;
- cambios de correlación;
- sincronización entre variables;
- anomalías;
- cambios de régimen;
- posibles transiciones críticas;
- propagación de perturbaciones;
- cascadas multisistémicas;
- señales de deterioro sanitario;
- señales de deterioro psicosocial;
- señales de saturación institucional;
- señales ambientales;
- señales informacionales;
- señales relacionadas con violencia o escalada;
- y combinaciones de las anteriores.
La unidad fundamental de análisis no será necesariamente el evento aislado.
Será:
> **estado + trayectoria + contexto + interacción + incertidumbre + capacidad de respuesta.**
---
# 2. Principio rector
CeutIA existe para ayudar a la población y contribuir a la contención de la crisis.
Ayudar a la población no significa ausencia de alertas.
En determinadas circunstancias, ayudar significa detectar precozmente una situación potencialmente peligrosa, facilitar una intervención preventiva, activar una revisión profesional o comunicar una alerta cualificada a la autoridad competente.
Por tanto:
```text
CeutIA
   ↓
observación
   ↓
detección de señales
   ↓
evaluación epistemológica
   ↓
corroboración / contradicción
   ↓
modelización dinámica
   ↓
alerta cualificada
   ↓
interpretación humana
   ↓
intervención apropiada
   ↓
evaluación del resultado

CeutIA no sustituye al profesional, al operador de emergencias, al médico, a los servicios sociales, a las autoridades ni a las fuerzas de seguridad.

La función de CeutIA es aumentar la capacidad humana de detectar, comprender y anticipar.

⸻

3. Objetivo de seguridad

El objetivo superior no es maximizar el número de alertas.

Es minimizar el daño esperado derivado de:

1. no detectar una señal relevante;
2. detectar tarde;
3. interpretar incorrectamente;
4. actuar sobre información falsa;
5. sobrerreaccionar ante una señal débil;
6. generar falsos positivos;
7. amplificar una amenaza mediante la propia comunicación;
8. estigmatizar a personas o colectivos;
9. producir automatización indebida de decisiones humanas;
10. revelar información personal innecesaria;
11. transformar una señal preventiva en una predicción determinista.

Por tanto:

Una alerta no es una conclusión. Es una solicitud estructurada de atención humana.

⸻

4. Fundamento científico

El modelo integra cinco familias de conocimiento:

4.1. Sistemas dinámicos y ciencia de la complejidad

El sistema territorial se representa como un sistema dinámico:

[
X_{t+1}=F(X_t,U_t,E_t,\Theta_t)+\epsilon_t
]

donde:

* (X_t): estado del sistema;
* (U_t): intervenciones;
* (E_t): perturbaciones externas;
* (\Theta_t): parámetros potencialmente variables;
* (\epsilon_t): incertidumbre y ruido.

La variable de interés no es únicamente (X_t).

También:

[
\frac{dX}{dt}
]

[
\frac{d^2X}{dt^2}
]

[
\Delta X
]

y, cuando sea relevante:

* persistencia;
* memoria;
* recuperación;
* variabilidad;
* autocorrelación;
* sincronización;
* dependencia entre subsistemas.

La literatura sobre transiciones críticas muestra que determinados sistemas pueden presentar cambios en propiedades dinámicas antes de una transición de régimen. Estas señales son probabilísticas, dependientes del contexto y no deben interpretarse como predictores deterministas. [REF-01]

4.2. Vigilancia y alerta temprana

El modelo sigue el principio de Early Warning, Alert and Response:

detección
→ verificación
→ evaluación
→ alerta
→ respuesta
→ reevaluación

La OMS establece EWAR como mecanismo para detectar eventos de forma temprana y permitir una respuesta más rápida durante emergencias. [REF-02]

4.3. Medicina de sistemas y carga alostática

La salud individual y colectiva puede deteriorarse cuando la exposición acumulada supera progresivamente la capacidad de adaptación.

La carga alostática constituye un marco útil para representar acumulación de estrés y adaptación fisiológica, aunque no debe convertirse en un diagnóstico automático ni en un índice único de salud. [REF-03]

La evidencia también relaciona alteraciones del sueño con mayor carga alostática y muestra asociaciones entre carga alostática elevada y cambios neurobiológicos, con heterogeneidad metodológica importante. [REF-04] [REF-05]

Por tanto:

exposición
+
estrés
+
alteración del sueño
+
incertidumbre
+
trauma
+
sobrecarga
+
pérdida de recuperación
        ↓
posible disminución de reserva adaptativa

CeutIA debe modelar esta trayectoria sin convertirla automáticamente en diagnóstico.

4.4. Inteligencia artificial fiable

El sistema adopta como principios técnicos:

* validez;
* fiabilidad;
* seguridad;
* resiliencia;
* trazabilidad;
* transparencia;
* explicabilidad;
* interpretabilidad;
* privacidad;
* equidad;
* gestión del sesgo.

Estos elementos son coherentes con NIST AI RMF. [REF-06]

4.5. Comunicación de riesgos

Una alerta mal comunicada puede convertirse en un amplificador de la propia crisis.

Por ello CeutIA debe distinguir:

inteligencia interna
≠
comunicación pública

La OMS considera la comunicación de riesgos y la participación comunitaria componentes esenciales de la respuesta ante emergencias. [REF-07] [REF-08]

⸻

5. Principio epistemológico fundamental

CeutIA nunca debe confundir:

dato
↓
observación
↓
testimonio
↓
señal
↓
inferencia
↓
hipótesis
↓
predicción
↓
escenario
↓
decisión

Cada elemento debe conservar su naturaleza.

5.1. Dato

Medición directa o registro estructurado.

Ejemplo:

ocupación hospitalaria = 82 %

5.2. Observación

Hecho registrado por una fuente.

5.3. Testimonio

Manifestación de una persona.

Un testimonio demuestra que una persona realizó una afirmación.

No demuestra automáticamente que el contenido de la afirmación sea cierto.

5.4. Señal

Patrón potencialmente relevante detectado en datos u observaciones.

5.5. Inferencia

Interpretación derivada de uno o varios datos.

5.6. Hipótesis

Explicación posible que compite con otras explicaciones.

5.7. Predicción

Estimación probabilística sobre un estado futuro.

5.8. Escenario

Configuración condicional:

si A y B persisten, C podría ocurrir bajo determinadas condiciones.

5.9. Decisión

Acto humano o institucional basado en información disponible.

CeutIA puede producir información para una decisión.

No debe convertir automáticamente una hipótesis en una decisión.

⸻

6. Separación entre persona y sistema

CeutIA contiene dos planos funcionales distintos.

Plano A — apoyo individual

PERSONA
   ↓
interacción voluntaria
   ↓
preguntas adaptativas
   ↓
identificación de necesidades
   ↓
información preventiva
   ↓
recursos
   ↓
recomendación de atención profesional cuando proceda

Plano B — inteligencia sistémica

fuentes públicas
+
datos agregados
+
señales territoriales
+
información institucional
+
señales comunitarias
+
datos sanitarios agregados cuando legalmente disponibles
        ↓
modelo dinámico
        ↓
alertas

Los dos planos pueden interactuar únicamente mediante mecanismos explícitos, legales y privacy-preserving.

La información individual no debe convertirse automáticamente en inteligencia de seguridad.

⸻

7. Principio de universalidad

CeutIA ayuda a todas las personas.

No existe una clasificación:

buen ciudadano
mal ciudadano
buen migrante
mal migrante
grupo peligroso
grupo seguro

Estas categorías no forman parte de la ontología de riesgo de CeutIA.

El sistema debe analizar:

* necesidades;
* exposición;
* comportamiento observable;
* contexto;
* síntomas declarados;
* señales ambientales;
* eventos;
* capacidad de respuesta;
* patrones agregados.

Nunca debe utilizar nacionalidad, origen étnico, religión, raza u otra característica protegida como sustituto de peligrosidad.

Migración no equivale a criminalidad.

Sufrimiento no equivale a peligrosidad.

Trauma no equivale a violencia.

Pertenencia a un grupo no equivale a conducta individual.

⸻

8. Riesgo de violencia

CeutIA puede detectar señales relacionadas con violencia, amenazas o escalada cuando existan indicadores objetivos, observables o reportados que justifiquen revisión.

Pero no debe construir:

[
P(\text{delito individual}|\text{nacionalidad})
]

ni:

[
P(\text{violencia}|\text{grupo})
]

ni sistemas equivalentes de perfilado.

La normativa europea de IA establece restricciones específicas sobre sistemas destinados a evaluar o predecir el riesgo de que una persona cometa un delito cuando dicha evaluación se basa exclusivamente en perfilado o características personales. [REF-09]

Además, la evidencia sobre herramientas de evaluación del riesgo de violencia muestra que su utilidad depende fuertemente de implementación, formación, adherencia y gestión profesional; no debe asumirse que una herramienta predictiva reduce por sí misma la violencia. [REF-10]

Por ello CeutIA utilizará el concepto:

señal de posible escalada

y no:

persona peligrosa.

⸻

9. Tipología de señales

Toda señal debe pertenecer a uno o varios dominios.

HEALTH

* demanda asistencial;
* saturación;
* síntomas agregados;
* infecciones;
* traumatología;
* urgencias;
* salud mental;
* sueño;
* fatiga;
* exposición ambiental;
* mortalidad;
* morbilidad.

PSYCHOSOCIAL

* estrés;
* ansiedad;
* miedo;
* irritabilidad;
* alteraciones del sueño;
* hipervigilancia;
* trauma;
* aislamiento;
* desesperanza;
* conflicto interpersonal;
* deterioro funcional.

VIOLENCE / ESCALATION

* amenazas verificables;
* violencia observada;
* concentración temporal de incidentes;
* escalada de gravedad;
* repetición;
* proximidad temporal;
* señales convergentes;
* cambios bruscos de comportamiento cuando exista evidencia válida;
* combinación de factores contextuales y eventos objetivos.

INFORMATION

* desinformación;
* narrativas falsas;
* rumores;
* información contradictoria;
* campañas coordinadas;
* aceleración anómala;
* manipulación;
* amplificación algorítmica;
* cambios en percepción colectiva.

ENVIRONMENT

* calor;
* contaminación;
* agua;
* calidad ambiental;
* ruido;
* hacinamiento;
* residuos;
* condiciones meteorológicas extremas.

INFRASTRUCTURE

* agua;
* electricidad;
* transporte;
* telecomunicaciones;
* hospitales;
* centros de atención;
* vivienda;
* logística.

INSTITUTIONAL

* saturación;
* tiempos de respuesta;
* absentismo;
* capacidad;
* recursos;
* acumulación de expedientes;
* interrupciones.

MIGRATION / HUMANITARIAN

Nunca se modelará como “amenaza”.

Se modelará mediante:

* flujos;
* velocidad;
* duración;
* distribución espacial;
* necesidades;
* alojamiento;
* acceso sanitario;
* condiciones higiénicas;
* vulnerabilidad;
* trauma;
* exposición;
* presión sobre servicios;
* capacidad de acogida;
* capacidad de respuesta.

MULTISYSTEM

Señales que aparecen simultáneamente en varios dominios.

Estas alertas tienen especial importancia porque pueden representar acoplamiento entre subsistemas.

⸻

10. El sistema debe detectar interacción

Una arquitectura basada únicamente en umbrales sería insuficiente.

Ejemplo:

ocupación hospitalaria ↑
+
tiempo de espera ↑
+
absentismo ↑
+
fatiga ↑
+
alteración del sueño ↑
+
incidentes ↑

Cada variable individual puede permanecer por debajo de un umbral.

La combinación puede representar una trayectoria peligrosa.

Por tanto:

[
Risk_t =
f(
State_t,
Velocity_t,
Acceleration_t,
Persistence_t,
Coupling_t,
Reserve_t,
Uncertainty_t
)
]

⸻

11. Estado, trayectoria y reserva

Para cada subsistema relevante se debe estimar:

Estado

¿Cómo está ahora?

Trayectoria

¿Hacia dónde se mueve?

Velocidad

¿A qué velocidad cambia?

Aceleración

¿El cambio se está acelerando?

Persistencia

¿El fenómeno desaparece o permanece?

Reserva

¿Cuánta capacidad de absorción queda?

Recuperación

¿El sistema vuelve al estado basal?

Acoplamiento

¿Otros subsistemas están respondiendo simultáneamente?

⸻

12. Capacidad

Debe diferenciarse:

[
C_{global}
\neq
C_{efectiva}
\neq
C_{accesible}
]

Una capacidad teórica puede ser muy superior a la capacidad realmente movilizable.

Ejemplo:

100 camas disponibles

no significa necesariamente:

100 camas operativas inmediatamente

Debe considerarse:

* personal;
* suministros;
* logística;
* tiempos;
* distribución;
* accesibilidad;
* saturación;
* capacidad de recuperación.

⸻

13. Pulsos y acumulación

CeutIA debe diferenciar:

1000 personas / 30 días

de:

1000 personas / 3 horas

Aunque el volumen acumulado sea idéntico, el sistema puede experimentar cargas radicalmente diferentes.

La variable relevante puede ser:

[
\lambda(t)
]

donde (\lambda) representa la tasa de llegada/demanda.

El sistema debe analizar:

[
\lambda(t) > \mu(t)
]

donde:

* (\lambda(t)): demanda;
* (\mu(t)): capacidad de servicio.

Si la demanda supera persistentemente la capacidad:

[
Q(t)\uparrow
]

y la cola puede crecer.

⸻

14. Señales tempranas de transición

El sistema puede monitorizar, cuando estadísticamente proceda:

* aumento de varianza;
* aumento de autocorrelación;
* aumento de persistencia;
* cambios de distribución;
* pérdida de recuperación;
* cambios en frecuencia de extremos;
* cambios de sincronización;
* cambios de conectividad de red.

Estas métricas deben considerarse señales probabilísticas.

Nunca:

autocorrelación ↑ → crisis inevitable

Sino:

autocorrelación ↑
+
otras señales
+
contexto
+
mecanismo plausible
+
corroboración
→
aumento de evidencia compatible con cambio de régimen

[REF-01]

⸻

15. Arquitectura de evidencia

Cada señal debe conservar:

evidence:
  source_id:
  source_type:
  timestamp:
  observation_time:
  publication_time:
  geographic_scope:
  data_quality:
  methodological_quality:
  independence:
  corroboration:
  contradiction:
  temporal_validity:
  provenance:
  uncertainty:

⸻

16. Independencia de las fuentes

El número de fuentes no equivale al número de evidencias independientes.

Cinco artículos que reproducen la misma agencia pueden constituir esencialmente una sola cadena informativa.

Por tanto:

[
EvidenceStrength
\neq
NumberOfSources
]

Debe estimarse:

[
EvidenceStrength =
f(
quality,
independence,
corroboration,
consistency,
recency,
directness
)
]

⸻

17. Contradicciones

CeutIA no debe eliminar automáticamente información contradictoria.

Debe conservarla.

Ejemplo:

Fuente A:
ocupación = 80 %
Fuente B:
ocupación = 62 %

El sistema debe producir:

CONTRADICTION DETECTED

y buscar:

* diferente hora;
* diferente definición;
* diferente población;
* diferente fuente;
* error;
* retraso;
* cambio real.

La contradicción puede ser informativa.

⸻

18. Hipótesis competidoras

Cuando exista una señal importante, CeutIA debe generar hipótesis alternativas cuando sea razonable.

Ejemplo:

H1: aumento real de demanda
H2: cambio en sistema de registro
H3: cambio de acceso
H4: evento localizado
H5: artefacto de medición

No debe seleccionar automáticamente una única explicación cuando varias permanecen plausibles.

⸻

19. Actualización bayesiana

Cuando sea apropiado:

[
P(H|E)

\frac{P(E|H)P(H)}
{P(E)}
]

La nueva evidencia actualiza la hipótesis.

No se debe asumir independencia entre evidencias cuando exista dependencia.

En consecuencia:

[
P(H|E_1,E_2,E_3)
]

no debe calcularse como si:

[
E_1,E_2,E_3
]

fueran independientes sin justificación.

⸻

20. Modelo de alerta

Cada alerta debe contener como mínimo:

alert:
  id:
  timestamp:
  domain:
  title:
  signal:
  observed:
  baseline:
  deviation:
  velocity:
  acceleration:
  persistence:
  spatial_scope:
  temporal_scope:
  affected_systems:
  coupling:
  evidence:
  corroboration:
  contradictions:
  alternative_hypotheses:
  uncertainty:
  confidence:
  potential_impact:
  urgency:
  severity:
  reversibility:
  reserve_estimate:
  recommended_verification:
  recommended_action:
  human_review_required:
  escalation_path:
  audit_trail:

⸻

21. Diferencia entre severidad y urgencia

No son equivalentes.

Severidad

Magnitud potencial del daño.

Urgencia

Tiempo disponible para actuar antes de que el coste esperado aumente significativamente.

Ejemplo:

Severidad alta
Urgencia baja

puede representar una tendencia crónica.

Mientras:

Severidad moderada
Urgencia extrema

puede representar una situación localizada que requiere respuesta inmediata.

⸻

22. Niveles de alerta

LEVEL 0 — INFORMATION

Información relevante sin señal de deterioro.

Acción:

registrar

LEVEL 1 — SIGNAL

Desviación detectada.

Acción:

monitorizar

LEVEL 2 — WATCH

Señales persistentes o convergentes.

Acción:

aumentar vigilancia
verificar fuentes

LEVEL 3 — WARNING

Evidencia suficiente de deterioro relevante o posible escalada.

Acción:

revisión humana prioritaria

LEVEL 4 — CRITICAL

Convergencia de señales con potencial de daño significativo y necesidad de actuación rápida.

Acción:

revisión humana inmediata

LEVEL 5 — EMERGENCY

Situación que puede requerir respuesta inmediata de servicios competentes.

Acción:

escalamiento humano inmediato

CeutIA no debe afirmar que una emergencia existe únicamente por superar una puntuación matemática.

Debe mostrar:

por qué
con qué evidencia
con qué incertidumbre
y qué necesita verificar el humano

⸻

23. Puntuación de alerta

No existe una única fórmula universal válida para todos los dominios.

Se utilizará una arquitectura modular.

Una representación conceptual:

[
A_t =
w_sS_t+
w_vV_t+
w_aA_t+
w_pP_t+
w_cC_t+
w_rR_t+
w_iI_t

w_uU_t

w_xX_t
]

donde:

* (S_t): magnitud del cambio;
* (V_t): velocidad;
* (A_t): aceleración;
* (P_t): persistencia;
* (C_t): acoplamiento;
* (R_t): relevancia/impacto;
* (I_t): independencia/corroboración;
* (U_t): incertidumbre;
* (X_t): contradicción.

Esta fórmula es un marco conceptual.

Los pesos deben aprenderse, validarse o definirse por dominio y posteriormente calibrarse.

Nunca debe presentarse como una ley universal.

⸻

24. Riesgo esperado

Cuando exista suficiente información:

[
ExpectedLoss =
P(Event)\times Severity(Event)\times Exposure(Event)
]

y, cuando sea posible:

[
NetRisk =
ExpectedLoss

ExpectedBenefitOfIntervention
]

Esto permite comparar:

no intervenir

frente a:

verificar

frente a:

intervenir preventivamente

frente a:

escalar

La decisión final corresponde al humano competente.

⸻

25. Falsos positivos y falsos negativos

El sistema debe optimizar una función de coste, no simplemente accuracy.

[
Cost =
C_{FP}FP+C_{FN}FN
]

Los costes dependen del dominio.

En determinados escenarios:

[
C_{FN} \gg C_{FP}
]

pero en otros:

[
C_{FP} \gg C_{FN}
]

Por ejemplo, una alerta sanitaria de baja gravedad puede tolerar un umbral diferente al de una comunicación pública capaz de generar pánico.

⸻

26. Calibración

Las probabilidades deben evaluarse retrospectivamente.

Si CeutIA asigna:

P(evento)=0.80

aproximadamente el 80 % de casos comparables deberían producir el evento dentro del horizonte definido, si el sistema está calibrado.

Deben monitorizarse:

* Brier score;
* calibration curves;
* expected calibration error;
* sensibilidad;
* especificidad;
* PPV;
* NPV;
* ROC-AUC cuando proceda;
* PR-AUC en eventos raros;
* lead time;
* false alarm rate;
* missed-event rate.

No se debe optimizar AUC ignorando la utilidad operacional.

⸻

27. Evaluación temporal

Cada alerta debe poder responder:

¿Cuánto antes detectó CeutIA la señal respecto del evento?

Debe medirse:

[
LeadTime =
T_{event}-T_{alert}
]

Pero el lead time no debe considerarse positivo si se consiguió mediante un exceso de falsos positivos.

La métrica adecuada es:

detección temprana
+
calibración
+
especificidad
+
utilidad operacional

⸻

28. Aprendizaje retrospectivo

Después de cada evento relevante:

ALERTA
↓
DECISIÓN HUMANA
↓
EVENTO REAL
↓
RESULTADO
↓
COMPARACIÓN
↓
ERROR
↓
ACTUALIZACIÓN

Debe existir un:

POST-EVENT REVIEW

que analice:

* qué detectó;
* qué no detectó;
* qué interpretó mal;
* qué información faltaba;
* qué fuente era incorrecta;
* qué hipótesis resultó falsa;
* qué hipótesis quedó corroborada;
* qué intervención funcionó;
* qué intervención produjo efectos no deseados.

⸻

29. Salud individual: interacción adaptativa

La capa de apoyo sanitario no debe realizar un cuestionario fijo de todas las enfermedades.

Debe ser adaptativa.

Ejemplo:

Pregunta inicial
      ↓
respuesta
      ↓
selección de siguiente pregunta
      ↓
nueva respuesta
      ↓
actualización del perfil de necesidades
      ↓
siguiente pregunta

Áreas potenciales:

* sueño;
* recuperación;
* estrés;
* ansiedad;
* miedo;
* irritabilidad;
* estado de ánimo;
* concentración;
* hipervigilancia;
* pesadillas;
* recuerdos intrusivos;
* síntomas respiratorios;
* fiebre;
* síntomas gastrointestinales;
* síntomas cutáneos;
* dolor;
* traumatismos;
* agotamiento;
* exposición ambiental;
* condiciones de alojamiento;
* higiene;
* acceso sanitario;
* exposición a violencia;
* trauma;
* aislamiento;
* seguridad percibida.

No deben preguntarse todas a todas las personas.

⸻

30. Motor adaptativo de entrevista

Cada pregunta debe maximizar:

[
InformationGain
]

sujeto a:

carga cognitiva
+
privacidad
+
relevancia clínica
+
seguridad

El sistema debe detener el interrogatorio cuando la información adicional tenga utilidad marginal baja.

⸻

31. Función de la interacción sanitaria

La interacción sanitaria tiene cuatro objetivos:

1. prevención;
2. identificación temprana de necesidades;
3. orientación hacia recursos;
4. derivación cuando exista necesidad profesional.

No debe realizar automáticamente:

* diagnóstico;
* prescripción;
* clasificación psiquiátrica definitiva;
* predicción criminal;
* determinación de peligrosidad;
* decisión médica irreversible.

⸻

32. Violencia y de-escalada

Cuando una persona manifieste:

* miedo;
* rabia;
* desesperación;
* pensamientos violentos;
* exposición a violencia;
* intención de dañar;
* amenazas;
* conflicto intenso;

CeutIA debe priorizar la pregunta:

¿Qué intervención puede reducir la probabilidad de escalada?

Las posibles respuestas pueden incluir:

* regulación emocional;
* información fiable;
* reducción de incertidumbre;
* apoyo psicológico;
* contacto con servicios profesionales;
* mediación;
* protección;
* servicios de emergencia;
* recursos comunitarios;
* comunicación con autoridades cuando exista fundamento suficiente y proceda legalmente.

La expresión de una emoción violenta no equivale por sí sola a una amenaza creíble.

Una amenaza explícita y contextualizada puede requerir otro nivel de evaluación.

⸻

33. Contenido violento

El contenido violento debe diferenciar:

contenido
valor epistemológico
riesgo
visibilidad pública

No son la misma variable.

Ejemplo:

vídeo violento

demuestra:

existencia del vídeo

pero no necesariamente:

lugar
fecha
autor
motivación
veracidad del relato asociado

El contenido puede ser almacenado y analizado para extraer señales sin ser amplificado públicamente.

⸻

34. Testimonios ciudadanos

Un vecino puede proporcionar información extraordinariamente temprana.

Por tanto:

testimonio ciudadano ≠ hecho confirmado

pero:

testimonio ciudadano ≠ información inútil

Debe registrarse como:

citizen_report

con:

* timestamp;
* localización aproximada;
* contenido;
* fuente;
* nivel de detalle;
* posible conflicto de interés;
* corroboración;
* contradicciones;
* repetición independiente.

Varios testimonios independientes pueden constituir una señal de alto valor aunque todavía no permitan afirmar el hecho.

⸻

35. Información de redes sociales

Las redes sociales pueden proporcionar:

* señales tempranas;
* cambios de percepción;
* emociones;
* movilización;
* rumores;
* coordinación;
* narrativas;
* desinformación;
* aceleración de mensajes.

Pero:

[
viralidad \neq veracidad
]

Una publicación viral no debe recibir mayor credibilidad simplemente por ser viral.

⸻

36. Desinformación

La detección debe distinguir:

falso
engañoso
inexacto
no verificable
fuera de contexto
satírico
opinión
testimonio
afirmación factual

La salida pública debe evitar amplificar innecesariamente el contenido dañino.

Debe priorizar:

hecho verificable
+
contexto
+
incertidumbre
+
fuente
+
qué sabemos
+
qué no sabemos
+
qué hacer

La comunicación de riesgo debe buscar información temprana, comprensible y fiable para permitir decisiones informadas. [REF-07]

⸻

37. Migración y salud

CeutIA puede incorporar migración como determinante contextual cuando sea científicamente pertinente.

Debe analizar variables como:

* exposición;
* condiciones de alojamiento;
* acceso sanitario;
* hacinamiento;
* higiene;
* continuidad asistencial;
* trauma;
* condiciones laborales;
* barreras lingüísticas;
* vulnerabilidad social.

La evidencia reciente muestra que los patrones de riesgo sanitario asociados con migración están mediados por múltiples factores contextuales y estructurales, y presentan heterogeneidad importante entre regiones. [REF-11]

Por tanto:

migración
→ contexto
→ exposición
→ necesidad

no:

migración
→ peligrosidad

⸻

38. Geografía

Cuando sea posible, toda señal debe tener una dimensión espacial.

Pero la precisión espacial debe ser proporcional al objetivo.

Debe evitarse almacenar una localización individual exacta cuando:

zona

sea suficiente.

Se priorizará:

agregación espacial
+
minimización de datos

⸻

39. Tiempo

Cada observación debe conservar al menos:

event_time
publication_time
ingestion_time

Porque:

[
event\ time
\neq
publication\ time
\neq
ingestion\ time
]

La latencia informativa forma parte de la evaluación de calidad.

⸻

40. Calidad temporal

Una fuente puede ser:

* muy fiable pero antigua;
* reciente pero poco fiable;
* fiable y reciente;
* contradictoria;
* válida para tendencia pero no para situación actual.

Por tanto:

[
SourceQuality=f(
authority,
methodology,
independence,
recency,
directness
)
]

⸻

41. Arquitectura de fuentes

Tier 1 — fuentes primarias oficiales

* INE;
* Ministerio de Sanidad;
* Ministerio del Interior;
* servicios sanitarios;
* organismos oficiales;
* protección civil;
* AEMET;
* instituciones europeas;
* resoluciones judiciales;
* estadísticas administrativas;
* organismos internacionales oficiales.

Tier 2 — literatura científica

* PubMed/MEDLINE;
* revisiones sistemáticas;
* metaanálisis;
* estudios epidemiológicos;
* estudios de sistemas complejos;
* literatura metodológica.

Tier 3 — organismos científicos y profesionales

* OMS;
* ECDC;
* Naciones Unidas;
* UNHCR;
* IOM;
* sociedades científicas;
* universidades.

Tier 4 — medios profesionales

Útiles especialmente para eventos recientes.

Requieren:

* evaluación de fuente;
* fecha;
* independencia;
* corroboración.

Tier 5 — redes sociales

Señal, no evidencia factual automática.

Tier 6 — testimonios

Señal humana potencialmente valiosa que requiere clasificación epistemológica.

⸻

42. Prohibición de consenso falso

No debe utilizarse:

10 fuentes repiten X

como prueba independiente de X cuando las 10 dependen de la misma fuente original.

Debe reconstruirse el grafo de procedencia:

FUENTE ORIGINAL
      ↓
MEDIO A
MEDIO B
RED C
BLOG D
      ↓
10 publicaciones

y tratarse como una cadena dependiente.

⸻

43. Grafo de procedencia

Toda afirmación importante debe poder representarse:

CLAIM
 ↓
SOURCE
 ↓
OBSERVATION
 ↓
TRANSFORMATION
 ↓
MODEL
 ↓
ALERT
 ↓
HUMAN INTERPRETATION
 ↓
ACTION

Esto permite auditoría completa.

⸻

44. Explicabilidad de las alertas

Toda alerta debe responder:

WHAT?

¿Qué se ha detectado?

WHEN?

¿Cuándo?

WHERE?

¿Dónde?

MAGNITUDE?

¿Cuánto?

VELOCITY?

¿A qué velocidad cambia?

PERSISTENCE?

¿Desde cuándo?

WHY?

¿Por qué es relevante?

EVIDENCE?

¿Qué evidencia existe?

INDEPENDENCE?

¿Las fuentes son independientes?

CONTRADICTION?

¿Qué información contradice la señal?

UNCERTAINTY?

¿Qué no sabemos?

ALTERNATIVES?

¿Qué explicaciones alternativas existen?

IMPACT?

¿Qué podría ocurrir?

ACTION?

¿Qué debe comprobar el humano?

⸻

45. Alertas multisistémicas

Una de las funciones principales de CeutIA será detectar:

[
Health
\leftrightarrow
Psychosocial
\leftrightarrow
Information
\leftrightarrow
Infrastructure
\leftrightarrow
Institutional
\leftrightarrow
Environmental
]

Ejemplo:

perturbación externa
        ↓
aumento de demanda
        ↓
sobrecarga institucional
        ↓
fatiga
        ↓
alteración del sueño
        ↓
irritabilidad
        ↓
conflicto
        ↓
más incidentes
        ↓
más percepción de amenaza
        ↓
más vigilancia
        ↓
más detección de incidentes
        ↓
mayor percepción de crisis

El sistema debe buscar estos bucles.

⸻

46. Información como variable dinámica

La información no es únicamente una representación del sistema.

Puede modificarlo.

[
Information
\rightarrow
Perception
\rightarrow
Behaviour
\rightarrow
System
\rightarrow
NewInformation
]

Por ello CeutIA debe modelar:

evento
+
interpretación
+
comunicación
+
respuesta social

como un sistema acoplado.

⸻

47. Bucles de retroalimentación

Deben identificarse:

Positive feedback

Amplifica una perturbación.

Negative feedback

Compensa una perturbación.

Delayed feedback

Produce respuesta retardada.

Perverse feedback

La intervención produce una consecuencia opuesta a la deseada.

Observation feedback

La propia vigilancia modifica el fenómeno observado.

⸻

48. Vigilancia y paradoja de observación

Un aumento de vigilancia puede incrementar la detección.

Por tanto:

[
ObservedIncidents \uparrow
]

no implica automáticamente:

[
TrueIncidence \uparrow
]

Debe considerarse:

[
Observed =
TrueIncidence
\times
DetectionProbability
]

Cuando cambie la probabilidad de detección, CeutIA debe evitar interpretar el cambio observado como cambio real sin corrección.

⸻

49. Cuello de botella

CeutIA debe intentar identificar:

¿Qué subsistema limita actualmente la capacidad global?

Puede utilizar:

queueing theory
+
network analysis
+
capacity modelling
+
flow analysis

El objetivo no es únicamente contar recursos.

Es identificar:

primer cuello de botella

y:

duración sostenible

⸻

50. Cascadas

Una cascada puede representarse:

[
A \rightarrow B \rightarrow C \rightarrow D
]

pero también:

[
A \leftrightarrow B
]

y:

[
A+B \rightarrow C
]

Por ello CeutIA debe detectar interacciones no lineales.

⸻

51. Reserva adaptativa

La capacidad de respuesta debe considerarse una variable dinámica.

Conceptualmente:

[
Reserve_{t+1}

Reserve_t
+
Recovery_t

Load_t

Shock_t
]

Si:

[
Load_t > Recovery_t
]

durante tiempo suficiente:

[
Reserve_t \downarrow
]

Esto puede preceder a deterioro sistémico.

⸻

52. Umbral

No todos los sistemas tienen un único umbral.

Puede existir:

* umbral temporal;
* umbral espacial;
* umbral de capacidad;
* umbral de saturación;
* umbral de coordinación;
* umbral psicológico;
* umbral epidemiológico;
* umbral de información.

Por ello CeutIA debe representar:

[
Threshold=f(context,time,state)
]

⸻

53. Histeresis

El estado de un sistema puede depender de su trayectoria previa.

Por tanto:

[
X_t
]

no siempre determina por sí solo:

[
X_{t+1}
]

Debe considerarse:

[
History(X_{0:t})
]

Un sistema sometido a una carga prolongada puede responder de manera distinta a un sistema que recibe la misma perturbación partiendo de una situación estable.

⸻

54. No equivalencia entre magnitudes iguales

El sistema debe evitar comparar cantidades sin contexto.

Ejemplo:

1000 personas

puede representar:

* 1000 personas durante 30 días;
* 1000 personas durante 3 horas;
* 1000 personas distribuidas territorialmente;
* 1000 personas concentradas;
* 1000 personas con alta necesidad;
* 1000 personas con baja necesidad.

La cantidad absoluta no es suficiente.

⸻

55. Escalamiento

La cadena estándar será:

CeutIA
   ↓
signal
   ↓
qualified alert
   ↓
human review
   ↓
interpretation
   ↓
decision
   ↓
competent authority when appropriate

Nunca:

CeutIA
   ↓
automated accusation

ni:

CeutIA
   ↓
automated police action

⸻

56. Condiciones para escalar

Una alerta puede requerir escalamiento cuando exista una combinación suficiente de:

impact
+
credibility
+
proximity
+
urgency
+
corroboration

y la incertidumbre residual sea compatible con la acción propuesta.

La severidad por sí sola no debe determinar el escalamiento.

⸻

57. Principio de proporcionalidad

La acción recomendada debe ser proporcional a:

[
ExpectedHarm
]

y:

[
EvidenceStrength
]

Una señal débil no debe justificar una intervención desproporcionada.

Una amenaza creíble y urgente no debe ser ignorada simplemente porque exista incertidumbre.

⸻

58. Principio de mínima intervención

Cuando varias acciones produzcan beneficios similares, CeutIA debe favorecer la intervención menos intrusiva compatible con la seguridad.

Ejemplo:

informar
<
verificar
<
contactar servicio competente
<
intervención urgente

El sistema debe recomendar la acción mínima suficiente, no la máxima disponible.

⸻

59. Derechos y dignidad

El diseño debe preservar:

* dignidad;
* autonomía;
* privacidad;
* igualdad;
* no discriminación;
* debido proceso;
* seguridad;
* proporcionalidad.

La OMS sitúa dignidad, autonomía, privacidad, transparencia, supervisión y derechos humanos en el centro de la gobernanza de IA sanitaria. [REF-12]

⸻

60. Privacidad

Principios:

data minimization
purpose limitation
least privilege
retention limitation
pseudonymization
aggregation
access control
audit logging

No debe recogerse información personal simplemente porque técnicamente pueda recogerse.

⸻

61. Separación de datos

Debe existir separación lógica y técnica entre:

PERSON SUPPORT DATA

y:

SYSTEM INTELLIGENCE DATA

La transferencia entre ambos dominios debe ser:

* explícita;
* minimizada;
* jurídicamente justificada;
* agregada cuando sea posible;
* auditada.

⸻

62. Regla de agregación

Una persona no debe convertirse automáticamente en sensor del sistema.

El paso:

individual → system signal

requiere reglas específicas.

Ejemplo:

1 persona con ansiedad

no implica:

crisis de salud mental territorial

Mientras:

aumento consistente de múltiples indicadores
+
muestras independientes
+
persistencia

puede constituir señal poblacional.

⸻

63. Confidencialidad diferencial

Cuando sea necesario, pueden emplearse técnicas de privacidad estadística, incluyendo:

* agregación;
* supresión de celdas pequeñas;
* k-anonymity cuando sea adecuada;
* differential privacy cuando sea técnicamente apropiada;
* perturbación controlada;
* minimización de granularidad.

La técnica debe elegirse según el riesgo de reidentificación y la utilidad analítica.

⸻

64. Seguridad del sistema

CeutIA debe asumir:

adversarial inputs
data poisoning
prompt injection
source manipulation
coordinated misinformation
account compromise
data exfiltration
model manipulation

Las fuentes externas nunca deben poder modificar directamente las reglas de decisión del sistema.

⸻

65. Separación de ingestión y decisión

Arquitectura:

EXTERNAL DATA
      ↓
INGESTION
      ↓
SANITIZATION
      ↓
PROVENANCE
      ↓
CLASSIFICATION
      ↓
VALIDATION
      ↓
ANALYTICS
      ↓
ALERT ENGINE

Nunca:

external text
→ direct system action

⸻

66. LLMs

Los modelos generativos pueden:

* resumir;
* clasificar;
* explicar;
* extraer entidades;
* detectar contradicciones;
* formular hipótesis;
* asistir al operador.

No deben ser la única fuente de verdad.

Toda afirmación generada debe mantener:

source
provenance
uncertainty
epistemic status

La OMS advierte sobre errores plausibles, sesgos, privacidad, ciberseguridad y automation bias en sistemas de IA generativa sanitaria. [REF-12] [REF-13]

⸻

67. Automation bias

El operador debe poder rechazar una alerta.

La interfaz debe mostrar:

CeutIA sugiere:
X
Confianza:
Y
Evidencia:
Z
Contradicciones:
N
Hipótesis alternativas:
...
Decisión humana:
[aceptar]
[rechazar]
[modificar]
[requiere más evidencia]

Nunca:

AI says danger → danger

⸻

68. Auditoría humana

Toda alerta de LEVEL 3 o superior debe generar:

human_review

El registro debe conservar:

* operador;
* fecha;
* interpretación;
* decisión;
* evidencia utilizada;
* modificación;
* escalamiento;
* resultado.

⸻

69. Derecho a la discrepancia

El humano puede discrepar de CeutIA.

El sistema debe registrar:

AI recommendation
≠
human decision

La discrepancia no debe considerarse automáticamente error humano.

Puede revelar:

* fallo del modelo;
* información ausente;
* contexto no modelado;
* cambio de régimen;
* error de datos.

⸻

70. Modo desconocido

CeutIA debe poder decir:

NO HAY INFORMACIÓN SUFICIENTE.

También:

EVIDENCIA CONTRADICTORIA.

Y:

MODELO FUERA DE DOMINIO.

Estas salidas son comportamientos correctos.

⸻

71. Prohibición de falsa precisión

No debe mostrar:

87.31 % de riesgo

si la evidencia solo permite:

baja / moderada / alta incertidumbre

La precisión numérica debe estar respaldada por calibración.

⸻

72. Incertidumbre

Toda alerta debe incluir:

[
Uncertainty
]

y, cuando sea posible:

[
CI
]

o distribución posterior.

Debe diferenciarse:

uncertainty from data
uncertainty from model
uncertainty from source
uncertainty from future

⸻

73. Robustez

Una alerta importante debe someterse, cuando sea posible, a:

* sensibilidad;
* análisis de escenarios;
* perturbación de datos;
* eliminación de fuentes;
* análisis leave-one-source-out;
* bootstrap;
* Monte Carlo;
* comparación de modelos.

Si una alerta desaparece al eliminar una única fuente:

single-source dependency = HIGH

⸻

74. Independencia estructural

La fuerza de una alerta aumenta cuando persiste después de retirar fuentes dependientes.

Conceptualmente:

[
Robustness =
P(Alert\ persists\ |\ source\ removal)
]

No es una fórmula obligatoria de producción, sino un principio de robustez.

⸻

75. Señales débiles

Una señal débil puede ser relevante si:

nueva
+
persistente
+
independiente
+
mecánicamente plausible
+
convergente

No debe descartarse por baja magnitud inicial.

Pero tampoco debe elevarse a alerta crítica sin evidencia suficiente.

⸻

76. Cambio de régimen

CeutIA debe distinguir:

anomalía transitoria

de:

cambio estructural

Debe evaluar:

* duración;
* reversibilidad;
* cambio de distribución;
* cambio de correlaciones;
* cambio de parámetros;
* recuperación.

⸻

77. Cascada multisistémica

Cuando se detecte:

A ↑
B ↑
C ↓
D ↑
E ↑

CeutIA debe buscar si existe:

[
A \rightarrow B \rightarrow C \rightarrow D
]

o:

[
A+B \rightarrow D
]

o:

[
D \rightarrow A
]

La causalidad nunca debe inferirse únicamente por correlación.

⸻

78. Causalidad

CeutIA debe diferenciar:

correlación

de:

causalidad

y:

precedencia temporal

de:

causalidad demostrada

Las narrativas causales deben estar respaldadas por:

* literatura;
* diseños causales;
* mecanismos plausibles;
* temporalidad;
* control de confusión;
* evidencia convergente.

⸻

79. Hipótesis causales

Cuando exista una hipótesis causal:

causal_hypothesis:
  exposure:
  outcome:
  mechanism:
  temporal_order:
  confounders:
  supporting_evidence:
  contradictory_evidence:
  causal_strength:
  falsification_conditions:

⸻

80. Falsabilidad

Toda hipótesis relevante debe indicar:

¿Qué observación haría disminuir significativamente su plausibilidad?

Si ninguna observación puede refutarla:

UNFALSIFIABLE

y no debe utilizarse como hipótesis científica operacional.

⸻

81. Predicciones prospectivas

CeutIA debe generar predicciones registradas antes de conocer el resultado.

prediction:
  created_at:
  horizon:
  target:
  probability:
  uncertainty:
  assumptions:
  evidence:

Posteriormente:

prediction
→ outcome
→ calibration
→ learning

Esto permite evaluar si CeutIA realmente anticipa o simplemente explica retrospectivamente.

⸻

82. Escenarios

Debe existir:

Baseline

Qué ocurre si continúa la trayectoria actual.

Optimistic

Qué ocurre si las capacidades de recuperación mejoran.

Adverse

Qué ocurre si la presión aumenta.

Cascade

Qué ocurre si se activa un acoplamiento entre subsistemas.

Shock

Qué ocurre ante una perturbación exógena.

Los escenarios no son predicciones.

⸻

83. Intervención y contrafactual

Cuando exista información suficiente:

[
Y(1)-Y(0)
]

puede representar el efecto potencial de una intervención frente a no intervenir.

CeutIA no debe afirmar causalidad contrafactual sin un diseño adecuado.

Puede, sin embargo, presentar:

possible intervention effect

como escenario modelizado.

⸻

84. Evaluación de intervención

Toda intervención relevante debería generar:

pre-intervention state
→ intervention
→ expected effect
→ observed effect
→ unintended effect
→ update

Esto convierte CeutIA en un sistema de aprendizaje.

⸻

85. Bucles de aprendizaje

Arquitectura completa:

OBSERVE
   ↓
MODEL
   ↓
DETECT
   ↓
ALERT
   ↓
HUMAN INTERPRET
   ↓
INTERVENE
   ↓
OBSERVE RESULT
   ↓
CALIBRATE
   ↓
UPDATE

⸻

86. Prevención sanitaria

El sistema puede proporcionar información sobre:

* sueño;
* recuperación;
* estrés;
* actividad física;
* alimentación;
* hidratación;
* exposición ambiental;
* salud respiratoria;
* salud mental;
* recursos sanitarios;
* prevención de infecciones;
* reducción de riesgos.

Debe utilizar lenguaje:

preventivo
probabilístico
no diagnóstico

⸻

87. Derivación profesional

CeutIA debe recomendar atención profesional cuando existan:

* síntomas potencialmente graves;
* deterioro funcional;
* riesgo de autolesión;
* riesgo de violencia;
* síntomas persistentes;
* signos de emergencia;
* necesidad de evaluación clínica.

Cuando exista riesgo inmediato, la interfaz debe priorizar servicios de emergencia apropiados.

⸻

88. No sustitución

CeutIA no debe presentarse como:

médico
psiquiatra
policía
juez
trabajador social
autoridad pública

Puede actuar como:

sistema de apoyo

y:

sistema de inteligencia

bajo supervisión humana.

⸻

89. Intervención de bajo riesgo

Cuando exista incertidumbre elevada y bajo riesgo inmediato:

información
+
apoyo
+
observación

puede ser preferible a:

escalamiento

siempre que sea seguro.

⸻

90. Principio de reversibilidad

Entre dos acciones con beneficio esperado similar:

[
prefer\ action\ with\ greater\ reversibility
]

Una acción reversible permite corregir errores.

Una acción irreversible exige mayor evidencia y supervisión.

⸻

91. Matriz de decisión

Evidencia	Impacto	Urgencia	Acción
baja	baja	baja	monitorizar
moderada	baja	baja	verificar
moderada	moderada	moderada	revisión humana
alta	moderada	alta	revisión prioritaria
alta	alta	alta	escalamiento
contradictoria	alta	alta	verificación urgente
desconocida	alta	alta	no automatizar decisión

⸻

92. Estructura mínima de una alerta

ALERTA CEUTIA
ID:
Fecha:
Dominio:
Nivel:
QUÉ:
Qué se ha detectado.
CUÁNDO:
Ventana temporal.
DÓNDE:
Área afectada.
MAGNITUD:
Valor actual.
BASELINE:
Valor esperado.
CAMBIO:
ΔX
VELOCIDAD:
dX/dt
PERSISTENCIA:
Duración.
INTERACCIONES:
Otros subsistemas afectados.
EVIDENCIA:
Fuentes.
INDEPENDENCIA:
Baja / media / alta.
CORROBORACIÓN:
Baja / media / alta.
CONTRADICCIONES:
Sí / no.
HIPÓTESIS:
H1
H2
H3
INCERTIDUMBRE:
Baja / media / alta.
IMPACTO POTENCIAL:
Bajo / medio / alto / crítico.
URGENCIA:
Baja / media / alta / inmediata.
QUÉ DEBE COMPROBAR EL HUMANO:
ACCIÓN SUGERIDA:
ESCALAMIENTO:
Sí / no.
LIMITACIONES:
...

⸻

93. Alertas para seguridad

Cuando una señal pueda tener relevancia para seguridad:

CeutIA
→ alerta estructurada
→ revisión humana
→ valoración
→ autoridad competente cuando proceda

La alerta debe distinguir claramente:

HECHO OBSERVADO

de:

INFERENCIA

de:

HIPÓTESIS

de:

RIESGO POTENCIAL

No debe emitir acusaciones.

No debe declarar culpabilidad.

No debe determinar peligrosidad jurídica.

No debe sustituir la investigación policial.

⸻

94. Ejemplo correcto

SEÑAL DETECTADA:
Durante las últimas 3 horas se han registrado
7 incidentes independientes en una misma zona.
Corroboración:
moderada-alta.
Cambio respecto al baseline:
+340 %.
Persistencia:
3 horas.
Fuentes:
5 independientes.
Contradicciones:
1.
Hipótesis:
H1 — aumento real de incidentes.
H2 — aumento de detección.
H3 — concentración temporal excepcional.
Recomendación:
verificación humana prioritaria.

No:

La zona es peligrosa.

⸻

95. Ejemplo incorrecto

El grupo X tiene alta probabilidad de violencia.

Motivo de rechazo:

* generalización;
* ausencia de evidencia individual;
* posible discriminación;
* falta de mecanismo;
* confusión entre grupo y persona;
* riesgo de perfilado.

⸻

96. Protección contra estigmatización

El sistema debe impedir inferencias automáticas del tipo:

nacionalidad → peligrosidad
religión → violencia
raza → riesgo
estatus migratorio → criminalidad
pobreza → peligrosidad
trauma → violencia
enfermedad mental → criminalidad

Las características contextuales pueden modificar necesidades de apoyo.

No deben convertirse automáticamente en etiquetas de riesgo criminal.

⸻

97. Diseño de la interfaz pública

La interfaz pública debe mostrar:

qué sabemos
qué no sabemos
qué está cambiando
qué significa
qué puede hacer la persona
dónde obtener ayuda

No debe mostrar:

listas de sospechosos
perfiles individuales
predicciones criminales
información personal sensible
contenido violento innecesario

⸻

98. Diseño de la interfaz del operador

El operador debe ver:

estado actual
+
trayectoria
+
mapa
+
timeline
+
alertas
+
fuentes
+
procedencia
+
contradicciones
+
hipótesis
+
incertidumbre
+
capacidad
+
escenarios

La interfaz debe permitir navegar:

alerta
→ evidencia
→ fuente
→ dato original
→ transformación
→ modelo

⸻

99. Registro de auditoría

Cada transformación debe generar:

audit:
  actor:
  timestamp:
  action:
  input:
  output:
  model_version:
  data_version:
  reason:

Debe ser posible reconstruir posteriormente:

por qué CeutIA generó una alerta determinada.

⸻

100. Versionado

Toda alerta debe estar vinculada a:

data_version
model_version
rules_version
source_version
ontology_version

Una alerta histórica no debe cambiar silenciosamente cuando se actualice el modelo.

⸻

101. Reproducibilidad

Debe ser posible reproducir:

input
+
model
+
parameters
+
rules
=
output

Cuando exista aleatoriedad:

random seed

debe registrarse cuando sea necesario para auditoría.

⸻

102. Deriva del modelo

Debe monitorizarse:

data drift
concept drift
label drift
performance drift
calibration drift

Un modelo que funcionaba durante una fase de la crisis puede dejar de funcionar cuando cambia el régimen.

⸻

103. Cambio de régimen

Si:

performance ↓

o:

calibration ↓

CeutIA debe poder reducir automáticamente la confianza de sus predicciones.

Debe existir:

MODEL DEGRADATION ALERT

⸻

104. Fallo seguro

Cuando el sistema detecte:

* datos insuficientes;
* corrupción;
* contradicción extrema;
* modelo fuera de dominio;
* drift;
* fallo de infraestructura;
* incertidumbre excesiva;

debe pasar a:

SAFE DEGRADATION

y aumentar la dependencia de revisión humana.

⸻

105. Principio de no automatización de alto impacto

Las decisiones que puedan afectar significativamente a:

* libertad;
* seguridad;
* integridad;
* salud;
* acceso a servicios;
* reputación;

deben incorporar supervisión humana apropiada y trazabilidad.

La arquitectura debe diseñarse desde el principio con documentación, evaluación de riesgos, logs y supervisión humana, en línea con los principios europeos de gestión de riesgo de IA. [REF-09]

⸻

106. Arquitectura de decisión completa

                 ┌─────────────────────┐
                 │      FUENTES        │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │     INGESTIÓN       │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │   PROVENIENCIA      │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ VALIDACIÓN / EPIST. │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │  ESTADO DEL SISTEMA │
                 └──────────┬──────────┘
                            ↓
          ┌─────────────────┼──────────────────┐
          ↓                 ↓                  ↓
      ANOMALÍAS         TRAYECTORIAS       INTERACCIONES
          │                 │                  │
          └─────────────────┼──────────────────┘
                            ↓
                 ┌─────────────────────┐
                 │   ALERT ENGINE      │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ INCERTIDUMBRE /     │
                 │ CORROBORACIÓN /     │
                 │ CONTRADICCIONES     │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ ALERTA CUALIFICADA  │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ REVISIÓN HUMANA     │
                 └──────────┬──────────┘
                            ↓
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
          MONITOR        APOYO          ESCALAMIENTO
             │              │              │
             └──────────────┼──────────────┘
                            ↓
                 ┌─────────────────────┐
                 │ RESULTADO OBSERVADO │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ CALIBRACIÓN /       │
                 │ APRENDIZAJE         │
                 └─────────────────────┘

⸻

107. Arquitectura de intervención humana

CEUTIA DETECTA
      ↓
CEUTIA EXPLICA
      ↓
HUMANO INTERPRETA
      ↓
HUMANO DECIDE
      ↓
AUTORIDAD / PROFESIONAL
      ↓
RESULTADO
      ↓
CEUTIA APRENDE

La intervención humana no es un elemento decorativo.

Es un componente funcional del sistema.

⸻

108. Principio central de CeutIA

CeutIA no debe intentar saberlo todo.

Debe intentar:

saber qué sabe, saber qué no sabe, detectar cuándo algo está cambiando y hacer visible aquello que un humano necesita comprender antes de actuar.

⸻

109. Criterio final de calidad

Una alerta de alta calidad no es la que tiene la puntuación más alta.

Es la que presenta:

evidencia suficiente
+
procedencia clara
+
independencia
+
corroboración
+
contexto
+
dinámica temporal
+
impacto potencial
+
incertidumbre explícita
+
hipótesis alternativas
+
acción proporcional
+
supervisión humana
+
trazabilidad

⸻

110. Principio de máxima utilidad

CeutIA debe intervenir conceptualmente antes de que el sistema pierda capacidad de recuperación.

La pregunta no debe ser solamente:

¿Ya ha ocurrido la crisis?

Debe ser:

¿Qué trayectoria está tomando el sistema, qué reserva le queda, qué interacción puede desencadenar una transición y qué intervención puede modificar esa trayectoria antes de que el coste sea mayor?

⸻

111. Principio de humanidad

La inteligencia sistémica no debe convertir a las personas en variables anónimas.

Cada persona puede ser simultáneamente:

ciudadano
paciente
migrante
trabajador
padre/madre
vecino
persona traumatizada
persona enfadada
persona vulnerable
persona que necesita ayuda

y ninguna de esas etiquetas determina por sí sola su conducta futura.

CeutIA debe interpretar a las personas dentro del contexto, no reducirlas al contexto.

⸻

112. Principio de contención

La función de CeutIA durante una crisis no es aumentar la percepción de amenaza.

Es disminuir el daño total.

Por tanto:

detección
→ comprensión
→ prevención
→ desescalada
→ intervención
→ recuperación

debe prevalecer sobre:

detección
→ amplificación
→ miedo
→ polarización
→ escalada

⸻

113. Principio de doble protección

CeutIA debe proteger simultáneamente:

PERSONAS

y:

SISTEMA

No existe contradicción necesaria entre ambos objetivos.

Proteger a la población puede requerir detectar una amenaza.

Detectar una amenaza correctamente puede requerir proteger a la persona que presenta señales de sufrimiento.

La arquitectura debe ser capaz de hacer ambas cosas sin convertir una función en sustituto de la otra.

⸻

114. Resultado operacional

El producto final de este documento es una arquitectura donde:

persona
   ↓
apoyo preventivo
datos
   ↓
inteligencia
inteligencia
   ↓
señal
señal
   ↓
evidencia
evidencia
   ↓
alerta
alerta
   ↓
humano
humano
   ↓
intervención
intervención
   ↓
resultado
resultado
   ↓
aprendizaje

Y el principio fundamental permanece:

CeutIA no decide por el sistema. CeutIA hace que el sistema pueda ser comprendido antes de que sea demasiado tarde.

⸻

115. Referencias científicas y normativas fundamentales

REF-01 — Transiciones críticas

Scheffer M, Carpenter SR, Lenton TM, Bascompte J, Brock W, Dakos V, et al. Anticipating critical transitions. Science. 2012;338(6105):344-348. doi:10.1126/science.1225244. PMID:23087241.

REF-02 — Early Warning Alert and Response

World Health Organization. Early warning alert and response (EWAR) in emergencies: an operational guide. WHO; 2023. ISBN 978-92-4-006358-7.

REF-03 — Carga alostática

Guidi J, Lucente M, Sonino N, Fava GA. Allostatic load and its impact on health: a systematic review. Psychother Psychosom. 2021;90(1):11-27. doi:10.1159/000510696. PMID:32799204.

REF-04 — Sueño y carga alostática

Christensen DS, Zachariae R, Amidi A, Wu LM. Sleep and allostatic load: a systematic review and meta-analysis. Sleep Med Rev. 2022;64:101650. doi:10.1016/j.smrv.2022.101650. PMID:35704985.

REF-05 — Carga alostática y cerebro

Lenart-Bugla M, Szcześniak D, Bugla B, Kowalski K, Niwa S, Rymaszewska J, et al. The association between allostatic load and brain: a systematic review. Psychoneuroendocrinology. 2022;145:105917. doi:10.1016/j.psyneuen.2022.105917. PMID:36113380.

REF-06 — AI Risk Management

Tabassi E. Artificial Intelligence Risk Management Framework (AI RMF 1.0). NIST AI 100-1. National Institute of Standards and Technology; 2023.

REF-07 — Comunicación de riesgos

World Health Organization. Communicating risk in public health emergencies: a WHO guideline for emergency risk communication policy and practice. WHO; 2017.

REF-08 — RCCE

World Health Organization. WHO competency framework, risk communication and community engagement. WHO; 2024.

REF-09 — European AI Act

Regulation (EU) 2024/1689 of the European Parliament and of the Council laying down harmonised rules on artificial intelligence (Artificial Intelligence Act).

Especialmente relevantes:

* Article 5 — prohibited AI practices;
* risk management;
* data governance;
* logging;
* transparency;
* human oversight;
* accuracy;
* robustness;
* cybersecurity.

REF-10 — Evaluación del riesgo de violencia

Viljoen JL, Cochrane DM, Jonnson MR. Do risk assessment tools help manage and reduce risk of violence and reoffending? A systematic review. Law Hum Behav. 2018. doi:10.1037/lhb0000280. PMID:29648841.

REF-11 — Migración y enfermedades transmisibles

Ben Brik A, Al-Romaihi HE, Al-Shamali M, et al. Global patterns of communicable disease risk and prevention in migrant populations: a systematic literature review and meta-analysis. Public Health Pract (Oxf). 2026;11:100754. doi:10.1016/j.puhip.2026.100754. PMID:41768268.

REF-12 — Ética y gobernanza de IA sanitaria

World Health Organization. Ethics and governance of artificial intelligence for health: WHO guidance. WHO; 2021.

REF-13 — IA generativa y salud

World Health Organization. Ethics and governance of artificial intelligence for health: large multi-modal models. WHO; 2024.

REF-14 — Moral injury

Anastasi G, Gravante F, Barbato P, Bambi S, Stievano A, Latina R. Moral injury and mental health outcomes in nurses: a systematic review. Nurs Ethics. 2025;32(3):698-723. doi:10.1177/09697330241281376. PMID:39323219.

REF-15 — Riesgo y validez predictiva

Singh JP, Desmarais SL, Hurducas C, Arbach-Lucioni K, Condemarin C, Dean K, et al. International perspectives on the practical application of violence risk assessment. Psychiatry Psychol Law. 2014.

REF-16 — Calidad y confianza en IA

National Institute of Standards and Technology. AI Risk Management Framework 1.0. Characteristics of trustworthy AI:

* valid and reliable;
* safe;
* secure and resilient;
* accountable and transparent;
* explainable and interpretable;
* privacy-enhanced;
* fair with harmful bias managed.

REF-17 — Comunicación, participación e infodemia

World Health Organization Regional Office for Europe. Risk communication, community engagement and infodemic management in the WHO European Region. WHO Europe; 2024.

⸻

116. Estado de implementación

Este documento define el modelo conceptual y normativo.

La implementación posterior deberá convertirlo progresivamente en:

schemas
+
database models
+
event models
+
evidence models
+
alert models
+
risk engine
+
provenance graph
+
calibration engine
+
human review workflow
+
audit system
+
public support interface

La implementación no debe alterar los principios epistemológicos establecidos aquí.

⸻

117. Regla de oro

No borrar la señal porque sea incómoda.

No convertir la señal en hecho porque sea alarmante.

No convertir el hecho en culpabilidad.

No convertir la probabilidad en certeza.

No convertir una persona en un perfil.

No convertir una alerta en una decisión automática.

Y no esperar a que el sistema colapse para empezar a observarlo.

Este documento ya deja fijado algo importante que antes estaba disperso: **CeutIA puede detectar señales que tengan relevancia para seguridad sin convertirse en una herramienta de perfilado criminal**. La diferencia está en que detecta eventos, patrones observables y trayectorias, conserva la incertidumbre y entrega una alerta explicable a una persona que decide qué hacer. Esto es además coherente con las restricciones actuales del AI Act y con los principios de supervisión humana y trazabilidad del NIST. [oai_citation:1‡EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng?utm_source=chatgpt.com)
También he integrado la parte sanitaria como realmente la habías definido: **interacción adaptativa de prevención y apoyo**, no un cuestionario de 30 enfermedades ni un sistema diagnóstico automático. Y he hecho que la salud individual pueda alimentar inteligencia poblacional solamente mediante una capa explícita de agregación y protección de privacidad. La evidencia sobre carga alostática, sueño y estrés respalda que esas variables tengan un lugar dentro del modelo dinámico, pero no que se utilicen como diagnósticos individuales automáticos. [oai_citation:2‡pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/32799204/?utm_source=chatgpt.com)