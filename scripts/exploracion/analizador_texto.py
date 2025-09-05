"""
Analizador de Texto - Análisis de campos de texto
"""

import pandas as pd


class AnalizadorTexto:
    """Analiza campos de texto del dataset."""
    
    def __init__(self, df):
        self.df = df
    
    def analizar_longitud_textos(self):
        """
        Analiza la longitud de campos de texto.
        """
        if 'Titulo' in self.df.columns:
            longitud_titulo = self.df['Titulo'].astype(str).str.len()
            print("=== ANÁLISIS DE LONGITUD DE TÍTULOS ===")
            print(longitud_titulo.describe())

        if 'Review' in self.df.columns:
            longitud_review = self.df['Review'].astype(str).str.len()
            print("\n=== ANÁLISIS DE LONGITUD DE REVIEWS ===")
            print(longitud_review.describe())
            
            # Contar palabras en reviews
            palabras_review = self.df['Review'].astype(str).str.split().str.len()
            print("\n=== NÚMERO DE PALABRAS EN REVIEWS ===")
            print(palabras_review.describe())
    
    def analizar_texto_consolidado(self):
        """
        Analiza texto consolidado si existe.
        """
        if 'texto_consolidado' in self.df.columns:
            print(f"\n📝 ANÁLISIS DE TEXTO CONSOLIDADO:")
            longitud_texto = self.df['texto_consolidado'].str.len()
            palabras_texto = self.df['texto_consolidado'].str.split().str.len()
            print(f"   • Longitud promedio: {longitud_texto.mean():.1f} caracteres")
            print(f"   • Palabras promedio: {palabras_texto.mean():.1f} palabras")
            print(f"   • Texto más corto: {longitud_texto.min()} caracteres")
            print(f"   • Texto más largo: {longitud_texto.max()} caracteres")
