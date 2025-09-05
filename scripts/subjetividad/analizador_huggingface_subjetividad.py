"""
Analizador de Subjetividad usando HuggingFace
===========================================

Este módulo contiene la lógica para el análisis de subjetividad usando modelos 
preentrenados de HuggingFace Transformers.

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


class AnalizadorHuggingFaceSubjetividad:
    """
    Clase para análisis de subjetividad usando modelos preentrenados de HuggingFace.
    
    Esta clase utiliza modelos de transformers para clasificar texto en:
    - Subjetivo: Opiniones, emociones, evaluaciones personales
    - Objetivo: Hechos, información factual
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
            print(f"🤖 Cargando modelo de subjetividad: {self.modelo_nombre}")
            print("⏳ Esto puede tomar unos momentos la primera vez...")
            
            self.pipeline = pipeline(
                "text-classification",
                model=self.modelo_nombre,
                return_all_scores=True
            )
            
            self.modelo_cargado = True
            print("✅ Modelo cargado exitosamente")
            print(f"🌍 Modelo: {self.modelo_nombre}")
            print("📋 Especializado en: Análisis de subjetividad multilingüe")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {e}")
            print("💡 Verificando modelo alternativo...")
            
            try:
                # Modelo alternativo más simple
                self.pipeline = pipeline("text-classification", return_all_scores=True)
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
            str: Categoría mapeada ('Subjetivo', 'Objetivo')
        """
        if not resultado:
            return "Objetivo"  # Por defecto objetivo si no hay resultado
        
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
        if any(subj in label_lower for subj in ['subject', 'subj', 'opinion', 'personal']):
            return "Subjetivo"
        elif any(obj in label_lower for obj in ['object', 'obj', 'fact', 'neutral']):
            return "Objetivo"
        else:
            # Si no reconocemos el patrón, usar la probabilidad más alta como criterio
            if mejor_score > 0.6:
                return "Subjetivo"  # Asumir subjetivo para scores altos no reconocidos
            else:
                return "Objetivo"
    
    def analizar_subjetividad_texto(self, texto: str) -> Dict:
        """
        Analiza la subjetividad de un texto usando el modelo preentrenado.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            Dict: Información completa del análisis incluyendo categoría y probabilidades
        """
        if not self.modelo_cargado:
            print("❌ Error: El modelo no ha sido cargado")
            return {"categoria": "Objetivo", "probabilidades": [], "texto_original": texto}
        
        if pd.isna(texto) or str(texto).strip() == "":
            return {"categoria": "Objetivo", "probabilidades": [], "texto_original": texto}
        
        try:
            # Limitar el texto a 512 caracteres para evitar problemas de memoria
            texto_procesado = str(texto)[:512]
            resultado = self.pipeline(texto_procesado)
            
            categoria = self.mapear_resultado_huggingface(resultado)
            
            return {
                "categoria": categoria,
                "probabilidades": resultado[0] if resultado else [],
                "texto_original": texto,
                "texto_procesado": texto_procesado
            }
            
        except Exception as e:
            print(f"⚠️ Error al procesar texto: {e}")
            return {"categoria": "Objetivo", "probabilidades": [], "texto_original": texto}
    
    def procesar_dataset_completo(self, df: pd.DataFrame, columna_texto: str = 'TituloReview') -> pd.DataFrame:
        """
        Procesa un dataset completo aplicando análisis de subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset a procesar
            columna_texto (str): Nombre de la columna con el texto a analizar
            
        Returns:
            pd.DataFrame: Dataset con nueva columna 'SubjetividadHF'
        """
        if not self.modelo_cargado:
            print("❌ Error: El modelo no ha sido cargado")
            return df
        
        print("🚀 Iniciando análisis de subjetividad en dataset completo...")
        print(f"📊 Total de registros a procesar: {len(df)}")
        
        df_resultado = df.copy()
        categorias = []
        
        # Procesar en lotes para mostrar progreso
        batch_size = 50
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        for i in range(0, len(df), batch_size):
            batch_end = min(i + batch_size, len(df))
            batch_num = (i // batch_size) + 1
            
            print(f"📦 Procesando lote {batch_num}/{total_batches} (registros {i+1}-{batch_end})")
            
            batch_categorias = []
            for idx in range(i, batch_end):
                texto = df.iloc[idx][columna_texto]
                resultado = self.analizar_subjetividad_texto(texto)
                batch_categorias.append(resultado["categoria"])
            
            categorias.extend(batch_categorias)
        
        df_resultado['SubjetividadHF'] = categorias
        
        print("✅ Análisis de subjetividad completado")
        print(f"📈 Nueva columna agregada: 'SubjetividadHF'")
        
        return df_resultado
    
    def obtener_estadisticas_subjetividad(self, df: pd.DataFrame) -> Dict:
        """
        Genera estadísticas descriptivas de la subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'SubjetividadHF'
        
        Returns:
            Dict: Diccionario con estadísticas de subjetividad
        """
        if 'SubjetividadHF' not in df.columns:
            print("❌ Error: El dataset no tiene la columna 'SubjetividadHF'")
            return {}
        
        conteo_subjetividad = df['SubjetividadHF'].value_counts()
        porcentajes = df['SubjetividadHF'].value_counts(normalize=True) * 100
        
        estadisticas = {
            'conteo': conteo_subjetividad,
            'porcentajes': porcentajes,
            'total': len(df),
            'por_atraccion': df.groupby('Atraccion')['SubjetividadHF'].value_counts().unstack(fill_value=0)
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
        
        # Mostrar descripción de cada categoría
        print(f"\n📝 DESCRIPCIÓN DE CATEGORÍAS:")
        print("-" * 40)
        for categoria in ['Subjetivo', 'Objetivo']:
            descripcion = self.config.obtener_descripcion_categoria(categoria)
            print(f"{categoria:>10}: {descripcion}")
    
    def mostrar_ejemplos_categoria(self, df: pd.DataFrame, categoria: str, 
                                 n_ejemplos: int = 3, mostrar_texto_completo: bool = True) -> None:
        """
        Muestra ejemplos representativos de una categoría específica.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'SubjetividadHF'
            categoria (str): Categoría a mostrar ('Subjetivo', 'Objetivo')
            n_ejemplos (int): Número de ejemplos a mostrar
            mostrar_texto_completo (bool): Si mostrar el texto completo sin cortes
        """
        ejemplos_disponibles = df[df['SubjetividadHF'] == categoria]
        n_mostrar = min(n_ejemplos, len(ejemplos_disponibles))
        
        print(f"\n🎯 EJEMPLOS DE TEXTO {categoria.upper()}")
        print("-" * 70)
        
        if n_mostrar == 0:
            print(f"   ❌ No se encontraron ejemplos de categoría {categoria}")
            return
        
        ejemplos = ejemplos_disponibles.sample(n=n_mostrar)
        
        for i, (idx, row) in enumerate(ejemplos.iterrows(), 1):
            print(f"\n📌 Ejemplo {i}:")
            print(f"   🏛️ Atracción: {row['Atraccion']}")
            print(f"   ⭐ Calificación: {row['Calificacion']} estrellas")
            print(f"   📝 Texto completo:")
            if mostrar_texto_completo:
                # Mostrar el texto completo sin cortes
                texto_completo = str(row['TituloReview'])
                print(f"      \"{texto_completo}\"")
            else:
                # Versión con corte para textos muy largos
                texto = str(row['TituloReview'])
                texto_mostrar = texto if len(texto) <= 200 else texto[:200] + "..."
                print(f"      \"{texto_mostrar}\"")
            print(f"   🏷️ Categoría: {categoria}")
    
    def mostrar_todos_los_ejemplos(self, df: pd.DataFrame, n_ejemplos: int = 3) -> None:
        """
        Muestra ejemplos de todas las categorías de subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset con columna 'SubjetividadHF'
            n_ejemplos (int): Número de ejemplos por categoría
        """
        print("🔍 EJEMPLOS REPRESENTATIVOS POR CATEGORÍA DE SUBJETIVIDAD")
        print("=" * 70)
        
        for categoria in self.config.CATEGORIAS_VALIDAS:
            self.mostrar_ejemplos_categoria(df, categoria, n_ejemplos, mostrar_texto_completo=True)
    
    def generar_resumen_final(self, df: pd.DataFrame) -> None:
        """
        Genera un resumen final del análisis de subjetividad.
        
        Args:
            df (pd.DataFrame): Dataset analizado
        """
        estadisticas = self.obtener_estadisticas_subjetividad(df)
        
        print("\n" + "🏆" * 25 + " RESUMEN FINAL " + "🏆" * 25)
        print("=" * 70)
        print(f"✅ Análisis de subjetividad completado exitosamente")
        print(f"🏙️ Ciudad analizada: {df['Ciudad'].iloc[0]}")
        print(f"📊 Total de opiniones analizadas: {len(df)}")
        print(f"🎯 Atracciones únicas: {df['Atraccion'].nunique()}")
        print(f"🤖 Modelo utilizado: {self.modelo_nombre}")
        
        if estadisticas:
            self.mostrar_estadisticas_consola(estadisticas)
        
        print("=" * 70)
