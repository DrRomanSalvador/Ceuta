"""
Calculadora de Riesgo Existencial
Fórmulas matemáticas trazables con intervalos de confianza
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

from .config import SystemConfig, ThresholdConfig
from .data_fetcher import VerifiedData

logger = logging.getLogger(__name__)

@dataclass
class RiskResult:
    """Resultado del cálculo de riesgo con incertidumbre"""
    risk_score: float  # 0-1
    confidence_interval: Tuple[float, float]  # 95% CI
    confidence_level: float  # 0.95
    standard_error: float
    sample_size: int
    component_scores: Dict[str, float]
    alert_level: str  # GREEN, YELLOW, ORANGE, RED
    calculation_timestamp: str
    data_sources: List[str]
    audit_hash: str
    
    def to_dict(self) -> Dict:
        return {
            'risk_score': self.risk_score,
            'confidence_interval': self.confidence_interval,
            'confidence_level': self.confidence_level,
            'standard_error': self.standard_error,
            'sample_size': self.sample_size,
            'component_scores': self.component_scores,
            'alert_level': self.alert_level,
            'calculation_timestamp': self.calculation_timestamp,
            'data_sources': self.data_sources,
            'audit_hash': self.audit_hash
        }


class RiskCalculator:
    """
    Calcula riesgo existencial usando fórmulas matemáticas auditables
    
    Fórmula base:
    R = sigmoid(sum(w_i * x_i))
    
    Donde:
    - w_i: pesos del modelo (públicos, auditados)
    - x_i: indicadores normalizados (0-1)
    - sigmoid: función logística para mapear a (0,1)
    """
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.thresholds = self.config.THRESHOLDS
    
    def calculate_risk(self, verified_data: List[VerifiedData]) -> RiskResult:
        """
        Calcula riesgo existencial a partir de datos verificados
        
        Pasos:
        1. Extraer indicadores de los datos
        2. Normalizar indicadores (0-1)
        3. Aplicar pesos del modelo
        4. Calcular score compuesto
        5. Aplicar función sigmoide
        6. Calcular intervalo de confianza
        7. Determinar nivel de alerta
        """
        
        # 1. Extraer indicadores
        indicators = self._extract_indicators(verified_data)
        
        # 2. Normalizar
        normalized = self._normalize_indicators(indicators)
        
        # 3-4. Aplicar pesos y calcular score
        raw_score = self._calculate_raw_score(normalized)
        
        # 5. Función sigmoide
        risk_score = self._sigmoid(raw_score)
        
        # 6. Intervalo de confianza
        ci_low, ci_high, se = self._calculate_confidence_interval(risk_score, len(verified_data))
        
        # 7. Nivel de alerta
        alert_level = self._determine_alert_level(risk_score)
        
        # Component scores para auditoría
        component_scores = {
            'capability_growth': normalized.get('capability_growth', 0.5),
            'incident_count': normalized.get('incident_count', 0.5),
            'governance_gap': normalized.get('governance_gap', 0.5),
            'awareness_level': normalized.get('awareness_level', 0.5),
            'international_cooperation': normalized.get('international_cooperation', 0.5)
        }
        
        # Hash de auditoría
        import hashlib
        audit_content = f"{risk_score}{ci_low}{ci_high}{self._dict_to_str(component_scores)}"
        audit_hash = hashlib.sha256(audit_content.encode()).hexdigest()[:16]
        
        from datetime import datetime
        result = RiskResult(
            risk_score=round(risk_score, 4),
            confidence_interval=(round(ci_low, 4), round(ci_high, 4)),
            confidence_level=self.config.CONFIDENCE_LEVEL,
            standard_error=round(se, 4),
            sample_size=len(verified_data),
            component_scores=component_scores,
            alert_level=alert_level,
            calculation_timestamp=datetime.utcnow().isoformat() + 'Z',
            data_sources=[d.source for d in verified_data],
            audit_hash=audit_hash
        )
        
        logger.info(f"Riesgo calculado: {result.risk_score:.4f} (nivel: {result.alert_level})")
        return result
    
    def _extract_indicators(self, verified_data: List[VerifiedData]) -> Dict[str, float]:
        """
        Extrae indicadores de los datos verificados
        
        En producción: lógica específica para cada fuente de datos
        Aquí: implementación de ejemplo con datos simulados verificables
        """
        
        # Indicadores base (valores por defecto si no hay datos)
        indicators = {
            'capability_growth': 0.5,  # Crecimiento de capacidades de IA
            'incident_count': 0.3,     # Incidentes de seguridad reportados
            'governance_gap': 0.6,     # Brecha de gobernanza
            'awareness_level': 0.4,    # Nivel de conciencia pública
            'international_cooperation': 0.3  # Cooperación internacional
        }
        
        # Actualizar con datos reales cuando estén disponibles
        for data in verified_data:
            # Ejemplo: si hay datos de incidentes de UN
            if 'UN' in data.source and isinstance(data.value, dict):
                if 'incidents' in data.value:
                    indicators['incident_count'] = min(data.value['incidents'] / 10.0, 1.0)
            
            # Ejemplo: si hay datos de cooperación internacional
            if 'Reuters' in data.source:
                # Analizar tono de noticias sobre cooperación
                indicators['international_cooperation'] = 0.5  # Placeholder
        
        return indicators
    
    def _normalize_indicators(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """
        Normaliza indicadores al rango (0, 1)
        
        Métodos de normalización deben ser documentados y auditables
        """
        normalized = {}
        
        for key, value in indicators.items():
            # Normalización min-max (asumiendo rango conocido)
            # En producción: usar estadísticas históricas reales
            min_val = 0.0
            max_val = 1.0
            
            if max_val == min_val:
                normalized[key] = 0.5
            else:
                normalized[key] = (value - min_val) / (max_val - min_val)
                normalized[key] = max(0.0, min(1.0, normalized[key]))
        
        return normalized
    
    def _calculate_raw_score(self, normalized: Dict[str, float]) -> float:
        """
        Calcula score bruto como combinación lineal ponderada
        
        Score = sum(w_i * x_i)
        
        Los pesos están definidos en config.py y deben ser auditados públicamente
        """
        weights = self.config.MODEL_WEIGHTS
        
        raw_score = 0.0
        for indicator, weight in weights.items():
            value = normalized.get(indicator, 0.5)
            raw_score += weight * value
        
        return raw_score
    
    def _sigmoid(self, x: float) -> float:
        """Función sigmoide para mapear score a (0, 1)"""
        return 1.0 / (1.0 + np.exp(-x))
    
    def _calculate_confidence_interval(self, risk_score: float, n: int) -> Tuple[float, float, float]:
        """
        Calcula intervalo de confianza del 95%
        
        Fórmula:
        SE = sqrt(p * (1-p) / n)
        CI = [p - z*SE, p + z*SE]
        
        Donde:
        - p: risk_score
        - n: tamaño de muestra (número de fuentes de datos)
        - z: z-score para nivel de confianza (1.96 para 95%)
        """
        if n < 2:
            # Muestra muy pequeña: incertidumbre máxima
            return (0.0, 1.0, 0.5)
        
        # Error estándar
        se = np.sqrt(risk_score * (1 - risk_score) / n)
        
        # Intervalo de confianza
        z = self.config.Z_SCORE
        ci_low = max(0.0, risk_score - z * se)
        ci_high = min(1.0, risk_score + z * se)
        
        return ci_low, ci_high, se
    
    def _determine_alert_level(self, risk_score: float) -> str:
        """Determina nivel de alerta basado en umbrales configurados"""
        if risk_score < self.thresholds.green_max:
            return 'GREEN'
        elif risk_score < self.thresholds.yellow_max:
            return 'YELLOW'
        elif risk_score < self.thresholds.orange_max:
            return 'ORANGE'
        else:
            return 'RED'
    
    def _dict_to_str(self, d: Dict) -> str:
        """Convierte diccionario a string para hashing"""
        return ','.join(f"{k}:{v}" for k, v in sorted(d.items()))
