import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora import Dictionary
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

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