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
            print("🔄 Combinando nuevas clasificaciones con datos existentes...")
            
            # Crear copia de datos existentes
            df_final = df_existente.copy()
            
            # Agregar nuevas clasificaciones
            df_final = pd.concat([df_final, df_clasificado], ignore_index=True)
            
            # Eliminar duplicados basados en TituloReview, manteniendo la última clasificación
            df_final = df_final.drop_duplicates(subset=['TituloReview'], keep='last')
            
            print(f"📊 Datos combinados: {len(df_existente)} existentes + {len(df_clasificado)} nuevas = {len(df_final)} total")
        else:
            df_final = df_clasificado.copy()
        
        # Guardar el dataset combinado
        df_final.to_csv(ruta_salida, index=False, encoding='utf-8')
        
        print(f"✅ Resultados guardados en: {ruta_salida}")
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
    
    print(f"📊 Total de reseñas procesadas: {total_reviews}")
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
    
    print("\n✅ Proceso de clasificación completado exitosamente")


def generar_reporte_completo(df_clasificado, df_clean, ruta_reporte="../data/processed/reporte_clasificacion.txt"):
    """
    Genera un reporte completo del proceso de clasificación en formato texto.
    
    Args:
        df_clasificado (pandas.DataFrame): DataFrame con todas las clasificaciones
        df_clean (pandas.DataFrame): DataFrame limpio sin errores
        ruta_reporte (str): Ruta donde guardar el reporte
        
    Returns:
        bool: True si el reporte se generó exitosamente
    """
    if df_clasificado is None or df_clean is None:
        print("❌ No hay datos suficientes para generar el reporte")
        return False
    
    try:
        with open(ruta_reporte, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE CLASIFICACIÓN DE SUBJETIVIDAD\n")
            f.write("=" * 50 + "\n\n")
            
            # Información general
            f.write(f"Total de reseñas procesadas: {len(df_clasificado)}\n")
            f.write(f"Reseñas clasificadas exitosamente: {len(df_clean)}\n")
            f.write(f"Reseñas con errores: {len(df_clasificado) - len(df_clean)}\n\n")
            
            # Distribución general
            conteo = df_clean['Clasificacion_Subjetividad'].value_counts()
            f.write("DISTRIBUCIÓN GENERAL:\n")
            for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
                if categoria in conteo:
                    count = conteo[categoria]
                    pct = (count / len(df_clean)) * 100
                    f.write(f"  {categoria}: {count} reseñas ({pct:.1f}%)\n")
            f.write("\n")
            
            # Distribución por ciudad
            f.write("DISTRIBUCIÓN POR CIUDAD:\n")
            for ciudad in df_clean['Ciudad'].unique():
                f.write(f"\n{ciudad}:\n")
                df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
                conteo_ciudad = df_ciudad['Clasificacion_Subjetividad'].value_counts()
                
                for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
                    if categoria in conteo_ciudad:
                        count = conteo_ciudad[categoria]
                        pct = (count / len(df_ciudad)) * 100
                        f.write(f"  {categoria}: {count} reseñas ({pct:.1f}%)\n")
            
            # Ejemplos de cada categoría
            f.write("\n\nEJEMPLOS POR CATEGORÍA:\n")
            for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
                f.write(f"\n{categoria.upper()}:\n")
                ejemplos = df_clean[df_clean['Clasificacion_Subjetividad'] == categoria]['TituloReview'].head(5)
                for i, ejemplo in enumerate(ejemplos, 1):
                    f.write(f"  {i}. {ejemplo}\n")
        
        print(f"✅ Reporte completo guardado en: {ruta_reporte}")
        return True
        
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")
        return False


def exportar_estadisticas_json(df_clean, ruta_json="../data/processed/estadisticas_clasificacion.json"):
    """
    Exporta las estadísticas de clasificación en formato JSON.
    
    Args:
        df_clean (pandas.DataFrame): DataFrame limpio con clasificaciones
        ruta_json (str): Ruta donde guardar el archivo JSON
        
    Returns:
        bool: True si la exportación fue exitosa
    """
    import json
    from datetime import datetime
    
    if df_clean is None:
        print("❌ No hay datos para exportar")
        return False
    
    try:
        # Generar estadísticas
        conteo_general = df_clean['Clasificacion_Subjetividad'].value_counts()
        porcentaje_general = df_clean['Clasificacion_Subjetividad'].value_counts(normalize=True) * 100
        
        estadisticas = {
            'timestamp': datetime.now().isoformat(),
            'total_reviews': len(df_clean),
            'distribucion_general': {
                'conteo': conteo_general.to_dict(),
                'porcentaje': porcentaje_general.to_dict()
            },
            'categoria_predominante': conteo_general.index[0],
            'distribucion_por_ciudad': {}
        }
        
        # Estadísticas por ciudad
        for ciudad in df_clean['Ciudad'].unique():
            df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
            conteo_ciudad = df_ciudad['Clasificacion_Subjetividad'].value_counts()
            porcentaje_ciudad = df_ciudad['Clasificacion_Subjetividad'].value_counts(normalize=True) * 100
            
            estadisticas['distribucion_por_ciudad'][ciudad] = {
                'total': len(df_ciudad),
                'conteo': conteo_ciudad.to_dict(),
                'porcentaje': porcentaje_ciudad.to_dict(),
                'categoria_predominante': conteo_ciudad.index[0]
            }
        
        # Guardar en JSON
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(estadisticas, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Estadísticas exportadas a: {ruta_json}")
        return True
        
    except Exception as e:
        print(f"❌ Error al exportar estadísticas: {e}")
        return False
