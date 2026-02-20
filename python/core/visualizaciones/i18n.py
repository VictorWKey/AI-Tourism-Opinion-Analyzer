"""
Internationalization (i18n) for Visualization Labels
=====================================================
Provides translation support for all chart titles, axis labels,
legend labels, and other text elements in the visualization generators.

Usage:
    from .i18n import get_translator
    t = get_translator()  # reads ANALYSIS_LANGUAGE env var
    t('chart_title')       # returns translated string
"""

import os
from collections.abc import Callable

# ──────────────────────────────────────────────────────────────
# Translation dictionaries
# ──────────────────────────────────────────────────────────────

_TRANSLATIONS = {
    'es': {
        # ── Common labels ──
        'periodo': 'Período',
        'cantidad_opiniones': 'Cantidad de opiniones',
        'sentimiento': 'Sentimiento',
        'calificacion_estrellas': 'Calificación (estrellas)',
        'porcentaje': 'Porcentaje',
        'porcentaje_pct': 'Porcentaje (%)',
        'frecuencia': 'Frecuencia',
        'subjetividad': 'Subjetividad',
        'menciones': 'Menciones',
        'categoria': 'Categoría',
        'calificacion': 'Calificación',
        'mes': 'Mes',
        'cantidad': 'Cantidad',
        'opiniones': 'opiniones',
        # ── Sentiment values (data labels) ──
        'positivo': 'Positivo',
        'neutro': 'Neutro',
        'negativo': 'Negativo',
        # ── Subjectivity values ──
        'subjetiva': 'Subjetiva',
        'mixta': 'Mixta',
        # ── Sentimientos generator ──
        'distribucion_sentimientos': 'Distribución de Sentimientos',
        'evolucion_temporal_sentimientos': 'Evolución Temporal de Sentimientos',
        'sentimientos_por_calificacion': 'Distribución de Sentimientos por Calificación',
        'wordcloud_sentimiento': 'Nube de Palabras - Sentimiento {sentimiento}',
        'top_palabras_comparacion': 'Top 15 Palabras: Negativas vs Positivas',
        'sentimiento_vs_subjetividad': 'Distribución de Sentimientos por Subjetividad',
        # ── Subjetividad generator ──
        'distribucion_subjetividad': 'Distribución de Subjetividad',
        'subjetividad_nota': 'Clasificación binaria · Subjetiva = opinativa · Mixta = subjetiva + objetiva',
        'subjetividad_por_calificacion': 'Subjetividad por Calificación',
        'subjetividad_nota_mixta': 'Mixta = reseñas que combinan contenido subjetivo y objetivo',
        'evolucion_temporal_subjetividad': 'Evolución Temporal de Subjetividad',
        # ── Categorías generator ──
        'categorias_mas_mencionadas': 'Categorías Más Mencionadas',
        'sentimientos_por_categoria': 'Distribución de Sentimientos por Categoría',
        'fortalezas_vs_debilidades': 'Fortalezas vs Debilidades por Categoría',
        'negativo_positivo_axis': '← Negativo % | Positivo % →',
        'radar_chart_360': 'Radar Chart 360° - Percepción por Categoría',
        'matriz_coocurrencia': 'Matriz de Co-ocurrencia de Categorías',
        'coocurrencias': 'Co-ocurrencias',
        'calificacion_por_categoria': 'Distribución de Calificaciones por Categoría',
        'promedio_general': 'Promedio general: {value}',
        'evolucion_categorias': 'Evolución Temporal de Categorías',
        # ── Tópicos generator ──
        'top_subtopicos_mencionados': 'Top 10 Sub-tópicos Más Mencionados',
        'top_subtopicos_problematicos': 'Top 10 Sub-tópicos Problemáticos',
        'pct_sentimiento_negativo': '% Sentimiento Negativo',
        'heatmap_subtopicos': 'Sentimiento por Sub-tópico (color: %, valor: conteo)',
        'pct_del_total': '% del total',
        # ── Temporal generator ──
        'volumen_opiniones_tiempo': 'Volumen de Opiniones en el Tiempo',
        'evolucion_sentimientos': 'Evolución de Sentimientos en el Tiempo',
        'tendencia_calificacion': 'Tendencia de Calificación en el Tiempo',
        'calificacion_promedio': 'Calificación Promedio',
        'opiniones_por_mes': 'Opiniones por mes',
        'promedio_mensual': 'Promedio mensual',
        'tendencia_media_movil': 'Tendencia (media móvil 3m)',
        'estacionalidad_categorias': 'Estacionalidad: Menciones por Categoría y Mes',
        'meses_abrev': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        # ── Texto generator ──
        'wordcloud_general': 'Nube de Palabras - Todas las Opiniones',
        'cantidad_palabras': 'Cantidad de palabras',
        'distribucion_longitud': 'Distribución de Longitud de Textos',
        'media_valor': 'Media: {value}',
        'mediana_valor': 'Mediana: {value}',
        'diagrama_caja_longitud': 'Diagrama de Caja - Longitud',
        'top_bigramas': 'Top 20 Bigramas Más Frecuentes',
        'top_trigramas': 'Top 20 Trigramas Más Frecuentes',
        # ── Combinados generator ──
        'sentimiento_vs_subjetividad_relacion': 'Relación Sentimiento vs Subjetividad',
        'calificacion_categoria_sentimiento': 'Calificación Promedio por Categoría y Sentimiento',
        'volumen_vs_satisfaccion': 'Volumen vs Satisfacción por Categoría',
        'volumen_menciones': 'Volumen de Menciones',
        'pct_opiniones_positivas': '% Opiniones Positivas',
        '50_pct_positivas': '50% positivas',
        'distribucion_calificacion_sentimiento': 'Distribución de Calificación por Sentimiento',
        'tabla_contingencia': 'Tabla de Contingencia Calificación-Sentimiento',
        'distribucion_categorias_calificacion': 'Distribución de Calificaciones por Categoría (%)',
    },
    'en': {
        # ── Common labels ──
        'periodo': 'Period',
        'cantidad_opiniones': 'Number of reviews',
        'sentimiento': 'Sentiment',
        'calificacion_estrellas': 'Rating (stars)',
        'porcentaje': 'Percentage',
        'porcentaje_pct': 'Percentage (%)',
        'frecuencia': 'Frequency',
        'subjetividad': 'Subjectivity',
        'menciones': 'Mentions',
        'categoria': 'Category',
        'calificacion': 'Rating',
        'mes': 'Month',
        'cantidad': 'Count',
        'opiniones': 'reviews',
        # ── Sentiment values (data labels) ──
        'positivo': 'Positive',
        'neutro': 'Neutral',
        'negativo': 'Negative',
        # ── Subjectivity values ──
        'subjetiva': 'Subjective',
        'mixta': 'Mixed',
        # ── Sentimientos generator ──
        'distribucion_sentimientos': 'Sentiment Distribution',
        'evolucion_temporal_sentimientos': 'Temporal Evolution of Sentiments',
        'sentimientos_por_calificacion': 'Sentiment Distribution by Rating',
        'wordcloud_sentimiento': 'Word Cloud - {sentimiento} Sentiment',
        'top_palabras_comparacion': 'Top 15 Words: Negative vs Positive',
        'sentimiento_vs_subjetividad': 'Sentiment Distribution by Subjectivity',
        # ── Subjetividad generator ──
        'distribucion_subjetividad': 'Subjectivity Distribution',
        'subjetividad_nota': 'Binary classification · Subjective = opinionated · Mixed = subjective + objective',
        'subjetividad_por_calificacion': 'Subjectivity by Rating',
        'subjetividad_nota_mixta': 'Mixed = reviews combining subjective and objective content',
        'evolucion_temporal_subjetividad': 'Temporal Evolution of Subjectivity',
        # ── Categorías generator ──
        'categorias_mas_mencionadas': 'Most Mentioned Categories',
        'sentimientos_por_categoria': 'Sentiment Distribution by Category',
        'fortalezas_vs_debilidades': 'Strengths vs Weaknesses by Category',
        'negativo_positivo_axis': '← Negative % | Positive % →',
        'radar_chart_360': 'Radar Chart 360° - Perception by Category',
        'matriz_coocurrencia': 'Category Co-occurrence Matrix',
        'coocurrencias': 'Co-occurrences',
        'calificacion_por_categoria': 'Rating Distribution by Category',
        'promedio_general': 'Overall average: {value}',
        'evolucion_categorias': 'Temporal Evolution of Categories',
        # ── Tópicos generator ──
        'top_subtopicos_mencionados': 'Top 10 Most Mentioned Sub-topics',
        'top_subtopicos_problematicos': 'Top 10 Problematic Sub-topics',
        'pct_sentimiento_negativo': '% Negative Sentiment',
        'heatmap_subtopicos': 'Sentiment by Sub-topic (color: %, value: count)',
        'pct_del_total': '% of total',
        # ── Temporal generator ──
        'volumen_opiniones_tiempo': 'Review Volume Over Time',
        'evolucion_sentimientos': 'Sentiment Evolution Over Time',
        'tendencia_calificacion': 'Rating Trend Over Time',
        'calificacion_promedio': 'Average Rating',
        'opiniones_por_mes': 'Reviews per month',
        'promedio_mensual': 'Monthly average',
        'tendencia_media_movil': 'Trend (3-month moving avg.)',
        'estacionalidad_categorias': 'Seasonality: Mentions by Category and Month',
        'meses_abrev': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        # ── Texto generator ──
        'wordcloud_general': 'Word Cloud - All Reviews',
        'cantidad_palabras': 'Word count',
        'distribucion_longitud': 'Text Length Distribution',
        'media_valor': 'Mean: {value}',
        'mediana_valor': 'Median: {value}',
        'diagrama_caja_longitud': 'Box Plot - Length',
        'top_bigramas': 'Top 20 Most Frequent Bigrams',
        'top_trigramas': 'Top 20 Most Frequent Trigrams',
        # ── Combinados generator ──
        'sentimiento_vs_subjetividad_relacion': 'Sentiment vs Subjectivity Relationship',
        'calificacion_categoria_sentimiento': 'Average Rating by Category and Sentiment',
        'volumen_vs_satisfaccion': 'Volume vs Satisfaction by Category',
        'volumen_menciones': 'Mention Volume',
        'pct_opiniones_positivas': '% Positive Reviews',
        '50_pct_positivas': '50% positive',
        'distribucion_calificacion_sentimiento': 'Rating Distribution by Sentiment',
        'tabla_contingencia': 'Rating-Sentiment Contingency Table',
        'distribucion_categorias_calificacion': 'Rating Distribution by Category (%)',
    },
}


# ── Sentiment label mapping (DataFrame values → translated display) ──
_SENTIMENT_LABELS = {
    'es': {'Positivo': 'Positivo', 'Neutro': 'Neutro', 'Negativo': 'Negativo'},
    'en': {'Positivo': 'Positive', 'Neutro': 'Neutral', 'Negativo': 'Negative'},
}

_SUBJECTIVITY_LABELS = {
    'es': {'Subjetiva': 'Subjetiva', 'Mixta': 'Mixta'},
    'en': {'Subjetiva': 'Subjective', 'Mixta': 'Mixed'},
}

# ── Category label mapping (DataFrame values → translated display) ──
_CATEGORY_LABELS = {
    'es': {},  # identity – Spanish data stays as-is
    'en': {
        'Alojamiento': 'Accommodation',
        'Gastronomía': 'Gastronomy',
        'Transporte': 'Transportation',
        'Eventos y festivales': 'Events and Festivals',
        'Historia y cultura': 'History and Culture',
        'Compras': 'Shopping',
        'Deportes y aventura': 'Sports and Adventure',
        'Vida nocturna': 'Nightlife',
        'Naturaleza': 'Nature',
        'Personal y servicio': 'Staff and Service',
        'Seguridad': 'Safety',
        'Fauna y vida animal': 'Wildlife',
    },
}


def _get_language() -> str:
    """Get the current analysis language from environment variable."""
    return os.environ.get('ANALYSIS_LANGUAGE', 'es')


def get_translator() -> Callable:
    """
    Returns a translation function t(key, **kwargs) for the current language.

    The function accepts format kwargs for string interpolation:
        t('promedio_general', value='4.2') → "Overall average: 4.2"
    """
    lang = _get_language()
    translations = _TRANSLATIONS.get(lang, _TRANSLATIONS['es'])

    def t(key: str, **kwargs) -> str:
        value = translations.get(key)
        if value is None:
            # Fallback to Spanish
            value = _TRANSLATIONS['es'].get(key, key)
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError):
                return value
        return value

    return t


def get_sentiment_labels() -> dict:
    """
    Returns a mapping from DataFrame sentiment values (Spanish) to
    display labels in the current language.

    Example (en): {'Positivo': 'Positive', 'Neutro': 'Neutral', 'Negativo': 'Negative'}
    """
    lang = _get_language()
    return _SENTIMENT_LABELS.get(lang, _SENTIMENT_LABELS['es']).copy()


def get_subjectivity_labels() -> dict:
    """
    Returns a mapping from DataFrame subjectivity values (Spanish) to
    display labels in the current language.

    Example (en): {'Subjetiva': 'Subjective', 'Mixta': 'Mixed'}
    """
    lang = _get_language()
    return _SUBJECTIVITY_LABELS.get(lang, _SUBJECTIVITY_LABELS['es']).copy()


def get_category_labels() -> dict:
    """
    Returns a mapping from DataFrame category values (Spanish) to
    display labels in the current language.

    Example (en): {'Alojamiento': 'Accommodation', 'Gastronomía': 'Gastronomy', ...}
    When lang='es', returns empty dict so .get(x, x) falls through to the original.
    """
    lang = _get_language()
    return _CATEGORY_LABELS.get(lang, _CATEGORY_LABELS['es']).copy()


def translate_category(name: str, cat_labels: dict = None) -> str:
    """Translate a single category name. Convenience helper."""
    if cat_labels is None:
        cat_labels = get_category_labels()
    return cat_labels.get(name, name)


def translate_categories(names, cat_labels: dict = None):
    """
    Translate a list / pandas Index of category names.
    Returns the same type with translated values.
    """
    import pandas as pd

    if cat_labels is None:
        cat_labels = get_category_labels()
    if isinstance(names, pd.Index):
        return names.map(lambda x: cat_labels.get(x, x))
    if isinstance(names, list):
        return [cat_labels.get(x, x) for x in names]
    return names


def translate_series_labels(series_or_index, label_map: dict):
    """
    Rename a pandas Series index or DataFrame columns using a label map.
    Leaves unknown labels unchanged.

    Args:
        series_or_index: pandas Index, Series, or list of labels
        label_map: dict mapping original labels to translated labels

    Returns:
        New object with translated labels
    """
    import pandas as pd

    if isinstance(series_or_index, pd.Index):
        return series_or_index.map(lambda x: label_map.get(x, x))
    if isinstance(series_or_index, pd.Series):
        series_or_index.index = series_or_index.index.map(lambda x: label_map.get(x, x))
        return series_or_index
    if isinstance(series_or_index, list):
        return [label_map.get(x, x) for x in series_or_index]
    return series_or_index
