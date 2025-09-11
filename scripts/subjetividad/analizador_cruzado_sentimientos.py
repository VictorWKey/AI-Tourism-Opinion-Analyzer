"""
Análisis cruzado entre subjetividad y sentimientos.
Permite analizar la distribución de sentimientos para cada categoría de subjetividad.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Tuple


class AnalizadorCruzadoSentimientos:
    """Analiza la relación entre clasificaciones de subjetividad y sentimientos."""
    
    def __init__(self, df: pd.DataFrame, columna_sentimiento: str = 'SentimientoPorCardiff'):
        """
        Inicializa el analizador con el dataset.
        
        Args:
            df: DataFrame con columnas de subjetividad y sentimientos
            columna_sentimiento: Columna de sentimientos a usar ('SentimientoPorCardiff', 'SentimientoPorHF', 'SentimientoPorCalificacion')
        """
        self.df = df.copy()
        self.columna_sentimiento = columna_sentimiento
        self._validar_columna_sentimiento()
        self._normalizar_terminologia()
    
    def _validar_columna_sentimiento(self):
        """Valida que la columna de sentimiento especificada exista en el dataset."""
        columnas_disponibles = ['SentimientoPorCardiff', 'SentimientoPorHF', 'SentimientoPorCalificacion']
        
        if self.columna_sentimiento not in self.df.columns:
            raise ValueError(f"Columna {self.columna_sentimiento} no encontrada. Columnas disponibles: {columnas_disponibles}")
    
    def _normalizar_terminologia(self):
        """Normaliza la terminología femenina a masculina para LLM."""
        if 'SubjetividadConLLM' in self.df.columns:
            self.df['SubjetividadConLLM'] = self.df['SubjetividadConLLM'].str.replace(
                'Subjetiva', 'Subjetivo', regex=False
            ).str.replace(
                'Objetiva', 'Objetivo', regex=False
            )
    
    def analizar_metodo_subjetividad(self, metodo_subjetividad: str) -> Dict:
        """
        Analiza la distribución de sentimientos para un método de subjetividad específico.
        
        Args:
            metodo_subjetividad: Nombre de la columna del método de subjetividad
            
        Returns:
            Dict con resultados del análisis
        """
        if metodo_subjetividad not in self.df.columns:
            raise ValueError(f"Método {metodo_subjetividad} no encontrado en el dataset")
        
        # Crear tabla cruzada
        tabla_cruzada = pd.crosstab(
            self.df[metodo_subjetividad], 
            self.df[self.columna_sentimiento],
            margins=True
        )
        
        # Calcular porcentajes por fila (por cada categoría de subjetividad)
        tabla_porcentajes = pd.crosstab(
            self.df[metodo_subjetividad], 
            self.df[self.columna_sentimiento],
            normalize='index'
        ) * 100
        
        # Estadísticas generales
        total_opiniones = len(self.df)
        distribuciones = {}
        
        for categoria in self.df[metodo_subjetividad].unique():
            if pd.isna(categoria):
                continue
            subset = self.df[self.df[metodo_subjetividad] == categoria]
            distribuciones[categoria] = {
                'total': len(subset),
                'porcentaje_total': len(subset) / total_opiniones * 100,
                'sentimientos': subset[self.columna_sentimiento].value_counts().to_dict()
            }
        
        return {
            'metodo': metodo_subjetividad,
            'columna_sentimiento': self.columna_sentimiento,
            'tabla_cruzada': tabla_cruzada,
            'tabla_porcentajes': tabla_porcentajes,
            'distribuciones': distribuciones,
            'total_opiniones': total_opiniones
        }
    
    def visualizar_analisis(self, resultados: Dict, figsize: Tuple = (12, 8)):
        """
        Crea visualizaciones para el análisis cruzado.
        
        Args:
            resultados: Resultados del análisis de un método
            figsize: Tamaño de la figura
        """
        metodo = resultados['metodo']
        columna_sentimiento = resultados['columna_sentimiento']
        tabla_porcentajes = resultados['tabla_porcentajes']
        
        # Crear subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(f'Análisis Cruzado: {metodo} vs {columna_sentimiento}', 
                    fontsize=16, fontweight='bold')
        
        # 1. Gráfico de barras apiladas (valores absolutos)
        tabla_cruzada_sin_total = resultados['tabla_cruzada'].iloc[:-1, :-1]
        tabla_cruzada_sin_total.plot(kind='bar', ax=ax1, stacked=True)
        ax1.set_title('Distribución Absoluta por Categoría de Subjetividad')
        ax1.set_xlabel('Categoría de Subjetividad')
        ax1.set_ylabel('Número de Opiniones')
        ax1.legend(title='Sentimiento')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Gráfico de barras apiladas (porcentajes)
        tabla_porcentajes.plot(kind='bar', ax=ax2, stacked=True)
        ax2.set_title('Distribución Porcentual por Categoría de Subjetividad')
        ax2.set_xlabel('Categoría de Subjetividad')
        ax2.set_ylabel('Porcentaje (%)')
        ax2.legend(title='Sentimiento')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Heatmap de la tabla cruzada
        sns.heatmap(tabla_cruzada_sin_total, annot=True, fmt='d', ax=ax3, cmap='Blues')
        ax3.set_title('Matriz de Frecuencias')
        ax3.set_xlabel('Sentimiento')
        ax3.set_ylabel('Subjetividad')
        
        # 4. Gráfico de barras por sentimiento
        tabla_cruzada_sin_total.T.plot(kind='bar', ax=ax4)
        ax4.set_title('Distribución por Sentimiento')
        ax4.set_xlabel('Sentimiento')
        ax4.set_ylabel('Número de Opiniones')
        ax4.legend(title='Subjetividad', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def mostrar_resumen(self, resultados: Dict):
        """
        Muestra un resumen textual del análisis.
        
        Args:
            resultados: Resultados del análisis de un método
        """
        metodo = resultados['metodo']
        columna_sentimiento = resultados['columna_sentimiento']
        distribuciones = resultados['distribuciones']
        total = resultados['total_opiniones']
        
        print(f"\n📊 ANÁLISIS CRUZADO: {metodo} vs {columna_sentimiento}")
        print("=" * 60)
        
        for categoria, datos in distribuciones.items():
            print(f"\n🔹 {categoria}:")
            print(f"   Total: {datos['total']} opiniones ({datos['porcentaje_total']:.1f}%)")
            print(f"   Distribución por sentimiento:")
            
            for sentimiento, cantidad in datos['sentimientos'].items():
                porcentaje = cantidad / datos['total'] * 100
                print(f"     • {sentimiento}: {cantidad} ({porcentaje:.1f}%)")
    
    def obtener_ejemplos_por_categoria(self, metodo_subjetividad: str, n_ejemplos: int = 2) -> Dict:
        """
        Obtiene ejemplos específicos para cada combinación de subjetividad y sentimiento.
        
        Args:
            metodo_subjetividad: Nombre de la columna del método de subjetividad
            n_ejemplos: Número de ejemplos por categoría
            
        Returns:
            Dict con ejemplos organizados por categoría
        """
        if metodo_subjetividad not in self.df.columns:
            raise ValueError(f"Método {metodo_subjetividad} no encontrado en el dataset")
        
        ejemplos = {}
        categorias_subjetividad = self.df[metodo_subjetividad].unique()
        sentimientos = self.df[self.columna_sentimiento].unique()
        
        for categoria in categorias_subjetividad:
            if pd.isna(categoria):
                continue
            ejemplos[categoria] = {}
            
            for sentimiento in sentimientos:
                if pd.isna(sentimiento):
                    continue
                    
                # Filtrar por categoría y sentimiento
                filtro = (self.df[metodo_subjetividad] == categoria) & \
                        (self.df[self.columna_sentimiento] == sentimiento)
                subset = self.df[filtro]
                
                if len(subset) > 0:
                    # Seleccionar ejemplos aleatorios
                    ejemplos_seleccionados = subset.sample(
                        min(n_ejemplos, len(subset)), 
                        random_state=42
                    )
                    
                    ejemplos[categoria][sentimiento] = []
                    for _, row in ejemplos_seleccionados.iterrows():
                        ejemplos[categoria][sentimiento].append({
                            'titulo': row['Titulo'],
                            'review': row['Review'],
                            'ciudad': row['Ciudad'],
                            'atraccion': row['Atraccion']
                        })
                else:
                    ejemplos[categoria][sentimiento] = []
        
        return ejemplos
    
    def mostrar_ejemplos(self, ejemplos: Dict, metodo: str):
        """
        Muestra ejemplos de forma organizada y legible.
        
        Args:
            ejemplos: Dict con ejemplos por categoría
            metodo: Nombre del método de subjetividad
        """
        print(f"\n📝 EJEMPLOS POR CATEGORÍA - {metodo} vs {self.columna_sentimiento}")
        print("=" * 80)
        
        for categoria, sentimientos in ejemplos.items():
            print(f"\n🏷️  CATEGORÍA: {categoria}")
            print("-" * 50)
            
            for sentimiento, lista_ejemplos in sentimientos.items():
                if lista_ejemplos:
                    print(f"\n   💭 {sentimiento}:")
                    
                    for i, ejemplo in enumerate(lista_ejemplos, 1):
                        print(f"\n   📍 Ejemplo {i}:")
                        print(f"      🏨 {ejemplo['ciudad']} - {ejemplo['atraccion']}")
                        print(f"      📰 Título: {ejemplo['titulo']}")
                        print(f"      💬 Review: {ejemplo['review']}")
                        print()
    
    def comparar_metodos(self) -> Dict:
        """
        Compara los dos métodos de subjetividad ternaria disponibles.
        
        Returns:
            Dict con la comparación entre métodos
        """
        metodos = ['SubjetividadConFrases', 'SubjetividadConLLM']
        resultados_comparacion = {}
        
        for metodo in metodos:
            if metodo in self.df.columns:
                resultados_comparacion[metodo] = self.analizar_metodo_subjetividad(metodo)
        
        return resultados_comparacion
    
    def visualizar_comparacion_metodos(self, resultados_comparacion: Dict, figsize: Tuple = (15, 10)):
        """
        Visualiza la comparación entre los dos métodos de subjetividad.
        
        Args:
            resultados_comparacion: Resultados de la comparación
            figsize: Tamaño de la figura
        """
        n_metodos = len(resultados_comparacion)
        fig, axes = plt.subplots(2, n_metodos, figsize=figsize)
        fig.suptitle('Comparación de Métodos de Subjetividad vs Sentimiento', 
                    fontsize=16, fontweight='bold')
        
        for i, (metodo, resultados) in enumerate(resultados_comparacion.items()):
            tabla_cruzada = resultados['tabla_cruzada'].iloc[:-1, :-1]
            tabla_porcentajes = resultados['tabla_porcentajes']
            
            # Gráfico de valores absolutos
            tabla_cruzada.plot(kind='bar', ax=axes[0, i])
            axes[0, i].set_title(f'{metodo}\n(Valores Absolutos)')
            axes[0, i].set_xlabel('Subjetividad')
            axes[0, i].set_ylabel('Número de Opiniones')
            axes[0, i].tick_params(axis='x', rotation=45)
            axes[0, i].legend(title='Sentimiento')
            
            # Gráfico de porcentajes
            tabla_porcentajes.plot(kind='bar', ax=axes[1, i])
            axes[1, i].set_title(f'{metodo}\n(Porcentajes)')
            axes[1, i].set_xlabel('Subjetividad')
            axes[1, i].set_ylabel('Porcentaje (%)')
            axes[1, i].tick_params(axis='x', rotation=45)
            axes[1, i].legend(title='Sentimiento')
        
        plt.tight_layout()
        plt.show()


def realizar_analisis_cruzado_completo(df: pd.DataFrame, columna_sentimiento: str = 'SentimientoPorCardiff') -> Dict:
    """
    Realiza el análisis cruzado completo para ambos métodos de subjetividad.
    
    Args:
        df: DataFrame con los datos
        columna_sentimiento: Columna de sentimientos a usar
        
    Returns:
        Dict con todos los resultados
    """
    analizador = AnalizadorCruzadoSentimientos(df, columna_sentimiento)
    return analizador.comparar_metodos()


def generar_visualizaciones_cruzadas(df: pd.DataFrame, columna_sentimiento: str = 'SentimientoPorCardiff'):
    """
    Genera todas las visualizaciones del análisis cruzado.
    
    Args:
        df: DataFrame con los datos
        columna_sentimiento: Columna de sentimientos a usar
    """
    analizador = AnalizadorCruzadoSentimientos(df, columna_sentimiento)
    resultados_comparacion = analizador.comparar_metodos()
    
    # Análisis individual de cada método
    for metodo, resultados in resultados_comparacion.items():
        analizador.mostrar_resumen(resultados)
        analizador.visualizar_analisis(resultados)
    
    # Comparación visual entre métodos
    analizador.visualizar_comparacion_metodos(resultados_comparacion)
    
    return resultados_comparacion