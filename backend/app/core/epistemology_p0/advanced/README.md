# P2 — Capacidad avanzada

| Módulo | Rol |
|--------|-----|
| `semantic_graph.py` | Grafo SOURCE→DOCUMENT→CLAIM→EVIDENCE (+ variables) |
| `ingestion.py` | Ingesta masiva con validación de procedencia |
| `backtesting.py` | Cortes temporales sin contaminación retrospectiva |
| `predictive_stub.py` | Consumidor predictivo **acotado** (hipótesis, no verdad) |

## Límites

- No llama a OpenAI/DeepSeek/Llama ni a ningún LLM.
- No toca `metrics.py`.
- La predicción del stub es heurística y sale como `HYPOTHESIS` / `UNVERIFIED`.
- CeutIA no resuelve contradicciones ni afirma causalidad.

## Tests

```bash
pytest tests/core/test_p2_advanced.py -v
```
