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
from .evaluador_metricas import extraer_palabras_fastopic, evaluar_modelo_topicos


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
            config['num_topics'] = min(5, max(3, stats['num_documentos'] // 5))
        elif stats['num_documentos'] < 500:
            config['num_topics'] = min(10, max(5, stats['num_documentos'] // 10))
        elif stats['num_documentos'] < 1000:
            config['num_topics'] = min(20, max(8, stats['num_documentos'] // 30))
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


class OptimizadorKFASTopic:
    """Optimizador automático del número de tópicos para FASTopic."""
    
    def __init__(self, min_diversidad: float = 0.98):
        self.min_diversidad = min_diversidad
    
    def definir_rangos_k(self, num_docs: int) -> List[int]:
        """Define rangos de k según número de documentos."""
        if num_docs < 100:
            return [2, 3, 4, 5]
        elif num_docs < 500:
            return [5, 7, 9, 11]
        elif num_docs < 1000:
            return [5, 10, 15]
        else:
            return [5, 10, 15, 20, 25, 30, 35, 40, 45]
    
    def afinar_k(self, mejor_k: int, num_docs: int) -> List[int]:
        """Afina el valor de k alrededor del mejor encontrado."""
        if num_docs < 1000:
            if mejor_k == 5:
                return [7, 9]
            elif mejor_k == 10:
                return [11, 13]
            elif mejor_k == 15:
                return [17, 19]
        return []
    
    def evaluar_k(self, textos: List[str], k: int, preprocess, epochs: int = 200) -> Dict:
        """Evalúa un valor específico de k y guarda el modelo completo."""
        model = FASTopic(
            num_topics=k,
            preprocess=preprocess,
            doc_embed_model='paraphrase-multilingual-MiniLM-L12-v2',
            verbose=False
        )
        
        top_words, doc_topic_dist = model.fit_transform(textos, epochs=epochs)
        topics_words = extraer_palabras_fastopic(top_words, words_per_topic=10)
        metricas = evaluar_modelo_topicos(textos, topics_words)
        
        return {
            'k': k,
            'coherencia': metricas['coherencia_cv'],
            'diversidad': metricas['diversidad_topicos'],
            'valido': metricas['diversidad_topicos'] >= self.min_diversidad,
            'model': model,
            'top_words': top_words,
            'doc_topic_dist': doc_topic_dist
        }
    
    def optimizar_k(self, textos: List[str], preprocess) -> Tuple[Dict, List[Dict]]:
        """Optimiza el número de tópicos automáticamente guardando todos los modelos."""
        num_docs = len(textos)
        rangos_k = self.definir_rangos_k(num_docs)
        
        todos_resultados = []
        mejor_resultado = None
        mejor_coherencia = -1
        
        # Evaluación inicial con rangos amplios
        for k in rangos_k:
            resultado = self.evaluar_k(textos, k, preprocess, epochs=200)
            todos_resultados.append(resultado)
            
            if resultado['valido'] and resultado['coherencia'] > mejor_coherencia:
                mejor_coherencia = resultado['coherencia']
                mejor_resultado = resultado
            elif not resultado['valido']:
                # Si la diversidad baja mucho, no evaluar k mayores
                if k > 5:
                    break
        
        # Afinación si es necesario
        if mejor_resultado and num_docs < 1000:
            k_afinacion = self.afinar_k(mejor_resultado['k'], num_docs)
            for k in k_afinacion:
                resultado = self.evaluar_k(textos, k, preprocess, epochs=200)
                todos_resultados.append(resultado)
                
                if resultado['valido'] and resultado['coherencia'] > mejor_coherencia:
                    mejor_coherencia = resultado['coherencia']
                    mejor_resultado = resultado
        
        if mejor_resultado is None:
            # Crear modelo por defecto
            k_default = min(5, max(2, num_docs // 50))
            resultado_default = self.evaluar_k(textos, k_default, preprocess, epochs=200)
            mejor_resultado = resultado_default
            todos_resultados.append(resultado_default)
        
        return mejor_resultado, todos_resultados


def configurar_fastopic_inteligente(textos: List[str], 
                                  idiomas: Optional[List[str]] = None,
                                  verbose: bool = True) -> Tuple[FASTopic, any, any, str, float]:
    """
    Configura y entrena FASTopic automáticamente optimizando k.
    
    Args:
        textos: Lista de documentos de texto
        idiomas: Idiomas para stopwords ['spanish', 'english']
        verbose: Si mostrar información de configuración
        
    Returns:
        Tuple[FASTopic, top_words, doc_topic_dist, str, float]: Modelo entrenado, reporte y tiempo
    """
    import time
    
    inicio_optimizacion = time.time()
    
    analizador = AnalizadorCaracteristicasFASTopic()
    stats = analizador.analizar_corpus(textos)
    
    # Configurar preprocesador
    preprocess, _ = configurar_preprocesador_inteligente(textos)
    
    # Optimizar número de tópicos - ahora devuelve el mejor modelo ya entrenado
    optimizador = OptimizadorKFASTopic()
    mejor_resultado, todos_resultados = optimizador.optimizar_k(textos, preprocess)
    
    tiempo_total = time.time() - inicio_optimizacion
    
    # Extraer el mejor modelo ya entrenado
    model = mejor_resultado['model']
    top_words = mejor_resultado['top_words'] 
    doc_topic_dist = mejor_resultado['doc_topic_dist']
    k_optimo = mejor_resultado['k']
    
    # Generar reporte completo
    num_modelos_evaluados = len(todos_resultados)
    reporte = f"""
📊 CONFIGURACIÓN Y OPTIMIZACIÓN AUTOMÁTICA DE FASTOPIC
{'='*60}

📈 Análisis del Corpus:
  📄 Documentos: {stats['num_documentos']:,}
  📝 Palabras promedio: {stats['palabras_promedio']:.1f}
  🔤 Vocabulario único: {stats['vocab_size']:,}

🎯 Optimización de Tópicos:
  🔍 Modelos evaluados: {num_modelos_evaluados}
  🏷️ K óptimo encontrado: {k_optimo}
  📈 Coherencia CV: {mejor_resultado['coherencia']:.4f}
  🔄 Diversidad: {mejor_resultado['diversidad']:.4f}
  ✅ Criterio diversidad (≥0.98): {'Cumplido' if mejor_resultado['diversidad'] >= 0.98 else 'No cumplido'}

🔧 Configuración Final:
  🌍 Modelo embeddings: paraphrase-multilingual-MiniLM-L12-v2
  🔧 Tokenizer: Multiidioma (ES, EN, PT, FR, IT)
  🚀 Épocas entrenamiento: 200 (para todos los candidatos)
  ⏱️ Tiempo total optimización: {tiempo_total:.2f}s
"""
    
    return model, top_words, doc_topic_dist, reporte, tiempo_total


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