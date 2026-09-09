"""
Módulo de obtención de datos de fuentes oficiales
TODOS los datos deben tener: fuente, fecha, método de obtención
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import logging

from .config import DataSource, SystemConfig

logger = logging.getLogger(__name__)

@dataclass
class VerifiedData:
    """Estructura de dato verificado"""
    value: Any
    source: str
    source_url: str
    fetch_date: str  # ISO 8601
    data_date: str  # Fecha del dato (puede diferir de fetch_date)
    method: str
    confidence: float  # 0-1
    audit_hash: str  # Hash para verificación de integridad
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def validate(self) -> bool:
        """Valida que el dato tenga toda la metadata requerida"""
        required_fields = ['source', 'source_url', 'fetch_date', 'data_date', 'method']
        return all(getattr(self, field) for field in required_fields)


class DataFetcher:
    """Obtiene datos de fuentes oficiales con trazabilidad completa"""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Ceuta-System/1.0 (Auditable AI Safety Monitor)',
            'Accept': 'application/json'
        })
    
    def fetch_from_source(self, source: DataSource) -> Optional[VerifiedData]:
        """
        Obtiene datos de una fuente oficial
        Retorna None si hay errores de validación
        """
        try:
            # Intentar API primero
            if source.api_endpoint:
                data = self._fetch_api(source)
            else:
                data = self._fetch_web(source)
            
            if data is None:
                logger.warning(f"No se pudieron obtener datos de {source.name}")
                return None
            
            # Crear objeto verificado
            verified = VerifiedData(
                value=data,
                source=source.name,
                source_url=source.url,
                fetch_date=datetime.utcnow().isoformat() + 'Z',
                data_date=datetime.utcnow().date().isoformat(),
                method='API' if source.api_endpoint else 'Web Scraping',
                confidence=self._calculate_confidence(source, data),
                audit_hash=self._generate_audit_hash(source, data)
            )
            
            # Validar antes de retornar
            if not verified.validate():
                logger.error(f"Dato no válido de {source.name}: falta metadata")
                return None
            
            logger.info(f"Datos obtenidos de {source.name} (confianza: {verified.confidence:.2f})")
            return verified
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de {source.name}: {str(e)}")
            return None
    
    def _fetch_api(self, source: DataSource) -> Optional[Dict]:
        """Obtiene datos vía API"""
        try:
            response = self.session.get(source.api_endpoint, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"API falló para {source.name}: {e}")
            return None
    
    def _fetch_web(self, source: DataSource) -> Optional[Dict]:
        """
        Obtiene datos vía scraping web (sólo para fuentes oficiales)
        En producción, usar APIs oficiales cuando sea posible
        """
        # Implementación simplificada para demo
        # En producción: usar BeautifulSoup, Scrapy, etc.
        logger.info(f"Web scraping de {source.url} (simulado)")
        return {'status': 'fetched', 'url': source.url}
    
    def _calculate_confidence(self, source: DataSource, data: Any) -> float:
        """
        Calcula nivel de confianza del dato
        Factores: fuente oficial, actualización reciente, consistencia
        """
        confidence = 0.5  # Base
        
        # Fuente oficial: +0.3
        if any(official in source.name.lower() for official in ['un', 'government', 'official']):
            confidence += 0.3
        
        # Actualización reciente: +0.2
        last_verified = datetime.fromisoformat(source.last_verified.replace('Z', '+00:00'))
        days_old = (datetime.utcnow() - last_verified).days
        if days_old < 7:
            confidence += 0.2
        elif days_old < 30:
            confidence += 0.1
        
        # Datos presentes: +0.1
        if data and len(str(data)) > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_audit_hash(self, source: DataSource, data: Any) -> str:
        """Genera hash para auditoría de integridad"""
        import hashlib
        content = f"{source.name}{source.url}{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def fetch_all_sources(self) -> List[VerifiedData]:
        """Obtiene datos de todas las fuentes configuradas"""
        verified_data = []
        
        for source in self.config.OFFICIAL_SOURCES:
            logger.info(f"Obteniendo datos de {source.name}...")
            data = self.fetch_from_source(source)
            if data:
                verified_data.append(data)
        
        logger.info(f"Datos obtenidos de {len(verified_data)}/{len(self.config.OFFICIAL_SOURCES)} fuentes")
        return verified_data
    
    def get_latest_data(self, source_name: str) -> Optional[VerifiedData]:
        """Obtiene el dato más reciente de una fuente específica"""
        # En producción: consultar base de datos o caché Redis
        sources = [s for s in self.config.OFFICIAL_SOURCES if s.name == source_name]
        if sources:
            return self.fetch_from_source(sources[0])
        return None
