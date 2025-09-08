"""
Analizador Categórico - Variables categóricas del dataset
"""

import pandas as pd


class AnalizadorCategorico:
    """Analiza variables categóricas del dataset."""
    
    def __init__(self, df):
        self.df = df
    
    def analizar_distribuciones_categoricas(self):
        """
        Analiza las distribuciones de variables categóricas.
        """
        # Distribución por ciudades
        print("=== DISTRIBUCIÓN POR CIUDADES ===")
        distribucion_ciudades = self.df['Ciudad'].value_counts()
        print(distribucion_ciudades)
        print(f"\nPorcentaje por ciudad:")
        print((distribucion_ciudades / distribucion_ciudades.sum() * 100).round(2))
        
    
    def analizar_calificaciones(self):
        """
        Analiza las calificaciones del dataset.
        """
        if 'Calificacion' in self.df.columns:
            print("=== ANÁLISIS DE CALIFICACIONES ===")
            
            # Convertir calificaciones a numérico para análisis
            calificaciones_num = pd.to_numeric(self.df['Calificacion'], errors='coerce')
            
            print("Estadísticas descriptivas de calificaciones:")
            print(calificaciones_num.describe())
            
            print("\nDistribución de calificaciones:")
            print(calificaciones_num.value_counts().sort_index())
            
            print(f"\nCalificación promedio general: {calificaciones_num.mean():.2f}")
    
    def analizar_origen_autor(self):
        """
        Analiza la columna OrigenAutor antes de cualquier limpieza.
        """
        print("=== ANÁLISIS DE VALORES EN OrigenAutor ===")
        print(f"Total de valores únicos: {self.df['OrigenAutor'].nunique()}")
        print(f"Total de valores no nulos: {self.df['OrigenAutor'].notna().sum()}")
        print(f"Valores nulos: {self.df['OrigenAutor'].isna().sum()}")

        print("\n=== PRIMEROS 30 VALORES ÚNICOS ===")
        valores_unicos = self.df['OrigenAutor'].value_counts().head(30)
        for valor, count in valores_unicos.items():
            print(f"'{valor}': {count} veces")

        print(f"\n=== TODOS LOS VALORES ÚNICOS (Muestra de {min(100, self.df['OrigenAutor'].nunique())}) ===")
        todos_valores = self.df['OrigenAutor'].dropna().unique()[:100]
        for i, valor in enumerate(todos_valores, 1):
            print(f"{i:2d}. '{valor}'")
