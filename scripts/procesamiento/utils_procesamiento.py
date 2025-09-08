"""
Utilidades de Procesamiento - Funciones auxiliares y pipeline principal
"""

import pandas as pd
import os
from .cargador_datos import CargadorDatos
from .limpieza_datos import LimpiadorDatos
from .transformador_datos import TransformadorDatos
from .validador_datos import ValidadorDatos


def verificar_datasets_creados(directorio_ciudades, df_original):
    """
    Verifica los datasets por ciudad creados y genera estadísticas.
    
    Args:
        directorio_ciudades (str): Directorio donde están los datasets por ciudad
        df_original (DataFrame): Dataset original para comparar
        
    Returns:
        list: Lista de diccionarios con información de cada dataset creado
    """
    if not os.path.exists(directorio_ciudades):
        print(f"❌ Directorio no encontrado: {directorio_ciudades}")
        return []
    
    archivos_creados = [f for f in os.listdir(directorio_ciudades) if f.endswith('.csv')]
    ciudades_reales = df_original['Ciudad'].unique()
    datasets_creados = []
    
    print(f"\n📊 RESUMEN:")
    print(f"   • Archivos encontrados: {len(archivos_creados)}")
    print(f"   • Total de filas en dataset principal: {len(df_original):,}")
    
    # Filtrar y procesar solo archivos de ciudades reales
    for archivo in archivos_creados:
        if archivo.startswith('dataset_') and archivo.endswith('.csv'):
            nombre_ciudad = archivo.replace('dataset_', '').replace('.csv', '')
            
            # Verificar que corresponda a una ciudad real
            if nombre_ciudad in [ciudad.lower() for ciudad in ciudades_reales]:
                ruta_archivo = os.path.join(directorio_ciudades, archivo)
                tamaño_kb = os.path.getsize(ruta_archivo) / 1024
                ciudad_nombre = nombre_ciudad.title()
                
                datasets_creados.append({
                    'ciudad': ciudad_nombre,
                    'archivo': archivo,
                    'ruta': ruta_archivo,
                    'tamaño_kb': tamaño_kb
                })
    
    print(f"   • Archivos de ciudades válidos: {len(datasets_creados)}")
    
    print(f"\n📋 ARCHIVOS DE CIUDADES GENERADOS:")
    for dataset in sorted(datasets_creados, key=lambda x: x['ciudad']):
        print(f"   📄 {dataset['ciudad']}: {dataset['archivo']} ({dataset['tamaño_kb']:.1f} KB)")
    
    return datasets_creados


def mostrar_resumen_detallado_datasets(datasets_creados, df_original):
    """
    Muestra un resumen detallado de los datasets por ciudad creados.
    VERSIÓN OPTIMIZADA - Sin lecturas innecesarias de archivos.
    
    Args:
        datasets_creados (list): Lista de datasets creados
        df_original (DataFrame): Dataset original para comparar
    """
    if not datasets_creados:
        print("⚠️ No hay datasets de ciudades para mostrar")
        return
    
    print("=== RESUMEN DETALLADO DE DATASETS POR CIUDAD ===")
    
    print(f"\n📊 Estadísticas generales:")
    print(f"   • Total de ciudades: {len(datasets_creados)}")
    print(f"   • Total de filas en dataset principal: {len(df_original):,}")
    print(f"   • Ciudades reales: {', '.join(df_original['Ciudad'].unique())}")
    
    # Obtener estadísticas del dataset original (más eficiente)
    print(f"\n📋 Detalle por ciudad:")
    total_archivos = 0
    total_filas_ciudades = 0
    
    # Calcular estadísticas desde el dataset original (evita leer archivos)
    distribución_ciudades = df_original['Ciudad'].value_counts()
    
    for i, dataset in enumerate(datasets_creados, 1):
        if os.path.exists(dataset['ruta']):
            # Obtener filas desde el conteo del dataset original (más eficiente)
            ciudad_original = None
            for ciudad in distribución_ciudades.index:
                if ciudad.lower() == dataset['ciudad'].lower():
                    ciudad_original = ciudad
                    break
            
            if ciudad_original:
                filas = distribución_ciudades[ciudad_original]
                columnas = len(df_original.columns)  # Mismo número de columnas
                
                porcentaje = (filas / len(df_original)) * 100
                total_filas_ciudades += filas
                
                print(f"   {i:2d}. {dataset['ciudad']:15} → {dataset['archivo']:25}")
                print(f"       📊 {filas:,} filas ({porcentaje:5.1f}%) | {columnas} columnas | {dataset['tamaño_kb']:.1f} KB")
                total_archivos += 1
            else:
                print(f"   {i:2d}. {dataset['ciudad']:15} → ⚠️ Ciudad no encontrada en dataset")
        else:
            print(f"   {i:2d}. {dataset['ciudad']:15} → ❌ Archivo no encontrado")
    
    # Verificación de integridad
    print(f"\n🔍 VERIFICACIÓN DE INTEGRIDAD:")
    print(f"   • Archivos creados correctamente: {total_archivos}/{len(datasets_creados)}")
    print(f"   • Total filas calculadas: {total_filas_ciudades:,}")
    print(f"   • Total filas en dataset principal: {len(df_original):,}")
    
    if total_filas_ciudades == len(df_original):
        print(f"   ✅ Integridad verificada: todas las filas están presentes")
    else:
        print(f"   ⚠️  Advertencia: discrepancia en el número de filas")
    
    # Mostrar columnas del dataset original (evita leer archivo)
    print(f"\n📋 Columnas disponibles en datasets por ciudad:")
    for i, col in enumerate(df_original.columns, 1):
        print(f"   {i:2d}. {col}")
    
    # Mostrar muestra rápida solo del primer dataset (lectura mínima)
    if datasets_creados and os.path.exists(datasets_creados[0]['ruta']):
        dataset_ejemplo = datasets_creados[0]
        print(f"\n📖 Muestra del dataset '{dataset_ejemplo['archivo']}':")
        
        # Usar el dataset original filtrado (más eficiente que leer archivo)
        ciudad_filtro = dataset_ejemplo['ciudad']
        df_muestra = df_original[df_original['Ciudad'].str.lower() == ciudad_filtro.lower()].head(3)
        print("Primeras 3 filas:")
        print(df_muestra.to_string())
    
    print(f"\n🎯 DATASETS LISTOS PARA:")
    print(f"   • Análisis de sentimientos por ciudad")
    print(f"   • Comparaciones entre ciudades") 
    print(f"   • Modelos de machine learning específicos")
    print(f"   • Visualizaciones personalizadas")
    
    print(f"\n📁 ESTRUCTURA FINAL:")
    print(f"   data/processed/datasets_por_ciudad/")
    for dataset in datasets_creados:
        print(f"   ├── {dataset['archivo']}")
    
    print(f"\n🎉 ¡{len(datasets_creados)} datasets de ciudades listos para análisis!")


def resumen_rapido_datasets(directorio_ciudades, df_original):
    """
    Función ultra-rápida para mostrar resumen básico sin lecturas de archivos.
    
    Args:
        directorio_ciudades (str): Directorio donde están los datasets
        df_original (DataFrame): Dataset original
        
    Returns:
        dict: Resumen básico de los datasets
    """
    if not os.path.exists(directorio_ciudades):
        return {"error": "Directorio no encontrado"}
    
    archivos = [f for f in os.listdir(directorio_ciudades) if f.endswith('.csv')]
    ciudades_en_datos = df_original['Ciudad'].unique()
    
    resumen = {
        "total_archivos": len(archivos),
        "ciudades_en_datos": len(ciudades_en_datos),
        "total_filas": len(df_original),
        "distribución": df_original['Ciudad'].value_counts().to_dict(),
        "archivos_encontrados": archivos
    }
    
    print(f"📊 RESUMEN RÁPIDO:")
    print(f"   • Archivos CSV encontrados: {len(archivos)}")
    print(f"   • Ciudades en dataset: {len(ciudades_en_datos)}")
    print(f"   • Total de opiniones: {len(df_original):,}")
    
    print(f"\n📋 Distribución por ciudad:")
    for ciudad, cantidad in df_original['Ciudad'].value_counts().items():
        porcentaje = (cantidad / len(df_original)) * 100
        print(f"   • {ciudad}: {cantidad:,} ({porcentaje:.1f}%)")
    
    return resumen


def obtener_rutas_data(ruta_base='../data'):
    """
    Obtiene las rutas de los directorios raw y processed.
    
    Args:
        ruta_base (str): Ruta base del directorio data
        
    Returns:
        tuple: (ruta_raw, ruta_processed)
    """
    ruta_raw = os.path.join(ruta_base, 'raw')
    ruta_processed = os.path.join(ruta_base, 'processed')
    return ruta_raw, ruta_processed


def crear_directorios_data(ruta_base='../data'):
    """
    Crea los directorios raw y processed si no existen.
    
    Args:
        ruta_base (str): Ruta base del directorio data
    """
    ruta_raw, ruta_processed = obtener_rutas_data(ruta_base)
    os.makedirs(ruta_raw, exist_ok=True)
    os.makedirs(ruta_processed, exist_ok=True)
    print(f"✅ Directorios verificados: {ruta_raw}, {ruta_processed}")


def capitalizar_palabras(texto):
    """
    Transforma a mayúscula la primera letra de **todas** las palabras de un texto.
    
    Args:
        texto (str): El texto a transformar
        
    Returns:
        str: El texto con la primera letra de cada palabra en mayúscula
    """
    if not texto or not isinstance(texto, str):
        return texto
    
    # Limpiar espacios al inicio y final
    texto = texto.strip()
    
    if len(texto) == 0:
        return texto
    
    # Capitalizar cada palabra
    palabras = texto.split()
    palabras_capitalizadas = [palabra[0].upper() + palabra[1:] if palabra else '' for palabra in palabras]
    return ' '.join(palabras_capitalizadas)


def extraer_nombre_atraccion(nombre_archivo):
    """
    Extrae el nombre de la atracción del nombre del archivo CSV.
    Por ejemplo: 'cancun-la-isla.csv' -> 'la isla'
    """
    # Remover la extensión .csv
    nombre_sin_extension = nombre_archivo.replace('.csv', '')
    
    # Dividir por guiones
    partes = nombre_sin_extension.split('-')
    
    # Omitir la primera parte (que es el nombre de la ciudad)
    # y unir el resto con espacios
    if len(partes) > 1:
        atraccion = ' '.join(partes[1:])
    else:
        atraccion = nombre_sin_extension
    
    return atraccion


def procesar_dataset_completo(ruta_data='../data'):
    """
    Pipeline completo de procesamiento del dataset.
    """
    print("="*80)
    print("             PIPELINE DE PROCESAMIENTO COMPLETO")
    print("="*80)
    
    # Crear directorios si no existen
    crear_directorios_data(ruta_data)
    
    # 1. Cargar datos
    print("\n🔄 PASO 1: Cargando datos...")
    cargador = CargadorDatos(ruta_data)
    df = cargador.cargar_datos_turisticos()
    
    if df.empty:
        print("❌ Error: No se pudieron cargar los datos")
        return pd.DataFrame()
    
    # 2. Convertir fechas
    print("\n🔄 PASO 2: Convirtiendo fechas...")
    transformador = TransformadorDatos(df)
    df = transformador.convertir_fechas()
    
    # 3. Limpieza específica de fechas - NUEVO
    print("\n🔄 PASO 3: Limpieza específica de columnas de fechas...")
    limpiador = LimpiadorDatos(df)
    
    # 3a. Eliminar columna FechaOpinion por exceso de nulos
    df = limpiador.eliminar_columna_fechaopinion()
    
    # 3b. Eliminar filas con FechaEstadia nula
    df = limpiador.eliminar_filas_fechaestadia_nulas()
    
    # 4. Limpiar columna OrigenAutor
    print("\n🔄 PASO 4: Limpiando columna OrigenAutor...")
    df = limpiador.limpiar_columna_origen_autor()
    
    # 5. Completar valores nulos
    print("\n🔄 PASO 5: Completando valores nulos...")
    df = limpiador.completar_valores_nulos()
    
    # 6. Eliminar duplicados
    print("\n🔄 PASO 6: Eliminando duplicados...")
    df = limpiador.eliminar_duplicados()
    
    # 7. Corregir contenidos mal ubicados
    print("\n🔄 PASO 7: Corrigiendo contenidos mal ubicados...")
    validador = ValidadorDatos(df)
    df = validador.examinar_y_corregir_contenidos_mal_ubicados()
    
    # 8. Crear texto consolidado
    print("\n🔄 PASO 8: Creando texto consolidado...")
    transformador = TransformadorDatos(df)
    df = transformador.agregar_texto_consolidado()
    
    # 9. Aplicar capitalización a columnas categóricas
    print("\n🔄 PASO 9: Aplicando capitalización a columnas categóricas...")
    df['Ciudad'] = df['Ciudad'].apply(capitalizar_palabras)
    df['Atraccion'] = df['Atraccion'].apply(capitalizar_palabras)
    print(f"✅ Capitalización aplicada a ciudades y atracciones")
    
    # 10. Guardar dataset final
    print("\n🔄 PASO 10: Guardando dataset procesado...")
    validador = ValidadorDatos(df)
    df = validador.guardar_dataset_procesado()
    
    # 11. Exportar datasets por ciudad
    print("\n🔄 PASO 11: Exportando datasets por ciudad...")
    exportar_datasets_por_ciudad(df, ruta_data)
    
    print("\n✅ PIPELINE DE PROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print(f"📊 Dataset final: {len(df)} filas, {len(df.columns)} columnas")
    print("\n📁 NUEVA ESTRUCTURA DE DATOS ORGANIZADA:")
    print(f"   📋 Datasets base: data/processed/datasets_por_ciudad/base/")
    print(f"   💭 Sentimientos: data/processed/datasets_por_ciudad/sentimientos/")
    print(f"   🎯 Subjetividad: data/processed/datasets_por_ciudad/subjetividad/")
    print(f"   🔗 Combinados: data/processed/datasets_por_ciudad/combinado/")
    
    return df


def exportar_datasets_por_ciudad(df, ruta_data='../data'):
    """
    Exporta datasets separados por ciudad al directorio processed.
    
    Args:
        df (DataFrame): Dataset consolidado
        ruta_data (str): Ruta base del directorio data
    """
    ruta_raw, ruta_processed = obtener_rutas_data(ruta_data)
    directorio_ciudades = os.path.join(ruta_processed, 'datasets_por_ciudad')
    directorio_base = os.path.join(directorio_ciudades, 'base')
    os.makedirs(directorio_base, exist_ok=True)
    
    print(f"📁 Directorio creado/verificado: {directorio_base}")
    
    # Exportar por ciudad
    ciudades = df['Ciudad'].unique()
    for ciudad in ciudades:
        df_ciudad = df[df['Ciudad'] == ciudad]
        nombre_archivo = f"dataset_{ciudad.lower()}.csv"
        ruta_archivo = os.path.join(directorio_base, nombre_archivo)
        
        df_ciudad.to_csv(ruta_archivo, index=False)
        print(f"💾 {nombre_archivo}: {len(df_ciudad)} filas guardadas")
        print(f"📁 Ubicación: {ruta_archivo}")
    
    print(f"✅ Exportación por ciudades completada en: {directorio_ciudades}")
    print(f"� {len(ciudades)} datasets de ciudades creados")
    return directorio_ciudades
