"""
Utilidades para Análisis de Subjetividad
=======================================

Este módulo contiene funciones auxiliares y utilidades para el análisis
de subjetividad de opiniones turísticas.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import os
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


def exportar_dataset_con_subjetividad(df: pd.DataFrame, ciudad: str, directorio_salida: str = '../data/processed/datasets_por_ciudad/') -> bool:
    """
    Exporta el dataset con análisis de subjetividad incluido.
    
    Args:
        df (pd.DataFrame): Dataset con análisis de subjetividad (debe tener columna ClasificacionSubjetividadConHF)
        ciudad (str): Nombre de la ciudad para el archivo
        directorio_salida (str): Directorio base donde guardar el archivo
        
    Returns:
        bool: True si se exportó exitosamente
    """
    try:
        # Crear estructura de directorios
        directorio_subjetividad = os.path.join(directorio_salida, 'subjetividad')
        os.makedirs(directorio_subjetividad, exist_ok=True)
        
        # Limpiar nombre de ciudad para el archivo
        ciudad_limpia = ciudad.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        nombre_archivo = f"dataset_{ciudad_limpia}_subjetividad.csv"
        ruta_completa = os.path.join(directorio_subjetividad, nombre_archivo)
        
        # Verificar que tenga las columnas necesarias
        if 'ClasificacionSubjetividadConHF' not in df.columns:
            print("❌ Error: El dataset debe contener la columna 'ClasificacionSubjetividadConHF'")
            return False
        
        # Exportar con todas las columnas
        df.to_csv(ruta_completa, index=False, encoding='utf-8')
        
        print(f"✅ Dataset con análisis de subjetividad exportado exitosamente")
        print(f"📁 Archivo: {nombre_archivo}")
        print(f"📍 Ubicación: {ruta_completa}")
        print(f"📊 Registros: {len(df)}")
        print(f"📋 Columnas incluidas: {', '.join(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al exportar dataset con subjetividad: {e}")
        return False


def exportar_dataset_combinado(df: pd.DataFrame, ciudad: str, directorio_salida: str = '../data/processed/datasets_por_ciudad/') -> bool:
    """
    Exporta el dataset con múltiples tipos de análisis (sentimientos + subjetividad).
    
    Args:
        df (pd.DataFrame): Dataset con análisis completos
        ciudad (str): Nombre de la ciudad para el archivo
        directorio_salida (str): Directorio base donde guardar el archivo
        
    Returns:
        bool: True si se exportó exitosamente
    """
    try:
        # Crear estructura de directorios
        directorio_combinado = os.path.join(directorio_salida, 'combinado')
        os.makedirs(directorio_combinado, exist_ok=True)
        
        # Limpiar nombre de ciudad para el archivo
        ciudad_limpia = ciudad.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        nombre_archivo = f"dataset_{ciudad_limpia}_completo.csv"
        ruta_completa = os.path.join(directorio_combinado, nombre_archivo)
        
        # Verificar que tenga análisis de sentimientos y subjetividad
        tiene_sentimientos = any(col in df.columns for col in ['SentimientoHF', 'SentimientoCardiff'])
        tiene_subjetividad = 'ClasificacionSubjetividadConHF' in df.columns
        
        if not (tiene_sentimientos or tiene_subjetividad):
            print("❌ Error: El dataset debe contener al menos un análisis (sentimientos o subjetividad)")
            return False
        
        # Exportar con todas las columnas
        df.to_csv(ruta_completa, index=False, encoding='utf-8')
        
        analisis_incluidos = []
        if tiene_sentimientos:
            analisis_incluidos.append("Sentimientos")
        if tiene_subjetividad:
            analisis_incluidos.append("Subjetividad")
        
        print(f"✅ Dataset combinado exportado exitosamente")
        print(f"📁 Archivo: {nombre_archivo}")
        print(f"📍 Ubicación: {ruta_completa}")
        print(f"📊 Registros: {len(df)}")
        print(f"🔬 Análisis incluidos: {', '.join(analisis_incluidos)}")
        print(f"📋 Columnas incluidas: {', '.join(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al exportar dataset combinado: {e}")
        return False


def actualizar_dataset_principal(df_analisis: pd.DataFrame, ruta_dataset_principal: str, 
                                nueva_columna: str = 'SubjetividadConFrases') -> bool:
    """
    Actualiza el dataset principal agregando solo una nueva columna sin las columnas temporales de análisis.
    
    Args:
        df_analisis (pd.DataFrame): Dataset con análisis completo que contiene las columnas temporales
        ruta_dataset_principal (str): Ruta del archivo principal a actualizar
        nueva_columna (str): Nombre de la nueva columna a agregar al dataset principal
        
    Returns:
        bool: True si se guardó exitosamente, False en caso contrario
    """
    try:
        print(f"📂 Actualizando dataset principal...")
        
        # Leer el dataset original para mantener las columnas originales
        df_original = pd.read_csv(ruta_dataset_principal)
        
        # Agregar/actualizar la columna SubjetividadConFrases desde el análisis
        if nueva_columna in df_analisis.columns:
            df_original[nueva_columna] = df_analisis[nueva_columna]
        else:
            print(f"❌ Error: No se encontró la columna '{nueva_columna}' en el dataset de análisis")
            return False
        
        # Definir columnas temporales de análisis que no se deben guardar
        columnas_analisis_temporales = [
            'TotalFrases', 'FrasesSubjetivas', 'FrasesObjetivas', 
            'TipoOpinion', 'EsMixta', 'PorcentajeSubjetivo', 'PorcentajeObjetivo'
        ]
        
        # Asegurar que solo se mantengan las columnas originales + nueva columna
        columnas_a_mantener = [col for col in df_original.columns if col not in columnas_analisis_temporales]
        df_final = df_original[columnas_a_mantener]
        
        # Sobrescribir el archivo principal con las columnas filtradas
        df_final.to_csv(ruta_dataset_principal, index=False, encoding='utf-8')
        
        # Mostrar resultados
        print(f"✅ Dataset principal actualizado exitosamente en: {ruta_dataset_principal}")
        print(f"📊 Total de registros: {len(df_final)}")
        print(f"🆕 Nueva columna agregada: {nueva_columna}")
        
        # Verificar distribución de la nueva columna
        distribucion = df_final[nueva_columna].value_counts()
        print(f"\n📈 Distribución de {nueva_columna}:")
        for tipo, cantidad in distribucion.items():
            porcentaje = (cantidad / len(df_final)) * 100
            print(f"   {tipo}: {cantidad} opiniones ({porcentaje:.1f}%)")
        
        # Comparar con análisis HF si existe
        columnas_subjetividad = ['SubjetividadConHF', 'ClasificacionSubjetividadConHF']
        columna_hf = None
        for col in columnas_subjetividad:
            if col in df_final.columns:
                columna_hf = col
                break
        
        if columna_hf:
            print(f"\n🔍 Comparación {columna_hf} vs {nueva_columna}:")
            comparacion = pd.crosstab(df_final[columna_hf], 
                                     df_final[nueva_columna], 
                                     margins=True)
            print(comparacion)
        
        # Mostrar resumen de columnas finales
        print(f"\n📋 Columnas finales en el dataset ({len(df_final.columns)} total):")
        for col in df_final.columns:
            print(f"   • {col}")
        
        print(f"\n🗑️ Columnas temporales eliminadas: {', '.join(columnas_analisis_temporales)}")
        print(f"🔄 Dataset listo para ser usado en análisis posteriores")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar dataset con nueva columna: {e}")
        return False
