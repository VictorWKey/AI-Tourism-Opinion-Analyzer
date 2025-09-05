"""
Comparador de Métodos de Análisis de Sentimientos
===============================================

Este módulo contiene la lógica para comparar diferentes métodos de análisis
de sentimientos (por calificación vs modelos de ML).

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
from typing import Dict
import warnings
warnings.filterwarnings('ignore')

from .base_sentimientos import ConfiguracionSentimientos


class ComparadorSentimientos:
    """
    Clase para comparar diferentes métodos de análisis de sentimientos.
    """
    
    def __init__(self):
        """Inicializa el comparador con la configuración base."""
        self.config = ConfiguracionSentimientos()
    
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
        for sentimiento in self.config.SENTIMIENTOS_VALIDOS:
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
    
    def obtener_discordancias(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Obtiene todas las opiniones donde los métodos no concuerdan.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            
        Returns:
            pd.DataFrame: Dataset filtrado con solo las discordancias
        """
        if 'Sentimiento' not in df.columns or 'SentimientoHF' not in df.columns:
            print("❌ Error: El dataset debe tener ambas columnas 'Sentimiento' y 'SentimientoHF'")
            return pd.DataFrame()
        
        discordantes = df[df['Sentimiento'] != df['SentimientoHF']].copy()
        return discordantes
    
    def analizar_tipos_discordancia(self, df: pd.DataFrame) -> Dict:
        """
        Analiza los tipos de discordancia entre métodos.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            
        Returns:
            Dict: Análisis de tipos de discordancia
        """
        discordantes = self.obtener_discordancias(df)
        
        if len(discordantes) == 0:
            return {'total_discordancias': 0, 'tipos': {}}
        
        tipos_discordancia = discordantes.groupby(['Sentimiento', 'SentimientoHF']).size().sort_values(ascending=False)
        total_discordancias = len(discordantes)
        
        tipos_detalle = {}
        for (sent_cal, sent_hf), count in tipos_discordancia.items():
            porcentaje = (count / total_discordancias) * 100
            tipos_detalle[f"{sent_cal} → {sent_hf}"] = {
                'count': count,
                'porcentaje': porcentaje,
                'ejemplos': discordantes[
                    (discordantes['Sentimiento'] == sent_cal) & 
                    (discordantes['SentimientoHF'] == sent_hf)
                ].head(3).to_dict('records')
            }
        
        return {
            'total_discordancias': total_discordancias,
            'porcentaje_total': (total_discordancias / len(df)) * 100,
            'tipos': tipos_detalle
        }
    
    def mostrar_resumen_discordancias(self, analisis_discordancias: Dict):
        """
        Muestra un resumen de las discordancias encontradas.
        
        Args:
            analisis_discordancias (Dict): Resultado de analizar_tipos_discordancia()
        """
        print("🔍 RESUMEN DE DISCORDANCIAS ENTRE MÉTODOS")
        print("=" * 60)
        
        if analisis_discordancias['total_discordancias'] == 0:
            print("✅ No se encontraron discordancias entre los métodos")
            return
        
        print(f"📊 Total de discordancias: {analisis_discordancias['total_discordancias']}")
        print(f"📊 Porcentaje de discordancias: {analisis_discordancias['porcentaje_total']:.1f}%")
        
        print(f"\n📈 Tipos de discordancia más comunes:")
        for tipo, detalle in list(analisis_discordancias['tipos'].items())[:5]:
            print(f"   • {tipo}: {detalle['count']} casos ({detalle['porcentaje']:.1f}%)")
    
    def calcular_metricas_precision(self, df: pd.DataFrame) -> Dict:
        """
        Calcula métricas de precisión, recall y F1 para la comparación.
        
        Args:
            df (pd.DataFrame): Dataset con ambas columnas de sentimiento
            
        Returns:
            Dict: Métricas de evaluación por sentimiento
        """
        if 'Sentimiento' not in df.columns or 'SentimientoHF' not in df.columns:
            return {}
        
        metricas = {}
        
        for sentimiento in self.config.SENTIMIENTOS_VALIDOS:
            # Verdaderos positivos: ambos métodos coinciden en el sentimiento
            tp = len(df[(df['Sentimiento'] == sentimiento) & (df['SentimientoHF'] == sentimiento)])
            
            # Falsos positivos: HF dice que es este sentimiento pero calificación dice que no
            fp = len(df[(df['Sentimiento'] != sentimiento) & (df['SentimientoHF'] == sentimiento)])
            
            # Falsos negativos: Calificación dice que es este sentimiento pero HF dice que no
            fn = len(df[(df['Sentimiento'] == sentimiento) & (df['SentimientoHF'] != sentimiento)])
            
            # Calcular métricas
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            metricas[sentimiento] = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'tp': tp,
                'fp': fp,
                'fn': fn
            }
        
        # Calcular métricas macro promedio
        precision_macro = sum(m['precision'] for m in metricas.values()) / len(metricas)
        recall_macro = sum(m['recall'] for m in metricas.values()) / len(metricas)
        f1_macro = sum(m['f1_score'] for m in metricas.values()) / len(metricas)
        
        metricas['macro_promedio'] = {
            'precision': precision_macro,
            'recall': recall_macro,
            'f1_score': f1_macro
        }
        
        return metricas
    
    def mostrar_metricas_precision(self, metricas: Dict):
        """
        Muestra las métricas de precisión en consola.
        
        Args:
            metricas (Dict): Métricas calculadas por calcular_metricas_precision()
        """
        print("📊 MÉTRICAS DE EVALUACIÓN (HuggingFace vs Calificaciones)")
        print("=" * 70)
        
        print(f"{'Sentimiento':<12} {'Precisión':<10} {'Recall':<10} {'F1-Score':<10}")
        print("-" * 50)
        
        for sentimiento in self.config.SENTIMIENTOS_VALIDOS:
            if sentimiento in metricas:
                m = metricas[sentimiento]
                print(f"{sentimiento:<12} {m['precision']:<10.3f} {m['recall']:<10.3f} {m['f1_score']:<10.3f}")
        
        if 'macro_promedio' in metricas:
            print("-" * 50)
            m_macro = metricas['macro_promedio']
            print(f"{'PROMEDIO':<12} {m_macro['precision']:<10.3f} {m_macro['recall']:<10.3f} {m_macro['f1_score']:<10.3f}")
        
        print("\nℹ️  Interpretación:")
        print("   • Precisión: % de predicciones HF correctas para cada sentimiento")
        print("   • Recall: % de casos reales detectados por HF")
        print("   • F1-Score: Promedio armónico de precisión y recall")
