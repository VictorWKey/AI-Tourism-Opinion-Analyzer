"""
Configuraciones Base para Análisis de Subjetividad
=================================================

Este módulo contiene las configuraciones base, mapeos y constantes
utilizadas en el análisis de subjetividad.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

from typing import Dict


class ConfiguracionSubjetividad:
    """
    Clase que contiene todas las configuraciones base para el análisis de subjetividad.
    """
    
    # Mapeo de etiquetas de HuggingFace a nuestras categorías
    MAPEO_ETIQUETAS_HF = {
        'SUBJECTIVE': 'Subjetivo',
        'OBJECTIVE': 'Objetivo',
        'SUBJ': 'Subjetivo',
        'OBJ': 'Objetivo',
        'subjective': 'Subjetivo',
        'objective': 'Objetivo',
        'LABEL_0': 'Objetivo',    # Para el modelo mdebertav3-subjectivity-multilingual
        'LABEL_1': 'Subjetivo',  # Para el modelo mdebertav3-subjectivity-multilingual
        1: 'Subjetivo',  # Para modelos que usan números
        0: 'Objetivo'
    }
    
    # Colores para visualizaciones
    COLORES_SUBJETIVIDAD = {
        'Subjetivo': '#e74c3c',    # Rojo (más llamativo para subjetivo)
        'Objetivo': '#3498db'      # Azul (más neutro para objetivo)
    }
    
    # Categorías válidas
    CATEGORIAS_VALIDAS = ['Subjetivo', 'Objetivo']
    
    # Configuración de modelos por defecto
    MODELO_HUGGINGFACE_DEFAULT = "GroNLP/mdebertav3-subjectivity-multilingual"
    
    @classmethod
    def obtener_color_subjetividad(cls, categoria: str) -> str:
        """
        Obtiene el color asociado a una categoría de subjetividad.
        
        Args:
            categoria (str): Categoría ('Subjetivo', 'Objetivo')
            
        Returns:
            str: Código de color hexadecimal
        """
        return cls.COLORES_SUBJETIVIDAD.get(categoria, '#95a5a6')
    
    @classmethod
    def validar_categoria(cls, categoria: str) -> bool:
        """
        Valida si una categoría es válida.
        
        Args:
            categoria (str): Categoría a validar
            
        Returns:
            bool: True si es válida, False en caso contrario
        """
        return categoria in cls.CATEGORIAS_VALIDAS
    
    @classmethod
    def obtener_descripcion_categoria(cls, categoria: str) -> str:
        """
        Obtiene la descripción de una categoría de subjetividad.
        
        Args:
            categoria (str): Categoría ('Subjetivo', 'Objetivo')
            
        Returns:
            str: Descripción de la categoría
        """
        descripciones = {
            'Subjetivo': 'Texto que expresa opiniones, emociones, evaluaciones personales',
            'Objetivo': 'Texto que presenta hechos, información factual sin opiniones'
        }
        return descripciones.get(categoria, 'Categoría no reconocida')
