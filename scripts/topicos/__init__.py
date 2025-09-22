"""
Módulo de análisis de tópicos para opiniones turísticas.

Este módulo proporciona herramientas para:
- Limpieza profunda de texto
- Análisis de tópicos con BERTopic y FASTopic
- Optimización automática de hiperparámetros
- Visualización de resultados
"""

from .limpieza_texto import LimpiadorTexto
from .limpieza_texto_mejorado import LimpiadorTextoMejorado
from .traductor_textos import TraductorTextos
from .utils_topicos import *
from .clasificador_topicos_llm import configurar_clasificador_topicos
from .analizador_caracteristicas import AnalizadorCaracteristicas, configurar_bertopic_inteligente
from .configurador_fastopic import (
    AnalizadorCaracteristicasFASTopic, 
    configurar_fastopic_inteligente,
    configurar_preprocesador_inteligente,
    obtener_configuracion_manual
)
from .evaluador_metricas import (
    evaluar_modelo_topicos,
    extraer_palabras_bertopic,
    extraer_palabras_fastopic,
    mostrar_metricas
)

__all__ = [
    'LimpiadorTexto', 
    'LimpiadorTextoMejorado',
    'TraductorTextos',
    'generar_reporte_limpieza',
    'mostrar_ejemplos_limpieza',
    'configurar_clasificador_topicos',
    'AnalizadorCaracteristicas',
    'configurar_bertopic_inteligente',
    'AnalizadorCaracteristicasFASTopic',
    'configurar_fastopic_inteligente',
    'configurar_preprocesador_inteligente',
    'obtener_configuracion_manual',
    'evaluar_modelo_topicos',
    'extraer_palabras_bertopic',
    'extraer_palabras_fastopic',
    'mostrar_metricas'
]
