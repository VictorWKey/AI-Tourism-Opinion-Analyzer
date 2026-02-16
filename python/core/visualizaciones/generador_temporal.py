"""
Generador de Análisis Temporal
================================
Sección 5: Temporal (visualizaciones esenciales)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
from pathlib import Path
from typing import List
from .utils import COLORES, COLORES_SENTIMIENTO, PALETA_CATEGORIAS, ESTILOS, guardar_figura


class GeneradorTemporal:
    """Genera visualizaciones de análisis temporal."""
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '05_temporal'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_todas(self) -> List[str]:
        """Genera visualizaciones esenciales temporales."""
        generadas = []
        
        if self.validador.puede_renderizar('volumen_opiniones_tiempo')[0]:
            self._generar_volumen_temporal()
            generadas.append('volumen_opiniones_tiempo')
        
        if self.validador.puede_renderizar('evolucion_sentimientos')[0]:
            self._generar_evolucion_sentimientos()
            generadas.append('evolucion_sentimientos')
        
        if self.validador.puede_renderizar('tendencia_calificacion')[0]:
            self._generar_tendencia_calificacion()
            generadas.append('tendencia_calificacion')
        
        if self.validador.puede_renderizar('estacionalidad_categorias')[0]:
            self._generar_estacionalidad_categorias()
            generadas.append('estacionalidad_categorias')
        
        return generadas
    
    def _generar_volumen_temporal(self):
        """5.1 Volumen de Opiniones en el Tiempo."""
        df_fechas = self.df[self.df['FechaEstadia'].notna()].copy()
        
        if len(df_fechas) == 0:
            return
        
        df_fechas['FechaEstadia'] = pd.to_datetime(df_fechas['FechaEstadia'])
        df_fechas['Mes'] = df_fechas['FechaEstadia'].dt.to_period('M')
        
        volumen = df_fechas.groupby('Mes').size()
        
        fig, ax = plt.subplots(figsize=(14, 6), facecolor=COLORES['fondo'])
        
        volumen.plot(kind='bar', ax=ax, color=COLORES['primario'], alpha=0.7)
        
        ax.set_xlabel('Período', **ESTILOS['etiquetas'])
        ax.set_ylabel('Cantidad de opiniones', **ESTILOS['etiquetas'])
        ax.set_title('Volumen de Opiniones en el Tiempo', **ESTILOS['titulo'])
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        
        guardar_figura(fig, self.output_dir / 'volumen_opiniones_tiempo.png')
    
    def _generar_evolucion_sentimientos(self):
        """5.2 Evolución Temporal de Sentimientos."""
        df_fechas = self.df[self.df['FechaEstadia'].notna()].copy()
        
        if len(df_fechas) == 0:
            return
        
        df_fechas['FechaEstadia'] = pd.to_datetime(df_fechas['FechaEstadia'])
        df_fechas['Mes'] = df_fechas['FechaEstadia'].dt.to_period('M')
        
        evol = df_fechas.groupby(['Mes', 'Sentimiento']).size().unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(14, 6), facecolor=COLORES['fondo'])
        
        for sentimiento in evol.columns:
            ax.plot(range(len(evol)), evol[sentimiento], 
                   label=sentimiento, color=COLORES_SENTIMIENTO.get(sentimiento, '#666'),
                   marker='o', linewidth=2)
        
        ax.set_xticks(range(len(evol)))
        ax.set_xticklabels([str(m) for m in evol.index], rotation=45, ha='right')
        ax.set_xlabel('Período', **ESTILOS['etiquetas'])
        ax.set_ylabel('Cantidad de opiniones', **ESTILOS['etiquetas'])
        ax.set_title('Evolución de Sentimientos en el Tiempo', **ESTILOS['titulo'])
        ax.legend(title='Sentimiento', loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        guardar_figura(fig, self.output_dir / 'evolucion_sentimientos.png')

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

    def _generar_tendencia_calificacion(self):
        """5.3 Tendencia de Calificación en el Tiempo.
        
        Línea de tendencia con media móvil que muestra si la calificación
        promedio del destino está mejorando, estable o empeorando.
        """
        if 'Calificacion' not in self.df.columns:
            return

        df_fechas = self.df[self.df['FechaEstadia'].notna()].copy()
        df_fechas['FechaEstadia'] = pd.to_datetime(df_fechas['FechaEstadia'], errors='coerce')
        df_fechas = df_fechas.dropna(subset=['FechaEstadia', 'Calificacion'])
        df_fechas['Mes'] = df_fechas['FechaEstadia'].dt.to_period('M')

        if len(df_fechas) < 20:
            return

        # Calcular promedio mensual
        mensual = df_fechas.groupby('Mes').agg(
            promedio=('Calificacion', 'mean'),
            conteo=('Calificacion', 'count')
        ).reset_index()
        mensual['Mes_str'] = mensual['Mes'].astype(str)

        fig, ax = plt.subplots(figsize=(14, 6), facecolor=COLORES['fondo'])

        x = range(len(mensual))

        # Barras para volumen (eje secundario)
        ax2 = ax.twinx()
        ax2.bar(x, mensual['conteo'], color=COLORES['primario'], alpha=0.15, width=0.8, label='Volumen')
        ax2.set_ylabel('Opiniones por mes', fontsize=10, color=COLORES['neutro'])
        ax2.tick_params(axis='y', labelcolor=COLORES['neutro'])
        ax2.spines['top'].set_visible(False)

        # Línea de calificación promedio
        ax.plot(x, mensual['promedio'], 'o-', color=COLORES['primario'],
                linewidth=2, markersize=5, label='Promedio mensual', zorder=3)

        # Media móvil (ventana de 3 meses)
        if len(mensual) >= 3:
            rolling = mensual['promedio'].rolling(window=3, center=True).mean()
            ax.plot(x, rolling, '-', color=COLORES['negativo'], linewidth=2.5,
                    alpha=0.8, label='Tendencia (media móvil 3m)', zorder=4)

        # Línea de promedio general
        promedio_global = df_fechas['Calificacion'].mean()
        ax.axhline(y=promedio_global, color=COLORES['neutro'], linestyle='--',
                   alpha=0.5, linewidth=1.5, label=f'Promedio general: {promedio_global:.2f}')

        ax.set_xticks(x)
        ax.set_xticklabels(mensual['Mes_str'], rotation=45, ha='right', fontsize=9)
        ax.set_xlabel('Período', **ESTILOS['etiquetas'])
        ax.set_ylabel('Calificación Promedio', **ESTILOS['etiquetas'])
        ax.set_title('Tendencia de Calificación en el Tiempo', **ESTILOS['titulo'])
        ax.set_ylim(0, 5.5)
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'tendencia_calificacion.png')

    def _generar_estacionalidad_categorias(self):
        """5.4 Heatmap de Estacionalidad por Categoría.
        
        Mapa de calor mostrando la intensidad de menciones de cada categoría
        por mes del año. Revela patrones estacionales: qué aspectos turísticos
        son más relevantes en cada época.
        """
        if 'FechaEstadia' not in self.df.columns or 'Categorias' not in self.df.columns:
            return

        df_fechas = self.df[self.df['FechaEstadia'].notna()].copy()
        df_fechas['FechaEstadia'] = pd.to_datetime(df_fechas['FechaEstadia'], errors='coerce')
        df_fechas = df_fechas.dropna(subset=['FechaEstadia'])
        df_fechas['MesNum'] = df_fechas['FechaEstadia'].dt.month

        if len(df_fechas) < 50:
            return

        # Expandir categorías
        datos = []
        for _, row in df_fechas.iterrows():
            cats = self._extraer_categorias(row)
            for cat in cats:
                datos.append({'MesNum': row['MesNum'], 'Categoria': cat})

        if not datos:
            return

        df_exp = pd.DataFrame(datos)

        # Top 8 categorías
        top_cats = df_exp['Categoria'].value_counts().head(8).index.tolist()
        df_top = df_exp[df_exp['Categoria'].isin(top_cats)]

        # Pivot: meses × categorías
        pivot = df_top.groupby(['MesNum', 'Categoria']).size().unstack(fill_value=0)
        pivot = pivot.reindex(columns=top_cats, fill_value=0)

        meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                         'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        # Only keep months that exist in data
        pivot.index = [meses_nombres[m - 1] for m in pivot.index]

        fig, ax = plt.subplots(figsize=(max(10, len(top_cats) * 1.2), 7), facecolor=COLORES['fondo'])

        sns.heatmap(
            pivot, annot=True, fmt='d', cmap='YlGnBu',
            ax=ax, linewidths=0.5, cbar_kws={'label': 'Menciones'},
            square=False
        )

        ax.set_xlabel('Categoría', **ESTILOS['etiquetas'])
        ax.set_ylabel('Mes', **ESTILOS['etiquetas'])
        ax.set_title('Estacionalidad: Menciones por Categoría y Mes', **ESTILOS['titulo'], pad=15)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha='right', fontsize=9)

        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'estacionalidad_categorias.png')
