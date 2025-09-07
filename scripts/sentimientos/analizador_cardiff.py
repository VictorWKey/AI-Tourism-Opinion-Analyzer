"""
Analizador de Sentimientos usando Cardiff NLP (Twitter XLM-RoBERTa)
===============================================================

Este módulo contiene la lógica para el análisis de sentimientos usando el modelo
preentrenado cardiffnlp/twitter-xlm-roberta-base-sentiment de HuggingFace.

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


class AnalizadorCardiff:
    """
    Clase para análisis de sentimientos usando el modelo Cardiff NLP Twitter XLM-RoBERTa.
    
    Este modelo está específicamente entrenado en datos de Twitter y es multilingüe,
    lo que lo hace ideal para texto corto y expresivo como las reseñas turísticas.
    """
    
    def __init__(self, modelo_nombre: Optional[str] = None):
        """
        Inicializa el analizador con el modelo Cardiff NLP.
        
        Args:
            modelo_nombre (str): Nombre del modelo preentrenado a usar
        """
        self.config = ConfiguracionSentimientos()
        self.modelo_nombre = modelo_nombre or "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        self.pipeline = None
        self.modelo_cargado = False
    
    def cargar_modelo(self) -> bool:
        """
        Carga el modelo preentrenado Cardiff NLP.
        
        Returns:
            bool: True si el modelo se cargó exitosamente, False en caso contrario
        """
        if not TRANSFORMERS_AVAILABLE:
            print("❌ Error: La librería transformers no está disponible")
            print("💡 Instala con: pip install transformers torch")
            return False
        
        try:
            print(f"🤖 Cargando modelo Cardiff NLP: {self.modelo_nombre}")
            print("⏳ Esto puede tomar unos momentos la primera vez...")
            
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.modelo_nombre,
                tokenizer=self.modelo_nombre
            )
            
            self.modelo_cargado = True
            print("✅ Modelo Cardiff NLP cargado exitosamente")
            print(f"🌍 Modelo: {self.modelo_nombre}")
            print("🐦 Optimizado para: Texto corto y expresivo (entrenado en Twitter)")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar el modelo Cardiff NLP: {e}")
            return False
    
    def mapear_resultado_cardiff(self, resultado: List[Dict]) -> str:
        """
        Mapea el resultado del modelo Cardiff NLP a nuestras categorías estándar.
        
        El modelo Cardiff NLP retorna etiquetas como 'Positive', 'Negative', 'Neutral'
        con scores de confianza.
        
        Args:
            resultado (List[Dict]): Resultado del modelo Cardiff NLP
            
        Returns:
            str: Sentimiento mapeado ('Positivo', 'Neutro', 'Negativo')
        """
        if not resultado:
            return "Neutro"
        
        # El modelo Cardiff NLP retorna un solo resultado con la predicción más probable
        prediccion = resultado[0]
        label = prediccion['label']
        score = prediccion['score']
        
        # Mapeo directo de las etiquetas del modelo Cardiff NLP
        mapeo_cardiff = {
            'Positive': 'Positivo',
            'Negative': 'Negativo',
            'Neutral': 'Neutro'
        }
        
        # Mapear la etiqueta a nuestro formato
        if label in mapeo_cardiff:
            return mapeo_cardiff[label]
        
        # Mapeo de respaldo basado en patrones
        label_lower = label.lower()
        if 'positive' in label_lower or 'pos' in label_lower:
            return "Positivo"
        elif 'negative' in label_lower or 'neg' in label_lower:
            return "Negativo"
        elif 'neutral' in label_lower or 'neu' in label_lower:
            return "Neutro"
        else:
            # Si no reconocemos la etiqueta, usar score como criterio
            if score > 0.6:
                return "Positivo"  # Asumir positivo para scores altos no reconocidos
            elif score > 0.4:
                return "Neutro"
            else:
                return "Negativo"
    
    def analizar_sentimiento_texto(self, texto: str) -> str:
        """
        Analiza el sentimiento de un texto usando el modelo Cardiff NLP.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            str: Sentimiento detectado ('Positivo', 'Neutro', 'Negativo')
        """
        if not self.modelo_cargado:
            print("❌ Error: El modelo Cardiff NLP no ha sido cargado")
            return "Neutro"
        
        if pd.isna(texto) or str(texto).strip() == "":
            return "Neutro"
        
        try:
            # Limitar el texto a 512 caracteres para evitar problemas de memoria
            texto_procesado = str(texto)[:512]
            resultado = self.pipeline(texto_procesado)
            return self.mapear_resultado_cardiff(resultado)
            
        except Exception as e:
            print(f"Error procesando texto: {str(texto)[:50]}... - {e}")
            return "Neutro"
    
    def procesar_dataset_completo(self, df: pd.DataFrame, columna_texto: str = 'TituloReview') -> pd.DataFrame:
        """
        Procesa todo el dataset para obtener sentimientos usando el modelo Cardiff NLP.
        
        Args:
            df (pd.DataFrame): Dataset a procesar
            columna_texto (str): Nombre de la columna que contiene el texto
            
        Returns:
            pd.DataFrame: Dataset con nueva columna 'SentimientoCardiff'
        """
        if not self.modelo_cargado:
            print("❌ Error: El modelo Cardiff NLP no ha sido cargado")
            return df
        
        print(f"🔄 Procesando sentimientos con Cardiff NLP para {len(df)} registros...")
        print("⏳ Esto puede tomar varios minutos...")
        
        df_resultado = df.copy()
        sentimientos_cardiff = []
        
        for i, texto in enumerate(df[columna_texto]):
            if i % 25 == 0:  # Progreso cada 25 registros
                print(f"   Procesando registro {i+1}/{len(df)} ({((i+1)/len(df)*100):.1f}%)")
            
            sentimiento = self.analizar_sentimiento_texto(texto)
            sentimientos_cardiff.append(sentimiento)
        
        df_resultado['SentimientoCardiff'] = sentimientos_cardiff
        print("✅ Procesamiento con Cardiff NLP completado")
        
        return df_resultado
    
    def mostrar_ejemplos_discordantes(self, df: pd.DataFrame, columna_referencia: str = 'Sentimiento', n_ejemplos: int = 5):
        """
        Muestra ejemplos donde el modelo Cardiff NLP no concuerda con otra clasificación.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            columna_referencia (str): Columna de referencia para comparar ('Sentimiento' o 'SentimientoHF')
            n_ejemplos (int): Número de ejemplos a mostrar por tipo de discordancia
        """
        print("🔍 EJEMPLOS DE DISCORDANCIAS: CARDIFF NLP vs", columna_referencia.upper())
        print("=" * 70)
        
        # Encontrar discordancias
        discordantes = df[df[columna_referencia] != df['SentimientoCardiff']].copy()
        
        if len(discordantes) == 0:
            print(f"✅ No se encontraron discordancias entre Cardiff NLP y {columna_referencia}")
            return
        
        print(f"📊 Total de discordancias: {len(discordantes)}/{len(df)} ({len(discordantes)/len(df)*100:.1f}%)")
        
        # Agrupar por tipo de discordancia
        tipos_discordancia = discordantes.groupby([columna_referencia, 'SentimientoCardiff']).size()
        
        for (sent_ref, sent_cardiff), count in tipos_discordancia.items():
            print(f"\n🎯 {sent_ref} ({columna_referencia}) → {sent_cardiff} (Cardiff): {count} casos")
            print("-" * 60)
            
            ejemplos = discordantes[
                (discordantes[columna_referencia] == sent_ref) & 
                (discordantes['SentimientoCardiff'] == sent_cardiff)
            ].sample(n=min(n_ejemplos, count))
            
            for i, (idx, row) in enumerate(ejemplos.iterrows(), 1):
                print(f"\n📌 Ejemplo {i}:")
                print(f"   🏛️ Atracción: {row['Atraccion']}")
                print(f"   ⭐ Calificación: {row['Calificacion']}/5")
                print(f"   🔄 {columna_referencia}: {row[columna_referencia]}")
                print(f"   🐦 Cardiff NLP: {row['SentimientoCardiff']}")
                print(f"   💬 Opinión: \"{row['TituloReview']}\"")
                print("   " + "-" * 50)
    
    def mostrar_todas_discordancias(self, df: pd.DataFrame, columna_referencia: str = 'Sentimiento'):
        """
        Muestra TODAS las opiniones discordantes completas organizadas por tipo.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            columna_referencia (str): Columna de referencia para comparar
        """
        # Configurar pandas para mostrar texto completo
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_columns', None)
        
        print("📋 LISTADO COMPLETO DE DISCORDANCIAS: CARDIFF NLP vs", columna_referencia.upper())
        print("=" * 80)
        
        # Encontrar discordancias
        discordantes = df[df[columna_referencia] != df['SentimientoCardiff']].copy()
        
        if len(discordantes) == 0:
            print(f"✅ No se encontraron discordancias entre Cardiff NLP y {columna_referencia}")
            return discordantes
        
        print(f"📊 Total de discordancias: {len(discordantes)}/{len(df)} ({len(discordantes)/len(df)*100:.1f}%)")
        
        # Agrupar por tipo de discordancia
        tipos_discordancia = discordantes.groupby([columna_referencia, 'SentimientoCardiff']).size().sort_values(ascending=False)
        
        print(f"\n📈 Tipos de discordancia encontrados:")
        for (sent_ref, sent_cardiff), count in tipos_discordancia.items():
            porcentaje = (count / len(discordantes)) * 100
            print(f"   • {sent_ref} → {sent_cardiff}: {count} casos ({porcentaje:.1f}%)")
        
        print("\n" + "=" * 80)
        print("📄 LISTADO DETALLADO DE TODAS LAS DISCORDANCIAS")
        print("=" * 80)
        
        # Mostrar todas las discordancias organizadas por tipo
        contador_global = 1
        for (sent_ref, sent_cardiff), count in tipos_discordancia.items():
            print(f"\n🎯 TIPO: {sent_ref} ({columna_referencia}) → {sent_cardiff} (Cardiff NLP)")
            print(f"📊 Total en esta categoría: {count} casos")
            print("-" * 80)
            
            # Obtener todos los casos de este tipo
            casos = discordantes[
                (discordantes[columna_referencia] == sent_ref) & 
                (discordantes['SentimientoCardiff'] == sent_cardiff)
            ].copy()
            
            # Ordenar por atracción para mejor organización
            casos = casos.sort_values('Atraccion')
            
            for idx, row in casos.iterrows():
                print(f"\n#{contador_global:03d} | {row['Atraccion']}")
                print(f"     ⭐ Calificación: {row['Calificacion']}/5")
                print(f"     🔄 {columna_referencia}: {row[columna_referencia]}")
                print(f"     🐦 Cardiff NLP: {row['SentimientoCardiff']}")
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
