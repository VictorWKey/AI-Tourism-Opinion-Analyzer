"""
Cargador de Datos para Análisis de Subjetividad
=============================================

Este módulo maneja la carga y preparación de datos para análisis de subjetividad.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import os
from typing import Optional, Tuple

def cargar_dataset_para_subjetividad(ruta_base: str = '../data/processed/') -> Tuple[pd.DataFrame, str]:
    """
    Carga el dataset más apropiado para análisis de subjetividad.
    
    Args:
        ruta_base: Ruta base donde buscar los datasets
        
    Returns:
        Tuple[DataFrame, str]: Dataset cargado y descripción de la fuente
    """
    # Rutas de datasets por prioridad
    rutas_datasets = [
        ('dataset_opiniones_analisis.csv', 'Dataset principal con análisis completo'),
        ('reviews_clasificadas_subjetividad.csv', 'Subjetividad completo'),
        ('dataset_opiniones_consolidado.csv', 'Consolidado general'),
        ('datasets_por_ciudad/sentimientos/simple/dataset_cdmx_sentimientos.csv', 'Sentimientos CDMX')
    ]
    
    for archivo, descripcion in rutas_datasets:
        ruta_completa = os.path.join(ruta_base, archivo)
        if os.path.exists(ruta_completa):
            df = pd.read_csv(ruta_completa)
            return df, descripcion
    
    raise FileNotFoundError("No se encontró ningún dataset válido para análisis")

def verificar_compatibilidad_cuda() -> bool:
    """
    Verifica si CUDA está disponible para aceleración.
    
    Returns:
        bool: True si CUDA está disponible
    """
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def preparar_dataset_mixtas(df: pd.DataFrame, columna_texto: str = 'TituloReview') -> pd.DataFrame:
    """
    Prepara el dataset para análisis de opiniones mixtas.
    
    Args:
        df: DataFrame original
        columna_texto: Columna con el texto a analizar
        
    Returns:
        DataFrame preparado
    """
    df_limpio = df.copy()
    
    # Filtrar textos válidos
    df_limpio = df_limpio[df_limpio[columna_texto].notna()]
    df_limpio = df_limpio[df_limpio[columna_texto].astype(str).str.len() > 10]
    
    return df_limpio

def mostrar_info_dataset(df: pd.DataFrame, fuente: str) -> None:
    """
    Muestra información básica del dataset cargado.
    
    Args:
        df: DataFrame cargado
        fuente: Descripción de la fuente del dataset
    """
    print(f"📊 Dataset cargado: {df.shape[0]} filas | Fuente: {fuente}")
    
    # Verificar si ya tiene análisis de subjetividad (múltiples columnas posibles)
    columnas_subjetividad = ['SubjetividadConHF', 'ClasificacionSubjetividadConHF', 'SubjetividadConFrases']
    columna_encontrada = None
    
    for col in columnas_subjetividad:
        if col in df.columns:
            columna_encontrada = col
            break
    
    if columna_encontrada:
        distribucion = df[columna_encontrada].value_counts()
        print(f"📋 Distribución de subjetividad ({columna_encontrada}):")
        for categoria, cantidad in distribucion.items():
            porcentaje = (cantidad / len(df)) * 100
            print(f"   • {categoria}: {cantidad} ({porcentaje:.1f}%)")
    else:
        print("⚠️ Dataset sin análisis previo de subjetividad")
