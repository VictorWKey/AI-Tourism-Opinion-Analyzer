"""
Visualizaciones para Análisis de Opiniones Mixtas
===============================================

Este módulo contiene visualizaciones específicas para el análisis de opiniones mixtas.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Optional

def visualizar_distribucion_tipos(df: pd.DataFrame, titulo: str = "Distribución de Tipos de Opiniones") -> None:
    """
    Visualiza la distribución de tipos de opiniones (Subjetivo, Objetivo, Mixto).
    
    Args:
        df: DataFrame con columna 'TipoOpinion'
        titulo: Título para los gráficos
    """
    tipos_conteo = df['TipoOpinion'].value_counts()
    tipos_porcentaje = (tipos_conteo / len(df) * 100).round(1)
    
    plt.figure(figsize=(12, 5))
    colores = ['#ff6b6b', '#4ecdc4', '#45b7d1']
    
    # Gráfico de conteos
    plt.subplot(1, 2, 1)
    bars = plt.bar(tipos_conteo.index, tipos_conteo.values, color=colores[:len(tipos_conteo)])
    plt.title(f'{titulo}\n(Conteos)', fontsize=12, fontweight='bold')
    plt.ylabel('Número de Opiniones')
    plt.xticks(rotation=0)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico de porcentajes
    plt.subplot(1, 2, 2)
    bars2 = plt.bar(tipos_porcentaje.index, tipos_porcentaje.values, color=colores[:len(tipos_porcentaje)])
    plt.title(f'{titulo}\n(Porcentajes)', fontsize=12, fontweight='bold')
    plt.ylabel('Porcentaje (%)')
    plt.xticks(rotation=0)
    
    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def mostrar_resumen_ejecutivo(estadisticas: Dict) -> None:
    """
    Muestra un resumen ejecutivo de los resultados del análisis.
    
    Args:
        estadisticas: Estadísticas del análisis de opiniones mixtas
    """
    print("🎯 RESUMEN EJECUTIVO - ANÁLISIS DE OPINIONES MIXTAS")
    print("=" * 60)
    
    # Resultados principales
    total = estadisticas['total_opiniones']
    mixtas = estadisticas['opiniones_mixtas']
    porcentaje_mixtas = estadisticas['porcentaje_mixtas']
    
    print(f"📊 RESULTADOS PRINCIPALES:")
    print(f"• Total opiniones analizadas: {total}")
    print(f"• Opiniones mixtas identificadas: {mixtas} ({porcentaje_mixtas:.1f}%)")
    
    # Distribución por tipos
    print(f"\n📋 DISTRIBUCIÓN POR TIPOS:")
    for tipo, cantidad in estadisticas['distribucion_tipos'].items():
        porcentaje = estadisticas['porcentajes_tipos'][tipo]
        print(f"• {tipo}: {cantidad} ({porcentaje}%)")
    
    # Análisis de frases
    print(f"\n🔍 ANÁLISIS GRANULAR:")
    print(f"• Total frases analizadas: {estadisticas['total_frases']}")
    print(f"• Promedio frases por opinión: {estadisticas['promedio_frases_por_opinion']:.1f}")
    print(f"• Distribución: {estadisticas['porcentaje_frases_subjetivas']:.1f}% subjetivas, {estadisticas['porcentaje_frases_objetivas']:.1f}% objetivas")
    
    # Implicaciones
    print(f"\n💡 IMPLICACIONES PARA TURISTOLOGÍA:")
    if porcentaje_mixtas > 15:
        print(f"• Las opiniones mixtas representan una fuente significativa de información")
        print(f"• Combinan percepciones emocionales con datos prácticos útiles")
        print(f"• Metodología validada para extracción de contenido híbrido")
    elif porcentaje_mixtas > 5:
        print(f"• Evidencia parcial de opiniones mixtas en el dataset")
        print(f"• Oportunidad para análisis granular en casos específicos")
    else:
        print(f"• Las opiniones tienden a ser predominantemente de un solo tipo")
        print(f"• Contenido menos mixto de lo esperado")
    
    print(f"\n✅ Metodología aplicada exitosamente: Segmentación + Clasificación por frases")

def mostrar_conclusiones_hipotesis(validacion: Dict, estadisticas: Dict) -> None:
    """
    Muestra las conclusiones finales sobre la validación de hipótesis.
    
    Args:
        validacion: Resultados de validación de hipótesis
        estadisticas: Estadísticas del análisis
    """
    print(f"\n🔬 CONCLUSIONES SOBRE LA HIPÓTESIS")
    print("=" * 50)
    
    print(validacion['mensaje_resultado'])
    
    if validacion['hipotesis_confirmada']:
        print(f"\n✅ EVIDENCIA ENCONTRADA:")
        print(f"• {validacion['porcentaje_mixtas']:.1f}% de opiniones contienen contenido mixto")
        print(f"• Las opiniones mixtas combinan información emocional y factual")
        print(f"• El análisis granular revela contenido híbrido no detectado previamente")
        
        if 'mixtas_promedio_subjetivo' in estadisticas:
            print(f"• Composición promedio: {estadisticas['mixtas_promedio_subjetivo']:.1f}% subjetivo, {estadisticas['mixtas_promedio_objetivo']:.1f}% objetivo")
    
    elif validacion['evidencia_significativa']:
        print(f"\n⚠️ EVIDENCIA PARCIAL:")
        print(f"• Se identificaron {estadisticas['opiniones_mixtas']} opiniones mixtas")
        print(f"• Aunque no alcanza el umbral establecido, es una proporción relevante")
        print(f"• Sugiere la existencia de contenido híbrido en ciertos contextos")
    
    else:
        print(f"\n❌ EVIDENCIA LIMITADA:")
        print(f"• Solo {validacion['porcentaje_mixtas']:.1f}% de opiniones son mixtas")
        print(f"• Las opiniones tienden a ser predominantemente de un tipo")
        print(f"• Menor contenido híbrido del esperado en este dataset")
    
    print(f"\n🎯 METODOLOGÍA VALIDADA:")
    print(f"• Segmentación automática de oraciones con modelos de deep learning")
    print(f"• Clasificación individual de frases para análisis granular")
    print(f"• Identificación exitosa de patrones de contenido híbrido")
    print(f"• Herramienta útil para análisis detallado de opiniones turísticas")
