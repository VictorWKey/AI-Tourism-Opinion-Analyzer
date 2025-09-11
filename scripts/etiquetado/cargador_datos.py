"""
Módulo para cargar y gestionar datasets para el etiquetado de subjetividad.
"""

import pandas as pd
import os


def cargar_datasets(verificar_existentes=True, ruta_personalizada=None):
    """
    Carga el dataset para clasificación de subjetividad.
    Usa el dataset de análisis específico que contiene los análisis previos.
    
    Args:
        verificar_existentes (bool): Si verificar datos previamente clasificados
        ruta_personalizada (str): Ruta personalizada al dataset
        
    Returns:
        tuple: (df_reviews_nuevas, df_existente, necesita_clasificacion)
    """
    # Ruta prioritaria: dataset de análisis con todos los análisis previos
    ruta_dataset_analisis = ruta_personalizada or '../data/processed/dataset_opiniones_analisis.csv'
    
    # Rutas alternativas para fallback
    ruta_dataset_enriquecido = '../data/processed/dataset_analisis_subjetividad.csv'
    ruta_dataset_consolidado = '../data/processed/dataset_opiniones_consolidado.csv'
    
    df_reviews = None
    df_existente = None
    necesita_clasificacion = True
    
    try:
        # Intentar cargar dataset de análisis principal
        if os.path.exists(ruta_dataset_analisis):
            df_completo = pd.read_csv(ruta_dataset_analisis)
            print(f"✅ Dataset de análisis cargado desde: {ruta_dataset_analisis}")
            print(f"📊 Total de registros: {len(df_completo)}")
            
            # Verificar si ya tiene clasificación LLM
            if 'SubjetividadConLLM' in df_completo.columns:
                print(f"🔍 Dataset ya contiene clasificación LLM")
                df_existente = df_completo
                df_reviews = None
                necesita_clasificacion = False
            else:
                print(f"🔄 Dataset listo para enriquecer con clasificación LLM")
                df_reviews = df_completo
                df_existente = None
        
        # Fallback al dataset enriquecido de notebooks anteriores
        elif os.path.exists(ruta_dataset_enriquecido):
            df_completo = pd.read_csv(ruta_dataset_enriquecido)
            print(f"✅ Dataset enriquecido cargado desde: {ruta_dataset_enriquecido}")
            print(f"📊 Total de registros: {len(df_completo)}")
            
            # Verificar si ya tiene clasificación LLM
            if 'SubjetividadConLLM' in df_completo.columns:
                print(f"� Dataset ya contiene clasificación LLM")
                df_existente = df_completo
                df_reviews = None
                necesita_clasificacion = False
            else:
                print(f"🔄 Dataset listo para enriquecer con clasificación LLM")
                df_reviews = df_completo
                df_existente = None
        
        else:
            # Fallback a método original con dataset consolidado
            print(f"⚠️ Dataset de análisis no encontrado: {ruta_dataset_analisis}")
            print(f"🔄 Usando dataset consolidado original")
            
            if os.path.exists(ruta_dataset_consolidado):
                df_reviews = pd.read_csv(ruta_dataset_consolidado)
                print(f"✅ Dataset consolidado cargado: {len(df_reviews)} registros")
            else:
                print(f"❌ No se encontró dataset consolidado: {ruta_dataset_consolidado}")
                return None, None, False
        
        return df_reviews, df_existente, necesita_clasificacion
        
    except Exception as e:
        print(f"❌ Error cargando datasets: {e}")
        return None, None, False


def cargar_muestra_prueba(n_samples=10):
    """
    Carga una muestra pequeña para pruebas.
    
    Args:
        n_samples (int): Número de muestras a cargar
        
    Returns:
        pandas.DataFrame: DataFrame con muestra de datos
    """
    df_reviews, df_existente, _ = cargar_datasets(verificar_existentes=False)
    
    if df_reviews is not None:
        return df_reviews.sample(min(n_samples, len(df_reviews)), random_state=42)
    else:
        print("❌ No se pudo cargar muestra de prueba")
        return None


def verificar_datos_clasificados():
    """
    Verifica el estado de los datos clasificados.
    
    Returns:
        dict: Información sobre el estado de los datos
    """
    rutas = {
        'dataset_analisis': '../data/processed/dataset_opiniones_analisis.csv',
        'dataset_enriquecido': '../data/processed/dataset_analisis_subjetividad.csv',
        'clasificaciones_llm': '../data/processed/reviews_clasificadas_subjetividad.csv',
        'dataset_consolidado': '../data/processed/dataset_opiniones_consolidado.csv'
    }
    
    estado = {}
    
    for nombre, ruta in rutas.items():
        if os.path.exists(ruta):
            try:
                df = pd.read_csv(ruta)
                estado[nombre] = {
                    'existe': True,
                    'registros': len(df),
                    'columnas': list(df.columns),
                    'ruta': ruta
                }
            except Exception as e:
                estado[nombre] = {
                    'existe': True,
                    'error': str(e),
                    'ruta': ruta
                }
        else:
            estado[nombre] = {
                'existe': False,
                'ruta': ruta
            }
    
    # Mostrar estado
    print("📊 ESTADO DE LOS DATASETS:")
    print("=" * 50)
    
    for nombre, info in estado.items():
        print(f"\n🔍 {nombre.replace('_', ' ').title()}:")
        if info['existe']:
            if 'error' not in info:
                print(f"   ✅ Disponible: {info['registros']} registros")
                print(f"   📋 Columnas: {len(info['columnas'])}")
                if 'SubjetividadConLLM' in info.get('columnas', []):
                    print(f"   🏷️ Contiene clasificación LLM")
                if 'SubjetividadConHF' in info.get('columnas', []):
                    print(f"   🤖 Contiene clasificación HuggingFace")
                if 'SubjetividadConFrases' in info.get('columnas', []):
                    print(f"   📝 Contiene clasificación por frases")
            else:
                print(f"   ❌ Error: {info['error']}")
        else:
            print(f"   ❌ No encontrado")
        print(f"   📁 Ruta: {info['ruta']}")
    
    return estado