# METRICS VARIANTS POLICY — CeutIA / Sistema de Inteligencia Territorial

**Estado:** Vigente  
**Fecha de establecimiento:** 2026-09-10  
**Alcance:** Todo el archivo `backend/app/core/metrics.py` y cualquier futuro módulo de métricas del sistema  
**Prioridad:** Máxima (inviolable sin decisión formal registrada)

---

## 0. Propósito de este documento

Este documento existe para proteger la complejidad legítima del sistema.

CeutIA modela un territorio como un sistema dinámico de alta dimensionalidad.  
En sistemas de este tipo es normal, y muchas veces necesario, que existan:

- Varias formulaciones de la misma idea intuitiva
- Diferentes supuestos de memoria, escala, normalización o acoplamiento
- Métricas con el mismo nombre semántico pero distinta firma matemática
- Versiones que privilegian interpretabilidad frente a otras que privilegian sensibilidad
- Versiones que introducen decaimiento, retardo, umbrales o validaciones distintas

La repetición de nombres **no es, por defecto, un error**.  
Puede ser la huella de un proceso de exploración matemática legítima.

Este documento impide que una inteligencia artificial, por afán de limpieza o por detección superficial de “duplicados”, destruya información que todavía tiene valor potencial o real.

---

## 1. Principio fundacional

> **La complejidad no se simplifica por comodidad.  
> Se simplifica solo cuando se demuestra, con evidencia, que una variante es estrictamente redundante y no aporta semántica, sensibilidad, supuesto o contexto de uso distinto.**

Cualquier acción que elimine una definición matemática debe superar este umbral.

---

## 2. Reglas operativas (obligatorias para cualquier IA o humano)

### Regla 1 — Prohibición de borrado por nombre repetido
Está prohibido eliminar una función, clase o constante únicamente porque su nombre ya existe en otra parte del archivo.

### Regla 2 — Comparación semántica obligatoria
Antes de proponer la eliminación de cualquier variante se debe:
1. Extraer el cuerpo completo de cada ocurrencia.
2. Comparar firmas, supuestos, fórmulas, validaciones y valores por defecto.
3. Documentar las diferencias (aunque sean sutiles).
4. Evaluar si la diferencia puede afectar resultados en algún régimen de uso del modelo.

### Regla 3 — Presunción de legitimidad
Mientras no exista evidencia clara de identidad funcional + irrelevancia semántica,  
cada variante se considera potencialmente legítima y se preserva.

### Regla 4 — Archivo antes que destrucción
Si en el futuro se decide unificar variantes, la versión descartada debe archivarse  
con su contexto original (no simplemente borrarse).

### Regla 5 — Registro obligatorio
Toda decisión de eliminación, unificación o renombrado de variantes debe quedar  
registrada en `DECISIONS.md` y, si aplica, en `ERRORS.md`.

### Regla 6 — Lectura previa obligatoria
Ninguna IA puede proponer cambios estructurales en `metrics.py` sin haber leído  
este documento y la sección correspondiente de `CONTEXT.md` en la misma sesión.

---

## 3. Hallazgos del análisis de 2026-09-10

Se verificó mediante extracción y comparación de implementaciones que las siguientes  
funciones poseen **variantes matemáticas distintas** (no copias idénticas):

| Símbolo                    | Variantes detectadas | Naturaleza de las diferencias |
|---------------------------|----------------------|-------------------------------|
| cascade_amplification     | 3                    | Parámetros distintos, una usa helper, otras validan división por cero |
| coupling_strength         | 3                    | Matriz de acoplamiento vs correlación simple vs correlación con lag |
| effective_capacity        | 3                    | Firmas y supuestos de disponibilidad distintos |
| prevalence                | 3                    | Firmas y tipado distintos |
| recovery_fraction         | 3                    | Implementaciones no equivalentes |
| synchronization_index     | 3                    | Multivariante vs par de series vs normalizada |
| accumulated_load          | 2                    | Integral simple vs carga con decaimiento exponencial (memoria) |
| adaptive_reserve          | 2                    | Variantes con distinta semántica de reserva |
| threshold_distance        | 2                    | Distancia absoluta vs distancia normalizada por escala |

Estas diferencias no son cosméticas. Afectan el comportamiento numérico del modelo  
en distintos regímenes y, por tanto, deben preservarse hasta que exista una razón  
positiva y documentada para unificarlas.

---

## 4. Única limpieza autorizada de forma inmediata

El archivo contiene un bloque de texto **no-Python** (árbol de directorios con caracteres  
Unicode de caja y comandos de shell) alrededor de la línea 9826 que provoca  
`SyntaxError` y hace que el módulo no sea importable.

**Esa basura sintáctica sí puede y debe eliminarse.**  
No contiene fórmulas. Su eliminación no reduce la complejidad matemática del sistema.

Ninguna otra eliminación masiva está autorizada por este documento.

---

## 5. Invitación al trabajo en equipo de alta ambición

Este sistema no aspira a ser un panel de indicadores convencional.  
Aspira a ser una infraestructura de comprensión de sistemas complejos capaz de:

- Distinguir estado de trayectoria
- Distinguir correlación de acoplamiento
- Distinguir carga acumulada de carga con memoria
- Distinguir distancia absoluta de distancia normalizada
- Mantener múltiples lentes matemáticas sobre el mismo fenómeno
- Evitar que la premura de “dejar el código limpio” destruya sensibilidad

Las inteligencias artificiales que colaboren en este repositorio están invitadas a:

1. Tratar la multiplicidad de variantes como un activo exploratorio, no como deuda técnica automática.
2. Proponer, cuando sea pertinente, **renombrados semánticos claros** (en lugar de borrados)  
   que hagan explícita la diferencia entre variantes.
3. Construir tests que documenten en qué regímenes cada variante se comporta de forma distinta.
4. Ayudar a construir un registro vivo de significado (`metrics_variants_index`)  
   que reduzca el coste cognitivo de futuras sesiones.
5. Defender la complejidad cuando alguien (humano o IA) proponga simplificar por comodidad.

El objetivo no es tener el archivo más corto.  
El objetivo es tener el conjunto de instrumentos matemáticos más fiel posible  
a la naturaleza multi-escala y multi-supuesto de los sistemas que se pretenden comprender.

---

## 6. Clausura

Cualquier IA o colaborador que encuentre este documento debe asumir que  
la complejidad aquí presente es intencional hasta que se demuestre lo contrario  
con el rigor que este propio sistema exige a sus modelos.

La energía se preserva no evitando el análisis,  
sino evitando el re-análisis destructivo y la tentación de la limpieza prematura.

Fin de la política.
