"""
Módulo para an    # Filtrar errores para el análisis
    df_clean = df_clasificado[df_clasificado    estadisticas = {
        'total_reviews': len(df_clean),
        'conteo_general': df_clean['SubjetividadConLLM'].value_counts().to_dict(),
        'porcentaje_general': (df_clean['SubjetividadConLLM'].value_counts(normalize=True) * 100).to_dict(),
        'categoria_predominante': df_clean['SubjetividadConLLM'].value_counts().index[0],
        'conteo_por_ciudad': {}
    }
    
    # Estadísticas por ciudad
    for ciudad in df_clean['Ciudad'].unique():
        df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
        estadisticas['conteo_por_ciudad'][ciudad] = {
            'total': len(df_ciudad),
            'conteo': df_ciudad['SubjetividadConLLM'].value_counts().to_dict(),
            'categoria_predominante': df_ciudad['SubjetividadConLLM'].value_counts().index[0]
        }nLLM'] != 'Error'].copy()
    
    if len(df_clean) == 0:
        return None
    
    print(f"\n📊 Análisis de {len(df_clean)} reseñas clasificadas")
    
    # Conteo general de clasificaciones
    conteo_general = df_clean['SubjetividadConLLM'].value_counts()adístico de resultados de clasificación.
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
        return None
    
    # Filtrar errores para el análisis
    df_clean = df_clasificado[df_clasificado['SubjetividadConLLM'] != 'Error'].copy()
    
    if len(df_clean) == 0:
        return None
    
    print(f"\n� Análisis de {len(df_clean)} reseñas clasificadas")
    
    # Conteo general de clasificaciones
    conteo_general = df_clean['SubjetividadConLLM'].value_counts()
    
    print("\n🏷️ DISTRIBUCIÓN GENERAL:")
    for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
        if categoria in conteo_general:
            count = conteo_general[categoria]
            pct = (count / len(df_clean)) * 100
            print(f"   {categoria}: {count} reseñas ({pct:.1f}%)")
    
    # Análisis por ciudad
    print("\n🌎 POR CIUDAD:")
    for ciudad in df_clean['Ciudad'].unique():
        df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
        conteo_ciudad = df_ciudad['SubjetividadConLLM'].value_counts()
        
        print(f"\n  📍 {ciudad}:")
        for categoria in ['Objetiva', 'Subjetiva', 'Mixta']:
            if categoria in conteo_ciudad:
                count = conteo_ciudad[categoria]
                pct = (count / len(df_ciudad)) * 100
                print(f"     {categoria}: {count} reseñas ({pct:.1f}%)")
    
    return df_clean


def mostrar_opiniones_por_categoria(df_clasificado):
    """
    Muestra las opiniones clasificadas por cada categoría para revisión manual.
    
    Args:
        df_clasificado (pandas.DataFrame): DataFrame con las clasificaciones
    """
    if df_clasificado is None or 'SubjetividadConLLM' not in df_clasificado.columns:
        return

    print("\n📋 Ejemplos por categoría:")
    print("=" * 30)

    categorias = ['Objetiva', 'Subjetiva', 'Mixta']
    for categoria in categorias:
        print(f"\n🏷️ {categoria}:")
        opiniones = df_clasificado[df_clasificado['SubjetividadConLLM'] == categoria]['TituloReview']
        if opiniones.empty:
            print("   (No hay opiniones en esta categoría)")
        else:
            # Mostrar solo las primeras 3 para evitar spam
            for idx, opinion in enumerate(opiniones.head(3), start=1):
                print(f"   {idx}. {opinion}")
            if len(opiniones) > 3:
                print(f"   ... y {len(opiniones) - 3} más")


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
        'conteo_general': df_clean['SubjetividadConLLM'].value_counts().to_dict(),
        'porcentaje_general': (df_clean['SubjetividadConLLM'].value_counts(normalize=True) * 100).to_dict(),
        'categoria_predominante': df_clean['SubjetividadConLLM'].value_counts().index[0],
        'conteo_por_ciudad': {}
    }
    
    # Estadísticas por ciudad
    for ciudad in df_clean['Ciudad'].unique():
        df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
        estadisticas['conteo_por_ciudad'][ciudad] = {
            'total': len(df_ciudad),
            'conteo': df_ciudad['SubjetividadConLLM'].value_counts().to_dict(),
            'categoria_predominante': df_ciudad['SubjetividadConLLM'].value_counts().index[0]
        }
    
    return estadisticas
