# P1 — Integración operativa

Capa sobre `epistemology_p0` que conecta el núcleo epistemológico con consumidores (p.ej. Serpiente) **sin** convertir claims en predicciones ni tocar `metrics.py`.

## Componentes

| Módulo | Función |
|--------|--------|
| `bridge.py` | Evidence → Observation contractual + `model_weight` |
| `uncertainty.py` | Propagación e intervalos; peso por confianza/dependencia |
| `versioning.py` | Registro append-only de versiones (data/rule/model/schema) |
| `context_service.py` | `pull_context` → ContextDossier con hipótesis rivales |

## Flujo

```
ClaimRegistry / Evidence
        │
        ▼
ObservationBridge.emit → Observation (+ model_weight)
        │
        ▼
   [consumidor / Serpiente]
        │ anomalía
        ▼
ContextService.pull_context → ContextDossier
        │
        ▼
  revisión humana (si procede)
```

## Tests

```bash
pytest tests/core/test_p1_operational.py -v
```
