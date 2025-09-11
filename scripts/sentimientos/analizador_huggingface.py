"""
Analizador de Sentimientos usando HuggingFace
===========================================

Este módulo contiene la lógica para el análisis de sentimientos usando modelos 
preentrenados de HuggingFace Transformers.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

from .base_sentimientos import ConfiguracionSentimientos

# Importaciones para modelos preentrenados (se importarán cuando se necesiten)
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class AnalizadorHuggingFace:
    """
    Clase para análisis de sentimientos usando modelos preentrenados de HuggingFace.
    
    Esta clase utiliza modelos de transformers para clasificar texto en sentimientos
    y permite comparar los resultados con clasificaciones basadas en calificaciones.
    """
    
    def __init__(self, modelo_nombre: Optional[str] = None):
        """
        Inicializa el analizador con un modelo preentrenado de HuggingFace.
        
        Args:
            modelo_nombre (str): Nombre del modelo preentrenado a usar
        """
        self.config = ConfiguracionSentimientos()
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
        if mejor_label in self.config.MAPEO_ETIQUETAS_HF:
            return self.config.MAPEO_ETIQUETAS_HF[mejor_label]
        
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
            pd.DataFrame: Dataset con nueva columna 'SentimientoPorHF'
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
        
        df_resultado['SentimientoPorHF'] = sentimientos_hf
        print("✅ Procesamiento con HuggingFace completado")
        
        return df_resultado
    
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
        discordantes = df[df['SentimientoPorCalificacion'] != df['SentimientoPorHF']].copy()
        
        if len(discordantes) == 0:
            print("✅ No se encontraron discordancias entre los métodos")
            return
        
        print(f"📊 Total de discordancias: {len(discordantes)}/{len(df)} ({len(discordantes)/len(df)*100:.1f}%)")
        
        # Agrupar por tipo de discordancia
        tipos_discordancia = discordantes.groupby(['SentimientoPorCalificacion', 'SentimientoPorHF']).size()
        
        for (sent_cal, sent_hf), count in tipos_discordancia.items():
            print(f"\n🎯 {sent_cal} (Calificación) → {sent_hf} (HuggingFace): {count} casos")
            print("-" * 60)
            
            ejemplos = discordantes[
                (discordantes['SentimientoPorCalificacion'] == sent_cal) & 
                (discordantes['SentimientoPorHF'] == sent_hf)
            ].sample(n=min(n_ejemplos, count))
            
            for i, (idx, row) in enumerate(ejemplos.iterrows(), 1):
                print(f"\n📌 Ejemplo {i}:")
                print(f"   🏛️ Atracción: {row['Atraccion']}")
                print(f"   ⭐ Calificación: {row['Calificacion']}/5 → {row['SentimientoPorCalificacion']}")
                print(f"   🤖 HuggingFace: {row['SentimientoPorHF']}")
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
        discordantes = df[df['SentimientoPorCalificacion'] != df['SentimientoPorHF']].copy()
        
        if len(discordantes) == 0:
            print("✅ No se encontraron discordancias entre los métodos")
            return discordantes
        
        print(f"📊 Total de discordancias: {len(discordantes)}/{len(df)} ({len(discordantes)/len(df)*100:.1f}%)")
        
        # Agrupar por tipo de discordancia
        tipos_discordancia = discordantes.groupby(['SentimientoPorCalificacion', 'SentimientoPorHF']).size().sort_values(ascending=False)
        
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
                (discordantes['SentimientoPorCalificacion'] == sent_cal) & 
                (discordantes['SentimientoPorHF'] == sent_hf)
            ].copy()
            
            # Ordenar por atracción para mejor organización
            casos = casos.sort_values('Atraccion')
            
            for idx, row in casos.iterrows():
                print(f"\n#{contador_global:03d} | {row['Atraccion']}")
                print(f"     ⭐ Calificación: {row['Calificacion']}/5 → {row['SentimientoPorCalificacion']}")
                print(f"     🤖 HuggingFace: {row['SentimientoPorHF']}")
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
