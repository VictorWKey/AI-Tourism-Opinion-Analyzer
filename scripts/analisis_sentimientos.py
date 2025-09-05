"""
Módulo de Análisis de Sentimientos
==================================

Este módulo contiene la lógica para el análisis de sentimientos basado en calificaciones
de estrellas (1-5) para opiniones turísticas.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Importaciones para modelos preentrenados (se importarán cuando se necesiten)
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class AnalizadorSentimientos:
    """
    Clase para realizar análisis de sentimientos basado en calificaciones de estrellas.
    
    Esta clase mapea calificaciones de 1-5 estrellas a categorías de sentimiento:
    - 4-5 estrellas → Positivo
    - 3 estrellas → Neutro  
    - 1-2 estrellas → Negativo
    """
    
    def __init__(self):
        """Inicializa el analizador con la configuración de colores para visualizaciones."""
        self.colores_sentimientos = {
            'Positivo': '#2ecc71',   # Verde
            'Neutro': '#f39c12',     # Naranja
            'Negativo': '#e74c3c'    # Rojo
        }
        
        self.mapeo_calificaciones = {
            1: "Negativo",
            2: "Negativo", 
            3: "Neutro",
            4: "Positivo",
            5: "Positivo"
        }
    
    def mapear_calificacion_a_sentimiento(self, calificacion: float) -> str:
        """
        Mapea una calificación de estrellas (1-5) a una categoría de sentimiento.
        
        Args:
            calificacion (float): Calificación de 1 a 5 estrellas
        
        Returns:
            str: Sentimiento mapeado ('Positivo', 'Neutro', 'Negativo')
        """
        if pd.isna(calificacion):
            return "Neutro"
        
        if calificacion >= 4:
            return "Positivo"
        elif calificacion == 3:
            return "Neutro"
        else:  # calificacion <= 2
            return "Negativo"
    
    def procesar_sentimientos_dataset(self, df: pd.DataFrame, columna_calificacion: str = 'Calificacion') -> pd.DataFrame:
        """
        Procesa un dataset completo agregando la columna de sentimientos.
        
        Args:
            df (pd.DataFrame): Dataset a procesar
            columna_calificacion (str): Nombre de la columna con las calificaciones
        
        Returns:
            pd.DataFrame: Dataset con la nueva columna 'Sentimiento'
        """
        print("🔄 Creando columna 'Sentimiento' basada en las calificaciones...")
        
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
        
        print("✅ Columna 'Sentimiento' creada exitosamente")
        print(f"📊 Total de registros procesados: {len(df_result)}")
        
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
    
    def crear_visualizaciones(self, df: pd.DataFrame, titulo_ciudad: str = "Cancún") -> plt.Figure:
        """
        Crea visualizaciones completas de los sentimientos.
        
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
        colores = [self.colores_sentimientos.get(sent, '#95a5a6') for sent in conteo.index]
        
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
                               color=[self.colores_sentimientos.get(col, '#95a5a6') 
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
                          color=self.colores_sentimientos['Positivo'], alpha=0.8)
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


def cargar_dataset_ciudad(ruta_dataset: str) -> pd.DataFrame:
    """
    Función auxiliar para cargar un dataset de ciudad.
    
    Args:
        ruta_dataset (str): Ruta al archivo CSV del dataset
    
    Returns:
        pd.DataFrame: Dataset cargado
    
    Raises:
        FileNotFoundError: Si no se encuentra el archivo
        Exception: Para otros errores de carga
    """
    try:
        df = pd.read_csv(ruta_dataset)
        print(f"✅ Dataset cargado exitosamente")
        print(f"📊 Dimensiones del dataset: {df.shape}")
        print(f"🏙️ Ciudad: {df['Ciudad'].iloc[0]}")
        return df
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo del dataset")
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        raise


def mostrar_info_dataset(df: pd.DataFrame) -> None:
    """
    Muestra información detallada del dataset cargado.
    
    Args:
        df (pd.DataFrame): Dataset a analizar
    """
    print("\n" + "=" * 50)
    print("INFORMACIÓN GENERAL DEL DATASET")
    print("=" * 50)
    print(df.info())
    
    print("\n" + "=" * 50)
    print("DISTRIBUCIÓN DE CALIFICACIONES")
    print("=" * 50)
    print(df['Calificacion'].value_counts().sort_index())
    
    print("\n" + "=" * 50)
    print("PRIMERAS 3 FILAS DEL DATASET")
    print("=" * 50)
    return df.head(3)


class AnalizadorSentimientosHuggingFace:
    """
    Clase para análisis de sentimientos usando modelos preentrenados de HuggingFace.
    
    Esta clase utiliza modelos de transformers para clasificar texto en sentimientos
    y permite comparar los resultados con clasificaciones basadas en calificaciones.
    """
    
    def __init__(self, modelo_nombre: str = "nlptown/bert-base-multilingual-uncased-sentiment"):
        """
        Inicializa el analizador con un modelo preentrenado de HuggingFace.
        
        Args:
            modelo_nombre (str): Nombre del modelo preentrenado a usar
        """
        self.modelo_nombre = modelo_nombre
        self.pipeline = None
        self.modelo_cargado = False
        
        # Mapeo de etiquetas comunes a nuestras categorías
        self.mapeo_etiquetas = {
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
        
        self.colores_sentimientos = {
            'Positivo': '#2ecc71',   # Verde
            'Neutro': '#f39c12',     # Naranja
            'Negativo': '#e74c3c'    # Rojo
        }
    
    def cargar_modelo(self) -> bool:
        """
        Carga el modelo preentrenado de HuggingFace.
        
        Returns:
            bool: True si el modelo se cargó exitosamente, False en caso contrario
        """
        if not TRANSFORMERS_AVAILABLE:
            print("❌ Error: La librería transformers no está disponible")
            print("💡 Instala con: pip install transformers torch")
            return False
        
        try:
            print(f"🤖 Cargando modelo: {self.modelo_nombre}")
            print("⏳ Esto puede tomar unos momentos la primera vez...")
            
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.modelo_nombre,
                return_all_scores=True
            )
            
            self.modelo_cargado = True
            print("✅ Modelo cargado exitosamente")
            print(f"🌍 Modelo: {self.modelo_nombre}")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {e}")
            print("💡 Intentando con modelo alternativo...")
            
            try:
                self.pipeline = pipeline("sentiment-analysis", return_all_scores=True)
                self.modelo_cargado = True
                print("✅ Modelo alternativo cargado exitosamente")
                return True
            except Exception as e2:
                print(f"❌ Error crítico: {e2}")
                return False
    
    def mapear_resultado_huggingface(self, resultado: List[Dict]) -> str:
        """
        Mapea el resultado de HuggingFace a nuestras categorías estándar.
        
        Args:
            resultado (List[Dict]): Resultado del modelo de HuggingFace
            
        Returns:
            str: Sentimiento mapeado ('Positivo', 'Neutro', 'Negativo')
        """
        if not resultado:
            return "Neutro"
        
        # Si el resultado es una lista de scores (estructura anidada)
        if isinstance(resultado[0], list):
            scores_list = resultado[0]
        else:
            scores_list = resultado
        
        # Encontrar la etiqueta con mayor probabilidad
        mejor_prediccion = max(scores_list, key=lambda x: x['score'])
        mejor_label = mejor_prediccion['label']
        mejor_score = mejor_prediccion['score']
        
        # Mapeo directo usando la etiqueta con mayor probabilidad
        if mejor_label in self.mapeo_etiquetas:
            return self.mapeo_etiquetas[mejor_label]
        
        # Mapeo de respaldo basado en patrones si no se encuentra mapeo directo
        label_lower = mejor_label.lower()
        if any(pos in label_lower for pos in ['positive', 'pos', '5', '4']):
            return "Positivo"
        elif any(neg in label_lower for neg in ['negative', 'neg', '1', '2']):
            return "Negativo"
        elif any(neu in label_lower for neu in ['neutral', 'neu', '3']):
            return "Neutro"
        else:
            # Si no reconocemos el patrón, usar la probabilidad más alta como criterio
            if mejor_score > 0.6:
                return "Positivo"  # Asumir positivo para scores altos no reconocidos
            else:
                return "Neutro"
    
    def analizar_sentimiento_texto(self, texto: str) -> str:
        """
        Analiza el sentimiento de un texto usando el modelo preentrenado.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            str: Sentimiento detectado ('Positivo', 'Neutro', 'Negativo')
        """
        if not self.modelo_cargado:
            print("❌ Error: El modelo no ha sido cargado")
            return "Neutro"
        
        if pd.isna(texto) or str(texto).strip() == "":
            return "Neutro"
        
        try:
            # Limitar el texto a 512 caracteres para evitar problemas de memoria
            texto_procesado = str(texto)[:512]
            resultado = self.pipeline(texto_procesado)
            return self.mapear_resultado_huggingface(resultado)
            
        except Exception as e:
            print(f"Error procesando texto: {str(texto)[:50]}... - {e}")
            return "Neutro"
    
    def procesar_dataset_completo(self, df: pd.DataFrame, columna_texto: str = 'TituloReview') -> pd.DataFrame:
        """
        Procesa todo el dataset para obtener sentimientos usando el modelo preentrenado.
        
        Args:
            df (pd.DataFrame): Dataset a procesar
            columna_texto (str): Nombre de la columna que contiene el texto
            
        Returns:
            pd.DataFrame: Dataset con nueva columna 'SentimientoHF'
        """
        if not self.modelo_cargado:
            print("❌ Error: El modelo no ha sido cargado")
            return df
        
        print(f"🔄 Procesando sentimientos con HuggingFace para {len(df)} registros...")
        print("⏳ Esto puede tomar varios minutos...")
        
        df_resultado = df.copy()
        sentimientos_hf = []
        
        for i, texto in enumerate(df[columna_texto]):
            if i % 25 == 0:  # Progreso cada 25 registros
                print(f"   Procesando registro {i+1}/{len(df)} ({((i+1)/len(df)*100):.1f}%)")
            
            sentimiento = self.analizar_sentimiento_texto(texto)
            sentimientos_hf.append(sentimiento)
        
        df_resultado['SentimientoHF'] = sentimientos_hf
        print("✅ Procesamiento con HuggingFace completado")
        
        return df_resultado
    
    def comparar_sentimientos(self, df: pd.DataFrame) -> Dict:
        """
        Compara los sentimientos obtenidos por calificación vs HuggingFace.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            
        Returns:
            Dict: Estadísticas de comparación
        """
        if 'Sentimiento' not in df.columns or 'SentimientoHF' not in df.columns:
            print("❌ Error: El dataset debe tener ambas columnas 'Sentimiento' y 'SentimientoHF'")
            return {}
        
        # Tabla de confusión
        tabla_confusion = pd.crosstab(
            df['Sentimiento'], 
            df['SentimientoHF'], 
            rownames=['Calificación'], 
            colnames=['HuggingFace'],
            margins=True
        )
        
        # Calcular concordancia
        concordancia = (df['Sentimiento'] == df['SentimientoHF']).sum()
        total = len(df)
        porcentaje_concordancia = (concordancia / total) * 100
        
        # Estadísticas por sentimiento
        estadisticas_por_sentimiento = {}
        for sentimiento in ['Positivo', 'Neutro', 'Negativo']:
            mask_calificacion = df['Sentimiento'] == sentimiento
            mask_hf = df['SentimientoHF'] == sentimiento
            mask_ambos = mask_calificacion & mask_hf
            
            if mask_calificacion.sum() > 0:
                precision = mask_ambos.sum() / mask_calificacion.sum() * 100
            else:
                precision = 0
                
            estadisticas_por_sentimiento[sentimiento] = {
                'calificacion': mask_calificacion.sum(),
                'huggingface': mask_hf.sum(),
                'concordancia': mask_ambos.sum(),
                'precision': precision
            }
        
        return {
            'tabla_confusion': tabla_confusion,
            'concordancia_total': concordancia,
            'total_registros': total,
            'porcentaje_concordancia': porcentaje_concordancia,
            'estadisticas_sentimiento': estadisticas_por_sentimiento
        }
    
    def mostrar_comparacion(self, comparacion: Dict):
        """
        Muestra las estadísticas de comparación en consola.
        
        Args:
            comparacion (Dict): Resultado de comparar_sentimientos()
        """
        print("📊 COMPARACIÓN DE MÉTODOS DE ANÁLISIS DE SENTIMIENTOS")
        print("=" * 70)
        
        print(f"🎯 CONCORDANCIA GENERAL:")
        print(f"   • Total de registros: {comparacion['total_registros']}")
        print(f"   • Registros concordantes: {comparacion['concordancia_total']}")
        print(f"   • Porcentaje de concordancia: {comparacion['porcentaje_concordancia']:.1f}%")
        
        print(f"\n📋 ESTADÍSTICAS POR SENTIMIENTO:")
        print("-" * 50)
        for sentimiento, stats in comparacion['estadisticas_sentimiento'].items():
            print(f"\n{sentimiento}:")
            print(f"   📊 Por calificación: {stats['calificacion']} registros")
            print(f"   🤖 Por HuggingFace: {stats['huggingface']} registros")
            print(f"   ✅ Concordancia: {stats['concordancia']} registros ({stats['precision']:.1f}%)")
    
    def crear_visualizacion_comparacion(self, df: pd.DataFrame, comparacion: Dict) -> plt.Figure:
        """
        Crea visualizaciones para comparar ambos métodos de análisis.
        
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
                      color=[self.colores_sentimientos[s] for s in sentimientos], alpha=0.7)
        axes[0,0].bar(x + width/2, conteo_hf, width, label='Por HuggingFace',
                      color=[self.colores_sentimientos[s] for s in sentimientos], alpha=0.4)
        
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
                             color=[self.colores_sentimientos[s] for s in sentimientos],
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
    
    def mostrar_ejemplos_discordantes(self, df: pd.DataFrame, n_ejemplos: int = 5):
        """
        Muestra ejemplos donde los dos métodos no concuerdan.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            n_ejemplos (int): Número de ejemplos a mostrar por tipo de discordancia
        """
        print("🔍 EJEMPLOS DE DISCORDANCIAS ENTRE MÉTODOS")
        print("=" * 70)
        
        # Encontrar discordancias
        discordantes = df[df['Sentimiento'] != df['SentimientoHF']].copy()
        
        if len(discordantes) == 0:
            print("✅ No se encontraron discordancias entre los métodos")
            return
        
        print(f"📊 Total de discordancias: {len(discordantes)}/{len(df)} ({len(discordantes)/len(df)*100:.1f}%)")
        
        # Agrupar por tipo de discordancia
        tipos_discordancia = discordantes.groupby(['Sentimiento', 'SentimientoHF']).size()
        
        for (sent_cal, sent_hf), count in tipos_discordancia.items():
            print(f"\n🎯 {sent_cal} (Calificación) → {sent_hf} (HuggingFace): {count} casos")
            print("-" * 60)
            
            ejemplos = discordantes[
                (discordantes['Sentimiento'] == sent_cal) & 
                (discordantes['SentimientoHF'] == sent_hf)
            ].sample(n=min(n_ejemplos, count))
            
            for i, (idx, row) in enumerate(ejemplos.iterrows(), 1):
                print(f"\n📌 Ejemplo {i}:")
                print(f"   🏛️ Atracción: {row['Atraccion']}")
                print(f"   ⭐ Calificación: {row['Calificacion']}/5 → {row['Sentimiento']}")
                print(f"   🤖 HuggingFace: {row['SentimientoHF']}")
                print(f"   💬 Opinión: \"{row['TituloReview']}\"")  # Texto completo sin cortar
                print("   " + "-" * 50)
    
    def mostrar_todas_discordancias(self, df: pd.DataFrame):
        """
        Muestra TODAS las opiniones discordantes completas organizadas por tipo.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
        """
        # Configurar pandas para mostrar texto completo
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_columns', None)
        
        print("📋 LISTADO COMPLETO DE TODAS LAS DISCORDANCIAS")
        print("=" * 80)
        
        # Encontrar discordancias
        discordantes = df[df['Sentimiento'] != df['SentimientoHF']].copy()
        
        if len(discordantes) == 0:
            print("✅ No se encontraron discordancias entre los métodos")
            return discordantes
        
        print(f"📊 Total de discordancias: {len(discordantes)}/{len(df)} ({len(discordantes)/len(df)*100:.1f}%)")
        
        # Agrupar por tipo de discordancia
        tipos_discordancia = discordantes.groupby(['Sentimiento', 'SentimientoHF']).size().sort_values(ascending=False)
        
        print(f"\n📈 Tipos de discordancia encontrados:")
        for (sent_cal, sent_hf), count in tipos_discordancia.items():
            porcentaje = (count / len(discordantes)) * 100
            print(f"   • {sent_cal} → {sent_hf}: {count} casos ({porcentaje:.1f}%)")
        
        print("\n" + "=" * 80)
        print("📄 LISTADO DETALLADO DE TODAS LAS DISCORDANCIAS")
        print("=" * 80)
        
        # Mostrar todas las discordancias organizadas por tipo
        contador_global = 1
        for (sent_cal, sent_hf), count in tipos_discordancia.items():
            print(f"\n🎯 TIPO: {sent_cal} (⭐Calificación) → {sent_hf} (🤖HuggingFace)")
            print(f"📊 Total en esta categoría: {count} casos")
            print("-" * 80)
            
            # Obtener todos los casos de este tipo
            casos = discordantes[
                (discordantes['Sentimiento'] == sent_cal) & 
                (discordantes['SentimientoHF'] == sent_hf)
            ].copy()
            
            # Ordenar por atracción para mejor organización
            casos = casos.sort_values('Atraccion')
            
            for idx, row in casos.iterrows():
                print(f"\n#{contador_global:03d} | {row['Atraccion']}")
                print(f"     ⭐ Calificación: {row['Calificacion']}/5 → {row['Sentimiento']}")
                print(f"     🤖 HuggingFace: {row['SentimientoHF']}")
                print(f"     💬 Opinión completa:")
                print(f"     \"{row['TituloReview']}\"")
                print("     " + "─" * 70)
                contador_global += 1
        
        print(f"\n✅ Análisis completo: {contador_global-1} discordancias mostradas")
        
        # Resetear configuración de pandas a valores por defecto
        pd.reset_option('display.max_colwidth')
        pd.reset_option('display.width') 
        pd.reset_option('display.max_columns')
        
        return discordantes
