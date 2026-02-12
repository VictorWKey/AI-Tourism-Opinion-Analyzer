"""
Fase 01: Procesamiento Básico de Datos
======================================
Este módulo procesa el dataset de opiniones turísticas aplicando:
- Conversión de fechas
- Eliminación de duplicados
- Creación de texto consolidado (TituloReview)
- Mantiene todas las columnas originales del dataset
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import os
from config.config import ConfigDataset


class ProcesadorBasico:
    """
    Procesa el dataset de producción aplicando transformaciones básicas.
    Reads from an input dataset and writes the processed result to the output directory.
    """
    
    def __init__(self, input_path: str = None):
        """Inicializa el procesador.
        
        Args:
            input_path: Path to the user-selected input CSV file.
                       If None, falls back to default dataset or output path.
        """
        # Output path where the processed dataset will be saved
        self.dataset_path = ConfigDataset.get_dataset_path()
        # Input path resolution order:
        # 1. Explicitly provided input_path (user-selected file)
        # 2. Output dataset path (for re-runs when output already exists)
        # 3. Default (bundled) dataset path
        if input_path:
            self.input_path = Path(input_path)
        elif self.dataset_path.exists():
            self.input_path = self.dataset_path
        else:
            self.input_path = ConfigDataset.get_default_dataset_path()
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
        
        # Cargar dataset from input path
        self.df = pd.read_csv(self.input_path)
        filas_iniciales = len(self.df)
        
        # Convertir FechaEstadia (ya está en formato ISO YYYY-MM-DD)
        if 'FechaEstadia' in self.df.columns:
            self.df['FechaEstadia'] = pd.to_datetime(self.df['FechaEstadia'], errors='coerce')
        
        # Eliminar filas con FechaEstadia nula
        self.df = self.df.dropna(subset=['FechaEstadia'])
        
        # Eliminar duplicados
        self.df = self.df.drop_duplicates()
        
        # Crear texto consolidado SOLO si no existe ya
        # Maneja tres casos:
        # 1. Ambas columnas (Titulo + Review) → concatena
        # 2. Solo Review → usa Review como TituloReview
        # 3. Solo Titulo → usa Titulo como TituloReview
        if 'TituloReview' not in self.df.columns:
            has_titulo = 'Titulo' in self.df.columns
            has_review = 'Review' in self.df.columns
            
            if has_titulo and has_review:
                # Caso 1: Ambas columnas existen, concatenar
                self.df['TituloReview'] = self.df.apply(self.crear_texto_consolidado, axis=1)
            elif has_review:
                # Caso 2: Solo Review existe (Titulo es opcional)
                self.df['TituloReview'] = self.df['Review'].fillna('').astype(str)
            elif has_titulo:
                # Caso 3: Solo Titulo existe (edge case)
                self.df['TituloReview'] = self.df['Titulo'].fillna('').astype(str)
            else:
                raise ValueError("El dataset debe contener al menos la columna 'Review' o 'Titulo'")
        
        # Guardar dataset procesado (mantiene todas las columnas existentes)
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(self.dataset_path, index=False)
        
        filas_finales = len(self.df)
        print(f"✅ Fase 01 completada: {filas_iniciales} → {filas_finales} filas | {len(self.df.columns)} columnas")
