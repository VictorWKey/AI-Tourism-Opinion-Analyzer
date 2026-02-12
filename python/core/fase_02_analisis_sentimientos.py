"""
Fase 02: Análisis de Sentimientos
==================================
Analiza sentimientos de las opiniones turísticas usando HuggingFace BERT.
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from tqdm import tqdm
from config.config import ConfigDataset

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class AnalizadorSentimientos:
    """
    Clase para análisis de sentimientos usando modelo preentrenado de HuggingFace.
    Agrega columna 'Sentimiento' al dataset.
    """
    
    @classmethod
    def _get_dataset_path(cls):
        from config.config import ConfigDataset
        return str(ConfigDataset.get_dataset_path())
    
    MODELO_NOMBRE = "nlptown/bert-base-multilingual-uncased-sentiment"
    
    # Mapeo de etiquetas del modelo nlptown (predice 1-5 estrellas)
    MAPEO_ETIQUETAS = {
        '1 star': 'Negativo',
        '2 stars': 'Negativo',
        '3 stars': 'Neutro',
        '4 stars': 'Positivo',
        '5 stars': 'Positivo'
    }
    
    # Mapeo de etiquetas a valor numérico de estrellas (polarity)
    MAPEO_ESTRELLAS = {
        '1 star': 1,
        '2 stars': 2,
        '3 stars': 3,
        '4 stars': 4,
        '5 stars': 5
    }
    
    def __init__(self):
        """Inicializa el analizador."""
        self.DATASET_PATH = self._get_dataset_path()
        self.pipeline = None
        self.modelo_cargado = False
        
    def cargar_modelo(self):
        """Carga el modelo preentrenado de HuggingFace."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "La librería transformers no está disponible. "
                "Instala con: pip install transformers torch"
            )
        
        try:
            cache_dir = ConfigDataset.get_models_cache_dir()
            tokenizer = AutoTokenizer.from_pretrained(self.MODELO_NOMBRE, cache_dir=cache_dir)
            model = AutoModelForSequenceClassification.from_pretrained(self.MODELO_NOMBRE, cache_dir=cache_dir)
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                return_all_scores=True,
            )
            self.modelo_cargado = True
            
        except Exception as e:
            raise RuntimeError(f"Error al cargar modelo: {e}")
    
    def mapear_resultado(self, resultado):
        """
        Mapea resultado de HuggingFace a categoría de sentimiento y número de estrellas.
        
        Args:
            resultado: Resultado del pipeline de HuggingFace
            
        Returns:
            tuple: (sentimiento: str, estrellas: int) — e.g. ('Positivo', 5)
        """
        if not resultado:
            return "Neutro", 3
        
        # Estructura anidada o directa
        scores_list = resultado[0] if isinstance(resultado[0], list) else resultado
        
        # Obtener etiqueta con mayor probabilidad
        mejor_prediccion = max(scores_list, key=lambda x: x['score'])
        mejor_label = mejor_prediccion['label']
        
        # Mapeo directo (modelo nlptown predice "1 star" ... "5 stars")
        sentimiento = self.MAPEO_ETIQUETAS.get(mejor_label, "Neutro")
        estrellas = self.MAPEO_ESTRELLAS.get(mejor_label, 3)
        
        return sentimiento, estrellas
    
    def analizar_texto(self, texto):
        """
        Analiza el sentimiento de un texto.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            tuple: (sentimiento: str, estrellas: int)
        """
        if not self.modelo_cargado:
            raise RuntimeError("Modelo no cargado")
        
        if pd.isna(texto) or str(texto).strip() == "":
            return "Neutro", 3
        
        try:
            # Limitar a 512 caracteres
            texto_procesado = str(texto)[:512]
            resultado = self.pipeline(texto_procesado)
            return self.mapear_resultado(resultado)
            
        except Exception:
            return "Neutro", 3
    
    def ya_procesado(self):
        """
        Verifica si esta fase ya fue ejecutada.
        Revisa si existe la columna 'Sentimiento' en el dataset.
        """
        try:
            df = pd.read_csv(self.DATASET_PATH)
            return 'Sentimiento' in df.columns
        except:
            return False
    
    def procesar(self, forzar=False):
        """
        Procesa el dataset completo y agrega columna 'Sentimiento'.
        Modifica el archivo dataset.csv directamente.
        
        Args:
            forzar: Si es True, ejecuta incluso si ya fue procesado
        """
        if not forzar and self.ya_procesado():
            print("   ⏭️  Fase ya ejecutada previamente (omitiendo)")
            return
        
        # Cargar dataset
        df = pd.read_csv(self.DATASET_PATH)
        
        # Cargar modelo
        self.cargar_modelo()
        
        # Procesar sentimientos
        total = len(df)
        sentimientos = []
        estrellas_list = []
        
        for i, texto in enumerate(tqdm(df['TituloReview'], desc="   Progreso")):
            sentimiento, estrellas = self.analizar_texto(texto)
            sentimientos.append(sentimiento)
            estrellas_list.append(estrellas)
        
        # Agregar columna de sentimiento al dataset
        df['Sentimiento'] = sentimientos
        
        # Agregar columna de calificación (polarity) si no existe en el dataset original
        if 'Calificacion' not in df.columns:
            df['Calificacion'] = estrellas_list
            print(f"   ⭐ Columna 'Calificacion' generada a partir del modelo (el dataset original no la tenía)")
        
        # Guardar dataset modificado
        df.to_csv(self.DATASET_PATH, index=False)
        
        # Estadísticas
        distribucion = df['Sentimiento'].value_counts()
        print(f"✅ Análisis completado: {total} opiniones procesadas")
        print(f"   Positivo: {distribucion.get('Positivo', 0)} | "
              f"Neutro: {distribucion.get('Neutro', 0)} | "
              f"Negativo: {distribucion.get('Negativo', 0)}")
