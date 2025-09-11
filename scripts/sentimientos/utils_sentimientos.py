"""
Utilidades para Análisis de Sentimientos
=======================================

Este módulo contiene funciones auxiliares y utilidades para el análisis
de sentimientos de opiniones turísticas.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')


def cargar_dataset_ciudad(ruta_dataset: str) -> pd.DataFrame:
    """
    Función auxiliar para cargar un dataset de ciudad.
    
    Args:
        ruta_dataset (str): Ruta al archivo CSV del dataset
    
    Returns:
        pd.DataFrame: Dataset cargado
    
    Raises:
        FileNotFoundError: Si no se encuentra el archivo
        Exception: Para otros errores de carga
    """
    try:
        df = pd.read_csv(ruta_dataset)
        print(f"✅ Dataset cargado exitosamente")
        print(f"📊 Dimensiones del dataset: {df.shape}")
        print(f"🏙️ Ciudad: {df['Ciudad'].iloc[0]}")
        return df
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo del dataset")
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        raise


def mostrar_info_dataset(df: pd.DataFrame) -> None:
    """
    Muestra información detallada del dataset cargado.
    
    Args:
        df (pd.DataFrame): Dataset a analizar
    """
    print("\n" + "=" * 50)
    print("INFORMACIÓN GENERAL DEL DATASET")
    print("=" * 50)
    print(df.info())
    
    print("\n" + "=" * 50)
    print("DISTRIBUCIÓN DE CALIFICACIONES")
    print("=" * 50)
    print(df['Calificacion'].value_counts().sort_index())
    
    print("\n" + "=" * 50)
    print("PRIMERAS 3 FILAS DEL DATASET")
    print("=" * 50)
    return df.head(3)


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
        bool: True si se exportó exitosamente
    """
    try:
        df.to_csv(ruta_salida, index=incluir_index, encoding='utf-8')
        print(f"✅ Resultados exportados exitosamente a: {ruta_salida}")
        print(f"📊 Registros exportados: {len(df)}")
        return True
    except Exception as e:
        print(f"❌ Error al exportar: {e}")
        return False


def exportar_dataset_con_sentimientos(df: pd.DataFrame, ciudad: str, directorio_salida: str = '../data/processed/datasets_por_ciudad/') -> bool:
    """
    Exporta el dataset con análisis de sentimientos incluido.
    
    Args:
        df (pd.DataFrame): Dataset con análisis de sentimientos (debe tener columna SentimientoHF)
        ciudad (str): Nombre de la ciudad para el archivo
        directorio_salida (str): Directorio donde guardar el archivo
        
    Returns:
        bool: True si se exportó exitosamente
    """
    try:
        # Crear estructura de directorios
        directorio_sentimientos = os.path.join(directorio_salida, 'sentimientos', 'simple')
        os.makedirs(directorio_sentimientos, exist_ok=True)
        
        # Limpiar nombre de ciudad para el archivo
        ciudad_limpia = ciudad.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        nombre_archivo = f"dataset_{ciudad_limpia}_sentimientos.csv"
        ruta_completa = os.path.join(directorio_sentimientos, nombre_archivo)
        
        # Verificar que tenga las columnas necesarias
        columnas_requeridas = ['Titulo', 'Review', 'TipoViaje', 'Calificacion', 'OrigenAutor', 
                              'FechaOpinion', 'FechaEstadia', 'Ciudad', 'Atraccion', 'TituloReview', 'SentimientoHF']
        
        if 'SentimientoHF' not in df.columns:
            print("❌ Error: El dataset debe contener la columna 'SentimientoHF'")
            return False
        
        # Exportar con todas las columnas
        df.to_csv(ruta_completa, index=False, encoding='utf-8')
        
        print(f"✅ Dataset con sentimientos exportado exitosamente")
        print(f"📁 Archivo: {nombre_archivo}")
        print(f"📍 Ubicación: {ruta_completa}")
        print(f"📊 Registros: {len(df)}")
        print(f"📋 Columnas incluidas: {', '.join(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al exportar dataset con sentimientos: {e}")
        return False


def exportar_dataset_con_ambos_sentimientos(df: pd.DataFrame, ciudad: str, directorio_salida: str = '../data/processed/datasets_por_ciudad/') -> bool:
    """
    Exporta el dataset con análisis de sentimientos de ambos modelos incluido.
    
    Args:
        df (pd.DataFrame): Dataset con análisis de sentimientos (debe tener columnas SentimientoPorHF y SentimientoPorCardiff)
        ciudad (str): Nombre de la ciudad para el archivo
        directorio_salida (str): Directorio donde guardar el archivo
        
    Returns:
        bool: True si se exportó exitosamente
    """
    try:
        # Crear estructura de directorios
        directorio_sentimientos = os.path.join(directorio_salida, 'sentimientos', 'completo')
        os.makedirs(directorio_sentimientos, exist_ok=True)
        
        # Limpiar nombre de ciudad para el archivo
        ciudad_limpia = ciudad.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        nombre_archivo = f"dataset_{ciudad_limpia}_sentimientos_completo.csv"
        ruta_completa = os.path.join(directorio_sentimientos, nombre_archivo)
        
        # Verificar que tenga las columnas necesarias
        columnas_ml_requeridas = ['SentimientoPorHF', 'SentimientoPorCardiff']
        
        for columna in columnas_ml_requeridas:
            if columna not in df.columns:
                print(f"❌ Error: El dataset debe contener la columna '{columna}'")
                return False
        
        # Exportar con todas las columnas
        df.to_csv(ruta_completa, index=False, encoding='utf-8')
        
        print(f"✅ Dataset con ambos modelos de sentimientos exportado exitosamente")
        print(f"📁 Archivo: {nombre_archivo}")
        print(f"📍 Ubicación: {ruta_completa}")
        print(f"📊 Registros: {len(df)}")
        print(f"🤖 Modelos incluidos: HuggingFace + Cardiff NLP")
        print(f"📋 Columnas incluidas: {', '.join(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al exportar dataset con ambos sentimientos: {e}")
        return False


def exportar_dataset_consolidado_analisis(df: pd.DataFrame, directorio_salida: str = '../data/processed/') -> bool:
    """
    Exporta el dataset consolidado final con todos los análisis de sentimiento para uso en futuros notebooks.
    
    Args:
        df (pd.DataFrame): Dataset consolidado con todas las columnas de análisis
        directorio_salida (str): Directorio donde guardar el archivo
        
    Returns:
        bool: True si se exportó exitosamente
    """
    try:
        # Crear el directorio si no existe
        os.makedirs(directorio_salida, exist_ok=True)
        
        nombre_archivo = "dataset_opiniones_analisis.csv"
        ruta_completa = os.path.join(directorio_salida, nombre_archivo)
        
        # Verificar que tenga las columnas necesarias de análisis
        columnas_analisis_requeridas = ['SentimientoPorCalificacion', 'SentimientoPorHF', 'SentimientoPorCardiff']
        
        for columna in columnas_analisis_requeridas:
            if columna not in df.columns:
                print(f"❌ Error: El dataset debe contener la columna '{columna}'")
                return False
        
        # Exportar con todas las columnas
        df.to_csv(ruta_completa, index=False, encoding='utf-8')
        
        ciudades = df['Ciudad'].unique()
        
        print(f"✅ Dataset consolidado de análisis exportado exitosamente")
        print(f"📁 Archivo: {nombre_archivo}")
        print(f"📍 Ubicación: {ruta_completa}")
        print(f"📊 Registros: {len(df)}")
        print(f"🏙️ Ciudades incluidas: {', '.join(ciudades)}")
        print(f"🎯 Atracciones únicas: {df['Atraccion'].nunique()}")
        print(f"🤖 Análisis incluidos: Calificación + HuggingFace + Cardiff NLP")
        print(f"📋 Total de columnas: {len(df.columns)}")
        print(f"💾 Listo para usar en futuros notebooks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al exportar dataset consolidado de análisis: {e}")
        return False
