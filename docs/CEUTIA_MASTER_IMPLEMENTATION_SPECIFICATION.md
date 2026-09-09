# CEUTIA — MASTER IMPLEMENTATION SPECIFICATION

**Estado:** BORRADOR DE GOBIERNO — 2026-09-09  
**Alcance:** reconstrucción del núcleo matemático (`metrics.py`) + defensa verificable contra proxy geográfico de hostilidad  
**Principio rector:**  
DOCUMENTADO ≠ IMPLEMENTADO ≠ EJECUTABLE ≠ VERIFICADO ≠ VALIDADO ≠ CALIBRADO ≠ OPERACIONAL

Este documento no sustituye la doctrina (`CEUTIA_MASTER_OPERATING_DOCTRINE.md`), la ontología ni la arquitectura.  
Gobierna **cómo** se reconstruye el código existente sin pérdida semántica y **qué** debe existir antes de cualquier promoción de señales sensibles.

---

## 1. Estado real del repositorio (contrato)

| Dimensión | Estado |
|-----------|--------|
| Documentado | Sí |
| Diseñado | Sí |
| Implementado (código presente) | Parcial |
| Importable | No garantizado |
| Ejecutable | No |
| Testeado | No |
| Verificado | No |
| Validado | No |
| Calibrado | No |
| Operacional | **No** |

**Motivo factual:**  
`backend/app/core/metrics.py` (~18.335 líneas) es un artefacto concatenado de bloques aditivos. Contiene 807 definiciones de nivel superior, 673 símbolos únicos y **127 símbolos duplicados con semánticas distintas**. El módulo no importa de forma fiable. Ninguna capacidad preventiva ha sido demostrada en runtime.

---

## 2. Regla de no reescritura sin inventario

**Prohibido** reescribir, consolidar o “limpiar” `metrics.py` eligiendo arbitrariamente la primera o la última definición de un símbolo duplicado.

Antes de cualquier modificación estructural se debe completar y versionar la **tabla de inventario semántico** de los 127 símbolos duplicados.

Para cada símbolo:

1. Localizar todas las ocurrencias (línea + firma).
2. Extraer la semántica real (ecuación, dominio, unidades, interpretación).
3. Clasificar:
   - **IDÉNTICA** → conservar una, eliminar la otra.
   - **EQUIVALENTE** → fusionar.
   - **PARCIALMENTE EQUIVALENTE** → especializar (renombrar o parametrizar).
   - **SEMÁNTICAMENTE DISTINTA** → **conservar ambas** con nombres canónicos distintos.
   - **INCOMPATIBLE** → resolver contradicción explícitamente.
4. Registrar la decisión y el nombre canónico propuesto.
5. Solo entonces proceder a la reconstrucción ordenada.

Una reconstrucción que salte este paso se considera **pérdida semántica no demostrada** y debe rechazarse.

---

## 3. Inventario semántico de casos críticos (demostrado)

| Símbolo | Ocurrencias | Semántica A | Semántica B / C | Clasificación | Decisión | Nombre canónico propuesto |
|---------|-------------|-------------|-----------------|---------------|----------|---------------------------|
| `adaptive_reserve` | 2 | Trayectoria dinámica \(R_t = R_{t-1} - L_t\,dt + G_t\,dt\) (estado) | Estática \(C - L\) | **DISTINTA** | Conservar ambas | `adaptive_reserve_trajectory` / `adaptive_reserve_static` |
| `cascade_depth` | 2 | Generaciones de matriz de activación (estructural) | Path depth desde nodo origen (NetworkX) | **DISTINTA** | Conservar ambas | `cascade_generation_depth` / `cascade_network_depth` |
| `coupling_strength` | 3 | Media absoluta off-diagonal de matriz | Correlación entre series / correlación retardada | **DISTINTA** | Conservar las tres | `coupling_matrix_strength` / `coupling_series_strength` / `coupling_lagged_strength` |
| `accumulated_load` | 2 | Integral \(\int L(t)\,dt\) | Carga con memoria exponencial (decay) | **DISTINTA** | Conservar ambas | `accumulated_load_integral` / `accumulated_load_decay` |
| `threshold_distance` | 2 | Distancia absoluta \(\|x - \theta\|\) | Distancia normalizada por escala | **PARCIAL** | Especializar | `threshold_distance` / `threshold_distance_scaled` |
| `recovery_fraction` | 3 | (pendiente de inventario completo) | | | | |
| `synchronization_index` | 3 | (pendiente) | | | | |
| `effective_capacity` | 3 | (pendiente) | | | | |
| `prevalence` | 3 | (pendiente) | | | | |
| … (resto de los 127) | | | | | | |

**Estado del inventario:** 5 casos críticos resueltos. 122 pendientes.  
**Bloqueo:** no se reescribe `metrics.py` hasta completar la tabla.

---

## 4. Defensa verificable contra proxy geográfico de hostilidad

### Problema

En un territorio de superficie pequeña y alta concentración espacial de flujos (Ceuta), una señal de “tensión / hostilidad / polarización” agregada por zona puede correlacionar fuertemente con composición demográfica o migratoria sin que ninguna variable prohibida aparezca explícitamente en el modelo. La geografía actúa como proxy.

Esto viola el principio fundamental de CeutIA:

> No inferir peligrosidad, criminalidad o riesgo individual a partir de nacionalidad, origen, etnia, religión, condición migratoria o pertenencia grupal.

### Requisito obligatorio (pre-salida)

Ninguna señal espacial de tensión, hostilidad, polarización o análoga puede:

- promocionarse a alerta OWNER, ni
- aparecer en PUBLIC,

hasta pasar (o declarar explícitamente `NO VERIFICADO`) el siguiente test:

```text
DISPARATE_IMPACT_TEST
─────────────────────
Entradas:
  S  = señal espacial candidata (tensión / hostilidad / …)
  U  = unidades territoriales
  C  = variable de composición (si existe y es legítimamente disponible)
  Y  = fenómeno objetivo observable (incidentes, eventos, etc.)

Procedimiento:
  1. Dependencia S ↔ C
  2. Dependencia S ↔ Y
  3. Dependencia parcial S ↔ Y | C

Criterio de fallo (PROXY_RISK):
  Si S predice C más fuertemente que predice Y
  (o que predice Y controlando por C),
  entonces:
    - la señal se clasifica PROXY_RISK
    - no puede promocionarse a OWNER sin revisión humana explícita y registrada
    - nunca puede aparecer en PUBLIC
    - debe generar deuda epistémica explícita

Si no existen datos suficientes de C o de Y:
  estado = NO VERIFICADO
  la señal no es utilizable operativamente.
```

### Ubicación futura de la implementación

- Preferente: extensión de `adversarial_validation.py` o `epistemic_validation.py`.
- No crear un archivo nuevo salvo que se demuestre que la responsabilidad no cabe en los módulos existentes.
- Debe devolver un objeto de deuda epistémica auditables.
- Debe tener tests unitarios y adversariales.

Hasta que el test exista y pase, **toda señal de tensión espacial permanece no promocionable**.

---

## 5. Auditoría matemática de la fórmula de susceptibilidad

Forma propuesta en la doctrina / discusión:

```text
Susceptibilidad = Shock × Sensitivity × Reserve⁻¹ × Coupling × Propagation
```

### Fallos confirmados

1. **Singularidad en Reserve → 0**  
   Cuando la reserva se aproxima a cero (justo en crisis), el término diverge y amplifica el ruido de medición sin control.  
   Si Reserve puede ser negativa (C < L), el signo se invierte y la interpretación se pierde.

2. **Confusión de vulnerabilidad local vs. potencial de cascada**  
   Si Coupling = 0, la fórmula da 0 aunque la zona esté agotada y el shock sea grande.  
   Mide susceptibilidad de propagación, no vulnerabilidad local.  
   Se requieren **dos salidas separadas**.

3. **Estructura multiplicativa continua vs. umbrales / percolación / branching**  
   Un producto suave no representa una transición de fase (p. ej. factor de ramificación cruzando 1).  
   Infra-alerta antes del umbral y sobre-alerta después.

4. **Ausencia de calibración**  
   Sin pares (Shock, Sensitivity, Reserve, Coupling, Propagation) → resultado observado (cascada / no cascada) en unidades zona-tiempo independientes, y sin comparación fuera de muestra contra al menos una alternativa, la fórmula es **hipótesis**, no instrumento operativo.

### Correcciones mínimas exigidas si se implementa

- Término de reserva acotado, p. ej.  
  `reserve_term = exp(-Reserve / Reserve_ref)`  
  o  
  `1.0 / (max(Reserve, 0.0) + eps)`
- Separación explícita:  
  `local_vulnerability` y `cascade_potential`.
- Término de umbral / branching si se pretende capturar tipping points.
- Etiquetado obligatorio: `epistemic_status = "hypothesis_uncalibrated"` hasta validación.

**Estado actual de la fórmula:** HIPÓTESIS NO CALIBRADA.  
No puede pesar en scores que lleguen a OWNER.

---

## 6. Orden de intervención (no negociable)

1. Completar la tabla de inventario semántico de los **127** símbolos duplicados.
2. Decidir, símbolo a símbolo: CONSERVAR / RENOMBRAR / FUSIONAR / DEPRECAR.
3. Solo entonces reconstruir `metrics.py` de forma que:
   - un único `from __future__ import annotations` al inicio,
   - un único bloque de imports,
   - definiciones antes de cualquier uso,
   - un único `__all__` construido al final,
   - sin texto residual ni caracteres no-ASCII que rompan el parser.
4. Añadir tests de regresión para cada semántica conservada.
5. Implementar el `DISPARATE_IMPACT_TEST` mínimo.
6. Solo después: nuevas capacidades o fórmulas.

Cualquier salto de los pasos 1-2 se considera violación del principio de conservación semántica.

---

## 7. Criterios de aceptación de esta fase

- [ ] Tabla completa de los 127 duplicados versionada en este documento o en anexo.
- [ ] `metrics.py` importa sin `SyntaxError` ni `NameError`.
- [ ] Tests de integridad de `adaptive_reserve_static`, trayectoria y umbral pasan.
- [ ] Ninguna señal de tensión espacial puede promocionarse sin pasar (o declarar `NO VERIFICADO`) el test de proxy.
- [ ] Bloque de estado real presente en `README.md` y `docs/SYSTEM_ARCHITECTURE.md`.
- [ ] Este documento de gobierno está referenciado desde la arquitectura.

---

## 8. Archivos que no deben tocarse en esta fase

- `backend/app/core/models.py`
- `backend/app/core/adversarial_validation.py` (salvo la futura adición del test de proxy)
- `backend/app/core/epistemic_validation.py`
- `backend/app/core/evidence_policy.py`
- `backend/app/core/information_boundary.py`
- `backend/app/security/`
- Doctrina, ontología y modelos de alerta (solo se añade referencia a este documento)

---

## 9. Comandos de verificación (cuando el inventario permita la reconstrucción)

```bash
cd /ruta/al/repo/Ceuta
python -c "from app.core import metrics; print('import OK')"
python -m pytest tests/core/test_metrics_integrity.py -q
```

Resultado esperado **hoy**: FAIL / BLOCKED.  
Declarar PASS sin haber cerrado el inventario y la reconstrucción es falsa sofisticación.

---

## 10. Principio final de esta especificación

La misión de CeutIA no es adivinar el futuro.  
Es aumentar la capacidad de detectar antes, comprender mejor, dudar cuando corresponde, falsar hipótesis, cuantificar incertidumbre, identificar puntos de intervención e intervenir con humanos.

Por tanto:

> No se construye una máquina que tenga siempre razón.  
> Se construye un sistema que tenga cada vez más capacidad para descubrir cuándo está equivocado.

Cualquier reconstrucción de `metrics.py` que oculte duplicaciones semánticas o elimine capacidades válidas sin demostración viola este principio.

---

**Fin del documento de gobierno (borrador 2026-09-09).**  
Próximo artefacto requerido: tabla completa de los 127 símbolos duplicados.


# CEUTIA — MASTER IMPLEMENTATION SPECIFICATION

**Estado:** BORRADOR DE GOBIERNO — 2026-09-09  
**Alcance:** reconstrucción del núcleo matemático (`metrics.py`) + defensa verificable contra proxy geográfico de hostilidad  
**Principio rector:**  
DOCUMENTADO ≠ IMPLEMENTADO ≠ EJECUTABLE ≠ VERIFICADO ≠ VALIDADO ≠ CALIBRADO ≠ OPERACIONAL

Este documento no sustituye la doctrina (`CEUTIA_MASTER_OPERATING_DOCTRINE.md`), la ontología ni la arquitectura.  
Gobierna **cómo** se reconstruye el código existente sin pérdida semántica y **qué** debe existir antes de cualquier promoción de señales sensibles.

---

## 1. Estado real del repositorio (contrato)

| Dimensión | Estado |
|-----------|--------|
| Documentado | Sí |
| Diseñado | Sí |
| Implementado (código presente) | Parcial |
| Importable | No garantizado |
| Ejecutable | No |
| Testeado | No |
| Verificado | No |
| Validado | No |
| Calibrado | No |
| Operacional | **No** |

**Motivo factual:**  
`backend/app/core/metrics.py` (~18.335 líneas) es un artefacto concatenado de bloques aditivos. Contiene 807 definiciones de nivel superior, 673 símbolos únicos y **127 símbolos duplicados con semánticas distintas**. El módulo no importa de forma fiable. Ninguna capacidad preventiva ha sido demostrada en runtime.

---

## 2. Regla de no reescritura sin inventario

**Prohibido** reescribir, consolidar o “limpiar” `metrics.py` eligiendo arbitrariamente la primera o la última definición de un símbolo duplicado.

Antes de cualquier modificación estructural se debe completar y versionar la **tabla de inventario semántico** de los 127 símbolos duplicados.

Para cada símbolo:

1. Localizar todas las ocurrencias (línea + firma).
2. Extraer la semántica real (ecuación, dominio, unidades, interpretación).
3. Clasificar:
   - **IDÉNTICA** → conservar una, eliminar la otra.
   - **EQUIVALENTE** → fusionar.
   - **PARCIALMENTE EQUIVALENTE** → especializar (renombrar o parametrizar).
   - **SEMÁNTICAMENTE DISTINTA** → **conservar ambas** con nombres canónicos distintos.
   - **INCOMPATIBLE** → resolver contradicción explícitamente.
4. Registrar la decisión y el nombre canónico propuesto.
5. Solo entonces proceder a la reconstrucción ordenada.

Una reconstrucción que salte este paso se considera **pérdida semántica no demostrada** y debe rechazarse.

---

## 3. Inventario semántico de casos críticos (demostrado)

| Símbolo | Ocurrencias | Semántica A | Semántica B / C | Clasificación | Decisión | Nombre canónico propuesto |
|---------|-------------|-------------|-----------------|---------------|----------|---------------------------|
| `adaptive_reserve` | 2 | Trayectoria dinámica \(R_t = R_{t-1} - L_t\,dt + G_t\,dt\) (estado) | Estática \(C - L\) | **DISTINTA** | Conservar ambas | `adaptive_reserve_trajectory` / `adaptive_reserve_static` |
| `cascade_depth` | 2 | Generaciones de matriz de activación (estructural) | Path depth desde nodo origen (NetworkX) | **DISTINTA** | Conservar ambas | `cascade_generation_depth` / `cascade_network_depth` |
| `coupling_strength` | 3 | Media absoluta off-diagonal de matriz | Correlación entre series / correlación retardada | **DISTINTA** | Conservar las tres | `coupling_matrix_strength` / `coupling_series_strength` / `coupling_lagged_strength` |
| `accumulated_load` | 2 | Integral \(\int L(t)\,dt\) | Carga con memoria exponencial (decay) | **DISTINTA** | Conservar ambas | `accumulated_load_integral` / `accumulated_load_decay` |
| `threshold_distance` | 2 | Distancia absoluta \(\|x - \theta\|\) | Distancia normalizada por escala | **PARCIAL** | Especializar | `threshold_distance` / `threshold_distance_scaled` |
| `recovery_fraction` | 3 | (pendiente de inventario completo) | | | | |
| `synchronization_index` | 3 | (pendiente) | | | | |
| `effective_capacity` | 3 | (pendiente) | | | | |
| `prevalence` | 3 | (pendiente) | | | | |
| … (resto de los 127) | | | | | | |

**Estado del inventario:** 5 casos críticos resueltos. 122 pendientes.  
**Bloqueo:** no se reescribe `metrics.py` hasta completar la tabla.

---

## 4. Defensa verificable contra proxy geográfico de hostilidad

### Problema

En un territorio de superficie pequeña y alta concentración espacial de flujos (Ceuta), una señal de “tensión / hostilidad / polarización” agregada por zona puede correlacionar fuertemente con composición demográfica o migratoria sin que ninguna variable prohibida aparezca explícitamente en el modelo. La geografía actúa como proxy.

Esto viola el principio fundamental de CeutIA:

> No inferir peligrosidad, criminalidad o riesgo individual a partir de nacionalidad, origen, etnia, religión, condición migratoria o pertenencia grupal.

### Requisito obligatorio (pre-salida)

Ninguna señal espacial de tensión, hostilidad, polarización o análoga puede:

- promocionarse a alerta OWNER, ni
- aparecer en PUBLIC,

hasta pasar (o declarar explícitamente `NO VERIFICADO`) el siguiente test:

```text
DISPARATE_IMPACT_TEST
─────────────────────
Entradas:
  S  = señal espacial candidata (tensión / hostilidad / …)
  U  = unidades territoriales
  C  = variable de composición (si existe y es legítimamente disponible)
  Y  = fenómeno objetivo observable (incidentes, eventos, etc.)

Procedimiento:
  1. Dependencia S ↔ C
  2. Dependencia S ↔ Y
  3. Dependencia parcial S ↔ Y | C

Criterio de fallo (PROXY_RISK):
  Si S predice C más fuertemente que predice Y
  (o que predice Y controlando por C),
  entonces:
    - la señal se clasifica PROXY_RISK
    - no puede promocionarse a OWNER sin revisión humana explícita y registrada
    - nunca puede aparecer en PUBLIC
    - debe generar deuda epistémica explícita

Si no existen datos suficientes de C o de Y:
  estado = NO VERIFICADO
  la señal no es utilizable operativamente.
```

### Ubicación futura de la implementación

- Preferente: extensión de `adversarial_validation.py` o `epistemic_validation.py`.
- No crear un archivo nuevo salvo que se demuestre que la responsabilidad no cabe en los módulos existentes.
- Debe devolver un objeto de deuda epistémica auditables.
- Debe tener tests unitarios y adversariales.

Hasta que el test exista y pase, **toda señal de tensión espacial permanece no promocionable**.

---

## 5. Auditoría matemática de la fórmula de susceptibilidad

Forma propuesta en la doctrina / discusión:

```text
Susceptibilidad = Shock × Sensitivity × Reserve⁻¹ × Coupling × Propagation
```

### Fallos confirmados

1. **Singularidad en Reserve → 0**  
   Cuando la reserva se aproxima a cero (justo en crisis), el término diverge y amplifica el ruido de medición sin control.  
   Si Reserve puede ser negativa (C < L), el signo se invierte y la interpretación se pierde.

2. **Confusión de vulnerabilidad local vs. potencial de cascada**  
   Si Coupling = 0, la fórmula da 0 aunque la zona esté agotada y el shock sea grande.  
   Mide susceptibilidad de propagación, no vulnerabilidad local.  
   Se requieren **dos salidas separadas**.

3. **Estructura multiplicativa continua vs. umbrales / percolación / branching**  
   Un producto suave no representa una transición de fase (p. ej. factor de ramificación cruzando 1).  
   Infra-alerta antes del umbral y sobre-alerta después.

4. **Ausencia de calibración**  
   Sin pares (Shock, Sensitivity, Reserve, Coupling, Propagation) → resultado observado (cascada / no cascada) en unidades zona-tiempo independientes, y sin comparación fuera de muestra contra al menos una alternativa, la fórmula es **hipótesis**, no instrumento operativo.

### Correcciones mínimas exigidas si se implementa

- Término de reserva acotado, p. ej.  
  `reserve_term = exp(-Reserve / Reserve_ref)`  
  o  
  `1.0 / (max(Reserve, 0.0) + eps)`
- Separación explícita:  
  `local_vulnerability` y `cascade_potential`.
- Término de umbral / branching si se pretende capturar tipping points.
- Etiquetado obligatorio: `epistemic_status = "hypothesis_uncalibrated"` hasta validación.

**Estado actual de la fórmula:** HIPÓTESIS NO CALIBRADA.  
No puede pesar en scores que lleguen a OWNER.

---

## 6. Orden de intervención (no negociable)

1. Completar la tabla de inventario semántico de los **127** símbolos duplicados.
2. Decidir, símbolo a símbolo: CONSERVAR / RENOMBRAR / FUSIONAR / DEPRECAR.
3. Solo entonces reconstruir `metrics.py` de forma que:
   - un único `from __future__ import annotations` al inicio,
   - un único bloque de imports,
   - definiciones antes de cualquier uso,
   - un único `__all__` construido al final,
   - sin texto residual ni caracteres no-ASCII que rompan el parser.
4. Añadir tests de regresión para cada semántica conservada.
5. Implementar el `DISPARATE_IMPACT_TEST` mínimo.
6. Solo después: nuevas capacidades o fórmulas.

Cualquier salto de los pasos 1-2 se considera violación del principio de conservación semántica.

---

## 7. Criterios de aceptación de esta fase

- [ ] Tabla completa de los 127 duplicados versionada en este documento o en anexo.
- [ ] `metrics.py` importa sin `SyntaxError` ni `NameError`.
- [ ] Tests de integridad de `adaptive_reserve_static`, trayectoria y umbral pasan.
- [ ] Ninguna señal de tensión espacial puede promocionarse sin pasar (o declarar `NO VERIFICADO`) el test de proxy.
- [ ] Bloque de estado real presente en `README.md` y `docs/SYSTEM_ARCHITECTURE.md`.
- [ ] Este documento de gobierno está referenciado desde la arquitectura.

---

## 8. Archivos que no deben tocarse en esta fase

- `backend/app/core/models.py`
- `backend/app/core/adversarial_validation.py` (salvo la futura adición del test de proxy)
- `backend/app/core/epistemic_validation.py`
- `backend/app/core/evidence_policy.py`
- `backend/app/core/information_boundary.py`
- `backend/app/security/`
- Doctrina, ontología y modelos de alerta (solo se añade referencia a este documento)

---

## 9. Comandos de verificación (cuando el inventario permita la reconstrucción)

```bash
cd /ruta/al/repo/Ceuta
python -c "from app.core import metrics; print('import OK')"
python -m pytest tests/core/test_metrics_integrity.py -q
```

Resultado esperado **hoy**: FAIL / BLOCKED.  
Declarar PASS sin haber cerrado el inventario y la reconstrucción es falsa sofisticación.

---

## 10. Principio final de esta especificación

La misión de CeutIA no es adivinar el futuro.  
Es aumentar la capacidad de detectar antes, comprender mejor, dudar cuando corresponde, falsar hipótesis, cuantificar incertidumbre, identificar puntos de intervención e intervenir con humanos.

Por tanto:

> No se construye una máquina que tenga siempre razón.  
> Se construye un sistema que tenga cada vez más capacidad para descubrir cuándo está equivocado.

Cualquier reconstrucción de `metrics.py` que oculte duplicaciones semánticas o elimine capacidades válidas sin demostración viola este principio.

---

**Fin del documento de gobierno (borrador 2026-09-09).**  
Próximo artefacto requerido: tabla completa de los 127 símbolos duplicados.
