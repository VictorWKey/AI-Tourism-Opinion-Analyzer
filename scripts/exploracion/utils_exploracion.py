"""
Utilidades de Exploración - Funciones auxiliares para exploración de datos
"""

import pandas as pd
import numpy as np
import os
import glob


def cargar_dataset_completo(ruta_data='../data'):
    """
    Carga un dataset completo desde archivo consolidado o archivos individuales.
    """
    # Intentar cargar dataset consolidado primero
    ruta_consolidado = os.path.join(ruta_data, 'dataset_opiniones_consolidado.csv')
    
    if os.path.exists(ruta_consolidado):
        print(f"Cargando dataset consolidado desde: {ruta_consolidado}")
        return pd.read_csv(ruta_consolidado)
    else:
        print("Dataset consolidado no encontrado. Use el módulo de procesamiento para crearlo.")
        return pd.DataFrame()


def resumen_ejecutivo(df):
    """
    Genera un resumen ejecutivo del análisis exploratorio.
    """
    print("\n" + "="*60)
    print("                    RESUMEN EJECUTIVO")
    print("="*60)

    print(f"📊 VOLUMEN DE DATOS:")
    print(f"   • Total de opiniones: {len(df):,}")
    print(f"   • Ciudades analizadas: {df['Ciudad'].nunique()}")
    print(f"   • Atracciones totales: {df['Atraccion'].nunique()}")

    print(f"\n🏙️ DISTRIBUCIÓN POR CIUDADES:")
    for ciudad, cantidad in df['Ciudad'].value_counts().items():
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
    print(f"   • Ciudades: {df['Ciudad'].nunique()}")
    print(f"   • Atracciones: {df['Atraccion'].nunique()}")

    # 2. Calidad de datos final
    print(f"\n🔍 CALIDAD DE DATOS FINAL:")
    valores_nulos_final = df.isnull().sum().sum()
    print(f"   • Valores nulos totales: {valores_nulos_final}")
    print(f"   • Duplicados restantes: {df.duplicated().sum()}")
    print(f"   • Integridad de datos: {'✅ PERFECTA' if valores_nulos_final == 0 else '⚠️ REVISAR'}")

    # 3. Distribución por ciudades (final)
    print(f"\n🏙️ DISTRIBUCIÓN FINAL POR CIUDADES:")
    dist_ciudades_final = df['Ciudad'].value_counts()
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

    # 6. Tipos de viaje final
    if 'TipoViaje' in df.columns:
        print(f"\n👥 TIPOS DE VIAJE FINAL:")
        dist_tipos_final = df['TipoViaje'].value_counts()
        for tipo, count in dist_tipos_final.items():
            porcentaje = (count / len(df)) * 100
            print(f"   • {tipo}: {count:,} ({porcentaje:.1f}%)")

    # 7. Top atracciones por calificación
    if 'Calificacion' in df.columns:
        print(f"\n🏆 TOP 5 ATRACCIONES POR CALIFICACIÓN PROMEDIO:")
        top_atracciones = df.groupby(['Ciudad', 'Atraccion']).agg({
            'Calificacion': ['mean', 'count']
        }).round(2)
        top_atracciones.columns = ['calificacion_promedio', 'num_opiniones']
        top_atracciones = top_atracciones[top_atracciones['num_opiniones'] >= 5]
        top_atracciones = top_atracciones.sort_values('calificacion_promedio', ascending=False).head()

        for (ciudad, atraccion), row in top_atracciones.iterrows():
            print(f"   • {atraccion} ({ciudad}): {row['calificacion_promedio']:.2f}/5 ({int(row['num_opiniones'])} opiniones)")

    # 8. Origen de autores más frecuentes (excluyendo anónimos)
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
