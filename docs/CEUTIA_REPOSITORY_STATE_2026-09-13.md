# CeutIA — Estado verificable del repositorio

**Fecha:** 2026-09-13  
**Rama:** `main`

## Regla de precedencia

Para determinar el estado real del sistema, el código y los artefactos ejecutables actuales tienen precedencia sobre documentación histórica. Una afirmación histórica que contradiga el repositorio actual no debe tratarse como estado vigente.

## `backend/app/core/metrics.py`

La versión actual de `metrics.py` ya no corresponde al artefacto concatenado de aproximadamente 18,3k líneas descrito en documentación anterior. El archivo actual es un módulo Python estructurado que comienza con un único módulo, imports y taxonomía explícita de métricas.

Por tanto, las siguientes afirmaciones históricas quedan retiradas como descripción del estado actual:

- aproximadamente 18.335 líneas;
- 807 definiciones de nivel superior;
- 673 símbolos únicos;
- 127 símbolos duplicados con semánticas distintas;
- módulo actualmente no importable por esa razón.

El antiguo inventario `docs/metrics_duplicate_inventory_skeleton.json` queda clasificado como **HISTÓRICO / NO AUTORITATIVO**. No se utilizará para reconstruir `metrics.py` sin volver a demostrar sus hallazgos sobre el código vigente.

## Estado epistemológico del núcleo

El módulo actual contiene mecanismos explícitos de clasificación y validación. Entre ellos se encuentra la separación entre estado de evidencia y probabilidad calibrada. La presencia de código no implica validación científica, calibración ni autorización operacional.

## Integración

`backend/app/core/system_integrator.py` contiene la implementación del screening auditable de proxy espacial introducida durante el ciclo 1.

Estado:

**IMPLEMENTED — NOT YET VALIDATED**

La implementación incluye bloqueo ante datos insuficientes y clasificación `PROXY_RISK`; el screening de asociación no constituye inferencia causal ni demuestra ausencia de sesgo.

## Documentación anterior

`docs/CEUTIA_MASTER_IMPLEMENTATION_SPECIFICATION.md` conserva valor como registro histórico de decisiones y restricciones de una fase anterior. Las afirmaciones de su sección de estado que describen el antiguo `metrics.py` no son el estado actual del repositorio.

## CI

`.github/workflows/ci.yml` mantiene ejecución automática para `push` a `main` y pull requests, y ahora admite también `workflow_dispatch`.

La ejecución comprueba:

- compilación de fuentes Python;
- instalación del proyecto y dependencias de desarrollo;
- suite completa de `pytest`;
- configuración de Docker Compose.

El último commit de `main` tras la reconciliación documental y la actualización de CI es:

`d9f352808dede52c80bad181be95b3fa49edaa00`

**Importante:** la interfaz GitHub disponible para esta sesión no expone de forma utilizable las ejecuciones `push` del workflow; por tanto, no se declara aquí un resultado `PASS` o `FAIL` que no haya sido observado. La ejecución CI queda habilitada y reproducible, pero su resultado debe verificarse en GitHub Actions.

## Próxima condición de avance

Antes de modificar estructuralmente `metrics.py`:

1. ejecutar CI;
2. ejecutar los tests de integridad específicos del núcleo;
3. generar un inventario reproducible del código actual;
4. determinar si existen realmente duplicaciones semánticas en la versión vigente;
5. reconciliar cualquier documentación adicional que contradiga el código;
6. solo después decidir si existe alguna necesidad real de refactorización estructural.
