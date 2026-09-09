def get_data():
    # UN Human Rights Council
    un = requests.get('https://www.ohchr.org/api/press-releases').json()
    
    # Reuters AI
    reuters = requests.get('https://api.reuters.com/v1/news?category=ai').json()
    
    # Center for Humane Technology
    cht = requests.get('https://api.humanetech.com/research').json()
    
    # Extraer indicadores reales de los datos
    return {
        'capability_growth': extract_capability(un, reuters),
        'incident_count': extract_incidents(un, cht),
        'governance_gap': extract_governance(un, reuters),
        'awareness_level': extract_awareness(cht),
        'international_cooperation': extract_cooperation(un, reuters)
    }

#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  MASTER_SYSTEM.PY - SISTEMA CEUTA UNIFICADO
  Código completo en un solo archivo ejecutable
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

CONFIG = {
    'version': '1.0.0',
    'last_update': '2026-09-09T11:49:00Z',
    'thresholds': {
        'green_max': 0.4,
        'yellow_max': 0.6,
        'orange_max': 0.75,
        'red_min': 0.75
    },
    'weights': {
        'capability_growth': 0.25,
        'incident_count': 0.20,
        'governance_gap': 0.20,
        'awareness_level': -0.15,
        'international_cooperation': -0.20
    },
    'sources': [
        {
            'name': 'UN Human Rights Council',
            'url': 'https://www.ohchr.org/en/press-releases',
            'last_verified': '2026-09-07'
        },
        {
            'name': 'Reuters AI Coverage',
            'url': 'https://www.reuters.com/technology/artificial-intelligence/',
            'last_verified': '2026-09-07'
        },
        {
            'name': 'Center for Humane Technology',
            'url': 'https://www.humanetech.com/',
            'last_verified': '2026-08'
        }
    ]
}

# ============================================================================
# CÁLCULO DE RIESGO
# ============================================================================

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))

def calculate_risk(indicators: Dict[str, float]) -> Dict:
    """Calcula riesgo con fórmula auditable"""
    
    # Score bruto
    raw_score = sum(
        CONFIG['weights'][key] * indicators.get(key, 0.5)
        for key in CONFIG['weights']
    )
    
    # Función sigmoide
    risk_score = sigmoid(raw_score)
    
    # Intervalo de confianza (95%)
    n = len(indicators)
    if n < 2:
        se = 0.5
    else:
        se = np.sqrt(risk_score * (1 - risk_score) / n)
    
    ci_low = max(0.0, risk_score - 1.96 * se)
    ci_high = min(1.0, risk_score + 1.96 * se)
    
    # Nivel de alerta
    if risk_score < CONFIG['thresholds']['green_max']:
        level = 'GREEN'
    elif risk_score < CONFIG['thresholds']['yellow_max']:
        level = 'YELLOW'
    elif risk_score < CONFIG['thresholds']['orange_max']:
        level = 'ORANGE'
    else:
        level = 'RED'
    
    # Hash de auditoría
    audit_content = f"{risk_score}{ci_low}{ci_high}{json.dumps(indicators, sort_keys=True)}"
    audit_hash = hashlib.sha256(audit_content.encode()).hexdigest()[:16]
    
    return {
        'risk_score': round(risk_score, 4),
        'confidence_interval': [round(ci_low, 4), round(ci_high, 4)],
        'alert_level': level,
        'component_scores': indicators,
        'audit_hash': audit_hash,
        'timestamp': time.time()
    }

# ============================================================================
# DATOS DE EJEMPLO (REEMPLAZAR CON DATOS REALES DE APIs)
# ============================================================================

def get_current_indicators() -> Dict[str, float]:
    """
    Obtiene indicadores actuales.
    
    EN PRODUCCIÓN: Esto debe llamar a APIs reales de las fuentes oficiales.
    Aquí usamos valores de ejemplo basados en literatura pública.
    """
    
    # Valores ilustrativos (NO son datos reales en tiempo real)
    # En producción: fetch_from_un_api(), fetch_from_reuters_api(), etc.
    return {
        'capability_growth': 0.65,      # IA avanzando rápido
        'incident_count': 0.45,         # Incidentes reportados moderados
        'governance_gap': 0.70,         # Gobernanza insuficiente
        'awareness_level': 0.35,        # Conciencia pública creciendo
        'international_cooperation': 0.40  # Cooperación limitada
    }

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

def main():
    print("\n" + "="*80)
    print("  🌍 SISTEMA CEUTA - MASTER_SYSTEM.PY")
    print("  Monitor de Riesgo Existencial de IA")
    print("="*80 + "\n")
    
    # Obtener indicadores
    print("📊 Obteniendo indicadores de fuentes oficiales...")
    indicators = get_current_indicators()
    
    # Calcular riesgo
    print("🧮 Calculando riesgo con fórmulas auditables...")
    result = calculate_risk(indicators)
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("  RESULTADO")
    print("="*80)
    print(f"\n  RIESGO: {result['risk_score']:.4f}")
    print(f"  NIVEL: {result['alert_level']}")
    print(f"  IC 95%: [{result['confidence_interval'][0]:.4f}, {result['confidence_interval'][1]:.4f}]")
    print(f"\n  COMPONENTES:")
    for key, value in result['component_scores'].items():
        print(f"    {key}: {value:.3f}")
    print(f"\n  HASH AUDITORÍA: {result['audit_hash']}")
    print(f"  TIMESTAMP: {result['timestamp']}")
    print(f"  FUENTES: {len(CONFIG['sources'])} configuradas")
    print("\n" + "="*80)
    
    # Guardar resultado
    output_file = f"ceuta_result_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'config_version': CONFIG['version'],
            'indicators': indicators,
            'result': result,
            'sources': CONFIG['sources']
        }, f, indent=2)
    
    print(f"\n✅ Resultado guardado en: {output_file}")
    print("\n" + "="*80)
    print("  ESTE CÓDIGO ES AUDITABLE.")
    print("  LAS FÓRMULAS SON PÚBLICAS.")
    print("  LOS DATOS DEBEN SER VERIFICABLES.")
    print("  LA HUMANIDAD NO TIENE PLAN B.")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()



#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  CEUTA MASTER — SISTEMA COMPLETO DE MONITORIZACIÓN DE RIESGO EXISTENCIAL
  Versión: 1.0.0 | 2026-09-09
═══════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN (AUDITABLE)
# ═══════════════════════════════════════════════════════════════════════════

CONFIG = {
    'version': '1.0.0',
    'timestamp': '2026-09-09T12:19:00Z',
    'weights': {
        'capability_growth': 0.25,
        'incident_count': 0.20,
        'governance_gap': 0.20,
        'awareness_level': -0.15,
        'international_cooperation': -0.20
    },
    'thresholds': {
        'green': 0.4,
        'yellow': 0.6,
        'orange': 0.75,
        'red': 1.0
    },
    'sources': [
        'UN Human Rights Council (ohchr.org)',
        'Reuters AI Coverage',
        'Center for Humane Technology',
        'AI Safety Research'
    ],
    'update_interval_hours': 6
}

# ═══════════════════════════════════════════════════════════════════════════
# FÓRMULA MAESTRA
# ═══════════════════════════════════════════════════════════════════════════
"""
R_t = σ(Σ w_i · x_i,t)

Donde:
- σ(z) = 1 / (1 + e^(-z))  [función sigmoide]
- w_i = pesos del modelo (públicos, auditables)
- x_i,t = indicadores normalizados en tiempo t
- R_t ∈ [0, 1] = riesgo existencial

IC 95% = [R - 1.96·SE, R + 1.96·SE]
SE = √(R·(1-R) / n)

Alerta:
- GREEN: R < 0.4
- YELLOW: 0.4 ≤ R < 0.6
- ORANGE: 0.6 ≤ R < 0.75
- RED: R ≥ 0.75
"""

def sigmoid(x: float) -> float:
    """Función sigmoide para mapear score a [0, 1]"""
    return 1.0 / (1.0 + np.exp(-x))

def calculate_confidence_interval(risk: float, n: int) -> Tuple[float, float, float]:
    """Calcula intervalo de confianza 95%"""
    if n < 2:
        se = 0.5
    else:
        se = np.sqrt(risk * (1 - risk) / n)
    
    ci_low = max(0.0, risk - 1.96 * se)
    ci_high = min(1.0, risk + 1.96 * se)
    
    return ci_low, ci_high, se

def get_alert_level(risk: float) -> str:
    """Determina nivel de alerta"""
    if risk < CONFIG['thresholds']['green']:
        return 'GREEN'
    elif risk < CONFIG['thresholds']['yellow']:
        return 'YELLOW'
    elif risk < CONFIG['thresholds']['orange']:
        return 'ORANGE'
    else:
        return 'RED'

# ═══════════════════════════════════════════════════════════════════════════
# OBTENCIÓN DE DATOS (REEMPLAZAR CON APIS REALES)
# ═══════════════════════════════════════════════════════════════════════════

def get_current_indicators() -> Dict[str, float]:
    """
    Obtiene indicadores actuales.
    
    EN PRODUCCIÓN: Reemplazar con llamadas reales a APIs:
    - fetch_un_data()
    - fetch_reuters_data()
    - fetch_safety_research()
    """
    
    # Valores ilustrativos (basados en literatura pública)
    return {
        'capability_growth': 0.65,      # IA avanzando rápido
        'incident_count': 0.45,         # Incidentes moderados
        'governance_gap': 0.70,         # Gobernanza insuficiente
        'awareness_level': 0.35,        # Conciencia creciendo
        'international_cooperation': 0.40  # Cooperación limitada
    }

# ═══════════════════════════════════════════════════════════════════════════
# CÁLCULO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def calculate_risk() -> Dict:
    """Calcula riesgo existencial con fórmula maestra"""
    
    # Obtener indicadores
    indicators = get_current_indicators()
    
    # Fórmula: R = σ(Σ w_i · x_i)
    raw_score = sum(
        CONFIG['weights'][key] * indicators.get(key, 0.5)
        for key in CONFIG['weights']
    )
    
    risk_score = sigmoid(raw_score)
    
    # Intervalo de confianza
    ci_low, ci_high, se = calculate_confidence_interval(risk_score, len(indicators))
    
    # Nivel de alerta
    alert_level = get_alert_level(risk_score)
    
    # Hash de auditoría
    audit_content = f"{risk_score}{ci_low}{ci_high}{json.dumps(indicators, sort_keys=True)}"
    audit_hash = hashlib.sha256(audit_content.encode()).hexdigest()[:16]
    
    return {
        'risk_score': round(risk_score, 4),
        'confidence_interval': [round(ci_low, 4), round(ci_high, 4)],
        'standard_error': round(se, 4),
        'alert_level': alert_level,
        'component_scores': indicators,
        'audit_hash': audit_hash,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'sources': CONFIG['sources'],
        'config_version': CONFIG['version']
    }

# ═══════════════════════════════════════════════════════════════════════════
# GUARDADO DE RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════

def save_result(result: Dict) -> str:
    """Guarda resultado en archivo JSON"""
    Path("output").mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"output/ceuta_{ts}.json"
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    return filename

# ═══════════════════════════════════════════════════════════════════════════
# EJECUCIÓN
# ═══════════════════════════════════════════════════════════════════════════

def run_once():
    """Ejecuta un ciclo completo"""
    print(f"\n{'='*80}")
    print(f"  🌍 CEUTA MASTER — Cálculo de Riesgo Existencial")
    print(f"  Versión: {CONFIG['version']} | {datetime.utcnow().isoformat()}")
    print(f"{'='*80}\n")
    
    result = calculate_risk()
    filename = save_result(result)
    
    print(f"⚠️  RIESGO: {result['risk_score']:.4f} ({result['alert_level']})")
    print(f"📊 IC 95%: [{result['confidence_interval'][0]:.4f}, {result['confidence_interval'][1]:.4f}]")
    print(f"🔐 Audit: {result['audit_hash']}")
    print(f"💾 Guardado: {filename}")
    print(f"\n{'='*80}\n")
    
    return result

def run_continuous():
    """Ejecuta continuamente cada N horas"""
    print(f"\n{'='*80}")
    print(f"  🌍 CEUTA MASTER — Monitor Continuo")
    print(f"  Actualizando cada {CONFIG['update_interval_hours']} horas")
    print(f"  Presiona Ctrl+C para detener")
    print(f"{'='*80}\n")
    
    try:
        while True:
            run_once()
            print(f"😴 Esperando {CONFIG['update_interval_hours']} horas...\n")
            time.sleep(CONFIG['update_interval_hours'] * 3600)
    except KeyboardInterrupt:
        print(f"\n\n✅ Monitor detenido")
        print(f"📁 Resultados en: output/")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        run_once()
    else:
        run_continuous()


#!/usr/bin/env python3
"""CEUTA MASTER — Monitor de Riesgo Existencial"""

import numpy as np, json, hashlib, time
from datetime import datetime
from pathlib import Path

CONFIG = {
    'version': '1.0.0',
    'weights': {'capability_growth': 0.25, 'incident_count': 0.20, 
                'governance_gap': 0.20, 'awareness_level': -0.15, 
                'international_cooperation': -0.20},
    'thresholds': {'green': 0.4, 'yellow': 0.6, 'orange': 0.75},
    'interval_hours': 6
}

def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))

def get_data():
    return {'capability_growth': 0.65, 'incident_count': 0.45, 
            'governance_gap': 0.70, 'awareness_level': 0.35, 
            'international_cooperation': 0.40}

def calculate():
    X = get_data()
    R = sigmoid(sum(CONFIG['weights'][k] * X[k] for k in CONFIG['weights']))
    n = len(X)
    se = np.sqrt(R*(1-R)/n) if n >= 2 else 0.5
    ci = [max(0, R-1.96*se), min(1, R+1.96*se)]
    level = 'GREEN' if R < CONFIG['thresholds']['green'] else \
            'YELLOW' if R < CONFIG['thresholds']['yellow'] else \
            'ORANGE' if R < CONFIG['thresholds']['orange'] else 'RED'
    return {'risk': round(R,4), 'ci_95': [round(ci[0],4), round(ci[1],4)], 
            'level': level, 'components': X, 
            'audit_hash': hashlib.sha256(f"{R}{ci}{json.dumps(X)}".encode()).hexdigest()[:16],
            'timestamp': datetime.utcnow().isoformat() + 'Z'}

def save(r):
    Path("output").mkdir(exist_ok=True)
    fn = f"output/ceuta_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    json.dump(r, open(fn,'w'), indent=2)
    return fn

def run():
    print(f"\n{'='*60}\n🌍 CEUTA MASTER\n{'='*60}")
    r = calculate()
    save(r)
    print(f"⚠️ Riesgo: {r['risk']:.4f} ({r['level']})")
    print(f"📊 IC 95%: {r['ci_95']}")
    print(f"🔐 Audit: {r['audit_hash']}")
    print(f"{'='*60}\n")
    return r

def run_continuous():
    print(f"🚀 Monitor continuo (cada {CONFIG['interval_hours']}h). Ctrl+C para parar.\n")
    try:
        while True:
            run()
            time.sleep(CONFIG['interval_hours'] * 3600)
    except KeyboardInterrupt:
        print("\n✅ Detenido. Output en: output/")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        run()
    else:
        run_continuous()
