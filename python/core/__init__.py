"""
Módulo Core - Pipeline de Análisis
===================================
Contiene todas las fases del pipeline de análisis de opiniones turísticas.
"""

from .llm_provider import (
    LLMProvider, 
    get_llm, 
    crear_chain, 
    crear_chain_robusto,
    RobustStructuredChain,
    LLMRetryExhaustedError
)
from .llm_utils import (
    parsear_json_seguro,
    parsear_pydantic_seguro,
    extraer_json_de_respuesta,
    reparar_json,
    RetryConfig,
    LLMError,
    LLMParsingError,
    LLMEmptyResponseError
)
from .fase_01_procesamiento_basico import ProcesadorBasico
from .fase_02_analisis_sentimientos import AnalizadorSentimientos
from .fase_03_analisis_subjetividad import AnalizadorSubjetividad
from .fase_04_clasificacion_categorias import ClasificadorCategorias
from .fase_05_analisis_jerarquico_topicos import AnalizadorJerarquicoTopicos
from .fase_06_resumen_inteligente import ResumidorInteligente
from .fase_07_visualizaciones import GeneradorVisualizaciones
from .rollback_manager import RollbackManager, get_rollback_manager

__all__ = [
    # LLM Provider
    'LLMProvider',
    'get_llm',
    'crear_chain',
    'crear_chain_robusto',
    'RobustStructuredChain',
    'LLMRetryExhaustedError',
    # LLM Utils
    'parsear_json_seguro',
    'parsear_pydantic_seguro',
    'extraer_json_de_respuesta',
    'reparar_json',
    'RetryConfig',
    'LLMError',
    'LLMParsingError',
    'LLMEmptyResponseError',
    # Fases del pipeline
    'ProcesadorBasico',
    'AnalizadorSentimientos',
    'AnalizadorSubjetividad',
    'ClasificadorCategorias',
    'AnalizadorJerarquicoTopicos',
    'ResumidorInteligente',
    'GeneradorVisualizaciones',
    'RollbackManager',
    'get_rollback_manager',
]
