"""Governed alert generation and explicit response coupling."""

import logging
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import requests

from .config import SystemConfig
from .response_coupling import ResponseBinding, ResponseCouplingSink
from .risk_calculator import RiskResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AlertGovernance:
    """Operational gate for external alert delivery.

    Alert creation is separated from public/external notification. External
    delivery is disabled unless the declared governance, response capacity,
    appeal, anti-stigmatisation and simulation controls are all satisfied.
    """

    false_positive_cost: float
    false_negative_cost: float
    minimum_persistence_seconds: int = 0
    expiry_seconds: int = 3600
    response_capacity_confirmed: bool = False
    governance_approved: bool = False
    appeal_mechanism: bool = False
    anti_stigma_reviewed: bool = False
    simulation_completed: bool = False

    def __post_init__(self) -> None:
        if self.false_positive_cost < 0 or self.false_negative_cost < 0:
            raise ValueError("alert loss costs cannot be negative")
        if self.minimum_persistence_seconds < 0:
            raise ValueError("minimum persistence cannot be negative")
        if self.expiry_seconds <= 0:
            raise ValueError("expiry_seconds must be positive")

    @property
    def externally_notifiable(self) -> bool:
        return all(
            (
                self.response_capacity_confirmed,
                self.governance_approved,
                self.appeal_mechanism,
                self.anti_stigma_reviewed,
                self.simulation_completed,
            )
        )


@dataclass
class Alert:
    """Structure of a generated alert."""

    level: str
    risk_score: float
    message: str
    timestamp: str
    recommended_actions: List[str]
    data_sources: List[str]
    audit_hash: str
    governance_ready: bool = False


class AlertSystem:
    """Alert generator with a fail-closed external-notification boundary."""

    def __init__(
        self,
        config: SystemConfig = None,
        response_sink: ResponseCouplingSink = None,
        governance: AlertGovernance | None = None,
    ):
        self.config = config or SystemConfig()
        self.alert_history: List[Alert] = []
        self.response_sink = response_sink
        self.governance = governance or AlertGovernance(
            false_positive_cost=1.0,
            false_negative_cost=1.0,
        )

    def check_and_alert(self, risk_result: RiskResult) -> Optional[Alert]:
        """Generate an alert; deliver externally only when governance permits it."""
        alert = self._create_alert(risk_result)
        if alert:
            self.alert_history.append(alert)
            if self.governance.externally_notifiable:
                self._send_notifications(alert)
            else:
                logger.warning(
                    "Alert %s generated but external notification is blocked by governance",
                    alert.level,
                )
        return alert

    def record_response(self, alert: Alert, binding: ResponseBinding, *, actor: str, timestamp: str) -> dict:
        """Persist an explicitly identified real response linked to an alert."""
        if self.response_sink is None:
            raise RuntimeError("Response coupling sink is not configured")
        if alert not in self.alert_history:
            raise ValueError("Alert is not owned by this AlertSystem instance")
        return self.response_sink.record(alert, binding, actor=actor, timestamp=timestamp)

    def _create_alert(self, risk_result: RiskResult) -> Optional[Alert]:
        if risk_result.alert_level == "GREEN":
            return None

        messages = {
            "YELLOW": "Riesgo moderado detectado. Monitoreo intensificado recomendado.",
            "ORANGE": "Riesgo alto detectado. Activar revisión humana del riesgo.",
            "RED": "Riesgo crítico detectado. Revisión humana inmediata requerida.",
        }
        actions = self._get_recommended_actions(risk_result.alert_level)
        return Alert(
            level=risk_result.alert_level,
            risk_score=risk_result.risk_score,
            message=messages.get(risk_result.alert_level, "Alerta de riesgo"),
            timestamp=datetime.utcnow().isoformat() + "Z",
            recommended_actions=actions,
            data_sources=risk_result.data_sources,
            audit_hash=risk_result.audit_hash,
            governance_ready=self.governance.externally_notifiable,
        )

    def _get_recommended_actions(self, level: str) -> List[str]:
        """Return bounded, review-oriented actions rather than autonomous coercion."""
        actions = {
            "YELLOW": [
                "Incrementar frecuencia de monitoreo",
                "Revisar fuentes de datos adicionales",
                "Notificar equipo de análisis para revisión humana",
            ],
            "ORANGE": [
                "Activar revisión humana del riesgo",
                "Contactar organismos responsables según competencia",
                "Preparar briefing para tomadores de decisión",
            ],
            "RED": [
                "Convocar revisión de emergencia por la autoridad competente",
                "Verificar fuentes y proceso de observación",
                "Evaluar opciones reversibles y capacidad disponible",
            ],
        }
        return actions.get(level, [])

    def _send_notifications(self, alert: Alert):
        if self.config.ALERT_CHANNELS.get("email"):
            self._send_email(alert)
        if self.config.ALERT_CHANNELS.get("webhook"):
            self._send_webhook(alert)
        if alert.level == "RED" and self.config.ALERT_CHANNELS.get("sms_provider"):
            self._send_sms(alert)
        logger.info("Notificaciones enviadas para alerta %s", alert.level)

    def _send_email(self, alert: Alert):
        msg = MIMEMultipart()
        msg["From"] = "ceuta-system@alerts.org"
        msg["To"] = self.config.ALERT_CHANNELS["email"]
        msg["Subject"] = f"ALERTA {alert.level}: Riesgo Existencial {alert.risk_score:.2f}"
        body = f"""
ALERTA DEL SISTEMA CEUTA
========================

Nivel: {alert.level}
Riesgo: {alert.risk_score:.4f}
Fecha: {alert.timestamp}

Mensaje:
{alert.message}

Acciones Recomendadas:
{chr(10).join(f'  - {action}' for action in alert.recommended_actions)}

Fuentes de Datos:
{chr(10).join(f'  - {source}' for source in alert.data_sources)}

Hash de Auditoría: {alert.audit_hash}

---
Sistema Ceuta v{self.config.VERSION}
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))
        logger.info("Email preparado para %s", self.config.ALERT_CHANNELS["email"])

    def _send_webhook(self, alert: Alert):
        webhook_url = self.config.ALERT_CHANNELS["webhook"]
        payload = {
            "level": alert.level,
            "risk_score": alert.risk_score,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "actions": alert.recommended_actions,
        }
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Webhook enviado exitosamente")
        except Exception as exc:
            logger.error("Error enviando webhook: %s", exc)

    def _send_sms(self, alert: Alert):
        logger.critical("SMS crítico: %s", alert.message)

    def get_alert_history(self, limit: int = 10) -> List[Dict]:
        return [a.__dict__ for a in self.alert_history[-limit:]]

    def clear_history(self):
        self.alert_history = []
        logger.info("Historial de alertas limpiado")
