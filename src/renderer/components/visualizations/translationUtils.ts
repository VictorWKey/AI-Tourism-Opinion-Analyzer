/**
 * Translation utilities for visualization components
 */

import type { TFunction } from 'i18next';

/**
 * Translates a chart name from the backend to the current language.
 * Chart names come from Python with Spanish display names.
 * This function extracts the key from the name and looks up the translation.
 * 
 * @param chartName - The display name from the backend (e.g., "Distribución de Sentimientos")
 * @param t - The translation function from useTranslation
 * @returns The translated chart name
 */
export function translateChartName(chartName: string, t: TFunction): string {
  // Mapping of Spanish display names to translation keys
  const nameToKeyMap: Record<string, string> = {
    'Dashboard Ejecutivo': 'dashboard_ejecutivo',
    'Distribución de Sentimientos': 'distribucion_sentimientos',
    'Evolución Temporal de Sentimientos': 'evolucion_temporal_sentimientos',
    'Sentimientos por Calificación': 'sentimientos_por_calificacion',
    'Sentimientos por Categoría': 'sentimientos_por_categoria',
    'Sentimiento vs Subjetividad': 'sentimiento_vs_subjetividad',
    'Distribución de Subjetividad': 'distribucion_subjetividad',
    'Subjetividad por Calificación': 'subjetividad_por_calificacion',
    'Evolución Temporal de Subjetividad': 'evolucion_temporal_subjetividad',
    'Nube de Palabras - Opiniones Positivas': 'wordcloud_positivo',
    'Nube de Palabras - Opiniones Neutras': 'wordcloud_neutro',
    'Nube de Palabras - Opiniones Negativas': 'wordcloud_negativo',
    'Comparación de Palabras Frecuentes': 'top_palabras_comparacion',
    'Top Categorías Mencionadas': 'top_categorias',
    'Vista 360° - Radar de Categorías': 'radar_chart_360',
    'Fortalezas vs Debilidades': 'fortalezas_vs_debilidades',
    'Matriz de Co-ocurrencia de Categorías': 'matriz_coocurrencia',
    'Calificación Promedio por Categoría': 'calificacion_por_categoria',
    'Evolución de Categorías en el Tiempo': 'evolucion_categorias',
    'Distribución por Categoría y Calificación': 'distribucion_categorias_calificacion',
    'Nube de Palabras General': 'wordcloud_general',
    'Top Subtópicos Más Mencionados': 'top_subtopicos_mencionados',
    'Top Subtópicos Problemáticos': 'top_subtopicos_problematicos',
    'Distribución de Subtópicos': 'distribucion_subtopicos',
    'Evolución de Sentimientos': 'evolucion_sentimientos',
    'Tendencia de Calificación': 'tendencia_calificacion',
    'Estacionalidad de Categorías': 'estacionalidad_categorias',
    'Volumen de Opiniones en el Tiempo': 'volumen_opiniones_tiempo',
    'Distribución de Longitud de Opiniones': 'distribucion_longitud',
    'Top Bigramas': 'top_bigramas',
    'Top Trigramas': 'top_trigramas',
    'Sentimiento y Subjetividad por Categoría': 'sentimiento_subjetividad_categoria',
    'Calificación, Categoría y Sentimiento': 'calificacion_categoria_sentimiento',
    'Volumen vs Sentimiento': 'volumen_vs_sentimiento_scatter',
    'Correlación: Calificación y Sentimiento': 'correlacion_calificacion_sentimiento',
  };

  const key = nameToKeyMap[chartName];
  if (key) {
    return t(`visualizations:chartNames.${key}`);
  }

  // Fallback to original name if no translation found
  return chartName;
}
