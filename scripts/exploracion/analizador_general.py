"""
Analizador General - Información básica del dataset
"""

import pandas as pd
import numpy as np


class AnalizadorGeneral:
    """Analiza información general del dataset."""
    
    def __init__(self, df):
        self.df = df
    
    def analizar_informacion_general(self):
        """
        Muestra información general del dataset.
        """
        print("=== INFORMACIÓN GENERAL DEL DATASET ===")
        print(f"Dimensiones: {self.df.shape}")
        print(f"Número de filas: {self.df.shape[0]:,}")
        print(f"Número de columnas: {self.df.shape[1]}")
        print("\nColumnas del dataset:")
        for i, col in enumerate(self.df.columns, 1):
            print(f"{i}. {col}")
        
        print("\n=== TIPOS DE DATOS ===")
        self.df.info()
    
    def analizar_valores_nulos(self):
        """
        Analiza los valores nulos en el dataset.
        """
        print("=== ANÁLISIS DE VALORES NULOS ===")
        valores_nulos = self.df.isnull().sum()
        porcentaje_nulos = (valores_nulos / len(self.df)) * 100
        
        resumen_nulos = pd.DataFrame({
            'Valores_Nulos': valores_nulos,
            'Porcentaje': porcentaje_nulos
        })
        
        resumen_nulos = resumen_nulos.sort_values('Porcentaje', ascending=False)
        print(resumen_nulos)
        
        return resumen_nulos
    
    def analizar_duplicados(self):
        """
        Analiza duplicados en el dataset sin eliminarlos.
        """
        print("=== ANÁLISIS DE DUPLICADOS ===")
        
        # Duplicados completos
        duplicados_completos = self.df.duplicated().sum()
        print(f"Filas completamente duplicadas encontradas: {duplicados_completos}")
        
        # Duplicados por combinación de columnas importantes
        if 'Titulo' in self.df.columns and 'Review' in self.df.columns:
            duplicados_contenido = self.df.duplicated(subset=['Titulo', 'Review', 'Ciudad', 'Atraccion']).sum()
            print(f"Duplicados por título + review + ciudad + atracción: {duplicados_contenido}")
        
        if duplicados_completos > 0:
            porcentaje_duplicados = (duplicados_completos / len(self.df)) * 100
            print(f"Porcentaje de duplicados completos: {porcentaje_duplicados:.2f}%")
        
        return duplicados_completos
