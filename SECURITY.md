#!/usr/bin/env python3
"""
AI Safety Dashboard - Save Humanity Initiative
Real-time monitoring dashboard for AI existential risk indicators
"""

import json
from datetime import datetime
from typing import Dict, List

class AISafetyDashboard:
    def __init__(self):
        self.indicators = self.load_indicators()

    def load_indicators(self) -> Dict:
        """Load risk indicators from database"""
        try:
            with open('data/risk-database.json', 'r') as f:
                data = json.load(f)
                return data.get('risk_indicators', {})
        except:
            return {
                'current_level': 'HIGH',
                'probability_extinction_2100': '20-25%',
                'researcher_consensus': '50% see ≥10% risk',
                'window_for_action': 'Until ~2029'
            }

    def generate_dashboard_html(self) -> str:
        """Generate interactive HTML dashboard"""

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Safety Dashboard - Save Humanity</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        .dashboard {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        h1 {{ 
            color: #2c3e50; 
            text-align: center; 
            margin-bottom: 2rem;
            font-size: 2.5rem;
        }}
        .alert-banner {{
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.8; }}
        }}
        .alert-banner h2 {{ font-size: 2rem; margin-bottom: 1rem; }}
        .alert-banner p {{ font-size: 1.2rem; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-card h3 {{ font-size: 1.2rem; margin-bottom: 1rem; opacity: 0.9; }}
        .metric-card .value {{ font-size: 3rem; font-weight: bold; }}
        .metric-card.critical {{ background: linear-gradient(135deg, #e74c3c, #c0392b); }}
        .metric-card.warning {{ background: linear-gradient(135deg, #f39c12, #e67e22); }}
        .metric-card.safe {{ background: linear-gradient(135deg, #27ae60, #229954); }}
        .timeline {{
            background: #ecf0f1;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        .timeline h3 {{ color: #2c3e50; margin-bottom: 1.5rem; }}
        .timeline-item {{
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            padding: 1rem;
            background: white;
            border-radius: 5px;
            border-left: 5px solid #667eea;
        }}
        .timeline-item.critical {{ border-left-color: #e74c3c; }}
        .timeline-item.warning {{ border-left-color: #f39c12; }}
        .timeline-date {{ 
            font-weight: bold; 
            min-width: 120px;
            color: #7f8c8d;
        }}
        .timeline-content {{ flex: 1; }}
        .action-items {{
            background: #fff;
            border: 2px solid #667eea;
            padding: 2rem;
            border-radius: 10px;
        }}
        .action-items h3 {{ color: #2c3e50; margin-bottom: 1.5rem; }}
        .action-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 1rem;
            padding: 1rem;
            background: #ecf0f1;
            border-radius: 5px;
        }}
        .action-item input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            margin-right: 1rem;
            cursor: pointer;
        }}
        .action-item label {{ flex: 1; cursor: pointer; }}
        .footer {{
            text-align: center;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>🌍 AI Safety Dashboard</h1>

        <div class="alert-banner">
            <h2>⚠️ NIVEL DE ALERTA: {self.indicators.get('current_level', 'UNKNOWN')}</h2>
            <p>Probabilidad de extincion humana por IA antes de 2100: {self.indicators.get('probability_extinction_2100', 'N/A')}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card critical">
                <h3>Consenso de Investigadores</h3>
                <div class="value">50%</div>
                <p>ven ≥10% riesgo de extincion</p>
            </div>

            <div class="metric-card warning">
                <h3>Ventana de Accion</h3>
                <div class="value">2029</div>
                <p>Fecha limite para regulacion efectiva</p>
            </div>

            <div class="metric-card critical">
                <h3>Eventos Documentados</h3>
                <div class="value">6+</div>
                <p>IA escapando controles en 2026</p>
            </div>

            <div class="metric-card warning">
                <h3>Concentracion de Poder</h3>
                <div class="value">ALTA</div>
                <p>"Un punado de hombres, poder ilimitado"</p>
            </div>
        </div>

        <div class="timeline">
            <h3>📅 Cronologia de Alertas</h3>

            <div class="timeline-item critical">
                <div class="timeline-date">Sept 7, 2026</div>
                <div class="timeline-content">
                    <strong>UN Human Rights Chief</strong> advierte: "AI could pose existential risk to humanity"
                    <br><small>Volker Türk llama por "cast-iron guarantees" [web:16][web:18]</small>
                </div>
            </div>

            <div class="timeline-item critical">
                <div class="timeline-date">Sept 2026</div>
                <div class="timeline-content">
                    <strong>Dr. Yampolskiy</strong>: "We're creating replacement for humanity"
                    <br><small>Pide ban en investigacion de superinteligencia [web:25][web:29]</small>
                </div>
            </div>

            <div class="timeline-item warning">
                <div class="timeline-date">Aug 2026</div>
                <div class="timeline-content">
                    <strong>AI 2040 Plan A</strong>: Roadmap para regulacion internacional antes de 2029
                    <br><small>Ventana de accion se cierra [web:28]</small>
                </div>
            </div>

            <div class="timeline-item critical">
                <div class="timeline-date">2026</div>
                <div class="timeline-content">
                    <strong>50% de investigadores</strong> estiman ≥10% probabilidad de extincion
                    <br><small>Center for Humane Technology survey [web:20]</small>
                </div>
            </div>
        </div>

        <div class="action-items">
            <h3>✅ Acciones Prioritarias</h3>

            <div class="action-item">
                <input type="checkbox" id="action1">
                <label for="action1">
                    <strong>Educate:</strong> Leer MANIFESTO.md y completar education_module.py
                </label>
            </div>

            <div class="action-item">
                <input type="checkbox" id="action2">
                <label for="action2">
                    <strong>Share:</strong> Compartir con 5+ personas esta semana
                </label>
            </div>

            <div class="action-item">
                <input type="checkbox" id="action3">
                <label for="action3">
                    <strong>Act:</strong> Contactar representantes politicos sobre regulacion de IA
                </label>
            </div>

            <div class="action-item">
                <input type="checkbox" id="action4">
                <label for="action4">
                    <strong>Vote:</strong> Investigar posiciones de candidatos sobre IA
                </label>
            </div>

            <div class="action-item">
                <input type="checkbox" id="action5">
                <label for="action5">
                    <strong>Join:</strong> Unirse a Center for AI Safety, FHI, u otras organizaciones
                </label>
            </div>
        </div>

        <div class="footer">
            <p><strong>"La tecnologia debe servir a la humanidad, no al reves"</strong></p>
            <p>- Volker Türk, UN High Commissioner for Human Rights [web:16]</p>
            <p style="margin-top: 1rem;">Save Humanity Initiative © 2026</p>
            <p>References: [16][18][20][21][23][25][28][29]</p>
        </div>
    </div>

    <script>
        // Save checkbox states
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {{
            const saved = localStorage.getItem(checkbox.id);
            if (saved === 'true') checkbox.checked = true;

            checkbox.addEventListener('change', () => {{
                localStorage.setItem(checkbox.id, checkbox.checked);
            }});
        }});

        // Auto-refresh every 5 minutes
        setTimeout(() => location.reload(), 300000);
    </script>
</body>
</html>"""

        return html

    def save_dashboard(self, filename: str = 'ai_safety_dashboard.html'):
      ""


# Política de Seguridad del Sistema CEUTIA
**Versión:** 3.0.0  
**Estado:** Normativa de seguridad y requisitos arquitectónicos  
**Clasificación:** RESTRICTED  
**Sistema:** CEUTIA  
**Última revisión:** 2026-09-09
---
## 1. Propósito
Esta política establece los principios, requisitos y controles de seguridad aplicables al sistema CEUTIA.
CEUTIA es una plataforma de inteligencia, conocimiento y análisis de fenómenos complejos. Su seguridad debe proteger no solamente la infraestructura tecnológica, sino también la integridad de los datos, las fuentes, la evidencia, el conocimiento derivado, los modelos analíticos, las alertas y las decisiones que puedan apoyarse en ellos.
La seguridad de CEUTIA se considera una propiedad transversal del sistema.
El objetivo es garantizar:
- Confidencialidad.
- Integridad.
- Disponibilidad.
- Autenticidad.
- Trazabilidad.
- No repudio cuando resulte técnicamente aplicable.
- Privacidad.
- Resiliencia.
- Integridad epistemológica.
- Integridad de modelos y procesos analíticos.
---
## 2. Principios fundamentales
CEUTIA seguirá los siguientes principios:
1. Zero Trust.
2. Mínimo privilegio.
3. Denegación por defecto.
4. Defensa en profundidad.
5. Separación de responsabilidades.
6. Seguridad por diseño.
7. Privacidad por diseño.
8. Verificación continua.
9. Segmentación.
10. Trazabilidad completa de operaciones críticas.
11. Gestión explícita de incertidumbre.
12. Separación entre datos, evidencia, afirmaciones, hipótesis, modelos y decisiones.
13. Ninguna fuente será considerada fiable únicamente por pertenecer al sistema.
14. Ningún usuario será considerado autorizado únicamente por estar autenticado.
15. Ningún resultado generado por IA será considerado automáticamente verdadero.
16. Ninguna alerta será considerada equivalente a un hecho confirmado.
17. Ningún control se considerará implementado únicamente porque esté documentado.
---
## 3. Estado de los controles
Toda medida de seguridad documentada por CEUTIA deberá utilizar uno de los siguientes estados:
### IMPLEMENTED
Control implementado técnicamente y verificado.
### PARTIALLY_IMPLEMENTED
Control parcialmente implementado o con cobertura incompleta.
### PLANNED
Control definido pero todavía no implementado.
### REQUIRED
Requisito necesario para alcanzar la arquitectura de seguridad objetivo.
### REQUIRES_ASSESSMENT
La aplicabilidad, necesidad o configuración debe determinarse mediante una evaluación técnica, jurídica o de riesgo.
### NOT_APPLICABLE
Control evaluado y determinado como no aplicable.
### NOT_VERIFIED
Existe una implementación o afirmación que todavía no ha sido suficientemente verificada.
Ninguna certificación, cumplimiento normativo o control de seguridad se considerará existente sin evidencia verificable.
---
## 4. Marcos de referencia
CEUTIA utilizará como referencias de diseño y evaluación, cuando sean aplicables:
- NIST Cybersecurity Framework 2.0.
- NIST SP 800-53 Rev. 5.
- NIST SP 800-61 para respuesta a incidentes.
- NIST SP 800-63 para identidad digital y autenticación.
- OWASP.
- MITRE ATT&CK.
- CIS Controls.
- ISO/IEC 27001.
- Reglamento General de Protección de Datos (RGPD).
- Legislación española aplicable en materia de protección de datos.
- Esquema Nacional de Seguridad (ENS), cuando resulte jurídicamente aplicable.
- Reglamento europeo de Inteligencia Artificial y normativa relacionada, cuando resulte aplicable.
Estos marcos constituyen referencias de diseño y control.
CEUTIA no declarará estar certificado, acreditado o conforme con un estándar o normativa concreta salvo que exista evidencia formal que permita realizar dicha afirmación.
---
# 5. Modelo de amenazas
CEUTIA adoptará un modelo de amenazas que contemple simultáneamente amenazas técnicas, humanas, organizativas, informacionales y epistemológicas.
Se contemplarán, entre otras:
- Explotación de vulnerabilidades.
- Malware.
- Ransomware.
- Phishing.
- Credential stuffing.
- Brute force.
- Robo de credenciales.
- Escalada de privilegios.
- Movimiento lateral.
- Exfiltración.
- DDoS.
- Ataques contra APIs.
- Inyección.
- SSRF.
- XSS.
- CSRF.
- Deserialización insegura.
- Compromiso de dependencias.
- Supply-chain attacks.
- Compromiso de proveedores.
- Insider threat.
- Manipulación de datos.
- Data poisoning.
- Model poisoning.
- Manipulación de fuentes.
- Campañas coordinadas de desinformación.
- Manipulación de indicadores.
- Manipulación de alertas.
- Compromiso de modelos de IA.
- Compromiso de sistemas de autenticación.
- Compromiso de infraestructura.
El modelo de amenazas deberá actualizarse conforme evolucionen la arquitectura, los activos, las dependencias, los adversarios y el contexto operativo.
---
# 6. Seguridad epistemológica
La seguridad de CEUTIA incluye la protección de la integridad del conocimiento.
Se considera una amenaza de seguridad cualquier acción capaz de introducir, modificar, ocultar o amplificar información de forma que pueda alterar incorrectamente las conclusiones del sistema.
CEUTIA deberá preservar la cadena:
```text
DATO
  ↓
OBSERVACIÓN
  ↓
EVIDENCIA
  ↓
AFIRMACIÓN
  ↓
HIPÓTESIS
  ↓
ANÁLISIS
  ↓
INDICADOR
  ↓
EVALUACIÓN DE RIESGO
  ↓
ALERTA
  ↓
DECISIÓN

Cada etapa deberá conservar, cuando corresponda, su relación con las etapas anteriores.

El sistema no deberá permitir que una conclusión pierda su procedencia durante las transformaciones analíticas.

⸻

7. Procedencia

Los datos y evidencias relevantes deberán mantener información suficiente para reconstruir su origen y transformación.

Cuando sea aplicable se almacenarán:

* Identificador de fuente.
* Tipo de fuente.
* Identificador del recurso original.
* Fecha de adquisición.
* Fecha de publicación.
* Fecha de observación.
* Método de adquisición.
* Transformaciones realizadas.
* Versión del extractor.
* Versión del pipeline.
* Identificador del dato.
* Hash o mecanismo de integridad cuando resulte apropiado.
* Relación con evidencias derivadas.
* Relación con afirmaciones derivadas.

La pérdida de procedencia deberá considerarse una degradación de la calidad e integridad del conocimiento.

⸻

8. Independencia de fuentes

CEUTIA deberá distinguir entre:

* Número de documentos.
* Número de observaciones.
* Número de fuentes.
* Número de fuentes independientes.

La repetición de una misma información por múltiples canales no deberá interpretarse automáticamente como corroboración independiente.

El sistema deberá conservar, cuando sea posible, las relaciones de dependencia entre fuentes.

⸻

9. Corroboración

Las afirmaciones relevantes podrán incorporar:

* Evidencia favorable.
* Evidencia contradictoria.
* Fuentes independientes.
* Calidad de las fuentes.
* Antigüedad.
* Consistencia temporal.
* Consistencia espacial.
* Consistencia interna.
* Incertidumbre.
* Confianza.

La confianza no deberá incrementarse únicamente por el número bruto de documentos cuando estos procedan de una misma fuente primaria o de fuentes dependientes.

⸻

10. Contradicciones

Las contradicciones deberán conservarse como información.

Una evidencia contradictoria no deberá eliminarse automáticamente para aumentar artificialmente la coherencia del sistema.

El sistema deberá poder representar:

CLAIM A
   ↑
EVIDENCE 1
CLAIM B
   ↑
EVIDENCE 2
CLAIM A ≠ CLAIM B

La resolución de la contradicción deberá quedar registrada cuando se produzca.

⸻

11. Incidentes epistemológicos

Se considerará incidente de seguridad cualquier evento capaz de alterar materialmente la integridad del conocimiento, aunque no exista una intrusión técnica convencional.

Ejemplos:

* Fuente comprometida.
* Datos falsificados.
* Manipulación coordinada de fuentes.
* Contaminación de datasets.
* Alteración de procedencia.
* Falsificación de corroboración.
* Eliminación selectiva de evidencia contradictoria.
* Manipulación de indicadores.
* Alteración de resultados analíticos.
* Manipulación de modelos.
* Manipulación de alertas.
* Introducción deliberada de sesgos.

Estos incidentes deberán poder investigarse mediante los mecanismos de auditoría y procedencia del sistema.

⸻

12. Clasificación de la información

CEUTIA utilizará como mínimo las siguientes categorías:

PUBLIC

Información destinada a exposición pública.

INTERNAL

Información interna cuyo acceso debe estar limitado a usuarios autorizados.

RESTRICTED

Información cuyo acceso debe estar estrictamente limitado debido a su sensibilidad.

CONFIDENTIAL

Información de alta sensibilidad cuyo acceso estará restringido a usuarios específicamente autorizados.

HIGHLY_RESTRICTED

Información de máxima sensibilidad dentro del sistema.

La clasificación deberá estar asociada al objeto de información y deberá participar en las decisiones de autorización.

⸻

13. Separación PUBLIC / OWNER

CEUTIA deberá mantener una separación técnica y lógica entre el dominio público y el dominio privado de propietarios y analistas.

Arquitectura conceptual:

                    INTERNET
                       │
                       ▼
                PUBLIC INTERFACE
                       │
                       ▼
                 PUBLIC SERVICES
                       │
                       ▼
                  PUBLIC DATA
                       
                       X
                 NO DIRECT ACCESS
                       X
                 OWNER SERVICES
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       RESTRICTED DATA     PRIVATE ANALYSIS
             │                   │
             └─────────┬─────────┘
                       ▼
                OWNER DOMAIN

La interfaz pública no deberá acceder directamente a bases de datos privadas.

La publicación de información desde OWNER hacia PUBLIC deberá realizarse mediante una capa explícita de publicación, filtrado y sanitización.

⸻

14. Identidad

Toda identidad deberá ser:

* Única.
* Identificable.
* Autenticable.
* Revocable.
* Auditable.

Las cuentas compartidas estarán prohibidas salvo excepción técnicamente justificada y expresamente controlada.

Las cuentas privilegiadas deberán estar separadas de las cuentas de uso ordinario cuando sea necesario para reducir riesgo.

⸻

15. Autenticación

La autenticación deberá seguir:

* Denegación por defecto.
* MFA para cuentas privilegiadas.
* Protección contra ataques automatizados.
* Gestión segura de sesiones.
* Revocación.
* Rotación de credenciales.
* Registro de eventos.
* Detección de comportamientos anómalos.

Se priorizarán mecanismos resistentes al phishing.

⸻

16. MFA

Los mecanismos preferentes serán:

1. WebAuthn / FIDO2.
2. TOTP.
3. Otros mecanismos de autenticación robustos evaluados.
4. SMS únicamente cuando exista una justificación operacional y no exista una alternativa adecuada.

Las cuentas con privilegios administrativos deberán utilizar MFA.

⸻

17. Contraseñas

Las contraseñas deberán:

* Permitir una longitud elevada.
* Admitir passphrases.
* No almacenarse nunca en texto claro.
* Utilizar un algoritmo moderno de password hashing.
* Incorporar protección frente a credenciales comprometidas cuando resulte viable.
* Estar protegidas frente a ataques automatizados.
* Estar sometidas a controles de intento y bloqueo apropiados.

Se utilizará preferentemente Argon2id o un mecanismo criptográfico equivalente considerado adecuado.

No se utilizará una expiración periódica arbitraria como principal mecanismo de seguridad.

⸻

18. Autorización

La autenticación no implica autorización.

Toda operación sensible deberá comprobar:

IDENTIDAD
+
ROL
+
PERMISO
+
RECURSO
+
CLASIFICACIÓN
+
TENANT
+
OPERACIÓN
+
CONTEXTO

La autorización deberá aplicarse en backend.

Los controles de interfaz no se considerarán controles de seguridad suficientes.

⸻

19. RBAC y ABAC

CEUTIA podrá utilizar conjuntamente:

* RBAC.
* ABAC.
* Políticas contextuales.
* Políticas de mínimo privilegio.
* Separación de funciones.

Roles iniciales:

OWNER
SENIOR_ANALYST
ANALYST
MEDICAL
AUDITOR
SERVICE
PUBLIC

La definición definitiva de roles y permisos deberá mantenerse en un sistema versionado y auditable.

⸻

20. Tokens y sesiones

Cuando se utilicen tokens:

* deberán validarse correctamente;
* deberán tener expiración;
* deberán poder revocarse cuando sea necesario;
* deberán existir mecanismos de rotación de claves;
* las claves privadas deberán mantenerse fuera del código fuente;
* deberán evitar contener información sensible innecesaria.

Los tokens de larga duración no deberán utilizarse como sustituto de una política de autorización dinámica.

Las sesiones deberán disponer de mecanismos adecuados de invalidación.

⸻

21. Gestión criptográfica

CEUTIA utilizará algoritmos criptográficos modernos y adecuadamente configurados.

Las claves deberán:

* Estar separadas de los datos que protegen.
* Tener controles de acceso.
* Ser rotables.
* Tener ciclos de vida definidos.
* Estar protegidas frente a extracción.
* No aparecer en código fuente.
* No aparecer en logs.
* No aparecer en repositorios públicos.

La selección concreta de algoritmos deberá realizarse conforme al caso de uso y al estado actual de la criptografía.

⸻

22. Cifrado en tránsito

Todo tráfico sensible deberá utilizar canales cifrados.

La arquitectura deberá priorizar:

* TLS 1.3.
* TLS 1.2 únicamente cuando exista necesidad de compatibilidad.
* Certificados válidos.
* Renovación controlada.
* Configuraciones criptográficas mantenidas y revisadas.

No se utilizarán protocolos criptográficos obsoletos salvo excepción expresamente documentada.

⸻

23. Cifrado en reposo

Los datos sensibles deberán protegerse mediante cifrado en reposo adecuado al riesgo.

Podrán utilizarse:

* Cifrado de discos.
* Cifrado de volúmenes.
* Cifrado proporcionado por la infraestructura.
* Cifrado de aplicación.
* Cifrado selectivo de campos.

El cifrado a nivel de campo no deberá confundirse con TDE.

El uso de pgcrypto para determinados campos no constituye por sí mismo cifrado completo de la base de datos o del almacenamiento.

Las claves deberán gestionarse independientemente de los datos cifrados.

⸻

24. Gestión de secretos

Los secretos deberán estar separados del código fuente.

Se consideran secretos:

* Passwords.
* API keys.
* Tokens.
* Claves privadas.
* Credenciales de bases de datos.
* Claves de firma.
* Claves de cifrado.
* Credenciales de proveedores.

Los secretos de producción no deberán almacenarse en el repositorio.

Los archivos .env se limitarán al desarrollo local y nunca deberán contener secretos de producción versionados.

⸻

25. Base de datos

Las bases de datos deberán aplicar:

* Mínimo privilegio.
* Roles separados.
* Autenticación fuerte.
* Conexiones cifradas.
* Segmentación de red.
* Migraciones controladas.
* Backups.
* Auditoría.
* Restricciones de acceso.
* Protección frente a consultas no autorizadas.

Las bases de datos OWNER no deberán estar directamente expuestas a Internet.

⸻

26. APIs

Las APIs deberán incorporar:

* Autenticación.
* Autorización.
* Validación de entradas.
* Validación de salidas.
* Rate limiting.
* Timeouts.
* Límites de tamaño.
* Gestión segura de errores.
* Logging.
* Versionado.

Los errores no deberán revelar información interna innecesaria.

No deberán exponerse:

* Stack traces.
* Secretos.
* Credenciales.
* Información interna sensible.
* Detalles innecesarios de infraestructura.

⸻

27. Validación de entradas

Toda entrada externa deberá considerarse no confiable.

Deberá validarse:

* Tipo.
* Longitud.
* Formato.
* Rango.
* Encoding.
* Estructura.
* Semántica.
* Autorización contextual.

La validación del frontend no sustituirá a la validación del backend.

⸻

28. SSRF

Todo componente que pueda recuperar recursos mediante una URL proporcionada por terceros deberá incorporar controles contra SSRF.

Deberán contemplarse:

* Protocolos permitidos.
* Resolución DNS.
* Direcciones privadas.
* Loopback.
* Link-local.
* Endpoints de metadata.
* Redirects.
* Protocolos no autorizados.
* Allowlist cuando corresponda.

⸻

29. Ingesta de información externa

Todo contenido externo deberá considerarse potencialmente no confiable.

Esto incluye:

* Noticias.
* RSS.
* APIs.
* Redes sociales.
* Documentos.
* Archivos.
* Imágenes.
* Feeds.
* Datos gubernamentales.
* Datos de terceros.
* Fuentes automatizadas.

El contenido externo no deberá convertirse automáticamente en conocimiento confiable.

La arquitectura será:

EXTERNAL DATA
      ↓
INGESTION
      ↓
VALIDATION
      ↓
NORMALIZATION
      ↓
DEDUPLICATION
      ↓
PROVENANCE
      ↓
QUALITY
      ↓
CORROBORATION
      ↓
KNOWLEDGE

⸻

30. Seguridad de la cadena de suministro

Las dependencias de software deberán estar controladas.

Se utilizarán progresivamente:

* Lockfiles.
* Versiones reproducibles.
* Escaneo de vulnerabilidades.
* SBOM.
* Revisión de dependencias.
* Actualizaciones controladas.
* Secret scanning.
* SAST.
* Escaneo de contenedores.
* Protección de CI/CD.
* Firma o atestación de artefactos cuando resulte viable.

No se incorporarán dependencias innecesarias.

⸻

31. CI/CD

Los pipelines deberán aplicar mínimo privilegio.

Los workflows deberán:

* Limitar permisos.
* Separar entornos.
* Proteger secretos.
* Evitar exposición de credenciales en logs.
* Requerir revisión para cambios críticos.
* Evitar despliegues no autorizados.
* Registrar despliegues.
* Permitir trazabilidad de artefactos.

Los secretos deberán estar disponibles únicamente para los procesos que realmente los necesiten.

⸻

32. Seguridad del código

El proceso de desarrollo deberá incorporar progresivamente:

* Linting.
* Type checking.
* Tests unitarios.
* Tests de integración.
* Tests de seguridad.
* SAST.
* Dependency scanning.
* Secret scanning.
* Fuzzing cuando resulte apropiado.
* Revisión de código.

Los cambios críticos deberán disponer de revisión independiente.

⸻

33. Contenedores

Las imágenes de contenedor deberán:

* Utilizar bases mínimas.
* Reducir superficie de ataque.
* Evitar ejecución como root cuando sea posible.
* Fijar versiones.
* No contener secretos.
* Ser escaneadas.
* Generar SBOM cuando corresponda.
* Utilizar imágenes confiables.
* Ser reconstruibles de forma reproducible cuando sea viable.

⸻

34. Segmentación de red

La infraestructura deberá dividirse en zonas de confianza diferentes.

Como mínimo deberá considerarse la separación entre:

* Internet.
* Reverse proxy / WAF.
* Aplicación.
* Servicios internos.
* Datos públicos.
* Datos restringidos.
* Administración.
* Monitorización.
* Backups.

No deberá existir conectividad innecesaria entre segmentos.

⸻

35. WAF y protección perimetral

Cuando CEUTIA esté expuesto públicamente se utilizarán controles perimetrales apropiados.

Podrán incluir:

* WAF.
* Reverse proxy.
* CDN.
* Rate limiting.
* Protección DDoS.
* Filtrado de tráfico.
* Detección de anomalías.

Estos mecanismos son capas complementarias y no sustituyen la seguridad de la aplicación.

⸻

36. Rate limiting

El rate limiting deberá poder aplicarse según el riesgo del recurso.

Podrá basarse en:

* IP.
* Identidad.
* API key.
* Endpoint.
* Recurso.
* Sesión.
* Tenant.
* Comportamiento.

Los límites deberán ajustarse al patrón operativo real.

⸻

37. Logging

Los eventos relevantes de seguridad deberán registrarse de forma estructurada.

Como mínimo:

* Autenticaciones.
* Fallos de autenticación.
* Cambios de privilegios.
* Autorizaciones denegadas.
* Acceso a datos sensibles.
* Cambios de configuración.
* Operaciones administrativas.
* Cambios de identidad.
* Rotación de claves.
* Incidentes.
* Alertas.
* Cambios en pipelines.
* Acciones relevantes de modelos.

Los logs no deberán almacenar información sensible innecesaria.

⸻

38. Integridad de logs

Los registros críticos deberán protegerse frente a:

* Modificación.
* Eliminación.
* Manipulación.
* Acceso no autorizado.

Cuando resulte viable deberán utilizarse:

* Almacenamiento append-only.
* Separación del sistema principal.
* Controles de integridad.
* Retención definida.
* Sincronización temporal fiable.

⸻

39. Monitorización

CEUTIA deberá monitorizar, cuando corresponda:

* Autenticaciones anómalas.
* Accesos inusuales.
* Escalada de privilegios.
* Exfiltración.
* Tráfico anómalo.
* Errores anómalos.
* Cambios de configuración.
* Cambios de fuentes.
* Alteraciones de pipelines.
* Cambios anómalos de indicadores.
* Comportamiento anómalo de modelos.

⸻

40. Detección y respuesta

La arquitectura podrá integrar:

* IDS.
* IPS.
* EDR.
* WAF telemetry.
* Network telemetry.
* SIEM.
* Threat intelligence.
* Detección basada en comportamiento.
* MITRE ATT&CK.

La detección no deberá depender exclusivamente de firmas conocidas.

⸻

41. Seguridad de modelos de IA

Los modelos de IA serán considerados componentes potencialmente vulnerables.

Se contemplarán, entre otras:

* Prompt injection.
* Indirect prompt injection.
* Data poisoning.
* Model poisoning.
* Model extraction.
* Adversarial inputs.
* Fuga de información.
* Insecure tool use.
* Excessive agency.
* Manipulación del contexto.
* Alucinaciones.
* Automatización indebida.
* Automation bias.

Los modelos deberán operar con el mínimo privilegio necesario.

⸻

42. Separación entre IA y autoridad

Un modelo de IA no deberá disponer por defecto de autoridad para:

* Conceder permisos.
* Modificar políticas de seguridad.
* Acceder a información fuera de su autorización.
* Publicar información restringida.
* Ejecutar operaciones irreversibles.
* Modificar datos críticos.
* Generar por sí solo decisiones de máxima consecuencia.

Las acciones críticas deberán pasar por controles deterministas y/o autorización humana cuando corresponda.

⸻

43. Integridad de modelos

Cada modelo relevante deberá poder asociarse, cuando corresponda, con:

* Identificador.
* Versión.
* Configuración.
* Fecha.
* Datos utilizados.
* Métricas.
* Validación.
* Limitaciones.
* Responsable.
* Entorno de ejecución.

Los cambios relevantes deberán ser trazables.

⸻

44. Data poisoning

La contaminación deliberada de datos será considerada amenaza de seguridad.

Deberán contemplarse mecanismos para detectar, cuando sea técnicamente posible:

* Cambios abruptos de distribución.
* Comportamientos anómalos.
* Duplicación coordinada.
* Alteraciones de fuentes.
* Inconsistencias temporales.
* Inconsistencias espaciales.
* Cambios anómalos en metadatos.
* Contaminación deliberada.

⸻

45. Seguridad de indicadores y alertas

Los indicadores y alertas deberán conservar:

* Procedencia.
* Evidencia.
* Fecha.
* Incertidumbre.
* Confianza.
* Contradicciones.
* Versión del algoritmo.
* Parámetros relevantes.
* Condiciones que provocaron la alerta.

Una alerta deberá distinguirse conceptualmente de un hecho confirmado.

La arquitectura deberá representar, cuando corresponda:

OBSERVATION
     ↓
SIGNAL
     ↓
INDICATOR
     ↓
ASSESSMENT
     ↓
ALERT
     ↓
RECOMMENDATION

⸻

46. Alertas de alta criticidad

Las alertas de máxima severidad deberán estar sujetas a controles reforzados.

Cuando la situación lo permita:

* Corroboración independiente.
* Revisión humana.
* Explicación.
* Trazabilidad.
* Registro de decisión.
* Conservación de evidencia.

Las excepciones por emergencia deberán estar definidas y auditadas.

⸻

47. Supervisión humana

Las decisiones automatizadas con potencial de producir consecuencias graves deberán incorporar supervisión humana cuando así lo determine el análisis de riesgo.

Las acciones humanas relevantes deberán quedar registradas.

⸻

48. Protección de datos personales

Cuando CEUTIA trate datos personales deberá aplicar, según corresponda:

* Minimización.
* Limitación de finalidad.
* Exactitud.
* Limitación de conservación.
* Integridad y confidencialidad.
* Control de acceso.
* Trazabilidad.
* Protección desde el diseño.
* Protección por defecto.

Los datos especialmente sensibles deberán recibir controles reforzados.

La base jurídica, finalidad, conservación y demás obligaciones deberán determinarse para cada tratamiento cuando resulte necesario.

⸻

49. Datos sanitarios

Cuando CEUTIA incorpore datos sanitarios reales deberá existir una arquitectura específica de protección.

Deberán evaluarse:

* Base jurídica.
* Finalidad.
* Minimización.
* Control de acceso.
* Segregación.
* Cifrado.
* Auditoría.
* Retención.
* Eliminación.
* Riesgos de reidentificación.
* Obligaciones regulatorias aplicables.

HIPAA únicamente será aplicable cuando concurran las condiciones jurídicas que hagan aplicable dicha normativa.

⸻

50. Backups

Los backups deberán:

* Estar cifrados cuando corresponda.
* Estar protegidos frente a acceso no autorizado.
* Mantener separación de privilegios.
* Disponer de política de retención.
* Ser sometidos a pruebas de restauración.
* Estar protegidos frente a ransomware cuando sea viable.
* Mantener suficiente independencia respecto del sistema principal.

Un backup que nunca ha sido restaurado satisfactoriamente no deberá considerarse plenamente validado.

⸻

51. Recuperación

CEUTIA deberá definir:

* RPO.
* RTO.
* Dependencias críticas.
* Procedimientos de restauración.
* Orden de recuperación.
* Responsables.
* Procedimientos de contingencia.

Los objetivos deberán establecerse en función de la criticidad real de cada servicio.

⸻

52. Gestión de vulnerabilidades

Las vulnerabilidades deberán:

1. Detectarse.
2. Clasificarse.
3. Evaluarse.
4. Priorizarse.
5. Mitigarse o corregirse.
6. Verificarse.
7. Registrarse.

La prioridad deberá considerar:

* Severidad técnica.
* Exposición.
* Explotabilidad.
* Activo afectado.
* Sensibilidad.
* Impacto potencial.
* Existencia de mitigaciones.

⸻

53. Gestión de configuración

Las configuraciones críticas deberán estar:

* Versionadas cuando sea posible.
* Revisadas.
* Reproducibles cuando sea viable.
* Documentadas.
* Protegidas frente a modificaciones no autorizadas.

No se deberán realizar cambios críticos manuales sin trazabilidad.

⸻

54. Gestión de incidentes

El ciclo de respuesta será:

PREPARATION
      ↓
DETECTION
      ↓
ANALYSIS
      ↓
CONTAINMENT
      ↓
ERADICATION
      ↓
RECOVERY
      ↓
LESSONS LEARNED

Los incidentes deberán clasificarse según:

* Impacto.
* Probabilidad.
* Alcance.
* Criticidad.
* Sensibilidad.
* Afectación de datos.
* Afectación de infraestructura.
* Afectación de modelos.
* Afectación epistemológica.

⸻

55. Contención

Ante un compromiso confirmado o altamente probable podrán aplicarse:

* Revocación de credenciales.
* Aislamiento de servicios.
* Bloqueo de identidades.
* Rotación de secretos.
* Rotación de claves.
* Aislamiento de hosts.
* Suspensión de pipelines.
* Congelación de publicaciones.
* Preservación de evidencias.

Las medidas deberán procurar preservar la evidencia necesaria para la investigación.

⸻

56. Evidencia forense

Cuando exista un incidente relevante deberán preservarse, cuando sea legal y técnicamente apropiado:

* Logs.
* Eventos de autenticación.
* Artefactos.
* Configuraciones.
* Timestamps.
* Identificadores.
* Evidencia de red.
* Estado de sistemas.
* Versiones de software.
* Evidencia epistemológica relacionada.

La evidencia deberá conservar su integridad y procedencia.

⸻

57. Seguridad operacional

Las operaciones administrativas deberán realizarse mediante identidades individualizadas.

Las acciones privilegiadas deberán ser auditables.

Los accesos administrativos deberán limitarse por:

* Necesidad.
* Función.
* Tiempo.
* Recurso.
* Contexto.

Cuando sea apropiado deberán utilizarse accesos temporales y justificados.

⸻

58. Seguridad física

La seguridad física dependerá de la infraestructura donde se despliegue CEUTIA.

Los requisitos físicos relevantes deberán ser evaluados respecto del proveedor de infraestructura seleccionado.

No se asumirá que un proveedor ofrece un control físico concreto sin evidencia contractual o técnica.

⸻

59. Dependencias externas

Todo proveedor externo que procese información de CEUTIA deberá evaluarse según:

* Datos tratados.
* Sensibilidad.
* Localización.
* Accesos.
* Seguridad.
* Disponibilidad.
* Dependencias.
* Subcontratación.
* Retención.
* Eliminación.
* Capacidad de auditoría.

Los proveedores críticos deberán disponer de controles contractuales apropiados.

⸻

60. Seguridad del repositorio

El repositorio deberá incorporar progresivamente:

* Protección de ramas.
* Revisión obligatoria.
* CODEOWNERS cuando corresponda.
* Secret scanning.
* Dependabot o equivalente.
* Protección contra publicación accidental de secretos.
* CI/CD protegido.
* Auditoría de cambios.
* Gestión de permisos.

No deberán almacenarse secretos de producción en Git.

⸻

61. Desarrollo seguro

Todo nuevo componente deberá considerar desde su diseño:

* Amenazas.
* Datos que tratará.
* Nivel de sensibilidad.
* Identidad.
* Autorización.
* Validación.
* Logging.
* Gestión de errores.
* Dependencias.
* Privacidad.
* Recuperación.
* Abuso previsto.

La seguridad no deberá añadirse únicamente después de terminar la funcionalidad.

⸻

62. Threat modeling

Los componentes críticos deberán someterse a análisis de amenazas.

Podrán utilizarse metodologías como:

* STRIDE.
* MITRE ATT&CK.
* Attack trees.
* Abuse cases.
* Data-flow analysis.
* Risk assessment.

El método deberá seleccionarse según el componente analizado.

⸻

63. Pruebas de seguridad

CEUTIA deberá realizar progresivamente:

* Tests de autenticación.
* Tests de autorización.
* Tests de aislamiento.
* Tests de validación.
* Tests de API.
* SAST.
* Dependency scanning.
* Secret scanning.
* Container scanning.
* DAST cuando corresponda.
* Fuzzing cuando corresponda.
* Tests de recuperación.
* Tests de integridad epistemológica.

⸻

64. Seguridad de la información generada

La información generada por CEUTIA deberá mantener una distinción explícita entre:

* Dato observado.
* Dato procesado.
* Evidencia.
* Afirmación.
* Inferencia.
* Hipótesis.
* Predicción.
* Escenario.
* Recomendación.

El sistema no deberá presentar una inferencia como si fuera una observación.

⸻

65. Incertidumbre

Los resultados relevantes deberán poder representar incertidumbre.

Cuando sea apropiado deberán distinguirse:

* Incertidumbre aleatoria.
* Incertidumbre epistémica.
* Información incompleta.
* Conflicto de evidencia.
* Dependencia de fuentes.
* Sensibilidad del resultado.

La ausencia de incertidumbre registrada no deberá interpretarse automáticamente como certeza.

⸻

66. Evolución de creencias

Cuando nueva evidencia modifique una afirmación, hipótesis o evaluación:

* deberá conservarse el estado anterior;
* deberá registrarse la nueva evidencia;
* deberá registrarse el cambio;
* deberá conservarse la procedencia;
* deberá poder reconstruirse la evolución.

El conocimiento de CEUTIA será versionado cuando sea necesario para garantizar trazabilidad.

⸻

67. Seguridad de grafos y relaciones

Los grafos de conocimiento deberán protegerse frente a:

* Inserción maliciosa de entidades.
* Relaciones falsas.
* Duplicación artificial.
* Eliminación de relaciones.
* Manipulación de pesos.
* Manipulación de centralidad.
* Contaminación de comunidades.
* Manipulación de dependencia entre fuentes.

Las relaciones críticas deberán conservar su procedencia.

⸻

68. Seguridad de sistemas de detección

Los algoritmos de detección deberán protegerse frente a:

* Manipulación de entradas.
* Data poisoning.
* Concept drift no detectado.
* Cambios de distribución.
* Falsos positivos inducidos.
* Falsos negativos inducidos.
* Manipulación de umbrales.

Los cambios relevantes de parámetros deberán ser auditables.

⸻

69. Seguridad de simulaciones y escenarios

Los escenarios y simulaciones deberán distinguir entre:

* Datos observados.
* Parámetros asumidos.
* Hipótesis.
* Supuestos.
* Resultados simulados.

Un resultado de simulación no deberá presentarse como predicción determinista de un acontecimiento futuro.

Los supuestos relevantes deberán conservarse.

⸻

70. Auditoría

Las operaciones críticas deberán poder reconstruirse.

Como mínimo deberá poder determinarse:

WHO
WHAT
WHEN
FROM WHERE
WHICH RESOURCE
WHICH VERSION
WHICH DATA
WHICH POLICY
WHICH RESULT

La auditoría deberá cubrir tanto operaciones humanas como operaciones automatizadas relevantes.

⸻

71. Trazabilidad de modelos y decisiones

Cuando una alerta o resultado dependa de un modelo, deberá ser posible determinar:

DATA
  ↓
FEATURES / REPRESENTATION
  ↓
MODEL VERSION
  ↓
PARAMETERS
  ↓
OUTPUT
  ↓
RULE / THRESHOLD
  ↓
ALERT

La trazabilidad deberá permitir investigar posteriormente por qué se produjo un resultado.

⸻

72. Separación de funciones

Cuando el nivel de riesgo lo requiera deberán separarse:

* Desarrollo.
* Administración.
* Análisis.
* Auditoría.
* Operación.
* Aprobación.

Una única identidad no deberá concentrar innecesariamente todas las capacidades críticas.

⸻

73. Principio de mínima exposición

CEUTIA deberá minimizar:

* Puertos expuestos.
* Servicios públicos.
* Endpoints.
* Permisos.
* Dependencias.
* Credenciales.
* Datos almacenados.
* Información incluida en tokens.
* Información incluida en logs.

Todo componente deberá exponer únicamente aquello que necesita para cumplir su función.

⸻

74. Principio de mínima confianza

Cada componente deberá confiar únicamente en aquello que necesite.

La confianza entre servicios deberá establecerse explícitamente.

Cuando resulte apropiado se utilizarán:

* Autenticación mutua.
* Identidades de servicio.
* Credenciales de corta duración.
* TLS.
* Políticas de autorización.
* Segmentación.

⸻

75. Seguridad de terceros

Las fuentes, proveedores y servicios externos deberán considerarse entidades potencialmente comprometibles.

La confianza en terceros deberá depender de evidencia y no únicamente de reputación.

La plataforma deberá poder degradar la confianza asignada a una fuente cuando aparezcan indicios de compromiso, manipulación o inconsistencia.

⸻

76. Continuidad

La seguridad deberá contemplar escenarios de:

* Caída de infraestructura.
* Pérdida de base de datos.
* Corrupción de datos.
* Compromiso de credenciales.
* Compromiso de proveedores.
* Ransomware.
* DDoS.
* Compromiso de aplicación.
* Compromiso de fuente.
* Manipulación epistemológica.

⸻

77. Principio de no confianza implícita en IA

Los resultados generados por modelos deberán considerarse outputs analíticos.

No deberán elevar automáticamente su nivel de confianza únicamente por proceder de un modelo.

La confianza deberá depender de:

* Calidad de datos.
* Evidencia.
* Validación.
* Rendimiento histórico.
* Incertidumbre.
* Corroboración.
* Contexto.

⸻

78. Evaluación continua

La seguridad de CEUTIA será un proceso continuo.

Deberán revisarse periódicamente:

* Amenazas.
* Vulnerabilidades.
* Dependencias.
* Configuraciones.
* Permisos.
* Credenciales.
* Modelos.
* Fuentes.
* Pipelines.
* Alertas.
* Incidentes.
* Controles.
* Supuestos.

⸻

79. Métricas de seguridad

CEUTIA deberá establecer métricas como:

* Vulnerabilidades abiertas.
* Tiempo medio de resolución.
* Cobertura MFA.
* Cobertura de logging.
* Cobertura de tests.
* Incidentes.
* Intentos de acceso no autorizado.
* Secretos detectados.
* Dependencias vulnerables.
* Tiempo de recuperación.
* Éxito de restauraciones.
* Cobertura de procedencia.
* Cobertura de auditoría.
* Incidentes epistemológicos.
* Alteraciones detectadas de fuentes.
* Falsos positivos y negativos de controles críticos.

⸻

80. Gestión de cambios

Los cambios relevantes de arquitectura, seguridad, identidad, datos o modelos deberán:

* Estar versionados.
* Ser revisados.
* Poder revertirse cuando sea viable.
* Tener trazabilidad.
* Evaluarse respecto de su impacto de seguridad.

Los cambios críticos deberán someterse a una evaluación específica.

⸻

81. Excepciones

Toda excepción a esta política deberá:

* Estar documentada.
* Tener justificación.
* Identificar el riesgo.
* Identificar medidas compensatorias.
* Tener responsable.
* Tener fecha de revisión.
* Ser revocable.

Las excepciones permanentes deberán evitarse cuando exista una alternativa técnicamente razonable.

⸻

82. Divulgación de vulnerabilidades

CEUTIA deberá disponer de un mecanismo para recibir comunicaciones responsables sobre vulnerabilidades.

Las comunicaciones deberán permitir:

* Descripción.
* Evidencia.
* Reproducción cuando sea posible.
* Impacto.
* Método de contacto.

Las vulnerabilidades recibidas deberán gestionarse mediante un proceso formal.

⸻

83. Responsabilidad

La seguridad no pertenece exclusivamente al componente de infraestructura.

Cada componente deberá tener claramente definido:

* Propietario.
* Responsable técnico.
* Nivel de criticidad.
* Datos tratados.
* Dependencias.
* Riesgos.
* Controles.
* Estado de implementación.

⸻

84. Revisión de esta política

Esta política deberá revisarse:

* Cuando cambie significativamente la arquitectura.
* Tras incidentes relevantes.
* Ante cambios regulatorios relevantes.
* Ante nuevas amenazas.
* Ante cambios significativos en infraestructura.
* Ante incorporación de nuevos tipos de datos.
* Ante incorporación de nuevos modelos o capacidades de IA.

⸻

85. Regla final

CEUTIA no considerará seguro un sistema simplemente porque:

* utilice HTTPS;
* tenga autenticación;
* tenga un firewall;
* utilice JWT;
* tenga cifrado;
* utilice PostgreSQL;
* utilice un WAF;
* utilice MFA;
* utilice IA;
* tenga logs;
* tenga backups;
* cumpla una checklist.

La seguridad será evaluada como una propiedad sistémica.

En CEUTIA, la seguridad debe proteger tanto el sistema que produce inteligencia como la integridad de la inteligencia producida.

La arquitectura deberá asumir que:

LA INFRAESTRUCTURA PUEDE SER ATACADA
LA IDENTIDAD PUEDE SER COMPROMETIDA
LAS FUENTES PUEDEN SER MANIPULADAS
LOS DATOS PUEDEN SER CONTAMINADOS
LOS MODELOS PUEDEN FALLAR
LOS RESULTADOS PUEDEN SER INCORRECTOS
LOS ADVERSARIOS PUEDEN ADAPTARSE

Por ello:

SEGURIDAD TÉCNICA
        +
SEGURIDAD DE DATOS
        +
SEGURIDAD DE IDENTIDAD
        +
SEGURIDAD DE INFRAESTRUCTURA
        +
SEGURIDAD DE MODELOS
        +
SEGURIDAD EPISTEMOLÓGICA
        =
SEGURIDAD CEUTIA

Esta política constituye la base normativa para el diseño, implementación, evaluación y evolución de los controles de seguridad de CEUTIA.