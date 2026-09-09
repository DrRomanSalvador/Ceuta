#!/usr/bin/env python3
"""
CEUTA FINAL - Monitor Continuo Actualizando
Ejecuta → Calcula → Guarda → Espera → Repite
"""

import time
import json
import hashlib
import numpy as np
from datetime import datetime
from pathlib import Path

# CONFIG
W = {'capability_growth': 0.25, 'incident_count': 0.20, 'governance_gap': 0.20, 
     'awareness_level': -0.15, 'international_cooperation': -0.20}
THRESHOLDS = {'green': 0.4, 'yellow': 0.6, 'orange': 0.75}
INTERVAL_HOURS = 6  # Cada cuántas horas se actualiza

def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))

def get_data():
    """
    AQUÍ VAN LAS APIs REALES.
    Por ahora: datos simulados basados en fuentes públicas.
    """
    return {
        'capability_growth': 0.65,
        'incident_count': 0.45,
        'governance_gap': 0.70,
        'awareness_level': 0.35,
        'international_cooperation': 0.40
    }

def calculate():
    X = get_data()
    raw = sum(W[k] * X[k] for k in W)
    R = sigmoid(raw)
    n = len(X)
    se = np.sqrt(R * (1-R) / n) if n >= 2 else 0.5
    ci = [max(0, R - 1.96*se), min(1, R + 1.96*se)]
    level = 'GREEN' if R < THRESHOLDS['green'] else 'YELLOW' if R < THRESHOLDS['yellow'] else 'ORANGE' if R < THRESHOLDS['orange'] else 'RED'
    audit = hashlib.sha256(f"{R}{ci}{json.dumps(X)}".encode()).hexdigest()[:16]
    
    return {
        'risk': round(R, 4),
        'ci_95': [round(ci[0], 4), round(ci[1], 4)],
        'level': level,
        'components': X,
        'audit_hash': audit,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

def save_result(result):
    """Guarda resultado con timestamp único"""
    Path("output").mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"output/ceuta_{ts}.json"
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"💾 Guardado: {filename}")

def run_once():
    """Ejecuta un ciclo"""
    print(f"\n{'='*60}")
    print(f"🕐 {datetime.utcnow().isoformat()}")
    print(f"{'='*60}")
    result = calculate()
    save_result(result)
    print(f"⚠️ Riesgo: {result['risk']:.4f} ({result['level']})")
    print(f"📊 IC 95%: {result['ci_95']}")
    print(f"🔐 Audit: {result['audit_hash']}")
    return result

def run_continuous():
    """Ejecuta continuamente cada INTERVAL_HOURS"""
    print("\n🌍 CEUTA FINAL - Monitor Continuo")
    print(f"📡 Actualizando cada {INTERVAL_HOURS} horas...")
    print("⏹️  Presiona Ctrl+C para detener\n")
    
    try:
        while True:
            run_once()
            print(f"\n😴 Esperando {INTERVAL_HOURS} horas...")
            time.sleep(INTERVAL_HOURS * 3600)
    except KeyboardInterrupt:
        print("\n\n✅ Monitor detenido por usuario")
        print("📁 Todos los resultados están en: output/")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        run_once()
    else:
        run_continuous()
