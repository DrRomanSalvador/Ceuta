docs/PUBLIC_SYSTEM_MODEL.md

# CEUTIA PUBLIC — MODELO SISTÉMICO GLOBAL
## 1. Propósito
CEUTIA PUBLIC es un sistema de inteligencia, conocimiento, prevención, salud pública, resiliencia y apoyo ciudadano centrado en Ceuta y conectado con su entorno territorial, nacional e internacional.
Su objeto no es únicamente observar Ceuta.
Debe representar matemáticamente la evolución de un sistema complejo compuesto por:
1. La población residente en Ceuta.
2. Las personas que entran, salen o transitan por Ceuta.
3. Los sistemas sanitarios, sociales y asistenciales.
4. Los servicios públicos y capacidades críticas.
5. Las Fuerzas y Cuerpos de Seguridad y, dentro del ámbito que legalmente corresponda, las capacidades de Defensa.
6. Las infraestructuras críticas y servicios esenciales.
7. La economía y actividad productiva.
8. La movilidad terrestre, marítima y aérea.
9. El entorno digital y la información pública.
10. El entorno geopolítico y transfronterizo.
11. La población general situada fuera de Ceuta pero conectada con ella.
12. Los flujos de información, percepción, opinión y comportamiento.
13. Los shocks externos.
14. La capacidad de absorción, adaptación, recuperación y transformación del sistema.
CEUTIA PUBLIC debe estudiar la trayectoria del sistema, no únicamente su estado instantáneo.
La unidad fundamental de análisis no es solamente:
    X(t)
sino:
    {X(t), dX/dt, d²X/dt², capacidad, reserva, presión, interacción, incertidumbre}
La plataforma debe poder responder simultáneamente:
- ¿Qué está ocurriendo?
- ¿Desde cuándo?
- ¿A qué velocidad está cambiando?
- ¿Está acelerando?
- ¿Es persistente o transitorio?
- ¿Qué capacidad está siendo consumida?
- ¿Qué reserva permanece?
- ¿Qué subsistema está aproximándose primero a un límite?
- ¿Qué interacciones pueden amplificar el fenómeno?
- ¿Qué señales débiles aparecen antes de una alteración mayor?
- ¿Qué hipótesis explican mejor la trayectoria?
- ¿Qué escenarios son compatibles con la evidencia?
- ¿Qué intervención preventiva podría modificar la trayectoria?
- ¿Qué incertidumbre existe?
- ¿Qué información falta?
- ¿Qué parte de la conclusión es observación, inferencia, hipótesis o predicción?
---
# 2. Principio central
CEUTIA adopta un modelo de sistema dinámico complejo.
Una representación mínima es:
    Estado(t+Δt) =
        f(
            Estado(t),
            presión(t),
            capacidad(t),
            reserva(t),
            interacciones(t),
            shocks(t),
            comportamiento(t),
            información(t),
            intervenciones(t),
            incertidumbre(t)
        )
Por tanto:
    dato ≠ indicador
    indicador ≠ señal
    señal ≠ explicación
    explicación ≠ causalidad
    causalidad ≠ predicción
    predicción ≠ hecho
Toda salida deberá conservar estas diferencias.
---
# 3. Escala territorial completa
CEUTIA PUBLIC no debe representar Ceuta como una isla analítica.
Debe utilizar cuatro escalas conectadas:
## Nivel A — Ceuta
Sistema territorial principal.
Incluye:
- población residente;
- población flotante;
- entradas;
- salidas;
- movilidad interna;
- movilidad fronteriza;
- presión asistencial;
- salud;
- seguridad;
- servicios públicos;
- infraestructuras;
- economía;
- educación;
- vivienda;
- alimentación;
- agua;
- energía;
- telecomunicaciones;
- transporte;
- percepción social;
- información;
- capacidad institucional;
- capacidad de respuesta;
- resiliencia.
## Nivel B — Entorno inmediato
Incluye:
- Marruecos;
- región del Estrecho;
- Andalucía;
- Melilla;
- Gibraltar;
- rutas marítimas;
- corredores migratorios;
- redes logísticas;
- dinámicas económicas y sociales relevantes.
## Nivel C — España
Incluye:
- población española;
- opinión pública;
- medios;
- redes sociales;
- decisiones gubernamentales;
- capacidad sanitaria;
- capacidad de seguridad;
- capacidad militar;
- recursos logísticos;
- transporte;
- legislación;
- protección civil;
- economía;
- respuesta institucional.
## Nivel D — Entorno internacional
Incluye únicamente información pertinente para explicar o anticipar fenómenos que puedan modificar la trayectoria del sistema.
Ejemplos:
- acontecimientos geopolíticos;
- conflictos;
- cambios económicos;
- fenómenos migratorios;
- climatología extrema;
- pandemias;
- ciberincidentes;
- alteraciones logísticas;
- cambios regulatorios;
- movimientos de población;
- acontecimientos diplomáticos.
No debe existir una frontera artificial entre los niveles.
Una alteración en un nivel puede propagarse a otro.
---
# 4. Poblaciones representadas
CEUTIA debe diferenciar explícitamente distintas poblaciones.
## 4.1 Población residente de Ceuta
Variables posibles:
    P_residente(t)
Incluye:
- tamaño;
- estructura por edad;
- distribución espacial;
- hogares;
- situación socioeconómica;
- necesidades;
- utilización de servicios;
- movilidad;
- salud poblacional;
- percepción;
- exposición a riesgos;
- capacidad adaptativa.
No se utilizará ningún atributo individual innecesario para el análisis colectivo.
---
## 4.2 Población temporal o flotante
Incluye personas que permanecen temporalmente en Ceuta.
Variables:
- tamaño;
- origen;
- duración prevista;
- distribución;
- movilidad;
- demanda potencial;
- utilización de servicios;
- necesidades básicas;
- presión sobre infraestructuras.
---
## 4.3 Personas en tránsito
Debe distinguirse:
    entrada → permanencia → salida
La variable relevante no es únicamente el número acumulado.
Debe modelarse:
    λ_in(t) = tasa de entrada
    λ_out(t) = tasa de salida
    P(t+1) = P(t) + Entradas(t) - Salidas(t)
La misma cantidad acumulada puede producir efectos completamente diferentes dependiendo de la velocidad de entrada.
Por tanto:
    1.000 personas / 30 días
no equivale sistémicamente a:
    1.000 personas / 3 horas
---
## 4.4 Población fuera de Ceuta
CEUTIA PUBLIC debe representar también a la población general que se encuentra fuera de Ceuta cuando exista una relación funcional con el sistema.
Esta población puede:
- recibir información sobre Ceuta;
- generar información;
- consumir información;
- difundir contenidos;
- modificar percepción;
- influir en decisiones;
- desplazarse hacia o desde Ceuta;
- aportar recursos;
- solicitar ayuda;
- participar en procesos de apoyo;
- verse afectada por consecuencias económicas, sanitarias o sociales.
Debe existir un subsistema:
    POP_EXTERNAL
con variables agregadas de:
- atención;
- percepción;
- exposición informativa;
- conocimiento;
- incertidumbre;
- confianza;
- comportamiento;
- movilidad;
- demanda de información;
- interacción con contenidos públicos.
No se debe convertir a la población externa en una herramienta de vigilancia individual.
El objetivo es modelar el entorno social conectado con Ceuta.
---
# 5. Fuerzas Armadas y capacidades de Defensa
CEUTIA PUBLIC debe contemplar el dominio de Defensa como parte del sistema global, pero con una separación estricta entre:
1. información pública;
2. información institucional autorizada;
3. información clasificada o sensible.
La existencia de un modelo conceptual no implica acceso a información clasificada.
## 5.1 Dominio DEFENSA
Representación conceptual:
    DEFENSA = {
        capacidades,
        disponibilidad agregada,
        preparación,
        logística,
        movilidad,
        apoyo a emergencias,
        dependencia de infraestructuras,
        interacción institucional,
        resiliencia,
        recuperación
    }
La plataforma pública solamente deberá utilizar información legalmente disponible para el nivel PUBLIC.
No debe exponer:
- posiciones operativas sensibles;
- vulnerabilidades tácticas;
- capacidades clasificadas;
- movimientos operativos no públicos;
- información personal de personal militar;
- información que pueda facilitar daño o comprometer operaciones.
---
## 5.2 Función sistémica de Defensa
A nivel abstracto, Defensa puede formar parte de la capacidad agregada de respuesta:
    C_total(t) =
        C_civil(t)
        + C_seguridad(t)
        + C_sanitario(t)
        + C_logistico(t)
        + C_proteccion_civil(t)
        + C_defensa(t)
Pero:
    C_total ≠ capacidad efectiva
porque pueden existir:
- restricciones temporales;
- restricciones geográficas;
- restricciones legales;
- dependencia logística;
- saturación;
- tiempos de movilización;
- incompatibilidades entre recursos;
- cuellos de botella.
Por tanto:
    C_efectiva(t)
        ≤
    C_total(t)
---
# 6. Servicios públicos y capacidades críticas
Cada capacidad debe representarse como una serie temporal.
Ejemplo:
    C_health(t)
    C_emergency(t)
    C_security(t)
    C_transport(t)
    C_water(t)
    C_energy(t)
    C_food(t)
    C_telecom(t)
    C_housing(t)
    C_social(t)
    C_logistics(t)
    C_governance(t)
Para cada capacidad:
    capacidad instalada
    capacidad nominal
    capacidad operativa
    capacidad disponible
    capacidad accesible
    capacidad efectiva
    utilización
    reserva
    tiempo de recuperación
---
# 7. Reserva adaptativa
Una capacidad no debe modelarse únicamente como:
    disponible / no disponible
Debe existir una reserva.
Conceptualmente:
    R(t) = C_effective(t) - D(t)
donde:
    R(t) = reserva disponible
    C_effective(t) = capacidad efectiva
    D(t) = demanda
Pero la reserva debe incorporar tiempo.
Una capacidad aparentemente suficiente durante una hora puede resultar insuficiente durante siete días.
Por tanto:
    R_time(t,T)
representará la capacidad de absorber presión durante un horizonte T.
---
# 8. Presión sistémica
La presión debe construirse a partir de múltiples componentes.
Conceptualmente:
    Pressure(t) =
        Demand(t)
        / EffectiveCapacity(t)
Pero CEUTIA no debe reducir la presión a una sola división.
Debe incorporar:
- intensidad;
- duración;
- velocidad de crecimiento;
- concentración espacial;
- concentración temporal;
- acumulación;
- repetición;
- distribución;
- vulnerabilidad;
- recuperación disponible.
Una formulación conceptual:
    Load(t) =
        ∫ Demand(τ) dτ
y:
    NetLoad(t) =
        AccumulatedLoad(t)
        - Recovery(t)
---
# 9. Cuellos de botella
Debe distinguirse:
    capacidad global
de:
    capacidad efectiva
y:
    capacidad efectiva accesible
Ejemplo conceptual:
    Entrada
       ↓
    Registro
       ↓
    Transporte
       ↓
    Alojamiento
       ↓
    Alimentación
       ↓
    Atención sanitaria
       ↓
    Derivación
       ↓
    Salida
El sistema puede disponer de suficiente capacidad agregada y, sin embargo, colapsar porque un nodo intermedio alcanza su límite.
CEUTIA debe identificar:
- bottlenecks;
- chokepoints;
- dependencia entre nodos;
- concentración;
- propagación;
- tiempo hasta saturación.
---
# 10. Dinámica temporal
Toda variable crítica deberá poder representarse como:
    X(t)
y analizar:
    dX/dt
    d²X/dt²
Además:
- tendencia;
- aceleración;
- volatilidad;
- persistencia;
- autocorrelación;
- estacionalidad;
- ciclos;
- cambios estructurales;
- recuperación;
- tiempo de recuperación.
Una situación estable puede convertirse en crítica no porque X sea actualmente extrema, sino porque:
    dX/dt >> 0
y simultáneamente:
    capacidad de adaptación ↓
---
# 11. Interacciones
CEUTIA debe representar relaciones entre subsistemas.
Ejemplo:
    movilidad
       ↓
    demanda
       ↓
    utilización sanitaria
       ↓
    carga profesional
       ↓
    fatiga
       ↓
    capacidad efectiva
       ↓
    tiempos de respuesta
       ↓
    percepción social
       ↓
    comportamiento
       ↓
    movilidad
Esto constituye un bucle de retroalimentación.
Por tanto, el sistema debe poder representar:
- feedback positivo;
- feedback negativo;
- retrasos temporales;
- amplificación;
- amortiguación;
- acoplamiento;
- desacoplamiento.
---
# 12. Salud poblacional
La salud debe modelarse como trayectoria.
No:
    salud = estado
sino:
    salud = trayectoria dinámica
Variables posibles:
- demanda sanitaria;
- urgencias;
- atención primaria;
- hospitalización;
- salud mental;
- estrés;
- sufrimiento;
- lesiones;
- enfermedades transmisibles;
- enfermedades crónicas;
- mortalidad;
- capacidad sanitaria;
- tiempos de respuesta;
- utilización;
- carga profesional;
- recuperación.
La plataforma debe estudiar:
    demanda sanitaria / capacidad sanitaria
pero también:
    velocidad de crecimiento de demanda
    +
    reserva sanitaria
    +
    fatiga profesional
    +
    capacidad de recuperación
---
# 13. Sufrimiento humano
El sufrimiento individual no debe reducirse a un indicador de seguridad.
CEUTIA PUBLIC debe disponer de una capa de interacción voluntaria destinada a:
- identificar necesidades expresadas por la persona;
- comprender contexto;
- ofrecer información;
- ofrecer recursos de bienestar;
- reducir incertidumbre;
- favorecer conductas preventivas;
- facilitar acceso a ayuda humana;
- acompañar durante situaciones difíciles.
La interacción individual y el modelo sistémico deben estar separados.
Una persona no debe convertirse automáticamente en un dato operativo.
---
# 14. Prevención y desescalada
CEUTIA PUBLIC debe intervenir preferentemente antes de que una perturbación se convierta en una crisis mayor.
Modelo:
    perturbación
        ↓
    señal temprana
        ↓
    comprensión
        ↓
    información fiable
        ↓
    prevención
        ↓
    reducción de presión
        ↓
    recuperación
La plataforma debe evitar:
- alarmismo;
- dramatización;
- estigmatización;
- desinformación;
- manipulación emocional;
- atribución causal no demostrada.
La desescalada debe basarse en:
- información verificable;
- reducción de incertidumbre;
- orientación práctica;
- dignidad;
- autonomía;
- proporcionalidad;
- evidencia.
---
# 15. Información pública y comportamiento
La información constituye una variable del sistema.
Debe modelarse:
    información
        ↓
    percepción
        ↓
    comportamiento
        ↓
    presión
        ↓
    respuesta institucional
        ↓
    nueva información
Variables posibles:
- volumen;
- velocidad de difusión;
- incertidumbre;
- contradicción;
- alcance;
- concentración;
- polarización;
- confianza;
- exposición;
- corrección;
- persistencia.
CEUTIA debe distinguir:
    información verdadera
    información no verificada
    información falsa
    información contradictoria
    información manipulada
No debe determinar falsedad únicamente por popularidad.
---
# 16. Fuentes y epistemología
Toda afirmación relevante debe poder remontarse a:
    fuente
       ↓
    dato
       ↓
    evidencia
       ↓
    afirmación
       ↓
    corroboración
       ↓
    contradicción
       ↓
    hipótesis
       ↓
    modelo
       ↓
    predicción
Cada elemento deberá mantener:
- procedencia;
- fecha;
- temporalidad;
- calidad;
- independencia;
- metodología;
- incertidumbre;
- grado de corroboración.
---
# 17. Independencia de fuentes
Tres fuentes que reproducen el mismo origen no deben contabilizarse como tres evidencias independientes.
CEUTIA debe estimar:
    EffectiveIndependentEvidence
en lugar de:
    NumberOfSources
Debe detectar:
- copias;
- dependencia editorial;
- dependencia institucional;
- reutilización;
- referencias circulares;
- fuentes derivadas.
---
# 18. Contradicciones
El sistema debe conservar las contradicciones.
No debe eliminarlas automáticamente.
Representación:
    Claim A
       ↕
    contradicts
       ↕
    Claim B
La contradicción debe provocar:
- reducción de confianza;
- investigación adicional;
- revisión de hipótesis;
- mantenimiento de escenarios alternativos.
No:
    contradicción → eliminación arbitraria
---
# 19. Hipótesis competidoras
Para fenómenos relevantes:
    H1
    H2
    H3
    ...
Cada hipótesis debe disponer de:
- evidencia a favor;
- evidencia en contra;
- predicciones observables;
- variables discriminantes;
- probabilidad o plausibilidad cuando sea justificable;
- incertidumbre;
- fecha de evaluación.
Ejemplo conceptual:
    H1 = perturbación espontánea
    H2 = perturbación parcialmente coordinada
    H3 = fenómeno híbrido
    H4 = combinación de factores independientes
El sistema no debe seleccionar automáticamente la hipótesis más dramática.
---
# 20. Señales tempranas
CEUTIA debe buscar indicadores de pérdida de resiliencia.
Ejemplos:
- aumento de varianza;
- aumento de autocorrelación;
- recuperación más lenta;
- sincronización creciente;
- cambios anómalos en correlaciones;
- aumento de volatilidad;
- acumulación de presión;
- pérdida de reserva;
- aumento de dependencia entre subsistemas.
Una señal temprana no equivale a una predicción confirmada.
Debe clasificarse como:
    señal → evidencia para vigilancia
---
# 21. Umbrales y transiciones de régimen
Un sistema puede presentar:
    estabilidad
        ↓
    estrés
        ↓
    compensación
        ↓
    agotamiento
        ↓
    amplificación
        ↓
    umbral
        ↓
    transición
        ↓
    cascada
El punto de transición puede depender del estado previo.
Por ello:
    riesgo(t) ≠ función exclusivamente de X(t)
También:
    riesgo(t) =
        f(
            X(t),
            dX/dt,
            reserve(t),
            coupling(t),
            shock(t),
            recovery(t)
        )
---
# 22. Shocks externos
CEUTIA debe representar perturbaciones:
    X(t) → X(t) + ΔX
Caracterizadas por:
- intensidad;
- duración;
- velocidad;
- frecuencia;
- repetición;
- localización;
- subsistemas afectados;
- capacidad disponible durante el shock.
Dos shocks idénticos pueden producir resultados diferentes dependiendo del estado previo.
Por tanto:
    Impact(shock)
        =
    f(
        shock,
        state_before,
        reserve,
        coupling,
        recovery
    )
---
# 23. Cascadas
Debe existir un modelo de propagación.
Ejemplo:
    shock fronterizo
        ↓
    movilidad
        ↓
    alojamiento
        ↓
    alimentación
        ↓
    atención sanitaria
        ↓
    logística
        ↓
    seguridad
        ↓
    percepción
        ↓
    comportamiento
        ↓
    nueva presión
La plataforma debe calcular:
- nodos afectados;
- velocidad de propagación;
- intensidad;
- capacidad de amortiguación;
- puntos de interrupción;
- escenarios de recuperación.
---
# 24. Modelo de escenarios
CEUTIA no debe producir solamente:
    "ocurrirá X"
Debe generar trayectorias alternativas.
Ejemplo:
### Escenario S0 — Continuidad
    presión estable
    capacidad suficiente
    recuperación normal
### Escenario S1 — Deterioro progresivo
    demanda ↑
    reserva ↓
    tiempos de respuesta ↑
### Escenario S2 — Shock puntual
    shock ↑
    presión ↑
    recuperación posterior
### Escenario S3 — Shock repetido
    shock
      ↓
    recuperación incompleta
      ↓
    segundo shock
      ↓
    reserva crítica
### Escenario S4 — Cascada
    shock
      ↓
    bottleneck
      ↓
    fallo secundario
      ↓
    amplificación
      ↓
    múltiples subsistemas afectados
Cada escenario debe contener:
- condiciones iniciales;
- variables críticas;
- trayectoria;
- incertidumbre;
- señales observables;
- puntos de decisión;
- capacidad de recuperación.
---
# 25. Contrafactuales
CEUTIA debe responder:
    ¿Qué ocurriría si aumentamos X?
    ¿Qué ocurriría si reducimos Y?
    ¿Qué capacidad tiene mayor efecto sobre la trayectoria?
    ¿Qué intervención evita alcanzar el umbral?
Conceptualmente:
    ΔOutcome / ΔIntervention
permite estudiar sensibilidad.
El objetivo es identificar:
    puntos de máxima palanca sistémica
---
# 26. Arquitectura de población y protección
El modelo debe diferenciar:
    PERSONA
    POBLACIÓN
    SISTEMA
Una persona puede interactuar voluntariamente con CEUTIA.
La población puede generar señales agregadas.
El sistema puede analizar dinámicas colectivas.
Pero:
    persona ≠ amenaza
    persona ≠ indicador
    persona ≠ hipótesis
    persona ≠ objetivo operativo
La agregación debe utilizarse siempre que sea suficiente para responder a la pregunta.
---
# 27. Arquitectura de usuarios
CEUTIA PUBLIC puede contemplar diferentes superficies.
## Ciudadano de Ceuta
Puede:
- consultar información;
- recibir orientación;
- consultar recursos;
- participar voluntariamente;
- expresar necesidades;
- acceder a contenidos de prevención y bienestar.
## Persona en tránsito
Puede:
- recibir información;
- conocer recursos;
- obtener orientación;
- conocer servicios;
- recibir información de prevención.
## Población fuera de Ceuta
Puede:
- consultar información;
- comprender la situación;
- acceder a fuentes;
- recibir contexto;
- consultar escenarios públicos;
- participar en iniciativas de apoyo.
## Profesionales
Pueden acceder a información agregada y autorizada según función.
## Administraciones
Únicamente mediante integraciones y permisos autorizados.
## Defensa / seguridad
El modelo conceptual existe, pero el acceso depende estrictamente de:
- autorización;
- clasificación;
- marco legal;
- necesidad de conocer;
- seguridad operacional.
---
# 28. Separación PUBLIC / OWNER
La arquitectura debe mantener:
    CEUTIA CORE
          │
      ┌───┴────┐
      ↓        ↓
   PUBLIC     OWNER
PUBLIC puede producir:
- datos públicos;
- modelos agregados;
- señales;
- alertas preventivas;
- escenarios públicos;
- información de bienestar;
- indicadores de resiliencia;
- análisis abiertos.
OWNER puede disponer de capacidades adicionales autorizadas.
PUBLIC no debe convertirse en una ventana indirecta hacia información privada o clasificada.
---
# 29. Flujo PUBLIC → OWNER
Cuando corresponda:
    Observación
        ↓
    Validación
        ↓
    Evidencia
        ↓
    Señal
        ↓
    Evaluación
        ↓
    Nivel de confianza
        ↓
    Alerta
        ↓
    OWNER
El sistema debe enviar señales estructuradas, no conclusiones opacas.
Ejemplo conceptual:
```json
{
  "signal": "increasing_systemic_pressure",
  "domain": "health_capacity",
  "trend": "increasing",
  "acceleration": "positive",
  "reserve": "declining",
  "confidence": 0.78,
  "uncertainty": 0.14,
  "time_window": "72h",
  "evidence_count": 12,
  "independent_sources": 5,
  "status": "requires_review"
}

⸻

30. Modelo matemático mínimo

Cada variable relevante debería poder representarse como:

X_i(t)

La dinámica:

dX_i/dt = F_i(X, U, E, ε)

donde:

X = estado del sistema
U = intervenciones
E = perturbaciones externas
ε = incertidumbre/residuo

Las interacciones pueden representarse mediante:

dX_i/dt =
    F_i(X_i)
    +
    Σ β_ij X_j
    +
    U_i
    +
    E_i
    +
    ε_i

Los parámetros β_ij deberán disponer de:

* origen;
* estimación;
* incertidumbre;
* método;
* periodo de validez;
* validación.

⸻

31. Modelo de resiliencia

Una aproximación conceptual:

Resilience(t) =
    Capacity(t)
    -
    Load(t)
    +
    RecoveryCapacity(t)

Pero debe evitarse convertir resiliencia en una cifra arbitraria.

Debe incluir:

* absorción;
* adaptación;
* recuperación;
* aprendizaje;
* redundancia;
* sustitución;
* reserva;
* diversidad;
* conectividad;
* tiempo de recuperación.

⸻

32. Riesgo dinámico

El riesgo debe ser función de:

Risk(t) =
    Probability(Event | State)
    ×
    Impact(Event | State)

Pero la probabilidad depende del estado del sistema.

Por tanto:

P(Event)
    =
P(Event | X(t), dX/dt, Reserve(t), Coupling(t))

No debe asumirse que el riesgo permanece constante.

⸻

33. Incertidumbre

Toda salida importante debe diferenciar:

Incertidumbre de medición

El dato tiene error.

Incertidumbre epistemológica

No sabemos suficientemente qué está ocurriendo.

Incertidumbre de modelo

El modelo puede ser incorrecto.

Incertidumbre futura

Existen múltiples trayectorias posibles.

Incertidumbre causal

La relación entre variables no está suficientemente demostrada.

CEUTIA debe representar estas incertidumbres explícitamente.

⸻

34. Aprendizaje retrospectivo

Toda predicción debe poder compararse posteriormente con la realidad.

Predicción(t0)
      ↓
Observación(t1)
      ↓
Comparación
      ↓
Error
      ↓
Calibración
      ↓
Revisión del modelo

Métricas posibles:

* Brier score;
* log loss;
* calibration error;
* precisión;
* recall;
* falsos positivos;
* falsos negativos;
* error de predicción;
* error de intervalo;
* estabilidad temporal.

El sistema debe aprender de sus errores.

⸻

35. Alertas

Una alerta no debe depender exclusivamente de un valor absoluto.

Puede activarse por combinación:

threshold
+
trend
+
acceleration
+
reserve
+
persistence
+
corroboration

Ejemplo conceptual:

ALERT =
    PressureHigh
    AND TrendIncreasing
    AND ReserveDeclining
    AND PersistenceConfirmed

⸻

36. Niveles de salida

CEUTIA PUBLIC deberá diferenciar:

Nivel 0 — Información

Hecho o dato contextual.

Nivel 1 — Señal

Patrón que merece observación.

Nivel 2 — Anomalía

Desviación estadísticamente relevante.

Nivel 3 — Riesgo

Conjunto de señales compatible con aumento de probabilidad de un evento.

Nivel 4 — Situación crítica

Evidencia de deterioro significativo de uno o varios subsistemas.

Nivel 5 — Cascada sistémica

Interacciones múltiples con propagación entre subsistemas.

Estos niveles no representan automáticamente niveles oficiales de emergencia.

Son categorías analíticas internas del sistema.

⸻

37. Salida para población general

La población no debe recibir el modelo matemático bruto.

Debe recibir:

* qué sabemos;
* qué no sabemos;
* qué significa;
* qué puede hacer;
* dónde encontrar ayuda;
* cómo protegerse;
* qué información es fiable;
* qué información no está confirmada.

Cuando exista incertidumbre:

"No se ha confirmado X"

es preferible a:

"X no está ocurriendo"

si la evidencia no permite excluirlo.

⸻

38. Salida de bienestar

Cuando una persona expresa sufrimiento, CEUTIA PUBLIC puede adaptar la interacción a:

situación
    ↓
comprensión
    ↓
apoyo
    ↓
prevención
    ↓
recurso adecuado

Puede proporcionar:

* información psicoeducativa;
* técnicas generales de regulación;
* higiene del sueño;
* actividad física segura;
* alimentación general saludable;
* conexión social;
* reducción de aislamiento;
* recursos comunitarios;
* contenidos audiovisuales de calidad;
* discursos y materiales educativos;
* orientación hacia profesionales.

No debe:

* diagnosticar automáticamente;
* prescribir medicamentos;
* modificar tratamientos;
* sustituir asistencia sanitaria;
* presentar contenido como tratamiento individualizado.

⸻

39. Biblioteca de conocimiento

Los contenidos recomendados deberán almacenarse con:

* título;
* autor;
* fuente;
* fecha;
* idioma;
* contexto;
* población objetivo;
* evidencia;
* limitaciones;
* riesgos;
* revisión;
* calidad;
* motivo de recomendación.

El sistema debe seleccionar contenido según:

contexto + necesidad + evidencia + seguridad

y no según popularidad únicamente.

⸻

40. Arquitectura de observación

Las fuentes pueden incluir:

* estadísticas oficiales;
* publicaciones científicas;
* registros públicos;
* datos meteorológicos;
* movilidad agregada;
* información sanitaria agregada;
* información económica;
* comunicaciones oficiales;
* información institucional;
* medios;
* fuentes abiertas;
* señales digitales públicas;
* datos proporcionados voluntariamente;
* sensores autorizados.

Cada fuente deberá conservar:

provenance
timestamp
reliability
independence
scope
limitations

⸻

41. No inferir más de lo que permiten los datos

CEUTIA debe evitar:

correlación → causalidad
anomalía → ataque
movilidad → criminalidad
sufrimiento → enfermedad
aumento de población → amenaza
actividad digital → intención hostil

Toda transición de:

observación → interpretación

deberá quedar explícitamente identificada.

⸻

42. Protección contra errores sistémicos

El sistema debe contemplar:

* falsos positivos;
* falsos negativos;
* sesgo de selección;
* sesgo de disponibilidad;
* sesgo de confirmación;
* dependencia de fuentes;
* datos incompletos;
* datos retrasados;
* cambios de definición;
* cambios metodológicos;
* cambios de comportamiento;
* concept drift;
* model drift.

Un modelo que funcionó históricamente puede dejar de funcionar.

⸻

43. Capa de gobernanza

Toda salida relevante debe permitir reconstruir:

qué sabía el sistema
+
qué no sabía
+
qué fuentes utilizó
+
qué modelo aplicó
+
qué supuestos realizó
+
qué incertidumbre tenía
+
qué produjo
+
qué ocurrió posteriormente

Esto permite auditar el razonamiento.

⸻

44. Arquitectura conceptual completa

La arquitectura global de CEUTIA PUBLIC puede representarse:

                         ENTORNO INTERNACIONAL
                                  │
                                  ▼
                         ENTORNO TRANSFRONTERIZO
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
              ESPAÑA                        CEUTA
                    │                           │
                    │              ┌────────────┼────────────┐
                    │              │            │            │
                    │              ▼            ▼            ▼
                    │          POBLACIÓN     CAPACIDADES   INFRAESTRUCTURAS
                    │              │            │            │
                    │              ▼            ▼            ▼
                    │          MOVILIDAD      SALUD       LOGÍSTICA
                    │              │            │            │
                    └──────────────┼────────────┼────────────┘
                                   │
                                   ▼
                         INFORMACIÓN / COMPORTAMIENTO
                                   │
                                   ▼
                           DINÁMICA DEL SISTEMA
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
           PRESIÓN              RESERVA             CAPACIDAD
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                                   ▼
                             INTERACCIONES
                                   │
                                   ▼
                          UMBRALES / CASCADAS
                                   │
                                   ▼
                             ESCENARIOS
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
               PREVENCIÓN                    SEÑALES OWNER
                    │
                    ▼
             APOYO / DESESCALADA
                    │
                    ▼
              RECUPERACIÓN
                    │
                    ▼
                APRENDIZAJE
                    │
                    └──────────────► MODELO REVISADO

⸻

45. Modelo de doble escala

CEUTIA debe operar simultáneamente en dos escalas.

Escala humana

persona
   ↓
necesidad
   ↓
sufrimiento
   ↓
apoyo
   ↓
prevención
   ↓
recuperación

Escala sistémica

población
   ↓
demanda
   ↓
capacidad
   ↓
reserva
   ↓
presión
   ↓
interacción
   ↓
umbral
   ↓
cascada
   ↓
recuperación

Ambas escalas pueden interactuar, pero no deben confundirse.

⸻

46. Modelo de población general fuera de Ceuta

La población externa constituye un sistema conectado:

             CEUTA
               │
               ▼
          INFORMACIÓN
               │
       ┌───────┴────────┐
       ▼                ▼
 PERCEPCIÓN          CONFIANZA
       │                │
       └───────┬────────┘
               ▼
           COMPORTAMIENTO
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
    MOVILIDAD APOYO  INFORMACIÓN
       │                │
       └───────┬────────┘
               ▼
             CEUTA

La finalidad es comprender el acoplamiento social, no vigilar individuos.

⸻

47. Modelo de Defensa dentro del sistema global

                 SISTEMA NACIONAL
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
      CAPACIDAD CIVIL          CAPACIDAD DEFENSA
          │                         │
          └────────────┬────────────┘
                       ▼
                CAPACIDAD GLOBAL
                       │
                       ▼
                CAPACIDAD EFECTIVA
                       │
                       ▼
                     RESERVA
                       │
                       ▼
                   RESPUESTA
                       │
                       ▼
                  RECUPERACIÓN

CEUTIA PUBLIC representa únicamente el nivel de información permitido para su superficie pública.

⸻

48. Principio de seguridad

La arquitectura completa debe asumir que:

cualquier dato puede ser incorrecto
cualquier fuente puede equivocarse
cualquier modelo puede fallar
cualquier predicción puede fallar
cualquier señal puede ser ambigua

Por ello:

confianza ≠ certeza

y:

alerta ≠ verdad

⸻

49. Principio de no manipulación

La capacidad de comprender el comportamiento colectivo no debe utilizarse para manipularlo.

CEUTIA PUBLIC debe orientarse a:

* informar;
* prevenir;
* proteger;
* acompañar;
* reducir sufrimiento;
* aumentar resiliencia;
* disminuir incertidumbre;
* facilitar decisiones responsables.

No debe utilizar vulnerabilidades psicológicas individuales para producir conductas predeterminadas.

⸻

50. Objetivo matemático final

El objetivo no es construir:

un dashboard de Ceuta

ni:

un único score de riesgo.

El objetivo es construir una representación dinámica:

SYSTEM(t)

capaz de estimar:

estado
trayectoria
presión
capacidad
reserva
interacciones
vulnerabilidades
señales tempranas
escenarios
incertidumbre
capacidad de recuperación

y aprender continuamente:

predicción → realidad → error → calibración → nuevo modelo

⸻

51. Definición funcional final

CEUTIA PUBLIC debe poder responder, dentro de sus límites de datos, seguridad y evidencia:

¿En qué estado se encuentra Ceuta?

¿Cómo está cambiando?

¿Qué está acelerando?

¿Qué capacidad está siendo consumida?

¿Dónde está la reserva?

¿Qué subsistema presenta mayor vulnerabilidad?

¿Qué interacciones pueden amplificar el problema?

¿Qué señales tempranas aparecen?

¿Qué hipótesis explican mejor la evidencia?

¿Qué escenarios son plausibles?

¿Qué intervención preventiva puede modificar la trayectoria?

¿Qué puede hacer una persona para proteger su bienestar?

¿Qué información debe conocer la población?

¿Qué señales deberían ser revisadas por el sistema OWNER?

¿Qué ocurrió finalmente?

¿Qué predijo CEUTIA correctamente?

¿En qué se equivocó?

¿Qué debe aprender el modelo?

La finalidad última es pasar de:

observar acontecimientos

a:

comprender trayectorias

y de:

reaccionar ante crisis

a:

detectar deterioro temprano,
aumentar capacidad de respuesta,
reducir sufrimiento,
prevenir escaladas
y favorecer la recuperación del sistema.