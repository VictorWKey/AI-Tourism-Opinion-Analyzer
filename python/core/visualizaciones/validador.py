"""
Validador de Visualizaciones
=============================
Sistema inteligente que determina qué visualizaciones son viables
según el volumen y características del dataset.
"""

import pandas as pd
from typing import Dict, Tuple
from datetime import datetime, timedelta


class ValidadorVisualizaciones:
    """
    Valida el dataset y decide qué visualizaciones renderizar.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.n_opiniones = len(df)
        self.tiene_fechas = self._validar_fechas()
        self.tiene_calificacion = 'Calificacion' in df.columns and df['Calificacion'].notna().sum() > 0
        self.tiene_topicos = self._validar_topicos()
        self.categorias_validas = self._validar_categorias()
        self.rango_temporal = self._calcular_rango_temporal()
        self.diversidad_sentimientos = self._calcular_diversidad()
        
    def _validar_fechas(self) -> bool:
        """Valida si hay fechas válidas."""
        if 'FechaEstadia' not in self.df.columns:
            return False
        
        fechas = pd.to_datetime(self.df['FechaEstadia'], errors='coerce')
        return fechas.notna().sum() >= 20
    
    def _validar_topicos(self) -> bool:
        """Valida si hay tópicos identificados."""
        if 'Topico' not in self.df.columns:
            return False
        
        topicos_validos = self.df['Topico'].apply(
            lambda x: x and str(x).strip() not in ['{}', 'nan', 'None', '']
        ).sum()
        
        return topicos_validos / len(self.df) > 0.3  # >30% con tópicos
    
    def _validar_categorias(self) -> int:
        """Cuenta categorías válidas."""
        if 'Categorias' not in self.df.columns:
            return 0
        
        todas_cats = set()
        for cats in self.df['Categorias'].dropna():
            try:
                cats_str = str(cats).strip("[]'\"").replace("'", "").replace('"', '')
                cats_list = [c.strip() for c in cats_str.split(',')]
                todas_cats.update([c for c in cats_list if c])
            except:
                continue
        
        return len(todas_cats)
    
    def _calcular_rango_temporal(self) -> int:
        """Calcula rango temporal en días."""
        if not self.tiene_fechas:
            return 0
        
        fechas = pd.to_datetime(self.df['FechaEstadia'], errors='coerce').dropna()
        if len(fechas) < 2:
            return 0
        
        rango = (fechas.max() - fechas.min()).days
        return rango
    
    def _calcular_diversidad(self) -> Dict:
        """Calcula diversidad de sentimientos."""
        if 'Sentimiento' not in self.df.columns:
            return {'positivo': 0, 'neutro': 0, 'negativo': 0}
        
        conteo = self.df['Sentimiento'].value_counts()
        return {
            'positivo': conteo.get('Positivo', 0),
            'neutro': conteo.get('Neutro', 0),
            'negativo': conteo.get('Negativo', 0)
        }
    
    def puede_renderizar(self, viz_name: str) -> Tuple[bool, str]:
        """
        Determina si una visualización es viable.
        
        Args:
            viz_name: Nombre de la visualización
            
        Returns:
            Tupla (puede_renderizar, razon)
        """
        reglas = {
            # Dashboard (graph-only)
            'dashboard_ejecutivo': (self.n_opiniones >= 10, 'Requiere ≥10 opiniones'),
            
            # Sentimientos
            'distribucion_sentimientos': (self.n_opiniones >= 5, 'Requiere ≥5 opiniones'),
            'evolucion_temporal_sentimientos': (
                self.tiene_fechas and self.n_opiniones >= 30 and self.rango_temporal > 60,
                'Requiere fechas, ≥30 opiniones y rango >60 días'
            ),
            'sentimientos_por_calificacion': (self.tiene_calificacion and self.n_opiniones >= 30, 'Requiere columna Calificacion y ≥30 opiniones'),
            'wordcloud_positivo': (self.diversidad_sentimientos['positivo'] >= 15, 'Requiere ≥15 opiniones positivas'),
            'wordcloud_neutro': (self.diversidad_sentimientos['neutro'] >= 15, 'Requiere ≥15 opiniones neutras'),
            'wordcloud_negativo': (self.diversidad_sentimientos['negativo'] >= 15, 'Requiere ≥15 opiniones negativas'),
            'top_palabras_comparacion': (
                self.diversidad_sentimientos['positivo'] >= 10 and self.diversidad_sentimientos['negativo'] >= 10,
                'Requiere ≥10 opiniones por sentimiento (pos/neg)'
            ),
            'sentimiento_vs_subjetividad': (self.n_opiniones >= 20, 'Requiere ≥20 opiniones'),
            
            # Categorías
            'top_categorias': (self.n_opiniones >= 5, 'Requiere ≥5 opiniones'),
            'sentimientos_por_categoria': (self.n_opiniones >= 10, 'Requiere ≥10 opiniones'),
            'fortalezas_vs_debilidades': (self.n_opiniones >= 10, 'Requiere ≥10 opiniones'),
            'radar_chart_360': (self.n_opiniones >= 50 and self.categorias_validas >= 4, 'Requiere ≥50 opiniones y ≥4 categorías'),
            'matriz_coocurrencia': (self.n_opiniones >= 100 and self.categorias_validas >= 3, 'Requiere ≥100 opiniones y ≥3 categorías'),
            'calificacion_por_categoria': (self.tiene_calificacion and self.n_opiniones >= 30, 'Requiere columna Calificacion y ≥30 opiniones'),
            'evolucion_categorias': (self.tiene_fechas and self.n_opiniones >= 60, 'Requiere fechas y ≥60 opiniones'),
            'wordclouds_por_categoria': (self.n_opiniones >= 50, 'Requiere ≥50 opiniones'),
            
            # Tópicos
            'sunburst_jerarquico': (self.tiene_topicos and self.n_opiniones >= 50, 'Requiere tópicos y ≥50 opiniones'),
            'treemap_subtopicos': (self.tiene_topicos and self.n_opiniones >= 30, 'Requiere tópicos y ≥30 opiniones'),
            'top_subtopicos_mencionados': (self.tiene_topicos and self.n_opiniones >= 20, 'Requiere tópicos y ≥20 opiniones'),
            'top_subtopicos_problematicos': (self.tiene_topicos and self.n_opiniones >= 20, 'Requiere tópicos y ≥20 opiniones'),
            'distribucion_subtopicos': (self.tiene_topicos and self.n_opiniones >= 50, 'Requiere tópicos y ≥50 opiniones'),
            'wordcloud_subtopicos': (self.tiene_topicos and self.n_opiniones >= 30, 'Requiere tópicos y ≥30 opiniones'),
            
            # Temporal
            'volumen_opiniones_tiempo': (self.tiene_fechas and self.n_opiniones >= 20 and self.rango_temporal > 30, 'Requiere fechas, ≥20 opiniones y rango >30 días'),
            'evolucion_sentimientos': (self.tiene_fechas and self.n_opiniones >= 30 and self.rango_temporal > 60, 'Requiere fechas, ≥30 opiniones y rango >60 días'),
            'calendar_heatmap': (self.tiene_fechas and self.n_opiniones >= 100 and self.rango_temporal > 90, 'Requiere fechas, ≥100 opiniones y rango >90 días'),
            'tendencia_calificacion': (self.tiene_calificacion and self.tiene_fechas and self.n_opiniones >= 50 and self.rango_temporal > 60, 'Requiere columna Calificacion, fechas, ≥50 opiniones y rango >60 días'),
            'estacionalidad_categorias': (self.tiene_fechas and self.n_opiniones >= 100 and self.rango_temporal > 180, 'Requiere fechas, ≥100 opiniones y rango >180 días'),
            
            # Texto
            'wordcloud_general': (self.n_opiniones >= 20, 'Requiere ≥20 opiniones'),
            'distribucion_longitud': (self.n_opiniones >= 30, 'Requiere ≥30 opiniones'),
            'top_bigramas': (self.n_opiniones >= 100, 'Requiere ≥100 opiniones'),
            'top_trigramas': (self.n_opiniones >= 100, 'Requiere ≥100 opiniones'),
            
            # Combinados
            'sentimiento_subjetividad_categoria': (self.n_opiniones >= 100, 'Requiere ≥100 opiniones'),
            'calificacion_categoria_sentimiento': (self.tiene_calificacion and self.n_opiniones >= 50, 'Requiere columna Calificacion y ≥50 opiniones'),
            'volumen_vs_sentimiento_scatter': (self.n_opiniones >= 50 and self.categorias_validas >= 5, 'Requiere ≥50 opiniones y ≥5 categorías'),
            'correlacion_calificacion_sentimiento': (self.tiene_calificacion and self.n_opiniones >= 50, 'Requiere columna Calificacion y ≥50 opiniones'),
            'distribucion_categorias_calificacion': (self.tiene_calificacion and self.n_opiniones >= 100, 'Requiere columna Calificacion y ≥100 opiniones'),
        }
        
        resultado = reglas.get(viz_name, (True, ''))
        return resultado
    
    def get_resumen(self) -> Dict:
        """Retorna resumen de validación."""
        return {
            'total_opiniones': self.n_opiniones,
            'tiene_fechas': self.tiene_fechas,
            'tiene_calificacion': self.tiene_calificacion,
            'rango_temporal_dias': self.rango_temporal,
            'tiene_topicos': self.tiene_topicos,
            'categorias_validas': self.categorias_validas,
            'diversidad_sentimientos': self.diversidad_sentimientos
        }
