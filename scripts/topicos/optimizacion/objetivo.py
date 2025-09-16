# ===== MÉTRICAS AVANZADAS DE EVALUACIÓN PARA COHERENCIA DE TÓPICOS =====
import numpy as np
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from .metricas import calcular_coherencia_topicos, normalizar_metricas


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

