"""
Analizador inteligente de características de texto para optimización automática de BERTopic.

Este módulo analiza las características de los textos de entrada y adapta automáticamente
los hiperparámetros de BERTopic para obtener resultados óptimos según el dataset.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import Counter
import re
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic


class AnalizadorCaracteristicas:
    """
    Analiza características del texto y optimiza hiperparámetros de BERTopic automáticamente.
    """
    
    def __init__(self):
        self.caracteristicas = {}
        self.hiperparametros_optimizados = {}
        
    def analizar_textos(self, textos: List[str]) -> Dict:
        """
        Analiza las características del conjunto de textos.
        
        Args:
            textos: Lista de textos a analizar
            
        Returns:
            Diccionario con características calculadas
        """
        # Filtrar textos válidos
        textos_validos = [t for t in textos if t and str(t).strip()]
        
        if not textos_validos:
            raise ValueError("No hay textos válidos para analizar")
        
        # Características básicas
        self.caracteristicas = {
            'num_textos': len(textos_validos),
            'longitud_promedio': np.mean([len(t) for t in textos_validos]),
            'palabras_promedio': np.mean([len(t.split()) for t in textos_validos]),
            'longitud_mediana': np.median([len(t) for t in textos_validos]),
            'palabras_mediana': np.median([len(t.split()) for t in textos_validos]),
        }
        
        # Variedad léxica
        todas_palabras = []
        for texto in textos_validos:
            palabras = texto.lower().split()
            todas_palabras.extend(palabras)
        
        palabras_unicas = set(todas_palabras)
        self.caracteristicas.update({
            'vocabulario_total': len(todas_palabras),
            'vocabulario_unico': len(palabras_unicas),
            'ratio_diversidad_lexica': len(palabras_unicas) / len(todas_palabras) if todas_palabras else 0,
            'palabras_repetidas': len(todas_palabras) - len(palabras_unicas)
        })
        
        # Análisis de distribución de longitudes
        longitudes = [len(t.split()) for t in textos_validos]
        self.caracteristicas.update({
            'std_palabras': np.std(longitudes),
            'min_palabras': min(longitudes),
            'max_palabras': max(longitudes),
            'rango_palabras': max(longitudes) - min(longitudes)
        })
        
        # Densidad semántica estimada
        self.caracteristicas['densidad_semantica'] = self._calcular_densidad_semantica(textos_validos)
        
        # Homogeneidad del conjunto
        self.caracteristicas['homogeneidad'] = self._calcular_homogeneidad(textos_validos)
        
        return self.caracteristicas
    
    def _calcular_densidad_semantica(self, textos: List[str]) -> float:
        """
        Estima la densidad semántica basada en la repetición de palabras clave.
        """
        # Extraer palabras significativas (más de 3 caracteres, no números)
        palabras_significativas = []
        for texto in textos:
            palabras = [p.lower() for p in texto.split() 
                       if len(p) > 3 and not p.isdigit() and not re.match(r'^\W+$', p)]
            palabras_significativas.extend(palabras)
        
        if not palabras_significativas:
            return 0.0
        
        # Calcular frecuencias
        contador = Counter(palabras_significativas)
        palabras_frecuentes = [palabra for palabra, freq in contador.items() if freq > 1]
        
        # Densidad como ratio de palabras que aparecen múltiples veces
        return len(palabras_frecuentes) / len(set(palabras_significativas))
    
    def _calcular_homogeneidad(self, textos: List[str]) -> float:
        """
        Calcula la homogeneidad del conjunto de textos basada en variabilidad léxica.
        """
        if len(textos) < 2:
            return 1.0
        
        # Calcular coeficiente de variación de longitudes
        longitudes = [len(t.split()) for t in textos]
        cv_longitud = np.std(longitudes) / np.mean(longitudes) if np.mean(longitudes) > 0 else 0
        
        # Homogeneidad inversa al coeficiente de variación (normalizada)
        homogeneidad = 1 / (1 + cv_longitud)
        
        return float(min(homogeneidad, 1.0))
    
    def optimizar_hiperparametros(self) -> Dict:
        """
        Optimiza hiperparámetros de BERTopic basado en las características analizadas.
        
        Returns:
            Diccionario con hiperparámetros optimizados
        """
        if not self.caracteristicas:
            raise ValueError("Debe analizar textos antes de optimizar hiperparámetros")
        
        # Configuración base
        config = {
            'embedding_model': self._seleccionar_embedding_model(),
            'umap_params': self._optimizar_umap(),
            'hdbscan_params': self._optimizar_hdbscan(),
            'vectorizer_params': self._optimizar_vectorizer()
        }
        
        self.hiperparametros_optimizados = config
        return config
    
    def _seleccionar_embedding_model(self) -> str:
        """
        Selecciona el modelo de embeddings más adecuado según el tamaño del dataset.
        """
        return 'paraphrase-multilingual-MiniLM-L12-v2'
        return 'intfloat/multilingual-e5-small'
        return 'sentence-transformers/distiluse-base-multilingual-cased-v2'

    
    def _optimizar_umap(self) -> Dict:
        """
        Optimiza parámetros de UMAP basado en características del texto.
        """
        num_textos = self.caracteristicas['num_textos']
        diversidad = self.caracteristicas['ratio_diversidad_lexica']
        homogeneidad = self.caracteristicas['homogeneidad']
        
        # n_neighbors: valores altos para mayor agrupación con leaf
        if num_textos < 50:
            n_neighbors = max(8, min(15, num_textos // 3))  # Aumentado de 5-10 a 8-15
        elif num_textos < 200:
            n_neighbors = 15 + int(homogeneidad * 8)  # Aumentado base de 8 a 15
        else:
            n_neighbors = 20 + int(homogeneidad * 10) # Aumentado base de 12 a 20
        
        # n_components: máximo dimensiones para preservar toda la estructura
        if diversidad > 0.7:  # Alta diversidad
            n_components = min(40, max(25, num_textos // 6))  # Aumentado de 30 a 40
        elif diversidad > 0.4:  # Diversidad media
            n_components = 30  # Aumentado de 25 a 30
        else:  # Baja diversidad
            n_components = 25  # Aumentado de 20 a 25
        
        # min_dist: valor mínimo para máxima compactación
        densidad = self.caracteristicas['densidad_semantica']
        min_dist = max(0.0, 0.01 - (densidad * 0.01))  # Reducido de 0.05 a 0.01
        
        return {
            'n_neighbors': n_neighbors,
            'n_components': n_components,
            'min_dist': min_dist,
            'metric': 'cosine',
            'random_state': 42
        }
    
    def _optimizar_hdbscan(self) -> Dict:
        """
        Optimiza parámetros de HDBSCAN basado en características del texto.
        """
        num_textos = self.caracteristicas['num_textos']
        homogeneidad = self.caracteristicas['homogeneidad']
        diversidad = self.caracteristicas['ratio_diversidad_lexica']
        
        # min_cluster_size: valores más restrictivos para menos tópicos con leaf
        if num_textos < 50:
            min_cluster_size = max(5, int(num_textos * 0.12))  # Aumentado de 0.08 a 0.15
        elif num_textos < 200:
            min_cluster_size = max(8, int(num_textos * 0.10))  # Aumentado de 0.06 a 0.12
        elif num_textos < 500:
            min_cluster_size = max(15, int(num_textos * 0.06)) # Aumentado de 0.04 a 0.08
        else:
            min_cluster_size = max(20, int(num_textos * 0.04)) # Aumentado de 0.03 a 0.06
        
        # Ajustar por homogeneidad (factores más conservadores)
        if homogeneidad > 0.8:  # Muy homogéneo
            min_cluster_size = int(min_cluster_size * 1.4)  # Aumentado de 1.2 a 1.4
        elif homogeneidad < 0.5:  # Muy heterogéneo
            min_cluster_size = int(min_cluster_size * 0.9)  # Menos agresivo
        
        # cluster_selection_epsilon: valores más altos para menos granularidad
        if diversidad > 0.6:
            epsilon = 0.1   # Aumentado de 0.05 a 0.1
        elif diversidad > 0.4:
            epsilon = 0.08  # Aumentado de 0.03 a 0.08
        else:
            epsilon = 0.05  # Aumentado de 0.01 a 0.05
        
        return {
            'min_cluster_size': max(8, min_cluster_size),  # Aumentado mínimo de 5 a 8 para ser más restrictivo
            'metric': 'euclidean',
            'cluster_selection_method': 'leaf',  # Mantener leaf con parámetros restrictivos
            'prediction_data': True,
            'cluster_selection_epsilon': epsilon
        }
    
    def _optimizar_vectorizer(self) -> Dict:
        """
        Optimiza parámetros del vectorizador basado en características del texto.
        """
        num_textos = self.caracteristicas['num_textos']
        palabras_promedio = self.caracteristicas['palabras_promedio']
        diversidad = self.caracteristicas['ratio_diversidad_lexica']
        
        # ngram_range: más n-gramas para textos más largos
        if palabras_promedio > 15:
            ngram_range = (1, 3)
        elif palabras_promedio > 8:
            ngram_range = (1, 2)
        else:
            ngram_range = (1, 1)
        
        # min_df: valor mínimo para incluir prácticamente todos los términos
        if num_textos < 50:
            min_df = 1
        elif num_textos < 200:
            min_df = 1
        else:
            min_df = 1  # Siempre 1 para máxima inclusión
        
        # max_df: muy permisivo para incluir la mayoría de términos
        if diversidad > 0.7:
            max_df = 0.95  # Aumentado de 0.85 a 0.95
        elif diversidad > 0.4:
            max_df = 0.98  # Aumentado de 0.9 a 0.98
        else:
            max_df = 0.99  # Aumentado de 0.95 a 0.99
        
        # max_features: valores restrictivos para menos granularidad con leaf
        if num_textos < 100:
            max_features = 250   # Reducido de 400 a 250
        elif num_textos < 500:
            max_features = 350   # Reducido de 600 a 350
        else:
            max_features = min(500, num_textos)  # Muy restrictivo
        
        return {
            'ngram_range': ngram_range,
            'stop_words': None,
            'min_df': min_df,
            'max_df': max_df,
            'max_features': max_features
        }
    
    def crear_modelo_bertopic(self) -> BERTopic:
        """
        Crea un modelo BERTopic con los hiperparámetros optimizados.
        
        Returns:
            Modelo BERTopic configurado
        """
        if not self.hiperparametros_optimizados:
            self.optimizar_hiperparametros()
        
        config = self.hiperparametros_optimizados
        
        # Crear componentes
        embedding_model = SentenceTransformer(config['embedding_model'])
        umap_model = UMAP(**config['umap_params'])
        hdbscan_model = HDBSCAN(**config['hdbscan_params'])
        vectorizer_model = CountVectorizer(**config['vectorizer_params'])
        
        # Crear modelo BERTopic
        topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            language="multilingual",
            calculate_probabilities=True,
            verbose=False
        )
        
        return topic_model
    
    def generar_reporte_optimizacion(self) -> str:
        """
        Genera un reporte de las optimizaciones realizadas.
        
        Returns:
            String con el reporte de optimización
        """
        if not self.caracteristicas or not self.hiperparametros_optimizados:
            return "No hay datos de optimización disponibles"
        
        reporte = []
        reporte.append("🤖 OPTIMIZACIÓN AUTOMÁTICA DE BERTOPIC")
        reporte.append("=" * 50)
        
        # Características analizadas
        reporte.append("\n📊 CARACTERÍSTICAS DEL DATASET:")
        reporte.append(f"   Número de textos: {self.caracteristicas['num_textos']}")
        reporte.append(f"   Palabras promedio: {self.caracteristicas['palabras_promedio']:.1f}")
        reporte.append(f"   Diversidad léxica: {self.caracteristicas['ratio_diversidad_lexica']:.3f}")
        reporte.append(f"   Homogeneidad: {self.caracteristicas['homogeneidad']:.3f}")
        reporte.append(f"   Densidad semántica: {self.caracteristicas['densidad_semantica']:.3f}")
        
        # Decisiones de optimización
        config = self.hiperparametros_optimizados
        reporte.append("\n⚙️ HIPERPARÁMETROS OPTIMIZADOS:")
        reporte.append(f"   Embedding: {config['embedding_model'].split('/')[-1]}")
        reporte.append(f"   UMAP n_neighbors: {config['umap_params']['n_neighbors']}")
        reporte.append(f"   UMAP n_components: {config['umap_params']['n_components']}")
        reporte.append(f"   HDBSCAN min_cluster_size: {config['hdbscan_params']['min_cluster_size']}")
        reporte.append(f"   Vectorizer max_features: {config['vectorizer_params']['max_features']}")
        reporte.append(f"   Vectorizer ngram_range: {config['vectorizer_params']['ngram_range']}")
        
        # Justificaciones
        reporte.append("\n💡 JUSTIFICACIONES:")
        self._agregar_justificaciones(reporte)
        
        return "\n".join(reporte)
    
    def _agregar_justificaciones(self, reporte: List[str]) -> None:
        """
        Agrega justificaciones de las decisiones de optimización al reporte.
        """
        num_textos = self.caracteristicas['num_textos']
        diversidad = self.caracteristicas['ratio_diversidad_lexica']
        homogeneidad = self.caracteristicas['homogeneidad']
        
        if num_textos < 100:
            reporte.append("   - Dataset pequeño: modelo embedding ligero y clusters pequeños")
        elif num_textos > 500:
            reporte.append("   - Dataset grande: modelo embedding robusto y clusters más grandes")
        
        if diversidad > 0.6:
            reporte.append("   - Alta diversidad: más dimensiones UMAP y n-gramas ampliados")
        elif diversidad < 0.4:
            reporte.append("   - Baja diversidad: dimensiones reducidas y filtrado más restrictivo")
        
        if homogeneidad > 0.8:
            reporte.append("   - Textos homogéneos: clusters más grandes para evitar fragmentación")
        elif homogeneidad < 0.5:
            reporte.append("   - Textos heterogéneos: clusters más pequeños para capturar variabilidad")


def configurar_bertopic_inteligente(textos: List[str]) -> Tuple[BERTopic, str]:
    """
    Configura automáticamente BERTopic basado en las características de los textos.
    
    Args:
        textos: Lista de textos para analizar
        
    Returns:
        Tuple con modelo BERTopic optimizado y reporte de optimización
    """
    analizador = AnalizadorCaracteristicas()
    
    # Analizar características
    analizador.analizar_textos(textos)
    
    # Optimizar hiperparámetros
    analizador.optimizar_hiperparametros()
    
    # Crear modelo
    modelo = analizador.crear_modelo_bertopic()
    
    # Generar reporte
    reporte = analizador.generar_reporte_optimizacion()
    
    return modelo, reporte