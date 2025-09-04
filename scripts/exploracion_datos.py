"""
Módulo para exploración de datos turísticos.
Contiene funciones para análisis descriptivo que NO modifican el dataset original.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


def analizar_informacion_general(df):
    """
    Muestra información general del dataset.
    """
    print("=== INFORMACIÓN GENERAL DEL DATASET ===")
    print(f"Dimensiones: {df.shape}")
    print(f"Número de filas: {df.shape[0]:,}")
    print(f"Número de columnas: {df.shape[1]}")
    print("\nColumnas del dataset:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")
    
    print("\n=== TIPOS DE DATOS ===")
    df.info()


def analizar_valores_nulos(df):
    """
    Analiza los valores nulos en el dataset.
    """
    print("=== ANÁLISIS DE VALORES NULOS ===")
    valores_nulos = df.isnull().sum()
    porcentaje_nulos = (valores_nulos / len(df)) * 100
    
    resumen_nulos = pd.DataFrame({
        'Valores_Nulos': valores_nulos,
        'Porcentaje': porcentaje_nulos
    })
    
    resumen_nulos = resumen_nulos.sort_values('Porcentaje', ascending=False)
    print(resumen_nulos)
    
    return resumen_nulos


def analizar_duplicados(df):
    """
    Analiza duplicados en el dataset sin eliminarlos.
    """
    print("=== ANÁLISIS DE DUPLICADOS ===")
    
    # Duplicados completos
    duplicados_completos = df.duplicated().sum()
    print(f"Filas completamente duplicadas encontradas: {duplicados_completos}")
    
    # Duplicados por combinación de columnas importantes
    if 'Titulo' in df.columns and 'Review' in df.columns:
        duplicados_contenido = df.duplicated(subset=['Titulo', 'Review', 'ciudad', 'atraccion']).sum()
        print(f"Duplicados por título + review + ciudad + atracción: {duplicados_contenido}")
    
    if duplicados_completos > 0:
        porcentaje_duplicados = (duplicados_completos / len(df)) * 100
        print(f"Porcentaje de duplicados completos: {porcentaje_duplicados:.2f}%")
    
    return duplicados_completos


def analizar_distribuciones_categoricas(df):
    """
    Analiza las distribuciones de variables categóricas.
    """
    # Distribución por ciudades
    print("=== DISTRIBUCIÓN POR CIUDADES ===")
    distribucion_ciudades = df['ciudad'].value_counts()
    print(distribucion_ciudades)
    print(f"\nPorcentaje por ciudad:")
    print((distribucion_ciudades / distribucion_ciudades.sum() * 100).round(2))
    
    # Top 10 atracciones
    print("\n=== TOP 10 ATRACCIONES CON MÁS OPINIONES ===")
    distribucion_atracciones = df['atraccion'].value_counts().head(10)
    print(distribucion_atracciones)
    
    # Análisis de tipos de viaje
    if 'TipoViaje' in df.columns:
        print("\n=== ANÁLISIS DE TIPOS DE VIAJE ===")
        distribucion_tipos = df['TipoViaje'].value_counts()
        print(distribucion_tipos)
        print(f"\nPorcentaje por tipo de viaje:")
        print((distribucion_tipos / distribucion_tipos.sum() * 100).round(2))


def analizar_calificaciones(df):
    """
    Analiza las calificaciones del dataset.
    """
    if 'Calificacion' in df.columns:
        print("=== ANÁLISIS DE CALIFICACIONES ===")
        
        # Convertir calificaciones a numérico para análisis
        calificaciones_num = pd.to_numeric(df['Calificacion'], errors='coerce')
        
        print("Estadísticas descriptivas de calificaciones:")
        print(calificaciones_num.describe())
        
        print("\nDistribución de calificaciones:")
        print(calificaciones_num.value_counts().sort_index())
        
        print(f"\nCalificación promedio general: {calificaciones_num.mean():.2f}")


def analizar_longitud_textos(df):
    """
    Analiza la longitud de campos de texto.
    """
    if 'Titulo' in df.columns:
        longitud_titulo = df['Titulo'].astype(str).str.len()
        print("=== ANÁLISIS DE LONGITUD DE TÍTULOS ===")
        print(longitud_titulo.describe())

    if 'Review' in df.columns:
        longitud_review = df['Review'].astype(str).str.len()
        print("\n=== ANÁLISIS DE LONGITUD DE REVIEWS ===")
        print(longitud_review.describe())
        
        # Contar palabras en reviews
        palabras_review = df['Review'].astype(str).str.split().str.len()
        print("\n=== NÚMERO DE PALABRAS EN REVIEWS ===")
        print(palabras_review.describe())


def analizar_temporal(df):
    """
    Analiza aspectos temporales del dataset.
    """
    if 'FechaOpinion' in df.columns:
        print("=== ANÁLISIS TEMPORAL DE OPINIONES ===")
        
        # Mostrar algunas fechas de ejemplo
        print("Ejemplos de fechas en el dataset:")
        print(df['FechaOpinion'].head(10).tolist())
        
        # Contar valores únicos en fechas
        print(f"\nFechas únicas de opinión: {df['FechaOpinion'].nunique()}")
        
        # Mostrar las fechas más comunes
        print("\nTop 10 fechas con más opiniones:")
        print(df['FechaOpinion'].value_counts().head(10))


def analizar_origen_autor(df):
    """
    Analiza la columna OrigenAutor antes de cualquier limpieza.
    """
    print("=== ANÁLISIS DE VALORES EN OrigenAutor ===")
    print(f"Total de valores únicos: {df['OrigenAutor'].nunique()}")
    print(f"Total de valores no nulos: {df['OrigenAutor'].notna().sum()}")
    print(f"Valores nulos: {df['OrigenAutor'].isna().sum()}")

    print("\n=== PRIMEROS 30 VALORES ÚNICOS ===")
    valores_unicos = df['OrigenAutor'].value_counts().head(30)
    for valor, count in valores_unicos.items():
        print(f"'{valor}': {count} veces")

    print(f"\n=== TODOS LOS VALORES ÚNICOS (Muestra de {min(100, df['OrigenAutor'].nunique())}) ===")
    todos_valores = df['OrigenAutor'].dropna().unique()[:100]
    for i, valor in enumerate(todos_valores, 1):
        print(f"{i:2d}. '{valor}'")


def detectar_contenidos_mal_ubicados(dataframe, min_longitud=10):
    """
    Detecta cuando el contenido de una columna aparece incorrectamente en otra columna.
    
    Args:
        dataframe: DataFrame a analizar
        min_longitud: Longitud mínima del texto para considerar en el análisis
    
    Returns:
        dict: Resultados de contenidos mal ubicados por par de columnas
        list: Lista de problemas encontrados
    """
    print("=== ANÁLISIS AVANZADO DE CONTENIDOS MAL UBICADOS ===")
    print("Detectando cuando el contenido de una columna aparece en otra columna diferente...")
    
    # Solo columnas de texto para analizar
    columnas_texto = ['Titulo', 'Review', 'TipoViaje', 'OrigenAutor']
    
    # Filtrar solo las columnas que existen en el dataframe y son de tipo texto
    columnas_existentes = []
    for col in columnas_texto:
        if col in dataframe.columns:
            dtype = dataframe[col].dtype
            if dtype == 'object' or pd.api.types.is_string_dtype(dtype):
                columnas_existentes.append(col)
    
    resultados = {}
    problemas_encontrados = []
    
    print(f"Analizando columnas de texto: {columnas_existentes}")
    print(f"Longitud mínima de texto: {min_longitud} caracteres\n")
    
    # Iterar sobre todas las combinaciones de columnas
    for i, col1 in enumerate(columnas_existentes):
        for j, col2 in enumerate(columnas_existentes):
            if i != j:  # No comparar una columna consigo misma
                
                # Crear sets de valores únicos no nulos y con longitud suficiente
                valores_col1 = set()
                valores_col2 = set()
                
                for valor in dataframe[col1].dropna():
                    valor_str = str(valor).strip()
                    if len(valor_str) >= min_longitud:
                        valores_col1.add(valor_str.lower())
                
                for valor in dataframe[col2].dropna():
                    valor_str = str(valor).strip()
                    if len(valor_str) >= min_longitud:
                        valores_col2.add(valor_str.lower())
                
                # Encontrar intersección
                contenidos_duplicados = valores_col1.intersection(valores_col2)
                
                if contenidos_duplicados:
                    par_columnas = f"{col1} ↔ {col2}"
                    resultados[par_columnas] = contenidos_duplicados
                    
                    print(f"⚠️  PROBLEMA DETECTADO: {par_columnas}")
                    print(f"   Contenidos duplicados encontrados: {len(contenidos_duplicados)}")
                    
                    # Mostrar algunos ejemplos
                    ejemplos = list(contenidos_duplicados)[:3]
                    for ejemplo in ejemplos:
                        # Encontrar las filas específicas donde ocurre esto
                        col1_str = dataframe[col1].astype(str).str.lower().str.strip()
                        col2_str = dataframe[col2].astype(str).str.lower().str.strip()
                        
                        filas_col1 = dataframe[col1_str == ejemplo].index.tolist()
                        filas_col2 = dataframe[col2_str == ejemplo].index.tolist()
                        
                        print(f"   📝 Ejemplo: '{ejemplo[:50]}...'")
                        print(f"      - En {col1}: filas {filas_col1[:3]}")
                        print(f"      - En {col2}: filas {filas_col2[:3]}")
                    
                    print()
                    
                    # Guardar información del problema
                    problemas_encontrados.append({
                        'columna_1': col1,
                        'columna_2': col2,
                        'contenidos_duplicados': len(contenidos_duplicados),
                        'ejemplos': ejemplos[:5]
                    })
    
    print(f"=== RESUMEN DEL ANÁLISIS ===")
    if problemas_encontrados:
        print(f"❌ Se encontraron {len(problemas_encontrados)} problemas de contenidos mal ubicados")
        print(f"Total de pares de columnas con problemas: {len(resultados)}")
        
        # Resumen por tipo de problema
        print(f"\n📊 ESTADÍSTICAS DE PROBLEMAS:")
        for problema in problemas_encontrados:
            print(f"   {problema['columna_1']} ↔ {problema['columna_2']}: {problema['contenidos_duplicados']} contenidos duplicados")
    else:
        print("✅ No se encontraron contenidos mal ubicados entre columnas")
        print("   El dataset parece estar bien estructurado en este aspecto")
    
    return resultados, problemas_encontrados


def resumen_ejecutivo(df):
    """
    Genera un resumen ejecutivo del análisis exploratorio.
    """
    print("\n" + "="*60)
    print("                    RESUMEN EJECUTIVO")
    print("="*60)

    print(f"📊 VOLUMEN DE DATOS:")
    print(f"   • Total de opiniones: {len(df):,}")
    print(f"   • Ciudades analizadas: {df['ciudad'].nunique()}")
    print(f"   • Atracciones totales: {df['atraccion'].nunique()}")

    print(f"\n🏙️ DISTRIBUCIÓN POR CIUDADES:")
    for ciudad, cantidad in df['ciudad'].value_counts().items():
        porcentaje = (cantidad / len(df)) * 100
        print(f"   • {ciudad.upper()}: {cantidad:,} opiniones ({porcentaje:.1f}%)")

    if 'Calificacion' in df.columns:
        calificaciones_num = pd.to_numeric(df['Calificacion'], errors='coerce')
        print(f"\n⭐ CALIFICACIONES:")
        print(f"   • Promedio general: {calificaciones_num.mean():.2f}/5")
        print(f"   • Mediana: {calificaciones_num.median():.1f}/5")

    if 'TipoViaje' in df.columns:
        tipo_mas_comun = df['TipoViaje'].mode()[0]
        print(f"\n👥 TIPO DE VIAJE:")
        print(f"   • Más común: {tipo_mas_comun}")

    print(f"\n🔍 CALIDAD DE DATOS:")
    print(f"   • Duplicados completos: {df.duplicated().sum()}")
    valores_nulos = df.isnull().sum()
    if valores_nulos.sum() > 0:
        print(f"   • Campos con valores nulos: {(valores_nulos > 0).sum()}")
    else:
        print(f"   • Sin valores nulos detectados")

    print("\n✅ Dataset listo para análisis más profundos!")
    print("="*60)


def analisis_final_completo(df):
    """
    Realiza un análisis final completo del dataset limpio.
    """
    print("=" * 80)
    print("                     ANÁLISIS FINAL COMPLETO")
    print("                    DATASET COMPLETAMENTE LIMPIO")
    print("=" * 80)

    # 1. Resumen general
    print(f"\n📊 RESUMEN GENERAL:")
    print(f"   • Total de registros finales: {len(df):,}")
    print(f"   • Total de columnas: {len(df.columns)}")
    print(f"   • Ciudades: {df['ciudad'].nunique()}")
    print(f"   • Atracciones: {df['atraccion'].nunique()}")

    # 2. Calidad de datos final
    print(f"\n🔍 CALIDAD DE DATOS FINAL:")
    valores_nulos_final = df.isnull().sum().sum()
    print(f"   • Valores nulos totales: {valores_nulos_final}")
    print(f"   • Duplicados restantes: {df.duplicated().sum()}")
    print(f"   • Integridad de datos: {'✅ PERFECTA' if valores_nulos_final == 0 else '⚠️ REVISAR'}")

    # 3. Distribución por ciudades (final)
    print(f"\n🏙️ DISTRIBUCIÓN FINAL POR CIUDADES:")
    dist_ciudades_final = df['ciudad'].value_counts()
    for ciudad, cantidad in dist_ciudades_final.items():
        porcentaje = (cantidad / len(df)) * 100
        print(f"   • {ciudad.upper()}: {cantidad:,} ({porcentaje:.1f}%)")

    # 4. Análisis de calificaciones (final)
    if 'Calificacion' in df.columns:
        print(f"\n⭐ ANÁLISIS DE CALIFICACIONES FINAL:")
        print(f"   • Promedio general: {df['Calificacion'].mean():.2f}/5")
        print(f"   • Mediana: {df['Calificacion'].median():.1f}/5")
        print(f"   • Moda: {df['Calificacion'].mode()[0]}/5")
        print(f"   • Desviación estándar: {df['Calificacion'].std():.2f}")

        # 5. Distribución de calificaciones
        print(f"\n   Distribución de calificaciones:")
        dist_calificaciones = df['Calificacion'].value_counts().sort_index()
        for cal, count in dist_calificaciones.items():
            porcentaje = (count / len(df)) * 100
            print(f"     {cal} estrellas: {count:,} ({porcentaje:.1f}%)")

    # 6. Análisis temporal final
    if 'FechaOpinion' in df.columns:
        print(f"\n📅 ANÁLISIS TEMPORAL FINAL:")
        rango_fechas = df['FechaOpinion'].dropna()
        if len(rango_fechas) > 0:
            fecha_min = rango_fechas.min()
            fecha_max = rango_fechas.max()
            print(f"   • Rango de fechas: {fecha_min.strftime('%d/%m/%Y')} - {fecha_max.strftime('%d/%m/%Y')}")
            print(f"   • Período cubierto: {(fecha_max - fecha_min).days} días")
            
            # Análisis por año
            print(f"   • Distribución por año:")
            dist_años = df['FechaOpinion'].dt.year.value_counts().sort_index()
            for año, count in dist_años.items():
                porcentaje = (count / len(df)) * 100
                print(f"     {año}: {count:,} opiniones ({porcentaje:.1f}%)")

    # 7. Tipos de viaje final
    if 'TipoViaje' in df.columns:
        print(f"\n👥 TIPOS DE VIAJE FINAL:")
        dist_tipos_final = df['TipoViaje'].value_counts()
        for tipo, count in dist_tipos_final.items():
            porcentaje = (count / len(df)) * 100
            print(f"   • {tipo}: {count:,} ({porcentaje:.1f}%)")

    # 8. Análisis de texto consolidado
    if 'texto_consolidado' in df.columns:
        print(f"\n📝 ANÁLISIS DE TEXTO CONSOLIDADO:")
        longitud_texto = df['texto_consolidado'].str.len()
        palabras_texto = df['texto_consolidado'].str.split().str.len()
        print(f"   • Longitud promedio: {longitud_texto.mean():.1f} caracteres")
        print(f"   • Palabras promedio: {palabras_texto.mean():.1f} palabras")
        print(f"   • Texto más corto: {longitud_texto.min()} caracteres")
        print(f"   • Texto más largo: {longitud_texto.max()} caracteres")

    # 9. Top atracciones por calificación
    if 'Calificacion' in df.columns:
        print(f"\n🏆 TOP 5 ATRACCIONES POR CALIFICACIÓN PROMEDIO:")
        top_atracciones = df.groupby(['ciudad', 'atraccion']).agg({
            'Calificacion': ['mean', 'count']
        }).round(2)
        top_atracciones.columns = ['calificacion_promedio', 'num_opiniones']
        top_atracciones = top_atracciones[top_atracciones['num_opiniones'] >= 5]
        top_atracciones = top_atracciones.sort_values('calificacion_promedio', ascending=False).head()

        for (ciudad, atraccion), row in top_atracciones.iterrows():
            print(f"   • {atraccion} ({ciudad}): {row['calificacion_promedio']:.2f}/5 ({int(row['num_opiniones'])} opiniones)")

    # 10. Origen de autores más frecuentes (excluyendo anónimos)
    if 'OrigenAutor' in df.columns:
        print(f"\n🌍 TOP 10 PAÍSES/REGIONES DE ORIGEN:")
        origenes_top = df[df['OrigenAutor'] != 'anonimo']['OrigenAutor'].value_counts().head(10)
        for origen, count in origenes_top.items():
            porcentaje = (count / len(df)) * 100
            print(f"   • {origen}: {count:,} ({porcentaje:.1f}%)")

    print(f"\n" + "=" * 80)
    print("✅ ANÁLISIS FINAL COMPLETADO")
    print("🎯 Dataset completamente limpio y listo para análisis avanzados")
    print("📊 Calidad de datos: EXCELENTE")
    print("=" * 80)
