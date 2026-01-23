"""
Generador de Análisis Temporal
================================
Sección 5: Temporal (visualizaciones esenciales)
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List
from .utils import COLORES, COLORES_SENTIMIENTO, ESTILOS, guardar_figura


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
        
        return generadas
    
    def _generar_volumen_temporal(self):
        """5.1 Volumen de Opiniones en el Tiempo."""
        df_fechas = self.df[self.df['FechaEstadia'].notna()].copy()
        df_fechas['FechaEstadia'] = pd.to_datetime(df_fechas['FechaEstadia'])
        df_fechas['Mes'] = df_fechas['FechaEstadia'].dt.to_period('M')
        
        volumen = df_fechas.groupby('Mes').size()
        
        fig, ax = plt.subplots(figsize=(14, 6), facecolor='white')
        
        volumen.plot(kind='bar', ax=ax, color=COLORES['primario'], alpha=0.7)
        
        ax.set_xlabel('Período', **ESTILOS['etiquetas'])
        ax.set_ylabel('Cantidad de opiniones', **ESTILOS['etiquetas'])
        ax.set_title('Volumen de Opiniones en el Tiempo', **ESTILOS['titulo'])
        ax.grid(True, axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        
        guardar_figura(fig, self.output_dir / 'volumen_opiniones_tiempo.png')
    
    def _generar_evolucion_sentimientos(self):
        """5.2 Evolución Temporal de Sentimientos."""
        df_fechas = self.df[self.df['FechaEstadia'].notna()].copy()
        df_fechas['FechaEstadia'] = pd.to_datetime(df_fechas['FechaEstadia'])
        df_fechas['Mes'] = df_fechas['FechaEstadia'].dt.to_period('M')
        
        evol = df_fechas.groupby(['Mes', 'Sentimiento']).size().unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(14, 6), facecolor='white')
        
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
        
        guardar_figura(fig, self.output_dir / 'evolucion_sentimientos.png')
