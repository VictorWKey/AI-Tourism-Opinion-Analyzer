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
    
    DATASET_PATH = "data/dataset.csv"
    MODELO_NOMBRE = "nlptown/bert-base-multilingual-uncased-sentiment"
    
    # Mapeo de etiquetas HuggingFace a sentimientos
    MAPEO_ETIQUETAS = {
        'POSITIVE': 'Positivo',
        'NEGATIVE': 'Negativo', 
        'NEUTRAL': 'Neutro',
        'POS': 'Positivo',
        'NEG': 'Negativo',
        'NEU': 'Neutro',
        '1 star': 'Negativo',
        '2 stars': 'Negativo',
        '3 stars': 'Neutro',
        '4 stars': 'Positivo',
        '5 stars': 'Positivo'
    }
    
    def __init__(self):
        """Inicializa el analizador."""
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
        Mapea resultado de HuggingFace a categoría de sentimiento.
        
        Args:
            resultado: Resultado del pipeline de HuggingFace
            
        Returns:
            str: 'Positivo', 'Neutro' o 'Negativo'
        """
        if not resultado:
            return "Neutro"
        
        # Estructura anidada o directa
        scores_list = resultado[0] if isinstance(resultado[0], list) else resultado
        
        # Obtener etiqueta con mayor probabilidad
        mejor_prediccion = max(scores_list, key=lambda x: x['score'])
        mejor_label = mejor_prediccion['label']
        mejor_score = mejor_prediccion['score']
        
        # Mapeo directo
        if mejor_label in self.MAPEO_ETIQUETAS:
            return self.MAPEO_ETIQUETAS[mejor_label]
        
        # Mapeo por patrones
        label_lower = mejor_label.lower()
        if any(pos in label_lower for pos in ['positive', 'pos', '5', '4']):
            return "Positivo"
        elif any(neg in label_lower for neg in ['negative', 'neg', '1', '2']):
            return "Negativo"
        elif any(neu in label_lower for neu in ['neutral', 'neu', '3']):
            return "Neutro"
        else:
            return "Positivo" if mejor_score > 0.6 else "Neutro"
    
    def analizar_texto(self, texto):
        """
        Analiza el sentimiento de un texto.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            str: Sentimiento detectado
        """
        if not self.modelo_cargado:
            raise RuntimeError("Modelo no cargado")
        
        if pd.isna(texto) or str(texto).strip() == "":
            return "Neutro"
        
        try:
            # Limitar a 512 caracteres
            texto_procesado = str(texto)[:512]
            resultado = self.pipeline(texto_procesado)
            return self.mapear_resultado(resultado)
            
        except Exception:
            return "Neutro"
    
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
        
        for i, texto in enumerate(tqdm(df['TituloReview'], desc="   Progreso")):
            sentimiento = self.analizar_texto(texto)
            sentimientos.append(sentimiento)
        
        # Agregar columna al dataset
        df['Sentimiento'] = sentimientos
        
        # Guardar dataset modificado
        df.to_csv(self.DATASET_PATH, index=False)
        
        # Estadísticas
        distribucion = df['Sentimiento'].value_counts()
        print(f"✅ Análisis completado: {total} opiniones procesadas")
        print(f"   Positivo: {distribucion.get('Positivo', 0)} | "
              f"Neutro: {distribucion.get('Neutro', 0)} | "
              f"Negativo: {distribucion.get('Negativo', 0)}")
