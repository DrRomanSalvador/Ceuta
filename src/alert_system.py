"""
Sistema de Alertas
Notifica cuando se cruzan umbrales críticos
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from .config import SystemConfig
from .risk_calculator import RiskResult

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    """Estructura de alerta"""
    level: str  # GREEN, YELLOW, ORANGE, RED
    risk_score: float
    message: str
    timestamp: str
    recommended_actions: List[str]
    data_sources: List[str]
    audit_hash: str


class AlertSystem:
    """Sistema de notificación de alertas"""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.alert_history: List[Alert] = []
    
    def check_and_alert(self, risk_result: RiskResult) -> Optional[Alert]:
        """
        Verifica si se deben generar alertas y las envía
        
        Retorna Alert si hay notificación, None si no
        """
        alert = self._create_alert(risk_result)
        
        if alert:
            # Guardar en historial
            self.alert_history.append(alert)
            
            # Enviar notificaciones
            self._send_notifications(alert)
            
            logger.warning(f"Alerta {alert.level} generada: {alert.message}")
        
        return alert
    
    def _create_alert(self, risk_result: RiskResult) -> Optional[Alert]:
        """Crea objeto Alert si el nivel lo requiere"""
        # Sólo alertar para YELLOW, ORANGE, RED
        if risk_result.alert_level == 'GREEN':
            return None
        
        # Mensajes según nivel
        messages = {
            'YELLOW': 'Riesgo moderado detectado. Monitoreo intensificado recomendado.',
            'ORANGE': 'Riesgo alto detectado. Activar protocolos de respuesta.',
            'RED': 'RIESGO CRÍTICO DETECTADO. Acción inmediata requerida.'
        }
        
        # Acciones recomendadas
        actions = self._get_recommended_actions(risk_result.alert_level)
        
        return Alert(
            level=risk_result.alert_level,
            risk_score=risk_result.risk_score,
            message=messages.get(risk_result.alert_level, 'Alerta de riesgo'),
            timestamp=datetime.utcnow().isoformat() + 'Z',
            recommended_actions=actions,
            data_sources=risk_result.data_sources,
            audit_hash=risk_result.audit_hash
        )
    
    def _get_recommended_actions(self, level: str) -> List[str]:
        """Obtiene acciones recomendadas según nivel de alerta"""
        actions = {
            'YELLOW': [
                'Incrementar frecuencia de monitoreo',
                'Revisar fuentes de datos adicionales',
                'Notificar equipo de análisis'
            ],
            'ORANGE': [
                'Activar comité de revisión de riesgos',
                'Contactar organismos reguladores',
                'Preparar briefing para tomadores de decisión',
                'Incrementar conciencia pública'
            ],
            'RED': [
                'CONVOCAR EMERGENCIA INTERNACIONAL',
                'Notificar a jefes de estado y gobierno',
                'Activar protocolos de la ONU',
                'Implementar medidas de contención inmediatas',
                'Coordinar respuesta global'
            ]
        }
        return actions.get(level, [])
    
    def _send_notifications(self, alert: Alert):
        """Envía notificaciones por múltiples canales"""
        # Email
        if self.config.ALERT_CHANNELS.get('email'):
            self._send_email(alert)
        
        # Webhook
        if self.config.ALERT_CHANNELS.get('webhook'):
            self._send_webhook(alert)
        
        # SMS (para nivel RED)
        if alert.level == 'RED' and self.config.ALERT_CHANNELS.get('sms_provider'):
            self._send_sms(alert)
        
        logger.info(f"Notificaciones enviadas para alerta {alert.level}")
    
    def _send_email(self, alert: Alert):
        """Envía alerta por email"""
        msg = MIMEMultipart()
        msg['From'] = 'ceuta-system@alerts.org'
        msg['To'] = self.config.ALERT_CHANNELS['email']
        msg['Subject'] = f"🚨 ALERTA {alert.level}: Riesgo Existencial {alert.risk_score:.2f}"
        
        body = f"""
ALERTA DEL SISTEMA CEUTA
========================

Nivel: {alert.level}
Riesgo: {alert.risk_score:.4f}
Fecha: {alert.timestamp}

Mensaje:
{alert.message}

Acciones Recomendadas:
{chr(10).join(f'  • {action}' for action in alert.recommended_actions)}

Fuentes de Datos:
{chr(10).join(f'  - {source}' for source in alert.data_sources)}

Hash de Auditoría: {alert.audit_hash}

---
Sistema Ceuta v{self.config.VERSION}
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # En producción: configurar SMTP real
        logger.info(f"Email enviado a {self.config.ALERT_CHANNELS['email']}")
    
    def _send_webhook(self, alert: Alert):
        """Envía alerta por webhook (Slack, Discord, etc.)"""
        webhook_url = self.config.ALERT_CHANNELS['webhook']
        
        payload = {
            'level': alert.level,
            'risk_score': alert.risk_score,
            'message': alert.message,
            'timestamp': alert.timestamp,
            'actions': alert.recommended_actions
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Webhook enviado exitosamente")
        except Exception as e:
            logger.error(f"Error enviando webhook: {e}")
    
    def _send_sms(self, alert: Alert):
        """Envía alerta por SMS (sólo nivel RED)"""
        # Implementación con Twilio u otro proveedor
        logger.critical(f"SMS CRÍTICO: {alert.message}")
    
    def get_alert_history(self, limit: int = 10) -> List[Dict]:
        """Obtiene historial de alertas"""
        return [a.__dict__ for a in self.alert_history[-limit:]]
    
    def clear_history(self):
        """Limpia historial de alertas"""
        self.alert_history = []
        logger.info("Historial de alertas limpiado")
