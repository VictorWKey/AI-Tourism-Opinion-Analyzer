"""
Generador de Análisis de Texto
================================
Sección 6: Texto (visualizaciones gráficas puras)
- Word cloud general
- Distribución de longitud de textos (histograma + box plot)
- Top bigramas (pares de palabras) - bar chart
- Top trigramas (tríos de palabras) - bar chart

Nota: Los resúmenes inteligentes (descriptivo, estructurado, insights)
se exportan ahora como datos JSON mediante ExportadorInsights para
ser mostrados en una sección separada de la UI.
"""

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from collections import Counter
from pathlib import Path
from typing import List
import re
from .utils import COLORES, ESTILOS, guardar_figura
from .i18n import get_translator


class GeneradorTexto:
    """Genera visualizaciones gráficas de análisis de texto."""
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '06_texto'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Descargar stopwords si no están
        try:
            stopwords.words('spanish')
        except:
            nltk.download('stopwords', quiet=True)
        
        # Stopwords multilingües ampliadas
        idiomas = ["spanish", "english", "portuguese", "french", "italian"]
        self.stopwords = set()
        for idioma in idiomas:
            try:
                self.stopwords.update(stopwords.words(idioma))
            except:
                pass
        
        # Agregar stopwords adicionales específicas del dominio turístico
        self.stopwords.update([
            'si', 'no', 'muy', 'más', 'mas', 'ya', 'bien', 'todo', 'toda', 'todos', 'todas',
            'pero', 'también', 'tambien', 'aunque', 'solo', 'sólo', 'así', 'asi', 'ser',
            'estar', 'hacer', 'tener', 'poder', 'ir', 'ver', 'dar', 'saber', 'querer',
            'the', 'is', 'it', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'uno', 'una', 'unos', 'unas', 'este', 'esta', 'esto', 'ese', 'esa', 'eso',
            'del', 'al', 'los', 'las', 'les', 'nos', 'era', 'fue', 'son', 'están',
        ])
    
    def generar_todas(self) -> List[str]:
        """Genera todas las visualizaciones gráficas de texto."""
        generadas = []
        
        # 6.1 Word cloud general
        if self.validador.puede_renderizar('wordcloud_general')[0]:
            self._generar_wordcloud_general()
            generadas.append('wordcloud_general')
        
        # 6.2 Distribución de longitud
        if self.validador.puede_renderizar('distribucion_longitud')[0]:
            self._generar_distribucion_longitud()
            generadas.append('distribucion_longitud')
        
        # 6.3 Top bigramas
        if self.validador.puede_renderizar('top_bigramas')[0]:
            self._generar_top_bigramas()
            generadas.append('top_bigramas')
        
        # 6.4 Top trigramas
        if self.validador.puede_renderizar('top_trigramas')[0]:
            self._generar_top_trigramas()
            generadas.append('top_trigramas')
        
        return generadas
    
    def _limpiar_texto(self, texto: str) -> str:
        """Limpia y normaliza un texto."""
        if pd.isna(texto):
            return ''
        texto = str(texto).lower()
        # Eliminar URLs
        texto = re.sub(r'http\S+|www\.\S+', '', texto)
        # Eliminar caracteres especiales pero mantener acentos
        texto = re.sub(r'[^\w\sáéíóúñü]', ' ', texto)
        # Eliminar números
        texto = re.sub(r'\d+', '', texto)
        # Eliminar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    
    def _obtener_palabras(self, texto: str) -> List[str]:
        """Obtiene palabras filtradas de un texto."""
        texto = self._limpiar_texto(texto)
        palabras = texto.split()
        return [p for p in palabras if len(p) > 2 and p not in self.stopwords]
    
    def _obtener_todos_textos(self) -> str:
        """Obtiene todo el texto del dataset."""
        columna = 'TituloReview' if 'TituloReview' in self.df.columns else 'Review'
        textos = self.df[columna].dropna()
        return ' '.join(textos.astype(str))
    
    def _generar_wordcloud_general(self):
        """6.1 Word Cloud General de todas las opiniones."""
        texto_completo = self._obtener_todos_textos()
        texto_limpio = self._limpiar_texto(texto_completo)
        
        # Filtrar stopwords
        palabras = [p for p in texto_limpio.split() if len(p) > 2 and p not in self.stopwords]
        texto_filtrado = ' '.join(palabras)
        
        if not texto_filtrado.strip():
            return
        
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=COLORES['fondo'])
        
        wc = WordCloud(
            width=1400,
            height=800,
            background_color=COLORES['fondo'],
            colormap='viridis',
            max_words=150,
            min_font_size=10,
            max_font_size=100,
            random_state=42,
            collocations=False
        ).generate(texto_filtrado)
        
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        t = get_translator()
        ax.set_title(t('wordcloud_general'), **ESTILOS['titulo'], pad=20)
        
        guardar_figura(fig, self.output_dir / 'wordcloud_general.png')
    
    def _generar_distribucion_longitud(self):
        """6.2 Distribución de Longitud de Textos."""
        columna = 'TituloReview' if 'TituloReview' in self.df.columns else 'Review'
        
        longitudes = self.df[columna].dropna().apply(lambda x: len(str(x).split()))
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=COLORES['fondo'])
        
        t = get_translator()
        
        # Histograma
        ax1 = axes[0]
        ax1.hist(longitudes, bins=30, color=COLORES['primario'], alpha=0.7, edgecolor=COLORES['borde_separador'])
        ax1.axvline(longitudes.mean(), color=COLORES['negativo'], linestyle='--', linewidth=2, label=t('media_valor', value=f'{longitudes.mean():.1f}'))
        ax1.axvline(longitudes.median(), color=COLORES['positivo'], linestyle='--', linewidth=2, label=t('mediana_valor', value=f'{longitudes.median():.1f}'))
        ax1.set_xlabel(t('cantidad_palabras'), **ESTILOS['etiquetas'])
        ax1.set_ylabel(t('frecuencia'), **ESTILOS['etiquetas'])
        ax1.set_title(t('distribucion_longitud'), **ESTILOS['titulo'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Box plot
        ax2 = axes[1]
        bp = ax2.boxplot(longitudes, patch_artist=True)
        bp['boxes'][0].set_facecolor(COLORES['primario'])
        bp['boxes'][0].set_alpha(0.7)
        bp['medians'][0].set_color(COLORES['negativo'])
        bp['medians'][0].set_linewidth(2)
        ax2.set_ylabel(t('cantidad_palabras'), **ESTILOS['etiquetas'])
        ax2.set_title(t('diagrama_caja_longitud'), **ESTILOS['titulo'])
        ax2.grid(True, axis='y', alpha=0.3)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'distribucion_longitud.png')
    
    def _generar_ngramas(self, n: int) -> List[tuple]:
        """Genera n-gramas más frecuentes."""
        columna = 'TituloReview' if 'TituloReview' in self.df.columns else 'Review'
        
        todos_ngramas = []
        for texto in self.df[columna].dropna():
            palabras = self._obtener_palabras(str(texto))
            if len(palabras) >= n:
                ngramas = list(zip(*[palabras[i:] for i in range(n)]))
                todos_ngramas.extend(ngramas)
        
        return Counter(todos_ngramas).most_common(20)
    
    def _generar_top_bigramas(self):
        """6.3 Top 20 Bigramas más frecuentes."""
        bigramas = self._generar_ngramas(2)
        
        if not bigramas:
            return
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORES['fondo'])
        
        etiquetas = [f'{b[0]} {b[1]}' for b, _ in bigramas]
        valores = [c for _, c in bigramas]
        colores = plt.cm.viridis([i/len(bigramas) for i in range(len(bigramas))])
        
        bars = ax.barh(range(len(bigramas)), valores, color=colores, 
                       edgecolor=COLORES['borde_separador'], linewidth=0.5)
        ax.set_yticks(range(len(bigramas)))
        ax.set_yticklabels(etiquetas)
        ax.invert_yaxis()
        t = get_translator()
        ax.set_xlabel(t('frecuencia'), **ESTILOS['etiquetas'])
        ax.set_title(t('top_bigramas'), **ESTILOS['titulo'])
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Añadir valores en las barras
        for bar, val in zip(bars, valores):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(val), va='center', fontsize=9)
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'top_bigramas.png')
    
    def _generar_top_trigramas(self):
        """6.4 Top 20 Trigramas más frecuentes."""
        trigramas = self._generar_ngramas(3)
        
        if not trigramas:
            return
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORES['fondo'])
        
        etiquetas = [f'{t[0]} {t[1]} {t[2]}' for t, _ in trigramas]
        valores = [c for _, c in trigramas]
        colores = plt.cm.plasma([i/len(trigramas) for i in range(len(trigramas))])
        
        bars = ax.barh(range(len(trigramas)), valores, color=colores,
                       edgecolor=COLORES['borde_separador'], linewidth=0.5)
        ax.set_yticks(range(len(trigramas)))
        ax.set_yticklabels(etiquetas)
        ax.invert_yaxis()
        t = get_translator()
        ax.set_xlabel(t('frecuencia'), **ESTILOS['etiquetas'])
        ax.set_title(t('top_trigramas'), **ESTILOS['titulo'])
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Añadir valores en las barras
        for bar, val in zip(bars, valores):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(val), va='center', fontsize=9)
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'top_trigramas.png')
