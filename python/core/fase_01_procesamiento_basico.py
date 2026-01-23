"""
Fase 01: Procesamiento Básico de Datos
======================================
Este módulo procesa el dataset de opiniones turísticas aplicando:
- Conversión de fechas
- Eliminación de duplicados
- Creación de texto consolidado (TituloReview)
- Selección de columnas finales: TituloReview, FechaEstadia, Calificacion
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import os


class ProcesadorBasico:
    """
    Procesa el dataset de producción aplicando transformaciones básicas.
    Modifica el archivo CSV directamente en /production/data/dataset.csv
    """
    
    def __init__(self):
        """Inicializa el procesador con la ruta fija del dataset de producción."""
        # Ruta relativa desde el directorio de producción
        self.dataset_path = Path(__file__).parent.parent / 'data' / 'dataset.csv'
        self.df = None
    
    def crear_texto_consolidado(self, row):
        """
        Crea texto consolidado combinando Titulo y Review.
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            String con el texto consolidado
        """
        titulo = str(row.get('Titulo', '')).strip()
        review = str(row.get('Review', '')).strip()
        
        texto_partes = []
        
        if titulo and titulo.lower() not in ['sin titulo', 'nan', 'none', '']:
            if not titulo.endswith('.'):
                titulo += '.'
            texto_partes.append(titulo)
        
        if review and review.lower() not in ['nan', 'none', '']:
            if not review.endswith('.'):
                review += '.'
            texto_partes.append(review)
        
        return ' '.join(texto_partes) if texto_partes else ''
    
    def ya_procesado(self):
        """
        Verifica si esta fase ya fue ejecutada.
        Revisa si existe la columna 'TituloReview' en el dataset.
        """
        try:
            df = pd.read_csv(self.dataset_path)
            return 'TituloReview' in df.columns
        except:
            return False
    
    def procesar(self, forzar=False):
        """
        Ejecuta el pipeline completo de procesamiento básico.
        Modifica el dataset CSV directamente.
        
        Args:
            forzar: Si es True, ejecuta incluso si ya fue procesado
        """
        if not forzar and self.ya_procesado():
            print("   ⏭️  Fase ya ejecutada previamente (omitiendo)")
            return
        
        # Cargar dataset
        self.df = pd.read_csv(self.dataset_path)
        filas_iniciales = len(self.df)
        
        # Convertir FechaEstadia (ya está en formato ISO YYYY-MM-DD)
        if 'FechaEstadia' in self.df.columns:
            self.df['FechaEstadia'] = pd.to_datetime(self.df['FechaEstadia'], errors='coerce')
        
        # Eliminar filas con FechaEstadia nula
        self.df = self.df.dropna(subset=['FechaEstadia'])
        
        # Eliminar duplicados
        self.df = self.df.drop_duplicates()
        
        # Crear texto consolidado SOLO si no existe ya
        if 'TituloReview' not in self.df.columns and 'Titulo' in self.df.columns and 'Review' in self.df.columns:
            self.df['TituloReview'] = self.df.apply(self.crear_texto_consolidado, axis=1)
        
        # Seleccionar solo las columnas finales
        columnas_finales = ['TituloReview', 'FechaEstadia', 'Calificacion']
        self.df = self.df[columnas_finales]
        
        # Guardar dataset procesado
        self.df.to_csv(self.dataset_path, index=False)
        
        filas_finales = len(self.df)
        print(f"✅ Fase 01 completada: {filas_iniciales} → {filas_finales} filas | {len(self.df.columns)} columnas")
