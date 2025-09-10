"""
Módulo para guardar resultados y generar resúmenes finales.
"""

import pandas as pd


def guardar_resultados(df_clasificado, df_existente=None, ruta_salida="../data/processed/reviews_clasificadas_subjetividad.csv"):
    """
    Guarda los resultados clasificados en un archivo CSV.
    Si hay datos existentes, los combina inteligentemente.
    
    Args:
        df_clasificado (pandas.DataFrame): DataFrame con las nuevas clasificaciones
        df_existente (pandas.DataFrame): DataFrame con clasificaciones previas (opcional)
        ruta_salida (str): Ruta donde guardar el archivo
        
    Returns:
        bool: True si el guardado fue exitoso, False en caso contrario
    """
    if df_clasificado is None:
        if df_existente is not None:
            print("ℹ️ No hay nuevas clasificaciones, manteniendo datos existentes")
            return True
        else:
            print("❌ No hay datos para guardar")
            return False
    
    try:
        # Si hay datos existentes, combinar inteligentemente
        if df_existente is not None and len(df_existente) > 0:
            # Eliminar reseñas duplicadas si existen (mantener las nuevas clasificaciones)
            df_existente = df_existente[~df_existente['TituloReview'].isin(df_clasificado['TituloReview'])]
            
            # Combinar dataframes
            df_final = pd.concat([df_existente, df_clasificado], ignore_index=True)
            df_final = df_final.drop_duplicates(subset=['TituloReview'], keep='last')
            
        else:
            df_final = df_clasificado.copy()
        
        # Guardar el dataset combinado
        df_final.to_csv(ruta_salida, index=False, encoding='utf-8')
        
        print(f"📄 Archivo contiene {len(df_final)} reseñas clasificadas")
        
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
        print("❌ No hay datos para resumir")
        return
    
    print("🎯 RESUMEN FINAL DEL PROCESO DE CLASIFICACIÓN")
    print("=" * 60)
    
    # Estadísticas generales
    total_reviews = len(df_clean)
    conteo = df_clean['Clasificacion_Subjetividad'].value_counts()
    
    print()
    
    print("🏷️ RESULTADOS DE CLASIFICACIÓN:")
    for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
        if categoria in conteo:
            count = conteo[categoria]
            percentage = (count / total_reviews) * 100
            print(f"   {categoria:10}: {count:4d} reseñas ({percentage:5.1f}%)")
    print()
    
    # Insights principales
    categoria_predominante = conteo.index[0]
    porcentaje_predominante = (conteo.iloc[0] / total_reviews) * 100
    
    print("🔍 INSIGHTS PRINCIPALES:")
    print(f"   • La categoría predominante es '{categoria_predominante}' con {porcentaje_predominante:.1f}% del total")
    
    if categoria_predominante == 'Subjetiva':
        print("   • Las reseñas turísticas tienden a ser principalmente subjetivas (opiniones y sentimientos)")
    elif categoria_predominante == 'Objetiva':
        print("   • Las reseñas turísticas tienden a ser principalmente objetivas (hechos verificables)")
    else:
        print("   • Las reseñas turísticas tienden a combinar hechos con opiniones (mixtas)")
    
    # Comparación por ciudad
    print("\n🌎 COMPARACIÓN POR CIUDAD:")
    for ciudad in df_clean['Ciudad'].unique():
        df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
        conteo_ciudad = df_ciudad['Clasificacion_Subjetividad'].value_counts()
        categoria_ciudad = conteo_ciudad.index[0]
        porcentaje_ciudad = (conteo_ciudad.iloc[0] / len(df_ciudad)) * 100
        
        print(f"   📍 {ciudad}: Predomina '{categoria_ciudad}' ({porcentaje_ciudad:.1f}%)")
    
    print("🎉 ¡Clasificación completada!")
