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
from tqdm import tqdm
from transformers import pipeline

import spacy
from .traductor_textos import TraductorTextos
from .filtrador_pos import FiltradorPOS

# Cargar modelos spaCy disponibles
modelos_spacy = {}
for idioma, modelo in [
    ('es', 'es_core_news_sm'),
    ('en', 'en_core_web_sm'), 
    ('pt', 'pt_core_news_sm'),
    ('fr', 'fr_core_news_sm'),
    ('it', 'it_core_news_sm')
]:
    try:
        modelos_spacy[idioma] = spacy.load(modelo)
    except OSError:
        modelos_spacy[idioma] = None

# Configurar detector de idioma con Hugging Face
detector_idioma = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")

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
        nltk.download(name)

class LimpiadorTextoMejorado:
    """
    Clase mejorada para realizar limpieza profunda de texto en opiniones turísticas.
    
    Funcionalidades:
    - Eliminación de emojis y caracteres especiales
    - Eliminación de números (enteros, decimales, con símbolos monetarios y porcentajes)
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
        
        # Inicializar filtrador POS
        self.filtrador_pos = None
    
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
        # Usar diccionario global de modelos spaCy
        self.modelos_spacy = modelos_spacy
        
        # Lematizador de NLTK como fallback
        self.lemmatizer_en = WordNetLemmatizer()
        
        # Detector de idioma
        self.detector_idioma = detector_idioma
    
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
        
        # Números (enteros, decimales y con símbolos)
        self.patron_numeros = re.compile(r'\b\d+(?:[.,]\d+)?\b|[$€¥£]\d+|\d+[%°]')
        
        # Múltiples espacios
        self.patron_espacios = re.compile(r'\s+')
        
        # Caracteres no deseados
        self.patron_caracteres_especiales = re.compile(r'[^\w\s]')
    
    def detectar_idioma(self, texto: str) -> str:
        """
        Detecta el idioma del texto usando el modelo de Hugging Face.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Código de idioma detectado (es, en, pt, fr, it, etc.)
        """
        if not texto or not texto.strip():
            return 'es'  # Default a español
        
        # Truncar texto si es muy largo para el modelo
        texto_truncado = texto[:500]  # Usar solo los primeros 500 caracteres
            
        resultado = self.detector_idioma(texto_truncado)
        return resultado[0]['label']
    
    def _inicializar_filtrador_pos(self):
        """Inicializa el filtrador POS solo cuando es necesario."""
        if self.filtrador_pos is None:
            self.filtrador_pos = FiltradorPOS()
    
    def _aplicar_traduccion_temporal(self, textos: List[str]) -> List[str]:
        """
        MÉTODO OBSOLETO: Ahora las traducciones se aplican directamente en el flujo unificado.
        Se mantiene por compatibilidad pero ya no se usa en el nuevo flujo optimizado.
        """
        print("⚠️ Método _aplicar_traduccion_temporal obsoleto - usando flujo unificado")
        return textos
    
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
        Elimina URLs, menciones, hashtags, emojis, números y caracteres especiales.
        
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
        
        # Eliminar números
        texto = self.patron_numeros.sub('', texto)
        
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
        
        texto_completo = " ".join(tokens)
        
        # Detectar idioma del texto usando Hugging Face
        idioma_detectado = self.detectar_idioma(texto_completo)
        
        # Mapear idiomas soportados
        idiomas_soportados = ['es', 'en', 'pt', 'fr', 'it']
        if idioma_detectado not in idiomas_soportados:
            idioma_detectado = 'es'  # Default a español
        
        # Seleccionar modelo según idioma detectado
        modelo_spacy = self.modelos_spacy.get(idioma_detectado)
        
        if modelo_spacy:
            # Usar spaCy para el idioma detectado
            doc = modelo_spacy(texto_completo)
            tokens_lematizados = []
            
            for token in doc:
                if token.text in tokens:  # Solo procesar tokens originales
                    lema = token.lemma_.lower().strip()
                    if lema and lema != '-PRON-' and len(lema) >= 2:
                        tokens_lematizados.append(lema)
                    else:
                        tokens_lematizados.append(token.text.lower())
        else:
            # Fallback a NLTK para inglés o cuando no hay modelo disponible
            tokens_lematizados = []
            for token in tokens:
                # Aplicar lematización para diferentes tipos de palabras
                token_lem = self.lemmatizer_en.lemmatize(token, pos='v')
                if token_lem == token:
                    token_lem = self.lemmatizer_en.lemmatize(token, pos='n')
                if token_lem == token:
                    token_lem = self.lemmatizer_en.lemmatize(token, pos='a')
                
                tokens_lematizados.append(token_lem)
        
        return tokens_lematizados
    
    def limpiar_texto(self, texto: str, 
                     aplicar_lematizacion: bool = True,
                     filtrar_adjetivos: bool = False,
                     min_longitud_palabra: int = 2,
                     max_palabras: Optional[int] = None) -> str:
        """
        Realiza limpieza completa del texto.
        
        Args:
            texto: Texto original a limpiar
            aplicar_lematizacion: Si aplicar lematización
            filtrar_adjetivos: Si filtrar adjetivos usando POS tagging
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
        
        # 3. Filtrar adjetivos si se solicita (antes de tokenizar)
        if filtrar_adjetivos:
            self._inicializar_filtrador_pos()
            if self.filtrador_pos is not None:
                texto, _ = self.filtrador_pos.filtrar_adjetivos_texto(texto)
        
        # 4. Tokenizar y filtrar
        tokens = self.tokenizar_y_filtrar(texto, min_longitud_palabra)
        
        # 5. Aplicar lematización si se solicita
        if aplicar_lematizacion:
            tokens = self.lematizar_texto_mejorado(tokens)
        
        # 6. Limitar número de palabras si se especifica
        if max_palabras and len(tokens) > max_palabras:
            tokens = tokens[:max_palabras]
        
        return " ".join(tokens)
    
    def limpiar_dataframe(self, df: pd.DataFrame, 
                         columna_texto: str,
                         nombre_columna_limpia: str = 'TituloReviewLimpio',
                         aplicar_traduccion: bool = False,
                         filtrar_adjetivos: bool = False,
                         filtrar_solo_espanol: bool = False,
                         mostrar_estadisticas: bool = True,
                         **kwargs) -> pd.DataFrame:
        """
        Aplica limpieza a una columna de DataFrame.
        
        Args:
            df: DataFrame a procesar
            columna_texto: Nombre de la columna con texto original
            nombre_columna_limpia: Nombre para la nueva columna limpia
            aplicar_traduccion: Si aplicar traducción de inglés a español
            filtrar_adjetivos: Si filtrar adjetivos usando POS tagging
            filtrar_solo_espanol: Si filtrar solo textos en español después de traducción
            mostrar_estadisticas: Si mostrar estadísticas detalladas del proceso
            **kwargs: Argumentos adicionales para limpiar_texto
            
        Returns:
            DataFrame con nueva columna de texto limpio
        """
        df_copia = df.copy()
        textos_originales = df_copia[columna_texto].dropna()
        textos_para_procesar = textos_originales.tolist()
        indices_originales = textos_originales.index.tolist()
        
        if mostrar_estadisticas:
            print(f"🔍 Procesando {len(df_copia)} opiniones totales")
            print(f"📝 Textos válidos para procesar: {len(textos_originales)}")
        
        # PASO 1: ANÁLISIS Y FILTRADO UNIFICADO DE IDIOMAS
        if aplicar_traduccion or filtrar_solo_espanol:
            if mostrar_estadisticas:
                print(f"\n🌐 ANÁLISIS UNIFICADO DE IDIOMAS:")
                print(f"   🔍 Detectando idiomas en {len(textos_originales):,} textos...")
            
            # Detectar idiomas en todos los textos de una vez
            textos_espanol = []
            textos_ingles = []
            textos_otros_idiomas = []
            indices_espanol = []
            indices_ingles = []
            idiomas_detectados = {}
            
            # Usar el detector unificado
            detector_usar = self.traductor.detectar_idioma if hasattr(self.traductor, 'detectar_idioma') else self.detectar_idioma
            
            for i, texto in enumerate(tqdm(textos_para_procesar, desc="🌐 Analizando idiomas", unit="texto")):
                if not texto or pd.isna(texto) or not str(texto).strip():
                    continue
                
                idioma = detector_usar(str(texto))
                idiomas_detectados[idioma] = idiomas_detectados.get(idioma, 0) + 1
                
                if idioma == 'es':
                    textos_espanol.append(texto)
                    indices_espanol.append(indices_originales[i])
                elif idioma == 'en':
                    textos_ingles.append(texto)
                    indices_ingles.append(indices_originales[i])
                else:
                    textos_otros_idiomas.append((idioma, texto))
            
            # Mostrar estadísticas del análisis
            if mostrar_estadisticas:
                total_procesados = len(textos_espanol) + len(textos_ingles) + len(textos_otros_idiomas)
                print(f"\n📊 RESULTADOS DEL ANÁLISIS DE IDIOMAS:")
                print(f"   ✅ Textos en español: {len(textos_espanol):,} ({len(textos_espanol)/total_procesados*100:.1f}%)")
                print(f"   🔄 Textos en inglés: {len(textos_ingles):,} ({len(textos_ingles)/total_procesados*100:.1f}%)")
                print(f"   ❌ Otros idiomas: {len(textos_otros_idiomas):,} ({len(textos_otros_idiomas)/total_procesados*100:.1f}%)")
                
                if textos_otros_idiomas and len(textos_otros_idiomas) <= 5:
                    print(f"\n🗑️ EJEMPLOS DE OTROS IDIOMAS DESCARTADOS:")
                    for i, (idioma, texto) in enumerate(textos_otros_idiomas[:3], 1):
                        print(f"      {i}. [{idioma.upper()}] '{texto[:80]}...'")
            
            # PASO 2: APLICAR TRADUCCIONES A TEXTOS EN INGLÉS
            if aplicar_traduccion and textos_ingles:
                if mostrar_estadisticas:
                    print(f"\n� TRADUCIENDO TEXTOS EN INGLÉS:")
                    print(f"   📝 Traduciendo {len(textos_ingles)} textos EN→ES...")
                
                textos_ingles_traducidos = []
                traducciones_exitosas = 0
                
                for texto in tqdm(textos_ingles, desc="🌐 Traduciendo EN→ES", unit="texto"):
                    try:
                        texto_traducido = self.traductor.traducir_texto(texto)
                        textos_ingles_traducidos.append(texto_traducido)
                        traducciones_exitosas += 1
                    except Exception:
                        # Si falla la traducción, mantener el original
                        textos_ingles_traducidos.append(texto)
                
                if mostrar_estadisticas:
                    print(f"      ✅ Traducciones exitosas: {traducciones_exitosas}/{len(textos_ingles)}")
                
                # Combinar textos en español + textos traducidos
                textos_para_procesar = textos_espanol + textos_ingles_traducidos
                indices_finales = indices_espanol + indices_ingles
            else:
                # Solo conservar textos en español si no se traduce
                textos_para_procesar = textos_espanol
                indices_finales = indices_espanol
                
                if mostrar_estadisticas and textos_ingles:
                    print(f"   ℹ️ {len(textos_ingles)} textos en inglés descartados (traducción desactivada)")
            
            # Actualizar DataFrame con índices finales
            if indices_finales:
                df_copia = df_copia.iloc[indices_finales].copy()
            
            # Mostrar resumen final del filtrado/traducción
            if mostrar_estadisticas:
                textos_finales = len(textos_para_procesar)
                textos_descartados = len(textos_originales) - textos_finales
                print(f"\n📈 RESUMEN FINAL DEL PROCESAMIENTO:")
                print(f"   📥 Textos originales: {len(textos_originales):,}")
                print(f"   ✅ Textos conservados: {textos_finales:,}")
                print(f"   🗑️ Textos descartados: {textos_descartados:,}")
                print(f"   🎯 Tasa de conservación: {(textos_finales/len(textos_originales)*100):.1f}%")
                print(f"   🌐 Detector usado: Modelo unificado Hugging Face")
        else:
            if mostrar_estadisticas:
                print(f"   ℹ️ Filtrado de idiomas desactivado - procesando todos los textos")
        
        if not textos_para_procesar:
            if mostrar_estadisticas:
                print("⚠️ No hay textos para procesar después del filtrado")
            return df_copia
        
        # Filtrar adjetivos si se solicita
        if filtrar_adjetivos:
            if mostrar_estadisticas:
                print(f"\n🏷️ FILTRANDO ADJETIVOS...")
            self._inicializar_filtrador_pos()
            if self.filtrador_pos is not None:
                textos_para_procesar, _ = self.filtrador_pos.filtrar_adjetivos_lista(
                    textos_para_procesar, 
                    mostrar_progreso=True
                )
        
        # Aplicar limpieza
        if mostrar_estadisticas:
            print(f"\n🧹 APLICANDO LIMPIEZA DE TEXTO...")
        textos_limpios = []
        for texto in tqdm(textos_para_procesar, desc="🧹 Limpiando textos", unit="texto"):
            kwargs_limpieza = {k: v for k, v in kwargs.items() if k not in ['filtrar_adjetivos', 'filtrar_solo_espanol']}
            texto_limpio = self.limpiar_texto(texto, **kwargs_limpieza)
            textos_limpios.append(texto_limpio)
        
        # Asignar textos limpios a DataFrame
        if nombre_columna_limpia in df_copia.columns:
            df_copia[nombre_columna_limpia] = textos_limpios
        else:
            try:
                loc_result = df_copia.columns.get_loc(columna_texto)
                pos_insercion = loc_result + 1 if isinstance(loc_result, int) else len(df_copia.columns)
            except:
                pos_insercion = len(df_copia.columns)
            
            if pos_insercion < len(df_copia.columns):
                df_copia.insert(pos_insercion, nombre_columna_limpia, textos_limpios)
            else:
                df_copia[nombre_columna_limpia] = textos_limpios
        
        # Verificación final de idiomas
        if filtrar_solo_espanol and mostrar_estadisticas:
            print(f"\n🔍 VERIFICACIÓN FINAL DE IDIOMAS:")
            if len(textos_limpios) > 0:
                muestra_final = pd.Series(textos_limpios).sample(n=min(20, len(textos_limpios)), random_state=42)
                idiomas_finales = {}
                
                # Usar el detector unificado para la verificación final
                detector_usar = self.traductor.detectar_idioma if hasattr(self.traductor, 'detectar_idioma') else self.detectar_idioma
                
                for texto in muestra_final:
                    idioma = detector_usar(texto)
                    idiomas_finales[idioma] = idiomas_finales.get(idioma, 0) + 1
                
                print(f"   📊 Verificación en muestra final (n={len(muestra_final)}):")
                for idioma, count in sorted(idiomas_finales.items(), key=lambda x: x[1], reverse=True):
                    pct = (count / len(muestra_final) * 100)
                    status = "✅ CORRECTO" if idioma == 'es' else "⚠️ REVISAR"
                    print(f"      {idioma.upper()}: {count} textos ({pct:.1f}%) - {status}")
                
                # Mostrar algunos ejemplos de textos conservados
                print(f"\n✅ EJEMPLOS DE TEXTOS PROCESADOS:")
                muestra_conservados = pd.Series(textos_limpios).sample(n=min(3, len(textos_limpios)), random_state=42)
                for i, texto_limpio in enumerate(muestra_conservados, 1):
                    print(f"      {i}. '{texto_limpio[:60]}...'")
                    
                print(f"   🎯 Detector usado: Modelo unificado Hugging Face (papluca/xlm-roberta-base-language-detection)")
        
        if mostrar_estadisticas:
            print(f"\n✅ PROCESAMIENTO COMPLETADO:")
            print(f"   📊 Textos finales: {len(textos_limpios):,}")
            promedio_palabras = sum(len(t.split()) for t in textos_limpios) / len(textos_limpios) if textos_limpios else 0
            print(f"   📝 Promedio palabras por texto: {promedio_palabras:.1f}")
        
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
