# Contrato CeutIA ↔ SERPIENTE

**Document class:** Inter-repository contract
**Status:** REQUIRES VALIDATION

---

## Principios

1. SERPIENTE es repositorio hermano privado del mismo propietario.
2. Todo intercambio de datos se realiza exclusivamente mediante contratos versionados en `/contracts`.
3. Ningún dato clasificado OWNER sale de CeutIA sin gate explícito y registro.
4. Toda integración debe pasar por el proxy-gate y el enforcement de seguridad del control plane.
5. Ningún agente puede crear canales de intercambio ad-hoc.

---

## Estado actual

El contrato está definido a nivel de principios. La implementación de los esquemas de intercambio y los gates de frontera permanece en estado REQUIRES VALIDATION.
