# CeutIA — Capa Epistemológica (P0 Foundations)

Implementación de los fundamentos de la auditoría de separación CeutIA / Serpiente.

**Rama:** `p0-epistemic-foundations`  
**Repo:** `drsalvadorroman-beep/Ceuta`  
**Regla central:** ninguna salida de CeutIA debe perder significado, procedencia, incertidumbre, temporalidad ni estado epistemológico al llegar a Serpiente.

## Qué se ha implementado (P0)

| Módulo | Contenido |
|--------|-----------|
| `epistemology/states.py` | Máquina de estados tipados + transiciones válidas |
| `temporal/multitemporal.py` | 7 tiempos distintos + filtro backtesting |
| `sources/independence.py` | Grafo de independencia (red, no contador) |
| `schemas/observation_v1.json` | Contrato versionado CeutIA→Serpiente |
| `contracts/` | Observation, pull_context, ContextDossier |

## Estados epistemológicos tipados

`ATTRIBUTED_CLAIM` → estado inicial de toda afirmación de una sola fuente.  
Solo pasa a `CORROBORATED_FACT` con evidencia independiente documentada.  
Las correcciones **nunca sobrescriben**: crean nueva versión.

## MUST NOT TOUCH

- `metrics.py` del core legacy (inventario de 127 duplicados pendiente)
- Documentación de gobernanza / seguridad ya consolidada

## Tests

Los tests P0 viven en `tests/test_p0_foundations.py` (pendiente de subir en este commit si no está). Cubren:

- Afirmación única fuente → ATTRIBUTED_CLAIM
- Diez documentos del mismo comunicado → peso ≈ 1
- Contradicciones explícitas
- Backtest sin contaminación retrospectiva
- Observation no entrega escalares desnudos

## Siguiente (P1)

1. Completar `evidence/models.py` (Evidence versionado e inmutable)
2. Completar `core/registry.py` (ClaimRegistry + linaje)
3. Completar contrato `contracts/ceutia_serpiente.py`
4. Tests E2E
5. Integrar sin tocar metrics.py
