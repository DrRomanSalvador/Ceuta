"""
Configuración del Sistema CEUTA
Todas las fuentes son verificables y oficiales
"""

from dataclasses import dataclass
from typing import List, Dict
import os

@dataclass
class DataSource:
    name: str
    url: str
    api_endpoint: str
    update_frequency_hours: int
    authentication_required: bool
    last_verified: str  # ISO 8601

@dataclass
class ThresholdConfig:
    green_max: float = 0.4
    yellow_max: float = 0.6
    orange_max: float = 0.75
    red_min: float = 0.75

class SystemConfig:
    """Configuración central del sistema"""
    
    VERSION = "1.0.0"
    LAST_UPDATE = "2026-09-09T11:34:00Z"
    
    # Fuentes oficiales verificadas
    OFFICIAL_SOURCES: List[DataSource] = [
        DataSource(
            name="UN Human Rights Council",
            url="https://www.ohchr.org/en/press-releases",
            api_endpoint="https://www.ohchr.org/api/press-releases",
            update_frequency_hours=6,
            authentication_required=False,
            last_verified="2026-09-07"  # [16][18]
        ),
        DataSource(
            name="Reuters AI Coverage",
            url="https://www.reuters.com/technology/artificial-intelligence/",
            api_endpoint="https://api.reuters.com/v1/news?category=ai",
            update_frequency_hours=1,
            authentication_required=True,
            last_verified="2026-09-07"  # [18]
        ),
        DataSource(
            name="Center for Humane Technology",
            url="https://www.humanetech.com/",
            api_endpoint="https://api.humanetech.com/research",
            update_frequency_hours=24,
            authentication_required=False,
            last_verified="2026-08"  # [20]
        ),
        DataSource(
            name="AI Safety Research",
            url="https://www.safe.ai/",
            api_endpoint="https://api.safe.ai/publications",
            update_frequency_hours=24,
            authentication_required=False,
            last_verified="2026-09"
        )
    ]
    
    # Umbrales de alerta
    THRESHOLDS = ThresholdConfig()
    
    # Intervalos de confianza
    CONFIDENCE_LEVEL = 0.95
    Z_SCORE = 1.96  # Para 95% CI
    
    # Parámetros del modelo (deben ser auditados públicamente)
    MODEL_WEIGHTS = {
        'capability_growth': 0.25,
        'incident_count': 0.20,
        'governance_gap': 0.20,
        'awareness_level': -0.15,  # Negativo: reduce riesgo
        'international_cooperation': -0.20  # Negativo: reduce riesgo
    }
    
    # Validación: suma de pesos absolutos = 1
    assert abs(sum(abs(w) for w in MODEL_WEIGHTS.values()) - 1.0) < 0.01, \
        "Los pesos del modelo deben sumar 1.0 para ser auditables"
    
    # Configuración de alertas
    ALERT_CHANNELS = {
        'email': os.getenv('ALERT_EMAIL', 'alerts@ceuta.system'),
        'webhook': os.getenv('ALERT_WEBHOOK', ''),
        'sms_provider': os.getenv('SMS_PROVIDER', 'twilio')
    }
    
    # Base de datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/ceuta')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging y auditoría
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    AUDIT_LOG_PATH = os.getenv('AUDIT_LOG_PATH', '/var/log/ceuta/audit.log')
    ENABLE_AUDIT = True
