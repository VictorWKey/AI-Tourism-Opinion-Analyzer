"""
Analizador Temporal - Análisis de aspectos temporales
"""

import pandas as pd
from datetime import datetime


class AnalizadorTemporal:
    """Analiza aspectos temporales del dataset."""
    
    def __init__(self, df):
        self.df = df
    
    def analizar_temporal(self):
        """
        Analiza aspectos temporales del dataset.
        """
        if 'FechaOpinion' in self.df.columns:
            print("=== ANÁLISIS TEMPORAL DE OPINIONES ===")
            
            # Mostrar algunas fechas de ejemplo
            print("Ejemplos de fechas en el dataset:")
            print(self.df['FechaOpinion'].head(10).tolist())
            
            # Contar valores únicos en fechas
            print(f"\nFechas únicas de opinión: {self.df['FechaOpinion'].nunique()}")
            
            # Mostrar las fechas más comunes
            print("\nTop 10 fechas con más opiniones:")
            print(self.df['FechaOpinion'].value_counts().head(10))
    
    def analisis_temporal_final(self):
        """
        Análisis temporal para dataset final limpio.
        """
        if 'FechaOpinion' in self.df.columns:
            print(f"\n📅 ANÁLISIS TEMPORAL FINAL:")
            rango_fechas = self.df['FechaOpinion'].dropna()
            if len(rango_fechas) > 0:
                fecha_min = rango_fechas.min()
                fecha_max = rango_fechas.max()
                print(f"   • Rango de fechas: {fecha_min.strftime('%d/%m/%Y')} - {fecha_max.strftime('%d/%m/%Y')}")
                print(f"   • Período cubierto: {(fecha_max - fecha_min).days} días")
                
                # Análisis por año
                print(f"   • Distribución por año:")
                dist_años = self.df['FechaOpinion'].dt.year.value_counts().sort_index()
                for año, count in dist_años.items():
                    porcentaje = (count / len(self.df)) * 100
                    print(f"     {año}: {count:,} opiniones ({porcentaje:.1f}%)")
