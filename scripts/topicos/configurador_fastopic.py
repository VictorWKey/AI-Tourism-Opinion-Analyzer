"""
Configurador inteligente para FASTopic.

Este módulo proporciona funciones para configurar automáticamente
FASTopic basándose en las características del dataset.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from fastopic import FASTopic
from topmost.preprocess import Preprocess
import spacy
from collections import Counter
import langdetect


def crear_tokenizer_multiidioma():
    """Crea tokenizers para múltiples idiomas usando spaCy."""
    modelos_spacy = {
        'es': 'es_core_news_sm',
        'en': 'en_core_web_sm',
        'pt': 'pt_core_news_sm',
        'fr': 'fr_core_news_sm',
        'it': 'it_core_news_sm'
    }
    
    nlp_models = {}
    for lang, model_name in modelos_spacy.items():
        nlp_models[lang] = spacy.load(model_name)
    
    def tokenizer_multiidioma(texto):
        """Tokeniza texto detectando automáticamente el idioma."""
        try:
            idioma_detectado = langdetect.detect(texto)
            if idioma_detectado in nlp_models:
                nlp = nlp_models[idioma_detectado]
            else:
                nlp = nlp_models['es']
        except:
            nlp = nlp_models['es']
        
        return [token.text.lower() for token in nlp(texto) 
                if not token.is_stop and not token.is_punct and token.text.strip()]
    
    return tokenizer_multiidioma


class AnalizadorCaracteristicasFASTopic:
    """Analiza características del texto para configurar FASTopic automáticamente."""
    
    def __init__(self):
        self.estadisticas = {}
        
    def analizar_corpus(self, textos: List[str]) -> Dict:
        """Analiza las características del corpus de texto."""
        
        # Estadísticas básicas
        num_docs = len(textos)
        palabras_por_doc = [len(texto.split()) for texto in textos]
        chars_por_doc = [len(texto) for texto in textos]
        
        # Vocabulario único
        all_words = ' '.join(textos).split()
        vocab_size = len(set(all_words))
        vocab_counter = Counter(all_words)
        
        # Análisis de diversidad
        palabra_freq_media = np.mean(list(vocab_counter.values()))
        diversidad_lexica = vocab_size / len(all_words) if all_words else 0
        
        self.estadisticas = {
            'num_documentos': num_docs,
            'palabras_promedio': np.mean(palabras_por_doc),
            'palabras_mediana': np.median(palabras_por_doc),
            'palabras_std': np.std(palabras_por_doc),
            'chars_promedio': np.mean(chars_por_doc),
            'vocab_size': vocab_size,
            'diversidad_lexica': diversidad_lexica,
            'palabra_freq_media': palabra_freq_media,
            'palabras_min': min(palabras_por_doc) if palabras_por_doc else 0,
            'palabras_max': max(palabras_por_doc) if palabras_por_doc else 0
        }
        
        return self.estadisticas
    
    def recomendar_configuracion(self) -> Dict:
        """Recomienda configuración óptima basada en características del corpus."""
        
        stats = self.estadisticas
        config = {}
        
        # Determinar número de tópicos
        if stats['num_documentos'] < 100:
            config['num_topics'] = min(10, max(3, stats['num_documentos'] // 10))
        elif stats['num_documentos'] < 500:
            config['num_topics'] = 3 # min(30, max(5, stats['num_documentos'] // 30))
        elif stats['num_documentos'] < 1000:
            config['num_topics'] = min(30, max(8, stats['num_documentos'] // 30))
        else:
            config['num_topics'] = min(50, max(10, int(np.sqrt(stats['num_documentos']))))
        
        # Configuración de vocabulario
        if stats['vocab_size'] < 1000:
            config['vocab_size'] = min(5000, stats['vocab_size'] * 2)
        elif stats['vocab_size'] < 5000:
            config['vocab_size'] = min(10000, stats['vocab_size'])
        else:
            config['vocab_size'] = min(15000, stats['vocab_size'])
        
        # Configuración de memoria
        config['low_memory'] = stats['num_documentos'] > 5000
        config['low_memory_batch_size'] = min(2000, max(500, stats['num_documentos'] // 10)) if config['low_memory'] else None
        
        # Configuración de entrenamiento
        if stats['diversidad_lexica'] < 0.1:  # Textos muy similares
            config['epochs'] = 150
            config['learning_rate'] = 0.005
            config['DT_alpha'] = 10.0
            config['normalize_embeddings'] = True
        elif stats['diversidad_lexica'] < 0.3:  # Diversidad media
            config['epochs'] = 100
            config['learning_rate'] = 0.002
            config['DT_alpha'] = 5.0
            config['normalize_embeddings'] = False
        else:  # Alta diversidad
            config['epochs'] = 80
            config['learning_rate'] = 0.001
            config['DT_alpha'] = 2.0
            config['normalize_embeddings'] = False
        
        # Configuración específica para textos cortos
        if stats['palabras_promedio'] < 10:
            config['normalize_embeddings'] = True
            config['DT_alpha'] = max(config['DT_alpha'], 8.0)
        
        return config


def configurar_preprocesador_inteligente(textos: List[str]) -> Tuple[Preprocess, Dict]:
    """Configura el preprocesador de FASTopic basándose en características del texto."""
    
    analizador = AnalizadorCaracteristicasFASTopic()
    stats = analizador.analizar_corpus(textos)
    config = analizador.recomendar_configuracion()
    
    # Crear tokenizer multiidioma
    tokenizer_multiidioma = crear_tokenizer_multiidioma()
    
    # Crear preprocesador con tokenizer personalizado
    preprocess = Preprocess(
        vocab_size=config['vocab_size'],
        tokenizer=tokenizer_multiidioma,
        min_doc_count=max(2, stats['num_documentos'] // 100),
        max_doc_freq=0.8
    )
    
    return preprocess, config


def configurar_fastopic_inteligente(textos: List[str], 
                                  idiomas: Optional[List[str]] = None,
                                  verbose: bool = True) -> Tuple[FASTopic, str]:
    """
    Configura FASTopic automáticamente basándose en características del corpus.
    
    Args:
        textos: Lista de documentos de texto
        idiomas: Idiomas para stopwords ['spanish', 'english']
        verbose: Si mostrar información de configuración
        
    Returns:
        Tuple[FASTopic, str]: Modelo configurado y reporte de optimización
    """
    
    analizador = AnalizadorCaracteristicasFASTopic()
    stats = analizador.analizar_corpus(textos)
    
    # Configurar preprocesador
    preprocess, config = configurar_preprocesador_inteligente(textos)
    
    # Crear modelo FASTopic
    model = FASTopic(
        num_topics=config['num_topics'],
        preprocess=preprocess,
        doc_embed_model='paraphrase-multilingual-MiniLM-L12-v2',
        verbose=verbose
    )
    
    # Generar reporte simplificado
    reporte = f"""
📊 CONFIGURACIÓN AUTOMÁTICA DE FASTOPIC
{'='*50}

📈 Análisis del Corpus:
  📄 Documentos: {stats['num_documentos']:,}
  📝 Palabras promedio por doc: {stats['palabras_promedio']:.1f}
  🔤 Vocabulario único: {stats['vocab_size']:,}

🎯 Configuración:
  🏷️ Número de tópicos: {config['num_topics']}
  📚 Tamaño vocabulario: {config['vocab_size']:,}
  🌍 Modelo embeddings: paraphrase-multilingual-MiniLM-L12-v2
  🔧 Tokenizer: Multiidioma (ES, EN, PT, FR, IT)
"""
    
    # Guardar configuración para entrenamiento
    setattr(model, '_training_config', {
        'epochs': config['epochs'],
        'learning_rate': config['learning_rate']
    })
    
    return model, reporte


def obtener_configuracion_manual(num_topics: int = 20,
                                vocab_size: int = 10000,
                                idiomas: Optional[List[str]] = None) -> Tuple[FASTopic, Preprocess]:
    """
    Configuración manual de FASTopic para casos específicos.
    
    Args:
        num_topics: Número de tópicos deseados
        vocab_size: Tamaño del vocabulario
        idiomas: Idiomas para stopwords
        
    Returns:
        Tuple[FASTopic, Preprocess]: Modelo y preprocesador configurados
    """
    
    # Crear tokenizer multiidioma
    tokenizer_multiidioma = crear_tokenizer_multiidioma()
    
    # Crear preprocesador
    preprocess = Preprocess(
        vocab_size=vocab_size,
        tokenizer=tokenizer_multiidioma
    )
    
    # Crear modelo
    model = FASTopic(
        num_topics=num_topics,
        preprocess=preprocess,
        doc_embed_model='paraphrase-multilingual-MiniLM-L12-v2',
        verbose=True
    )
    
    return model, preprocess