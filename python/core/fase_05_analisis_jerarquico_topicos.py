"""
Fase 05: Análisis Jerárquico de Tópicos
========================================
Identifica sub-tópicos dentro de cada categoría usando BERTopic.
Añade la columna 'Topico' al dataset con el sub-tópico identificado.
"""

import pandas as pd
import numpy as np
import warnings
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings('ignore')

from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from typing import List, Dict
from collections import Counter
import re
from pydantic import BaseModel, Field
import nltk
from nltk.corpus import stopwords

# Importar proveedor de LLM unificado
from .llm_provider import crear_chain


class TopicLabel(BaseModel):
    topic_id: int = Field(..., description="ID del tópico")
    label: str = Field(..., description="Etiqueta descriptiva para el tópico")


class TopicsOutput(BaseModel):
    topics: List[TopicLabel] = Field(..., description="Lista de tópicos con sus etiquetas")


class AnalizadorJerarquicoTopicos:
    """
    Analiza sub-tópicos dentro de categorías usando BERTopic.
    Añade columna 'Topico' al dataset con un DICCIONARIO {categoria: nombre_topico}.
    
    Dado que cada reseña puede tener múltiples categorías, cada reseña puede tener
    múltiples tópicos (uno por cada categoría a la que pertenece).
    
    Ejemplo:
        Categorias: ['Transporte', 'Personal y servicio']
        Topico: {'Transporte': 'Servicio de ferry', 'Personal y servicio': 'Atención al cliente'}
    """
    
    def __init__(self):
        self.dataset_path = 'data/dataset.csv'
        self.min_opiniones_categoria = 50  # Mínimo de opiniones para aplicar BERTopic
        
        # Descargar stopwords si no están disponibles
        try:
            stopwords.words('spanish')
        except:
            nltk.download('stopwords', quiet=True)
    
    def _analizar_caracteristicas(self, textos: List[str]) -> Dict:
        """Analiza características básicas de los textos."""
        textos_validos = [t for t in textos if t and str(t).strip()]
        
        if not textos_validos:
            return {}
        
        # Características básicas
        caracteristicas = {
            'num_textos': len(textos_validos),
            'palabras_promedio': np.mean([len(t.split()) for t in textos_validos]),
            'homogeneidad': self._calcular_homogeneidad(textos_validos),
            'diversidad_lexica': self._calcular_diversidad_lexica(textos_validos),
            'densidad_semantica': self._calcular_densidad_semantica(textos_validos)
        }
        
        return caracteristicas
    
    def _calcular_homogeneidad(self, textos: List[str]) -> float:
        """Calcula homogeneidad basada en variabilidad de longitudes."""
        if len(textos) < 2:
            return 1.0
        
        longitudes = [len(t.split()) for t in textos]
        cv_longitud = np.std(longitudes) / np.mean(longitudes) if np.mean(longitudes) > 0 else 0
        homogeneidad = 1 / (1 + cv_longitud)
        
        return float(min(homogeneidad, 1.0))
    
    def _calcular_diversidad_lexica(self, textos: List[str]) -> float:
        """Calcula diversidad léxica (ratio palabras únicas / total)."""
        todas_palabras = []
        for texto in textos:
            palabras = texto.lower().split()
            todas_palabras.extend(palabras)
        
        if not todas_palabras:
            return 0.0
        
        palabras_unicas = set(todas_palabras)
        return len(palabras_unicas) / len(todas_palabras)
    
    def _calcular_densidad_semantica(self, textos: List[str]) -> float:
        """Estima densidad semántica basada en repetición de palabras clave."""
        palabras_significativas = []
        for texto in textos:
            palabras = [p.lower() for p in texto.split() 
                       if len(p) > 3 and not p.isdigit() and not re.match(r'^\W+$', p)]
            palabras_significativas.extend(palabras)
        
        if not palabras_significativas:
            return 0.0
        
        contador = Counter(palabras_significativas)
        palabras_frecuentes = [palabra for palabra, freq in contador.items() if freq > 1]
        
        return len(palabras_frecuentes) / len(set(palabras_significativas))
    
    def _optimizar_umap(self, caracteristicas: Dict) -> Dict:
        """Optimiza parámetros de UMAP."""
        num_textos = caracteristicas['num_textos']
        homogeneidad = caracteristicas['homogeneidad']
        diversidad = caracteristicas['diversidad_lexica']
        
        # n_neighbors
        if num_textos < 50:
            n_neighbors = max(8, min(15, num_textos // 3))
        elif num_textos < 200:
            n_neighbors = 15 + int(homogeneidad * 8)
        else:
            n_neighbors = 10 + int(homogeneidad * 10)
        
        # n_components
        if diversidad > 0.7:
            n_components = min(40, max(15, num_textos // 6))
        elif diversidad > 0.4:
            n_components = 30
        else:
            n_components = 15
        
        # min_dist
        densidad = caracteristicas['densidad_semantica']
        min_dist = max(0.0, 0.01 - (densidad * 0.01))
        
        return {
            'n_neighbors': n_neighbors,
            'n_components': n_components,
            'min_dist': min_dist,
            'metric': 'cosine',
            'random_state': 42
        }
    
    def _optimizar_hdbscan(self, caracteristicas: Dict) -> Dict:
        """Optimiza parámetros de HDBSCAN."""
        num_textos = caracteristicas['num_textos']
        homogeneidad = caracteristicas['homogeneidad']
        diversidad = caracteristicas['diversidad_lexica']
        
        # min_cluster_size - REDUCIDO para generar más sub-tópicos granulares
        if num_textos < 50:
            min_cluster_size = max(3, int(num_textos * 0.08))
        elif num_textos < 200:
            min_cluster_size = max(5, int(num_textos * 0.06))
        elif num_textos < 500:
            min_cluster_size = max(8, int(num_textos * 0.03))
        else:
            min_cluster_size = max(10, int(num_textos * 0.025))
        
        # Ajustar por homogeneidad - MENOS AGRESIVO
        if homogeneidad > 0.8:
            min_cluster_size = int(min_cluster_size * 1.2)
        elif homogeneidad < 0.5:
            min_cluster_size = int(min_cluster_size * 0.85)
        
        # cluster_selection_epsilon - REDUCIDO para permitir más sub-división
        if diversidad > 0.6:
            epsilon = 0.05
        elif diversidad > 0.4:
            epsilon = 0.03
        else:
            epsilon = 0.0
        
        return {
            'min_cluster_size': max(5, min_cluster_size),  # Mínimo reducido de 8 a 5
            'metric': 'euclidean',
            'cluster_selection_method': 'eom',  # CAMBIADO: genera más tópicos granulares
            'prediction_data': True,
            'cluster_selection_epsilon': epsilon
        }
    
    def _optimizar_vectorizer(self, caracteristicas: Dict) -> Dict:
        """Optimiza parámetros del vectorizador."""
        num_textos = caracteristicas['num_textos']
        palabras_promedio = caracteristicas['palabras_promedio']
        diversidad = caracteristicas['diversidad_lexica']
        
        # ngram_range
        if palabras_promedio > 15:
            ngram_range = (1, 3)
        elif palabras_promedio > 8:
            ngram_range = (1, 2)
        else:
            ngram_range = (1, 1)
        
        # min_df
        min_df = 1
        
        # max_df
        if diversidad > 0.7:
            max_df = 0.95
        elif diversidad > 0.4:
            max_df = 0.98
        else:
            max_df = 0.99
        
        # max_features
        if num_textos < 100:
            max_features = 250
        elif num_textos < 500:
            max_features = 350
        else:
            max_features = min(500, num_textos)
        
        # Stopwords multilingües
        idiomas = ["spanish", "english", "portuguese", "french", "italian"]
        stopwords_multilingues = set()
        for idioma in idiomas:
            stopwords_multilingues.update(stopwords.words(idioma))
        
        return {
            'ngram_range': ngram_range,
            'stop_words': list(stopwords_multilingues),
            'min_df': min_df,
            'max_df': max_df,
            'max_features': max_features
        }
    
    def _crear_bertopic(self, textos: List[str]) -> BERTopic:
        """Crea modelo BERTopic optimizado para los textos."""
        # Analizar características
        caracteristicas = self._analizar_caracteristicas(textos)
        
        # Optimizar hiperparámetros
        umap_params = self._optimizar_umap(caracteristicas)
        hdbscan_params = self._optimizar_hdbscan(caracteristicas)
        vectorizer_params = self._optimizar_vectorizer(caracteristicas)
        
        # Crear componentes
        embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        umap_model = UMAP(**umap_params)
        hdbscan_model = HDBSCAN(**hdbscan_params)
        vectorizer_model = CountVectorizer(**vectorizer_params)
        
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
    
    def _configurar_clasificador_llm(self, categoria_padre: str):
        """Configura el clasificador LLM para etiquetar tópicos."""
        contexto_categoria = f"""
CONTEXTO IMPORTANTE:
Estás analizando sub-tópicos DENTRO de la categoría "{categoria_padre}".
Todos los nombres deben ser SUB-CATEGORÍAS específicas de "{categoria_padre}", NO categorías generales.
"""
        
        ejemplos_por_categoria = {
            "Gastronomía": "restaurantes temáticos, comida callejera, mariscos frescos, cocina internacional",
            "Naturaleza": "cenotes y grutas, áreas de snorkel, reservas ecológicas, avistamiento de fauna",
            "Transporte": "transporte marítimo, tours en vehículo, acceso peatonal, estacionamiento",
            "Personal y servicio": "atención al cliente, guías turísticos, limpieza y mantenimiento, seguridad del personal",
            "Fauna y vida animal": "nado con delfines, observación de aves, tortugas marinas, acuarios y exhibiciones",
            "Historia y cultura": "ruinas arqueológicas, museos temáticos, sitios coloniales, arquitectura histórica",
            "Compras": "artesanías locales, mercados tradicionales, joyería y plata, souvenirs temáticos",
            "Deportes y aventura": "buceo y snorkel, tirolesas y rappel, kayak y paddle, escalada",
            "Vida nocturna": "bares y cantinas, discotecas, shows nocturnos, terrazas y lounges",
            "Alojamiento": "resorts todo incluido, hoteles boutique, hostales económicos, ubicación estratégica",
            "Eventos y festivales": "festivales culturales, eventos deportivos, celebraciones tradicionales, espectáculos temáticos",
            "Seguridad": "vigilancia y control, medidas sanitarias, salvavidas, iluminación nocturna"
        }
        ejemplos = ejemplos_por_categoria.get(categoria_padre, "actividades específicas, instalaciones, servicios particulares")
        
        prompt_template = """
Eres un experto en análisis de opiniones turísticas y taxonomía de tópicos.

""" + contexto_categoria + """

Analiza los siguientes tópicos identificados por BERTopic con sus palabras clave:

{topics_info}

Tu tarea: Asignar un nombre descriptivo único a cada tópico basándote en las palabras clave.

REGLAS OBLIGATORIAS:
1. Nombres en ESPAÑOL
2. Máximo 4 palabras por nombre
3. Nombres CONCRETOS y DESCRIPTIVOS basados en las palabras clave mostradas
4. El nombre DEBE tener COHERENCIA SEMÁNTICA - las palabras deben relacionarse lógicamente
5. NO combinar conceptos no relacionados
6. Si las palabras clave mezclan temas, identificar el tema DOMINANTE más coherente
7. Evitar adjetivos de opinión (hermoso, increíble, excelente)
8. NO usar nombres de lugares específicos
9. NO usar nombres de marcas comerciales
10. TODOS los nombres deben ser ÚNICOS - sin duplicados
11. Si dos tópicos son similares, diferenciarlos por matiz específico

NIVEL DE ESPECIFICIDAD:
- ✅ CORRECTO: """ + ejemplos + """
- ❌ INCORRECTO: Muy genérico (turismo, atracción, lugar, experiencia)

IMPORTANTE - FORMATO JSON:
1. Responde SOLO con JSON válido, sin texto adicional
2. NO traduzcas nombres de campos al español
3. Usa "topics" (inglés) como campo principal
4. Usa "topic_id" y "label" (inglés) para cada tópico

{format_instructions}
"""
        
        # Usar el proveedor de LLM unificado
        chain = crear_chain(prompt_template, pydantic_model=TopicsOutput)
        
        return chain
    
    def _analizar_categoria(self, df: pd.DataFrame, categoria: str) -> Dict:
        """
        Analiza sub-tópicos para una categoría específica.
        Retorna diccionario con mapeo índice -> {categoria: nombre_tópico}.
        """
        # Filtrar opiniones de esta categoría
        mask = df['Categorias'].apply(lambda x: categoria in str(x))
        df_categoria = df[mask].copy()
        
        num_opiniones = len(df_categoria)
        
        if num_opiniones < self.min_opiniones_categoria:
            return {}
        
        # Extraer textos
        textos = df_categoria['TituloReview'].dropna().tolist()
        
        if not textos:
            return {}
        
        # Crear y entrenar modelo BERTopic
        topic_model = self._crear_bertopic(textos)
        topics, _ = topic_model.fit_transform(textos)
        
        # Obtener información de tópicos
        topic_info = topic_model.get_topic_info()
        
        # Preparar información para LLM
        topics_info_text = ""
        topic_data = []
        
        for topic_id in topic_info['Topic']:
            if topic_id == -1:
                continue
            
            topic_words = topic_model.get_topic(topic_id)
            keywords = ", ".join([word for word, _ in topic_words[:8]])
            count = topic_info[topic_info['Topic'] == topic_id]['Count'].iloc[0]
            
            topic_data.append({
                'id': topic_id,
                'keywords': keywords,
                'count': count
            })
            
            topics_info_text += f"Tópico {topic_id}: {keywords} (documentos: {count})\n"
        
        # Etiquetar tópicos con LLM
        topic_names = {}
        topic_names[-1] = "Opiniones Diversas"  # Outliers
        
        if topic_data:
            clasificador_llm = self._configurar_clasificador_llm(categoria)
            resultado_llm = clasificador_llm.invoke({"topics_info": topics_info_text})
            
            for topic_label in resultado_llm.topics:
                topic_names[topic_label.topic_id] = topic_label.label
        
        # Crear mapeo índice -> {categoria: nombre_tópico}
        mapeo_topicos = {}
        for idx, topic_id in enumerate(topics):
            original_idx = df_categoria.iloc[idx].name
            topico_nombre = topic_names.get(topic_id, "Opiniones Diversas")
            mapeo_topicos[original_idx] = {categoria: topico_nombre}
        
        return mapeo_topicos
    
    def ya_procesado(self):
        """
        Verifica si esta fase ya fue ejecutada.
        Revisa si existe la columna 'Topico' en el dataset.
        """
        try:
            df = pd.read_csv(self.dataset_path)
            return 'Topico' in df.columns
        except:
            return False
    
    def procesar(self, forzar=False):
        """
        Procesa el dataset completo:
        1. Identifica categorías con suficientes opiniones
        2. Aplica BERTopic a cada categoría
        3. Etiqueta tópicos con LLM
        4. Añade columna 'Topico' al dataset como DICCIONARIO {categoria: topico}
        
        Args:
            forzar: Si es True, ejecuta incluso si ya fue procesado
        """
        if not forzar and self.ya_procesado():
            print("   ⏭️  Fase ya ejecutada previamente (omitiendo)")
            return
        
        # Cargar dataset
        df = pd.read_csv(self.dataset_path)
        
        # Inicializar diccionario para acumular tópicos por índice
        topicos_por_indice = {idx: {} for idx in df.index}
        
        # Extraer todas las categorías únicas
        todas_categorias = set()
        for cats in df['Categorias']:
            if pd.notna(cats):
                # Parsear la lista de categorías (formato string de lista)
                cats_str = str(cats).strip("[]'\"").replace("'", "").replace('"', '')
                cats_list = [c.strip() for c in cats_str.split(',')]
                todas_categorias.update(cats_list)
        
        # Filtrar categorías válidas (no vacías)
        categorias_validas = [c for c in todas_categorias if c and c.strip()]
        
        print(f"Analizando {len(categorias_validas)} categorías únicas...")
        
        categorias_procesadas = 0
        
        # Procesar cada categoría
        for categoria in categorias_validas:
            # Contar opiniones en esta categoría
            mask = df['Categorias'].apply(lambda x: categoria in str(x))
            num_opiniones = mask.sum()
            
            if num_opiniones < self.min_opiniones_categoria:
                continue
            
            print(f"  • {categoria}: {num_opiniones} opiniones - procesando...")
            
            # Analizar sub-tópicos
            mapeo_topicos = self._analizar_categoria(df, categoria)
            
            # Asignar tópicos al diccionario (ACUMULATIVO - múltiples tópicos por reseña)
            for idx, topico_dict in mapeo_topicos.items():
                topicos_por_indice[idx].update(topico_dict)
            
            categorias_procesadas += 1
        
        # Convertir diccionarios a strings para guardar en CSV
        df['Topico'] = [str(topicos_por_indice[idx]) if topicos_por_indice[idx] else '{}' 
                       for idx in df.index]
        
        # Guardar dataset actualizado
        df.to_csv(self.dataset_path, index=False)
        
        # Estadísticas
        num_con_topico = sum(1 for idx in df.index if topicos_por_indice[idx])
        total_topicos = sum(len(topicos_por_indice[idx]) for idx in df.index)
        promedio_topicos = total_topicos / num_con_topico if num_con_topico > 0 else 0
        
        print(f"✅ Análisis de tópicos completado.")
        print(f"   • Categorías procesadas: {categorias_procesadas}")
        print(f"   • Opiniones con tópico asignado: {num_con_topico}/{len(df)}")
        print(f"   • Promedio de tópicos por opinión: {promedio_topicos:.2f}")
