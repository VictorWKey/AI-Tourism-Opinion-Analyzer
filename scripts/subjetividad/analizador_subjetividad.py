"""
Analizador Principal de Subjetividad
===================================

Este módulo contiene la lógica principal para el análisis de subjetividad
usando modelos preentrenados de HuggingFace.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

from .base_subjetividad import ConfiguracionSubjetividad

# Importaciones para modelos preentrenados (se importarán cuando se necesiten)
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class AnalizadorSubjetividad:
    """
    Clase principal para análisis de subjetividad usando modelos preentrenados de HuggingFace.
    
    Esta clase utiliza modelos de transformers para clasificar texto en subjetivo u objetivo.
    """
    
    def __init__(self, modelo_nombre: Optional[str] = None):
        """
        Inicializa el analizador con un modelo preentrenado de HuggingFace.
        
        Args:
            modelo_nombre (str): Nombre del modelo preentrenado a usar
        """
        self.config = ConfiguracionSubjetividad()
        self.modelo_nombre = modelo_nombre or self.config.MODELO_HUGGINGFACE_DEFAULT
        self.pipeline = None
        self.modelo_cargado = False
    
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
                "text-classification",
                model=self.modelo_nombre,
                return_all_scores=True
            )
            
            self.modelo_cargado = True
            print("✅ Modelo cargado exitosamente")
            print(f"🌍 Modelo: {self.modelo_nombre}")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {e}")
            return False
    
    def mapear_resultado_huggingface(self, resultado: List[Dict]) -> str:
        """
        Mapea el resultado de HuggingFace a nuestras categorías estándar.
        
        Args:
            resultado (List[Dict]): Resultado del modelo de HuggingFace
            
        Returns:
            str: Subjetividad mapeada ('Subjetivo', 'Objetivo')
        """
        if not resultado:
            return "Objetivo"
        
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
        if mejor_label in self.config.MAPEO_ETIQUETAS_HF:
            return self.config.MAPEO_ETIQUETAS_HF[mejor_label]
        
        # Mapeo de respaldo basado en patrones si no se encuentra mapeo directo
        label_lower = mejor_label.lower()
        if any(subj in label_lower for subj in ['subjective', 'subj', 'opinion']):
            return "Subjetivo"
        elif any(obj in label_lower for obj in ['objective', 'obj', 'fact']):
            return "Objetivo"
        else:
            # Si no reconocemos el patrón, usar la probabilidad como criterio
            if mejor_score > 0.6:
                return "Subjetivo"  # Asumir subjetivo para scores altos no reconocidos
            else:
                return "Objetivo"
    
    def analizar_subjetividad_texto(self, texto: str) -> str:
        """
        Analiza la subjetividad de un texto usando el modelo preentrenado.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            str: Subjetividad detectada ('Subjetivo', 'Objetivo')
        """
        if not self.modelo_cargado:
            print("❌ Error: El modelo no ha sido cargado")
            return "Objetivo"
        
        if pd.isna(texto) or str(texto).strip() == "":
            return "Objetivo"
        
        try:
            # Limitar el texto a 512 caracteres para evitar problemas de memoria
            texto_procesado = str(texto)[:512]
            resultado = self.pipeline(texto_procesado)
            return self.mapear_resultado_huggingface(resultado)
        except Exception as e:
            print(f"⚠️ Error procesando texto: {e}")
            return "Objetivo"
    
    def procesar_dataset_completo(self, df: pd.DataFrame, columna_texto: str = 'TituloReview') -> pd.DataFrame:
        """
        Procesa un dataset completo analizando la subjetividad de todos los textos.
        
        Args:
            df (pd.DataFrame): Dataset a procesar
            columna_texto (str): Nombre de la columna con el texto
            
        Returns:
            pd.DataFrame: Dataset con nueva columna 'ClasificacionSubjetividadConHF'
        """
        if not self.modelo_cargado:
            print("❌ Error: Debe cargar el modelo primero usando cargar_modelo()")
            return df
        
        df_resultado = df.copy()
        total_textos = len(df_resultado)
        
        print(f"🔄 Procesando {total_textos} textos con modelo de subjetividad...")
        print("⏳ Este proceso puede tomar varios minutos...")
        
        # Procesar cada texto individualmente con barra de progreso
        subjetividades = []
        for i, texto in enumerate(df_resultado[columna_texto], 1):
            if i % 50 == 0 or i == total_textos:
                porcentaje = (i / total_textos) * 100
                print(f"   📊 Progreso: {i}/{total_textos} ({porcentaje:.1f}%)")
            
            subjetividad = self.analizar_subjetividad_texto(texto)
            subjetividades.append(subjetividad)
        
        df_resultado['ClasificacionSubjetividadConHF'] = subjetividades
        
        print("✅ Análisis de subjetividad completado")
        print(f"📊 Resultados:")
        conteo = df_resultado['ClasificacionSubjetividadConHF'].value_counts()
        for categoria, cantidad in conteo.items():
            porcentaje = (cantidad / total_textos) * 100
            print(f"   • {categoria}: {cantidad} ({porcentaje:.1f}%)")
        
        return df_resultado
    
    def obtener_estadisticas_subjetividad(self, df: pd.DataFrame) -> Dict:
        """
        Genera estadísticas descriptivas de la subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'ClasificacionSubjetividadConHF'
        
        Returns:
            Dict: Diccionario con estadísticas de subjetividad
        """
        if 'ClasificacionSubjetividadConHF' not in df.columns:
            print("❌ Error: El dataset debe tener la columna 'ClasificacionSubjetividadConHF'")
            return {}
        
        conteo_subjetividad = df['ClasificacionSubjetividadConHF'].value_counts()
        porcentajes = df['ClasificacionSubjetividadConHF'].value_counts(normalize=True) * 100
        
        estadisticas = {
            'conteo': conteo_subjetividad,
            'porcentajes': porcentajes,
            'total': len(df),
            'por_atraccion': df.groupby('Atraccion')['ClasificacionSubjetividadConHF'].value_counts().unstack(fill_value=0)
        }
        
        return estadisticas
    
    def mostrar_estadisticas_consola(self, estadisticas: Dict) -> None:
        """
        Muestra las estadísticas de subjetividad en la consola.
        
        Args:
            estadisticas (Dict): Estadísticas generadas por obtener_estadisticas_subjetividad
        """
        print("📊 ESTADÍSTICAS DESCRIPTIVAS DE SUBJETIVIDAD")
        print("=" * 60)
        
        conteo_subjetividad = estadisticas['conteo']
        porcentajes = estadisticas['porcentajes']
        
        print("🔢 DISTRIBUCIÓN DE SUBJETIVIDAD:")
        print("-" * 40)
        for categoria in ['Subjetivo', 'Objetivo']:
            if categoria in conteo_subjetividad.index:
                count = conteo_subjetividad[categoria]
                percent = porcentajes[categoria]
                print(f"{categoria:>10}: {count:>3} registros ({percent:>5.1f}%)")
            else:
                print(f"{categoria:>10}: {0:>3} registros ({0:>5.1f}%)")
        
        print(f"\n📈 TOTAL DE REGISTROS: {estadisticas['total']}")
    
    def mostrar_ejemplos_subjetividad(self, df: pd.DataFrame, categoria: str, 
                                     n_ejemplos: int = 3, mostrar_completo: bool = True) -> None:
        """
        Muestra ejemplos representativos de una categoría específica.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'ClasificacionSubjetividadConHF'
            categoria (str): Categoría a mostrar ('Subjetivo', 'Objetivo')
            n_ejemplos (int): Número de ejemplos a mostrar
            mostrar_completo (bool): Si mostrar el texto completo sin cortes
        """
        ejemplos_disponibles = df[df['ClasificacionSubjetividadConHF'] == categoria]
        n_mostrar = min(n_ejemplos, len(ejemplos_disponibles))
        
        print(f"\n🎯 EJEMPLOS DE CATEGORÍA {categoria.upper()}")
        print("-" * 80)
        
        if n_mostrar == 0:
            print(f"   ❌ No se encontraron ejemplos de categoría {categoria}")
            return
        
        ejemplos = ejemplos_disponibles.sample(n=n_mostrar)
        
        for i, (idx, row) in enumerate(ejemplos.iterrows(), 1):
            print(f"\n📌 Ejemplo {i}:")
            print(f"   🏛️ Atracción: {row['Atraccion']}")
            print(f"   ⭐ Calificación: {row['Calificacion']} estrellas")
            if mostrar_completo:
                # Mostrar texto completo sin cortes
                print(f"   💬 Opinión completa: {row['TituloReview']}")
            else:
                # Mostrar solo los primeros 100 caracteres
                texto_corto = row['TituloReview'][:100] + "..." if len(row['TituloReview']) > 100 else row['TituloReview']
                print(f"   💬 Opinión: {texto_corto}")
            print(f"   🎯 Subjetividad: {row['ClasificacionSubjetividadConHF']}")
    
    def mostrar_todos_los_ejemplos(self, df: pd.DataFrame, n_ejemplos: int = 5) -> None:
        """
        Muestra ejemplos de todas las categorías de subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'ClasificacionSubjetividadConHF'
            n_ejemplos (int): Número de ejemplos por categoría
        """
        categorias = ['Subjetivo', 'Objetivo']
        
        for categoria in categorias:
            self.mostrar_ejemplos_subjetividad(df, categoria, n_ejemplos, mostrar_completo=True)
    
    def generar_resumen_final(self, df: pd.DataFrame) -> None:
        """
        Genera un resumen final del análisis de subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset procesado
        """
        print("\n" + "🎯" * 30)
        print("RESUMEN FINAL DEL ANÁLISIS DE SUBJETIVIDAD")
        print("🎯" * 30)
        
        total = len(df)
        ciudad = df['Ciudad'].iloc[0] if 'Ciudad' in df.columns else 'No especificada'
        atracciones = df['Atraccion'].nunique() if 'Atraccion' in df.columns else 0
        
        print(f"🏙️ Ciudad analizada: {ciudad}")
        print(f"📊 Total de opiniones: {total}")
        print(f"🎪 Atracciones únicas: {atracciones}")
        
        if 'ClasificacionSubjetividadConHF' in df.columns:
            conteo = df['ClasificacionSubjetividadConHF'].value_counts()
            print(f"\n🔍 Distribución de subjetividad:")
            for categoria, cantidad in conteo.items():
                porcentaje = (cantidad / total) * 100
                print(f"   • {categoria}: {cantidad} opiniones ({porcentaje:.1f}%)")
        
        print(f"\n🤖 Modelo utilizado: {self.modelo_nombre}")
        print("✅ Análisis completado exitosamente")
