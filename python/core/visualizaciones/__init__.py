"""
Módulo de Visualizaciones - Fase 08
====================================
Sistema inteligente y adaptativo de generación de visualizaciones gráficas.
Los insights textuales se exportan a JSON mediante ExportadorInsights.
"""

from .exportador_insights import ExportadorInsights
from .utils import COLORES, CONFIG_EXPORT, FONT_SIZES, PALETA_CATEGORIAS, configurar_tema, guardar_figura
from .validador import ValidadorVisualizaciones

__all__ = [
    'COLORES',
    'CONFIG_EXPORT',
    'FONT_SIZES',
    'PALETA_CATEGORIAS',
    'ExportadorInsights',
    'ValidadorVisualizaciones',
    'configurar_tema',
    'guardar_figura',
]
