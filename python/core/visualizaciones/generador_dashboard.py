"""
Generador de Dashboard y Resumen Ejecutivo
===========================================
Sección 1: Dashboard (visualizaciones gráficas puras)

Genera un dashboard ejecutivo con 4 cuadrantes gráficos:
1. Distribución de sentimientos (donut chart)
2. Top categorías mencionadas (horizontal bar)
3. Top fortalezas del destino (horizontal bar - % positivo)
4. Top debilidades del destino (horizontal bar - % negativo)
"""

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .utils import COLORES, COLORES_SENTIMIENTO, ESTILOS, FONT_SIZES, PALETA_CATEGORIAS, guardar_figura


class GeneradorDashboard:
    """Genera visualizaciones gráficas de dashboard ejecutivo."""

    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '01_dashboard'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generar_todas(self) -> list[str]:
        """Genera todas las visualizaciones de dashboard."""
        generadas = []

        # Dashboard ejecutivo is deprecated - no longer generated
        # The folder exists for backward compatibility but remains empty

        return generadas

    def _generar_dashboard_ejecutivo(self):
        """Dashboard Ejecutivo con 4 cuadrantes gráficos puros."""
        fig = plt.figure(figsize=(18, 11), facecolor=COLORES['fondo'])
        gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.35)

        # Título principal
        fig.suptitle(
            'DASHBOARD EJECUTIVO - ANÁLISIS DE OPINIONES TURÍSTICAS',
            fontsize=FONT_SIZES['titulo_dashboard'],
            fontweight='bold',
            color=COLORES['texto'],
            y=0.97,
        )

        # Cuadrante 1: Distribución de sentimientos (donut)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_sentimientos_donut(ax1)

        # Cuadrante 2: Top categorías (horizontal bar)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_top_categorias(ax2)

        # Cuadrante 3: Top fortalezas (horizontal bar chart)
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_fortalezas_bar(ax3)

        # Cuadrante 4: Top debilidades (horizontal bar chart)
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_debilidades_bar(ax4)

        guardar_figura(fig, self.output_dir / 'dashboard_ejecutivo.png')

    def _plot_sentimientos_donut(self, ax):
        """Donut chart de distribución de sentimientos."""
        sentimientos = self.df['Sentimiento'].value_counts()
        colores = [COLORES_SENTIMIENTO.get(s, '#666666') for s in sentimientos.index]

        _wedges, texts, autotexts = ax.pie(
            sentimientos.values,
            labels=sentimientos.index,
            autopct='%1.1f%%',
            colors=colores,
            startangle=90,
            pctdistance=0.82,
            wedgeprops=dict(width=0.45, edgecolor=COLORES['borde_separador'], linewidth=2),
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(FONT_SIZES['subtitulo_dashboard'])

        for text in texts:
            text.set_fontsize(FONT_SIZES['etiquetas'])
            text.set_fontweight('bold')

        # Centro con total
        total = sentimientos.sum()
        ax.text(
            0,
            0,
            f'{total}',
            ha='center',
            va='center',
            fontsize=FONT_SIZES['titulo_dashboard'],
            fontweight='bold',
            color=COLORES['texto'],
        )
        ax.text(0, -0.12, 'opiniones', ha='center', va='center', fontsize=FONT_SIZES['texto'], color=COLORES['texto'])

        ax.set_title('Distribución de Sentimientos', **ESTILOS['subtitulo'], pad=15)

    def _plot_top_categorias(self, ax):
        """Top categorías más mencionadas (horizontal bar)."""
        cats_counter = {}
        for cats in self.df['Categorias'].dropna():
            try:
                cats_str = str(cats).strip()
                # Excluir listas vacías explícitamente
                if cats_str in ['[]', '{}', '']:
                    continue

                cats_str = cats_str.strip('[]\'"')
                cats_list = [c.strip() for c in cats_str.split(',') if c.strip()]
                for cat in cats_list:
                    cats_counter[cat] = cats_counter.get(cat, 0) + 1
            except Exception:
                continue

        if not cats_counter:
            ax.text(
                0.5,
                0.5,
                'Sin datos de categorías',
                ha='center',
                va='center',
                fontsize=FONT_SIZES['subtitulo_dashboard'],
                color=COLORES['texto'],
            )
            ax.axis('off')
            return

        top_cats = sorted(cats_counter.items(), key=lambda x: x[1], reverse=True)[:7]
        categorias, valores = zip(*top_cats)

        y_pos = np.arange(len(categorias))
        bars = ax.barh(
            y_pos,
            valores,
            color=PALETA_CATEGORIAS[: len(categorias)],
            edgecolor=COLORES['borde_separador'],
            linewidth=0.5,
            height=0.65,
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(categorias, fontsize=FONT_SIZES['texto'])
        ax.set_xlabel('Menciones', fontsize=FONT_SIZES['etiquetas'], color=COLORES['texto'])
        ax.set_title('Top Categorías Mencionadas', **ESTILOS['subtitulo'], pad=15)
        ax.invert_yaxis()
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for i, (_, val) in enumerate(zip(bars, valores)):
            ax.text(
                val + max(valores) * 0.02, i, f'{val}', va='center', fontsize=FONT_SIZES['texto'], fontweight='bold'
            )

    def _plot_fortalezas_bar(self, ax):
        """Top fortalezas del destino (horizontal bar chart - % positivo)."""
        fortalezas_debilidades = self._calcular_fortalezas_debilidades()
        fortalezas = fortalezas_debilidades['fortalezas'][:7]

        if not fortalezas:
            ax.text(
                0.5,
                0.5,
                'Sin datos suficientes',
                ha='center',
                va='center',
                fontsize=FONT_SIZES['subtitulo_dashboard'],
                color=COLORES['texto'],
            )
            ax.axis('off')
            return

        categorias = [f[0] for f in fortalezas]
        valores = [f[1] for f in fortalezas]

        y_pos = np.arange(len(categorias))

        ax.barh(
            y_pos,
            valores,
            color=COLORES['positivo'],
            alpha=0.75,
            edgecolor=COLORES['borde_separador'],
            linewidth=0.5,
            height=0.65,
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(categorias, fontsize=FONT_SIZES['texto'])
        ax.set_xlabel('% Opiniones Positivas', fontsize=FONT_SIZES['etiquetas'], color=COLORES['texto'])
        ax.set_title('Top Fortalezas del Destino', **ESTILOS['subtitulo'], pad=15, color=COLORES['positivo'])
        ax.invert_yaxis()
        ax.set_xlim(0, 105)
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for i, val in enumerate(valores):
            ax.text(
                val + 1.5,
                i,
                f'{val:.1f}%',
                va='center',
                fontsize=FONT_SIZES['texto'],
                fontweight='bold',
                color=COLORES['positivo'],
            )

    def _plot_debilidades_bar(self, ax):
        """Top debilidades del destino (horizontal bar chart - % negativo)."""
        fortalezas_debilidades = self._calcular_fortalezas_debilidades()
        debilidades = fortalezas_debilidades['debilidades'][:7]

        if not debilidades:
            ax.text(
                0.5,
                0.5,
                'Sin datos suficientes',
                ha='center',
                va='center',
                fontsize=FONT_SIZES['subtitulo_dashboard'],
                color=COLORES['texto'],
            )
            ax.axis('off')
            return

        categorias = [d[0] for d in debilidades]
        valores = [d[1] for d in debilidades]

        y_pos = np.arange(len(categorias))

        ax.barh(
            y_pos,
            valores,
            color=COLORES['negativo'],
            alpha=0.75,
            edgecolor=COLORES['borde_separador'],
            linewidth=0.5,
            height=0.65,
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(categorias, fontsize=FONT_SIZES['texto'])
        ax.set_xlabel('% Opiniones Negativas', fontsize=FONT_SIZES['etiquetas'], color=COLORES['texto'])
        ax.set_title('Top Debilidades del Destino', **ESTILOS['subtitulo'], pad=15, color=COLORES['negativo'])
        ax.invert_yaxis()
        ax.set_xlim(0, max(valores) * 1.25 if valores else 100)
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for i, val in enumerate(valores):
            ax.text(
                val + max(valores) * 0.03,
                i,
                f'{val:.1f}%',
                va='center',
                fontsize=FONT_SIZES['texto'],
                fontweight='bold',
                color=COLORES['negativo'],
            )

    def _calcular_fortalezas_debilidades(self) -> dict:
        """Calcula fortalezas y debilidades por categoría."""
        cat_sentimientos = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})

        for _, row in self.df.iterrows():
            try:
                cats_str = str(row['Categorias']).strip()
                # Excluir listas vacías explícitamente
                if cats_str in ['[]', '{}', '', 'nan', 'None']:
                    continue

                cats_str = cats_str.strip('[]\'"')
                cats_list = [c.strip() for c in cats_str.split(',') if c.strip()]
                sentimiento = row['Sentimiento']

                for cat in cats_list:
                    cat_sentimientos[cat][sentimiento] += 1
            except Exception:
                continue

        fortalezas = []
        debilidades = []

        for cat, sents in cat_sentimientos.items():
            total = sum(sents.values())
            if total < 5:
                continue

            pct_pos = (sents['Positivo'] / total) * 100
            pct_neg = (sents['Negativo'] / total) * 100

            fortalezas.append((cat, pct_pos))
            debilidades.append((cat, pct_neg))

        fortalezas.sort(key=lambda x: x[1], reverse=True)
        debilidades.sort(key=lambda x: x[1], reverse=True)

        return {'fortalezas': fortalezas, 'debilidades': debilidades}
