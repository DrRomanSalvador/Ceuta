SECURITY_ARCHITECTURE.md

CEUTIA PUBLIC — SECURITY ARCHITECTURE

1. Purpose

CEUTIA PUBLIC requiere una arquitectura de seguridad capaz de proteger simultáneamente:

* la infraestructura técnica;
* los datos;
* la identidad de las personas;
* los datos personales y especialmente sensibles;
* la integridad de las fuentes;
* la cadena de evidencia;
* los modelos analíticos;
* las señales y alertas;
* las interacciones ciudadanas;
* la separación entre PUBLIC y OWNER;
* y la integridad epistemológica del sistema.

La seguridad de CEUTIA PUBLIC no se limita a impedir accesos no autorizados.

También debe impedir que información manipulada, incompleta, contaminada o mal interpretada atraviese las diferentes capas del sistema y termine produciendo una conclusión, recomendación o señal incorrecta.

⸻

2. Principio fundamental

CEUTIA PUBLIC adopta un modelo de seguridad de defensa en profundidad y mínimo privilegio.

La arquitectura parte de los siguientes principios:

* deny by default;
* least privilege;
* separación de responsabilidades;
* separación de datos;
* separación de identidades;
* validación de entradas;
* validación de salidas;
* trazabilidad;
* integridad;
* confidencialidad;
* disponibilidad;
* resiliencia;
* auditabilidad;
* recuperación;
* evaluación continua.

Ningún control aislado debe considerarse suficiente.

⸻

3. Superficies de seguridad

CEUTIA PUBLIC tiene varias superficies de ataque y fallo.

                         CEUTIA PUBLIC
                              │
       ┌──────────┬───────────┼───────────┬───────────┐
       ▼          ▼           ▼           ▼           ▼
    USUARIO     API        INGESTA      DATOS       MODELOS
       │          │           │           │           │
       ▼          ▼           ▼           ▼           ▼
   identidad   acceso      fuentes     almacenamiento inferencia
       │          │           │           │           │
       └──────────┴───────────┼───────────┴───────────┘
                              ▼
                       SALIDAS DEL SISTEMA
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                 PUBLIC               OWNER

Cada superficie requiere controles específicos.

⸻

4. Seguridad técnica y seguridad epistemológica

CEUTIA PUBLIC considera dos dimensiones de seguridad.

4.1 Seguridad técnica

Protege:

* servidores;
* redes;
* APIs;
* bases de datos;
* credenciales;
* secretos;
* sesiones;
* dispositivos;
* dependencias;
* contenedores;
* almacenamiento;
* comunicaciones;
* infraestructura cloud;
* pipelines de despliegue.

4.2 Seguridad epistemológica

Protege:

* procedencia;
* autenticidad de fuentes;
* integridad de evidencia;
* independencia entre fuentes;
* consistencia temporal;
* contradicciones;
* hipótesis;
* modelos;
* inferencias;
* señales;
* predicciones;
* decisiones derivadas.

Una vulnerabilidad epistemológica puede producir un daño operativo aunque toda la infraestructura técnica permanezca intacta.

⸻

5. Cadena de contaminación epistemológica

El sistema debe asumir que una entrada incorrecta puede propagarse.

FUENTE MANIPULADA
       ↓
EVIDENCIA INCORRECTA
       ↓
AFIRMACIÓN INCORRECTA
       ↓
MODELO DISTORSIONADO
       ↓
SEÑAL ERRÓNEA
       ↓
RECOMENDACIÓN INCORRECTA
       ↓
DECISIÓN / INTERVENCIÓN

Por ello, CEUTIA debe poder reconstruir retrospectivamente:

* qué fuente produjo el dato;
* cuándo se obtuvo;
* qué transformación sufrió;
* qué modelo lo utilizó;
* qué inferencia produjo;
* qué versión del modelo estaba activa;
* qué señal se generó;
* qué salida se presentó;
* y qué información posterior permitió confirmar o refutar el resultado.

⸻

6. Modelo de confianza

Ninguna entrada debe recibir confianza absoluta simplemente por estar disponible.

La confianza debe poder depender de variables como:

* procedencia;
* reputación histórica;
* autenticidad;
* independencia;
* consistencia;
* actualidad;
* corroboración;
* contradicciones;
* calidad metodológica;
* integridad técnica;
* incertidumbre.

La confianza de una fuente tampoco debe confundirse automáticamente con la confianza de una afirmación concreta.

⸻

7. Identidad y autenticación

Toda funcionalidad que requiera identificación debe utilizar mecanismos de autenticación apropiados al nivel de riesgo.

La arquitectura debe contemplar:

* gestión segura de identidades;
* sesiones;
* expiración;
* revocación;
* protección contra reutilización indebida;
* MFA cuando corresponda;
* recuperación segura;
* protección contra credential stuffing;
* rate limiting;
* detección de actividad anómala.

Las credenciales nunca deben almacenarse en código fuente.

Los secretos de producción nunca deben almacenarse en el repositorio.

⸻

8. Autorización

La autenticación demuestra quién es una identidad.

La autorización determina qué puede hacer.

CEUTIA PUBLIC debe aplicar autorización explícita sobre:

* recursos;
* operaciones;
* datos;
* endpoints;
* funciones administrativas;
* datasets;
* modelos;
* exportaciones;
* registros;
* configuraciones.

La autorización debe ser evaluada en servidor y nunca confiar únicamente en controles del cliente.

⸻

9. Separación PUBLIC / OWNER

La separación entre CEUTIA PUBLIC y CEUTIA OWNER es un requisito arquitectónico.

PUBLIC no debe convertirse en una puerta de acceso indirecto a OWNER.

La frontera debe proteger:

IDENTIDAD
   +
PERMISOS
   +
DATOS
   +
APIs
   +
SECRETOS
   +
MODELOS
   +
SALIDAS
   +
LOGS

Una señal procedente de PUBLIC puede ser transmitida a OWNER mediante una interfaz controlada.

Esto no implica que OWNER pueda acceder indiscriminadamente a los datos personales recogidos por PUBLIC.

La transferencia debe estar limitada a la finalidad y al nivel de información autorizado.

⸻

10. Datos personales

CEUTIA PUBLIC debe aplicar minimización de datos.

Antes de almacenar un dato personal debe existir una razón funcional documentada.

Debe evitarse recopilar información simplemente porque técnicamente sea posible.

La arquitectura debe separar, cuando sea posible:

IDENTIDAD
    │
    └── datos identificativos
DATOS DE INTERACCIÓN
    │
    └── información proporcionada por la persona
DATOS ANALÍTICOS
    │
    └── variables utilizadas para análisis
DATOS AGREGADOS
    │
    └── información utilizada para comprender el sistema

No toda información obtenida durante una interacción individual debe convertirse en una variable del modelo territorial.

⸻

11. Datos de salud y bienestar

La información relacionada con salud, sufrimiento psicológico o bienestar puede presentar una sensibilidad especialmente elevada.

El sistema debe aplicar controles reforzados.

Entre ellos:

* minimización;
* finalidad específica;
* acceso restringido;
* separación lógica;
* cifrado cuando corresponda;
* retención limitada;
* auditoría;
* controles de exportación;
* eliminación segura;
* gestión adecuada de consentimiento y base jurídica;
* prevención de reutilizaciones incompatibles.

La arquitectura técnica deberá concretarse conforme al marco jurídico aplicable y al tratamiento real que finalmente se implemente.

No debe asumirse automáticamente la aplicabilidad de un régimen jurídico concreto sin analizar el tratamiento y la jurisdicción correspondiente.

⸻

12. Interacción ciudadana

La interacción con ciudadanos debe ser voluntaria salvo que una funcionalidad concreta tenga otra base jurídica legítima y documentada.

La interfaz debe evitar:

* coerción;
* manipulación;
* presión emocional;
* preguntas innecesarias;
* recopilación excesiva;
* falsas garantías;
* falsa apariencia de atención médica;
* atribución automática de diagnósticos.

El ciudadano debe poder comprender, en términos claros:

* qué información se solicita;
* para qué se solicita;
* si es opcional;
* cómo puede utilizarse;
* qué tipo de ayuda puede proporcionar CEUTIA;
* cuáles son sus límites.

⸻

13. Seguridad de las recomendaciones

Las recomendaciones dirigidas a ciudadanos deben tener una superficie de seguridad propia.

Antes de presentar una recomendación, el sistema debe poder evaluar:

* finalidad;
* contexto;
* nivel de riesgo;
* evidencia disponible;
* población destinataria;
* posibles contraindicaciones;
* límites;
* necesidad de derivación.

Las recomendaciones generales de bienestar deben permanecer dentro del ámbito para el que hayan sido diseñadas.

CEUTIA PUBLIC no debe improvisar tratamientos médicos.

No debe generar prescripciones farmacológicas.

No debe presentar una inferencia automatizada como diagnóstico.

No debe retrasar una atención profesional necesaria.

⸻

14. Detección de situaciones de riesgo

El sistema puede detectar señales compatibles con un nivel elevado de necesidad.

La respuesta debe ser proporcional.

SEÑAL
  ↓
EVALUACIÓN
  ↓
┌────────────┬──────────────┬───────────────────┐
│ BAJO       │ MODERADO     │ ALTO / CRÍTICO    │
│            │              │                   │
▼            ▼              ▼
Bienestar    Apoyo y        Derivación a        │
general      seguimiento    ayuda humana        │

Los criterios concretos de escalado deben estar documentados, probados y revisados.

Cuando una situación pueda implicar un riesgo que requiera intervención profesional o de emergencia, CEUTIA debe orientar hacia recursos humanos apropiados.

⸻

15. Seguridad de contenidos

Los vídeos, discursos, textos, ejercicios y otros materiales utilizados por CEUTIA deben proceder de una biblioteca controlada.

El sistema debe registrar:

* fuente;
* autor;
* versión;
* fecha de incorporación;
* fecha de revisión;
* evidencia;
* clasificación;
* contexto recomendado;
* restricciones;
* estado de aprobación.

El contenido externo no debe incorporarse automáticamente como contenido de confianza.

⸻

16. Seguridad frente a contenido externo

Las fuentes externas pueden contener:

* información falsa;
* instrucciones maliciosas;
* prompt injection;
* código malicioso;
* enlaces peligrosos;
* contenido manipulado;
* datos falsificados;
* instrucciones destinadas a alterar el comportamiento del sistema.

El contenido ingerido debe tratarse como datos no confiables hasta superar los controles correspondientes.

Los datos externos no deben tener capacidad directa para modificar:

* permisos;
* configuración;
* políticas;
* secretos;
* código;
* modelos;
* instrucciones internas.

⸻

17. Ingesta segura

Todo pipeline de ingestión debe contemplar:

FUENTE
  ↓
IDENTIFICACIÓN
  ↓
AUTENTICACIÓN / VALIDACIÓN
  ↓
RECEPCIÓN
  ↓
NORMALIZACIÓN
  ↓
VALIDACIÓN
  ↓
CONTROL DE INTEGRIDAD
  ↓
CLASIFICACIÓN
  ↓
ALMACENAMIENTO
  ↓
PROCESAMIENTO

Debe conservarse la trazabilidad entre el dato original y sus transformaciones.

Los errores de ingestión no deben eliminarse silenciosamente.

⸻

18. Integridad de los datos

Los datos críticos deben disponer de mecanismos adecuados para detectar:

* modificación;
* corrupción;
* duplicación;
* pérdida;
* alteración temporal;
* inconsistencias;
* manipulación.

Cuando proceda, se utilizarán hashes, firmas, checksums, identificadores de versión u otros mecanismos apropiados.

La elección concreta dependerá del tipo de dato y del nivel de riesgo.

⸻

19. Base de datos

La capa de persistencia debe aplicar:

* autenticación fuerte;
* autorización;
* segregación de privilegios;
* cifrado en tránsito;
* cifrado en reposo cuando corresponda;
* backups;
* recuperación;
* auditoría;
* controles de acceso;
* gestión de credenciales;
* protección contra inyección;
* validación de consultas;
* migraciones controladas.

Las credenciales de base de datos no deben aparecer en el código fuente.

⸻

20. Cifrado

La arquitectura debe contemplar cifrado:

* en tránsito;
* en reposo;
* de secretos;
* de credenciales sensibles;
* de determinados campos cuando sea necesario.

La gestión criptográfica debe separar las claves de los datos que protegen.

Las claves deben gestionarse mediante mecanismos apropiados al entorno de despliegue.

No se debe utilizar una biblioteca o extensión concreta como sinónimo de cifrado completo de infraestructura.

⸻

21. Gestión de secretos

Los secretos deben mantenerse fuera del código y del repositorio.

Se incluyen:

* contraseñas;
* API keys;
* tokens;
* claves privadas;
* credenciales cloud;
* secretos JWT;
* credenciales de bases de datos;
* claves criptográficas;
* certificados privados.

En producción deben utilizarse mecanismos de gestión de secretos apropiados.

La rotación debe estar contemplada cuando el riesgo lo requiera.

⸻

22. APIs

Las APIs deben implementar:

* autenticación;
* autorización;
* validación de entrada;
* validación de salida;
* rate limiting;
* límites de tamaño;
* control de errores;
* logging;
* protección contra abuso;
* versionado;
* gestión segura de CORS;
* protección contra inyección;
* controles específicos para operaciones sensibles.

Los mensajes de error no deben revelar información interna innecesaria.

⸻

23. Protección de entradas

Toda entrada externa debe considerarse no confiable.

Debe validarse:

* tipo;
* formato;
* longitud;
* rango;
* codificación;
* estructura;
* contenido;
* contexto.

La validación debe realizarse en el servidor.

La sanitización no debe utilizarse como sustituto de una arquitectura de autorización correcta.

⸻

24. Protección de salidas

Las salidas también requieren controles.

Antes de mostrar o transmitir información, CEUTIA debe verificar:

* autorización;
* clasificación;
* contexto;
* destinatario;
* minimización;
* presencia de datos personales;
* riesgo de filtración;
* riesgo de inferencia;
* compatibilidad con la superficie PUBLIC.

Una salida válida para OWNER puede ser completamente inapropiada para PUBLIC.

⸻

25. Seguridad de modelos de IA

Los modelos de IA pueden introducir riesgos propios.

CEUTIA debe contemplar:

* prompt injection;
* data poisoning;
* model drift;
* hallucination;
* extracción de información;
* fuga de contexto;
* uso indebido de herramientas;
* manipulación de instrucciones;
* comportamiento no esperado;
* errores de clasificación;
* automatización excesiva.

Los modelos no deben recibir privilegios superiores a los estrictamente necesarios.

Una IA no debe poder modificar unilateralmente componentes críticos de seguridad.

⸻

26. Separación entre inferencia y decisión

La generación de una inferencia no debe equivaler automáticamente a una decisión operativa.

DATOS
 ↓
MODELO
 ↓
INFERENCIA
 ↓
INCERTIDUMBRE
 ↓
SEÑAL
 ↓
EVALUACIÓN
 ↓
DECISIÓN

Cuando el impacto potencial sea elevado, debe existir supervisión humana apropiada.

⸻

27. Seguridad de las señales

Cada señal debe poder conservar:

* identificador;
* timestamp;
* origen;
* variables relevantes;
* modelo utilizado;
* versión del modelo;
* nivel de confianza;
* incertidumbre;
* explicación;
* severidad;
* estado;
* destinatario;
* historial de cambios.

Una señal debe poder reconstruirse retrospectivamente.

⸻

28. Registro y auditoría

Los eventos relevantes deben generar registros de auditoría.

Entre ellos:

* autenticaciones;
* cambios de permisos;
* accesos sensibles;
* modificaciones de configuración;
* cambios de modelos;
* ingestión relevante;
* generación de señales;
* exportaciones;
* operaciones administrativas;
* eventos de seguridad;
* cambios en políticas.

Los logs deben protegerse contra modificación no autorizada.

La retención debe ser proporcional a las necesidades legales, operativas y de seguridad.

No debe almacenarse información sensible innecesaria en logs.

⸻

29. Detección de incidentes

La plataforma debe poder identificar comportamientos anómalos como:

* múltiples intentos fallidos;
* accesos inusuales;
* escalada de privilegios;
* extracción masiva;
* patrones anómalos de API;
* cambios inesperados de configuración;
* alteraciones de datos;
* anomalías en pipelines;
* comportamiento inesperado de modelos.

Los eventos deben poder clasificarse por severidad.

⸻

30. Respuesta ante incidentes

Debe existir un procedimiento documentado para:

DETECCIÓN
   ↓
CLASIFICACIÓN
   ↓
CONTENCIÓN
   ↓
ERRADICACIÓN
   ↓
RECUPERACIÓN
   ↓
ANÁLISIS FORENSE
   ↓
LECCIONES APRENDIDAS
   ↓
ACTUALIZACIÓN DE CONTROLES

Los incidentes epistemológicos deben investigarse igual que los incidentes técnicos cuando puedan haber alterado conclusiones o señales.

⸻

31. Resiliencia

CEUTIA debe diseñarse para continuar funcionando de forma segura ante fallos parciales.

Debe contemplar:

* degradación controlada;
* redundancia cuando corresponda;
* backups;
* recuperación;
* límites de dependencia;
* aislamiento de componentes;
* timeouts;
* circuit breakers;
* reintentos controlados;
* colas cuando proceda;
* recuperación ante corrupción.

Cuando no pueda garantizarse una salida fiable, el sistema debe preferir una respuesta segura antes que inventar información.

⸻

32. Fail-safe y fail-closed

En operaciones sensibles, la arquitectura debe favorecer estados seguros ante fallos.

Ejemplos:

FALLO DE AUTORIZACIÓN
→ DENEGAR
FALLO DE VALIDACIÓN
→ RECHAZAR
INFORMACIÓN CRÍTICA INCONSISTENTE
→ MARCAR INCERTIDUMBRE
MODELO NO DISPONIBLE
→ NO SIMULAR UNA PREDICCIÓN
FUENTE NO VERIFICADA
→ NO ELEVAR AUTOMÁTICAMENTE SU CONFIANZA

El comportamiento concreto dependerá de la función y del riesgo.

⸻

33. Seguridad de la infraestructura

La infraestructura debe aplicar, según el entorno:

* segmentación de red;
* aislamiento de servicios;
* mínimos privilegios;
* hardening;
* gestión de parches;
* imágenes verificadas;
* gestión de vulnerabilidades;
* control de dependencias;
* protección de endpoints;
* gestión de certificados;
* backups;
* monitorización.

La separación lógica entre componentes no debe describirse como un “air gap” si no existe una separación física real.

⸻

34. Dependencias y cadena de suministro

El proyecto debe controlar sus dependencias de software.

Se deben contemplar:

* versiones fijadas cuando proceda;
* actualización controlada;
* análisis de vulnerabilidades;
* revisión de dependencias;
* SBOM;
* procedencia de paquetes;
* detección de paquetes maliciosos;
* revisión de imágenes de contenedor;
* protección de CI/CD.

Un paquete externo debe considerarse una dependencia de confianza limitada, no una extensión automática del perímetro de seguridad.

⸻

35. CI/CD y cambios

Los cambios de código e infraestructura deben pasar por controles apropiados.

La arquitectura debe favorecer:

* revisión de cambios;
* pruebas automatizadas;
* análisis estático;
* análisis de dependencias;
* secret scanning;
* validación de configuración;
* control de versiones;
* despliegues reproducibles;
* rollback.

Los cambios de seguridad críticos deben quedar auditados.

⸻

36. Gestión de configuración

Las configuraciones sensibles deben estar centralizadas y versionadas cuando corresponda.

Debe distinguirse entre:

CÓDIGO
CONFIGURACIÓN
SECRETO
DATO

No deben mezclarse estas categorías.

Una variable de configuración pública no debe utilizarse como mecanismo para almacenar un secreto.

⸻

37. Privacidad por diseño

La privacidad debe formar parte de la arquitectura desde el inicio.

No debe añadirse únicamente después de construir el sistema.

El diseño debe considerar:

* minimización;
* separación;
* anonimización cuando sea posible;
* pseudonimización cuando proceda;
* control de acceso;
* retención;
* eliminación;
* transparencia;
* derechos de las personas;
* trazabilidad del tratamiento.

⸻

38. Retención y eliminación

Cada categoría de información debe tener una política de retención definida.

No debe conservarse información indefinidamente por defecto.

Debe existir una distinción entre:

* datos operativos;
* datos personales;
* datos agregados;
* logs;
* evidencia;
* modelos;
* auditoría;
* backups.

La eliminación debe ser compatible con las obligaciones legales y con las necesidades legítimas de auditoría.

⸻

39. Exportación de información

Las exportaciones constituyen una superficie de riesgo.

Deben existir controles sobre:

* quién exporta;
* qué exporta;
* por qué;
* a dónde;
* en qué formato;
* qué datos contiene;
* si incluye información personal;
* si incluye información restringida;
* cuánto tiempo permanece disponible.

Cuando sea necesario, las exportaciones deben quedar auditadas.

⸻

40. Monitorización

La observabilidad debe cubrir tanto infraestructura como comportamiento del sistema.

INFRAESTRUCTURA
      +
APLICACIÓN
      +
SEGURIDAD
      +
DATOS
      +
PIPELINES
      +
MODELOS
      +
EPISTEMOLOGÍA

Una caída de CPU puede ser un problema técnico.

Una modificación súbita de la distribución de los datos puede ser un problema epistemológico.

Ambos deben poder detectarse.

⸻

41. Límites de automatización

CEUTIA PUBLIC no debe automatizar decisiones de alto impacto simplemente porque una predicción tenga un score elevado.

La automatización debe estar limitada por:

* riesgo;
* incertidumbre;
* contexto;
* sensibilidad de los datos;
* impacto potencial;
* capacidad de revisión;
* posibilidad de intervención humana.

La plataforma debe distinguir entre:

AUTOMATIZACIÓN
ASISTENCIA
RECOMENDACIÓN
SEÑAL
ALERTA
DECISIÓN HUMANA

⸻

42. Principio de no manipulación

Las capacidades de análisis de CEUTIA PUBLIC no deben utilizarse para manipular deliberadamente a la población.

La personalización de información debe orientarse a:

* comprensión;
* prevención;
* promoción de la salud;
* reducción de incertidumbre;
* acompañamiento;
* desescalada;
* acceso a recursos.

No debe diseñarse una intervención cuyo objetivo sea explotar vulnerabilidades psicológicas de las personas.

⸻

43. Seguridad de la desescalada

La desescalada también requiere seguridad.

Una recomendación pública debe evaluarse respecto a su posible efecto.

El sistema debe evitar:

* amplificación innecesaria del miedo;
* lenguaje alarmista;
* generalizaciones sobre grupos;
* atribuciones causales no demostradas;
* exposición de individuos;
* difusión de rumores;
* publicación de información operacional sensible.

Cuando exista incertidumbre significativa, debe expresarse.

⸻

44. Gestión de errores

CEUTIA debe asumir que cometerá errores.

La arquitectura debe impedir que un error sea ocultado o propagado silenciosamente.

Debe ser posible identificar:

QUÉ FALLÓ
   ↓
CUÁNDO FALLÓ
   ↓
POR QUÉ FALLÓ
   ↓
QUÉ INFORMACIÓN UTILIZÓ
   ↓
QUÉ SALIDAS PRODUJO
   ↓
A QUIÉN AFECTÓ
   ↓
CÓMO SE CORRIGIÓ

⸻

45. Seguridad de la memoria histórica

La evolución del sistema debe conservarse de manera controlada.

Cuando un modelo cambie, debe poder determinarse:

* qué versión estaba activa;
* qué parámetros utilizaba;
* qué datos recibió;
* qué resultado produjo;
* cuándo fue sustituido;
* por qué fue sustituido.

Esto es necesario para evaluación, auditoría y reproducibilidad.

⸻

46. Control de versiones epistemológico

No solamente el código debe tener versiones.

También deben poder versionarse:

* ontologías;
* taxonomías;
* modelos;
* reglas;
* fuentes;
* políticas;
* criterios de alerta;
* bibliotecas de intervención;
* hipótesis;
* definiciones de indicadores.

Un cambio semántico puede producir consecuencias tan importantes como un cambio de código.

⸻

47. Principio de trazabilidad completa

Siempre que sea técnicamente posible, CEUTIA debe poder recorrer la cadena:

SALIDA
 ↓
MODELO
 ↓
HIPÓTESIS / REGLA
 ↓
EVIDENCIA
 ↓
DATOS
 ↓
FUENTE

Y en sentido inverso:

FUENTE
 ↓
DATOS
 ↓
EVIDENCIA
 ↓
MODELO
 ↓
SEÑAL
 ↓
SALIDA

La trazabilidad es un requisito fundamental para confiar en el sistema.

⸻

48. Seguridad frente a falsos positivos y negativos

La seguridad no consiste únicamente en evitar ataques.

También consiste en evitar que el sistema produzca intervenciones innecesarias o deje pasar situaciones relevantes.

Debe evaluarse:

* sensibilidad;
* especificidad;
* precisión;
* recall;
* falsos positivos;
* falsos negativos;
* calibración;
* coste del error;
* asimetría entre tipos de error.

Los umbrales no deben elegirse únicamente por conveniencia técnica.

Deben justificarse respecto al contexto y al riesgo.

⸻

49. Gestión de incertidumbre

La incertidumbre debe atravesar las capas del sistema.

DATOS
 ↓
INCERTIDUMBRE
 ↓
MODELO
 ↓
INCERTIDUMBRE
 ↓
PREDICCIÓN
 ↓
INCERTIDUMBRE
 ↓
SEÑAL
 ↓
INTERPRETACIÓN

Una señal con elevada incertidumbre no debe presentarse de la misma manera que una señal altamente corroborada.

⸻

50. Controles de seguridad de CEUTIA PUBLIC

Los controles deberán clasificarse explícitamente como:

IMPLEMENTADO
EN DESARROLLO
PLANIFICADO
EXPERIMENTAL
NO VERIFICADO
NO APLICABLE

La documentación nunca debe afirmar que un control existe simplemente porque está previsto.

Tampoco debe afirmarse una certificación, cumplimiento normativo o nivel de seguridad que no haya sido formalmente verificado.

⸻

51. Marco normativo

CEUTIA deberá determinar el marco jurídico aplicable en función de:

* finalidad;
* datos tratados;
* responsables y encargados;
* ubicación;
* usuarios;
* infraestructura;
* naturaleza de las decisiones;
* tratamiento de datos personales;
* tratamiento de datos de salud;
* utilización de IA;
* transferencias internacionales.

El sistema no debe declarar automáticamente certificaciones o conformidades que no hayan sido obtenidas y verificadas.

Los marcos de seguridad o buenas prácticas pueden utilizarse como referencia arquitectónica sin presentarlos como certificaciones.

⸻

52. Objetivo final de seguridad

La seguridad de CEUTIA PUBLIC no consiste únicamente en mantener el sistema inaccesible para un atacante.

Consiste en conseguir que:

LA PERSONA
   ↓
ESTÉ PROTEGIDA
EL DATO
   ↓
SEA ÍNTEGRO Y PROPORCIONAL
LA FUENTE
   ↓
SEA TRAZABLE
LA EVIDENCIA
   ↓
SEA EVALUABLE
EL MODELO
   ↓
SEA AUDITABLE
LA SEÑAL
   ↓
SEA INTERPRETABLE
LA RECOMENDACIÓN
   ↓
SEA SEGURA Y PROPORCIONADA
PUBLIC
   ↓
PERMANEZCA SEPARADO DE OWNER
Y TODO EL SISTEMA
   ↓
PUEDA SER RECONSTRUIDO, EVALUADO Y CORREGIDO

La seguridad es, por tanto, una propiedad transversal de CEUTIA PUBLIC: seguridad técnica, seguridad de los datos, seguridad de las personas y seguridad del conocimiento deben funcionar como un único sistema de control.