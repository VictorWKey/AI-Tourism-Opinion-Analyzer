"""
Módulo para análisis estadístico de resultados de clasificación.
"""


def analizar_resultados(df_clasificado):
    """
    Analiza los resultados de la clasificación y genera estadísticas.
    
    Args:
        df_clasificado (pandas.DataFrame): DataFrame con las clasificaciones
        
    Returns:
        pandas.DataFrame: DataFrame limpio sin errores para análisis adicional
    """
    if df_clasificado is None:
        print("❌ No hay datos clasificados para analizar")
        return None
    
    print("📊 ANÁLISIS DE RESULTADOS DE CLASIFICACIÓN")
    print("=" * 50)
    
    # Filtrar errores para el análisis
    df_clean = df_clasificado[df_clasificado['Clasificacion_Subjetividad'] != 'Error'].copy()
    
    if len(df_clean) == 0:
        print("❌ No hay clasificaciones válidas para analizar")
        return None
    
    print(f"📈 Total de reseñas analizadas: {len(df_clean)}")
    print(f"❌ Reseñas con errores: {len(df_clasificado) - len(df_clean)}")
    print()
    
    # Conteo general de clasificaciones
    conteo_general = df_clean['Clasificacion_Subjetividad'].value_counts()
    porcentaje_general = df_clean['Clasificacion_Subjetividad'].value_counts(normalize=True) * 100
    
    print("🏷️ DISTRIBUCIÓN GENERAL DE CLASIFICACIONES:")
    for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
        if categoria in conteo_general:
            count = conteo_general[categoria]
            pct = porcentaje_general[categoria]
            print(f"   {categoria:10}: {count:4d} reseñas ({pct:5.1f}%)")
    print()
    
    # Análisis por ciudad
    print("🌎 DISTRIBUCIÓN POR CIUDAD:")
    for ciudad in df_clean['Ciudad'].unique():
        print(f"\n  📍 {ciudad}:")
        df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
        conteo_ciudad = df_ciudad['Clasificacion_Subjetividad'].value_counts()
        
        for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
            if categoria in conteo_ciudad:
                count = conteo_ciudad[categoria]
                pct = (count / len(df_ciudad)) * 100
                print(f"     {categoria:10}: {count:4d} reseñas ({pct:5.1f}%)")
    
    return df_clean


def mostrar_opiniones_por_categoria(df_clasificado):
    """
    Muestra las opiniones clasificadas por cada categoría para revisión manual.
    
    Args:
        df_clasificado (pandas.DataFrame): DataFrame con las clasificaciones
    """
    if df_clasificado is None or 'Clasificacion_Subjetividad' not in df_clasificado.columns:
        print("❌ No hay datos clasificados para mostrar")
        return

    print("📋 Opiniones clasificadas por categoría:")
    print("=" * 50)

    categorias = ['Objetiva', 'Subjetiva', 'Mixta']
    for categoria in categorias:
        print(f"\n🏷️ {categoria}:")
        opiniones = df_clasificado[df_clasificado['Clasificacion_Subjetividad'] == categoria]['TituloReview']
        if opiniones.empty:
            print("   (No hay opiniones en esta categoría)")
        else:
            for idx, opinion in enumerate(opiniones, start=1):
                print(f"   {idx}. {opinion}")


def obtener_estadisticas_resumidas(df_clean):
    """
    Obtiene estadísticas resumidas de los resultados de clasificación.
    
    Args:
        df_clean (pandas.DataFrame): DataFrame limpio con clasificaciones
        
    Returns:
        dict: Diccionario con estadísticas resumidas
    """
    if df_clean is None or len(df_clean) == 0:
        return None
    
    estadisticas = {
        'total_reviews': len(df_clean),
        'conteo_general': df_clean['Clasificacion_Subjetividad'].value_counts().to_dict(),
        'porcentaje_general': (df_clean['Clasificacion_Subjetividad'].value_counts(normalize=True) * 100).to_dict(),
        'categoria_predominante': df_clean['Clasificacion_Subjetividad'].value_counts().index[0],
        'conteo_por_ciudad': {}
    }
    
    # Estadísticas por ciudad
    for ciudad in df_clean['Ciudad'].unique():
        df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
        estadisticas['conteo_por_ciudad'][ciudad] = {
            'total': len(df_ciudad),
            'conteo': df_ciudad['Clasificacion_Subjetividad'].value_counts().to_dict(),
            'categoria_predominante': df_ciudad['Clasificacion_Subjetividad'].value_counts().index[0]
        }
    
    return estadisticas
