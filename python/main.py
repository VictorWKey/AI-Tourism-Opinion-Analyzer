"""
Pipeline de Producción - AI Tourism Opinion Analyzer
===================================================
Ejecuta todas las fases de procesamiento en orden.
"""

from core import (
    ProcesadorBasico,
    GeneradorEstadisticasBasicas,
    AnalizadorSentimientos,
    AnalizadorSubjetividad,
    ClasificadorCategorias,
    AnalizadorJerarquicoTopicos,
    ResumidorInteligente,
    GeneradorInsightsEstrategicos,
    GeneradorVisualizaciones,
    LLMProvider
)


# ============================================================
# CONFIGURACIÓN DE FASES
# ============================================================
# Controla qué fases se ejecutan.
# True = Ejecutar siempre
# False = Omitir si ya fue ejecutada previamente
# Nota: Si una fase NO ha sido ejecutada nunca, se ejecutará
#       automáticamente sin importar esta configuración.
# ============================================================

CONFIG_FASES = {
    'fase_01': True,   # Procesamiento Básico
    'fase_02': True,   # Estadísticas Básicas
    'fase_03': True,   # Análisis de Sentimientos
    'fase_04': True,   # Análisis de Subjetividad
    'fase_05': True,   # Clasificación de Categorías
    'fase_06': True,   # Análisis Jerárquico de Tópicos
    'fase_07': True,   # Resumen Inteligente (Structured)
    'fase_08': True,   # Insights Estratégicos
    'fase_09': True,   # Generación de Visualizaciones
}


def main():
    """Ejecuta el pipeline completo de procesamiento."""
    print("="*60)
    print("PIPELINE DE PRODUCCIÓN - AI TOURISM OPINION ANALYZER")
    print("="*60)
    
    # Mostrar configuración de LLM
    print("\n[Configuración LLM]")
    try:
        llm_info = LLMProvider.get_info()
        print(f"   • Modo: {llm_info['modo'].upper()}")
        print(f"   • Modelo: {llm_info['modelo']}")
        if llm_info['modo'] == 'api':
            print(f"   • API configurada: {'✓' if llm_info.get('api_key_configurada') else '✗'}")
        else:
            print(f"   • URL base: {llm_info['base_url']}")
        print(f"   • Temperatura: {llm_info['temperatura']}")
    except Exception as e:
        print(f"   ⚠️  Error al cargar configuración LLM: {e}")
        print(f"   💡 Revisa el archivo .env o consulta LLM_SETUP.md")
        return
    
    # Fase 01: Procesamiento Básico
    print("\n[Fase 01] Procesamiento Básico de Datos")
    procesador_basico = ProcesadorBasico()
    procesador_basico.procesar(forzar=CONFIG_FASES['fase_01'])
    
    # Fase 02: Estadísticas Básicas
    print("\n[Fase 02] Estadísticas Básicas del Dataset")
    generador_estadisticas = GeneradorEstadisticasBasicas()
    generador_estadisticas.procesar(forzar=CONFIG_FASES['fase_02'])
    
    # Fase 03: Análisis de Sentimientos
    print("\n[Fase 03] Análisis de Sentimientos")
    analizador_sentimientos = AnalizadorSentimientos()
    analizador_sentimientos.procesar(forzar=CONFIG_FASES['fase_03'])
    
    # Fase 04: Análisis de Subjetividad
    print("\n[Fase 04] Análisis de Subjetividad")
    analizador_subjetividad = AnalizadorSubjetividad()
    analizador_subjetividad.procesar(forzar=CONFIG_FASES['fase_04'])
    
    # Fase 05: Clasificación de Categorías Multi-etiqueta
    print("\n[Fase 05] Clasificación de Categorías")
    clasificador_categorias = ClasificadorCategorias()
    clasificador_categorias.procesar(forzar=CONFIG_FASES['fase_05'])
    
    # Fase 06: Análisis Jerárquico de Tópicos
    print("\n[Fase 06] Análisis Jerárquico de Tópicos")
    analizador_topicos = AnalizadorJerarquicoTopicos()
    analizador_topicos.procesar(forzar=CONFIG_FASES['fase_06'])
    
    # Fase 07: Resumen Inteligente de Reseñas
    print("\n[Fase 07] Resumen Inteligente de Reseñas")
    # Parámetros optimizados por defecto:
    # - top_n_subtopicos=3: Solo los 3 subtópicos más frecuentes por categoría
    # - incluir_neutros=False: Excluir sentimientos neutros (solo Positivo y Negativo)
    resumidor = ResumidorInteligente(top_n_subtopicos=3, incluir_neutros=False)
    # Only structured summary is generated
    resumidor.procesar(forzar=CONFIG_FASES['fase_07'])
    
    # Fase 08: Insights Estratégicos
    print("\n[Fase 08] Insights Estratégicos")
    generador_insights = GeneradorInsightsEstrategicos()
    generador_insights.procesar(forzar=CONFIG_FASES['fase_08'])
    
    # Fase 09: Generación de Visualizaciones
    print("\n[Fase 09] Generación de Visualizaciones")
    generador_viz = GeneradorVisualizaciones()
    generador_viz.procesar(forzar=CONFIG_FASES['fase_09'])
    
    print("\n" + "="*60)
    print("✅ Pipeline completado exitosamente")
    print("="*60)


if __name__ == "__main__":
    main()
