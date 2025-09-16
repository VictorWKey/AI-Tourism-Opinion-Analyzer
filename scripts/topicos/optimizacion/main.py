# 🔧 CONFIGURACIÓN INICIAL: Solucionar warnings de HuggingFace Tokenizers
import os
import warnings

# ===== SOLUCIONAR WARNINGS DE TOKENIZERS_PARALLELISM =====
# Estos warnings aparecen cuando HuggingFace Tokenizers usa paralelismo y luego 
# se crean nuevos procesos (como en optimización con Optuna)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
print("✓ TOKENIZERS_PARALLELISM configurado a 'false' para evitar warnings")

# Opcional: Suprimir otros warnings comunes
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

print("✓ Configuración de warnings completada")
print("=" * 50)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
import nltk
import optuna
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
optuna.logging.set_verbosity(optuna.logging.WARNING)  # Reducir logs verbosos

import nltk
from nltk.tokenize import word_tokenize
from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora import Dictionary
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

nltk.download('punkt_tab')

# Agregar la carpeta scripts al path para importar módulos
# Obtener el directorio raíz del proyecto (3 niveles arriba desde este archivo)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
scripts_path = os.path.join(project_root, 'scripts')
sys.path.insert(0, scripts_path)

# Importar módulo de limpieza de texto
from topicos.limpieza_texto_mejorado import LimpiadorTextoMejorado
from topicos.utils_topicos import generar_reporte_limpieza, mostrar_ejemplos_limpieza

# Importar funciones de optimización
from topicos.optimizacion.caracteristicas_ciudad import analizar_caracteristicas_dataset, analizar_caracteristicas_multiciudad
from topicos.optimizacion.metricas import calcular_coherencia_topicos, normalizar_metricas
from topicos.optimizacion.objetivo import calcular_pesos_dinamicos, calcular_puntuacion_objetivo, objetivo_bertopic_multiciudad

load_dotenv()
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class TopicNaming(BaseModel):
    nombre_topico: str = Field(description="Nombre descriptivo del tópico en español")

def configurar_clasificador_topicos():
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=50
    )
    
    parser = PydanticOutputParser(pydantic_object=TopicNaming)
    
    prompt_template = """Eres un experto en análisis de opiniones turísticas y modelado de tópicos.

Analiza las siguientes palabras clave que representan un tópico identificado automáticamente en reseñas de atracciones turísticas en México (Cancún, CDMX, Mazatlán, Puebla, Puerto Vallarta).

Palabras clave del tópico: {keywords}

Basándote en estas palabras, asigna un nombre descriptivo y coherente al tópico que capture la esencia de las opiniones turísticas que representa. El nombre debe ser:
- Específico y relacionado con turismo
- En español
- Máximo 4 palabras
- Descriptivo de la experiencia o aspecto turístico
- Evitar mencionar entidades específicas (nombres de lugares, marcas, personas)

{format_instructions}
"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["keywords"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    return prompt | llm | parser

clasificador_topicos = configurar_clasificador_topicos()

# Configurar ciudad a analizar
CIUDAD_ANALIZAR = "Cdmx"  # Cambiar por la ciudad deseada: Cancun, Cdmx, Mazatlan, Puebla, Puerto_Vallarta

# 🆕 NUEVA VARIABLE: Ciudades para optimización de hiperparámetros (cross-validation entre datasets)
CIUDADES_OPTIMIZACION = ["Cancun", "Cdmx", "Mazatlan", "Puebla", "Puerto_vallarta"]

df = pd.read_csv('data/processed/dataset_opiniones_analisis.csv')

# Inicializar columna TopicoConBERTopic si no existe
if 'TopicoConBERTopic' not in df.columns:
    df['TopicoConBERTopic'] = np.nan

print(f"Dataset cargado: {df.shape[0]} opiniones")
print(f"Columnas disponibles: {list(df.columns)}")
print(f"\nDistribución total por ciudad:")
print(df['Ciudad'].value_counts())

# Validar ciudades disponibles para optimización
ciudades_disponibles = df['Ciudad'].unique()
ciudades_optimizacion_validas = [c for c in CIUDADES_OPTIMIZACION if c in ciudades_disponibles]
print(f"\n🎯 Ciudades configuradas para optimización: {CIUDADES_OPTIMIZACION}")
print(f"✅ Ciudades disponibles en el dataset: {ciudades_optimizacion_validas}")

if len(ciudades_optimizacion_validas) != len(CIUDADES_OPTIMIZACION):
    ciudades_faltantes = set(CIUDADES_OPTIMIZACION) - set(ciudades_optimizacion_validas)
    print(f"⚠️ Ciudades no encontradas en el dataset: {list(ciudades_faltantes)}")

# Filtrar por ciudad específica para análisis individual
df_ciudad = df[df['Ciudad'] == CIUDAD_ANALIZAR].copy()
print(f"\n🎯 Analizando ciudad individual: {CIUDAD_ANALIZAR}")
print(f"Opiniones de {CIUDAD_ANALIZAR}: {len(df_ciudad)}")

# Siempre usar texto limpio para BERTopic si está disponible
columna_texto = 'TituloReviewLimpio'
print(f"📝 Usando texto limpio para análisis de tópicos")

texts = df_ciudad[columna_texto].dropna().tolist()

print(f"📝 Columna de texto utilizada: {columna_texto}")
print(f"🧹 Textos para análisis: {len(texts)} opiniones")

# Mostrar estadísticas de texto
if len(texts) > 0:
    palabras_promedio = sum(len(text.split()) for text in texts) / len(texts)
    print(f"📊 Promedio de palabras por texto: {palabras_promedio:.1f}")
    print(f"📏 Longitud promedio: {sum(len(text) for text in texts) / len(texts):.1f} caracteres")

# 📊 Estadísticas para optimización multi-ciudad
print(f"\n📈 ESTADÍSTICAS PARA OPTIMIZACIÓN MULTI-CIUDAD:")
print(f"=" * 60)
for ciudad in ciudades_optimizacion_validas:
    df_temp = df[df['Ciudad'] == ciudad]
    textos_temp = df_temp[columna_texto].dropna()
    print(f"🏙️ {ciudad}: {len(textos_temp)} opiniones válidas")
    if len(textos_temp) > 0:
        palabras_prom = textos_temp.str.split().str.len().mean()
        print(f"   📝 Promedio palabras: {palabras_prom:.1f}")
print(f"=" * 60)

# ===== LIMPIEZA DE TEXTO PARA ANÁLISIS DE TÓPICOS =====
print("🧹 Iniciando proceso de limpieza de texto...")

# Crear instancia del limpiador
limpiador = LimpiadorTextoMejorado(idiomas=['spanish', 'english'])

# Guardar DataFrame antes de la limpieza para comparación
df_antes = df.copy()

if 'TituloReviewLimpio' not in df.columns:
    # Aplicar limpieza al dataset completo
    df = limpiador.limpiar_dataframe(
        df, 
        columna_texto='TituloReview',
        nombre_columna_limpia='TituloReviewLimpio',
        aplicar_lematizacion=True,
        min_longitud_palabra=2,
        max_palabras=None
    )

# Mostrar ejemplos de limpieza
print(f"\n🔍 Ejemplos de limpieza aplicada:")
mostrar_ejemplos_limpieza(df, n_ejemplos=3)

# Generar reporte completo
generar_reporte_limpieza(df_antes, df, 'TituloReview', 'TituloReviewLimpio')

# Guardar dataset actualizado
df.to_csv('data/processed/dataset_opiniones_analisis.csv', index=False)
print(f"\n💾 Dataset actualizado y guardado con columna 'TituloReviewLimpio'")


print(f"\n📋 Estructura actual del dataset:")
print(f"Dimensiones: {df.shape}")
print(f"Columnas: {list(df.columns)}")

# Mostrar posición de las columnas de texto
pos_original = df.columns.get_loc('TituloReview') + 1
pos_limpia = df.columns.get_loc('TituloReviewLimpio') + 1
print(f"📍 TituloReview: columna {pos_original}")
print(f"📍 TituloReviewLimpio: columna {pos_limpia}")

# ===== ANÁLISIS DEL DATASET PARA OPTIMIZACIÓN =====

def analizar_caracteristicas_dataset(texts):
    """Analiza las características del dataset para guiar la optimización"""
    
    print("🔍 Analizando características del dataset...")
    
    # Estadísticas básicas
    num_docs = len(texts)
    avg_length = np.mean([len(text.split()) for text in texts])
    std_length = np.std([len(text.split()) for text in texts])
    min_length = min([len(text.split()) for text in texts])
    max_length = max([len(text.split()) for text in texts])
    
    # Diversidad léxica
    all_words = set()
    for text in texts:
        all_words.update(text.split())
    vocab_size = len(all_words)
    
    # Análisis de duplicados
    unique_texts = len(set(texts))
    duplicate_ratio = 1 - (unique_texts / num_docs)
    
    characteristics = {
        'num_docs': num_docs,
        'avg_length': avg_length,
        'std_length': std_length,
        'min_length': min_length,
        'max_length': max_length,
        'vocab_size': vocab_size,
        'unique_texts': unique_texts,
        'duplicate_ratio': duplicate_ratio,
        'lexical_diversity': vocab_size / sum(len(text.split()) for text in texts)
    }
    
    print(f"📊 Características del dataset:")
    print(f"   • Número de documentos: {num_docs}")
    print(f"   • Longitud promedio: {avg_length:.1f} ± {std_length:.1f} palabras")
    print(f"   • Rango de longitud: {min_length} - {max_length} palabras")
    print(f"   • Vocabulario único: {vocab_size:,} palabras")
    print(f"   • Textos únicos: {unique_texts} ({(1-duplicate_ratio)*100:.1f}%)")
    print(f"   • Diversidad léxica: {characteristics['lexical_diversity']:.4f}")
    
    return characteristics

def analizar_caracteristicas_multiciudad(df, ciudades, columna_texto):
    """
    🆕 Analiza las características de múltiples ciudades para optimización cross-validation
    """
    print("🌍 Analizando características multi-ciudad para optimización...")
    
    caracteristicas_por_ciudad = {}
    
    for ciudad in ciudades:
        print(f"\n🏙️ Analizando {ciudad}:")
        df_ciudad = df[df['Ciudad'] == ciudad]
        texts_ciudad = df_ciudad[columna_texto].dropna().tolist()
    
        caracteristicas_por_ciudad[ciudad] = analizar_caracteristicas_dataset(texts_ciudad)
    
    # Calcular estadísticas combinadas
    total_docs = sum(char['num_docs'] for char in caracteristicas_por_ciudad.values() if char is not None)
    ciudades_validas = [ciudad for ciudad, char in caracteristicas_por_ciudad.items() if char is not None]
    
    if ciudades_validas:
        avg_docs_per_city = total_docs / len(ciudades_validas)
        min_docs = min(char['num_docs'] for char in caracteristicas_por_ciudad.values() if char is not None)
        max_docs = max(char['num_docs'] for char in caracteristicas_por_ciudad.values() if char is not None)
        
        # Diversidad léxica promedio
        avg_lexical_diversity = np.mean([char['lexical_diversity'] for char in caracteristicas_por_ciudad.values() if char is not None])
        
        caracteristicas_combinadas = {
            'total_docs': total_docs,
            'num_ciudades': len(ciudades_validas),
            'avg_docs_per_city': avg_docs_per_city,
            'min_docs_city': min_docs,
            'max_docs_city': max_docs,
            'avg_lexical_diversity': avg_lexical_diversity,
            'ciudades_validas': ciudades_validas,
            'por_ciudad': caracteristicas_por_ciudad
        }
        
        print(f"\n📈 RESUMEN MULTI-CIUDAD:")
        print(f"   • Total documentos: {total_docs:,}")
        print(f"   • Ciudades válidas: {len(ciudades_validas)}")
        print(f"   • Promedio docs/ciudad: {avg_docs_per_city:.1f}")
        print(f"   • Rango docs/ciudad: {min_docs} - {max_docs}")
        print(f"   • Diversidad léxica promedio: {avg_lexical_diversity:.4f}")
        
        return caracteristicas_combinadas
    else:
        print("❌ No se encontraron ciudades válidas")
        return None

# 🆕 Analizar características multi-ciudad para optimización
if len(ciudades_optimizacion_validas) > 1:
    print(f"\n" + "="*80)
    dataset_chars_multiciudad = analizar_caracteristicas_multiciudad(
        df, ciudades_optimizacion_validas, columna_texto
    )
    print(f"="*80)
else:
    print(f"\n⚠️ Solo hay una ciudad válida para optimización multi-ciudad")
    dataset_chars_multiciudad = None

print("🔧 Funciones objetivo cargadas")

# ===== EJECUTAR OPTIMIZACIÓN CON OPTUNA =====

# Configuración de la optimización
OPTIMIZATION_CONFIG = {
    'n_trials': 100,  # Número de pruebas (ajustar según tiempo disponible)
    'timeout': 360000,  # Timeout en segundos (1 hora)
    'n_jobs': 1  # Paralelización (cuidado con memoria)
}

if dataset_chars_multiciudad is not None:
    print(f"🌍 OPTIMIZACIÓN MULTI-CIUDAD ACTIVADA")
    print(f"🎯 Cross-validation entre {len(ciudades_optimizacion_validas)} ciudades")
    print(f"✅ Ciudades: {ciudades_optimizacion_validas}")
    print(f"📊 Total documentos: {dataset_chars_multiciudad['total_docs']:,}")
    print(f"📈 Promedio docs/ciudad: {dataset_chars_multiciudad['avg_docs_per_city']:.1f}")
    
    OPTIMIZATION_CONFIG['sample_size'] = dataset_chars_multiciudad['total_docs']
    optimization_function = lambda trial: objetivo_bertopic_multiciudad(
        trial, df, ciudades_optimizacion_validas, columna_texto, dataset_chars_multiciudad
    )    
    
print(f"\n📊 Configuración de optimización:")
print(f"   • Muestra para optimización: {OPTIMIZATION_CONFIG['sample_size']:,} textos")
print(f"   • Número de pruebas: {OPTIMIZATION_CONFIG['n_trials']}")

def save_callback(study, trial):
    df = study.trials_dataframe(attrs=("number", "value", "params", "state"))
    df.to_csv("optuna_trials.csv", index=False)

# Crear estudio de Optuna
study_name = f"bertopic_multiciudad"
study = optuna.create_study(
    direction='maximize',  # Maximizar la puntuación objetivo
    sampler=optuna.samplers.TPESampler(seed=42),
    pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=5),
    study_name=study_name,
    storage="sqlite:///resultados.db",
    load_if_exists=True
)

print(f"\n🔧 Iniciando optimización ({study_name})...")

# Ejecutar optimización
start_time = pd.Timestamp.now()


study.optimize(
    optimization_function,
    n_trials=OPTIMIZATION_CONFIG['n_trials'],
    timeout=OPTIMIZATION_CONFIG['timeout'],
    n_jobs=OPTIMIZATION_CONFIG['n_jobs'],
    callbacks=[save_callback]
)

optimization_time = pd.Timestamp.now() - start_time
print(f"\n✅ Optimización completada en {optimization_time}")
    
print(f"\n📈 RESULTADO DE LA OPTIMIZACIÓN MULTI-CIUDAD:")
print(f"✅ Los hiperparámetros encontrados funcionan bien en:")
for ciudad in ciudades_optimizacion_validas:
    docs_ciudad = dataset_chars_multiciudad['por_ciudad'][ciudad]['num_docs']
    print(f"   🏙️ {ciudad}: {docs_ciudad} documentos")
