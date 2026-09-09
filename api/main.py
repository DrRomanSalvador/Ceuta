"""
API REST del Sistema Ceuta
Endpoints para integración con dashboards y otros sistemas
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import uvicorn

from src.monitor import CeutaMonitor
from src.config import SystemConfig

app = FastAPI(
    title="Ceuta System API",
    description="API para monitorización de riesgo existencial de IA",
    version="1.0.0"
)

# CORS para dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia del monitor
monitor = CeutaMonitor()

@app.get("/")
async def root():
    """Endpoint de salud"""
    return {
        "service": "Ceuta System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/status")
async def get_status():
    """Obtiene estado actual del sistema"""
    return monitor.get_current_status()

@app.get("/risk/current")
async def get_current_risk():
    """Obtiene cálculo de riesgo más reciente"""
    if not monitor.last_risk_result:
        # Ejecutar cálculo si no existe
        monitor.run_once()
    
    return monitor.last_risk_result.to_dict()

@app.post("/risk/calculate")
async def calculate_risk():
    """Fuerza nuevo cálculo de riesgo"""
    result = monitor.run_once()
    return result.to_dict()

@app.get("/alerts")
async def get_alerts(limit: int = 10):
    """Obtiene historial de alertas"""
    return monitor.alert_system.get_alert_history(limit)

@app.get("/sources")
async def get_sources():
    """Obtiene lista de fuentes de datos configuradas"""
    config = SystemConfig()
    return [
        {
            "name": source.name,
            "url": source.url,
            "last_verified": source.last_verified,
            "update_frequency_hours": source.update_frequency_hours
        }
        for source in config.OFFICIAL_SOURCES
    ]

@app.get("/audit/latest")
async def get_latest_audit():
    """Obtiene log de auditoría más reciente"""
    # En producción: consultar base de datos
    return {
        "message": "Audit logs stored separately for security",
        "config_version": SystemConfig().VERSION
    }

# Para ejecutar: uvicorn api.main:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
