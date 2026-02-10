"""
Generador de Análisis de Texto
================================
Sección 6: Texto (visualizaciones)
- Word cloud general
- Distribución de longitud de textos
- Top bigramas (pares de palabras)
- Top trigramas (tríos de palabras)
- Resúmenes inteligentes (si existen)
"""

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from collections import Counter
from pathlib import Path
from typing import List, Dict
import re
import json
import textwrap
from .utils import COLORES, ESTILOS, guardar_figura


class GeneradorTexto:
    """Genera visualizaciones de análisis de texto."""
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '06_texto'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ruta al archivo de resúmenes (use ConfigDataset for dynamic path)
        from config.config import ConfigDataset
        self.resumenes_path = ConfigDataset.get_shared_dir() / 'resumenes.json'
        
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
        """Genera todas las visualizaciones de texto."""
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
        
        # 6.5-6.7 Resúmenes inteligentes (si existen)
        if self.resumenes_path.exists():
            try:
                resumenes_generados = self._generar_resumenes_visuales()
                generadas.extend(resumenes_generados)
            except Exception as e:
                print(f"   ⚠️  Error generando resúmenes: {e}")
        
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
        
        fig, ax = plt.subplots(figsize=(14, 8), facecolor='white')
        
        wc = WordCloud(
            width=1400,
            height=800,
            background_color='white',
            colormap='viridis',
            max_words=150,
            min_font_size=10,
            max_font_size=100,
            random_state=42,
            collocations=False
        ).generate(texto_filtrado)
        
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Nube de Palabras - Todas las Opiniones', **ESTILOS['titulo'], pad=20)
        
        guardar_figura(fig, self.output_dir / 'wordcloud_general.png')
    
    def _generar_distribucion_longitud(self):
        """6.2 Distribución de Longitud de Textos."""
        columna = 'TituloReview' if 'TituloReview' in self.df.columns else 'Review'
        
        longitudes = self.df[columna].dropna().apply(lambda x: len(str(x).split()))
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor='white')
        
        # Histograma
        ax1 = axes[0]
        ax1.hist(longitudes, bins=30, color=COLORES['primario'], alpha=0.7, edgecolor='white')
        ax1.axvline(longitudes.mean(), color=COLORES['negativo'], linestyle='--', linewidth=2, label=f'Media: {longitudes.mean():.1f}')
        ax1.axvline(longitudes.median(), color=COLORES['positivo'], linestyle='--', linewidth=2, label=f'Mediana: {longitudes.median():.1f}')
        ax1.set_xlabel('Cantidad de palabras', **ESTILOS['etiquetas'])
        ax1.set_ylabel('Frecuencia', **ESTILOS['etiquetas'])
        ax1.set_title('Distribución de Longitud de Textos', **ESTILOS['titulo'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        ax2 = axes[1]
        bp = ax2.boxplot(longitudes, patch_artist=True)
        bp['boxes'][0].set_facecolor(COLORES['primario'])
        bp['boxes'][0].set_alpha(0.7)
        ax2.set_ylabel('Cantidad de palabras', **ESTILOS['etiquetas'])
        ax2.set_title('Diagrama de Caja - Longitud', **ESTILOS['titulo'])
        ax2.grid(True, axis='y', alpha=0.3)
        
        # Estadísticas
        stats_text = f"Min: {longitudes.min()}\nMax: {longitudes.max()}\nMedia: {longitudes.mean():.1f}\nStd: {longitudes.std():.1f}"
        ax2.text(1.3, longitudes.median(), stats_text, fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
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
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')
        
        etiquetas = [f'{b[0]} {b[1]}' for b, _ in bigramas]
        valores = [c for _, c in bigramas]
        colores = plt.cm.viridis([i/len(bigramas) for i in range(len(bigramas))])
        
        bars = ax.barh(range(len(bigramas)), valores, color=colores)
        ax.set_yticks(range(len(bigramas)))
        ax.set_yticklabels(etiquetas)
        ax.invert_yaxis()
        ax.set_xlabel('Frecuencia', **ESTILOS['etiquetas'])
        ax.set_title('Top 20 Bigramas Más Frecuentes', **ESTILOS['titulo'])
        ax.grid(True, axis='x', alpha=0.3)
        
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
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')
        
        etiquetas = [f'{t[0]} {t[1]} {t[2]}' for t, _ in trigramas]
        valores = [c for _, c in trigramas]
        colores = plt.cm.plasma([i/len(trigramas) for i in range(len(trigramas))])
        
        bars = ax.barh(range(len(trigramas)), valores, color=colores)
        ax.set_yticks(range(len(trigramas)))
        ax.set_yticklabels(etiquetas)
        ax.invert_yaxis()
        ax.set_xlabel('Frecuencia', **ESTILOS['etiquetas'])
        ax.set_title('Top 20 Trigramas Más Frecuentes', **ESTILOS['titulo'])
        ax.grid(True, axis='x', alpha=0.3)
        
        # Añadir valores en las barras
        for bar, val in zip(bars, valores):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(val), va='center', fontsize=9)
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'top_trigramas.png')
    
    def _generar_resumenes_visuales(self) -> List[str]:
        """Genera visualizaciones de los resúmenes inteligentes."""
        generadas = []
        
        try:
            with open(self.resumenes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            resumenes = data.get('resumenes', {})
            
            # 6.5 Resumen Descriptivo
            if 'descriptivo' in resumenes:
                self._generar_resumen_descriptivo(resumenes['descriptivo'])
                generadas.append('resumen_descriptivo')
            
            # 6.6 Resumen Estructurado
            if 'estructurado' in resumenes:
                self._generar_resumen_estructurado(resumenes['estructurado'])
                generadas.append('resumen_estructurado')
            
            # 6.7 Insights Estratégicos
            if 'insights' in resumenes:
                self._generar_insights_estrategicos(resumenes['insights'])
                generadas.append('resumen_insights')
        
        except Exception as e:
            print(f"   ⚠️  Error leyendo resúmenes: {e}")
        
        return generadas
    
    def _crear_caja_texto(self, ax, texto: str, titulo: str, posicion: tuple = (0.5, 0.5), 
                          ancho: float = 0.9, color: str = 'lightblue'):
        """Crea una caja de texto formateada en un eje."""
        # Envolver texto
        wrapped = textwrap.fill(texto, width=100)
        
        # Caja de texto
        ax.text(posicion[0], posicion[1], wrapped, 
                ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round,pad=1', facecolor=color, alpha=0.3, edgecolor='gray'),
                wrap=True)
        
        # Título
        ax.text(posicion[0], 0.95, titulo, 
                ha='center', va='top', fontsize=14, fontweight='bold')
        
        ax.axis('off')
    
    def _generar_resumen_descriptivo(self, descriptivo: Dict):
        """6.5 Genera visualización del resumen descriptivo."""
        # Resumen global
        if 'global' in descriptivo:
            fig = plt.figure(figsize=(16, 10), facecolor='white')
            fig.suptitle('Resumen Descriptivo - Global', fontsize=18, fontweight='bold', y=0.98)
            
            ax = fig.add_subplot(111)
            self._crear_caja_texto(ax, descriptivo['global'], '', (0.5, 0.45), color='#E8F4F8')
            
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            guardar_figura(fig, self.output_dir / 'resumen_descriptivo_global.png')
        
        # Resumen por categoría (crear múltiples páginas si es necesario)
        if 'por_categoria' in descriptivo:
            categorias = list(descriptivo['por_categoria'].items())
            
            # Dividir en grupos de 3 categorías por página
            for i in range(0, len(categorias), 3):
                batch = categorias[i:i+3]
                num_cats = len(batch)
                
                fig = plt.figure(figsize=(16, 4 * num_cats), facecolor='white')
                fig.suptitle(f'Resumen Descriptivo - Por Categoría (Parte {i//3 + 1})', 
                           fontsize=18, fontweight='bold', y=0.99)
                
                for idx, (categoria, texto) in enumerate(batch):
                    ax = fig.add_subplot(num_cats, 1, idx + 1)
                    self._crear_caja_texto(ax, texto, categoria, (0.5, 0.5), color='#FFF4E6')
                
                plt.tight_layout(rect=[0, 0, 1, 0.98])
                guardar_figura(fig, self.output_dir / f'resumen_descriptivo_categorias_{i//3 + 1}.png')
    
    def _generar_resumen_estructurado(self, estructurado: Dict):
        """6.6 Genera visualización del resumen estructurado."""
        # Resumen global
        if 'global' in estructurado:
            fig = plt.figure(figsize=(16, 10), facecolor='white')
            fig.suptitle('Resumen Estructurado - Global', fontsize=18, fontweight='bold', y=0.98)
            
            ax = fig.add_subplot(111)
            self._crear_caja_texto(ax, estructurado['global'], '', (0.5, 0.45), color='#F0F8E8')
            
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            guardar_figura(fig, self.output_dir / 'resumen_estructurado_global.png')
        
        # Resumen por categoría
        if 'por_categoria' in estructurado:
            categorias = list(estructurado['por_categoria'].items())
            
            for i in range(0, len(categorias), 3):
                batch = categorias[i:i+3]
                num_cats = len(batch)
                
                fig = plt.figure(figsize=(16, 4 * num_cats), facecolor='white')
                fig.suptitle(f'Resumen Estructurado - Por Categoría (Parte {i//3 + 1})', 
                           fontsize=18, fontweight='bold', y=0.99)
                
                for idx, (categoria, texto) in enumerate(batch):
                    ax = fig.add_subplot(num_cats, 1, idx + 1)
                    self._crear_caja_texto(ax, texto, categoria, (0.5, 0.5), color='#F0F8E8')
                
                plt.tight_layout(rect=[0, 0, 1, 0.98])
                guardar_figura(fig, self.output_dir / f'resumen_estructurado_categorias_{i//3 + 1}.png')
    
    def _generar_insights_estrategicos(self, insights: Dict):
        """6.7 Genera visualización de insights estratégicos."""
        # Insights global
        if 'global' in insights:
            fig = plt.figure(figsize=(16, 10), facecolor='white')
            fig.suptitle('Insights Estratégicos - Global', fontsize=18, fontweight='bold', y=0.98)
            
            ax = fig.add_subplot(111)
            self._crear_caja_texto(ax, insights['global'], '', (0.5, 0.45), color='#FFF0F5')
            
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            guardar_figura(fig, self.output_dir / 'resumen_insights_global.png')
        
        # Insights por categoría
        if 'por_categoria' in insights:
            categorias = list(insights['por_categoria'].items())
            
            for i in range(0, len(categorias), 3):
                batch = categorias[i:i+3]
                num_cats = len(batch)
                
                fig = plt.figure(figsize=(16, 4 * num_cats), facecolor='white')
                fig.suptitle(f'Insights Estratégicos - Por Categoría (Parte {i//3 + 1})', 
                           fontsize=18, fontweight='bold', y=0.99)
                
                for idx, (categoria, texto) in enumerate(batch):
                    ax = fig.add_subplot(num_cats, 1, idx + 1)
                    self._crear_caja_texto(ax, texto, categoria, (0.5, 0.5), color='#FFF0F5')
                
                plt.tight_layout(rect=[0, 0, 1, 0.98])
                guardar_figura(fig, self.output_dir / f'resumen_insights_categorias_{i//3 + 1}.png')
