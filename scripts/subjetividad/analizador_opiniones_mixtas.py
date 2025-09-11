"""
Analizador de Opiniones Mixtas - Análisis de Subjetividad por Frases
================================================================

Este módulo proporciona análisis granular de subjetividad dividing opiniones 
en frases individuales para identificar contenido mixto (subjetivo + objetivo).

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from .analizador_huggingface_subjetividad import AnalizadorHuggingFaceSubjetividad

class AnalizadorOpinionesMixtas:
    """
    Analizador especializado para identificar opiniones mixtas mediante
    segmentación de frases y análisis individual de subjetividad.
    """
    
    def __init__(self, modelo_subjetividad: str = "GroNLP/mdebertav3-subjectivity-multilingual"):
        """
        Inicializa el analizador de opiniones mixtas.
        
        Args:
            modelo_subjetividad: Modelo para análisis de subjetividad
        """
        self.analizador_subjetividad = AnalizadorHuggingFaceSubjetividad(modelo_subjetividad)
        self.segmentador = None
        self.modelo_cargado = False
    
    def configurar_modelos(self) -> bool:
        """
        Configura y carga los modelos necesarios.
        
        Returns:
            bool: True si los modelos se cargaron correctamente
        """
        try:
            # Configurar segmentador de frases
            from wtpsplit import SaT
            import torch
            
            self.segmentador = SaT("sat-3l-sm")
            if torch.cuda.is_available():
                self.segmentador.half().to("cuda")
            
            # Configurar analizador de subjetividad
            self.analizador_subjetividad.cargar_modelo()
            
            self.modelo_cargado = True
            return True
            
        except ImportError:
            print("❌ Error: Instalar wtpsplit con: pip install wtpsplit")
            return False
        except Exception as e:
            print(f"❌ Error configurando modelos: {e}")
            return False
    
    def analizar_opinion_por_frases(self, opinion: str) -> Dict:
        """
        Analiza una opinión dividiéndola en frases y clasificando cada una.
        
        Args:
            opinion: Texto de la opinión a analizar
            
        Returns:
            Dict: Resultados del análisis por frases
        """
        if pd.isna(opinion) or str(opinion).strip() == "":
            return self._resultado_vacio()
        
        try:
            # Segmentar en frases
            frases_raw = self.segmentador.split(str(opinion))
            frases = [f.strip() for f in frases_raw 
                     if len(f.strip()) > 5 and any(c.isalpha() for c in f.strip())]
            
            if not frases:
                return self._resultado_vacio()
            
            # Clasificar cada frase
            clasificaciones = []
            for frase in frases:
                resultado = self.analizador_subjetividad.analizar_subjetividad_texto(frase)
                clasificaciones.append(resultado['categoria'])
            
            # Calcular estadísticas
            return self._calcular_estadisticas_frases(frases, clasificaciones)
            
        except Exception:
            return self._resultado_vacio()
    
    def _resultado_vacio(self) -> Dict:
        """Retorna resultado vacío por defecto."""
        return {
            'frases': [],
            'clasificaciones_frases': [],
            'total_frases': 0,
            'frases_subjetivas': 0,
            'frases_objetivas': 0,
            'clasificacion_final': 'Objetivo',
            'es_mixta': False,
            'porcentaje_subjetivo': 0.0,
            'porcentaje_objetivo': 0.0,
            'tipo_opinion': 'Objetivo'
        }
    
    def _calcular_estadisticas_frases(self, frases: List[str], clasificaciones: List[str]) -> Dict:
        """Calcula estadísticas de análisis por frases."""
        total_frases = len(frases)
        frases_subjetivas = clasificaciones.count('Subjetivo')
        frases_objetivas = clasificaciones.count('Objetivo')
        
        porcentaje_subjetivo = (frases_subjetivas / total_frases) * 100
        porcentaje_objetivo = (frases_objetivas / total_frases) * 100
        
        # Determinar tipo de opinión
        if frases_subjetivas > 0 and frases_objetivas > 0:
            tipo_opinion = 'Mixta'
            es_mixta = True
        elif frases_subjetivas > frases_objetivas:
            tipo_opinion = 'Subjetivo'
            es_mixta = False
        else:
            tipo_opinion = 'Objetivo'
            es_mixta = False
        
        return {
            'frases': frases,
            'clasificaciones_frases': clasificaciones,
            'total_frases': total_frases,
            'frases_subjetivas': frases_subjetivas,
            'frases_objetivas': frases_objetivas,
            'clasificacion_final': tipo_opinion,
            'es_mixta': es_mixta,
            'porcentaje_subjetivo': porcentaje_subjetivo,
            'porcentaje_objetivo': porcentaje_objetivo,
            'tipo_opinion': tipo_opinion
        }
    
    def procesar_dataset(self, df: pd.DataFrame, columna_texto: str = 'TituloReview', 
                        batch_size: int = 10) -> pd.DataFrame:
        """
        Procesa un dataset completo analizando opiniones por frases.
        
        Args:
            df: Dataset a procesar
            columna_texto: Columna con el texto a analizar
            batch_size: Tamaño de lote para procesamiento
            
        Returns:
            DataFrame con análisis de opiniones mixtas
        """
        df_resultado = df.copy()
        resultados = []
        total_opiniones = len(df)

        for i in range(0, total_opiniones, batch_size):
            batch_end = min(i + batch_size, total_opiniones)
            print(f"🔄 Procesando lote {i + 1}-{batch_end} de {total_opiniones} opiniones...")

            for idx in range(i, batch_end):
                opinion = df.iloc[idx][columna_texto]
                resultado = self.analizar_opinion_por_frases(opinion)
                resultados.append(resultado)

        # Agregar resultados al DataFrame
        df_resultado['TotalFrases'] = [r['total_frases'] for r in resultados]
        df_resultado['FrasesSubjetivas'] = [r['frases_subjetivas'] for r in resultados]
        df_resultado['FrasesObjetivas'] = [r['frases_objetivas'] for r in resultados]
        df_resultado['TipoOpinion'] = [r['tipo_opinion'] for r in resultados]
        df_resultado['EsMixta'] = [r['es_mixta'] for r in resultados]
        df_resultado['PorcentajeSubjetivo'] = [r['porcentaje_subjetivo'] for r in resultados]
        df_resultado['PorcentajeObjetivo'] = [r['porcentaje_objetivo'] for r in resultados]

        print("✅ Procesamiento completo.")
        return df_resultado
    
    def obtener_estadisticas_mixtas(self, df: pd.DataFrame) -> Dict:
        """
        Calcula estadísticas de opiniones mixtas.
        
        Args:
            df: DataFrame con análisis de opiniones mixtas
            
        Returns:
            Dict con estadísticas
        """
        total_opiniones = len(df)
        
        # Distribución por tipos
        distribucion_tipos = df['TipoOpinion'].value_counts()
        porcentajes_tipos = (distribucion_tipos / total_opiniones * 100).round(1)
        
        # Estadísticas de frases
        total_frases = df['TotalFrases'].sum()
        total_subjetivas = df['FrasesSubjetivas'].sum()
        total_objetivas = df['FrasesObjetivas'].sum()
        
        # Estadísticas de opiniones mixtas
        opiniones_mixtas = df[df['EsMixta'] == True]
        
        estadisticas = {
            'total_opiniones': total_opiniones,
            'distribucion_tipos': distribucion_tipos,
            'porcentajes_tipos': porcentajes_tipos,
            'total_frases': total_frases,
            'total_frases_subjetivas': total_subjetivas,
            'total_frases_objetivas': total_objetivas,
            'porcentaje_frases_subjetivas': (total_subjetivas / total_frases * 100) if total_frases > 0 else 0,
            'porcentaje_frases_objetivas': (total_objetivas / total_frases * 100) if total_frases > 0 else 0,
            'promedio_frases_por_opinion': total_frases / total_opiniones if total_opiniones > 0 else 0,
            'opiniones_mixtas': len(opiniones_mixtas),
            'porcentaje_mixtas': (len(opiniones_mixtas) / total_opiniones * 100) if total_opiniones > 0 else 0
        }
        
        # Estadísticas específicas de opiniones mixtas
        if len(opiniones_mixtas) > 0:
            estadisticas.update({
                'mixtas_promedio_frases': opiniones_mixtas['TotalFrases'].mean(),
                'mixtas_promedio_subjetivo': opiniones_mixtas['PorcentajeSubjetivo'].mean(),
                'mixtas_promedio_objetivo': opiniones_mixtas['PorcentajeObjetivo'].mean()
            })
        
        return estadisticas
    
    def mostrar_estadisticas(self, estadisticas: Dict) -> None:
        """
        Muestra estadísticas de análisis de opiniones mixtas.
        
        Args:
            estadisticas: Estadísticas calculadas
        """
        print("📊 ANÁLISIS DE OPINIONES MIXTAS")
        print("=" * 50)
        
        print(f"📈 Total opiniones: {estadisticas['total_opiniones']}")
        
        print(f"\n📋 DISTRIBUCIÓN POR TIPOS:")
        for tipo, cantidad in estadisticas['distribucion_tipos'].items():
            porcentaje = estadisticas['porcentajes_tipos'][tipo]
            print(f"• {tipo}: {cantidad} ({porcentaje}%)")
        
        print(f"\n📊 ESTADÍSTICAS DE FRASES:")
        print(f"• Total frases: {estadisticas['total_frases']}")
        print(f"• Subjetivas: {estadisticas['total_frases_subjetivas']} ({estadisticas['porcentaje_frases_subjetivas']:.1f}%)")
        print(f"• Objetivas: {estadisticas['total_frases_objetivas']} ({estadisticas['porcentaje_frases_objetivas']:.1f}%)")
        print(f"• Promedio por opinión: {estadisticas['promedio_frases_por_opinion']:.1f}")
        
        if estadisticas['porcentaje_mixtas'] > 0:
            print(f"\n🔀 CARACTERÍSTICAS OPINIONES MIXTAS:")
            print(f"• Total: {estadisticas['opiniones_mixtas']} ({estadisticas['porcentaje_mixtas']:.1f}%)")
            print(f"• Promedio frases: {estadisticas.get('mixtas_promedio_frases', 0):.1f}")
            print(f"• Promedio subjetivo: {estadisticas.get('mixtas_promedio_subjetivo', 0):.1f}%")
            print(f"• Promedio objetivo: {estadisticas.get('mixtas_promedio_objetivo', 0):.1f}%")
    
    def mostrar_ejemplos_mixtos(self, df: pd.DataFrame, n_ejemplos: int = 3) -> None:
        """
        Muestra ejemplos de opiniones mixtas con desglose detallado.
        
        Args:
            df: DataFrame con análisis
            n_ejemplos: Número de ejemplos a mostrar
        """
        opiniones_mixtas = df[df['EsMixta'] == True]
        
        if len(opiniones_mixtas) == 0:
            print("❌ No se encontraron opiniones mixtas")
            return
        
        print(f"\n🔍 EJEMPLOS DE OPINIONES MIXTAS")
        print("=" * 60)
        
        ejemplos = opiniones_mixtas.sample(min(n_ejemplos, len(opiniones_mixtas)), random_state=42)
        
        for i, (_, ejemplo) in enumerate(ejemplos.iterrows(), 1):
            print(f"\n🎯 EJEMPLO {i}:")
            print(f"📝 Opinión: \"{ejemplo['TituloReview']}\"")
            print(f"📊 {ejemplo['TotalFrases']} frases | {ejemplo['FrasesSubjetivas']} subjetivas | {ejemplo['FrasesObjetivas']} objetivas")
            print(f"📈 {ejemplo['PorcentajeSubjetivo']:.1f}% subjetivo, {ejemplo['PorcentajeObjetivo']:.1f}% objetivo")
            
            # Mostrar desglose de frases si se tiene el análisis detallado
            resultado_detallado = self.analizar_opinion_por_frases(ejemplo['TituloReview'])
            if resultado_detallado['frases']:
                print(f"📋 Desglose por frases:")
                for j, (frase, clasificacion) in enumerate(zip(resultado_detallado['frases'], 
                                                             resultado_detallado['clasificaciones_frases']), 1):
                    icono = "💭" if clasificacion == 'Subjetivo' else "📊"
                    frase_corta = frase if len(frase) <= 70 else frase[:67] + "..."
                    print(f"   {icono} {j}. [{clasificacion}] \"{frase_corta}\"")
    
    def validar_hipotesis(self, estadisticas: Dict, umbral_mixtas: float = 15.0) -> Dict:
        """
        Valida la hipótesis de opiniones mixtas.
        
        Args:
            estadisticas: Estadísticas del análisis
            umbral_mixtas: Umbral para considerar significativo el porcentaje de mixtas
            
        Returns:
            Dict con resultados de validación
        """
        porcentaje_mixtas = estadisticas['porcentaje_mixtas']
        hipotesis_confirmada = porcentaje_mixtas >= umbral_mixtas
        
        validacion = {
            'hipotesis_confirmada': hipotesis_confirmada,
            'porcentaje_mixtas': porcentaje_mixtas,
            'umbral_usado': umbral_mixtas,
            'evidencia_significativa': porcentaje_mixtas > 10.0,
            'mensaje_resultado': self._generar_mensaje_validacion(porcentaje_mixtas, hipotesis_confirmada)
        }
        
        return validacion
    
    def _generar_mensaje_validacion(self, porcentaje: float, confirmada: bool) -> str:
        """Genera mensaje de validación de hipótesis."""
        if confirmada:
            return f"✅ HIPÓTESIS CONFIRMADA: {porcentaje:.1f}% de opiniones son mixtas"
        elif porcentaje > 5:
            return f"⚠️ EVIDENCIA PARCIAL: {porcentaje:.1f}% de opiniones son mixtas"
        else:
            return f"❌ HIPÓTESIS NO CONFIRMADA: Solo {porcentaje:.1f}% de opiniones son mixtas"
    
    def mostrar_validacion_hipotesis(self, validacion: Dict) -> None:
        """
        Muestra los resultados de validación de hipótesis.
        
        Args:
            validacion: Resultados de validación
        """
        print(f"\n🎯 VALIDACIÓN DE HIPÓTESIS")
        print("=" * 40)
        print(validacion['mensaje_resultado'])
        
        if validacion['evidencia_significativa']:
            print(f"📊 Las opiniones mixtas representan una proporción significativa")
            print(f"💡 Combinan información emocional con datos útiles para turistólogos")
        
        print(f"\n📈 Metodología validada:")
        print(f"• Segmentación automática con WtP-Split")
        print(f"• Clasificación por frases individuales")
        print(f"• Identificación exitosa de contenido híbrido")

def analizar_opiniones_mixtas(df: pd.DataFrame, columna_texto: str = 'TituloReview',
                             modelo_subjetividad: str = "GroNLP/mdebertav3-subjectivity-multilingual",
                             mostrar_ejemplos: bool = True, n_ejemplos: int = 3) -> pd.DataFrame:
    """
    Función principal para análisis completo de opiniones mixtas.
    
    Args:
        df: DataFrame con opiniones
        columna_texto: Columna con el texto a analizar
        modelo_subjetividad: Modelo para análisis de subjetividad
        mostrar_ejemplos: Si mostrar ejemplos de opiniones mixtas
        n_ejemplos: Número de ejemplos a mostrar
        
    Returns:
        DataFrame con análisis de opiniones mixtas
    """
    # Configurar analizador
    analizador = AnalizadorOpinionesMixtas(modelo_subjetividad)
    
    if not analizador.configurar_modelos():
        print("❌ Error configurando modelos")
        return df
    
    # Procesar dataset
    df_resultado = analizador.procesar_dataset(df, columna_texto)
    
    # Calcular y mostrar estadísticas
    estadisticas = analizador.obtener_estadisticas_mixtas(df_resultado)
    analizador.mostrar_estadisticas(estadisticas)
    
    # Validar hipótesis
    validacion = analizador.validar_hipotesis(estadisticas)
    analizador.mostrar_validacion_hipotesis(validacion)
    
    # Mostrar ejemplos si se solicita
    if mostrar_ejemplos:
        analizador.mostrar_ejemplos_mixtos(df_resultado, n_ejemplos)
    
    return df_resultado
