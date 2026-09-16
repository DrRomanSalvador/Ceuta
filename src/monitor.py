"""
Monitor Principal del Sistema CEUTA
Orquesta todos los componentes
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import schedule
import time

from .config import SystemConfig
from .data_fetcher import DataFetcher
from .risk_calculator import RiskCalculator
from .alert_system import AlertSystem
from .risk_calculator import RiskResult
from .response_coupling import ResponseBinding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CeutaMonitor:
    """
    Sistema de monitorización continua de riesgo existencial
    
    Flujo:
    1. Obtener datos de fuentes oficiales
    2. Calcular riesgo con fórmulas auditables
    3. Generar alertas si corresponde
    4. Almacenar resultados para auditoría
    5. Repetir en intervalo configurado
    """
    
    def __init__(self, config: SystemConfig = None, response_sink=None):
        self.config = config or SystemConfig()
        self.data_fetcher = DataFetcher(self.config)
        self.risk_calculator = RiskCalculator(self.config)
        self.alert_system = AlertSystem(self.config, response_sink=response_sink)
        
        self.last_risk_result: Optional[RiskResult] = None
        self.is_running = False
    
    def run_once(self) -> RiskResult:
        """
        Ejecuta un ciclo completo de monitorización
        
        Retorna: RiskResult con el cálculo actual
        """
        logger.info("Iniciando ciclo de monitorización...")
        
        # 1. Obtener datos
        verified_data = self.data_fetcher.fetch_all_sources()
        if not verified_data:
            logger.warning("No se obtuvieron datos de ninguna fuente")
            # Usar datos previos si existen
            if self.last_risk_result:
                return self.last_risk_result
        
        # 2. Calcular riesgo
        risk_result = self.risk_calculator.calculate_risk(verified_data)
        self.last_risk_result = risk_result
        
        # 3. Verificar alertas
        alert = self.alert_system.check_and_alert(risk_result)
        if alert:
            logger.warning(f"Alerta generada: {alert.level}")
        
        # 4. Log para auditoría
        if self.config.ENABLE_AUDIT:
            self._log_for_audit(risk_result, verified_data)
        
        logger.info(f"Ciclo completado. Riesgo: {risk_result.risk_score:.4f} ({risk_result.alert_level})")
        return risk_result

    def record_alert_response(self, alert, binding: ResponseBinding, *, actor: str, timestamp: str) -> dict:
        """Bind a real response to an emitted alert using explicit identities."""
        return self.alert_system.record_response(alert, binding, actor=actor, timestamp=timestamp)
    
    def start_continuous(self, interval_hours: int = 6):
        """
        Inicia monitorización continua
        
        interval_hours: Frecuencia de ejecución (default: 6 horas)
        """
        logger.info(f"Iniciando monitorización continua (intervalo: {interval_hours}h)")
        self.is_running = True
        
        # Programar ejecuciones
        schedule.every(interval_hours).hours.do(self.run_once)
        
        # Ejecutar inmediatamente
        self.run_once()
        
        # Loop principal
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Chequear cada minuto
    
    def stop(self):
        """Detiene monitorización continua"""
        self.is_running = False
        logger.info("Monitorización detenida")
    
    def _log_for_audit(self, risk_result: RiskResult, verified_data):
        """Registra información para auditoría"""
        if not self.config.ENABLE_AUDIT:
            return
        
        import json
        audit_log = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'risk_result': risk_result.to_dict(),
            'data_sources': [d.to_dict() for d in verified_data],
            'config_version': self.config.VERSION
        }
        
        # En producción: escribir a archivo o base de datos
        logger.info(f"Audit log: {json.dumps(audit_log, indent=2)}")
    
    def get_current_status(self) -> dict:
        """Obtiene estado actual del sistema"""
        return {
            'is_running': self.is_running,
            'last_risk': self.last_risk_result.to_dict() if self.last_risk_result else None,
            'alert_history': self.alert_system.get_alert_history(5),
            'config_version': self.config.VERSION,
            'last_update': self.config.LAST_UPDATE
        }


# Función principal para ejecutar como script
def main():
    """Ejecuta el monitor en modo continuo"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema Ceuta - Monitor de Riesgo Existencial')
    parser.add_argument('--once', action='store_true', help='Ejecutar una vez y salir')
    parser.add_argument('--interval', type=int, default=6, help='Intervalo en horas (default: 6)')
    args = parser.parse_args()
    
    monitor = CeutaMonitor()
    
    if args.once:
        result = monitor.run_once()
        print(f"\n{'='*60}")
        print(f"RESULTADO: {result.risk_score:.4f} ({result.alert_level})")
        print(f"Intervalo 95%: [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]")
        print(f"Fuentes: {len(result.data_sources)}")
        print(f"Hash auditoría: {result.audit_hash}")
        print(f"{'='*60}\n")
    else:
        try:
            monitor.start_continuous(args.interval)
        except KeyboardInterrupt:
            monitor.stop()
            print("\nMonitor detenido por usuario")


if __name__ == '__main__':
    main()
