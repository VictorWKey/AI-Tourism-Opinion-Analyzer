"""
Evaluación de métricas para modelos de tópicos.
Proporciona coherencia CV y diversidad de tópicos.
"""

import numpy as np
from gensim.corpora import Dictionary
from gensim.models.coherencemodel import CoherenceModel
from sklearn.feature_extraction.text import CountVectorizer
import warnings
warnings.filterwarnings("ignore")

def calcular_coherencia_cv(texts, topics_words, num_topics=None):
    """
    Calcula coherencia CV para un modelo de tópicos.
    
    Args:
        texts: Lista de documentos tokenizados
        topics_words: Lista de listas con palabras por tópico
        num_topics: Número de tópicos a evaluar
    
    Returns:
        float: Valor de coherencia CV
    """
    texts_tokenized = [text.split() for text in texts]
    dictionary = Dictionary(texts_tokenized)
    corpus = [dictionary.doc2bow(text) for text in texts_tokenized]
    
    coherence_model = CoherenceModel(
        topics=topics_words,
        texts=texts_tokenized,
        corpus=corpus,
        dictionary=dictionary,
        coherence='c_v'
    )
    
    return coherence_model.get_coherence()

def calcular_diversidad_topicos(topics_words, top_n=10):
    """
    Calcula diversidad de tópicos como porcentaje de palabras únicas.
    
    Args:
        topics_words: Lista de listas con palabras por tópico
        top_n: Número de palabras top por tópico
    
    Returns:
        float: Diversidad de tópicos (0-1)
    """
    all_words = set()
    total_words = 0
    
    for topic in topics_words:
        topic_words = topic[:top_n]
        all_words.update(topic_words)
        total_words += len(topic_words)
    
    return len(all_words) / total_words if total_words > 0 else 0.0

def extraer_palabras_bertopic(topic_model, num_topics=None, words_per_topic=10):
    """
    Extrae palabras de tópicos de BERTopic.
    
    Args:
        topic_model: Modelo BERTopic entrenado
        num_topics: Número de tópicos a extraer
        words_per_topic: Palabras por tópico
    
    Returns:
        list: Lista de listas con palabras por tópico
    """
    topic_info = topic_model.get_topic_info()
    topics_words = []
    
    valid_topics = [t for t in topic_info['Topic'] if t != -1]
    if num_topics:
        valid_topics = valid_topics[:num_topics]
    
    for topic_id in valid_topics:
        topic_words = topic_model.get_topic(topic_id)
        words = [word for word, _ in topic_words[:words_per_topic]]
        topics_words.append(words)
    
    return topics_words

def extraer_palabras_fastopic(top_words, num_topics=None, words_per_topic=10):
    """
    Extrae palabras de tópicos de FASTopic.
    
    Args:
        top_words: Lista con palabras por tópico de FASTopic
        num_topics: Número de tópicos a extraer
        words_per_topic: Palabras por tópico
    
    Returns:
        list: Lista de listas con palabras por tópico
    """
    topics_words = []
    
    num_topics_available = len(top_words)
    if num_topics:
        num_topics_available = min(num_topics, num_topics_available)
    
    for topic_id in range(num_topics_available):
        words = top_words[topic_id]
        
        if isinstance(words, str):
            words = words.split()
        elif isinstance(words, (list, tuple)):
            words = list(words)
        else:
            words = []
            
        topics_words.append(words[:words_per_topic])
    
    return topics_words

def evaluar_modelo_topicos(texts, topics_words, modelo_nombre=""):
    """
    Evalúa un modelo de tópicos con coherencia CV y diversidad.
    
    Args:
        texts: Lista de documentos
        topics_words: Lista de listas con palabras por tópico
        modelo_nombre: Nombre del modelo para reporte
    
    Returns:
        dict: Métricas calculadas
    """
    coherencia = calcular_coherencia_cv(texts, topics_words)
    diversidad = calcular_diversidad_topicos(topics_words)
    
    metricas = {
        'modelo': modelo_nombre,
        'coherencia_cv': coherencia,
        'diversidad_topicos': diversidad,
        'num_topicos': len(topics_words)
    }
    
    return metricas

def mostrar_metricas(metricas):
    """
    Muestra las métricas calculadas de forma formateada.
    
    Args:
        metricas: Diccionario con métricas
    """
    print(f"📊 Evaluación {metricas['modelo']}:")
    print(f"   🎯 Tópicos: {metricas['num_topicos']}")
    print(f"   📈 Coherencia CV: {metricas['coherencia_cv']:.4f}")
    print(f"   🔄 Diversidad: {metricas['diversidad_topicos']:.4f}")