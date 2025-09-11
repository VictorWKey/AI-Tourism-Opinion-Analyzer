"""
Módulo para guardar resultados y generar resúmenes finales.
"""

import pandas as pd


def guardar_resultados(df_clasificado, df_existente=None, ruta_salida="../data/processed/dataset_opiniones_analisis.csv"):
    """
    Guarda los resultados clasificados con LLM agregando la columna SubjetividadConLLM al dataset original.
    SOLO sobrescribe el archivo cuando la clasificación está 100% completa.
    
    Args:
        df_clasificado (pandas.DataFrame): DataFrame con las nuevas clasificaciones LLM COMPLETAS
        df_existente (pandas.DataFrame): DataFrame con clasificaciones previas (opcional)
        ruta_salida (str): Ruta donde guardar el archivo (por defecto sobrescribe el dataset original)
        
    Returns:
        bool: True si el guardado fue exitoso, False en caso contrario
    """
    if df_clasificado is None:
        print("❌ Error: No hay datos clasificados para guardar")
        return False
    
    try:
        # Verificar que tengamos datos válidos para guardar
        if 'SubjetividadConLLM' not in df_clasificado.columns:
            print("❌ Error: El DataFrame no contiene la columna SubjetividadConLLM")
            return False
        
        # Verificar que no hay valores nulos o errores en la clasificación
        errores_count = len(df_clasificado[df_clasificado['SubjetividadConLLM'] == 'Error'])
        if errores_count > 0:
            print(f"⚠️ Advertencia: {errores_count} reseñas tienen errores de clasificación")
            respuesta = input("¿Desea guardar de todos modos? (s/n): ")
            if respuesta.lower() not in ['s', 'si', 'sí', 'yes', 'y']:
                print("❌ Guardado cancelado por el usuario")
                return False
        
        print(f"💾 GUARDANDO DATASET FINAL...")
        print(f"📁 Ruta: {ruta_salida}")
        print(f"📊 Registros: {len(df_clasificado)}")
        
        df_final = df_clasificado.copy()
        
        # Sobrescribir el archivo del dataset original
        df_final.to_csv(ruta_salida, index=False, encoding='utf-8')
        
        print(f"✅ Dataset actualizado y guardado exitosamente")
        print(f"📊 Total de registros: {len(df_final)}")
        
        # Mostrar resumen de análisis disponibles
        tipos_analisis = []
        if 'SubjetividadConHF' in df_final.columns:
            tipos_analisis.append("HuggingFace")
        if 'SubjetividadConFrases' in df_final.columns:
            tipos_analisis.append("Análisis por frases")
        if 'SubjetividadConLLM' in df_final.columns:
            tipos_analisis.append("LLM")
        
        print(f"🎯 Tipos de análisis disponibles: {', '.join(tipos_analisis)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar resultados: {e}")
        return False


def generar_resumen_final(df_clean):
    """
    Genera un resumen final del proceso de clasificación.
    
    Args:
        df_clean (pandas.DataFrame): DataFrame limpio con clasificaciones válidas
    """
    if df_clean is None:
        return
    
    print("\n🎯 RESUMEN FINAL")
    print("=" * 40)
    
    # Estadísticas generales
    total_reviews = len(df_clean)
    conteo = df_clean['SubjetividadConLLM'].value_counts()
    
    print("\n🏷️ RESULTADOS:")
    for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
        if categoria in conteo:
            count = conteo[categoria]
            percentage = (count / total_reviews) * 100
            print(f"   {categoria}: {count} reseñas ({percentage:.1f}%)")
    
    # Comparación por ciudad
    print("\n🌎 POR CIUDAD:")
    for ciudad in df_clean['Ciudad'].unique():
        df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
        conteo_ciudad = df_ciudad['SubjetividadConLLM'].value_counts()
        categoria_ciudad = conteo_ciudad.index[0]
        porcentaje_ciudad = (conteo_ciudad.iloc[0] / len(df_ciudad)) * 100
        
        print(f"   {ciudad}: {categoria_ciudad} ({porcentaje_ciudad:.1f}%)")
    
    print("\n✅ Clasificación completada")
