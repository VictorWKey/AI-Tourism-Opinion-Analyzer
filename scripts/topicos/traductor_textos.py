import pandas as pd
from transformers import MarianMTModel, MarianTokenizer, pipeline
from tqdm import tqdm
import warnings

# Suprimir warnings de importación
warnings.filterwarnings("ignore", message=".*not exported from module.*")


class TraductorTextos:
    """
    Traductor de textos de inglés a español usando Helsinki-NLP/opus-mt-en-es.
    Detecta automáticamente el idioma usando el mismo modelo que el limpiador de texto
    y traduce únicamente textos en inglés.
    """
    
    def __init__(self):
        self.model_name = "Helsinki-NLP/opus-mt-en-es"
        self._model = None
        self._tokenizer = None
        self._detector_idioma = None
    
    @property
    def detector_idioma(self):
        """Detector de idioma lazy loading - mismo modelo que el limpiador."""
        if self._detector_idioma is None:
            self._detector_idioma = pipeline(
                "text-classification", 
                model="papluca/xlm-roberta-base-language-detection"
            )
        return self._detector_idioma
    
    @property
    def model(self):
        if self._model is None:
            self._cargar_modelo()
        return self._model
    
    @property
    def tokenizer(self):
        if self._tokenizer is None:
            self._cargar_modelo()
        return self._tokenizer
    
    def _cargar_modelo(self):
        """Carga el modelo de traducción de forma lazy."""
        self._tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        self._model = MarianMTModel.from_pretrained(self.model_name)
    
    def detectar_idioma(self, texto):
        """
        Detecta el idioma del texto usando el mismo modelo de Hugging Face que el limpiador.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            str: Código del idioma detectado ('en', 'es', etc.)
        """
        if not texto or pd.isna(texto) or len(str(texto).strip()) < 3:
            return 'unknown'
        
        try:
            # Truncar texto si es muy largo para el modelo
            texto_truncado = str(texto)[:500]
            resultado = self.detector_idioma(texto_truncado)
            # El resultado es una lista con un diccionario
            if isinstance(resultado, list) and len(resultado) > 0:
                return resultado[0]['label']
            return 'unknown'
        except Exception:
            return 'unknown'
    
    def traducir_texto(self, texto):
        """
        Traduce un texto del inglés al español.
        
        Args:
            texto (str): Texto en inglés a traducir
            
        Returns:
            str: Texto traducido al español
        """
        if not texto or pd.isna(texto):
            return texto
        
        texto_str = str(texto).strip()
        if len(texto_str) < 3:
            return texto
        
        try:
            inputs = self.tokenizer(texto_str, return_tensors="pt", padding=True, truncation=True, max_length=512)
            outputs = self.model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
            traduccion = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return traduccion
        except Exception:
            return texto  # Si falla la traducción, devolver original
    
    def traducir_dataframe(self, df, columna_texto, crear_columna_traducida=False):
        """
        Traduce textos en inglés de un DataFrame al español.
        
        Args:
            df (pd.DataFrame): DataFrame con textos
            columna_texto (str): Nombre de la columna con textos
            crear_columna_traducida (bool): Si crear una nueva columna con traducciones
            
        Returns:
            pd.DataFrame: DataFrame con textos traducidos
        """
        df_resultado = df.copy()
        
        if columna_texto not in df_resultado.columns:
            return df_resultado
        
        # Detectar textos en inglés usando el modelo unificado
        textos_validos = df_resultado[columna_texto].dropna()
        
        # Detectar idiomas usando el modelo de Hugging Face
        indices_ingles = []
        for idx, texto in textos_validos.items():
            if self.detectar_idioma(texto) == 'en':
                indices_ingles.append(idx)
        
        if len(indices_ingles) == 0:
            print("   ℹ️ No se encontraron textos en inglés para traducir")
            return df_resultado
        
        # Configurar columna de destino
        columna_destino = f"{columna_texto}_traducido" if crear_columna_traducida else columna_texto
        if crear_columna_traducida:
            df_resultado[columna_destino] = df_resultado[columna_texto]
        
        print(f"   📝 Traduciendo {len(indices_ingles)} textos EN→ES...")
        
        # Traducir textos en inglés con barra de progreso
        for idx in tqdm(indices_ingles, desc="Traduciendo textos EN→ES", unit="texto"):
            texto_original = df_resultado.loc[idx, columna_texto]
            texto_traducido = self.traducir_texto(texto_original)
            df_resultado.loc[idx, columna_destino] = texto_traducido
        
        return df_resultado
    
    def obtener_estadisticas_traduccion(self, df, columna_texto):
        """
        Obtiene estadísticas de idiomas en el DataFrame usando el modelo unificado.
        
        Args:
            df (pd.DataFrame): DataFrame con textos
            columna_texto (str): Nombre de la columna con textos
            
        Returns:
            dict: Estadísticas de idiomas detectados
        """
        if columna_texto not in df.columns:
            return {}
        
        textos_validos = df[columna_texto].dropna()
        
        # Usar el modelo unificado para detectar idiomas
        idiomas_detectados = []
        for texto in textos_validos:
            idioma = self.detectar_idioma(texto)
            idiomas_detectados.append(idioma)
        
        idiomas_series = pd.Series(idiomas_detectados)
        
        estadisticas = {
            'total_textos': len(textos_validos),
            'textos_en_ingles': (idiomas_series == 'en').sum(),
            'textos_en_espanol': (idiomas_series == 'es').sum(),
            'otros_idiomas': len(idiomas_series) - (idiomas_series == 'en').sum() - (idiomas_series == 'es').sum(),
            'distribucion_idiomas': idiomas_series.value_counts().to_dict()
        }
        
        return estadisticas