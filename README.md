# CeutIA

## Estado real del repositorio — 2026-09-14

**Estado de ingeniería:** IMPLEMENTADO PARCIALMENTE — VALIDACIÓN CONTINUA

Este README describe el estado actual observado del repositorio. Las referencias históricas a una versión concatenada de `backend/app/core/metrics.py` de aproximadamente 18,3k líneas y 127 símbolos duplicados quedan **obsoletas** para el estado actual de `main` y no deben utilizarse como descripción del código vigente.

### Núcleo matemático

`backend/app/core/metrics.py` existe actualmente como un módulo Python coherente y contiene el catálogo matemático y motor determinista de métricas de CeutIA. El archivo actual ya no corresponde al artefacto concatenado descrito en documentación anterior.

La existencia del módulo y de sus definiciones no implica que todas las métricas estén validadas para CeutIA, calibradas, autorizadas para uso operacional o aptas para producir riesgo. El propio módulo mantiene estados epistemológicos y restricciones de uso.

La antigua hipótesis de reconstrucción de `metrics.py` basada en 127 duplicados debe considerarse **histórica**. No se debe ejecutar ninguna reconstrucción basada en ese inventario sin volver a demostrar que las duplicaciones existen en el código actual.

### Estado de integración

Existe una capa de integración en `backend/app/core/system_integrator.py`. El primer ciclo de ingeniería ha añadido un screening auditable de proxy espacial que:

- compara asociación señal ↔ composición;
- compara asociación señal ↔ fenómeno objetivo;
- utiliza asociación parcial señal ↔ fenómeno objetivo controlando por composición cuando los datos lo permiten;
- bloquea cuando la muestra es insuficiente o los datos no permiten una evaluación válida;
- clasifica condiciones de proxy como `PROXY_RISK` sin convertirlas en causalidad ni en prueba de ausencia de sesgo.

La implementación está cubierta por pruebas automatizadas. La ejecución de la suite completa en el commit `e46b1826f4465e2ad71fc992ea69d51513b99eff` terminó correctamente; esto verifica ejecución e integración de código, pero no constituye validación científica, calibración ni autorización operacional de la señal.

### Evidencia y epistemología

CeutIA debe mantener separadas observación, evidencia, afirmación, inferencia, hipótesis, señal, predicción y riesgo. La confianza de evidencia no debe confundirse con probabilidad del evento. Las fuentes derivativas no deben contarse como evidencia independiente.

El motor epistemológico existente utiliza estados explícitos y no emite una probabilidad calibrada salvo que sea suministrada por un modelo calibrado independiente.

### CI y controles automáticos

`.github/workflows/validation-on-push.yml` ejecuta en cada `push` a `main`:

1. compilación de las fuentes Python;
2. instalación del proyecto y dependencias de desarrollo;
3. suite completa de `pytest`;
4. pruebas de integridad de runtime;
5. validación de `docker compose config`.

`.github/workflows/security-control-plane.yml` ejecuta ahora también en `push` a `main` y `pull_request`, además de `workflow_dispatch`, los controles del control plane protegido, las regresiones de seguridad, los contratos P0/temporales, los esquemas JSON v1 y los análisis estáticos.

El workflow `.github/workflows/ci.yml` conserva la ejecución manual de la batería ampliada de invariantes de fases y contratos avanzados.

Una ejecución automatizada es evidencia del estado del commit concreto que ejecuta; no debe extrapolarse a commits posteriores sin una nueva ejecución.

### Documentación histórica

`docs/CEUTIA_MASTER_IMPLEMENTATION_SPECIFICATION.md` contiene decisiones y restricciones de una fase anterior de reconstrucción de `metrics.py`. Sus afirmaciones sobre el estado del núcleo deben interpretarse como **históricas** cuando contradigan el código actual.

`docs/metrics_duplicate_inventory_skeleton.json` es igualmente un artefacto histórico de inventario y no constituye evidencia de duplicaciones presentes en la versión actual de `metrics.py`.

El estado actual y los cambios iterativos se registran en:

- `docs/ENGINEERING_EXECUTION_STATUS.md`
- `docs/CEUTIA_REPOSITORY_STATE_2026-09-13.md`

### Regla de ingeniería

El código actual es la fuente primaria para determinar qué existe realmente. La documentación debe reconciliarse con el repositorio y nunca utilizarse para inventar capacidades ausentes.

Estados permitidos:

- `IMPLEMENTED`
- `PARTIALLY IMPLEMENTED`
- `IMPLEMENTED — NOT YET VALIDATED`
- `REQUIRES VALIDATION`
- `EXTERNAL DEPENDENCY`
- `KNOWN LIMITATION`
- `EXPERIMENTAL`

Una capacidad solo puede considerarse operacional cuando implementación, pruebas, integración, observabilidad, seguridad y validación suficiente hayan sido demostradas.