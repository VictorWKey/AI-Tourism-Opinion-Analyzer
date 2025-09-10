"""
Analizador de Sentimientos Basado en Calificaciones
=================================================

Este módulo contiene la lógica para el análisis de sentimientos basado en calificaciones
de estrellas (1-5) para opiniones turísticas.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

from .base_sentimientos import ConfiguracionSentimientos


class AnalizadorCalificaciones:
    """
    Clase para realizar análisis de sentimientos basado en calificaciones de estrellas.
    
    Esta clase mapea calificaciones de 1-5 estrellas a categorías de sentimiento:
    - 4-5 estrellas → Positivo
    - 3 estrellas → Neutro  
    - 1-2 estrellas → Negativo
    """
    
    def __init__(self):
        """Inicializa el analizador con la configuración base."""
        self.config = ConfiguracionSentimientos()
    
    def mapear_calificacion_a_sentimiento(self, calificacion: float) -> str:
        """
        Mapea una calificación de estrellas (1-5) a una categoría de sentimiento.
        
        Args:
            calificacion (float): Calificación de 1 a 5 estrellas
        
        Returns:
            str: Sentimiento mapeado ('Positivo', 'Neutro', 'Negativo')
        """
        return self.config.mapear_calificacion_a_sentimiento(calificacion)
    
    def procesar_sentimientos_dataset(self, df: pd.DataFrame, columna_calificacion: str = 'Calificacion') -> pd.DataFrame:
        """
        Procesa un dataset completo agregando la columna de sentimientos.
        
        Args:
            df (pd.DataFrame): Dataset a procesar
            columna_calificacion (str): Nombre de la columna con las calificaciones
        
        Returns:
            pd.DataFrame: Dataset con la nueva columna 'Sentimiento'
        """
        # Crear condiciones para el mapeo vectorizado (más eficiente)
        condiciones = [
            df[columna_calificacion] >= 4,  # Positivo
            df[columna_calificacion] == 3,  # Neutro
            df[columna_calificacion] <= 2   # Negativo
        ]
        
        valores = ['Positivo', 'Neutro', 'Negativo']
        
        # Aplicar el mapeo de forma vectorizada
        df_result = df.copy()
        df_result['Sentimiento'] = np.select(condiciones, valores, default='Neutro')
        
        return df_result
    
    def obtener_estadisticas_sentimientos(self, df: pd.DataFrame) -> Dict:
        """
        Genera estadísticas descriptivas de los sentimientos.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'Sentimiento'
        
        Returns:
            Dict: Diccionario con estadísticas de sentimientos
        """
        conteo_sentimientos = df['Sentimiento'].value_counts()
        porcentajes = df['Sentimiento'].value_counts(normalize=True) * 100
        
        estadisticas = {
            'conteo': conteo_sentimientos,
            'porcentajes': porcentajes,
            'total': len(df),
            'tabla_cruzada': pd.crosstab(df['Sentimiento'], df['Calificacion'], margins=True),
            'por_atraccion': df.groupby('Atraccion')['Sentimiento'].value_counts().unstack(fill_value=0)
        }
        
        return estadisticas
    
    def mostrar_estadisticas_consola(self, estadisticas: Dict) -> None:
        """
        Muestra las estadísticas de sentimientos en la consola.
        
        Args:
            estadisticas (Dict): Estadísticas generadas por obtener_estadisticas_sentimientos
        """
        print("📊 ESTADÍSTICAS DESCRIPTIVAS DE SENTIMIENTOS")
        print("=" * 60)
        
        conteo_sentimientos = estadisticas['conteo']
        porcentajes = estadisticas['porcentajes']
        
        print("🔢 DISTRIBUCIÓN DE SENTIMIENTOS:")
        print("-" * 40)
        for sentimiento in ['Positivo', 'Neutro', 'Negativo']:
            if sentimiento in conteo_sentimientos.index:
                count = conteo_sentimientos[sentimiento]
                percent = porcentajes[sentimiento]
                print(f"{sentimiento:>10}: {count:>3} registros ({percent:>5.1f}%)")
            else:
                print(f"{sentimiento:>10}: {0:>3} registros ({0:>5.1f}%)")
        
        print(f"\n📈 TOTAL DE REGISTROS: {estadisticas['total']}")
    
    def mostrar_ejemplos_sentimiento(self, df: pd.DataFrame, sentimiento: str, 
                                   n_ejemplos: int = 3) -> None:
        """
        Muestra ejemplos representativos de un sentimiento específico.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'Sentimiento'
            sentimiento (str): Sentimiento a mostrar ('Positivo', 'Neutro', 'Negativo')
            n_ejemplos (int): Número de ejemplos a mostrar
        """
        ejemplos_disponibles = df[df['Sentimiento'] == sentimiento]
        n_mostrar = min(n_ejemplos, len(ejemplos_disponibles))
        
        print(f"\n🎯 EJEMPLOS DE SENTIMIENTO {sentimiento.upper()}")
        print("-" * 60)
        
        if n_mostrar == 0:
            print(f"   ❌ No se encontraron ejemplos de sentimiento {sentimiento}")
            return
        
        ejemplos = ejemplos_disponibles.sample(n=n_mostrar)
        
        for i, (idx, row) in enumerate(ejemplos.iterrows(), 1):
            print(f"\n📌 Ejemplo {i}:")
            print(f"   🏛️ Atracción: {row['Atraccion']}")
            print(f"   ⭐ Calificación: {row['Calificacion']}/5")
            print(f"   📅 Fecha: {row['FechaEstadia']}")
            print(f"   💬 Opinión: \"{row['TituloReview'][:200]}{'...' if len(row['TituloReview']) > 200 else ''}\"")
            print("   " + "-" * 50)
    
    def mostrar_todos_los_ejemplos(self, df: pd.DataFrame, n_ejemplos: int = 3) -> None:
        """
        Muestra ejemplos de todos los tipos de sentimiento.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'Sentimiento' 
            n_ejemplos (int): Número de ejemplos por sentimiento
        """
        print("📝 EJEMPLOS REPRESENTATIVOS DE CADA SENTIMIENTO")
        print("=" * 70)
        
        for sentimiento in ['Positivo', 'Neutro', 'Negativo']:
            self.mostrar_ejemplos_sentimiento(df, sentimiento, n_ejemplos)
    
    def generar_resumen_final(self, df: pd.DataFrame) -> None:
        """
        Genera un resumen final del análisis de sentimientos.
        
        Args:
            df (pd.DataFrame): Dataset procesado con columna 'Sentimiento'
        """
        print("\n" + "=" * 70)
        print("📊 RESUMEN FINAL")
        print("=" * 70)
        print(f"✅ Análisis completado para {len(df)} opiniones")
        print(f"🏙️ Ciudad analizada: {df['Ciudad'].iloc[0]}")
        print(f"🎯 Atracciones únicas: {df['Atraccion'].nunique()}")
        print(f"📈 Distribución de sentimientos:")
        
        for sentimiento, count in df['Sentimiento'].value_counts().items():
            porcentaje = (count / len(df)) * 100
            print(f"   • {sentimiento}: {count} ({porcentaje:.1f}%)")
        
        print(f"\n🔄 Mapeo utilizado:")
        print(f"   • 4-5 estrellas → Positivo")
        print(f"   • 3 estrellas → Neutro")
        print(f"   • 1-2 estrellas → Negativo")
