"""
Configuraciones Base para Análisis de Sentimientos
================================================

Este módulo contiene las configuraciones base, mapeos y constantes
utilizadas en el análisis de sentimientos.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

from typing import Dict


class ConfiguracionSentimientos:
    """
    Clase que contiene todas las configuraciones base para el análisis de sentimientos.
    """
    
    # Mapeo de calificaciones de estrellas a sentimientos
    MAPEO_CALIFICACIONES = {
        1: "Negativo",
        2: "Negativo", 
        3: "Neutro",
        4: "Positivo",
        5: "Positivo"
    }
    
    # Colores para visualizaciones
    COLORES_SENTIMIENTOS = {
        'Positivo': '#2ecc71',   # Verde
        'Neutro': '#f39c12',     # Naranja
        'Negativo': '#e74c3c'    # Rojo
    }
    
    # Mapeo de etiquetas de HuggingFace a nuestras categorías
    MAPEO_ETIQUETAS_HF = {
        'POSITIVE': 'Positivo',
        'NEGATIVE': 'Negativo', 
        'NEUTRAL': 'Neutro',
        'POS': 'Positivo',
        'NEG': 'Negativo',
        'NEU': 'Neutro',
        '1 star': 'Negativo',
        '2 stars': 'Negativo',
        '3 stars': 'Neutro',
        '4 stars': 'Positivo',
        '5 stars': 'Positivo'
    }
    
    # Sentimientos válidos
    SENTIMIENTOS_VALIDOS = ['Positivo', 'Neutro', 'Negativo']
    
    # Configuración de modelos por defecto
    MODELO_HUGGINGFACE_DEFAULT = "nlptown/bert-base-multilingual-uncased-sentiment"
    
    @classmethod
    def mapear_calificacion_a_sentimiento(cls, calificacion: float) -> str:
        """
        Mapea una calificación de estrellas (1-5) a una categoría de sentimiento.
        
        Args:
            calificacion (float): Calificación de 1 a 5 estrellas
        
        Returns:
            str: Sentimiento mapeado ('Positivo', 'Neutro', 'Negativo')
        """
        import pandas as pd
        
        if pd.isna(calificacion):
            return "Neutro"
        
        if calificacion >= 4:
            return "Positivo"
        elif calificacion == 3:
            return "Neutro"
        else:  # calificacion <= 2
            return "Negativo"
    
    @classmethod
    def obtener_color_sentimiento(cls, sentimiento: str) -> str:
        """
        Obtiene el color asociado a un sentimiento.
        
        Args:
            sentimiento (str): Sentimiento ('Positivo', 'Neutro', 'Negativo')
            
        Returns:
            str: Código de color hexadecimal
        """
        return cls.COLORES_SENTIMIENTOS.get(sentimiento, '#95a5a6')
    
    @classmethod
    def validar_sentimiento(cls, sentimiento: str) -> bool:
        """
        Valida si un sentimiento es válido.
        
        Args:
            sentimiento (str): Sentimiento a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        return sentimiento in cls.SENTIMIENTOS_VALIDOS


# Crear instancia global para fácil acceso
config = ConfiguracionSentimientos()
