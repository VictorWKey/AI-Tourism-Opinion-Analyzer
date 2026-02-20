"""
Módulo Core - Pipeline de Análisis
===================================
Contiene todas las fases del pipeline de análisis de opiniones turísticas.

Heavy ML dependencies (torch, transformers, bertopic, langchain, etc.) are
imported lazily so that lightweight modules (fase_01, rollback_manager) remain
importable in environments that only have the minimal test dependencies.
"""

# Always available — only require stdlib + pandas
from .fase_01_procesamiento_basico import ProcesadorBasico
from .rollback_manager import RollbackManager, get_rollback_manager

# Optional heavy dependencies — silently unavailable if packages aren't installed
try:
    from .fase_02_estadisticas_basicas import GeneradorEstadisticasBasicas
    from .fase_03_analisis_sentimientos import AnalizadorSentimientos
    from .fase_04_analisis_subjetividad import AnalizadorSubjetividad
    from .fase_05_clasificacion_categorias import ClasificadorCategorias
    from .fase_06_analisis_jerarquico_topicos import AnalizadorJerarquicoTopicos
    from .fase_07_resumen_inteligente import ResumidorInteligente
    from .fase_08_insights_estrategicos import GeneradorInsightsEstrategicos
    from .fase_08_visualizaciones import GeneradorVisualizaciones
except ImportError:
    pass

try:
    from .llm_provider import (
        LLMProvider,
        LLMRetryExhaustedError,
        RobustStructuredChain,
        crear_chain,
        crear_chain_robusto,
        get_llm,
    )
except ImportError:
    pass

try:
    from .llm_utils import (
        LLMEmptyResponseError,
        LLMError,
        LLMParsingError,
        RetryConfig,
        extraer_json_de_respuesta,
        parsear_json_seguro,
        parsear_pydantic_seguro,
        reparar_json,
    )
except ImportError:
    pass

__all__ = [
    # Always available
    'ProcesadorBasico',
    'RollbackManager',
    'get_rollback_manager',
    # Available when full dependencies are installed
    'GeneradorEstadisticasBasicas',
    'AnalizadorSentimientos',
    'AnalizadorSubjetividad',
    'ClasificadorCategorias',
    'AnalizadorJerarquicoTopicos',
    'ResumidorInteligente',
    'GeneradorInsightsEstrategicos',
    'GeneradorVisualizaciones',
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
]
