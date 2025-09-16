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
sys.path.append('../')

# Importar módulo de limpieza de texto
from limpieza_texto_mejorado import LimpiadorTextoMejorado
from utils_topicos import generar_reporte_limpieza, mostrar_ejemplos_limpieza

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
    
    # ===== MÉTRICAS AVANZADAS DE EVALUACIÓN PARA COHERENCIA DE TÓPICOS =====

from regex import P


def calcular_coherencia_topicos(topic_model, texts, topics):
    """
    Calcula múltiples métricas de coherencia avanzadas para evaluar la calidad de los tópicos
    Incluye métricas estándar de la literatura: NPMI, CV
    """
    
    # FIX 1: Verificar si el modelo está entrenado
    if not hasattr(topic_model, 'topics_') or topic_model.topics_ is None:
        print("Warning: Modelo no entrenado, retornando métricas por defecto")
        return {
            'num_topics': 0,
            'silhouette_score': -1,
            'topic_diversity': 0,
            'coverage': 0,
            'avg_topic_size': 0,
            'coherence_cv': -1,
            'coherence_npmi': -1,
            'coherence_uci': -1,
            'semantic_diversity': 0
        }

    topic_info = topic_model.get_topic_info()
    num_topics = len([t for t in topic_info['Topic'] if t != -1])
    
    if num_topics < 2:
        return {
            'num_topics': num_topics,
            'silhouette_score': -1,
            'topic_diversity': 0,
            'coverage': 0,
            'avg_topic_size': 0,
            'coherence_cv': -1,
            'coherence_npmi': -1,
            'semantic_diversity': 0
        }
    
    # 1. Silhouette Score usando embeddings
    embeddings = topic_model._extract_embeddings(texts)
    valid_topics = [t for t in topics if t != -1]
    valid_embeddings = [embeddings[i] for i, t in enumerate(topics) if t != -1]
    
    silhouette = -1
    if len(set(valid_topics)) > 1 and len(valid_embeddings) > 1:
        silhouette = silhouette_score(valid_embeddings, valid_topics)

    
    # 2. Preparar datos para métricas de coherencia con Gensim
    topic_words_lists = []
    topic_embeddings = []
    
    for topic_id in topic_info['Topic']:
        if topic_id != -1:
            # Obtener palabras del tópico - SOLO las palabras, no las puntuaciones
            topic_words = [word for word, score in topic_model.get_topic(topic_id)[:10]]
            topic_words_lists.append(topic_words)

            # FIX 2: Calcular embeddings de palabras de forma robusta con SentenceTransformerBackend
            word_embeddings = []
            try:
                # Acceder al modelo real de sentence transformers
                actual_model = None
                if hasattr(topic_model.embedding_model, 'embedding_model'):
                    # Para SentenceTransformerBackend
                    actual_model = topic_model.embedding_model.embedding_model
                elif hasattr(topic_model.embedding_model, 'encode'):
                    # Para modelos directos
                    actual_model = topic_model.embedding_model
                
                if actual_model and hasattr(actual_model, 'encode'):
                    for word in topic_words[:5]:  # Top 5 palabras
                        word_emb = actual_model.encode([word])[0]
                        word_embeddings.append(word_emb)
                
                if word_embeddings:
                    topic_emb = np.mean(word_embeddings, axis=0)
                    topic_embeddings.append(topic_emb)
                else:
                    # Fallback: usar embeddings promedio de documentos del tópico
                    topic_doc_indices = [i for i, t in enumerate(topics) if t == topic_id]
                    if topic_doc_indices:
                        topic_emb = np.mean([embeddings[i] for i in topic_doc_indices], axis=0)
                        topic_embeddings.append(topic_emb)
                    else:
                        topic_embeddings.append(np.zeros(embeddings[0].shape[0]))
                        
            except Exception as e:
                print(f"Warning: Error calculando embeddings para tópico {topic_id}: {e}")
                # Usar embeddings promedio de documentos del tópico como fallback
                topic_doc_indices = [i for i, t in enumerate(topics) if t == topic_id]
                if topic_doc_indices:
                    topic_emb = np.mean([embeddings[i] for i in topic_doc_indices], axis=0)
                    topic_embeddings.append(topic_emb)
                else:
                    topic_embeddings.append(np.zeros(embeddings[0].shape[0]))
    
    
    # 3. Calcular métricas de coherencia estándar con Gensim
    coherence_cv = -1
    coherence_npmi = -1   

    # Descargar punkt si no está disponible
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    # FIX 3: Tokenización más permisiva (era el problema principal!)
    tokenized_texts = []
    for text in texts:
        clean_text = str(text).lower().strip()
        if len(clean_text) > 0:
            tokens = word_tokenize(clean_text)
            # FIX: Filtro más permisivo - solo que contenga letras
            tokens_filtered = [token for token in tokens 
                                if len(token) >= 2 and any(c.isalpha() for c in token)]
            if len(tokens_filtered) > 0:
                tokenized_texts.append(tokens_filtered)
            else:
                # Fallback con split básico
                basic_tokens = [word for word in clean_text.split() 
                                if len(word) >= 2 and any(c.isalpha() for c in word)]
                if basic_tokens:
                    tokenized_texts.append(basic_tokens)
    
    # Calcular métricas de coherencia si tenemos suficientes datos
    if len(tokenized_texts) >= 5 and len(topic_words_lists) >= 2:
        # Crear diccionario Gensim
        dictionary = Dictionary(tokenized_texts)
        dictionary.filter_extremes(
            no_below=max(1, len(tokenized_texts) // 100),
            no_above=0.8,
            keep_n=min(5000, len(dictionary))
        )
        
        # Verificar que el diccionario tenga suficiente vocabulario
        if len(dictionary) >= 5:
            # Verificar que las palabras de los tópicos estén en el diccionario
            topic_words_in_dict = []
            for topic_words in topic_words_lists:
                valid_words = [word for word in topic_words if word in dictionary.token2id]
                if len(valid_words) >= 2:
                    topic_words_in_dict.append(valid_words)
            
            if len(topic_words_in_dict) >= 2:
                # Calcular métricas de coherencia
                try:
                    cm_cv = CoherenceModel(
                        topics=topic_words_in_dict, 
                        texts=tokenized_texts, 
                        dictionary=dictionary, 
                        coherence='c_v'
                    )
                    coherence_cv = cm_cv.get_coherence()
                except Exception as e:
                    print(f"Warning: Error en coherencia CV: {e}")
                

                try:
                    cm_npmi = CoherenceModel(
                        topics=topic_words_in_dict, 
                        texts=tokenized_texts, 
                        dictionary=dictionary, 
                        coherence='c_npmi'
                    )
                    coherence_npmi = cm_npmi.get_coherence()
                except Exception as e:
                    print(f"Warning: Error en coherencia NPMI: {e}")
                
    else:
        print(f"Info: Datos insuficientes para coherencia: {len(tokenized_texts)} textos, {len(topic_words_lists)} tópicos")

    
    # 4. Diversidad semántica entre tópicos (usando embeddings)
    semantic_diversity = 0
    if len(topic_embeddings) > 1:
        try:
            similarities = []
            
            for i in range(len(topic_embeddings)):
                for j in range(i+1, len(topic_embeddings)):
                    sim = cosine_similarity([topic_embeddings[i]], [topic_embeddings[j]])[0][0]
                    similarities.append(sim)
            
            # Diversidad = 1 - similitud promedio (mayor diversidad = menor similitud)
            avg_similarity = np.mean(similarities) if similarities else 0
            semantic_diversity = 1 - max(0, avg_similarity)
        except Exception as e:
            print(f"Warning: Error calculando diversidad semántica: {e}")
    
    # 5. Diversidad léxica (método original mejorado)
    topic_diversity = 0
    if len(topic_words_lists) > 1:
        # Calcular intersección promedio entre tópicos (menor es mejor)
        intersections = []
        for i in range(len(topic_words_lists)):
            for j in range(i+1, len(topic_words_lists)):
                intersection = len(set(topic_words_lists[i]).intersection(set(topic_words_lists[j])))
                intersections.append(intersection)
        
        avg_intersection = np.mean(intersections) if intersections else 0
        topic_diversity = 1 - (avg_intersection / 10)  # Normalizar por top 10 palabras

    # 6. Cobertura (porcentaje de documentos no outliers)
    coverage = sum(1 for t in topics if t != -1) / len(topics)
    
    # 7. Tamaño promedio de tópicos (normalizado)
    topic_sizes = [sum(1 for t in topics if t == topic_id) 
                    for topic_id in topic_info['Topic'] if topic_id != -1]
    avg_topic_size = np.mean(topic_sizes) if topic_sizes else 0
    
    
    return {
        'num_topics': num_topics,
        'silhouette_score': silhouette,
        'topic_diversity': topic_diversity,
        'coverage': coverage,
        'avg_topic_size': avg_topic_size,
        'coherence_cv': coherence_cv,
        'coherence_npmi': coherence_npmi,
        'semantic_diversity': semantic_diversity
    }
        

def normalizar_metricas(metrics, dataset_chars):
    """
    Normaliza las métricas a un rango [0,1] para comparación justa
    """
    
    normalized_metrics = metrics.copy()
    num_docs = dataset_chars['num_docs']
    
    # 1. Silhouette ya está en [-1, 1], normalizar a [0, 1]
    if metrics['silhouette_score'] != -1:
        normalized_metrics['silhouette_score'] = (metrics['silhouette_score'] + 1) / 2
    else:
        normalized_metrics['silhouette_score'] = 0
    
    # 2. Topic diversity ya está en [0, 1]
    # 3. Coverage ya está en [0, 1]
    
    # 4. Avg topic size - normalizar por tamaño esperado del tópico
    expected_topic_size = num_docs / max(1, metrics['num_topics'])
    if expected_topic_size > 0:
        normalized_metrics['avg_topic_size'] = min(1, metrics['avg_topic_size'] / expected_topic_size)
    else:
        normalized_metrics['avg_topic_size'] = 0
    
    # 5. Coherencia CV: ya está normalizada aproximadamente en [0, 1]
    if metrics['coherence_cv'] == -1:
        normalized_metrics['coherence_cv'] = 0
    else:
        normalized_metrics['coherence_cv'] = max(0, min(1, metrics['coherence_cv']))
    

    
    # 7. Coherencia NPMI: ya está en [-1, 1], normalizar a [0, 1]
    if metrics['coherence_npmi'] == -1:
        normalized_metrics['coherence_npmi'] = 0
    else:
        normalized_metrics['coherence_npmi'] = (metrics['coherence_npmi'] + 1) / 2
    
    # 9. Semantic diversity ya está en [0, 1]
    
    return normalized_metrics

def calcular_pesos_dinamicos(dataset_chars):
    """
    Calcula pesos dinámicos basados en las características del dataset
    """
    num_docs = dataset_chars['num_docs']
    vocab_size = dataset_chars['vocab_size']
    diversity_ratio = dataset_chars['lexical_diversity']
    duplicate_ratio = dataset_chars['duplicate_ratio']
    
    # Categorías de métricas
    # 1. Separación de clusters (silhouette, coverage)
    # 2. Diversidad (topic_diversity, semantic_diversity)  
    # 3. Coherencia interna (coherence_cv, coherence_npmi, coherence_uci)
    
    # Pesos base
    base_weights = {
        'separation': 0.3,    # silhouette + coverage
        'diversity': 0.35,    # topic_diversity + semantic_diversity
        'coherence': 0.35     # coherencias Gensim
    }
    
    # Ajustes dinámicos basados en características del dataset
    
    # Si hay pocos documentos, priorizar coherencia y diversidad
    if num_docs < 100:
        base_weights['coherence'] += 0.1
        base_weights['diversity'] += 0.05
        base_weights['separation'] -= 0.15
    
    # Si hay muchos documentos, priorizar separación
    elif num_docs > 1000:
        base_weights['separation'] += 0.1
        base_weights['coherence'] -= 0.05
        base_weights['diversity'] -= 0.05
    
    # Si hay mucha diversidad léxica, dar más peso a coherencia
    if diversity_ratio > 0.1:
        base_weights['coherence'] += 0.05
        base_weights['diversity'] -= 0.05
    
    # Si hay muchos duplicados, priorizar diversidad
    if duplicate_ratio > 0.3:
        base_weights['diversity'] += 0.1
        base_weights['separation'] -= 0.05
        base_weights['coherence'] -= 0.05
    
    # Normalizar para que sumen 1
    total = sum(base_weights.values())
    for key in base_weights:
        base_weights[key] /= total
    
    return base_weights

def calcular_puntuacion_objetivo(metrics, dataset_chars):
    """
    Combina múltiples métricas normalizadas en una puntuación objetivo para optimización
    Usa pesos dinámicos y métricas estándar de coherencia
    """
    # Normalizar métricas
    normalized_metrics = normalizar_metricas(metrics, dataset_chars)
    
    # Obtener pesos dinámicos
    weights = calcular_pesos_dinamicos(dataset_chars)
    
    # Número objetivo de tópicos basado en el tamaño del dataset
    num_docs = dataset_chars['num_docs']
    # Número objetivo flexible de tópicos
    if num_docs < 100:
        target_topics_range = (3, max(3, num_docs // 20))
    elif num_docs < 500:
        target_topics_range = (5, max(5, num_docs // 30))
    else:
        target_topics_range = (8, min(15, num_docs // 40))
    
    # Penalización suave si el número de tópicos está fuera del rango
    if metrics['num_topics'] > 0:
        if metrics['num_topics'] < target_topics_range[0]:
            topic_penalty = (target_topics_range[0] - metrics['num_topics']) / target_topics_range[0] * 0.5
        elif metrics['num_topics'] > target_topics_range[1]:
            topic_penalty = (metrics['num_topics'] - target_topics_range[1]) / target_topics_range[1] * 0.5
        else:
            topic_penalty = 0  # dentro del rango, sin penalización
    else:
        topic_penalty = 1.0
    
    # 1. SEPARACIÓN DE CLUSTERS
    separation_score = (
        0.60 * normalized_metrics['silhouette_score'] +
        0.40 * normalized_metrics['coverage']
    )
    
    # 2. DIVERSIDAD (Combinar diversidad léxica y semántica)
    diversity_score = (
        0.20 * normalized_metrics['topic_diversity'] +
        0.80 * normalized_metrics['semantic_diversity']
    )
    
    # 3. COHERENCIA INTERNA (Combinar múltiples métricas de coherencia)
    coherence_scores = [
        normalized_metrics['coherence_cv'],
        normalized_metrics['coherence_npmi']
    ]
    
    # Usar solo las coherencias válidas (no -1)
    valid_coherences = [score for score in coherence_scores if score > 0]
    
    if valid_coherences:
        # Dar más peso a CV y NPMI que son más interpretables
        if len(valid_coherences) >= 4:
            coherence_score = (
                0.70 * normalized_metrics['coherence_cv'] +
                0.30 * normalized_metrics['coherence_npmi'] 
            )
        else:
            coherence_score = np.mean(valid_coherences)
    else:
        # Fallback: usar tamaño de tópicos normalizado
        coherence_score = normalized_metrics['avg_topic_size']
    
    # PUNTUACIÓN FINAL
    final_score = (
        weights['separation'] * separation_score +
        weights['diversity'] * diversity_score +
        weights['coherence'] * coherence_score -
        0.15 * topic_penalty  # Penalización por número de tópicos
    )
    
    return max(0, final_score)

def objetivo_bertopic_multiciudad(trial, df, ciudades, columna_texto, dataset_chars_multiciudad):
    """
    🆕 Función objetivo multi-ciudad que implementa cross-validation entre datasets de ciudades
    
    Para cada trial de Optuna:
    1. Entrena y evalúa en cada ciudad por separado
    2. Calcula el promedio de scores
    3. Garantiza que los hiperparámetros funcionen bien en general
    """
    try:
        # Usar los mismos hiperparámetros que la función original pero adaptados para multi-ciudad
        embedding_options = [
            'paraphrase-multilingual-MiniLM-L12-v2', # 118M Params
            'sentence-transformers/distiluse-base-multilingual-cased-v2', # 135M Params
            'intfloat/multilingual-e5-small'
        ]
        
        embedding_name = trial.suggest_categorical('embedding_model', embedding_options)
        
        # UMAP adaptativo - usar estadísticas multi-ciudad
        min_neighbors = max(2, dataset_chars_multiciudad['min_docs_city'] // 30)
        max_neighbors = min(30, dataset_chars_multiciudad['avg_docs_per_city'] // 8)
        
        umap_neighbors = trial.suggest_int('umap_n_neighbors', min_neighbors, max_neighbors)
        umap_components = trial.suggest_int('umap_n_components', 2, 30)
        umap_min_dist = trial.suggest_float('umap_min_dist', 0.0, 0.4)
        umap_metric = trial.suggest_categorical('umap_metric', ['cosine', 'euclidean'])
        
        # HDBSCAN adaptativo - considerar la ciudad más pequeña
        min_cluster_size_min = max(5, dataset_chars_multiciudad['min_docs_city'] // 50)
        min_cluster_size_max = min(50, dataset_chars_multiciudad['min_docs_city'] // 3)
        
        hdbscan_min_cluster_size = trial.suggest_int('hdbscan_min_cluster_size', 
                                                   min_cluster_size_min, min_cluster_size_max)
        hdbscan_min_samples = trial.suggest_int('hdbscan_min_samples', 1, 
                                              max(1, hdbscan_min_cluster_size // 2))
        hdbscan_metric = trial.suggest_categorical('hdbscan_metric', ['euclidean', 'manhattan'])
        hdbscan_method = trial.suggest_categorical('hdbscan_cluster_selection', ['eom', 'leaf'])
        hdbscan_epsilon = trial.suggest_float('hdbscan_epsilon', 0.0, 0.3)
        
        vectorizer_ngram_max = trial.suggest_int('vectorizer_ngram_max', 1, 2)
        min_df_fraction = trial.suggest_float('min_df_fraction', 0.005, 0.08)
        max_df_fraction = trial.suggest_float('max_df_fraction', 0.7, 0.92)
        
        if min_df_fraction >= max_df_fraction:
            min_df_fraction = max_df_fraction - 0.05
            min_df_fraction = max(0.005, min_df_fraction)
        
        vectorizer_max_features = trial.suggest_int('vectorizer_max_features', 200, 1000)
        
        # ===== EVALUACIÓN EN CADA CIUDAD =====
        scores_por_ciudad = {}
        metricas_por_ciudad = {}
        resultados_evaluacion = []  # Para el reporte final
        
        for i, ciudad in enumerate(ciudades):
            try:
                # Preparar datos de la ciudad
                df_ciudad = df[df['Ciudad'] == ciudad]
                texts_ciudad = df_ciudad[columna_texto].dropna().tolist()
                
                if len(texts_ciudad) < 10:  # Mínimo de textos necesarios
                    resultados_evaluacion.append(f"    ⚠️ {ciudad}: Muy pocos textos ({len(texts_ciudad)}), omitiendo...")
                    continue
                
                # Crear características específicas de la ciudad
                dataset_chars_ciudad = dataset_chars_multiciudad['por_ciudad'][ciudad]
                
                if dataset_chars_ciudad is None:
                    resultados_evaluacion.append(f"    ❌ {ciudad}: No hay características válidas")
                    continue
                
                # Crear modelos con los hiperparámetros sugeridos
                embedding_model = SentenceTransformer(embedding_name)
                
                umap_model = UMAP(
                    n_neighbors=min(umap_neighbors, len(texts_ciudad)-1),
                    n_components=min(umap_components, len(texts_ciudad)-1),
                    min_dist=umap_min_dist,
                    metric=umap_metric,
                    random_state=42
                )
                
                hdbscan_model = HDBSCAN(
                    min_cluster_size=min(hdbscan_min_cluster_size, len(texts_ciudad)//3),
                    min_samples=hdbscan_min_samples,
                    metric=hdbscan_metric,
                    cluster_selection_method=hdbscan_method,
                    cluster_selection_epsilon=hdbscan_epsilon,
                    prediction_data=True
                )
                
                vectorizer_model = CountVectorizer(
                    ngram_range=(1, vectorizer_ngram_max),
                    min_df=min_df_fraction,
                    max_df=max_df_fraction,
                    max_features=vectorizer_max_features
                )
                
                # Crear y entrenar BERTopic para esta ciudad
                topic_model_ciudad = BERTopic(
                    embedding_model=embedding_model,
                    umap_model=umap_model,
                    hdbscan_model=hdbscan_model,
                    vectorizer_model=vectorizer_model,
                    language="multilingual",
                    calculate_probabilities=False,
                    verbose=False
                )
                
                # Entrenar en la ciudad
                topics_ciudad, _ = topic_model_ciudad.fit_transform(texts_ciudad)
                
                # Calcular métricas para esta ciudad
                metrics_ciudad = calcular_coherencia_topicos(topic_model_ciudad, texts_ciudad, topics_ciudad)
                score_ciudad = calcular_puntuacion_objetivo(metrics_ciudad, dataset_chars_ciudad)
                
                scores_por_ciudad[ciudad] = score_ciudad
                metricas_por_ciudad[ciudad] = metrics_ciudad
                
                resultados_evaluacion.append(f"    ✅ {ciudad}: Score = {score_ciudad:.4f}, Tópicos = {metrics_ciudad['num_topics']}")
                
            except Exception as e:
                resultados_evaluacion.append(f"    ❌ Error en {ciudad}: {str(e)}.")
                continue
        
        # Imprimir todos los resultados de una vez al final
        print(f"🌍 Trial {trial.number}: Evaluando en {len(ciudades)} ciudades...")
        for resultado in resultados_evaluacion:
            print(resultado)
        
        # ===== CALCULAR SCORE PROMEDIO =====
        if len(scores_por_ciudad) == 0:
            print(f"  ❌ Trial {trial.number}: No se pudo evaluar en ninguna ciudad")
            return 0.0
        
        # Score promedio ponderado por tamaño de dataset
        score_promedio = np.mean(list(scores_por_ciudad.values()))
        
        # Score ponderado por número de documentos (ciudades más grandes tienen más peso)
        total_docs = sum(dataset_chars_multiciudad['por_ciudad'][ciudad]['num_docs'] 
                        for ciudad in scores_por_ciudad.keys())
        
        score_ponderado = sum(
            scores_por_ciudad[ciudad] * (dataset_chars_multiciudad['por_ciudad'][ciudad]['num_docs'] / total_docs)
            for ciudad in scores_por_ciudad.keys()
        )
        
        # Usar promedio de ambos enfoques
        score_final = (score_promedio + score_ponderado) / 2
        
        # ===== GUARDAR MÉTRICAS AGREGADAS =====
        # Promedio de métricas individuales
        metricas_agregadas = {}
        for metric_name in ['num_topics', 'silhouette_score', 'topic_diversity', 'coverage', 
                           'coherence_cv', 'coherence_npmi', 'semantic_diversity']:
            valores = [metricas_por_ciudad[ciudad].get(metric_name, 0) 
                      for ciudad in scores_por_ciudad.keys()
                      if metricas_por_ciudad[ciudad].get(metric_name, -999) != -1]
            
            if valores:
                metricas_agregadas[metric_name] = np.mean(valores)
            else:
                metricas_agregadas[metric_name] = 0
        
        # Guardar en trial
        trial.set_user_attr('score_promedio', score_promedio)
        trial.set_user_attr('score_ponderado', score_ponderado)
        trial.set_user_attr('ciudades_evaluadas', list(scores_por_ciudad.keys()))
        trial.set_user_attr('num_ciudades_exitosas', len(scores_por_ciudad))
        
        # Métricas agregadas
        for metric_name, value in metricas_agregadas.items():
            trial.set_user_attr(f'avg_{metric_name}', value)
        
        # Scores individuales por ciudad
        for ciudad, score in scores_por_ciudad.items():
            trial.set_user_attr(f'score_{ciudad}', score)
        
        # Parámetros del modelo
        trial.set_user_attr('embedding_model', embedding_name)
        trial.set_user_attr('min_df', min_df_fraction)
        trial.set_user_attr('max_df', max_df_fraction)
        
        print(f"  ✅ Trial {trial.number}: Score final = {score_final:.4f} (promedio de {len(scores_por_ciudad)} ciudades)")
        
        return score_final
        
    except Exception as e:
        print(f"❌ Error general en trial {trial.number}: {e}")
        return 0.0

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
