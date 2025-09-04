"""
Módulo para procesamiento de datos turísticos.
Contiene funciones que SÍ modifican el dataset para limpieza y transformación.
"""

import pandas as pd
import numpy as np
import os
import glob
import re
from datetime import datetime
from pathlib import Path


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


def cargar_datos_turisticos(ruta_data='../data'):
    """
    Carga todos los archivos CSV de las carpetas de ciudades y
    los consolida en un solo DataFrame.
    """
    dataframes = []
    
    # Obtener todas las carpetas (ciudades) en el directorio data
    carpetas_ciudades = [d for d in os.listdir(ruta_data) 
                        if os.path.isdir(os.path.join(ruta_data, d))]
    
    print(f"Ciudades encontradas: {carpetas_ciudades}")
    
    for ciudad in carpetas_ciudades:
        ruta_ciudad = os.path.join(ruta_data, ciudad)
        
        # Encontrar todos los archivos CSV en la carpeta de la ciudad
        archivos_csv = glob.glob(os.path.join(ruta_ciudad, '*.csv'))
        
        print(f"\nProcesando ciudad: {ciudad}")
        print(f"Archivos encontrados: {len(archivos_csv)}")
        
        for archivo_csv in archivos_csv:
            try:
                # Leer el archivo CSV
                df = pd.read_csv(archivo_csv)
                
                # Extraer nombre del archivo sin la ruta
                nombre_archivo = os.path.basename(archivo_csv)
                
                # Agregar columnas de ciudad y atracción
                df['ciudad'] = ciudad
                df['atraccion'] = extraer_nombre_atraccion(nombre_archivo)
                
                dataframes.append(df)
                
                print(f"  - {nombre_archivo}: {len(df)} filas")
                
            except Exception as e:
                print(f"  - Error al cargar {archivo_csv}: {e}")
    
    # Concatenar todos los DataFrames
    if dataframes:
        df_consolidado = pd.concat(dataframes, ignore_index=True)
        print(f"\n=== RESUMEN ===")
        print(f"Total de filas: {len(df_consolidado)}")
        print(f"Ciudades procesadas: {df_consolidado['ciudad'].nunique()}")
        print(f"Atracciones procesadas: {df_consolidado['atraccion'].nunique()}")
        
        return df_consolidado
    else:
        print("No se encontraron archivos CSV para procesar.")
        return pd.DataFrame()


def convertir_fecha_opinion(fecha_str):
    """
    Convierte fechas del formato '31 de agosto de 2025' a datetime
    """
    if pd.isna(fecha_str):
        return pd.NaT
    
    try:
        # Mapeo de meses en español
        meses = {
            'enero': 'January', 'febrero': 'February', 'marzo': 'March',
            'abril': 'April', 'mayo': 'May', 'junio': 'June',
            'julio': 'July', 'agosto': 'August', 'septiembre': 'September',
            'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
        }
        
        fecha_str = str(fecha_str).strip()
        
        # Reemplazar nombres de meses en español por inglés
        for esp, eng in meses.items():
            fecha_str = fecha_str.replace(esp, eng)
        
        # Convertir a datetime
        return pd.to_datetime(fecha_str, format='%d de %B de %Y', errors='coerce')
    except:
        return pd.NaT


def convertir_fecha_estadia(fecha_str):
    """
    Convierte fechas del formato 'ago de 2025' a datetime (primer día del mes)
    """
    if pd.isna(fecha_str):
        return pd.NaT
    
    try:
        # Mapeo de meses abreviados en español
        meses = {
            'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
            'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
            'sept': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
        }
        
        fecha_str = str(fecha_str).strip()
        
        # Reemplazar nombres de meses en español por inglés
        for esp, eng in meses.items():
            fecha_str = fecha_str.replace(esp, eng)
        
        # Agregar día 1 para hacer válida la fecha
        fecha_str = '1 ' + fecha_str
        
        # Convertir a datetime
        return pd.to_datetime(fecha_str, format='%d %b de %Y', errors='coerce')
    except:
        return pd.NaT


def convertir_fechas(df):
    """
    Convierte las columnas de fechas del DataFrame.
    """
    print("=== CONVERSIÓN DE TIPOS DE DATOS PARA FECHAS ===")
    
    # Mostrar ejemplos antes de conversión
    print("Ejemplos de fechas ANTES de conversión:")
    if 'FechaOpinion' in df.columns:
        print(f"FechaOpinion: {df['FechaOpinion'].head(3).tolist()}")
    if 'FechaEstadia' in df.columns:
        print(f"FechaEstadia: {df['FechaEstadia'].head(3).tolist()}")
    
    # Aplicar conversiones
    print("\nConvirtiendo fechas...")
    if 'FechaOpinion' in df.columns:
        df['FechaOpinion'] = df['FechaOpinion'].apply(convertir_fecha_opinion)
    if 'FechaEstadia' in df.columns:
        df['FechaEstadia'] = df['FechaEstadia'].apply(convertir_fecha_estadia)
    
    # Mostrar ejemplos después de conversión
    print("\nEjemplos de fechas DESPUÉS de conversión:")
    if 'FechaOpinion' in df.columns:
        print(f"FechaOpinion: {df['FechaOpinion'].head(3).tolist()}")
        print(f"Tipo: {df['FechaOpinion'].dtype}")
        
        # Verificar fechas nulas después de conversión
        fechas_nulas_opinion = df['FechaOpinion'].isna().sum()
        print(f"FechaOpinion nulas: {fechas_nulas_opinion}")
    
    if 'FechaEstadia' in df.columns:
        print(f"FechaEstadia: {df['FechaEstadia'].head(3).tolist()}")
        print(f"Tipo: {df['FechaEstadia'].dtype}")
        
        fechas_nulas_estadia = df['FechaEstadia'].isna().sum()
        print(f"FechaEstadia nulas: {fechas_nulas_estadia}")
    
    print("✅ Conversión de fechas completada")
    return df


def limpiar_origen_autor(valor):
    """
    Limpia los valores de la columna OrigenAutor según los criterios especificados:
    1. Eliminar valores que contengan "aporte"
    2. Eliminar valores con más de 10 palabras
    3. Eliminar nombres propios con patrón "Nombre L" (nombre + letra)
    4. Eliminar valores en mayúsculas como "ALCIRA HAYDEE M"
    5. Mantener lugares válidos como "Puerto Rico", "Buenos Aires, Argentina"
    """
    # Si es NaN o None, mantenerlo
    if pd.isna(valor) or valor is None:
        return valor
    
    valor_str = str(valor).strip()
    
    # Criterio 1: Eliminar si contiene "aporte"
    if "aporte" in valor_str.lower():
        return None
    
    # Criterio 2: Eliminar si tiene más de 10 palabras
    palabras = valor_str.split()
    if len(palabras) > 10:
        return None
    
    # Criterio 3: Eliminar patrón "Nombre L" (nombre seguido de una sola letra)
    patron_nombre_letra = r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+[A-Z]$'
    if re.match(patron_nombre_letra, valor_str):
        return None
    
    # Criterio 4: Eliminar si está todo en mayúsculas (nombres como "ALCIRA HAYDEE M")
    if valor_str.isupper():
        # Si es una sola palabra corta o tiene patrón de nombre personal, eliminar
        if len(palabras) <= 3 and not any(word.lower() in ['usa', 'uk', 'eu'] for word in palabras):
            return None
    
    # Criterio adicional: Eliminar si es claramente un nombre personal
    patron_nombre_personal = r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+[A-Z]$'
    if re.match(patron_nombre_personal, valor_str):
        return None
    
    # Si sobrevive a todos los filtros, mantener el valor
    return valor_str


def limpiar_columna_origen_autor(df):
    """
    Limpia la columna OrigenAutor del DataFrame.
    """
    print("=== LIMPIEZA DE COLUMNA OrigenAutor ===")
    print(f"Valores únicos antes de limpieza: {df['OrigenAutor'].nunique()}")
    
    # Crear columna limpia
    df['OrigenAutor_limpio'] = df['OrigenAutor'].apply(limpiar_origen_autor)
    
    print(f"Valores únicos después de limpieza: {df['OrigenAutor_limpio'].nunique()}")
    print(f"Valores eliminados (convertidos a None): {df['OrigenAutor_limpio'].isna().sum() - df['OrigenAutor'].isna().sum()}")
    
    # Mostrar algunos ejemplos de valores eliminados
    print("\n=== EJEMPLOS DE VALORES ELIMINADOS ===")
    valores_eliminados = df[
        df['OrigenAutor'].notna() & 
        df['OrigenAutor_limpio'].isna()
    ]['OrigenAutor'].value_counts().head(20)
    
    for valor, count in valores_eliminados.items():
        print(f"'{valor}' -> ELIMINADO ({count} veces)")
    
    print(f"\n=== VALORES CONSERVADOS (Top 20) ===")
    valores_conservados = df['OrigenAutor_limpio'].value_counts().head(20)
    for valor, count in valores_conservados.items():
        print(f"'{valor}': {count} veces")
    
    # Validación adicional de la limpieza
    print("\n=== VALIDACIÓN DE LA LIMPIEZA ===")
    casos_test = ['Pamela L', 'Cifuentes E', 'ALCIRA HAYDEE M', '1 aporte', 
                  'Puerto Rico', 'Buenos Aires, Argentina', 'San Juan, Puerto Rico',
                  'Ciudad de México, México']
    
    print("Prueba de casos específicos:")
    for caso in casos_test:
        resultado = limpiar_origen_autor(caso)
        estado = "✅ CONSERVADO" if resultado is not None else "❌ ELIMINADO"
        print(f"'{caso}' -> {estado}")
    
    print(f"\n=== REEMPLAZANDO COLUMNA ORIGINAL ===")
    df['OrigenAutor'] = df['OrigenAutor_limpio']
    df.drop('OrigenAutor_limpio', axis=1, inplace=True)
    
    print("✅ Columna OrigenAutor limpiada exitosamente")
    print(f"Valores únicos finales en OrigenAutor: {df['OrigenAutor'].nunique()}")
    
    # Mostrar muestra de los valores finales más comunes
    print(f"\n=== TOP 15 PAÍSES/LUGARES MÁS COMUNES (DESPUÉS DE LIMPIEZA) ===")
    valores_finales = df['OrigenAutor'].value_counts().head(15)
    for valor, count in valores_finales.items():
        print(f"'{valor}': {count} opiniones")
    
    return df


def completar_valores_nulos(df):
    """
    Completa valores nulos en el dataset con valores descriptivos.
    """
    print("=== COMPLETANDO VALORES NULOS EN DATASET ===")
    
    # Mostrar valores nulos antes de la limpieza
    print("Valores nulos ANTES de completar:")
    if 'Titulo' in df.columns:
        print(f"- Titulo: {df['Titulo'].isna().sum()} nulos")
    if 'TipoViaje' in df.columns:
        print(f"- TipoViaje: {df['TipoViaje'].isna().sum()} nulos")
    if 'OrigenAutor' in df.columns:
        print(f"- OrigenAutor: {df['OrigenAutor'].isna().sum()} nulos")
    
    # Completar valores nulos con valores descriptivos
    if 'Titulo' in df.columns:
        df['Titulo'].fillna('sin titulo', inplace=True)
    if 'TipoViaje' in df.columns:
        df['TipoViaje'].fillna('desconocido', inplace=True)
    if 'OrigenAutor' in df.columns:
        df['OrigenAutor'].fillna('anonimo', inplace=True)
    
    # Mostrar valores nulos después de la limpieza
    print("\nValores nulos DESPUÉS de completar:")
    if 'Titulo' in df.columns:
        print(f"- Titulo: {df['Titulo'].isna().sum()} nulos")
    if 'TipoViaje' in df.columns:
        print(f"- TipoViaje: {df['TipoViaje'].isna().sum()} nulos")
    if 'OrigenAutor' in df.columns:
        print(f"- OrigenAutor: {df['OrigenAutor'].isna().sum()} nulos")
    
    print("\n✅ Valores nulos completados exitosamente")
    
    # Mostrar algunos ejemplos de los valores agregados
    print(f"\n=== DISTRIBUCIÓN DE VALORES AGREGADOS ===")
    if 'Titulo' in df.columns:
        print(f"'sin titulo': {(df['Titulo'] == 'sin titulo').sum()} registros")
    if 'TipoViaje' in df.columns:
        print(f"'desconocido': {(df['TipoViaje'] == 'desconocido').sum()} registros")
    if 'OrigenAutor' in df.columns:
        print(f"'anonimo': {(df['OrigenAutor'] == 'anonimo').sum()} registros")
    
    return df


def eliminar_duplicados(df):
    """
    Elimina duplicados del DataFrame.
    """
    print("=== ELIMINACIÓN DE DUPLICADOS ===")
    
    # Guardar dimensiones antes de eliminar duplicados
    filas_antes = len(df)
    
    # Duplicados completos
    duplicados_completos = df.duplicated().sum()
    print(f"Filas completamente duplicadas encontradas: {duplicados_completos}")
    
    # Duplicados por combinación de columnas importantes
    if 'Titulo' in df.columns and 'Review' in df.columns:
        duplicados_contenido = df.duplicated(subset=['Titulo', 'Review', 'ciudad', 'atraccion']).sum()
        print(f"Duplicados por título + review + ciudad + atracción: {duplicados_contenido}")
    
    # Eliminar duplicados completos
    if duplicados_completos > 0:
        porcentaje_duplicados = (duplicados_completos / len(df)) * 100
        print(f"Porcentaje de duplicados completos: {porcentaje_duplicados:.2f}%")
        
        print(f"\n🔄 Eliminando {duplicados_completos} filas duplicadas...")
        df = df.drop_duplicates()
        
        filas_despues = len(df)
        filas_eliminadas = filas_antes - filas_despues
        
        print(f"✅ Duplicados eliminados exitosamente")
        print(f"   Filas antes: {filas_antes:,}")
        print(f"   Filas después: {filas_despues:,}")
        print(f"   Filas eliminadas: {filas_eliminadas:,}")
    else:
        print("✅ No se encontraron duplicados completos para eliminar")
    
    return df


def examinar_y_corregir_contenidos_mal_ubicados(df):
    """
    Examina casos específicos donde Titulo y OrigenAutor tienen el mismo contenido
    y corrige automáticamente cuando es posible detectar el error.
    """
    print("=== CORRECCIÓN DE CONTENIDOS MAL UBICADOS ===")
    print("Examinando registros con contenido duplicado entre Titulo y OrigenAutor...\n")
    
    casos_problematicos = []
    correcciones_realizadas = 0
    
    # Encontrar todas las filas donde Titulo y OrigenAutor son idénticos
    for idx, row in df.iterrows():
        titulo = str(row['Titulo']).strip()
        origen = str(row['OrigenAutor']).strip()
        
        # Si son idénticos y tienen longitud significativa
        if titulo.lower() == origen.lower() and len(titulo) > 10:
            
            casos_problematicos.append({
                'fila': idx,
                'titulo': titulo,
                'origen': origen,
                'ciudad': row['ciudad'],
                'atraccion': row['atraccion']
            })
            
            print(f"🔍 FILA {idx}:")
            print(f"   Titulo: '{titulo[:80]}...'")
            print(f"   OrigenAutor: '{origen[:80]}...'")
            print(f"   Ciudad: {row['ciudad']}")
            print(f"   Atracción: {row['atraccion']}")
            
            # Lógica de corrección automática
            df.at[idx, 'OrigenAutor'] = 'anonimo'
            correcciones_realizadas += 1
            print(f"   ✅ CORREGIDO: OrigenAutor cambiado a 'anonimo'")
            print()
    
    print(f"=== RESUMEN DE CORRECCIONES ===")
    print(f"📊 Casos problemáticos encontrados: {len(casos_problematicos)}")
    print(f"✅ Correcciones automáticas realizadas: {correcciones_realizadas}")
    print(f"⚠️  Casos que requieren revisión manual: {len(casos_problematicos) - correcciones_realizadas}")
    
    return df, casos_problematicos, correcciones_realizadas


def crear_texto_consolidado(row):
    """
    Crea un texto consolidado que combina todos los campos en una narrativa natural.
    
    Formato: [Titulo]. [Review]. Mi viaje fue [en/con] [TipoViaje].
    """
    
    # Obtener los valores y limpiarlos
    titulo = str(row['Titulo']).strip()
    review = str(row['Review']).strip()
    tipo_viaje = str(row['TipoViaje']).strip()
    
    # Construir el texto consolidado
    texto_partes = []
    
    # 1. Agregar título (si no es "sin titulo")
    if titulo and titulo.lower() != 'sin titulo':
        # Asegurar que termine con punto
        if not titulo.endswith('.'):
            titulo += '.'
        texto_partes.append(titulo)
    
    # 2. Agregar review
    if review and review.lower() not in ['nan', 'none']:
        # Asegurar que termine con punto
        if not review.endswith('.'):
            review += '.'
        texto_partes.append(review)
    
    # 3. Agregar información del tipo de viaje (si no es "desconocido")
    if tipo_viaje and tipo_viaje.lower() != 'desconocido':
        # Mapear cada tipo de viaje específico a su frase correspondiente
        if tipo_viaje.lower() == 'familia':
            texto_partes.append("Mi viaje fue con mi familia.")
        elif tipo_viaje.lower() == 'pareja':
            texto_partes.append("Mi viaje fue con mi pareja.")
        elif tipo_viaje.lower() == 'amigos':
            texto_partes.append("Mi viaje fue con amigos.")
        elif tipo_viaje.lower() == 'solitario':
            texto_partes.append("Mi viaje fue en solitario.")
        elif tipo_viaje.lower() == 'negocios':
            texto_partes.append("Mi viaje fue por negocios.")
        else:
            # Para cualquier otro caso no previsto, usar genérico
            texto_partes.append(f"Mi viaje fue en {tipo_viaje.lower()}.")
    
    # Unir todas las partes con espacios
    texto_consolidado = ' '.join(texto_partes)
    
    return texto_consolidado


def agregar_texto_consolidado(df):
    """
    Agrega la columna de texto consolidado al DataFrame.
    """
    print("=== CREACIÓN DE COLUMNA DE TEXTO CONSOLIDADO ===")
    print("Combinando todos los campos en una narrativa coherente...")
    
    # Aplicar la función a todo el dataset
    print("Generando texto consolidado para cada registro...")
    df['texto_consolidado'] = df.apply(crear_texto_consolidado, axis=1)
    
    print(f"✅ Columna 'texto_consolidado' creada exitosamente")
    print(f"Total de registros procesados: {len(df)}")
    
    # Mostrar estadísticas de la nueva columna
    longitudes = df['texto_consolidado'].str.len()
    print(f"\n📊 ESTADÍSTICAS DE TEXTO CONSOLIDADO:")
    print(f"   • Longitud promedio: {longitudes.mean():.1f} caracteres")
    print(f"   • Longitud mínima: {longitudes.min()} caracteres")
    print(f"   • Longitud máxima: {longitudes.max()} caracteres")
    print(f"   • Mediana: {longitudes.median():.1f} caracteres")
    
    # Mostrar algunos ejemplos
    print(f"\n📝 EJEMPLOS DE TEXTO CONSOLIDADO:")
    print("="*80)
    ejemplos = df.sample(5, random_state=42)
    for idx, row in ejemplos.iterrows():
        print(f"\nEjemplo {idx}:")
        print(f"Ciudad: {row['ciudad']} | Atracción: {row['atraccion']}")
        print(f"Texto consolidado: {row['texto_consolidado']}")
        print("-" * 80)
    
    return df


def guardar_dataset_procesado(df, nombre_archivo='dataset_opiniones_consolidado.csv', ruta='../data/'):
    """
    Guarda el dataset procesado en un archivo CSV.
    """
    print("=== GUARDANDO DATASET PROCESADO ===")
    
    # Verificar que tenemos todas las columnas esperadas
    print("Columnas en el dataset final:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    print(f"\nDimensiones finales: {df.shape}")
    print(f"Filas: {df.shape[0]:,}")
    print(f"Columnas: {df.shape[1]}")
    
    # Construir ruta completa
    ruta_completa = os.path.join(ruta, nombre_archivo)
    
    # Guardar el dataset
    df.to_csv(ruta_completa, index=False)
    
    print(f"\n✅ Dataset final guardado como '{nombre_archivo}'")
    
    # Resumen final si existe la columna de texto consolidado
    if 'texto_consolidado' in df.columns:
        print(f"📊 Incluye la nueva columna 'texto_consolidado' con narrativa completa")
        
        longitudes_finales = df['texto_consolidado'].str.len()
        palabras_finales = df['texto_consolidado'].str.split().str.len()
        
        print(f"\n📈 ESTADÍSTICAS FINALES DE TEXTO CONSOLIDADO:")
        print(f"   • Longitud promedio: {longitudes_finales.mean():.1f} caracteres")
        print(f"   • Palabras promedio: {palabras_finales.mean():.1f} palabras")
        print(f"   • Registros procesados: {len(df):,}")
    
    print(f"\n🎉 PROCESAMIENTO COMPLETADO CON ÉXITO!")
    print("="*60)
    
    return df


def procesar_dataset_completo(ruta_data='../data'):
    """
    Pipeline completo de procesamiento del dataset.
    """
    print("="*80)
    print("             PIPELINE DE PROCESAMIENTO COMPLETO")
    print("="*80)
    
    # 1. Cargar datos
    print("\n🔄 PASO 1: Cargando datos...")
    df = cargar_datos_turisticos(ruta_data)
    
    if df.empty:
        print("❌ No se pudieron cargar los datos. Abortando procesamiento.")
        return None
    
    # 2. Convertir fechas
    print("\n🔄 PASO 2: Convirtiendo fechas...")
    df = convertir_fechas(df)
    
    # 3. Limpiar columna OrigenAutor
    print("\n🔄 PASO 3: Limpiando columna OrigenAutor...")
    df = limpiar_columna_origen_autor(df)
    
    # 4. Completar valores nulos
    print("\n🔄 PASO 4: Completando valores nulos...")
    df = completar_valores_nulos(df)
    
    # 5. Eliminar duplicados
    print("\n🔄 PASO 5: Eliminando duplicados...")
    df = eliminar_duplicados(df)
    
    # 6. Corregir contenidos mal ubicados
    print("\n🔄 PASO 6: Corrigiendo contenidos mal ubicados...")
    df, casos_problematicos, correcciones = examinar_y_corregir_contenidos_mal_ubicados(df)
    
    # 7. Crear texto consolidado
    print("\n🔄 PASO 7: Creando texto consolidado...")
    df = agregar_texto_consolidado(df)
    
    # 8. Guardar dataset final
    print("\n🔄 PASO 8: Guardando dataset procesado...")
    df = guardar_dataset_procesado(df)
    
    print("\n✅ PIPELINE DE PROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print(f"📊 Dataset final: {len(df)} filas, {len(df.columns)} columnas")
    
    return df
