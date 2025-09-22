"""
Módulo mejorado para limpieza profunda de texto para análisis de tópicos

Este módulo proporciona herramientas para limpiar texto de reseñas turísticas,
eliminando ruido y normalizando el contenido para mejorar el análisis de tópicos.
Incluye soporte mejorado para lematización con detección automática de idioma
usando spaCy para español, inglés, portugués, francés e italiano.
"""

import re
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import unicodedata
from typing import List, Optional, Dict, Tuple, Any
import warnings
from langdetect import detect

import spacy
from .traductor_textos import TraductorTextos

try:
    nlp_es = spacy.load("es_core_news_sm")
    print("✓ Modelo spaCy español cargado")
except OSError:
    nlp_es = None
    print("⚠ Modelo spaCy español no disponible")

try:
    nlp_en = spacy.load("en_core_web_sm")
    print("✓ Modelo spaCy inglés cargado")
except OSError:
    nlp_en = None
    print("⚠ Modelo spaCy inglés no disponible")

try:
    nlp_pt = spacy.load("pt_core_news_sm")
    print("✓ Modelo spaCy portugués cargado")
except OSError:
    nlp_pt = None
    print("⚠ Modelo spaCy portugués no disponible")

try:
    nlp_fr = spacy.load("fr_core_news_sm")
    print("✓ Modelo spaCy francés cargado")
except OSError:
    nlp_fr = None
    print("⚠ Modelo spaCy francés no disponible")

try:
    nlp_it = spacy.load("it_core_news_sm")
    print("✓ Modelo spaCy italiano cargado")
except OSError:
    nlp_it = None
    print("⚠ Modelo spaCy italiano no disponible")

USAR_SPACY = any([nlp_es, nlp_en, nlp_pt, nlp_fr, nlp_it])

# Descargar recursos necesarios de NLTK
recursos_nltk = [
    ('tokenizers/punkt', 'punkt'),
    ('corpora/stopwords', 'stopwords'),
    ('corpora/wordnet', 'wordnet')
]

for path, name in recursos_nltk:
    try:
        nltk.data.find(path)
    except LookupError:
        print(f"Descargando {name}...")
        nltk.download(name)

class LimpiadorTextoMejorado:
    """
    Clase mejorada para realizar limpieza profunda de texto en opiniones turísticas.
    
    Funcionalidades:
    - Eliminación de emojis y caracteres especiales
    - Normalización de texto (acentos, mayúsculas)
    - Eliminación de stopwords en español e inglés
    - Lematización con detección automática de idioma usando spaCy (español, inglés, portugués, francés, italiano)
    - Eliminación de URLs, menciones y hashtags
    - Filtrado por longitud de palabras
    """
    
    def __init__(self, idiomas: List[str] = ['spanish', 'english', "portuguese", "french", "italian"]):
        """
        Inicializa el limpiador de texto.
        
        Args:
            idiomas: Lista de idiomas para stopwords (por defecto español e inglés)
        """
        self.idiomas = idiomas
        
        # Configurar stopwords
        self._configurar_stopwords()
        
        # Configurar lematizadores
        self._configurar_lematizadores()
        
        # Patrones de regex para limpieza
        self._configurar_patrones()
        
        # Inicializar traductor
        self.traductor = TraductorTextos()
    
    def _configurar_stopwords(self):
        """Configura las stopwords para múltiples idiomas."""
        self.stopwords_set = set()
        for idioma in self.idiomas:
            try:
                self.stopwords_set.update(stopwords.words(idioma))
            except:
                warnings.warn(f"No se pudieron cargar stopwords para {idioma}")
    
    def _configurar_lematizadores(self):
        """Configura los lematizadores según disponibilidad."""
        # Configurar modelos spaCy para múltiples idiomas
        self.nlp_es = nlp_es  # Español
        self.nlp_en = nlp_en  # Inglés
        self.nlp_pt = nlp_pt  # Portugués
        self.nlp_fr = nlp_fr  # Francés
        self.nlp_it = nlp_it  # Italiano
        
        # Lematizador de NLTK como fallback
        self.lemmatizer_en = WordNetLemmatizer()
    
    def _configurar_patrones(self):
        """Configura patrones de regex para limpieza."""
        # Emojis
        self.patron_emojis = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
            "\U0001F680-\U0001F6FF"  # transporte & símbolos de mapas
            "\U0001F1E0-\U0001F1FF"  # banderas (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        # URLs
        self.patron_urls = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Menciones y hashtags
        self.patron_menciones = re.compile(r'@\w+')
        self.patron_hashtags = re.compile(r'#\w+')
        
        # Múltiples espacios
        self.patron_espacios = re.compile(r'\s+')
        
        # Caracteres no deseados
        self.patron_caracteres_especiales = re.compile(r'[^\w\s]')
    
    def normalizar_texto(self, texto: str) -> str:
        """
        Normaliza el texto eliminando acentos y convirtiendo a minúsculas.
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        if not isinstance(texto, str):
            return ""
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Eliminar acentos
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
        
        return texto
    
    def eliminar_elementos_no_deseados(self, texto: str) -> str:
        """
        Elimina URLs, menciones, hashtags, emojis y caracteres especiales.
        
        Args:
            texto: Texto a limpiar
            
        Returns:
            Texto sin elementos no deseados
        """
        if not isinstance(texto, str):
            return ""
        
        # Eliminar URLs
        texto = self.patron_urls.sub('', texto)
        
        # Eliminar menciones y hashtags
        texto = self.patron_menciones.sub('', texto)
        texto = self.patron_hashtags.sub('', texto)
        
        # Eliminar emojis
        texto = self.patron_emojis.sub('', texto)
        
        # Eliminar puntuación y caracteres especiales
        texto = self.patron_caracteres_especiales.sub(' ', texto)
        
        # Normalizar espacios múltiples
        texto = self.patron_espacios.sub(' ', texto)
        
        return texto.strip()

    def tokenizar_y_filtrar(self, texto: str, min_longitud: int = 2, filtrar: bool = False) -> List[str]:
        """
        Tokeniza el texto y filtra tokens por longitud y stopwords.
        
        Args:
            texto: Texto a procesar
            min_longitud: Longitud mínima de palabras a conservar
            
        Returns:
            Lista de tokens filtrados
        """
        if filtrar:
            tokens = word_tokenize(texto, language='spanish')
            # Filtrar tokens
            tokens_filtrados = []
            for token in tokens:
                if (len(token) >= min_longitud and 
                    token not in self.stopwords_set and
                    token.isalpha()):  # Solo palabras alfabéticas
                    tokens_filtrados.append(token)

            return tokens_filtrados
        else:
            tokens = texto.split()
            return tokens
        


    def lematizar_texto_mejorado(self, tokens: List[str]) -> List[str]:
        """
        Aplica lematización mejorada usando spaCy con detección de idioma.
        
        Args:
            tokens: Lista de tokens a lematizar
            
        Returns:
            Lista de tokens lematizados
        """
        if not tokens:
            return []
        
        tokens_lematizados = []
        texto_completo = " ".join(tokens)
        
        # Detectar idioma del texto
        try:
            idioma_detectado = detect(texto_completo)
        except:
            # Si falla la detección, asumir español como predeterminado
            idioma_detectado = 'es'
        
        # Si el idioma detectado no es uno de los soportados, usar español como predeterminado
        idiomas_soportados = ['es', 'en', 'pt', 'fr', 'it']
        if idioma_detectado not in idiomas_soportados:
            idioma_detectado = 'es'
        
        # Seleccionar modelo según idioma detectado
        if idioma_detectado == 'es' and self.nlp_es:
            # Usar spaCy para español
            doc = self.nlp_es(texto_completo)
            
            for token in doc:
                if token.text in tokens:  # Solo procesar tokens originales
                    # Usar el lema si es diferente y válido
                    lema = token.lemma_.lower().strip()
                    if lema and lema != '-PRON-' and len(lema) >= 2:
                        tokens_lematizados.append(lema)
                    else:
                        tokens_lematizados.append(token.text.lower())
                        
        elif idioma_detectado == 'en' and self.nlp_en:
            # Usar spaCy para inglés
            doc = self.nlp_en(texto_completo)
            
            for token in doc:
                if token.text in tokens:  # Solo procesar tokens originales
                    # Usar el lema si es diferente y válido
                    lema = token.lemma_.lower().strip()
                    if lema and lema != '-PRON-' and len(lema) >= 2:
                        tokens_lematizados.append(lema)
                    else:
                        tokens_lematizados.append(token.text.lower())
                        
        elif idioma_detectado == 'pt' and self.nlp_pt:
            # Usar spaCy para portugués
            doc = self.nlp_pt(texto_completo)
            
            for token in doc:
                if token.text in tokens:  # Solo procesar tokens originales
                    # Usar el lema si es diferente y válido
                    lema = token.lemma_.lower().strip()
                    if lema and lema != '-PRON-' and len(lema) >= 2:
                        tokens_lematizados.append(lema)
                    else:
                        tokens_lematizados.append(token.text.lower())
                        
        elif idioma_detectado == 'fr' and self.nlp_fr:
            # Usar spaCy para francés
            doc = self.nlp_fr(texto_completo)
            
            for token in doc:
                if token.text in tokens:  # Solo procesar tokens originales
                    # Usar el lema si es diferente y válido
                    lema = token.lemma_.lower().strip()
                    if lema and lema != '-PRON-' and len(lema) >= 2:
                        tokens_lematizados.append(lema)
                    else:
                        tokens_lematizados.append(token.text.lower())
                        
        elif idioma_detectado == 'it' and self.nlp_it:
            # Usar spaCy para italiano
            doc = self.nlp_it(texto_completo)
            
            for token in doc:
                if token.text in tokens:  # Solo procesar tokens originales
                    # Usar el lema si es diferente y válido
                    lema = token.lemma_.lower().strip()
                    if lema and lema != '-PRON-' and len(lema) >= 2:
                        tokens_lematizados.append(lema)
                    else:
                        tokens_lematizados.append(token.text.lower())
        else:
            # Fallback a NLTK para inglés o cuando no hay modelo disponible
            for token in tokens:
                try:
                    # Aplicar lematización para diferentes tipos de palabras
                    token_lem = self.lemmatizer_en.lemmatize(token, pos='v')
                    if token_lem == token:
                        token_lem = self.lemmatizer_en.lemmatize(token, pos='n')
                    if token_lem == token:
                        token_lem = self.lemmatizer_en.lemmatize(token, pos='a')
                    
                    tokens_lematizados.append(token_lem)
                except:
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
        if not isinstance(texto, str) or not texto.strip():
            return ""
        
        # 1. Eliminar elementos no deseados
        texto = self.eliminar_elementos_no_deseados(texto)
        
        # 2. Normalizar texto
        texto = self.normalizar_texto(texto)
        
        # 3. Tokenizar y filtrar
        tokens = self.tokenizar_y_filtrar(texto, min_longitud_palabra)
        
        # 4. Aplicar lematización si se solicita
        if aplicar_lematizacion:
            tokens = self.lematizar_texto_mejorado(tokens)
        
        # 5. Limitar número de palabras si se especifica
        if max_palabras and len(tokens) > max_palabras:
            tokens = tokens[:max_palabras]
        
        return " ".join(tokens)
    
    def limpiar_dataframe(self, df: pd.DataFrame, 
                         columna_texto: str,
                         nombre_columna_limpia: str = 'TituloReviewLimpio',
                         aplicar_traduccion: bool = False,
                         **kwargs) -> pd.DataFrame:
        """
        Aplica limpieza a una columna de DataFrame.
        
        Args:
            df: DataFrame a procesar
            columna_texto: Nombre de la columna con texto original
            nombre_columna_limpia: Nombre para la nueva columna limpia
            aplicar_traduccion: Si aplicar traducción de inglés a español
            **kwargs: Argumentos adicionales para limpiar_texto
            
        Returns:
            DataFrame con nueva columna de texto limpio
        """
        df_copia = df.copy()
        
        # Aplicar traducción si se solicita
        if aplicar_traduccion:
            print(f"🌐 Aplicando traducción EN→ES...")
            estadisticas_idioma = self.traductor.obtener_estadisticas_traduccion(df_copia, columna_texto)
            
            if estadisticas_idioma.get('textos_en_ingles', 0) > 0:
                print(f"   Textos en inglés detectados: {estadisticas_idioma['textos_en_ingles']}")
                print(f"   Total textos: {estadisticas_idioma['total_textos']}")
                df_copia = self.traductor.traducir_dataframe(df_copia, columna_texto)
                print(f"✅ Traducción completada")
            else:
                print(f"   No se encontraron textos en inglés para traducir")
        
        print(f"🧹 Limpiando columna '{columna_texto}'...")
        print(f"Procesando {len(df_copia)} textos...")
        
        # Aplicar limpieza
        textos_limpios = []
        for i, texto in enumerate(df_copia[columna_texto]):
            if i % 100 == 0:
                print(f"Procesado: {i}/{len(df_copia)} textos")
            
            texto_limpio = self.limpiar_texto(texto, **kwargs)
            textos_limpios.append(texto_limpio)
        
        # Verificar si la columna ya existe
        if nombre_columna_limpia in df_copia.columns:
            df_copia[nombre_columna_limpia] = textos_limpios
            print(f"✓ Columna '{nombre_columna_limpia}' actualizada")
        else:
            try:
                loc_result = df_copia.columns.get_loc(columna_texto)
                if isinstance(loc_result, int):
                    pos_insercion = loc_result + 1
                else:
                    pos_insercion = len(df_copia.columns)
            except:
                pos_insercion = len(df_copia.columns)
            
            if pos_insercion < len(df_copia.columns):
                df_copia.insert(pos_insercion, nombre_columna_limpia, textos_limpios)
            else:
                df_copia[nombre_columna_limpia] = textos_limpios
            
            print(f"✓ Nueva columna '{nombre_columna_limpia}' creada")
        
        # Estadísticas de limpieza
        textos_vacios = sum(1 for texto in textos_limpios if not texto.strip())
        textos_validos = len(textos_limpios) - textos_vacios
        
        # Estadísticas de longitud
        longitudes_originales = [len(str(texto).split()) for texto in df_copia[columna_texto]]
        longitudes_limpias = [len(texto.split()) for texto in textos_limpios if texto.strip()]
        
        promedio_original = sum(longitudes_originales) / len(longitudes_originales) if longitudes_originales else 0
        promedio_limpio = sum(longitudes_limpias) / len(longitudes_limpias) if longitudes_limpias else 0
        
        print(f"\n📊 Estadísticas de limpieza:")
        print(f"   • Textos procesados: {len(textos_limpios)}")
        print(f"   • Textos válidos: {textos_validos}")
        print(f"   • Textos vacíos: {textos_vacios}")
        print(f"   • Promedio palabras original: {promedio_original:.1f}")
        print(f"   • Promedio palabras limpio: {promedio_limpio:.1f}")
        print(f"   • Reducción promedio: {((promedio_original - promedio_limpio) / promedio_original * 100):.1f}%")
        
        return df_copia
    
    def obtener_estadisticas_limpieza(self, texto_original: str, texto_limpio: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas de comparación entre texto original y limpio.
        
        Args:
            texto_original: Texto antes de limpiar
            texto_limpio: Texto después de limpiar
            
        Returns:
            Diccionario con estadísticas
        """
        stats = {
            'longitud_original': len(texto_original),
            'longitud_limpia': len(texto_limpio),
            'palabras_original': len(texto_original.split()),
            'palabras_limpia': len(texto_limpio.split()),
            'reduccion_caracteres': len(texto_original) - len(texto_limpio),
            'reduccion_palabras': len(texto_original.split()) - len(texto_limpio.split()),
            'porcentaje_reduccion_palabras': 0.0
        }
        
        if stats['palabras_original'] > 0:
            stats['porcentaje_reduccion_palabras'] = (stats['reduccion_palabras'] / stats['palabras_original']) * 100
            
        return stats
