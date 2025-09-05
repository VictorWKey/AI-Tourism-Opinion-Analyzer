"""
Visualizaciones para Análisis de Subjetividad
============================================

Este módulo contiene todas las funciones de visualización para el análisis
de subjetividad de opiniones turísticas.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

from .base_subjetividad import ConfiguracionSubjetividad


class VisualizadorSubjetividad:
    """
    Clase para crear visualizaciones del análisis de subjetividad.
    """
    
    def __init__(self):
        """Inicializa el visualizador con la configuración base."""
        self.config = ConfiguracionSubjetividad()
    
    def crear_visualizaciones_basicas(self, df: pd.DataFrame, titulo_ciudad: str = "Ciudad") -> plt.Figure:
        """
        Crea visualizaciones básicas de la subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'SubjetividadHF'
            titulo_ciudad (str): Nombre de la ciudad para el título
        
        Returns:
            plt.Figure: Figura de matplotlib con las visualizaciones
        """
        print("📈 GENERANDO VISUALIZACIONES DE SUBJETIVIDAD")
        print("=" * 50)
        
        # Crear figura con subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Análisis de Subjetividad - Opiniones Turísticas de {titulo_ciudad}', 
                    fontsize=16, fontweight='bold')
        
        # 1. Gráfico de barras - Distribución de subjetividad
        conteo = df['SubjetividadHF'].value_counts()
        colores = [self.config.obtener_color_subjetividad(cat) for cat in conteo.index]
        
        axes[0,0].bar(conteo.index, conteo.values, color=colores, alpha=0.8, 
                     edgecolor='black', linewidth=1)
        axes[0,0].set_title('Distribución de Subjetividad', fontweight='bold')
        axes[0,0].set_ylabel('Número de Opiniones')
        axes[0,0].set_xlabel('Categoría')
        
        # Agregar valores en las barras
        for i, v in enumerate(conteo.values):
            axes[0,0].text(i, v + 5, str(v), ha='center', va='bottom', fontweight='bold')
        
        # 2. Gráfico de pie - Porcentajes de subjetividad
        axes[0,1].pie(conteo.values, labels=conteo.index, autopct='%1.1f%%', 
                     colors=colores, startangle=90, explode=(0.05, 0.05))
        axes[0,1].set_title('Distribución Porcentual de Subjetividad', fontweight='bold')
        
        # 3. Subjetividad por calificación
        if 'Calificacion' in df.columns:
            subj_by_rating = df.groupby('Calificacion')['SubjetividadHF'].value_counts().unstack(fill_value=0)
            subj_by_rating.plot(kind='bar', ax=axes[1,0], 
                               color=[self.config.obtener_color_subjetividad(col) 
                                     for col in subj_by_rating.columns])
            axes[1,0].set_title('Subjetividad por Calificación', fontweight='bold')
            axes[1,0].set_xlabel('Calificación (1-5 estrellas)')
            axes[1,0].set_ylabel('Número de Opiniones')
            axes[1,0].legend(title='Subjetividad')
            axes[1,0].tick_params(axis='x', rotation=0)
        else:
            axes[1,0].text(0.5, 0.5, 'No hay datos de calificación disponibles', 
                          ha='center', va='center', transform=axes[1,0].transAxes)
            axes[1,0].set_title('Subjetividad por Calificación', fontweight='bold')
        
        # 4. Top 5 atracciones por texto subjetivo
        if 'Atraccion' in df.columns:
            top_atracciones = df[df['SubjetividadHF'] == 'Subjetivo']['Atraccion'].value_counts().head(5)
            if len(top_atracciones) > 0:
                axes[1,1].barh(range(len(top_atracciones)), top_atracciones.values, 
                              color=self.config.obtener_color_subjetividad('Subjetivo'), alpha=0.8)
                axes[1,1].set_yticks(range(len(top_atracciones)))
                axes[1,1].set_yticklabels([atrac[:30] + '...' if len(atrac) > 30 else atrac 
                                          for atrac in top_atracciones.index])
                axes[1,1].set_title('Top 5 Atracciones con Texto Subjetivo', fontweight='bold')
                axes[1,1].set_xlabel('Número de Opiniones Subjetivas')
            else:
                axes[1,1].text(0.5, 0.5, 'No hay datos de atracciones subjetivas', 
                              ha='center', va='center', transform=axes[1,1].transAxes)
                axes[1,1].set_title('Top 5 Atracciones con Texto Subjetivo', fontweight='bold')
        else:
            axes[1,1].text(0.5, 0.5, 'No hay datos de atracciones disponibles', 
                          ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('Top 5 Atracciones con Texto Subjetivo', fontweight='bold')
        
        plt.tight_layout()
        
        print("✅ Visualizaciones generadas exitosamente")
        return fig
    
    def crear_visualizacion_detallada(self, df: pd.DataFrame, titulo_ciudad: str = "Ciudad") -> plt.Figure:
        """
        Crea visualizaciones más detalladas del análisis de subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'SubjetividadHF'
            titulo_ciudad (str): Nombre de la ciudad para el título
            
        Returns:
            plt.Figure: Figura con visualizaciones detalladas
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Análisis Detallado de Subjetividad - {titulo_ciudad}', 
                     fontsize=16, fontweight='bold')
        
        # 1. Distribución básica
        conteo = df['SubjetividadHF'].value_counts()
        colores = [self.config.obtener_color_subjetividad(cat) for cat in conteo.index]
        
        axes[0,0].bar(conteo.index, conteo.values, color=colores, alpha=0.8)
        axes[0,0].set_title('Distribución General')
        axes[0,0].set_ylabel('Número de Opiniones')
        
        # 2. Por atracción (top 8)
        if 'Atraccion' in df.columns:
            subj_por_atraccion = df.groupby('Atraccion')['SubjetividadHF'].value_counts().unstack(fill_value=0)
            top_atracciones = subj_por_atraccion.sum(axis=1).nlargest(8)
            subj_top = subj_por_atraccion.loc[top_atracciones.index]
            
            subj_top.plot(kind='bar', ax=axes[0,1], 
                         color=[self.config.obtener_color_subjetividad(col) for col in subj_top.columns])
            axes[0,1].set_title('Subjetividad por Atracción (Top 8)')
            axes[0,1].set_ylabel('Número de Opiniones')
            axes[0,1].tick_params(axis='x', rotation=45)
            axes[0,1].legend(title='Categoría')
        
        # 3. Longitud de texto por categoría
        if 'TituloReview' in df.columns:
            df_temp = df.copy()
            df_temp['LongitudTexto'] = df_temp['TituloReview'].astype(str).str.len()
            
            categorias = df_temp['SubjetividadHF'].unique()
            longitudes_por_categoria = [df_temp[df_temp['SubjetividadHF'] == cat]['LongitudTexto'] 
                                       for cat in categorias]
            
            axes[0,2].boxplot(longitudes_por_categoria, labels=categorias)
            axes[0,2].set_title('Longitud de Texto por Categoría')
            axes[0,2].set_ylabel('Caracteres')
            axes[0,2].set_xlabel('Categoría')
        
        # 4. Subjetividad por calificación (detallado)
        if 'Calificacion' in df.columns:
            subj_by_rating = df.groupby('Calificacion')['SubjetividadHF'].value_counts(normalize=True).unstack(fill_value=0)
            subj_by_rating.plot(kind='bar', ax=axes[1,0], stacked=True,
                               color=[self.config.obtener_color_subjetividad(col) for col in subj_by_rating.columns])
            axes[1,0].set_title('Proporción de Subjetividad por Calificación')
            axes[1,0].set_ylabel('Proporción')
            axes[1,0].set_xlabel('Calificación')
            axes[1,0].tick_params(axis='x', rotation=0)
            axes[1,0].legend(title='Categoría')
        
        # 5. Heatmap de subjetividad por atracción y calificación
        if 'Atraccion' in df.columns and 'Calificacion' in df.columns:
            # Crear tabla pivote para el heatmap
            df_subjetivo = df[df['SubjetividadHF'] == 'Subjetivo']
            if len(df_subjetivo) > 0:
                pivot_data = df_subjetivo.groupby(['Atraccion', 'Calificacion']).size().unstack(fill_value=0)
                # Tomar solo las top 10 atracciones
                if len(pivot_data) > 10:
                    top_10_atracciones = pivot_data.sum(axis=1).nlargest(10).index
                    pivot_data = pivot_data.loc[top_10_atracciones]
                
                sns.heatmap(pivot_data, annot=True, fmt='d', cmap='Reds', ax=axes[1,1])
                axes[1,1].set_title('Opiniones Subjetivas por Atracción y Calificación')
                axes[1,1].set_ylabel('Atracción')
                axes[1,1].set_xlabel('Calificación')
        
        # 6. Tendencia temporal (si hay fecha)
        if 'Fecha' in df.columns:
            try:
                df_temp = df.copy()
                df_temp['Fecha'] = pd.to_datetime(df_temp['Fecha'], errors='coerce')
                df_temp = df_temp.dropna(subset=['Fecha'])
                
                if len(df_temp) > 0:
                    temporal = df_temp.groupby([df_temp['Fecha'].dt.to_period('M'), 'SubjetividadHF']).size().unstack(fill_value=0)
                    temporal.plot(ax=axes[1,2], color=[self.config.obtener_color_subjetividad(col) for col in temporal.columns])
                    axes[1,2].set_title('Tendencia Temporal de Subjetividad')
                    axes[1,2].set_ylabel('Número de Opiniones')
                    axes[1,2].set_xlabel('Período')
                    axes[1,2].legend(title='Categoría')
                else:
                    axes[1,2].text(0.5, 0.5, 'No hay datos temporales válidos', 
                                  ha='center', va='center', transform=axes[1,2].transAxes)
            except:
                axes[1,2].text(0.5, 0.5, 'Error procesando datos temporales', 
                              ha='center', va='center', transform=axes[1,2].transAxes)
        else:
            axes[1,2].text(0.5, 0.5, 'No hay datos temporales disponibles', 
                          ha='center', va='center', transform=axes[1,2].transAxes)
        
        plt.tight_layout()
        print("✅ Visualizaciones detalladas generadas exitosamente")
        return fig
