"""
Generador de Análisis de Sentimientos
======================================
Sección 2: Sentimientos (8 visualizaciones)
"""

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import nltk
import pandas as pd
from nltk.corpus import stopwords
from wordcloud import WordCloud

from .i18n import get_sentiment_labels, get_translator
from .utils import COLORES, COLORES_SENTIMIENTO, ESTILOS, FONT_SIZES, guardar_figura


class GeneradorSentimientos:
    """Genera visualizaciones de análisis de sentimientos."""

    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '01_sentimientos'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Descargar stopwords si no están
        try:
            stopwords.words('spanish')
        except Exception:
            nltk.download('stopwords', quiet=True)

        # Stopwords multilingües
        idiomas = ['spanish', 'english', 'portuguese', 'french', 'italian']
        self.stopwords = set()
        for idioma in idiomas:
            try:
                self.stopwords.update(stopwords.words(idioma))
            except Exception:
                pass

    def generar_todas(self) -> list[str]:
        """Genera todas las visualizaciones de sentimientos."""
        generadas = []

        # 2.1 Distribución de sentimientos
        if self.validador.puede_renderizar('distribucion_sentimientos')[0]:
            self._generar_distribucion_sentimientos()
            generadas.append('distribucion_sentimientos')

        # 2.2 Evolución temporal
        if self.validador.puede_renderizar('evolucion_temporal_sentimientos')[0]:
            self._generar_evolucion_temporal()
            generadas.append('evolucion_temporal_sentimientos')

        # 2.3 Sentimientos por calificación
        if self.validador.puede_renderizar('sentimientos_por_calificacion')[0]:
            self._generar_sentimientos_por_calificacion()
            generadas.append('sentimientos_por_calificacion')

        # 2.4-2.6 Word clouds por sentimiento
        for sentimiento in ['positivo', 'neutro', 'negativo']:
            viz_name = f'wordcloud_{sentimiento}'
            if self.validador.puede_renderizar(viz_name)[0]:
                self._generar_wordcloud(sentimiento.capitalize())
                generadas.append(viz_name)

        # 2.7 Top palabras comparación
        if self.validador.puede_renderizar('top_palabras_comparacion')[0]:
            self._generar_top_palabras_comparacion()
            generadas.append('top_palabras_comparacion')

        # 2.8 Sentimiento vs subjetividad
        if self.validador.puede_renderizar('sentimiento_vs_subjetividad')[0]:
            self._generar_sentimiento_vs_subjetividad()
            generadas.append('sentimiento_vs_subjetividad')

        return generadas

    def _generar_distribucion_sentimientos(self):
        """2.1 Distribución General de Sentimientos (donut chart)."""
        fig, ax = plt.subplots(figsize=(10, 8), facecolor=COLORES['fondo'])

        t = get_translator()
        sent_labels = get_sentiment_labels()

        sentimientos = self.df['Sentimiento'].value_counts()
        colores = [COLORES_SENTIMIENTO.get(s, '#666666') for s in sentimientos.index]

        _wedges, texts, autotexts = ax.pie(
            sentimientos.values,
            labels=[f'{sent_labels.get(s, s)}\n({v})' for s, v in zip(sentimientos.index, sentimientos.values)],
            autopct='%1.1f%%',
            colors=colores,
            startangle=90,
            pctdistance=0.85,
            wedgeprops=dict(width=0.5, edgecolor=COLORES['borde_separador'], linewidth=2),
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(FONT_SIZES['subtitulo'])

        for text in texts:
            text.set_fontsize(FONT_SIZES['subtitulo_dashboard'])
            text.set_fontweight('bold')

        ax.set_title(t('distribucion_sentimientos'), **ESTILOS['titulo'], pad=20)

        guardar_figura(fig, self.output_dir / 'distribucion_sentimientos.png')

    def _generar_evolucion_temporal(self):
        """2.2 Evolución Temporal de Sentimientos."""
        df_fechas = self.df[self.df['FechaEstadia'].notna()].copy()
        df_fechas['FechaEstadia'] = pd.to_datetime(df_fechas['FechaEstadia'])
        df_fechas['Mes'] = df_fechas['FechaEstadia'].dt.to_period('M')

        # Agrupar por mes y sentimiento
        evol = df_fechas.groupby(['Mes', 'Sentimiento']).size().unstack(fill_value=0)

        t = get_translator()
        sent_labels = get_sentiment_labels()

        # Translate column names for legend
        evol = evol.rename(columns=sent_labels)

        fig, ax = plt.subplots(figsize=(14, 6), facecolor=COLORES['fondo'])

        # Gráfico de área apilada
        evol.plot.area(
            ax=ax,
            color=[COLORES_SENTIMIENTO.get(s, '#666') for s in self.df['Sentimiento'].value_counts().index],
            alpha=0.7,
            stacked=True,
        )

        ax.set_xlabel(t('periodo'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('cantidad_opiniones'), **ESTILOS['etiquetas'])
        ax.set_title(t('evolucion_temporal_sentimientos'), **ESTILOS['titulo'])
        ax.legend(title=t('sentimiento'), loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        guardar_figura(fig, self.output_dir / 'evolucion_temporal_sentimientos.png')

    def _generar_sentimientos_por_calificacion(self):
        """2.3 Sentimientos por Calificación."""
        if 'Calificacion' not in self.df.columns:
            return

        # Crear tabla de contingencia
        tabla = pd.crosstab(self.df['Calificacion'], self.df['Sentimiento'], normalize='index') * 100

        t = get_translator()
        sent_labels = get_sentiment_labels()

        # Translate column names for legend
        tabla = tabla.rename(columns=sent_labels)

        fig, ax = plt.subplots(figsize=(12, 6), facecolor=COLORES['fondo'])

        # Stacked bar chart
        tabla.plot.bar(
            ax=ax,
            stacked=True,
            color=[COLORES_SENTIMIENTO.get(s, '#666') for s in self.df['Sentimiento'].value_counts().index],
            width=0.7,
        )

        ax.set_xlabel(t('calificacion_estrellas'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('porcentaje'), **ESTILOS['etiquetas'])
        ax.set_title(t('sentimientos_por_calificacion'), **ESTILOS['titulo'])
        ax.legend(title=t('sentimiento'), bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        guardar_figura(fig, self.output_dir / 'sentimientos_por_calificacion.png')

    def _generar_wordcloud(self, sentimiento: str):
        """2.4-2.6 Nubes de Palabras por Sentimiento."""
        df_sent = self.df[self.df['Sentimiento'] == sentimiento]

        if len(df_sent) == 0:
            return

        # Concatenar todos los textos
        texto = ' '.join(df_sent['TituloReview'].dropna().astype(str))

        # Colormap según sentimiento
        colormap = {'Positivo': 'Greens', 'Neutro': 'Greys', 'Negativo': 'Reds'}

        # Generar wordcloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color=COLORES['fondo'],
            stopwords=self.stopwords,
            max_words=150,
            colormap=colormap.get(sentimiento, 'viridis'),
            relative_scaling=0.5,
            min_font_size=10,
        ).generate(texto)

        t = get_translator()
        sent_labels = get_sentiment_labels()
        sent_display = sent_labels.get(sentimiento, sentimiento)

        fig, ax = plt.subplots(figsize=(15, 8), facecolor=COLORES['fondo'])
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(t('wordcloud_sentimiento', sentimiento=sent_display), **ESTILOS['titulo'], pad=20)

        nombre_archivo = f'wordcloud_{sentimiento.lower()}.png'
        guardar_figura(fig, self.output_dir / nombre_archivo)

    def _generar_top_palabras_comparacion(self):
        """2.7 Top Palabras: Positivas vs Negativas."""
        # Extraer palabras por sentimiento
        palabras_pos = self._extraer_palabras('Positivo')
        palabras_neg = self._extraer_palabras('Negativo')

        # Top 15 de cada uno
        top_pos = Counter(palabras_pos).most_common(15)
        top_neg = Counter(palabras_neg).most_common(15)

        fig, ax = plt.subplots(figsize=(14, 8), facecolor=COLORES['fondo'])

        # Diverging bar chart
        y_pos = range(max(len(top_pos), len(top_neg)))

        t = get_translator()
        sent_labels = get_sentiment_labels()

        # Barras negativas (izquierda)
        if top_neg:
            _palabras_neg_list, valores_neg = zip(*top_neg)
            ax.barh(
                y_pos[: len(top_neg)],
                [-v for v in valores_neg],
                color=COLORES['negativo'],
                alpha=0.7,
                label=sent_labels.get('Negativo', 'Negativo'),
            )

            # Etiquetas negativas
            for i, (palabra, valor) in enumerate(top_neg):
                ax.text(-valor - 5, i, palabra, ha='right', va='center', fontsize=FONT_SIZES['texto'])

        # Barras positivas (derecha)
        if top_pos:
            _palabras_pos_list, valores_pos = zip(*top_pos)
            ax.barh(
                y_pos[: len(top_pos)],
                valores_pos,
                color=COLORES['positivo'],
                alpha=0.7,
                label=sent_labels.get('Positivo', 'Positivo'),
            )

            # Etiquetas positivas
            for i, (palabra, valor) in enumerate(top_pos):
                ax.text(valor + 5, i, palabra, ha='left', va='center', fontsize=FONT_SIZES['texto'])

        ax.set_yticks([])
        ax.set_xlabel(t('frecuencia'), **ESTILOS['etiquetas'])
        ax.set_title(t('top_palabras_comparacion'), **ESTILOS['titulo'])
        ax.axvline(x=0, color=COLORES['texto'], linewidth=1)
        ax.legend(loc='lower right')
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        guardar_figura(fig, self.output_dir / 'top_palabras_comparacion.png')

    def _generar_sentimiento_vs_subjetividad(self):
        """2.8 Sentimiento vs Subjetividad."""
        if 'Subjetividad' not in self.df.columns:
            return

        # Crear tabla de contingencia
        tabla = pd.crosstab(self.df['Subjetividad'], self.df['Sentimiento'])

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLORES['fondo'])

        t = get_translator()
        sent_labels = get_sentiment_labels()
        from .i18n import get_subjectivity_labels

        subj_labels = get_subjectivity_labels()

        # Translate labels
        tabla = tabla.rename(columns=sent_labels, index=subj_labels)

        tabla.plot.bar(
            ax=ax,
            color=[COLORES_SENTIMIENTO.get(s, '#666') for s in self.df['Sentimiento'].value_counts().index],
            width=0.6,
        )

        ax.set_xlabel(t('subjetividad'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('cantidad_opiniones'), **ESTILOS['etiquetas'])
        ax.set_title(t('sentimiento_vs_subjetividad'), **ESTILOS['titulo'])
        ax.legend(title=t('sentimiento'), bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        guardar_figura(fig, self.output_dir / 'sentimiento_vs_subjetividad.png')

    def _extraer_palabras(self, sentimiento: str) -> list[str]:
        """Extrae palabras limpias de un sentimiento específico."""
        df_sent = self.df[self.df['Sentimiento'] == sentimiento]

        palabras = []
        for texto in df_sent['TituloReview'].dropna():
            texto_limpio = str(texto).lower()
            # Extraer solo palabras alfanuméricas de más de 3 caracteres
            tokens = [
                palabra
                for palabra in texto_limpio.split()
                if len(palabra) > 3 and palabra.isalpha() and palabra not in self.stopwords
            ]
            palabras.extend(tokens)

        return palabras
