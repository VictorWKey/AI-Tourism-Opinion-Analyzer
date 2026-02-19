"""
Generador de Análisis de Subjetividad
=======================================
Sección dedicada a subjetividad (3 visualizaciones).

Nota metodológica: El modelo de clasificación (victorwkey/tourism-subjectivity-bert)
es un clasificador binario que produce dos categorías:
  - Subjetiva: contenido predominantemente opinativo
  - Mixta: combina elementos subjetivos y objetivos

No se contempla una categoría "Objetiva" independiente.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List
from .utils import COLORES, ESTILOS, FONT_SIZES, guardar_figura
from .i18n import get_translator, get_subjectivity_labels


# Colores dedicados para subjetividad
COLORES_SUBJETIVIDAD = {
    'Subjetiva': '#9C27B0',  # Púrpura
    'Mixta': '#FF9800',      # Ámbar
}


class GeneradorSubjetividad:
    """Genera visualizaciones exclusivas de análisis de subjetividad."""

    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '02_subjetividad'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generar_todas(self) -> List[str]:
        """Genera todas las visualizaciones de subjetividad."""
        generadas = []

        if 'Subjetividad' not in self.df.columns:
            return generadas

        # S.1 Distribución de subjetividad (donut)
        if self.validador.puede_renderizar('distribucion_subjetividad')[0]:
            self._generar_distribucion_subjetividad()
            generadas.append('distribucion_subjetividad')

        # S.2 Subjetividad por calificación
        if self.validador.puede_renderizar('subjetividad_por_calificacion')[0]:
            self._generar_subjetividad_por_calificacion()
            generadas.append('subjetividad_por_calificacion')

        # S.3 Evolución temporal de subjetividad
        if self.validador.puede_renderizar('evolucion_temporal_subjetividad')[0]:
            self._generar_evolucion_temporal_subjetividad()
            generadas.append('evolucion_temporal_subjetividad')

        return generadas

    # ──────────────────────────────────────────────────────────────
    # S.1 Distribución de Subjetividad (donut chart)
    # ──────────────────────────────────────────────────────────────
    def _generar_distribucion_subjetividad(self):
        """Donut chart con la proporción Subjetiva / Mixta."""
        t = get_translator()
        subj_labels = get_subjectivity_labels()
        
        fig, ax = plt.subplots(figsize=(10, 8), facecolor=COLORES['fondo'])

        conteo = self.df['Subjetividad'].value_counts()
        colores = [COLORES_SUBJETIVIDAD.get(s, '#666666') for s in conteo.index]

        wedges, texts, autotexts = ax.pie(
            conteo.values,
            labels=[f'{subj_labels.get(s, s)}\n({v})' for s, v in zip(conteo.index, conteo.values)],
            autopct='%1.1f%%',
            colors=colores,
            startangle=90,
            pctdistance=0.85,
            wedgeprops=dict(width=0.5, edgecolor=COLORES['borde_separador'], linewidth=2),
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        for text in texts:
            text.set_fontsize(FONT_SIZES['subtitulo_dashboard'])

        ax.set_title(t('distribucion_subjetividad'), **ESTILOS['titulo'], pad=20)

        # Methodology note
        fig.text(
            0.5, 0.02,
            t('subjetividad_nota'),
            ha='center', fontsize=FONT_SIZES['nota'], style='italic', color=COLORES['nota'],
        )

        guardar_figura(fig, self.output_dir / 'distribucion_subjetividad.png')

    # ──────────────────────────────────────────────────────────────
    # S.2 Subjetividad por Calificación (stacked bar 100 %)
    # ──────────────────────────────────────────────────────────────
    def _generar_subjetividad_por_calificacion(self):
        """Stacked bar: proporción Subjetiva/Mixta por cada estrella."""
        if 'Calificacion' not in self.df.columns:
            return

        t = get_translator()
        subj_labels = get_subjectivity_labels()

        fig, ax = plt.subplots(figsize=(12, 7), facecolor=COLORES['fondo'])

        ct = pd.crosstab(
            self.df['Calificacion'],
            self.df['Subjetividad'],
            normalize='index',
        ) * 100

        # Ensure consistent column order
        for col in ['Subjetiva', 'Mixta']:
            if col not in ct.columns:
                ct[col] = 0.0
        ct = ct[['Subjetiva', 'Mixta']]

        # Translate column names for legend
        ct = ct.rename(columns=subj_labels)

        ct.plot.bar(
            stacked=True,
            ax=ax,
            color=[COLORES_SUBJETIVIDAD.get(c, '#666') for c in ['Subjetiva', 'Mixta']],
            width=0.6,
        )

        ax.set_xlabel(t('calificacion_estrellas'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('porcentaje_pct'), **ESTILOS['etiquetas'])
        ax.set_title(t('subjetividad_por_calificacion'), **ESTILOS['titulo'])
        ax.legend(title=t('subjetividad'), bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.set_ylim(0, 100)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Methodology note
        fig.text(
            0.5, -0.02,
            t('subjetividad_nota_mixta'),
            ha='center', fontsize=FONT_SIZES['nota'], style='italic', color=COLORES['nota'],
        )

        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'subjetividad_por_calificacion.png')

    # ──────────────────────────────────────────────────────────────
    # S.3 Evolución Temporal de Subjetividad (stacked area)
    # ──────────────────────────────────────────────────────────────
    def _generar_evolucion_temporal_subjetividad(self):
        """Stacked area: evolución de proporción Subjetiva/Mixta en el tiempo."""
        if 'FechaEstadia' not in self.df.columns:
            return

        t = get_translator()
        subj_labels = get_subjectivity_labels()

        df_temp = self.df.copy()
        df_temp['FechaEstadia'] = pd.to_datetime(df_temp['FechaEstadia'], errors='coerce')
        df_temp = df_temp.dropna(subset=['FechaEstadia', 'Subjetividad'])

        if len(df_temp) < 30:
            return

        df_temp['Periodo'] = df_temp['FechaEstadia'].dt.to_period('M')

        ct = pd.crosstab(df_temp['Periodo'], df_temp['Subjetividad'])
        # Normalise to percentages
        ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

        for col in ['Subjetiva', 'Mixta']:
            if col not in ct_pct.columns:
                ct_pct[col] = 0.0
        ct_pct = ct_pct[['Subjetiva', 'Mixta']]

        fig, ax = plt.subplots(figsize=(14, 6), facecolor=COLORES['fondo'])

        x = range(len(ct_pct))
        labels = [str(p) for p in ct_pct.index]

        ax.stackplot(
            x,
            ct_pct['Subjetiva'].values,
            ct_pct['Mixta'].values,
            labels=[subj_labels.get('Subjetiva', 'Subjetiva'), subj_labels.get('Mixta', 'Mixta')],
            colors=[COLORES_SUBJETIVIDAD['Subjetiva'], COLORES_SUBJETIVIDAD['Mixta']],
            alpha=0.8,
        )

        # X-axis labels — show every Nth label to avoid clutter
        step = max(1, len(labels) // 12)
        ax.set_xticks(x[::step])
        ax.set_xticklabels(labels[::step], rotation=45, ha='right', fontsize=FONT_SIZES['texto'])

        ax.set_ylabel(t('porcentaje_pct'), **ESTILOS['etiquetas'])
        ax.set_title(t('evolucion_temporal_subjetividad'), **ESTILOS['titulo'])
        ax.legend(title=t('subjetividad'), loc='upper right')
        ax.set_ylim(0, 100)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'evolucion_temporal_subjetividad.png')
