## ⚠️ IMPORTANTE: Proyecto Privado y Propietario

**CEUTIA es un proyecto privado y propietario.**

- Solo pueden contribuir **miembros autorizados explícitamente**
- Todo el código es **confidencial**
- No se puede compartir externamente sin permiso escrito
- Las contribuciones están sujetas a la [Licencia](./LICENSE)

Si has recibido acceso a este repositorio, es porque has sido **explícitamente autorizado** por el propietario.

---

## 🎯 Propósito de esta Guía

Esta guía establece los estándares para contribuir a CEUTIA, asegurando:

- **Calidad técnica** — Código robusto, seguro, mantenible
- **Consistencia** — Estilo uniforme en todo el proyecto
- **Seguridad** — Protección de datos sensibles y secretos
- **Trazabilidad** — Todo cambio es auditable
- **Propósito alineado** — Contribuciones alineadas con la misión de salvar vidas

---

## 🌟 Principios Fundamentales

### 1. Evidencia antes que Narrativa

> **Los hechos documentados gobiernan.**

- No implementar funcionalidad basada en suposiciones
- Todo debe estar documentado o ser trazable a una fuente
- Si hay incertidumbre, hacerla explícita

### 2. Seguridad Primero

> **Nunca comprometer la seguridad por conveniencia.**

- Nunca subir secretos al repositorio
- Validar siempre inputs del usuario
- Usar parámetros preparados (no SQL injection)
- Encriptar datos sensibles
- Seguir principio de mínimo privilegio

### 3. Separación Estricta de Perímetros

> **Público, Owner y Médico son independientes.**

- No cruzar datos entre perímetros
- Módulo médico NUNCA se usa para inteligencia territorial
- Datos sensibles solo en Owner

### 4. Auditoría Completa

> **Todo cambio debe ser trazable.**

- Commits descriptivos
- Tests para funcionalidad crítica
- Logs de acciones importantes
- Documentar cambios significativos

### 5. Propósito Claro

> **Ayudar a la humanidad, no acumular datos.**

- Cada línea de código debe servir al propósito
- No implementar features "porque sí"
- Priorizar impacto sobre complejidad

---

## 🚀 Flujo de Trabajo

### 1. Crear Rama (Branch)

```bash
# Desde main, crear rama descriptiva
git checkout main
git pull origin main
git checkout -b feature/descripcion-corta


Perfecto. Continuamos.

***

## 2. `CONTRIBUTING.md` — Guía de Contribución

**Crea el archivo:** `CONTRIBUTING.md`

**Copia y pega esto COMPLETO:**

```markdown
# Contributing to CEUTIA

> **Guía exhaustiva para contribuir al sistema CEUTIA**
>
> *Sistema de Inteligencia Territorial para Salvar a la Humanidad*

---

## ⚠️ IMPORTANTE: Proyecto Privado

**CEUTIA es un proyecto privado y propietario.**

- Solo pueden contribuir **miembros autorizados explícitamente**
- Todo el código es **confidencial**
- No se puede compartir externamente sin permiso escrito

Si tienes acceso, has sido **explícitamente autorizado** por el propietario.

---

## 🎯 Propósito

Esta guía establece estándares para contribuir a CEUTIA, asegurando:

- **Calidad técnica** — Código robusto, seguro, mantenible
- **Consistencia** — Estilo uniforme
- **Seguridad** — Protección de datos sensibles y secretos
- **Trazabilidad** — Todo cambio auditable
- **Propósito alineado** — Contribuciones alineadas con salvar vidas

---

## 🌟 Principios Fundamentales

### 1. Evidencia antes que Narrativa

> Los hechos documentados gobiernan.

- No implementar basado en suposiciones
- Todo debe estar documentado o trazable a fuente
- Incertidumbre explícita

### 2. Seguridad Primero

> Nunca comprometer seguridad por conveniencia.

- Nunca subir secretos al repositorio
- Validar siempre inputs
- Usar parámetros preparados (no SQL injection)
- Encriptar datos sensibles
- Mínimo privilegio

### 3. Separación Estricta de Perímetros

> Público, Owner y Médico son independientes.

- No cruzar datos entre perímetros
- Módulo médico NUNCA para inteligencia territorial
- Datos sensibles solo en Owner

### 4. Auditoría Completa

> Todo cambio debe ser trazable.

- Commits descriptivos
- Tests para funcionalidad crítica
- Logs de acciones importantes
- Documentar cambios significativos

### 5. Propósito Claro

> Ayudar a la humanidad, no acumular datos.

- Cada línea de código debe servir al propósito
- No features "porque sí"
- Priorizar impacto sobre complejidad

---

## 🚀 Flujo de Trabajo

### 1. Crear Rama

```bash
git checkout main
git pull origin main
git checkout -b feature/descripcion-corta
```

**Convenciones de nombres:**

| Tipo | Prefijo | Ejemplo |
|---|---|---|
| Feature | `feature/` | `feature/auth-mfa` |
| Bug fix | `fix/` | `fix/rate-limit-bypass` |
| Hotfix | `hotfix/` | `hotfix/security-patch` |
| Refactor | `refactor/` | `refactor/epistemic-engine` |
| Docs | `docs/` | `docs/architecture-update` |
| Tests | `tests/` | `tests/ingestion-pipeline` |

### 2. Implementar Cambios

- Código limpio y legible
- Funciones pequeñas y enfocadas
- Nombres descriptivos

### 3. Ejecutar Tests

```bash
npm test
npm run test:integration
npm run test:e2e
npm run test:coverage
```

**Requisitos:**

- Coverage mínimo: **80%**
- Todos los tests deben pasar

### 4. Commit Changes

```bash
git add .
git commit -m "type: descripción corta

descripción detallada

- cambio 1
- cambio 2

Closes #123"
```

**Convenciones de Commits (Conventional Commits):**

| Tipo | Descripción | Ejemplo |
|---|---|---|
| `feat` | Nueva funcionalidad | `feat(auth): add MFA support` |
| `fix` | Corrección de bug | `fix(api): prevent SQL injection` |
| `docs` | Documentación | `docs: update architecture` |
| `style` | Formato, estilo | `style: fix indentation` |
| `refactor` | Refactorización | `refactor: simplify risk calculation` |
| `test` | Tests | `test: add unit tests for alerts` |
| `chore` | Mantenimiento | `chore: update dependencies` |
| `security` | Seguridad | `security: patch XSS vulnerability` |

### 5. Push y Pull Request

```bash
git push origin feature/descripcion-corta
```

**Crear PR:**

1. GitHub → Pull Requests → "New Pull Request"
2. Base: `main`, Compare: tu rama
3. Completar plantilla
4. Solicitar review

### 6. Revisión de Código

**Requisitos para merge:**

- ✅ Al menos **1 approval** de maintainer
- ✅ Todos los **CI checks** passing
- ✅ **Tests** passing
- ✅ **Coverage** >= 80%
- ✅ **Security scan** passing
- ✅ **No secrets** detectados

### 7. Merge

**Estrategia:** Squash and Merge

---

## 📝 Estándares de Código

### TypeScript

**Configuración estricta:**

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

**Reglas:**

- ✅ Usar tipos explícitos (no `any`)
- ✅ Usar interfaces para objetos
- ✅ Usar `const` en lugar de `let`
- ✅ Nombres descriptivos

**Ejemplo:**

```typescript
interface RiskFactors {
  probability: number; // 0-1
  impact: number; // 1-5
  vulnerability?: number; // 0-1
}

function calculateRisk(factors: RiskFactors): number {
  const { probability, impact, vulnerability = 1 } = factors;
  
  if (probability < 0 || probability > 1) {
    throw new Error('Probability must be between 0 and 1');
  }
  
  return probability * impact * vulnerability;
}
```

### Backend (Node.js / Fastify)

**Estructura:**

```
src/
├── routes/
├── controllers/
├── services/
├── middleware/
├── utils/
└── types/
```

**Validación (Zod):**

```typescript
import { z } from 'zod';

const CreateRiskSchema = z.object({
  title: z.string().min(1).max(500),
  probability: z.number().min(0).max(1),
  impact: z.number().min(1).max(5),
});

app.post('/risks', async (request) => {
  const input = CreateRiskSchema.parse(request.body);
  const risk = await riskService.create(input);
  return risk;
});
```

### Frontend (Next.js / React)

**Estructura:**

```
src/
├── app/ (public, owner, medical, api)
├── components/ (ui, layout, features)
├── lib/
├── hooks/
└── types/
```

**Componentes:**

```typescript
interface AlertCardProps {
  alert: Alert;
  onAcknowledge: (id: string) => void;
}

export function AlertCard({ alert, onAcknowledge }: AlertCardProps) {
  return (
    <div className="alert-card">
      <h3>{alert.title}</h3>
      <AlertLevelBadge level={alert.level} />
      <button onClick={() => onAcknowledge(alert.id)}>Acknowledge</button>
    </div>
  );
}
```

### Base de Datos (Prisma)

**Schema:**

```prisma
model Alert {
  id          String   @id @default(uuid())
  title       String   @unique
  level       AlertLevel
  status      String   @default("ACTIVE")
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  @@index([level])
  @@index([status])
}
```

**Queries:**

```typescript
// ✅ Bien: Single query con include
const alerts = await prisma.alert.findMany({
  include: { risks: true },
  orderBy: { createdAt: 'desc' },
  take: 100,
});
```

---

## 🔐 Seguridad

### Secretos

**NUNCA subir:**

- ❌ `.env` con valores reales
- ❌ API keys, passwords, certificados, tokens

**Usar variables de entorno:**

```bash
# .env (no subir a Git)
DATABASE_URL=postgresql://user:password@localhost:5432/ceutia
JWT_SECRET=super_secret_value_min_64_chars
```

```typescript
const config = {
  database: { url: process.env.DATABASE_URL! },
  jwt: { secret: process.env.JWT_SECRET! },
};
```

### Autenticación

**JWT:**

```typescript
import jwt from 'jsonwebtoken';

const token = jwt.sign(
  { userId: user.id, role: user.role },
  process.env.JWT_SECRET!,
  { expiresIn: '24h' }
);

const payload = jwt.verify(token, process.env.JWT_SECRET!);
```

### Input Validation

**Siempre validar:**

```typescript
const CreateRiskSchema = z.object({
  probability: z.number().min(0).max(1),
  impact: z.number().min(1).max(5),
});

app.post('/risks', async (request) => {
  const input = CreateRiskSchema.parse(request.body);
  // ...
});
```

### SQL Injection Prevention

**Siempre parámetros preparados:**

```typescript
// ❌ Mal
const query = `SELECT * FROM alerts WHERE level = '${level}'`;

// ✅ Bien
const alerts = await prisma.alert.findMany({ where: { level } });
```

---

## 🧪 Testing

### Tipos

| Tipo | Herramienta | Coverage |
|---|---|---|
| Unit | Jest | 80%+ |
| Integration | Jest + Supertest | 60%+ |
| E2E | Playwright | 40%+ |

### Unit Tests

```typescript
import { calculateRisk } from '../../src/services/risk';

describe('calculateRisk', () => {
  it('should calculate risk score correctly', () => {
    const result = calculateRisk({
      probability: 0.8,
      impact: 4,
      vulnerability: 0.5,
    });
    
    expect(result).toBe(1.6);
  });

  it('should throw error for invalid probability', () => {
    expect(() => {
      calculateRisk({ probability: 1.5, impact: 4 });
    }).toThrow('Probability must be between 0 and 1');
  });
});
```

### Integration Tests

```typescript
import request from 'supertest';
import { app } from '../../src/app';

describe('POST /api/v1/alerts', () => {
  it('should create an alert', async () => {
    const response = await request(app)
      .post('/api/v1/alerts')
      .send({ title: 'Test', level: 'WARNING' })
      .expect(201);

    expect(response.body.title).toBe('Test');
  });
});
```

---

## 📚 Documentación

**Siempre documentar:**

- ✅ APIs públicas
- ✅ Funciones complejas
- ✅ Decisiones arquitectónicas
- ✅ Cambios significativos

**No documentar:**

- ❌ Código autoexplicativo
- ❌ Getters/setters simples

---

## 🚫 Qué NO Hacer

- ❌ Nunca subir secretos
- ❌ Nunca hacer SQL injection
- ❌ Nunca ignorar errores
- ❌ Nunca hardcodear credenciales

# Contributing to CEUTIA

> **Guía exhaustiva para contribuir al sistema CEUTIA**
>
> *Sistema de Inteligencia Territorial para Salvar a la Humanidad*

---

---

## 📞 Contacto

- Email: dev@ceutia.system
- Issues: GitHub Issues

---

*Gracias por contribuir a CEUTIA.*

**Última actualización:** Septiembre 2026  
**Versión:** 2.0.0
```

***
