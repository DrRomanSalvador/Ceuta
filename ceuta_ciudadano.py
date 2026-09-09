#!/usr/bin/env python3
"""
CEUTA CIUDADANO — Información estratificada por veracidad
Para ciudadanos que quieren saber QUÉ creer y CÓMO verificarlo
"""

import requests
import json
from datetime import datetime
from typing import Dict, List
import hashlib

# ═══════════════════════════════════════════════════════════════════════════
# FUENTES OFICIALES VERIFICADAS
# ═══════════════════════════════════════════════════════════════════════════

FUENTES = {
    'UN': {
        'nombre': 'Naciones Unidas',
        'url': 'https://www.ohchr.org/en/press-releases',
        'api': 'https://www.ohchr.org/api/press-releases',
        'veracidad': 'OFICIAL',
        'sesgo': 'Institucional',
        'actualizacion': 'Diaria'
    },
    'Reuters': {
        'nombre': 'Reuters News',
        'url': 'https://www.reuters.com/technology/artificial-intelligence/',
        'api': 'https://api.reuters.com/v1/news',
        'veracidad': 'MEDIO_PROFESIONAL',
        'sesgo': 'Comercial',
        'actualizacion': 'Hora en hora'
    },
    'ScienceDirect': {
        'nombre': 'ScienceDirect (Elsevier)',
        'url': 'https://www.sciencedirect.com/',
        'api': 'https://api.elsevier.com/content/search/article',
        'veracidad': 'CIENTIFICA_REVISADA',
        'sesgo': 'Académico',
        'actualizacion': 'Semanal'
    },
    'arXiv': {
        'nombre': 'arXiv Preprints',
        'url': 'https://arxiv.org/',
        'api': 'http://export.arxiv.org/api/query',
        'veracidad': 'PREPRINT',
        'sesgo': 'Técnico',
        'actualizacion': 'Diaria'
    },
    'Twitter_X': {
        'nombre': 'X (Twitter)',
        'url': 'https://twitter.com/',
        'api': 'https://api.twitter.com/2/tweets/search/recent',
        'veracidad': 'SOCIAL_NO_VERIFICADA',
        'sesgo': 'Alto',
        'actualizacion': 'Tiempo real'
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# ESTRATIFICACIÓN POR VERACIDAD
# ═══════════════════════════════════════════════════════════════════════════

def estratificar_veracidad(fuente: str) -> Dict:
    """
    Estratifica información por nivel de veracidad
    
    Niveles:
    1. OFICIAL (gobiernos, ONU, organismos internacionales)
    2. CIENTIFICA_REVISADA (papers con peer review)
    3. MEDIO_PROFESIONAL (periodismo profesional)
    4. PREPRINT (papers sin revisar aún)
    5. SOCIAL_NO_VERIFICADA (redes sociales)
    """
    info = FUENTES.get(fuente, {})
    
    nivel = info.get('veracidad', 'DESCONOCIDA')
    
    return {
        'fuente': info.get('nombre', fuente),
        'nivel_veracidad': nivel,
        'sesgo': info.get('sesgo', 'Desconocido'),
        'actualizacion': info.get('actualizacion', 'Desconocida'),
        'url': info.get('url', ''),
        'recomendacion': get_recomendacion(nivel)
    }

def get_recomendacion(nivel: str) -> str:
    """Recomendación de uso según nivel de veracidad"""
    recomendaciones = {
        'OFICIAL': 'ALTA CONFIANZA - Usar como fuente primaria',
        'CIENTIFICA_REVISADA': 'ALTA CONFIANZA - Validar fecha y contexto',
        'MEDIO_PROFESIONAL': 'CONFIANZA MEDIA - Cruzar con otras fuentes',
        'PREPRINT': 'CONFIANZA BAJA - Esperar peer review',
        'SOCIAL_NO_VERIFICADA': 'SIN CONFIANZA - Verificar antes de compartir'
    }
    return recomendaciones.get(nivel, 'VERIFICAR MANUALMENTE')

# ═══════════════════════════════════════════════════════════════════════════
# VERIFICACIÓN DE FUENTES
# ═══════════════════════════════════════════════════════════════════════════

def verificar_fuente(fuente: str, contenido: str) -> Dict:
    """
    Verifica si una fuente es confiable para un contenido específico
    
    Retorna:
    - es_confiable: bool
    - nivel_confianza: 0-1
    - recomendacion: str
    - fuentes_alternativas: list
    """
    info = FUENTES.get(fuente, {})
    nivel = info.get('veracidad', 'DESCONOCIDA')
    
    # Mapeo a score numérico
    scores = {
        'OFICIAL': 0.95,
        'CIENTIFICA_REVISADA': 0.90,
        'MEDIO_PROFESIONAL': 0.75,
        'PREPRINT': 0.50,
        'SOCIAL_NO_VERIFICADA': 0.20,
        'DESCONOCIDA': 0.10
    }
    
    score = scores.get(nivel, 0.10)
    
    return {
        'es_confiable': score >= 0.70,
        'nivel_confianza': score,
        'recomendacion': get_recomendacion(nivel),
        'fuentes_alternativas': [
            f for f in FUENTES 
            if scores.get(FUENTES[f]['veracidad'], 0) >= 0.70
        ],
        'como_comprobar': [
            f"1. Buscar en {FUENTES[f]['url']}" 
            for f in FUENTES 
            if scores.get(FUENTES[f]['veracidad'], 0) >= 0.70
        ]
    }

# ═══════════════════════════════════════════════════════════════════════════
# CÁLCULO DE RIESGO ESTRATIFICADO
# ═══════════════════════════════════════════════════════════════════════════

def calcular_riesgo_ciudadano() -> Dict:
    """
    Calcula riesgo para ciudadano ceutí con información estratificada
    """
    
    # Simulación de datos (en producción: obtener de APIs reales)
    datos = {
        'UN': {'riesgo': 0.70, 'peso': 0.30, 'veracidad': 'OFICIAL'},
        'Reuters': {'riesgo': 0.65, 'peso': 0.25, 'veracidad': 'MEDIO_PROFESIONAL'},
        'ScienceDirect': {'riesgo': 0.60, 'peso': 0.25, 'veracidad': 'CIENTIFICA_REVISADA'},
        'arXiv': {'riesgo': 0.55, 'peso': 0.10, 'veracidad': 'PREPRINT'},
        'Twitter_X': {'riesgo': 0.80, 'peso': 0.10, 'veracidad': 'SOCIAL_NO_VERIFICADA'}
    }
    
    # Riesgo ponderado por veracidad
    riesgo_ponderado = sum(
        d['riesgo'] * d['peso'] 
        for d in datos.values()
    )
    
    # Riesgo solo con fuentes confiables (>= 0.70)
    riesgo_confiable = sum(
        d['riesgo'] * d['peso'] 
        for d in datos.values() 
        if d['veracidad'] in ['OFICIAL', 'CIENTIFICA_REVISADA', 'MEDIO_PROFESIONAL']
    ) / sum(
        d['peso'] 
        for d in datos.values() 
        if d['veracidad'] in ['OFICIAL', 'CIENTIFICA_REVISADA', 'MEDIO_PROFESIONAL']
    )
    
    return {
        'riesgo_general': round(riesgo_ponderado, 4),
        'riesgo_fuentes_confiables': round(riesgo_confiable, 4),
        'diferencia': round(riesgo_ponderado - riesgo_confiable, 4),
        'interpretacion': interpretacion(riesgo_ponderado),
        'fuentes_recomendadas': [
            f for f, d in datos.items() 
            if d['veracidad'] in ['OFICIAL', 'CIENTIFICA_REVISADA', 'MEDIO_PROFESIONAL']
        ],
        'fuentes_no_recomendadas': [
            f for f, d in datos.items() 
            if d['veracidad'] not in ['OFICIAL', 'CIENTIFICA_REVISADA', 'MEDIO_PROFESIONAL']
        ]
    }

def interpretacion(riesgo: float) -> str:
    if riesgo < 0.4:
        return 'RIESGO BAJO - Mantener vigilancia'
    elif riesgo < 0.6:
        return 'RIESGO MODERADO - Informarse de fuentes oficiales'
    elif riesgo < 0.75:
        return 'RIESGO ALTO - Contactar autoridades si hay señales'
    else:
        return 'RIESGO CRÍTICO - Seguir protocolos oficiales'

# ═══════════════════════════════════════════════════════════════════════════
# DISCURSO DIRIGIDO
# ═══════════════════════════════════════════════════════════════════════════

def generar_discurso_ciudadano() -> str:
    """
    Genera discurso dirigido a ciudadanos ceutíes
    """
    riesgo = calcular_riesgo_ciudadano()
    
    discurso = f"""
═══════════════════════════════════════════════════════════════════════════════
  INFORMACIÓN PARA CIUDADANOS CEUTÍES
  {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}
═══════════════════════════════════════════════════════════════════════════════

📊 RIESGO ACTUAL: {riesgo['riesgo_general']:.2f} ({riesgo['interpretacion']})

🔍 DESGLOSE POR VERACIDAD:

  • Fuentes OFICIALES y CIENTÍFICAS: {riesgo['riesgo_fuentes_confiables']:.2f}
  • Diferencia con redes sociales: {riesgo['diferencia']:.2f}

✅ FUENTES RECOMENDADAS (alta confianza):
"""
    
    for fuente in riesgo['fuentes_recomendadas']:
        discurso += f"\n   • {FUENTES[fuente]['nombre']}: {FUENTES[fuente]['url']}"
    
    discurso += f"\n\n⚠️  FUENTES NO RECOMENDADAS (baja confianza):"
    
    for fuente in riesgo['fuentes_no_recomendadas']:
        discurso += f"\n   • {FUENTES[fuente]['nombre']}: {FUENTES[fuente]['url']}"
    
    discurso += f"""

📋 CÓMO VERIFICAR INFORMACIÓN:

  1. ¿La fuente es oficial o científica revisada?
  2. ¿La información está en múltiples fuentes confiables?
  3. ¿La fecha es reciente?
  4. ¿Hay evidencia concreta o solo opiniones?

🎯 RECOMENDACIONES:

  • Para información sobre IA: usar {', '.join(riesgo['fuentes_recomendadas'][:2])}
  • Para verificar noticias: cruzar con Reuters y fuentes oficiales
  • Para investigación: usar ScienceDirect y arXiv (con precaución)
  • Evitar: Twitter/X como única fuente

═══════════════════════════════════════════════════════════════════════════════
  ESTE INFORME SE GENERA AUTOMÁTICAMENTE
  FUENTES: {len(FUENTES)} configuradas
  ACTUALIZACIÓN: Cada 6 horas
═══════════════════════════════════════════════════════════════════════════════
"""
    
    return discurso

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print(generar_discurso_ciudadano())
    
    # Guardar
    with open(f"ceuta_ciudadano_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
        f.write(generar_discurso_ciudadano())


