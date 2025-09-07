"""
Módulo de etiquetado de subjetividad para análisis de opiniones turísticas.

Este módulo contiene las clases y funciones necesarias para clasificar
reseñas turísticas en categorías de subjetividad usando LangChain y GPT-4o-mini.
"""

from .configuracion import SubjectivityClassification, configurar_clasificador, verificar_api_key
from .cargador_datos import cargar_datasets, cargar_muestra_prueba, verificar_datos_clasificados
from .clasificador import clasificar_reviews, verificar_checkpoint, limpiar_checkpoint, reiniciar_clasificacion, prueba_rapida
from .analizador import analizar_resultados, mostrar_opiniones_por_categoria, obtener_estadisticas_resumidas
from .visualizador import crear_visualizaciones, crear_grafico_simple, configurar_estilo_graficos
from .guardador import guardar_resultados, generar_resumen_final, generar_reporte_completo, exportar_estadisticas_json
from .utils_etiquetado import configurar_entorno, mostrar_comandos_utiles, proceso_completo_clasificacion, validar_dependencias

__all__ = [
    # Configuración
    'SubjectivityClassification',
    'configurar_clasificador',
    'verificar_api_key',
    
    # Carga de datos
    'cargar_datasets',
    'cargar_muestra_prueba',
    'verificar_datos_clasificados',
    
    # Clasificación
    'clasificar_reviews',
    'verificar_checkpoint',
    'limpiar_checkpoint',
    'reiniciar_clasificacion',
    'prueba_rapida',
    
    # Análisis
    'analizar_resultados',
    'mostrar_opiniones_por_categoria',
    'obtener_estadisticas_resumidas',
    
    # Visualización
    'crear_visualizaciones',
    'crear_grafico_simple',
    'configurar_estilo_graficos',
    
    # Guardado
    'guardar_resultados',
    'generar_resumen_final',
    'generar_reporte_completo',
    'exportar_estadisticas_json',
    
    # Utilidades
    'configurar_entorno',
    'mostrar_comandos_utiles',
    'proceso_completo_clasificacion',
    'validar_dependencias'
]
