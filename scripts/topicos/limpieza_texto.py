"""
Módulo para limpieza profunda de texto para análisis de tópicos

Este módulo proporciona herramientas para limpiar texto de reseñas turísticas,
eliminando ruido y normalizando el contenido para mejorar el análisis de tópicos.
"""

import re
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
import unicodedata
from typing import List, Optional
import warnings

class LimpiadorTexto:
    """
    Clase para realizar limpieza profunda de texto en opiniones turísticas.
    
    Funcionalidades:
    - Eliminación de emojis y caracteres especiales
    - Normalización de texto (acentos, mayúsculas)
    - Eliminación de stopwords en español e inglés
    - Lematización y stemming
    - Eliminación de URLs, menciones y hashtags
    - Filtrado por longitud de palabras
    """
    
    def __init__(self, idiomas: List[str] = ['spanish', 'english']):
        """
        Inicializa el limpiador de texto.
        
        Args:
            idiomas: Lista de idiomas para stopwords (por defecto español e inglés)
        """
        self.idiomas = idiomas
        self._descargar_recursos_nltk()
        self._configurar_herramientas()
        
    def _descargar_recursos_nltk(self):
        """Descarga los recursos necesarios de NLTK."""
        recursos_nltk = [
            'stopwords',
            'punkt',
            'wordnet',
            'omw-1.4',
            'punkt_tab'
        ]
        
        for recurso in recursos_nltk:
            try:
                nltk.download(recurso, quiet=True)
            except Exception as e:
                warnings.warn(f"No se pudo descargar {recurso}: {e}")
    
    def _configurar_herramientas(self):
        """Configura las herramientas de procesamiento de texto."""
        # Stopwords para múltiples idiomas
        self.stopwords_set = set()
        for idioma in self.idiomas:
            try:
                self.stopwords_set.update(stopwords.words(idioma))
            except Exception as e:
                warnings.warn(f"No se pudieron cargar stopwords para {idioma}: {e}")
        
        # Stopwords adicionales específicas para turismo
        stopwords_turismo = {
            # Español
            'muy', 'todo', 'bien', 'mal', 'si', 'no', 'vez', 'veces', 'lugar', 'sitio',
            'día', 'días', 'hora', 'horas', 'momento', 'tiempo', 'gente', 'persona',
            'personas', 'cosa', 'cosas', 'parte', 'gracias', 'favor', 'verdad',
            'además', 'tampoco', 'quizás', 'tal', 'tanto', 'tan', 'más', 'menos',
            # Inglés
            'really', 'very', 'quite', 'pretty', 'just', 'time', 'place', 'thing',
            'things', 'way', 'people', 'person', 'day', 'days', 'hour', 'hours',
            'moment', 'thanks', 'thank', 'maybe', 'perhaps', 'actually', 'definitely'
        }
        self.stopwords_set.update(stopwords_turismo)
        
        # Herramientas de procesamiento
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer_es = SnowballStemmer('spanish')
        self.stemmer_en = SnowballStemmer('english')
        
        # Patrones de expresiones regulares
        self.patron_emoji = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # símbolos y pictogramas
            "\U0001F680-\U0001F6FF"  # transporte y mapas
            "\U0001F1E0-\U0001F1FF"  # banderas
            "\U00002702-\U000027B0"  # otros símbolos
            "\U000024C2-\U0001F251"  # símbolos adicionales
            "]+", flags=re.UNICODE
        )
        
        self.patron_url = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.patron_mencion = re.compile(r'@\w+')
        self.patron_hashtag = re.compile(r'#\w+')
        self.patron_numeros = re.compile(r'\b\d+\b')
        self.patron_espacios = re.compile(r'\s+')
    
    def eliminar_emojis(self, texto: str) -> str:
        """Elimina emojis del texto."""
        return self.patron_emoji.sub('', texto)
    
    def eliminar_urls_menciones(self, texto: str) -> str:
        """Elimina URLs, menciones y hashtags."""
        texto = self.patron_url.sub('', texto)
        texto = self.patron_mencion.sub('', texto)
        texto = self.patron_hashtag.sub('', texto)
        return texto
    
    def normalizar_texto(self, texto: str) -> str:
        """
        Normaliza el texto eliminando acentos y convirtiendo a minúsculas.
        """
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Eliminar acentos
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
        
        return texto
    
    def eliminar_puntuacion(self, texto: str) -> str:
        """Elimina signos de puntuación."""
        # Crear tabla de traducción para eliminar puntuación
        translator = str.maketrans('', '', string.punctuation + '¡¿""''…–—«»')
        return texto.translate(translator)
    
    def tokenizar_y_filtrar(self, texto: str, min_longitud: int = 2) -> List[str]:
        """
        Tokeniza el texto y filtra palabras cortas y stopwords.
        
        Args:
            texto: Texto a procesar
            min_longitud: Longitud mínima de palabras a conservar
            
        Returns:
            Lista de tokens filtrados
        """
        try:
            tokens = word_tokenize(texto, language='spanish')
        except:
            # Fallback a separación por espacios si falla la tokenización
            tokens = texto.split()
        
        # Filtrar tokens
        tokens_filtrados = []
        for token in tokens:
            if (len(token) >= min_longitud and 
                token not in self.stopwords_set and
                token.isalpha()):  # Solo palabras alfabéticas
                tokens_filtrados.append(token)
        
        return tokens_filtrados
    
    def lematizar_texto(self, tokens: List[str]) -> List[str]:
        """
        Aplica lematización a los tokens usando WordNetLemmatizer.
        
        Args:
            tokens: Lista de tokens a lematizar
            
        Returns:
            Lista de tokens lematizados
        """
        tokens_lematizados = []
        for token in tokens:
            try:
                # Aplicar lematización para diferentes tipos de palabras
                # Intentar como verbo
                token_lem = self.lemmatizer.lemmatize(token, pos='v')
                # Si no cambió, intentar como sustantivo
                if token_lem == token:
                    token_lem = self.lemmatizer.lemmatize(token, pos='n')
                # Si no cambió, intentar como adjetivo
                if token_lem == token:
                    token_lem = self.lemmatizer.lemmatize(token, pos='a')
                # Si no cambió, intentar como adverbio
                if token_lem == token:
                    token_lem = self.lemmatizer.lemmatize(token, pos='r')
                
                tokens_lematizados.append(token_lem)
            except:
                # Si falla, mantener el token original
                tokens_lematizados.append(token)
        
        return tokens_lematizados
    
    def limpiar_texto(self, texto: str, 
                     aplicar_lematizacion: bool = True,
                     min_longitud_palabra: int = 2,
                     max_palabras: Optional[int] = None) -> str:
        """
        Realiza limpieza completa del texto.
        
        Args:
            texto: Texto original a limpiar
            aplicar_lematizacion: Si aplicar lematización
            min_longitud_palabra: Longitud mínima de palabras
            max_palabras: Número máximo de palabras (None = sin límite)
            
        Returns:
            Texto limpio
        """
        if pd.isna(texto) or not isinstance(texto, str):
            return ""
        
        # Paso 1: Eliminar elementos no deseados
        texto_limpio = self.eliminar_emojis(texto)
        texto_limpio = self.eliminar_urls_menciones(texto_limpio)
        
        # Paso 2: Normalizar
        texto_limpio = self.normalizar_texto(texto_limpio)
        
        # Paso 3: Eliminar números si no son relevantes
        texto_limpio = self.patron_numeros.sub('', texto_limpio)
        
        # Paso 4: Eliminar puntuación
        texto_limpio = self.eliminar_puntuacion(texto_limpio)
        
        # Paso 5: Normalizar espacios
        texto_limpio = self.patron_espacios.sub(' ', texto_limpio).strip()
        
        # Paso 6: Tokenizar y filtrar
        tokens = self.tokenizar_y_filtrar(texto_limpio, min_longitud_palabra)
        
        # Paso 7: Lematización (opcional)
        if aplicar_lematizacion and tokens:
            tokens = self.lematizar_texto(tokens)
        
        # Paso 8: Limitar número de palabras (opcional)
        if max_palabras and len(tokens) > max_palabras:
            tokens = tokens[:max_palabras]
        
        # Paso 9: Filtrar tokens vacíos y reconstruir texto
        tokens_finales = [token for token in tokens if token and len(token.strip()) > 0]
        
        return ' '.join(tokens_finales)
    
    def limpiar_dataframe(self, df: pd.DataFrame, 
                         columna_texto: str,
                         nombre_columna_limpia: str = 'TituloReviewLimpio',
                         **kwargs) -> pd.DataFrame:
        """
        Limpia una columna de texto en un DataFrame.
        
        Args:
            df: DataFrame con los datos
            columna_texto: Nombre de la columna con texto original
            nombre_columna_limpia: Nombre para la columna con texto limpio
            **kwargs: Argumentos adicionales para limpiar_texto()
            
        Returns:
            DataFrame con la nueva columna de texto limpio
        """
        df_copia = df.copy()
        
        print(f"🧹 Iniciando limpieza de texto...")
        print(f"📊 Total de textos a procesar: {len(df_copia)}")
        
        # Aplicar limpieza
        textos_limpios = []
        for i, texto in enumerate(df_copia[columna_texto]):
            if i % 1000 == 0 and i > 0:
                print(f"   Procesados: {i}/{len(df_copia)}")
            
            texto_limpio = self.limpiar_texto(texto, **kwargs)
            textos_limpios.append(texto_limpio)
        
        # Agregar o actualizar columna limpia al lado de la original
        if nombre_columna_limpia in df_copia.columns:
            # Si la columna ya existe, actualizarla
            print(f"⚠️ Columna '{nombre_columna_limpia}' ya existe, sobrescribiendo...")
            df_copia[nombre_columna_limpia] = textos_limpios
        else:
            # Si no existe, insertarla después de la columna original
            pos_columna_original = df_copia.columns.get_loc(columna_texto)
            
            # Asegurar que pos_columna_original es un entero
            if isinstance(pos_columna_original, int):
                pos_insercion = pos_columna_original + 1
            else:
                # Si get_loc devuelve algo que no es int, buscar la posición manualmente
                pos_insercion = list(df_copia.columns).index(columna_texto) + 1
            
            # Insertar nueva columna después de la original
            df_copia.insert(pos_insercion, nombre_columna_limpia, textos_limpios)
        
        # Estadísticas de limpieza
        textos_vacios = sum(1 for texto in textos_limpios if not texto.strip())
        textos_validos = len(textos_limpios) - textos_vacios
        
        print(f"✅ Limpieza completada:")
        print(f"   📝 Textos válidos: {textos_validos}")
        print(f"   🚫 Textos vacíos tras limpieza: {textos_vacios}")
        print(f"   📊 Tasa de éxito: {textos_validos/len(textos_limpios)*100:.1f}%")
        
        return df_copia
    
    def obtener_estadisticas_limpieza(self, texto_original: str, texto_limpio: str) -> dict:
        """
        Calcula estadísticas de la limpieza aplicada.
        
        Args:
            texto_original: Texto antes de limpiar
            texto_limpio: Texto después de limpiar
            
        Returns:
            Diccionario con estadísticas
        """
        if pd.isna(texto_original):
            texto_original = ""
        if pd.isna(texto_limpio):
            texto_limpio = ""
            
        palabras_originales = len(texto_original.split()) if texto_original else 0
        palabras_limpias = len(texto_limpio.split()) if texto_limpio else 0
        
        return {
            'longitud_original': len(texto_original),
            'longitud_limpia': len(texto_limpio),
            'palabras_originales': palabras_originales,
            'palabras_limpias': palabras_limpias,
            'reduccion_longitud': len(texto_original) - len(texto_limpio),
            'reduccion_palabras': palabras_originales - palabras_limpias,
            'porcentaje_reduccion': ((len(texto_original) - len(texto_limpio)) / len(texto_original) * 100) if len(texto_original) > 0 else 0
        }
