"""
Generador de Análisis de Categorías
====================================
Sección 3: Categorías (visualizaciones esenciales)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from pathlib import Path
from typing import List
from .utils import COLORES, COLORES_SENTIMIENTO, PALETA_CATEGORIAS, ESTILOS, guardar_figura


class GeneradorCategorias:
    """Genera visualizaciones de análisis de categorías."""
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '03_categorias'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_todas(self) -> List[str]:
        """Genera visualizaciones esenciales de categorías."""
        generadas = []
        
        if self.validador.puede_renderizar('top_categorias')[0]:
            self._generar_top_categorias()
            generadas.append('top_categorias')
        
        if self.validador.puede_renderizar('sentimientos_por_categoria')[0]:
            self._generar_sentimientos_por_categoria()
            generadas.append('sentimientos_por_categoria')
        
        if self.validador.puede_renderizar('fortalezas_vs_debilidades')[0]:
            self._generar_fortalezas_vs_debilidades()
            generadas.append('fortalezas_vs_debilidades')
        
        if self.validador.puede_renderizar('radar_chart_360')[0]:
            self._generar_radar_chart()
            generadas.append('radar_chart_360')
        
        return generadas
    
    def _extraer_categorias_sentimientos(self):
        """Extrae categorías con sus sentimientos asociados."""
        cat_sentimientos = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})
        
        for idx, row in self.df.iterrows():
            try:
                cats_str = str(row['Categorias']).strip("[]'\"").replace("'", "").replace('"', '')
                cats_list = [c.strip() for c in cats_str.split(',') if c.strip()]
                sentimiento = str(row['Sentimiento'])
                
                for cat in cats_list:
                    if sentimiento in cat_sentimientos[cat]:
                        cat_sentimientos[cat][sentimiento] += 1
            except:
                continue
        
        return cat_sentimientos
    
    def _generar_top_categorias(self):
        """3.1 Top Categorías Mencionadas."""
        cats_counter = {}
        for cats in self.df['Categorias'].dropna():
            try:
                cats_str = str(cats).strip("[]'\"").replace("'", "").replace('"', '')
                cats_list = [c.strip() for c in cats_str.split(',') if c.strip()]
                for cat in cats_list:
                    cats_counter[cat] = cats_counter.get(cat, 0) + 1
            except:
                continue
        
        if not cats_counter:
            return
        
        # Ordenar por frecuencia
        cats_ordenadas = sorted(cats_counter.items(), key=lambda x: x[1], reverse=True)
        categorias, valores = zip(*cats_ordenadas)
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')
        
        y_pos = range(len(categorias))
        bars = ax.barh(y_pos, valores, color=PALETA_CATEGORIAS[:len(categorias)])
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categorias, fontsize=10)
        ax.set_xlabel('Menciones', **ESTILOS['etiquetas'])
        ax.set_title('Categorías Más Mencionadas', **ESTILOS['titulo'])
        ax.invert_yaxis()
        ax.grid(True, axis='x', alpha=0.3)
        
        # Añadir valores
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(val + max(valores)*0.01, i, f'{val}', va='center', fontsize=9)
        
        guardar_figura(fig, self.output_dir / 'top_categorias.png')
    
    def _generar_sentimientos_por_categoria(self):
        """3.2 Sentimientos por Categoría (stacked bar 100%)."""
        cat_sent = self._extraer_categorias_sentimientos()
        
        # Filtrar categorías con pocas menciones
        cat_sent_filtrado = {k: v for k, v in cat_sent.items() if sum(v.values()) > 3}
        
        if not cat_sent_filtrado:
            return
        
        # Crear DataFrame
        df_cat = pd.DataFrame(cat_sent_filtrado).T
        df_cat_pct = df_cat.div(df_cat.sum(axis=1), axis=0) * 100
        df_cat_pct = df_cat_pct.sort_values('Positivo', ascending=True)
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(df_cat_pct) * 0.4)), facecolor='white')
        
        df_cat_pct.plot.barh(
            ax=ax,
            stacked=True,
            color=[COLORES_SENTIMIENTO[s] for s in df_cat_pct.columns],
            width=0.7
        )
        
        ax.set_xlabel('Porcentaje', **ESTILOS['etiquetas'])
        ax.set_ylabel('Categoría', **ESTILOS['etiquetas'])
        ax.set_title('Distribución de Sentimientos por Categoría', **ESTILOS['titulo'])
        ax.legend(title='Sentimiento', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, axis='x', alpha=0.3)
        
        guardar_figura(fig, self.output_dir / 'sentimientos_por_categoria.png')
    
    def _generar_fortalezas_vs_debilidades(self):
        """3.3 Fortalezas vs Debilidades (diverging bar chart)."""
        cat_sent = self._extraer_categorias_sentimientos()
        
        # Calcular porcentajes
        datos = []
        for cat, sents in cat_sent.items():
            total = sum(sents.values())
            if total < 5:
                continue
            
            pct_pos = (sents['Positivo'] / total) * 100
            pct_neg = (sents['Negativo'] / total) * 100
            datos.append({'categoria': cat, 'positivo': pct_pos, 'negativo': pct_neg})
        
        if not datos:
            return
        
        df_balance = pd.DataFrame(datos).sort_values('positivo', ascending=True)
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(df_balance) * 0.4)), facecolor='white')
        
        y_pos = range(len(df_balance))
        
        # Barras negativas (izquierda)
        ax.barh(y_pos, -df_balance['negativo'], color=COLORES['negativo'], alpha=0.7, label='Negativo')
        # Barras positivas (derecha)
        ax.barh(y_pos, df_balance['positivo'], color=COLORES['positivo'], alpha=0.7, label='Positivo')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df_balance['categoria'], fontsize=10)
        ax.set_xlabel('← Negativo % | Positivo % →', **ESTILOS['etiquetas'])
        ax.set_title('Fortalezas vs Debilidades por Categoría', **ESTILOS['titulo'])
        ax.axvline(x=0, color='black', linewidth=1)
        ax.legend(loc='lower right')
        ax.grid(True, axis='x', alpha=0.3)
        
        guardar_figura(fig, self.output_dir / 'fortalezas_vs_debilidades.png')
    
    def _generar_radar_chart(self):
        """3.4 Radar Chart 360° del Destino."""
        cat_sent = self._extraer_categorias_sentimientos()
        
        # Filtrar categorías válidas
        cat_sent_filtrado = {k: v for k, v in cat_sent.items() if sum(v.values()) > 5}
        
        if len(cat_sent_filtrado) < 4:
            return
        
        # Preparar datos
        categorias = list(cat_sent_filtrado.keys())
        pct_positivo = []
        pct_negativo = []
        
        for cat in categorias:
            sents = cat_sent_filtrado[cat]
            total = sum(sents.values())
            pct_positivo.append((sents['Positivo'] / total) * 100)
            pct_negativo.append((sents['Negativo'] / total) * 100)
        
        # Cerrar el polígono
        pct_positivo.append(pct_positivo[0])
        pct_negativo.append(pct_negativo[0])
        
        # Ángulos
        num_vars = len(categorias)
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'), facecolor='white')
        
        # Plot líneas
        ax.plot(angles, pct_positivo, 'o-', linewidth=2, label='Positivo', color=COLORES['positivo'])
        ax.fill(angles, pct_positivo, alpha=0.25, color=COLORES['positivo'])
        
        ax.plot(angles, pct_negativo, 'o-', linewidth=2, label='Negativo', color=COLORES['negativo'])
        ax.fill(angles, pct_negativo, alpha=0.25, color=COLORES['negativo'])
        
        # Etiquetas
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categorias, size=9)
        ax.set_ylim(0, 100)
        ax.set_title('Radar Chart 360° - Percepción por Categoría', **ESTILOS['titulo'], pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)
        
        guardar_figura(fig, self.output_dir / 'radar_chart_360.png')
