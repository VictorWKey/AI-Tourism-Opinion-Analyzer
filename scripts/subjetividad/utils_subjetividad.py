"""
Utilidades para Análisis de Subjetividad
=======================================

Este módulo contiene funciones auxiliares y utilidades para el análisis
de subjetividad de opiniones turísticas.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')



def limpiar_texto_opiniones(df: pd.DataFrame, columna_texto: str = 'TituloReview') -> pd.DataFrame:
    """
    Limpia y preprocesa el texto de las opiniones.
    
    Args:
        df (pd.DataFrame): Dataset con columna de texto
        columna_texto (str): Nombre de la columna con el texto
        
    Returns:
        pd.DataFrame: Dataset con texto limpio
    """
    df_limpio = df.copy()
    
    # Eliminar valores nulos y convertir a string
    df_limpio[columna_texto] = df_limpio[columna_texto].fillna("").astype(str)
    
    # Eliminar espacios extra
    df_limpio[columna_texto] = df_limpio[columna_texto].str.strip()
    
    # Filtrar opiniones muy cortas (menos de 10 caracteres)
    longitud_inicial = len(df_limpio)
    df_limpio = df_limpio[df_limpio[columna_texto].str.len() >= 10]
    longitud_final = len(df_limpio)
    
    if longitud_inicial != longitud_final:
        print(f"🧹 Texto limpiado: eliminadas {longitud_inicial - longitud_final} opiniones muy cortas")
    
    return df_limpio


def exportar_resultados_csv(df: pd.DataFrame, ruta_salida: str, incluir_index: bool = False) -> bool:
    """
    Exporta los resultados del análisis a un archivo CSV.
    
    Args:
        df (pd.DataFrame): Dataset con resultados
        ruta_salida (str): Ruta donde guardar el archivo
        incluir_index (bool): Si incluir el índice en el archivo
        
    Returns:
        bool: True si se exportó exitosamente, False en caso contrario
    """
    try:
        df.to_csv(ruta_salida, index=incluir_index, encoding='utf-8')
        print(f"✅ Resultados exportados exitosamente a: {ruta_salida}")
        print(f"📊 Total de registros exportados: {len(df)}")
        return True
    except Exception as e:
        print(f"❌ Error al exportar resultados: {e}")
        return False


def obtener_estadisticas_texto(df: pd.DataFrame, columna_texto: str = 'TituloReview') -> dict:
    """
    Obtiene estadísticas básicas del texto en el dataset.
    
    Args:
        df (pd.DataFrame): Dataset a analizar
        columna_texto (str): Nombre de la columna con el texto
        
    Returns:
        dict: Estadísticas del texto
    """
    if columna_texto not in df.columns:
        print(f"❌ Error: No se encontró la columna '{columna_texto}'")
        return {}
    
    textos = df[columna_texto].astype(str)
    longitudes = textos.str.len()
    
    estadisticas = {
        'total_textos': len(textos),
        'textos_vacios': (textos == '').sum(),
        'longitud_promedio': longitudes.mean(),
        'longitud_mediana': longitudes.median(),
        'longitud_min': longitudes.min(),
        'longitud_max': longitudes.max(),
        'longitud_std': longitudes.std()
    }
    
    return estadisticas


def mostrar_estadisticas_texto(df: pd.DataFrame, columna_texto: str = 'TituloReview') -> None:
    """
    Muestra las estadísticas de texto en consola.
    
    Args:
        df (pd.DataFrame): Dataset a analizar
        columna_texto (str): Nombre de la columna con el texto
    """
    estadisticas = obtener_estadisticas_texto(df, columna_texto)
    
    if not estadisticas:
        return
    
    print("📝 ESTADÍSTICAS DE TEXTO")
    print("=" * 40)
    print(f"Total de textos: {estadisticas['total_textos']}")
    print(f"Textos vacíos: {estadisticas['textos_vacios']}")
    print(f"Longitud promedio: {estadisticas['longitud_promedio']:.1f} caracteres")
    print(f"Longitud mediana: {estadisticas['longitud_mediana']:.1f} caracteres")
    print(f"Longitud mínima: {estadisticas['longitud_min']} caracteres")
    print(f"Longitud máxima: {estadisticas['longitud_max']} caracteres")
    print(f"Desviación estándar: {estadisticas['longitud_std']:.1f} caracteres")
