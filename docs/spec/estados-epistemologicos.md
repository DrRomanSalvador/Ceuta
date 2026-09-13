# Estados epistemológicos permitidos — CeutIA

**Document class:** Closed vocabulary contract
**Authority:** Binding. No other epistemic state labels are authorised.

---

## Closed set

| Estado | Definición operativa |
|--------|----------------------|
| `NO_VERIFICADO` | No se ha ejecutado verificación reproducible |
| `INSUFICIENTE` | Datos presentes pero insuficientes para evaluación válida |
| `PROXY_RISK` | Señal se comporta como proxy de composición; promoción bloqueada |
| `CONSISTENTE` | Evidencias independientes alineadas bajo el método declarado |
| `CONTRADICTORIO` | Evidencias independientes en conflicto material |
| `DEPENDIENTE` | Fuentes no independientes (derivativas o compartidas) |
| `TEMPORAL_LEAKAGE` | Información futura o fuera de ventana temporal contaminó el análisis |
| `BLOQUEADO` | Condición fail-closed activada; no se emite conclusión operacional |
| `VALIDADO` | Verificación reproducible registrada y aprobada |

---

## Reglas de uso

1. Todo artefacto que emita un estado epistemológico debe usar exactamente una etiqueta de este conjunto.
2. `VALIDADO` solo puede asignarse tras evidencia registrada de ejecución exitosa.
3. `PROXY_RISK` y `BLOQUEADO` impiden promoción operacional.
4. Ningún agente puede inventar estados adicionales.
