"""
Módulo para carga y procesamiento de datasets de reseñas turísticas.
"""

import pandas as pd
import os


def verificar_datos_clasificados(ruta_salida="../data/processed/reviews_clasificadas_subjetividad.csv"):
    """
    Verifica si ya existen datos clasificados previamente.
    
    Args:
        ruta_salida (str): Ruta del archivo de clasificaciones
        
    Returns:
        tuple: (existe_archivo, df_clasificado, ciudades_clasificadas)
    """
    if os.path.exists(ruta_salida):
        try:
            df_existente = pd.read_csv(ruta_salida)
            
            # Verificar que tiene las columnas necesarias
            columnas_requeridas = ['TituloReview', 'Ciudad', 'Clasificacion_Subjetividad']
            if all(col in df_existente.columns for col in columnas_requeridas):
                
                # Filtrar datos válidos (sin errores)
                df_valido = df_existente[df_existente['Clasificacion_Subjetividad'] != 'Error']
                
                # Obtener ciudades clasificadas
                ciudades_clasificadas = set(df_valido['Ciudad'].unique())
                
                # Estadísticas por ciudad
                estadisticas = {}
                for ciudad in ciudades_clasificadas:
                    df_ciudad = df_valido[df_valido['Ciudad'] == ciudad]
                    estadisticas[ciudad] = {
                        'total_clasificadas': len(df_ciudad),
                        'distribucion': df_ciudad['Clasificacion_Subjetividad'].value_counts().to_dict()
                    }
                
                print(f"✅ Datos clasificados encontrados: {ruta_salida}")
                
                for ciudad, stats in estadisticas.items():
                    print(f"   📍 {ciudad}: {stats['total_clasificadas']} reseñas")
                
                return True, df_existente, ciudades_clasificadas
            else:
                print(f"⚠️ Archivo encontrado pero faltan columnas requeridas")
                return False, None, set()
                
        except Exception as e:
            print(f"⚠️ Error al leer archivo existente: {e}")
            return False, None, set()
    else:
        print(f"ℹ️ No se encontraron datos clasificados previos")
        return False, None, set()


def cargar_datasets(verificar_existentes=True, ruta_clasificados="../data/processed/reviews_clasificadas_subjetividad.csv"):
    """
    Carga los datasets de Cancún y CDMX y extrae solo la columna TituloReview.
    Automáticamente detecta qué ciudades ya están clasificadas y las omite.
    
    Args:
        verificar_existentes (bool): Si verificar datos ya clasificados
        ruta_clasificados (str): Ruta del archivo con clasificaciones existentes
        
    Returns:
        tuple: (df_reviews_nuevas, df_existente, necesita_clasificacion)
    """
    # Verificar si ya hay datos clasificados
    if verificar_existentes:
        existe_archivo, df_existente, ciudades_clasificadas = verificar_datos_clasificados(ruta_clasificados)
        
        if existe_archivo and df_existente is not None:
            # Obtener ciudades ya clasificadas
            print(f"🔍 Ciudades ya clasificadas encontradas: {list(ciudades_clasificadas)}")
            
            # Cargar datos originales
            df_originales = _cargar_datasets_originales()
            if df_originales is None:
                return None, df_existente, False
            
            # Filtrar solo ciudades no clasificadas
            ciudades_disponibles = set(df_originales['Ciudad'].unique())
            ciudades_nuevas = ciudades_disponibles - ciudades_clasificadas
            
            if not ciudades_nuevas:
                print("💰 No se requieren llamadas adicionales a la API")
                return None, df_existente, False
            else:
                print(f"🆕 Ciudades nuevas para clasificar: {list(ciudades_nuevas)}")
                
                # Filtrar solo las reseñas de ciudades nuevas
                df_nuevas = df_originales[df_originales['Ciudad'].isin(ciudades_nuevas)].copy()
                
                for ciudad in ciudades_nuevas:
                    count = len(df_nuevas[df_nuevas['Ciudad'] == ciudad])
                    print(f"   � {ciudad}: {count} reseñas")
                
                return df_nuevas, df_existente, True
        else:
            print("ℹ️ No se encontraron clasificaciones previas")
    
    # Si no hay verificación o no hay datos existentes, cargar todo
    df_originales = _cargar_datasets_originales()
    return df_originales, None, True


def _cargar_datasets_originales():
    """
    Función interna para cargar los datasets originales.
    """
    # Rutas de los datasets
    ruta_cancun = "../data/processed/datasets_por_ciudad/base/dataset_cancun.csv"
    ruta_cdmx = "../data/processed/datasets_por_ciudad/base/dataset_cdmx.csv"
    ruta_puebla = "../data/processed/datasets_por_ciudad/base/dataset_puebla.csv"
    ruta_puerto_vallarta = "../data/processed/datasets_por_ciudad/base/dataset_puerto_vallarta.csv"
    ruta_mazatlan = "../data/processed/datasets_por_ciudad/base/dataset_mazatlan.csv"
    
    try:
        # Cargar datasets
        df_cancun = pd.read_csv(ruta_cancun)
        df_cdmx = pd.read_csv(ruta_cdmx)
        df_puebla = pd.read_csv(ruta_puebla)
        df_puerto_vallarta = pd.read_csv(ruta_puerto_vallarta)
        df_mazatlan = pd.read_csv(ruta_mazatlan)
        
        # Extraer solo la columna TituloReview
        reviews_cancun = df_cancun[['TituloReview']].copy()
        reviews_cdmx = df_cdmx[['TituloReview']].copy()
        reviews_puebla = df_puebla[['TituloReview']].copy()
        reviews_puerto_vallarta = df_puerto_vallarta[['TituloReview']].copy()
        reviews_mazatlan = df_mazatlan[['TituloReview']].copy()
        
        # Agregar columna de ciudad para identificación
        reviews_cancun['Ciudad'] = 'Cancun'
        reviews_cdmx['Ciudad'] = 'CDMX'
        reviews_puebla['Ciudad'] = 'Puebla'
        reviews_puerto_vallarta['Ciudad'] = 'Puerto Vallarta'
        reviews_mazatlan['Ciudad'] = 'Mazatlan'
        
        # Combinar ambos datasets
        reviews_combined = pd.concat([reviews_cancun, reviews_cdmx, reviews_puebla, reviews_mazatlan, reviews_puerto_vallarta], ignore_index=True)
        
        # Eliminar duplicados y valores nulos
        reviews_combined = reviews_combined.dropna(subset=['TituloReview'])
        reviews_combined = reviews_combined.drop_duplicates(subset=['TituloReview'])
        
        return reviews_combined
        
    except FileNotFoundError as e:
        print(f"❌ Error: No se pudo encontrar el archivo {e}")
        return None
    except Exception as e:
        print(f"❌ Error al cargar los datasets: {e}")
        return None


def _identificar_datos_nuevos(df_originales, df_existente):
    """
    Identifica reseñas que no han sido clasificadas previamente.
    
    Args:
        df_originales (pandas.DataFrame): Datos originales completos
        df_existente (pandas.DataFrame): Datos ya clasificados
        
    Returns:
        pandas.DataFrame: Datos nuevos sin clasificar
    """
    try:
        # Obtener reseñas ya clasificadas
        reseñas_existentes = set(df_existente['TituloReview'].tolist())
        
        # Filtrar reseñas que no han sido clasificadas
        mask_nuevas = ~df_originales['TituloReview'].isin(reseñas_existentes)
        df_nuevos = df_originales[mask_nuevas].copy()
        
        return df_nuevos
        
    except Exception as e:
        print(f"❌ Error al identificar datos nuevos: {e}")
        return None


def cargar_muestra_prueba(df_reviews, n_samples=5):
    """
    Carga una muestra pequeña para pruebas rápidas.
    
    Args:
        df_reviews (pandas.DataFrame): DataFrame con las reseñas completas
        n_samples (int): Número de muestras a tomar
        
    Returns:
        pandas.DataFrame: DataFrame con la muestra seleccionada
    """
    if df_reviews is None or len(df_reviews) == 0:
        print("❌ No hay datos para muestrear")
        return None
    
    # Tomar una muestra pequeña
    df_muestra = df_reviews.head(n_samples)
    
    print(f"🧪 Muestra de {len(df_muestra)} reseñas preparada para prueba")
    
    return df_muestra
