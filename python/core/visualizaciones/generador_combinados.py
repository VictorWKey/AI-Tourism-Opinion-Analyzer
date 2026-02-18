"""
Generador de Análisis Combinados
==================================
Sección 7: Combinados (5 visualizaciones)
Visualizaciones que cruzan múltiples dimensiones de análisis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List
from .utils import COLORES, COLORES_SENTIMIENTO, PALETA_CATEGORIAS, ESTILOS, FONT_SIZES, guardar_figura
from .i18n import get_translator, get_sentiment_labels, get_category_labels, translate_categories


class GeneradorCombinados:
    """Genera visualizaciones que combinan múltiples dimensiones de análisis."""
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '07_combinados'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_todas(self) -> List[str]:
        """Genera todas las visualizaciones combinadas."""
        generadas = []
        
        # 7.1 Sentimiento vs Subjetividad vs Categoría
        if self.validador.puede_renderizar('sentimiento_subjetividad_categoria')[0]:
            self._generar_sentimiento_subjetividad_categoria()
            generadas.append('sentimiento_subjetividad_categoria')
        
        # 7.2 Calificación por Categoría y Sentimiento
        if self.validador.puede_renderizar('calificacion_categoria_sentimiento')[0]:
            self._generar_calificacion_categoria_sentimiento()
            generadas.append('calificacion_categoria_sentimiento')
        
        # 7.3 Volumen vs Sentimiento (scatter)
        if self.validador.puede_renderizar('volumen_vs_sentimiento_scatter')[0]:
            self._generar_volumen_vs_sentimiento()
            generadas.append('volumen_vs_sentimiento_scatter')
        
        # 7.4 Correlación Calificación-Sentimiento
        if self.validador.puede_renderizar('correlacion_calificacion_sentimiento')[0]:
            self._generar_correlacion_calificacion_sentimiento()
            generadas.append('correlacion_calificacion_sentimiento')
        
        # 7.5 Distribución de Categorías por Calificación
        if self.validador.puede_renderizar('distribucion_categorias_calificacion')[0]:
            self._generar_distribucion_categorias_calificacion()
            generadas.append('distribucion_categorias_calificacion')
        
        return generadas
    
    def _extraer_categorias(self, row) -> List[str]:
        """Extrae lista de categorías de una fila."""
        cats = row.get('Categorias', '')
        if pd.isna(cats) or str(cats).strip() in ['', '[]', 'nan']:
            return []
        try:
            cats_str = str(cats).strip("[]'\"").replace("'", "").replace('"', '')
            return [c.strip() for c in cats_str.split(',') if c.strip()]
        except:
            return []
    
    def _generar_sentimiento_subjetividad_categoria(self):
        """7.1 Matriz de Sentimiento vs Subjetividad coloreada por Categorías top."""
        if 'Subjetividad' not in self.df.columns or 'Sentimiento' not in self.df.columns:
            return
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORES['fondo'])
        
        # Crear tabla de contingencia
        contingencia = pd.crosstab(self.df['Sentimiento'], self.df['Subjetividad'])
        
        t = get_translator()
        sent_labels = get_sentiment_labels()
        from .i18n import get_subjectivity_labels
        subj_labels = get_subjectivity_labels()
        
        # Translate labels
        contingencia = contingencia.rename(index=sent_labels, columns=subj_labels)
        
        # Heatmap
        sns.heatmap(contingencia, annot=True, fmt='d', cmap='YlGnBu', 
                   ax=ax, cbar_kws={'label': t('cantidad')}, linewidths=0.5)
        
        ax.set_xlabel(t('subjetividad'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('sentimiento'), **ESTILOS['etiquetas'])
        ax.set_title(t('sentimiento_vs_subjetividad_relacion'), **ESTILOS['titulo'])
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'sentimiento_subjetividad_categoria.png')
    
    def _generar_calificacion_categoria_sentimiento(self):
        """7.2 Calificación promedio por Categoría coloreada por Sentimiento."""
        if 'Categorias' not in self.df.columns or 'Calificacion' not in self.df.columns:
            return
        
        # Expandir categorías
        datos = []
        for _, row in self.df.iterrows():
            cats = self._extraer_categorias(row)
            for cat in cats:
                datos.append({
                    'Categoria': cat,
                    'Calificacion': row.get('Calificacion', 0),
                    'Sentimiento': row.get('Sentimiento', 'Neutro')
                })
        
        if not datos:
            return
        
        df_exp = pd.DataFrame(datos)
        
        # Calcular estadísticas por categoría y sentimiento
        resumen = df_exp.groupby(['Categoria', 'Sentimiento'])['Calificacion'].agg(['mean', 'count']).reset_index()
        resumen.columns = ['Categoria', 'Sentimiento', 'CalifPromedio', 'Cantidad']
        
        # Ordenar por calificación promedio general
        orden = df_exp.groupby('Categoria')['Calificacion'].mean().sort_values(ascending=False).index[:10]
        resumen = resumen[resumen['Categoria'].isin(orden)]
        
        t = get_translator()
        sent_labels = get_sentiment_labels()
        
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=COLORES['fondo'])
        
        # Pivot para barras agrupadas
        pivot = resumen.pivot(index='Categoria', columns='Sentimiento', values='CalifPromedio')
        pivot = pivot.reindex(orden)
        
        x = np.arange(len(pivot))
        width = 0.25
        
        for i, sent in enumerate(pivot.columns):
            valores = pivot[sent].fillna(0)
            color = COLORES_SENTIMIENTO.get(sent, COLORES['primario'])
            ax.bar(x + i*width, valores, width, label=sent_labels.get(sent, sent), color=color, alpha=0.8)
        
        ax.set_xlabel(t('categoria'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('calificacion_promedio'), **ESTILOS['etiquetas'])
        ax.set_title(t('calificacion_categoria_sentimiento'), **ESTILOS['titulo'])
        ax.set_xticks(x + width)
        cat_labels = get_category_labels()
        ax.set_xticklabels(translate_categories(pivot.index, cat_labels), rotation=45, ha='right')
        ax.legend(title=t('sentimiento'))
        ax.set_ylim(0, 5.5)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'calificacion_categoria_sentimiento.png')
    
    def _generar_volumen_vs_sentimiento(self):
        """7.3 Scatter: Volumen de menciones vs Porcentaje de sentimiento positivo."""
        if 'Categorias' not in self.df.columns:
            return
        
        # Calcular estadísticas por categoría
        stats = {}
        for _, row in self.df.iterrows():
            cats = self._extraer_categorias(row)
            sent = row.get('Sentimiento', 'Neutro')
            for cat in cats:
                if cat not in stats:
                    stats[cat] = {'total': 0, 'positivo': 0, 'negativo': 0}
                stats[cat]['total'] += 1
                if sent == 'Positivo':
                    stats[cat]['positivo'] += 1
                elif sent == 'Negativo':
                    stats[cat]['negativo'] += 1
        
        if not stats:
            return
        
        # Preparar datos
        categorias = list(stats.keys())
        volumenes = [stats[c]['total'] for c in categorias]
        pct_positivo = [stats[c]['positivo'] / stats[c]['total'] * 100 if stats[c]['total'] > 0 else 0 for c in categorias]
        pct_negativo = [stats[c]['negativo'] / stats[c]['total'] * 100 if stats[c]['total'] > 0 else 0 for c in categorias]
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORES['fondo'])
        
        # Colores basados en el balance positivo/negativo
        colores = []
        for pp, pn in zip(pct_positivo, pct_negativo):
            if pp > pn + 10:
                colores.append(COLORES['positivo'])
            elif pn > pp + 10:
                colores.append(COLORES['negativo'])
            else:
                colores.append(COLORES['neutro'])
        
        # Scatter plot
        scatter = ax.scatter(volumenes, pct_positivo, s=[v*3 for v in volumenes], 
                            c=colores, alpha=0.7, edgecolors=COLORES['borde_separador'], linewidth=1)
        
        # Etiquetas para cada punto
        cat_labels = get_category_labels()
        for i, cat in enumerate(categorias):
            cat_display = cat_labels.get(cat, cat)[:15]
            ax.annotate(cat_display, (volumenes[i], pct_positivo[i]), 
                       textcoords="offset points", xytext=(5, 5), fontsize=FONT_SIZES['texto_pequeno'])
        
        t = get_translator()
        
        ax.set_xlabel(t('volumen_menciones'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('pct_opiniones_positivas'), **ESTILOS['etiquetas'])
        ax.set_title(t('volumen_vs_satisfaccion'), **ESTILOS['titulo'])
        ax.grid(True, alpha=0.3)
        ax.axhline(y=50, color=COLORES['neutro'], linestyle='--', alpha=0.5, label=t('50_pct_positivas'))
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'volumen_vs_sentimiento_scatter.png')
    
    def _generar_correlacion_calificacion_sentimiento(self):
        """7.4 Matriz de correlación entre Calificación y Sentimiento."""
        if 'Sentimiento' not in self.df.columns or 'Calificacion' not in self.df.columns:
            return
        
        t = get_translator()
        sent_labels = get_sentiment_labels()
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=COLORES['fondo'])
        
        # Panel 1: Distribución de calificaciones por sentimiento (violin plot)
        ax1 = axes[0]
        df_valid = self.df.dropna(subset=['Calificacion', 'Sentimiento'])
        
        orden_sent = ['Positivo', 'Neutro', 'Negativo']
        orden_sent_display = [sent_labels.get(s, s) for s in orden_sent]
        colores_sent = [COLORES_SENTIMIENTO.get(s, COLORES['neutro']) for s in orden_sent]
        
        parts = ax1.violinplot([df_valid[df_valid['Sentimiento'] == s]['Calificacion'].values 
                                for s in orden_sent if s in df_valid['Sentimiento'].values],
                               positions=range(len(orden_sent)), showmeans=True, showmedians=True)
        
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colores_sent[i])
            pc.set_alpha(0.7)
        
        ax1.set_xticks(range(len(orden_sent)))
        ax1.set_xticklabels(orden_sent_display)
        ax1.set_xlabel(t('sentimiento'), **ESTILOS['etiquetas'])
        ax1.set_ylabel(t('calificacion'), **ESTILOS['etiquetas'])
        ax1.set_title(t('distribucion_calificacion_sentimiento'), **ESTILOS['titulo'])
        ax1.set_ylim(0, 5.5)
        ax1.grid(True, axis='y', alpha=0.3)
        
        # Panel 2: Heatmap de contingencia
        ax2 = axes[1]
        contingencia = pd.crosstab(df_valid['Calificacion'], df_valid['Sentimiento'])
        contingencia = contingencia.reindex(columns=orden_sent, fill_value=0)
        contingencia = contingencia.rename(columns=sent_labels)
        
        sns.heatmap(contingencia, annot=True, fmt='d', cmap='Blues', ax=ax2, 
                   cbar_kws={'label': t('cantidad')}, linewidths=0.5)
        ax2.set_xlabel(t('sentimiento'), **ESTILOS['etiquetas'])
        ax2.set_ylabel(t('calificacion'), **ESTILOS['etiquetas'])
        ax2.set_title(t('tabla_contingencia'), **ESTILOS['titulo'])
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'correlacion_calificacion_sentimiento.png')
    
    def _generar_distribucion_categorias_calificacion(self):
        """7.5 Distribución de menciones de categorías por nivel de calificación."""
        if 'Categorias' not in self.df.columns or 'Calificacion' not in self.df.columns:
            return
        
        # Expandir categorías
        datos = []
        for _, row in self.df.iterrows():
            cats = self._extraer_categorias(row)
            calif = row.get('Calificacion', 0)
            for cat in cats:
                datos.append({'Categoria': cat, 'Calificacion': calif})
        
        if not datos:
            return
        
        df_exp = pd.DataFrame(datos)
        
        # Top 10 categorías
        top_cats = df_exp['Categoria'].value_counts().head(10).index
        df_top = df_exp[df_exp['Categoria'].isin(top_cats)]
        
        # Crear pivot
        pivot = df_top.groupby(['Categoria', 'Calificacion']).size().unstack(fill_value=0)
        pivot = pivot.div(pivot.sum(axis=1), axis=0) * 100  # Porcentajes
        # Translate category index
        cat_labels = get_category_labels()
        pivot.index = translate_categories(pivot.index, cat_labels)
        
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=COLORES['fondo'])
        
        # Stacked bar horizontal
        pivot.plot(kind='barh', stacked=True, ax=ax, 
                  colormap='RdYlGn', alpha=0.8, edgecolor=COLORES['borde_separador'], linewidth=0.5)
        
        t = get_translator()
        
        ax.set_xlabel(t('porcentaje'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('categoria'), **ESTILOS['etiquetas'])
        ax.set_title(t('distribucion_categorias_calificacion'), **ESTILOS['titulo'])
        ax.legend(title=t('calificacion'), bbox_to_anchor=(1.02, 1), loc='upper left')
        ax.grid(True, axis='x', alpha=0.3)
        ax.set_xlim(0, 100)
        
        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'distribucion_categorias_calificacion.png')
