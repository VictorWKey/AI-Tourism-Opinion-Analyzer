"""
Visualizaciones para Análisis de Sentimientos
============================================

Este módulo contiene todas las funciones de visualización para el análisis
de sentimientos de opiniones turísticas.

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

from .base_sentimientos import ConfiguracionSentimientos


class VisualizadorSentimientos:
    """
    Clase para crear visualizaciones del análisis de sentimientos.
    """
    
    def __init__(self):
        """Inicializa el visualizador con la configuración base."""
        self.config = ConfiguracionSentimientos()
    
    def crear_visualizaciones_basicas(self, df: pd.DataFrame, titulo_ciudad: str = "Cancún") -> plt.Figure:
        """
        Crea visualizaciones básicas de los sentimientos.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'Sentimiento'
            titulo_ciudad (str): Nombre de la ciudad para el título
        
        Returns:
            plt.Figure: Figura de matplotlib con las visualizaciones
        """
        print("📈 GENERANDO VISUALIZACIONES DE SENTIMIENTOS")
        print("=" * 50)
        
        # Crear figura con subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Análisis de Sentimientos - Opiniones Turísticas de {titulo_ciudad}', 
                    fontsize=16, fontweight='bold')
        
        # 1. Gráfico de barras - Distribución de sentimientos
        conteo = df['Sentimiento'].value_counts()
        colores = [self.config.obtener_color_sentimiento(sent) for sent in conteo.index]
        
        axes[0,0].bar(conteo.index, conteo.values, color=colores, alpha=0.8, 
                     edgecolor='black', linewidth=1)
        axes[0,0].set_title('Distribución de Sentimientos', fontweight='bold')
        axes[0,0].set_ylabel('Número de Opiniones')
        axes[0,0].set_xlabel('Sentimiento')
        
        # Agregar valores en las barras
        for i, v in enumerate(conteo.values):
            axes[0,0].text(i, v + 5, str(v), ha='center', va='bottom', fontweight='bold')
        
        # 2. Gráfico de pie - Porcentajes de sentimientos
        axes[0,1].pie(conteo.values, labels=conteo.index, autopct='%1.1f%%', 
                     colors=colores, startangle=90, explode=(0.05, 0.05, 0.05))
        axes[0,1].set_title('Distribución Porcentual de Sentimientos', fontweight='bold')
        
        # 3. Sentimientos por calificación
        sentiment_by_rating = df.groupby('Calificacion')['Sentimiento'].value_counts().unstack(fill_value=0)
        sentiment_by_rating.plot(kind='bar', ax=axes[1,0], 
                               color=[self.config.obtener_color_sentimiento(col) 
                                     for col in sentiment_by_rating.columns])
        axes[1,0].set_title('Sentimientos por Calificación', fontweight='bold')
        axes[1,0].set_xlabel('Calificación (1-5 estrellas)')
        axes[1,0].set_ylabel('Número de Opiniones')
        axes[1,0].legend(title='Sentimiento')
        axes[1,0].tick_params(axis='x', rotation=0)
        
        # 4. Top 5 atracciones por sentimiento positivo
        top_atracciones = df[df['Sentimiento'] == 'Positivo']['Atraccion'].value_counts().head(5)
        if len(top_atracciones) > 0:
            axes[1,1].barh(range(len(top_atracciones)), top_atracciones.values, 
                          color=self.config.obtener_color_sentimiento('Positivo'), alpha=0.8)
            axes[1,1].set_yticks(range(len(top_atracciones)))
            axes[1,1].set_yticklabels([atrac[:30] + '...' if len(atrac) > 30 else atrac 
                                      for atrac in top_atracciones.index])
            axes[1,1].set_title('Top 5 Atracciones con Sentimientos Positivos', fontweight='bold')
            axes[1,1].set_xlabel('Número de Opiniones Positivas')
        else:
            axes[1,1].text(0.5, 0.5, 'No hay datos de atracciones positivas', 
                          ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('Top 5 Atracciones con Sentimientos Positivos', fontweight='bold')
        
        plt.tight_layout()
        
        print("✅ Visualizaciones generadas exitosamente")
        return fig
    
    def crear_visualizacion_comparacion(self, df: pd.DataFrame, comparacion: Dict) -> plt.Figure:
        """
        Crea visualizaciones para comparar métodos de análisis (Calificación vs HuggingFace).
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            comparacion (Dict): Estadísticas de comparación
            
        Returns:
            plt.Figure: Figura con las visualizaciones
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Comparación: Análisis por Calificación vs HuggingFace', 
                     fontsize=16, fontweight='bold')
        
        # 1. Distribución lado a lado
        sentimientos = ['Positivo', 'Neutro', 'Negativo']
        conteo_cal = [df[df['Sentimiento'] == s].shape[0] for s in sentimientos]
        conteo_hf = [df[df['SentimientoHF'] == s].shape[0] for s in sentimientos]
        
        x = np.arange(len(sentimientos))
        width = 0.35
        
        axes[0,0].bar(x - width/2, conteo_cal, width, label='Por Calificación', 
                      color=[self.config.obtener_color_sentimiento(s) for s in sentimientos], alpha=0.7)
        axes[0,0].bar(x + width/2, conteo_hf, width, label='Por HuggingFace',
                      color=[self.config.obtener_color_sentimiento(s) for s in sentimientos], alpha=0.4)
        
        axes[0,0].set_title('Distribución de Sentimientos por Método')
        axes[0,0].set_xlabel('Sentimiento')
        axes[0,0].set_ylabel('Número de Registros')
        axes[0,0].set_xticks(x)
        axes[0,0].set_xticklabels(sentimientos)
        axes[0,0].legend()
        
        # 2. Matriz de confusión como heatmap
        tabla_sin_totales = comparacion['tabla_confusion'].iloc[:-1, :-1]
        sns.heatmap(tabla_sin_totales, annot=True, fmt='d', cmap='Blues', 
                    ax=axes[0,1], cbar_kws={'label': 'Número de Registros'})
        axes[0,1].set_title('Matriz de Confusión')
        axes[0,1].set_ylabel('Clasificación por Calificación')
        axes[0,1].set_xlabel('Clasificación por HuggingFace')
        
        # 3. Concordancia por sentimiento
        sentimientos_stats = comparacion['estadisticas_sentimiento']
        precisiones = [sentimientos_stats[s]['precision'] for s in sentimientos]
        
        bars = axes[1,0].bar(sentimientos, precisiones, 
                             color=[self.config.obtener_color_sentimiento(s) for s in sentimientos],
                             alpha=0.7, edgecolor='black', linewidth=1)
        axes[1,0].set_title('Concordancia por Tipo de Sentimiento')
        axes[1,0].set_xlabel('Sentimiento')
        axes[1,0].set_ylabel('Porcentaje de Concordancia (%)')
        axes[1,0].set_ylim(0, 100)
        
        # Agregar valores en las barras
        for bar, precision in zip(bars, precisiones):
            axes[1,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           f'{precision:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 4. Concordancia general
        labels = ['Concordantes', 'Discordantes']
        sizes = [comparacion['concordancia_total'], 
                 comparacion['total_registros'] - comparacion['concordancia_total']]
        colors = ['#2ecc71', '#e74c3c']
        
        axes[1,1].pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
                      startangle=90, explode=(0.05, 0.05))
        axes[1,1].set_title('Concordancia General entre Métodos')
        
        plt.tight_layout()
        return fig
    
    def crear_grafico_temporal_sentimientos(self, df: pd.DataFrame, titulo: str = "Evolución Temporal") -> plt.Figure:
        """
        Crea un gráfico de evolución temporal de sentimientos si hay columna de fecha.
        
        Args:
            df (pd.DataFrame): Dataset con columnas de sentimiento y fecha
            titulo (str): Título del gráfico
            
        Returns:
            plt.Figure: Figura con el gráfico temporal
        """
        if 'FechaEstadia' not in df.columns:
            print("❌ No se encontró columna 'FechaEstadia' para análisis temporal")
            return None
        
        # Convertir fecha si es necesario
        df_temp = df.copy()
        df_temp['FechaEstadia'] = pd.to_datetime(df_temp['FechaEstadia'], errors='coerce')
        df_temp = df_temp.dropna(subset=['FechaEstadia'])
        
        if len(df_temp) == 0:
            print("❌ No hay fechas válidas para análisis temporal")
            return None
        
        # Agrupar por mes y sentimiento
        df_temp['AñoMes'] = df_temp['FechaEstadia'].dt.to_period('M')
        evolucion = df_temp.groupby(['AñoMes', 'Sentimiento']).size().unstack(fill_value=0)
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for sentimiento in self.config.SENTIMIENTOS_VALIDOS:
            if sentimiento in evolucion.columns:
                ax.plot(evolucion.index.astype(str), evolucion[sentimiento], 
                       label=sentimiento, 
                       color=self.config.obtener_color_sentimiento(sentimiento),
                       marker='o', linewidth=2)
        
        ax.set_title(f'{titulo} - Evolución de Sentimientos por Mes', fontweight='bold', fontsize=14)
        ax.set_xlabel('Mes')
        ax.set_ylabel('Número de Opiniones')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas del eje x si hay muchas
        if len(evolucion.index) > 6:
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    
    def crear_heatmap_sentimientos_por_atraccion(self, df: pd.DataFrame, top_n: int = 10) -> plt.Figure:
        """
        Crea un heatmap de sentimientos por atracción.
        
        Args:
            df (pd.DataFrame): Dataset con columnas de sentimiento y atracción
            top_n (int): Número de atracciones top a mostrar
            
        Returns:
            plt.Figure: Figura con el heatmap
        """
        # Obtener las top N atracciones por número de reviews
        top_atracciones = df['Atraccion'].value_counts().head(top_n).index
        df_filtrado = df[df['Atraccion'].isin(top_atracciones)]
        
        # Crear tabla de contingencia
        tabla_contingencia = pd.crosstab(df_filtrado['Atraccion'], 
                                       df_filtrado['Sentimiento'], 
                                       normalize='index') * 100
        
        # Ordenar por sentimiento positivo
        tabla_contingencia = tabla_contingencia.sort_values('Positivo', ascending=False)
        
        # Crear heatmap
        fig, ax = plt.subplots(figsize=(10, max(6, len(tabla_contingencia) * 0.4)))
        
        sns.heatmap(tabla_contingencia, 
                   annot=True, 
                   fmt='.1f', 
                   cmap='RdYlGn',
                   ax=ax,
                   cbar_kws={'label': 'Porcentaje de Opiniones'})
        
        ax.set_title(f'Distribución Porcentual de Sentimientos por Atracción (Top {top_n})', 
                    fontweight='bold', fontsize=12)
        ax.set_xlabel('Sentimiento')
        ax.set_ylabel('Atracción')
        
        # Ajustar nombres de atracciones si son muy largos
        labels = [label.get_text()[:40] + '...' if len(label.get_text()) > 40 
                 else label.get_text() for label in ax.get_yticklabels()]
        ax.set_yticklabels(labels)
        
        plt.tight_layout()
        return fig
    
    def crear_visualizacion_comparacion_cardiff(self, df: pd.DataFrame, comparacion: Dict, columna_referencia: str = 'Sentimiento') -> plt.Figure:
        """
        Crea visualizaciones para comparar el modelo Cardiff NLP con otra clasificación.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            comparacion (Dict): Estadísticas de comparación
            columna_referencia (str): Columna de referencia ('Sentimiento' o 'SentimientoHF')
            
        Returns:
            plt.Figure: Figura con las visualizaciones
        """
        nombre_referencia = "Calificación" if columna_referencia == 'Sentimiento' else "HuggingFace"
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Comparación: {nombre_referencia} vs Cardiff NLP', 
                     fontsize=16, fontweight='bold')
        
        # 1. Distribución lado a lado
        sentimientos = ['Positivo', 'Neutro', 'Negativo']
        conteo_ref = [df[df[columna_referencia] == s].shape[0] for s in sentimientos]
        conteo_cardiff = [df[df['SentimientoCardiff'] == s].shape[0] for s in sentimientos]
        
        x = np.arange(len(sentimientos))
        width = 0.35
        
        axes[0,0].bar(x - width/2, conteo_ref, width, label=f'Por {nombre_referencia}', 
                      color=[self.config.obtener_color_sentimiento(s) for s in sentimientos], alpha=0.7)
        axes[0,0].bar(x + width/2, conteo_cardiff, width, label='Por Cardiff NLP',
                      color=[self.config.obtener_color_sentimiento(s) for s in sentimientos], alpha=0.4)
        
        axes[0,0].set_title('Distribución de Sentimientos por Método')
        axes[0,0].set_xlabel('Sentimiento')
        axes[0,0].set_ylabel('Número de Registros')
        axes[0,0].set_xticks(x)
        axes[0,0].set_xticklabels(sentimientos)
        axes[0,0].legend()
        
        # 2. Matriz de confusión como heatmap
        tabla_confusion_cardiff = pd.crosstab(df[columna_referencia], df['SentimientoCardiff'], 
                                            rownames=[nombre_referencia], colnames=['Cardiff NLP'])
        sns.heatmap(tabla_confusion_cardiff, annot=True, fmt='d', cmap='Blues', 
                    ax=axes[0,1], cbar_kws={'label': 'Número de Registros'})
        axes[0,1].set_title('Matriz de Confusión')
        axes[0,1].set_ylabel(f'Clasificación por {nombre_referencia}')
        axes[0,1].set_xlabel('Clasificación por Cardiff NLP')
        
        # 3. Concordancia por sentimiento
        concordancia_por_sent = []
        for sentimiento in sentimientos:
            df_sent = df[df[columna_referencia] == sentimiento]
            if len(df_sent) > 0:
                concordantes = len(df_sent[df_sent['SentimientoCardiff'] == sentimiento])
                porcentaje = (concordantes / len(df_sent)) * 100
                concordancia_por_sent.append(porcentaje)
            else:
                concordancia_por_sent.append(0)
        
        bars = axes[1,0].bar(sentimientos, concordancia_por_sent, 
                             color=[self.config.obtener_color_sentimiento(s) for s in sentimientos],
                             alpha=0.7, edgecolor='black', linewidth=1)
        axes[1,0].set_title('Concordancia por Tipo de Sentimiento')
        axes[1,0].set_xlabel('Sentimiento')
        axes[1,0].set_ylabel('Porcentaje de Concordancia (%)')
        axes[1,0].set_ylim(0, 100)
        
        # Agregar valores en las barras
        for bar, precision in zip(bars, concordancia_por_sent):
            axes[1,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           f'{precision:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 4. Concordancia general
        concordantes = len(df[df[columna_referencia] == df['SentimientoCardiff']])
        discordantes = len(df) - concordantes
        
        labels = ['Concordantes', 'Discordantes']
        sizes = [concordantes, discordantes]
        colors = ['#2ecc71', '#e74c3c']
        
        axes[1,1].pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
                      startangle=90, explode=(0.05, 0.05))
        axes[1,1].set_title('Concordancia General entre Métodos')
        
        plt.tight_layout()
        return fig
    
    def crear_visualizacion_comparacion_tres_modelos(self, df: pd.DataFrame) -> plt.Figure:
        """
        Crea visualizaciones para comparar los tres métodos: Calificación, HuggingFace y Cardiff.
        
        Args:
            df (pd.DataFrame): Dataset con las tres columnas de sentimiento
            
        Returns:
            plt.Figure: Figura con las visualizaciones
        """
        if 'SentimientoHF' not in df.columns or 'SentimientoCardiff' not in df.columns:
            print("❌ Error: Faltan columnas necesarias para comparar los tres modelos")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Comparación de Tres Métodos: Calificación vs HuggingFace vs Cardiff NLP', 
                     fontsize=16, fontweight='bold')
        
        # 1. Distribución lado a lado de los tres métodos
        sentimientos = ['Positivo', 'Neutro', 'Negativo']
        conteo_cal = [df[df['Sentimiento'] == s].shape[0] for s in sentimientos]
        conteo_hf = [df[df['SentimientoHF'] == s].shape[0] for s in sentimientos]
        conteo_cardiff = [df[df['SentimientoCardiff'] == s].shape[0] for s in sentimientos]
        
        x = np.arange(len(sentimientos))
        width = 0.25
        
        axes[0,0].bar(x - width, conteo_cal, width, label='Calificación', 
                      color=[self.config.obtener_color_sentimiento(s) for s in sentimientos], alpha=0.8)
        axes[0,0].bar(x, conteo_hf, width, label='HuggingFace',
                      color=[self.config.obtener_color_sentimiento(s) for s in sentimientos], alpha=0.6)
        axes[0,0].bar(x + width, conteo_cardiff, width, label='Cardiff NLP',
                      color=[self.config.obtener_color_sentimiento(s) for s in sentimientos], alpha=0.4)
        
        axes[0,0].set_title('Distribución de Sentimientos por Método')
        axes[0,0].set_xlabel('Sentimiento')
        axes[0,0].set_ylabel('Número de Registros')
        axes[0,0].set_xticks(x)
        axes[0,0].set_xticklabels(sentimientos)
        axes[0,0].legend()
        
        # 2. Concordancia entre cada par de métodos
        concordancia_cal_hf = len(df[df['Sentimiento'] == df['SentimientoHF']]) / len(df) * 100
        concordancia_cal_cardiff = len(df[df['Sentimiento'] == df['SentimientoCardiff']]) / len(df) * 100
        concordancia_hf_cardiff = len(df[df['SentimientoHF'] == df['SentimientoCardiff']]) / len(df) * 100
        
        comparaciones = ['Cal vs HF', 'Cal vs Cardiff', 'HF vs Cardiff']
        concordancias = [concordancia_cal_hf, concordancia_cal_cardiff, concordancia_hf_cardiff]
        
        bars = axes[0,1].bar(comparaciones, concordancias, 
                            color=['#3498db', '#e67e22', '#9b59b6'], alpha=0.7)
        axes[0,1].set_title('Concordancia entre Pares de Métodos')
        axes[0,1].set_ylabel('Porcentaje de Concordancia (%)')
        axes[0,1].set_ylim(0, 100)
        
        for bar, concordancia in zip(bars, concordancias):
            axes[0,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           f'{concordancia:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 3. Concordancia perfecta entre los tres métodos
        concordancia_total = len(df[(df['Sentimiento'] == df['SentimientoHF']) & 
                                   (df['Sentimiento'] == df['SentimientoCardiff'])]) / len(df) * 100
        
        labels = ['Los 3 concordantes', 'Al menos 1 discordante']
        sizes = [concordancia_total, 100 - concordancia_total]
        colors = ['#27ae60', '#e74c3c']
        
        axes[1,0].pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
                      startangle=90, explode=(0.05, 0.05))
        axes[1,0].set_title('Concordancia entre los Tres Métodos')
        
        # 4. Heatmap de concordancia por sentimiento
        concordancia_matriz = np.zeros((len(sentimientos), 3))
        
        for i, sentimiento in enumerate(sentimientos):
            df_sent = df[df['Sentimiento'] == sentimiento]
            if len(df_sent) > 0:
                concordancia_matriz[i, 0] = len(df_sent[df_sent['SentimientoHF'] == sentimiento]) / len(df_sent) * 100
                concordancia_matriz[i, 1] = len(df_sent[df_sent['SentimientoCardiff'] == sentimiento]) / len(df_sent) * 100
                concordancia_matriz[i, 2] = len(df_sent[(df_sent['SentimientoHF'] == sentimiento) & 
                                                       (df_sent['SentimientoCardiff'] == sentimiento)]) / len(df_sent) * 100
        
        im = axes[1,1].imshow(concordancia_matriz, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        axes[1,1].set_xticks(range(3))
        axes[1,1].set_xticklabels(['HF vs Cal', 'Cardiff vs Cal', 'HF & Cardiff vs Cal'])
        axes[1,1].set_yticks(range(len(sentimientos)))
        axes[1,1].set_yticklabels(sentimientos)
        axes[1,1].set_title('Concordancia por Sentimiento (%)')
        
        # Agregar valores en el heatmap
        for i in range(len(sentimientos)):
            for j in range(3):
                axes[1,1].text(j, i, f'{concordancia_matriz[i, j]:.1f}%',
                              ha='center', va='center', fontweight='bold')
        
        plt.colorbar(im, ax=axes[1,1], label='Porcentaje de Concordancia')
        plt.tight_layout()
        return fig
