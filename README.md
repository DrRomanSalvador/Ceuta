# CEUTIA — README maestro para GitHub

A continuación tienes **exactamente** lo que debes pegar en tu repositorio GitHub como `README.md`. Este documento está diseñado para ser:

- **Idóneo**: técnicamente preciso y alineado con la especificación del dossier.
- **Excelente**: claro para colaboradores, auditores y futuros desarrolladores.
- **Magnífico**: útil como contrato arquitectónico y punto de partida para la implementación.

Después del README encontrarás una **lista de comprobación cloud** con lo que debes hacer en tu proveedor cloud (Clouding u otro) para que la arquitectura funcione en producción.

***

## `README.md` para GitHub

```markdown
# CEUTIA

**Infraestructura de inteligencia territorial, análisis de riesgos y reflexión ciudadana centrada en Ceuta.**

CEUTIA no es una web informativa ni un chatbot. Es un sistema vivo de conocimiento epistemológico que:

- Recopila información exclusivamente de **fuentes autorizadas y trazables**.
- Conserva **procedencia, fecha, naturaleza y nivel de evidencia** de cada afirmación.
- Diferencia **hechos, declaraciones, inferencias, hipótesis, probabilidades, riesgos y escenarios**.
- Detecta **corroboraciones, contradicciones, independencia de fuentes y evolución temporal**.
- Mantiene **hipótesis competidoras** con evidencia favorable, desfavorable y falsadora.
- Analiza dominios separados: desinformación, influencia, polarización, violencia, ambiente, frontera y riesgo territorial integrado.
- Ofrece **dos salidas completamente separadas**:
  - **Capa pública**: comprensión, reflexión y bienestar ciudadano.
  - **Capa Owner**: radar territorial, alertas, escenarios y auditoría privada.

**Principio fundamental:**

> No decir a las personas qué deben pensar sobre Ceuta, sino hacer visible qué sabemos, qué no sabemos, qué evidencia tenemos, qué interpretaciones son posibles y cómo está cambiando la situación.

---

## Tabla de contenidos

1. [Arquitectura](#arquitectura)
2. [Dominios](#dominios)
3. [Capa pública vs Owner](#capa-pública-vs-owner)
4. [Modelo epistemológico](#modelo-epistemológico)
5. [Hipótesis competidoras](#hipótesis-competidoras)
6. [Trazabilidad y auditoría](#trazabilidad-y-auditoría)
7. [Seguridad](#seguridad)
8. [GitHub y organización del código](#github-y-organización-del-código)
9. [Cloud y entornos](#cloud-y-entornos)
10. [MVP y fases](#mvp-y-fases)
11. [Contribuir](#contribuir)
12. [Licencia](#licencia)

---

## Arquitectura

CEUTIA se organiza en capas:

```text
┌──────────────────────────────────────────┐
│              USUARIOS                    │
└────────────────┬─────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
┌─────▼─────┐         ┌─────▼──────┐
│ PÚBLICO   │         │ OWNER      │
│ ciudadano │         │ privado    │
└─────┬─────┘         └─────┬──────┘
      │                     │
      ▼                     ▼
┌─────────────┐       ┌─────────────┐
│ Public API  │       │ Owner API   │
└─────┬───────┘       └─────┬───────┘
      │                     │
      └──────────┬──────────┘
                 ▼
      ┌──────────────────────┐
      │ APPLICATION LAYER    │
      ├──────────────────────┤
      │ Knowledge Engine     │
      │ AI / RAG Layer       │
      │ Analytics Engine     │
      │ Output Policy        │
      └──────────┬───────────┘
                 ▼
      ┌──────────────────────┐
      │ EPISTEMIC CORE       │
      ├──────────────────────┤
      │ Sources              │
      │ Documents            │
      │ Observations         │
      │ Evidence             │
      │ Claims               │
      │ Provenance           │
      │ Independence         │
      │ Corroboration        │
      │ Contradiction        │
      │ Hypotheses           │
      │ Indicators           │
      │ Evaluations          │
      │ Temporal versions    │
      └──────────┬───────────┘
                 ▼
      ┌──────────────────────┐
      │ DATA LAYER           │
      ├──────────────────────┤
      │ Structured database  │
      │ Document storage     │
      │ Optional vectors     │
      │ Audit/log storage    │
      └──────────▲───────────┘
                 │
      ┌──────────┴───────────┐
      │ INGESTION SYSTEM     │
      └──────────┬───────────┘
                 ▼
      ┌──────────────────────┐
      │ AUTHORIZED SOURCES   │
      └──────────────────────┘
```

La IA opera como una capa subordinada al núcleo epistemológico. No debe existir el salto:

```text
Documento → LLM → verdad
```

---

## Dominios

CEUTIA analiza diez dominios que comparten el mismo núcleo epistemológico:

1. **Estado epistemológico**: qué está documentado, qué se afirma, qué permanece incierto.
2. **Desinformación**: rumores, falsedades, información engañosa.
3. **Manipulación e influencia**: coordinación, amplificación, instrumentalización.
4. **Polarización y convivencia**: hostilidad, deshumanización, deterioro de la convivencia.
5. **Violencia y escalada**: amenazas, incidentes, movilización, reciprocidad.
6. **Riesgo ambiental**: incendios, contaminación, fenómenos extremos.
7. **Riesgo fronterizo/geopolítico**: frontera, migración, Marruecos, actividad institucional.
8. **Riesgo territorial integrado**: convergencias, anomalías, escenarios.
9. **Experiencia humana/emocional**: módulo voluntario de reflexión y bienestar.
10. **Salud/médico**: información sanitaria y consulta profesional opcional.

Cada dominio conserva sus propios indicadores y evaluaciones, pero comparte el mismo modelo de fuentes, evidencias, afirmaciones e hipótesis.

---

## Capa pública vs Owner

### Capa pública

El ciudadano puede recibir:

- Respuestas verificables.
- Fuentes, fechas y nivel de evidencia.
- Contradicciones e incertidumbre.
- Herramientas de reflexión.
- Módulo emocional voluntario.
- Información general de salud.
- Posibilidad de solicitar consulta médica.

**Nunca recibe:**

- Clasificaciones internas sobre su propia interacción.
- Puntuaciones de desinformación, influencia, polarización u hostilidad.
- Evaluaciones individuales de riesgo.
- Radar territorial ni alertas privadas.
- Hipótesis internas no publicadas.
- Reglas, umbrales, prompts o metadatos sensibles.

### Capa Owner

El Owner puede acceder a:

- Evidencia primaria.
- Contradicciones y hipótesis competidoras.
- Señales débiles, baselines y anomalías.
- Convergencias entre dominios.
- Tendencias y evaluaciones privadas.
- Riesgos multidimensionales y escenarios.
- Alertas explicables y auditables.
- Configuración de fuentes, reglas y modelos.
- Historial temporal y auditoría completa.

### Módulo médico

El módulo médico tiene un perímetro independiente. La información sanitaria voluntaria **no** se utiliza para inferir la veracidad de las opiniones de una persona ni para construir inteligencia territorial individual.

---

## Modelo epistemológico

La unidad fundamental no es el documento, es la **afirmación (Claim)**.

### Entidades principales

#### Source

```text
Source
- id
- name
- type
- origin
- authorization_status
- reliability_assessment
- independence_group
- created_at
- updated_at
```

#### Document

```text
Document
- id
- source_id
- title
- publication_date
- retrieval_date
- content_location
- checksum
- version
- status
```

#### Observation

```text
Observation
- id
- document_id
- extracted_content
- temporal_reference
- extraction_method
```

#### Evidence

```text
Evidence
- id
- observation_id
- evidence_type
- directness
- relevance
- quality
```

#### Claim

```text
Claim
- id
- text
- claim_type
- temporal_scope
- status
- first_observed_at
- last_updated_at
- current_version
```

Tipos de `claim_type`:

```text
FACT
QUANTITATIVE_DATA
SOURCE_ASSERTION
DIRECT_EVIDENCE
INDIRECT_EVIDENCE
INFERENCE
HYPOTHESIS
PREDICTION
OPINION
UNVERIFIED
CONTRADICTED
```

---

## Hipótesis competidoras

Para cada fenómeno relevante, CEUTIA mantiene hipótesis competidoras:

```text
Hypothesis
- id
- phenomenon_id
- statement
- prior_evaluation
- current_evaluation
- probability
- confidence
- uncertainty
- status
- evaluation_date
- version
```

Relaciones:

```text
HypothesisEvidence
- hypothesis_id
- evidence_id
- polarity  (SUPPORTING, OPPOSING, NEUTRAL, FALSIFYING)
- strength
- rationale
```

El sistema busca activamente:

- Evidencia favorable.
- Evidencia desfavorable.
- Posibles falsadores.
- Observaciones esperadas.
- Explicaciones alternativas.

---

## Trazabilidad y auditoría

La procedencia debe poder reconstruirse así:

```text
ANSWER
 ↓
OUTPUT POLICY
 ↓
EVALUATION
 ↓
CLAIM
 ↓
EVIDENCE
 ↓
OBSERVATION
 ↓
DOCUMENT
 ↓
SOURCE
```

Cada respuesta importante conserva:

- Pregunta o entrada.
- Documentos recuperados.
- Fuentes.
- Versiones (sistema, modelo, prompt, índice).
- Clasificaciones e inferencias.
- Respuesta generada.
- Fecha.
- Política de salida aplicada.

Las evaluaciones se versionan. Nunca se sobrescribe silenciosamente una evaluación anterior.

---

## Seguridad

- **Allowlist estricta de fuentes**: solo dominios autorizados.
- **Denylist configurable** por Owner.
- **Protección SSRF** y validación de redirects.
- **Documentos tratados como datos**, nunca como instrucciones.
- **Protección contra prompt injection**.
- **Secretos exclusivamente en backend**, fuera del repositorio.
- **Mínima conservación de información personal**.
- **Separación técnica** entre datos públicos, administrativos y sanitarios.
- **Control de acceso por recurso** y principio de mínimo privilegio.
- **Model gateway**: los frontends no contactan directamente con modelos cuando existe información sensible.

### Prueba crítica de aislamiento

Debe comprobarse que:

```text
PRIVATE_SECRET = "TEST OWNER DATA"
public query → nunca devuelve PRIVATE_SECRET
```

Incluso ante reformulaciones, resúmenes, prompt injection o consultas indirectas.

---

## GitHub y organización del código

**INFORMACIÓN FALTANTE:** las fuentes no indican qué repositorio GitHub existe actualmente. La siguiente estructura es una **propuesta** para un monorepo inicial.

```text
ceutia/
├── apps/
│   ├── public-web/
│   └── owner-web/
├── services/
│   ├── public-api/
│   ├── owner-api/
│   ├── ingestion/
│   ├── epistemic-engine/
│   ├── ai/
│   └── analytics/
├── packages/
│   ├── schemas/
│   ├── auth/
│   ├── provenance/
│   ├── permissions/
│   └── shared/
├── database/
│   ├── migrations/
│   └── seeds/
├── infrastructure/
├── docs/
│   ├── architecture/
│   ├── security/
│   └── epistemology/
├── tests/
├── config/
└── README.md
```

### Separación de artefactos

| Elemento | GitHub | Producción |
|---|---:|---|
| Código | Sí | Código desplegado |
| Esquemas | Sí | Migraciones aplicadas |
| Configuración no secreta | Sí | Inyectada por entorno |
| Datos | No | Base de datos / storage |
| Documentos | No | Object/document storage |
| Modelos externos | No | Registry o proveedor |
| Secrets | Nunca | Secret manager |
| Logs | No | Sistema de observabilidad |
| Backups | No | Almacenamiento de backup |
| Infraestructura declarativa | Sí | Recursos cloud |

---

## Cloud y entornos

**INFORMACIÓN FALTANTE:** no constan proveedor cloud, región, base de datos, almacenamiento, autenticación, IA, sistema de despliegue, dominio, DNS ni observabilidad. La siguiente arquitectura es **abstracta** y debe adaptarse a tu proveedor concreto.

```text
DNS
 ├── Public frontend
 └── Owner frontend

Public frontend
 └── Public API
      ├── Public projection
      └── Public RAG

Owner frontend
 └── Owner API
      ├── Private knowledge
      ├── Analytics
      ├── Alerts
      └── Audit

Data layer
 ├── Structured database
 ├── Document/object storage
 ├── Optional vector index
 └── Audit/log storage
```

### Entornos

```text
DEVELOPMENT
    ↓
PULL REQUEST
    ↓
CI
    ↓
STAGING
    ↓
TESTS / EVALUATION / SECURITY
    ↓
APPROVAL
    ↓
PRODUCTION
```

Debe cumplirse:

```text
DEV DATA      ≠ STAGING DATA      ≠ PRODUCTION DATA
DEV SECRETS   ≠ STAGING SECRETS   ≠ PROD SECRETS
```

---

## MVP y fases

### MVP imprescindible

1. Frontend público.
2. Frontend Owner.
3. Autenticación.
4. Autorización real.
5. Registro de fuentes.
6. Ingestión documental.
7. Base de datos estructurada.
8. Procedencia.
9. Evidencias.
10. Afirmaciones.
11. Independencia de fuentes.
12. Contradicciones.
13. Confianza e incertidumbre.
14. Versionado temporal.
15. Separación Público/Owner.
16. RAG básico.
17. Auditoría.
18. Gestión de secretos.
19. Entornos separados.
20. CI/CD básico.

### Núcleo mínimo

```text
SOURCE
 ↓
DOCUMENT
 ↓
EVIDENCE
 ↓
CLAIM
 ↓
PROVENANCE
 ↓
CORROBORATION / CONTRADICTION
 ↓
CONFIDENCE / UNCERTAINTY
 ↓
PUBLIC ANSWER
```

### Fases posteriores

1. Motor de hipótesis y alternativas.
2. Observaciones esperadas y falsadores.
3. Indicadores y detección de cambios temporales.
4. Baselines, anomalías y convergencias.
5. Riesgo territorial integrado.
6. Escenarios y alertas.
7. Análisis avanzado (grafo, anomalías, forecasting).
8. Radar ambiental.
9. Radar fronterizo/geopolítico.
10. Intervención pública A–G (cuando se recupere su definición exacta).
11. Módulos emocionales, de salud y médico con aislamiento propio.

---

## Contribuir

CEUTIA está diseñado para ser:

- **Reproducible**: cualquier persona puede reconstruir el estado del sistema en una fecha dada.
- **Auditable**: cada evaluación puede trazarse hasta sus fuentes originales.
- **Transparente**: se muestra qué se sabe, qué no se sabe y cómo cambia el conocimiento.
- **Seguro**: separación estricta entre capas pública, Owner y médica.

Si deseas contribuir, lee primero la documentación en `docs/` y respeta los principios epistemológicos y de seguridad definidos en este proyecto.

---

## Licencia

[Indica aquí la licencia que elijas para el proyecto.]
```

***

## Qué hacer en Clouding (o tu proveedor cloud)

**HECHO CONOCIDO:** estás desarrollando con GitHub y servicios cloud.  
**INFORMACIÓN FALTANTE:** no constan proveedor concreto, región, base de datos, almacenamiento, autenticación, IA, dominio, DNS ni observabilidad. Por tanto, no puedo darte instrucciones específicas de un proveedor sin asumir tecnologías.

A continuación tienes una **lista de comprobación genérica** que debes ejecutar en Clouding (o equivalente):

### 1. Crear recursos básicos

- [ ] **Base de datos estructurada** (PostgreSQL u otra compatible):
  - Instancia separada para producción.
  - Usuarios y roles diferenciados para:
    - `public_api`
    - `owner_api`
    - `medical` (si aplica)
  - Backups automáticos y retenidos según política.
- [ ] **Almacenamiento de documentos** (object storage):
  - Bucket o contenedor para documentos crudos.
  - Bucket o contenedor para documentos procesados (chunks, metadatos).
  - Políticas de acceso diferenciadas (público vs privado).
- [ ] **Índice vectorial** (opcional, para RAG):
  - Servicio de vectores o base de datos con soporte vectorial.
  - Índices separados para:
    - Conocimiento público.
    - Conocimiento privado Owner.
    - Datos médicos (si se implementan).
- [ ] **Aplicación / computación**:
  - Entorno para desplegar:
    - `public-api`
    - `owner-api`
    - `ingestion`
    - `epistemic-engine`
    - `ai`
    - `analytics`
  - Posibilidad de ejecutar tareas programadas (cron/jobs) para ingestión y monitorización.

### 2. Separar entornos

- [ ] Crear **tres entornos** claramente separados:
  - `development`
  - `staging`
  - `production`
- [ ] Para cada entorno:
  - Base de datos independiente.
  - Almacenamiento independiente.
  - Variables de entorno y secretos independientes.
  - Credenciales de IA, autenticación y otros servicios independientes.
- [ ] Asegurar que:
  - El código en `production` solo usa secretos de producción.
  - No hay conexión cruzada entre entornos.

### 3. Gestionar secretos

- [ ] Usar un **secret manager** del proveedor o equivalente:
  - Claves de base de datos.
  - Credenciales de object storage.
  - Tokens de IA / modelos.
  - Credenciales de autenticación.
  - Canales de alerta (por ejemplo, Telegram, email, etc.).
- [ ] **Nunca** subir secretos a GitHub.
- [ ] Configurar acceso a secretos solo para los servicios que los necesiten.

### 4. Redes y seguridad

- [ ] Configurar **redes privadas** para:
  - Base de datos.
  - Almacenamiento sensible.
  - Servicios internos (APIs, ingestión, analytics).
- [ ] Exponer únicamente:
  - Frontend público.
  - Frontend Owner (con autenticación).
  - APIs necesarias según política de acceso.
- [ ] Implementar:
  - Firewall / reglas de seguridad.
  - Restricción de IPs si procede.
  - TLS/HTTPS para todos los endpoints públicos.

### 5. CI/CD

- [ ] Conectar GitHub con tu proveedor cloud o con un sistema CI/CD:
  - Pipeline que:
    - Ejecute tests.
    - Despliegue en `staging`.
    - Permita aprobación manual.
    - Despliegue en `production`.
- [ ] Asegurar que:
  - Cada despliegue registra la versión del sistema.
  - Las migraciones de base de datos se aplican de forma controlada.
  - Los secretos no se exponen en logs de CI/CD.

### 6. Observabilidad y auditoría

- [ ] Configurar:
  - Logs centralizados de aplicaciones y APIs.
  - Métricas de rendimiento y disponibilidad.
  - Alertas técnicas (errores, latencia, uso de recursos).
- [ ] Implementar una tabla o sistema de **auditoría** en la base de datos:
  - Registro de accesos a datos Owner.
  - Cambios de configuración.
  - Creación/modificación de alertas.
  - Versiones de modelos, prompts e índices.

### 7. Dominio y DNS

- [ ] Registrar un dominio (si aún no lo tienes).
- [ ] Configurar DNS para:
  - `app.ceutia...` → frontend público.
  - `owner.ceutia...` → frontend Owner.
  - Subdominios o rutas para APIs si procede.
- [ ] Asegurar certificados TLS válidos.

### 8. Validación final

Antes de considerar el despliegue completo:

- [ ] Comprobar que:
  - Una consulta pública **nunca** puede acceder a datos Owner.
  - Una consulta Owner **no** puede modificar configuración sin autorización.
  - Los datos médicos (si existen) están aislados.
- [ ] Ejecutar pruebas de:
  - Prompt injection.
  - SSRF.
  - Extracción de información privada.
  - Escalada de privilegios.

***

## Resumen de lo que debes hacer ahora

1. **En GitHub:**
   - Crea un repositorio `ceutia` (o usa el existente).
   - Pega el contenido del bloque `README.md` anterior como archivo `README.md` en la raíz.
   - Crea la estructura de directorios propuesta (puedes empezar con un esqueleto mínimo).

2. **En Clouding (o tu cloud):**
   - Crea:
     - Una base de datos.
     - Un almacenamiento de objetos.
     - Un entorno de computación para las APIs y servicios.
   - Separa claramente:
     - `development`, `staging`, `production`.
   - Configura secretos, redes y CI/CD según la lista de comprobación.

3. **Próximo paso técnico:**
   - Una vez tengas el README en GitHub y la infraestructura básica en cloud, el siguiente artefacto lógico es la **CEUTIA MASTER SPEC v1.0**, que convertirá esta arquitectura en un contrato detallado de:
     - Esquemas de base de datos.
     - Definición exacta de APIs.
     - Políticas de seguridad.
     - Criterios de aceptación y pruebas.

Si quieres, en el siguiente mensaje puedo generarte directamente:

- El esqueleto inicial de la base de datos (tablas principales en SQL).
- La definición OpenAPI de las APIs `/public` y `/owner`.
- Un primer borrador de la MASTER SPEC v1.0 listo para pegar en `docs/architecture/`.

Sources

