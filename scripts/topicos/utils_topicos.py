"""
Utilidades para análisis de tópicos en opiniones turísticas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Dict, Optional


def mostrar_estadisticas_limpieza(df: pd.DataFrame, 
                                columna_original: str = 'TituloReview',
                                columna_limpia: str = 'TituloReviewLimpio') -> None:
    """
    Muestra estadísticas comparativas entre texto original y limpio.
    
    Args:
        df: DataFrame con los datos
        columna_original: Nombre de la columna con texto original
        columna_limpia: Nombre de la columna con texto limpio
    """
    # Filtrar filas válidas
    df_valido = df.dropna(subset=[columna_original, columna_limpia])
    
    # Calcular estadísticas
    stats_original = {
        'longitud_promedio': df_valido[columna_original].str.len().mean(),
        'palabras_promedio': df_valido[columna_original].str.split().str.len().mean(),
        'textos_vacios': df_valido[columna_original].str.strip().eq('').sum()
    }
    
    stats_limpia = {
        'longitud_promedio': df_valido[columna_limpia].str.len().mean(),
        'palabras_promedio': df_valido[columna_limpia].str.split().str.len().mean(),
        'textos_vacios': df_valido[columna_limpia].str.strip().eq('').sum()
    }
    
    print("📊 ESTADÍSTICAS DE LIMPIEZA DE TEXTO")
    print("=" * 50)
    print(f"📈 Total de textos analizados: {len(df_valido)}")
    print()
    
    print("📝 TEXTO ORIGINAL:")
    print(f"   Longitud promedio: {stats_original['longitud_promedio']:.1f} caracteres")
    print(f"   Palabras promedio: {stats_original['palabras_promedio']:.1f}")
    print(f"   Textos vacíos: {stats_original['textos_vacios']}")
    print()
    
    print("🧹 TEXTO LIMPIO:")
    print(f"   Longitud promedio: {stats_limpia['longitud_promedio']:.1f} caracteres")
    print(f"   Palabras promedio: {stats_limpia['palabras_promedio']:.1f}")
    print(f"   Textos vacíos: {stats_limpia['textos_vacios']}")
    print()
    
    # Calcular reducciones
    reduccion_longitud = ((stats_original['longitud_promedio'] - stats_limpia['longitud_promedio']) / 
                         stats_original['longitud_promedio'] * 100)
    reduccion_palabras = ((stats_original['palabras_promedio'] - stats_limpia['palabras_promedio']) / 
                         stats_original['palabras_promedio'] * 100)
    
    print("📉 REDUCCIÓN TRAS LIMPIEZA:")
    print(f"   Reducción en longitud: {reduccion_longitud:.1f}%")
    print(f"   Reducción en palabras: {reduccion_palabras:.1f}%")
    print(f"   Textos perdidos: {stats_limpia['textos_vacios'] - stats_original['textos_vacios']}")


def mostrar_ejemplos_limpieza(df: pd.DataFrame,
                            columna_original: str = 'TituloReview',
                            columna_limpia: str = 'TituloReviewLimpio',
                            n_ejemplos: int = 5) -> None:
    """
    Muestra ejemplos de texto antes y después de la limpieza.
    
    Args:
        df: DataFrame con los datos
        columna_original: Nombre de la columna con texto original
        columna_limpia: Nombre de la columna con texto limpio
        n_ejemplos: Número de ejemplos a mostrar
    """
    print(f"\n🔍 EJEMPLOS DE LIMPIEZA DE TEXTO (mostrando {n_ejemplos})")
    print("=" * 80)
    
    # Seleccionar ejemplos aleatorios
    df_muestra = df.dropna(subset=[columna_original, columna_limpia]).sample(n=min(n_ejemplos, len(df)))
    
    for i, (idx, row) in enumerate(df_muestra.iterrows(), 1):
        print(f"\n📄 EJEMPLO {i}:")
        print(f"🔸 Original: {row[columna_original]}")
        print(f"🔹 Limpio:   {row[columna_limpia]}")
        
        # Mostrar estadísticas del ejemplo
        len_orig = len(str(row[columna_original]))
        len_limpio = len(str(row[columna_limpia]))
        reduccion = ((len_orig - len_limpio) / len_orig * 100) if len_orig > 0 else 0
        print(f"📊 Reducción: {len_orig} → {len_limpio} caracteres ({reduccion:.1f}%)")
        print("-" * 80)


def validar_textos_para_topicos(df: pd.DataFrame,
                               columna_texto: str = 'TituloReviewLimpio',
                               min_palabras: int = 2) -> Tuple[pd.DataFrame, Dict]:
    """
    Valida y filtra textos para análisis de tópicos.
    
    Args:
        df: DataFrame con los datos
        columna_texto: Nombre de la columna con texto a validar
        min_palabras: Número mínimo de palabras válidas
        
    Returns:
        Tuple con DataFrame filtrado y estadísticas de validación
    """
    df_original = df.copy()
    
    # Filtrar textos válidos
    mask_valido = (
        df[columna_texto].notna() &
        (df[columna_texto].str.strip() != '') &
        (df[columna_texto].str.split().str.len() >= min_palabras)
    )
    
    df_valido = df[mask_valido].copy()
    
    # Estadísticas de validación
    stats = {
        'total_original': len(df_original),
        'textos_validos': len(df_valido),
        'textos_eliminados': len(df_original) - len(df_valido),
        'porcentaje_validos': len(df_valido) / len(df_original) * 100 if len(df_original) > 0 else 0,
        'promedio_palabras': df_valido[columna_texto].str.split().str.len().mean() if len(df_valido) > 0 else 0
    }
    
    print("✅ VALIDACIÓN DE TEXTOS PARA ANÁLISIS DE TÓPICOS")
    print("=" * 55)
    print(f"📊 Total textos originales: {stats['total_original']}")
    print(f"✅ Textos válidos: {stats['textos_validos']}")
    print(f"❌ Textos eliminados: {stats['textos_eliminados']}")
    print(f"📈 Porcentaje válidos: {stats['porcentaje_validos']:.1f}%")
    print(f"📝 Promedio palabras por texto: {stats['promedio_palabras']:.1f}")
    
    return df_valido, stats


def generar_reporte_limpieza(df_antes: pd.DataFrame,
                           df_despues: pd.DataFrame,
                           columna_original: str = 'TituloReview',
                           columna_limpia: str = 'TituloReviewLimpio') -> None:
    """
    Genera un reporte completo del proceso de limpieza.
    
    Args:
        df_antes: DataFrame antes de la limpieza
        df_despues: DataFrame después de la limpieza
        columna_original: Nombre de la columna original
        columna_limpia: Nombre de la columna limpia
    """
    print("📋 REPORTE COMPLETO DE LIMPIEZA DE TEXTO")
    print("=" * 60)
    
    # Estadísticas generales
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   Registros procesados: {len(df_antes)}")
    print(f"   Nueva columna creada: {columna_limpia}")
    print(f"   Posición en dataset: columna {df_despues.columns.get_loc(columna_limpia) + 1}")
    
    # Mostrar estadísticas detalladas
    mostrar_estadisticas_limpieza(df_despues, columna_original, columna_limpia)
    
    # Validar textos para tópicos
    print(f"\n{'='*60}")
    df_valido, stats_validacion = validar_textos_para_topicos(df_despues, columna_limpia)
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if stats_validacion['porcentaje_validos'] < 80:
        print("   ⚠️  Bajo porcentaje de textos válidos. Considera ajustar parámetros de limpieza.")
    else:
        print("   ✅ Buen porcentaje de textos válidos para análisis de tópicos.")
    
    if stats_validacion['promedio_palabras'] < 3:
        print("   ⚠️  Promedio de palabras bajo. Los tópicos pueden ser menos informativos.")
    else:
        print("   ✅ Promedio de palabras adecuado para análisis de tópicos.")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"   1. Usar columna '{columna_limpia}' para análisis de tópicos")
    print(f"   2. Dataset guardado con nueva columna")
    print(f"   3. Ejecutar BERTopic con textos limpios")


def visualizar_distribucion_palabras(df: pd.DataFrame,
                                   columna_original: str = 'TituloReview',
                                   columna_limpia: str = 'TituloReviewLimpio') -> None:
    """
    Visualiza la distribución de palabras antes y después de la limpieza.
    
    Args:
        df: DataFrame con los datos
        columna_original: Nombre de la columna original
        columna_limpia: Nombre de la columna limpia
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Calcular número de palabras
    palabras_original = df[columna_original].str.split().str.len().dropna()
    palabras_limpia = df[columna_limpia].str.split().str.len().dropna()
    
    # Histograma texto original
    axes[0].hist(palabras_original, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0].set_title(f'Distribución de Palabras - {columna_original}', fontweight='bold')
    axes[0].set_xlabel('Número de Palabras')
    axes[0].set_ylabel('Frecuencia')
    axes[0].axvline(palabras_original.mean(), color='red', linestyle='--', 
                   label=f'Media: {palabras_original.mean():.1f}')
    axes[0].legend()
    
    # Histograma texto limpio
    axes[1].hist(palabras_limpia, bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[1].set_title(f'Distribución de Palabras - {columna_limpia}', fontweight='bold')
    axes[1].set_xlabel('Número de Palabras')
    axes[1].set_ylabel('Frecuencia')
    axes[1].axvline(palabras_limpia.mean(), color='red', linestyle='--', 
                   label=f'Media: {palabras_limpia.mean():.1f}')
    axes[1].legend()
    
    plt.tight_layout()
    plt.show()
    
    # Estadísticas adicionales
    print("📊 ESTADÍSTICAS DE DISTRIBUCIÓN DE PALABRAS:")
    print(f"Original - Media: {palabras_original.mean():.1f}, Mediana: {palabras_original.median():.1f}")
    print(f"Limpio   - Media: {palabras_limpia.mean():.1f}, Mediana: {palabras_limpia.median():.1f}")
