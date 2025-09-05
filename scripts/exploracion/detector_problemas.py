"""
Detector de Problemas - Detecta contenidos mal ubicados y otros problemas
"""

import pandas as pd
import re


class DetectorProblemas:
    """Detecta problemas en el dataset."""
    
    def __init__(self, df):
        self.df = df
    
    def detectar_contenidos_mal_ubicados(self, min_longitud=10):
        """
        Detecta cuando el contenido de una columna aparece incorrectamente en otra columna.
        
        Args:
            min_longitud: Longitud mínima del texto para considerar en el análisis
        
        Returns:
            dict: Resultados de contenidos mal ubicados por par de columnas
            list: Lista de problemas encontrados
        """
        print("=== ANÁLISIS AVANZADO DE CONTENIDOS MAL UBICADOS ===")
        print("Detectando cuando el contenido de una columna aparece en otra columna diferente...")
        
        # Solo columnas de texto para analizar
        columnas_texto = ['Titulo', 'Review', 'TipoViaje', 'OrigenAutor']
        
        # Filtrar solo las columnas que existen en el dataframe y son de tipo texto
        columnas_existentes = []
        for col in columnas_texto:
            if col in self.df.columns:
                dtype = self.df[col].dtype
                if dtype == 'object' or pd.api.types.is_string_dtype(dtype):
                    columnas_existentes.append(col)
        
        resultados = {}
        problemas_encontrados = []
        
        print(f"Analizando columnas de texto: {columnas_existentes}")
        print(f"Longitud mínima de texto: {min_longitud} caracteres\n")
        
        # Iterar sobre todas las combinaciones de columnas
        for i, col1 in enumerate(columnas_existentes):
            for j, col2 in enumerate(columnas_existentes):
                if i != j:  # No comparar una columna consigo misma
                    
                    # Crear sets de valores únicos no nulos y con longitud suficiente
                    valores_col1 = set()
                    valores_col2 = set()
                    
                    for valor in self.df[col1].dropna():
                        valor_str = str(valor).strip()
                        if len(valor_str) >= min_longitud:
                            valores_col1.add(valor_str.lower())
                    
                    for valor in self.df[col2].dropna():
                        valor_str = str(valor).strip()
                        if len(valor_str) >= min_longitud:
                            valores_col2.add(valor_str.lower())
                    
                    # Encontrar intersección
                    contenidos_duplicados = valores_col1.intersection(valores_col2)
                    
                    if contenidos_duplicados:
                        par_columnas = f"{col1} ↔ {col2}"
                        resultados[par_columnas] = contenidos_duplicados
                        
                        print(f"⚠️  PROBLEMA DETECTADO: {par_columnas}")
                        print(f"   Contenidos duplicados encontrados: {len(contenidos_duplicados)}")
                        
                        # Mostrar algunos ejemplos
                        ejemplos = list(contenidos_duplicados)[:3]
                        for ejemplo in ejemplos:
                            # Encontrar las filas específicas donde ocurre esto
                            col1_str = self.df[col1].astype(str).str.lower().str.strip()
                            col2_str = self.df[col2].astype(str).str.lower().str.strip()
                            
                            filas_col1 = self.df[col1_str == ejemplo].index.tolist()
                            filas_col2 = self.df[col2_str == ejemplo].index.tolist()
                            
                            print(f"   📝 Ejemplo: '{ejemplo[:50]}...'")
                            print(f"      - En {col1}: filas {filas_col1[:3]}")
                            print(f"      - En {col2}: filas {filas_col2[:3]}")
                        
                        print()
                        
                        # Guardar información del problema
                        problemas_encontrados.append({
                            'columna_1': col1,
                            'columna_2': col2,
                            'contenidos_duplicados': len(contenidos_duplicados),
                            'ejemplos': ejemplos[:5]
                        })
        
        print(f"=== RESUMEN DEL ANÁLISIS ===")
        if problemas_encontrados:
            print(f"❌ Se encontraron {len(problemas_encontrados)} problemas de contenidos mal ubicados")
            print(f"Total de pares de columnas con problemas: {len(resultados)}")
            
            # Resumen por tipo de problema
            print(f"\n📊 ESTADÍSTICAS DE PROBLEMAS:")
            for problema in problemas_encontrados:
                print(f"   {problema['columna_1']} ↔ {problema['columna_2']}: {problema['contenidos_duplicados']} contenidos duplicados")
        else:
            print("✅ No se encontraron contenidos mal ubicados entre columnas")
            print("   El dataset parece estar bien estructurado en este aspecto")
        
        return resultados, problemas_encontrados
