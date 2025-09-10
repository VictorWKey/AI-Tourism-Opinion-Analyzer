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
            self.pipeline = pipeline(
                "text-classification",
                model=self.modelo_nombre,
                return_all_scores=True
            )
            
            self.modelo_cargado = True
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {e}")
            
            try:
                # Modelo alternativo más simple
                self.pipeline = pipeline("text-classification", return_all_scores=True)
                self.modelo_cargado = True
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
            categoria_mapeada = self.config.MAPEO_ETIQUETAS_HF[mejor_label]
            return categoria_mapeada
        
        # Mapeo de respaldo basado en patrones si no se encuentra mapeo directo
        label_lower = mejor_label.lower()
        if any(subj in label_lower for subj in ['subject', 'subj', 'opinion', 'personal', 'label_1']):
            return "Subjetivo"
        elif any(obj in label_lower for obj in ['object', 'obj', 'fact', 'neutral', 'label_0']):
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
            return df
        
        df_resultado = df.copy()
        categorias = []
        
        # Procesar en lotes
        batch_size = 50
        
        for i in range(0, len(df), batch_size):
            batch_end = min(i + batch_size, len(df))
            
            batch_categorias = []
            for idx in range(i, batch_end):
                texto = df.iloc[idx][columna_texto]
                resultado = self.analizar_subjetividad_texto(texto)
                batch_categorias.append(resultado["categoria"])
            
            categorias.extend(batch_categorias)
        
        df_resultado['SubjetividadHF'] = categorias
        
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
    
    def analizar_subjetividad_por_sentimientos(self, df: pd.DataFrame) -> Dict:
        """
        Analiza la relación entre subjetividad y sentimientos.
        
        Args:
            df (pd.DataFrame): Dataset con columnas 'SubjetividadHF' y 'SentimientoHF'
            
        Returns:
            Dict: Estadísticas de la relación entre subjetividad y sentimientos
        """
        if 'SentimientoHF' not in df.columns:
            print("❌ Error: No se encontró la columna 'SentimientoHF'")
            return {}
        
        # Crear tabla cruzada
        tabla_cruzada = pd.crosstab(df['SubjetividadHF'], df['SentimientoHF'], margins=True)
        tabla_porcentual = pd.crosstab(df['SubjetividadHF'], df['SentimientoHF'], normalize='index') * 100
        
        # Calcular estadísticas específicas
        subjetivos = df[df['SubjetividadHF'] == 'Subjetivo']
        objetivos = df[df['SubjetividadHF'] == 'Objetivo']
        
        estadisticas = {
            'tabla_cruzada': tabla_cruzada,
            'tabla_porcentual': tabla_porcentual,
            'total_registros': len(df),
            'subjetivos_total': len(subjetivos),
            'objetivos_total': len(objetivos),
            'subjetivos_sentimientos': subjetivos['SentimientoHF'].value_counts(),
            'objetivos_sentimientos': objetivos['SentimientoHF'].value_counts(),
        }
        
        # Calcular calificaciones promedio si están disponibles
        if 'Calificacion' in df.columns:
            estadisticas['calificacion_promedio_por_combinacion'] = df.groupby(['SubjetividadHF', 'SentimientoHF'])['Calificacion'].mean()
        
        return estadisticas
    
    def mostrar_estadisticas_subjetividad_sentimientos(self, estadisticas: Dict) -> None:
        """
        Muestra las estadísticas de la relación entre subjetividad y sentimientos.
        
        Args:
            estadisticas (Dict): Estadísticas calculadas
        """
        print("\n📊 ANÁLISIS DE SUBJETIVIDAD vs SENTIMIENTOS")
        print("=" * 60)
        
        print(f"📈 Total de registros analizados: {estadisticas['total_registros']}")
        print(f"📝 Texto subjetivo: {estadisticas['subjetivos_total']} ({estadisticas['subjetivos_total']/estadisticas['total_registros']*100:.1f}%)")
        print(f"📋 Texto objetivo: {estadisticas['objetivos_total']} ({estadisticas['objetivos_total']/estadisticas['total_registros']*100:.1f}%)")
        
        print(f"\n📋 TABLA CRUZADA COMPLETA:")
        print("-" * 40)
        print(estadisticas['tabla_cruzada'])
        
        print(f"\n📊 DISTRIBUCIÓN PORCENTUAL POR SUBJETIVIDAD:")
        print("-" * 50)
        print(estadisticas['tabla_porcentual'].round(1))
        
        print(f"\n🔍 SENTIMIENTOS EN TEXTO SUBJETIVO:")
        print("-" * 40)
        for sentimiento, cantidad in estadisticas['subjetivos_sentimientos'].items():
            porcentaje = (cantidad / estadisticas['subjetivos_total']) * 100
            print(f"   • {sentimiento}: {cantidad} ({porcentaje:.1f}%)")
        
        print(f"\n🔍 SENTIMIENTOS EN TEXTO OBJETIVO:")
        print("-" * 40)
        for sentimiento, cantidad in estadisticas['objetivos_sentimientos'].items():
            porcentaje = (cantidad / estadisticas['objetivos_total']) * 100
            print(f"   • {sentimiento}: {cantidad} ({porcentaje:.1f}%)")
        
        if 'calificacion_promedio_por_combinacion' in estadisticas:
            print(f"\n⭐ CALIFICACIONES PROMEDIO POR COMBINACIÓN:")
            print("-" * 50)
            for (subjetividad, sentimiento), calificacion in estadisticas['calificacion_promedio_por_combinacion'].items():
                print(f"   • {subjetividad} + {sentimiento}: {calificacion:.1f} estrellas")
        
        # Insights automáticos
        print(f"\n💡 INSIGHTS PRINCIPALES:")
        print("-" * 30)
        
        # Determinar el sentimiento dominante en texto subjetivo
        if len(estadisticas['subjetivos_sentimientos']) > 0:
            sentimiento_dominante_subj = estadisticas['subjetivos_sentimientos'].index[0]
            porcentaje_dominante_subj = (estadisticas['subjetivos_sentimientos'].iloc[0] / estadisticas['subjetivos_total']) * 100
            print(f"• El {porcentaje_dominante_subj:.1f}% del texto subjetivo es {sentimiento_dominante_subj}")
        
        # Determinar el sentimiento dominante en texto objetivo
        if len(estadisticas['objetivos_sentimientos']) > 0:
            sentimiento_dominante_obj = estadisticas['objetivos_sentimientos'].index[0]
            porcentaje_dominante_obj = (estadisticas['objetivos_sentimientos'].iloc[0] / estadisticas['objetivos_total']) * 100
            print(f"• El {porcentaje_dominante_obj:.1f}% del texto objetivo es {sentimiento_dominante_obj}")
        
        # Calcular correlación general
        if 'subjetivos_sentimientos' in estadisticas and 'objetivos_sentimientos' in estadisticas:
            if 'Positivo' in estadisticas['subjetivos_sentimientos'] and 'Positivo' in estadisticas['objetivos_sentimientos']:
                pos_subj = estadisticas['subjetivos_sentimientos'].get('Positivo', 0) / estadisticas['subjetivos_total'] * 100
                pos_obj = estadisticas['objetivos_sentimientos'].get('Positivo', 0) / estadisticas['objetivos_total'] * 100
                if pos_subj > pos_obj:
                    print(f"• El texto subjetivo tiende a ser más positivo ({pos_subj:.1f}% vs {pos_obj:.1f}%)")
                elif pos_obj > pos_subj:
                    print(f"• El texto objetivo tiende a ser más positivo ({pos_obj:.1f}% vs {pos_subj:.1f}%)")
