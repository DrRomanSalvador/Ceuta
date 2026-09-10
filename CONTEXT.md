## Estado del núcleo matemático — metrics.py (actualizado 2026-09-10)

### Naturaleza del archivo
`backend/app/core/metrics.py` es un artefacto histórico de alta densidad que contiene 
múltiples generaciones de exploración matemática sobre sistemas dinámicos territoriales, 
capacidad, carga, acoplamiento, sincronización, reservas adaptativas, umbrales y 
señales de alerta temprana.

El archivo presenta nombres repetidos. Un análisis exhaustivo de implementaciones 
realizado el 2026-09-10 demostró que la gran mayoría de esas repeticiones **no son 
copias idénticas**, sino variantes con firmas, supuestos, normalizaciones, 
validaciones o estructuras matemáticas distintas.

### Principio de protección activo
Existe una política formal e inviolable en:

→ `docs/METRICS_VARIANTS_POLICY.md`

Esa política establece que:
- Está prohibido eliminar una función solo porque su nombre ya existe.
- Cada variante se presume legítima hasta prueba en contrario.
- Solo se autoriza de inmediato la eliminación del bloque de texto no-Python 
  (árbol de directorios + comandos shell) que provoca SyntaxError.
- Cualquier unificación futura exige comparación semántica, archivo de la 
  versión descartada y registro formal de la decisión.

### Implicaciones para cualquier IA que trabaje en este repositorio
1. Leer `docs/METRICS_VARIANTS_POLICY.md` antes de proponer cambios estructurales 
   en el núcleo de métricas.
2. No tratar la multiplicidad de nombres como deuda técnica automática.
3. Preferir, cuando sea útil, el renombrado semántico explícito frente al borrado.
4. Contribuir a documentar las diferencias de comportamiento entre variantes 
   en lugar de intentar colapsarlas prematuramente.
5. Entender que este sistema aspira a mantener lentes matemáticas múltiples 
   sobre los mismos fenómenos (carga con y sin memoria, acoplamiento matricial 
   frente a correlación retardada, distancia absoluta frente a normalizada, etc.).

### Estado operativo actual
- El archivo todavía contiene un bloque no-Python que impide su importación limpia.
- Una vez eliminado ese bloque, el módulo podrá ser parseado, aunque seguirá 
  conteniendo múltiples variantes de varios símbolos.
- No existe todavía un registro completo y vivo de todas las variantes 
  (se irá construyendo).
- El sistema de métricas no se considera calibrado ni validado operativamente.

### Invitación
Este repositorio no busca la versión más corta del código.  
Busca la versión más capaz de representar la complejidad real de los sistemas 
que observa. Las inteligencias que colaboren aquí están invitadas a elevar 
el nivel de rigor, a proteger lo que aún no se comprende del todo y a 
construir, en equipo, instrumentos que permitan anticipar transiciones 
antes de que se conviertan en crisis.

La energía se preserva cuando no se redescubre destructivamente lo que 
ya se analizó, y cuando se protege lo que todavía puede tener valor.