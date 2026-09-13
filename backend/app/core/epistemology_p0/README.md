# CeutIA — Capa Epistemológica (P0)

**Rama:** `p0-epistemic-foundations`  
**Ubicación:** `backend/app/core/epistemology_p0/` (paquete aislado, aplanado)

## Por qué aquí

- Aislado de `metrics.py`, `epistemic.py` y `models.py` legacy (enums distintos; no se sobrescriben).
- Misma raíz `backend/app/core/` que el resto del dominio, pero en subpaquete dedicado.
- Tests en `tests/core/test_epistemology_p0.py` (mismo patrón del proyecto).
- Cuando P0 esté estable, se puede promover a `backend/app/epistemology/` como capa canónica.

## Estructura

```
epistemology_p0/
├── epistemology/states.py     # Máquina de estados tipados
├── evidence/models.py         # Evidence versionado e inmutable
├── sources/independence.py    # Grafo de independencia de fuentes
├── temporal/multitemporal.py  # Modelo temporal + backtesting
├── contracts/ceutia_serpiente.py  # Observation + pull_context
├── schemas/observation_v1.json
├── registry.py                # ClaimRegistry (aplanado, no core/core)
└── __init__.py
```

## Regla central

> Ninguna salida de CeutIA debe perder significado, procedencia, incertidumbre, temporalidad ni estado epistemológico al llegar a Serpiente.

## MUST NOT TOUCH (esta rama)

- `backend/app/core/metrics.py`
- `backend/app/core/epistemic.py` (enum legacy distinto)
- `backend/app/core/models.py`
- Gobernanza y seguridad ya consolidadas

## Tests

```bash
pytest tests/core/test_epistemology_p0.py -v
```
