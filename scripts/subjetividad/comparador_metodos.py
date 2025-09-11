"""
Comparador de Métodos de Subjetividad
====================================

Este módulo contiene funciones para comparar diferentes métodos de clasificación
de subjetividad: HuggingFace, Análisis por Frases y LLM.

Autor: Sistema de Análisis de Opiniones Turísticas
Fecha: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, List


class ComparadorMetodosSubjetividad:
    """
    Comparador de métodos de clasificación de subjetividad.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el comparador con el dataset.
        
        Args:
            df (pd.DataFrame): Dataset con columnas de subjetividad
        """
        self.df = df.copy()
        self.columnas_subjetividad = {
            'hf': 'SubjetividadConHF',
            'frases': 'SubjetividadConFrases', 
            'llm': 'SubjetividadConLLM'
        }
        
    def comparar_hf_vs_frases(self) -> Dict:
        """
        Compara clasificaciones entre HuggingFace y Análisis por Frases.
        
        Returns:
            Dict: Diccionario con estadísticas de comparación
        """
        col_hf = self.columnas_subjetividad['hf']
        col_frases = self.columnas_subjetividad['frases']
        
        if col_hf not in self.df.columns or col_frases not in self.df.columns:
            return {}
        
        # Crear tabla de contingencia
        contingencia = pd.crosstab(self.df[col_hf], self.df[col_frases], margins=True)
        
        # Calcular transiciones desde HF
        total_subjetivo_hf = (self.df[col_hf] == 'Subjetivo').sum()
        total_objetivo_hf = (self.df[col_hf] == 'Objetivo').sum()
        
        # Transiciones desde Subjetivo (HF)
        subj_a_subj = ((self.df[col_hf] == 'Subjetivo') & (self.df[col_frases] == 'Subjetivo')).sum()
        subj_a_mixta = ((self.df[col_hf] == 'Subjetivo') & (self.df[col_frases] == 'Mixta')).sum()
        subj_a_obj = ((self.df[col_hf] == 'Subjetivo') & (self.df[col_frases] == 'Objetivo')).sum()
        
        # Transiciones desde Objetivo (HF)
        obj_a_subj = ((self.df[col_hf] == 'Objetivo') & (self.df[col_frases] == 'Subjetivo')).sum()
        obj_a_mixta = ((self.df[col_hf] == 'Objetivo') & (self.df[col_frases] == 'Mixta')).sum()
        obj_a_obj = ((self.df[col_hf] == 'Objetivo') & (self.df[col_frases] == 'Objetivo')).sum()
        
        resultados = {
            'contingencia': contingencia,
            'total_hf': len(self.df),
            'subjetivo_hf': total_subjetivo_hf,
            'objetivo_hf': total_objetivo_hf,
            'transiciones_subjetivo': {
                'permanece_subjetivo': subj_a_subj,
                'se_vuelve_mixta': subj_a_mixta,
                'se_vuelve_objetivo': subj_a_obj,
                'pct_permanece': (subj_a_subj / total_subjetivo_hf * 100) if total_subjetivo_hf > 0 else 0,
                'pct_mixta': (subj_a_mixta / total_subjetivo_hf * 100) if total_subjetivo_hf > 0 else 0,
                'pct_objetivo': (subj_a_obj / total_subjetivo_hf * 100) if total_subjetivo_hf > 0 else 0
            },
            'transiciones_objetivo': {
                'permanece_objetivo': obj_a_obj,
                'se_vuelve_mixta': obj_a_mixta,
                'se_vuelve_subjetivo': obj_a_subj,
                'pct_permanece': (obj_a_obj / total_objetivo_hf * 100) if total_objetivo_hf > 0 else 0,
                'pct_mixta': (obj_a_mixta / total_objetivo_hf * 100) if total_objetivo_hf > 0 else 0,
                'pct_subjetivo': (obj_a_subj / total_objetivo_hf * 100) if total_objetivo_hf > 0 else 0
            }
        }
        
        return resultados
    
    def comparar_frases_vs_llm_coincidencias(self) -> Dict:
        """
        Compara métodos de Frases vs LLM enfocándose solo en coincidencias.
        
        Returns:
            Dict: Diccionario con estadísticas de coincidencias
        """
        col_frases = self.columnas_subjetividad['frases']
        col_llm = self.columnas_subjetividad['llm']
        
        if col_frases not in self.df.columns or col_llm not in self.df.columns:
            return {}
        
        # Crear tabla de contingencia completa
        contingencia_completa = pd.crosstab(self.df[col_frases], self.df[col_llm], margins=True)
        
        # Filtrar solo coincidencias
        coincidencias = self.df[self.df[col_frases] == self.df[col_llm]]
        
        # Contar coincidencias por tipo
        coincidencias_por_tipo = coincidencias[col_frases].value_counts()
        
        # Calcular porcentajes de coincidencia para cada tipo
        total_por_tipo_frases = self.df[col_frases].value_counts()
        total_por_tipo_llm = self.df[col_llm].value_counts()
        
        resultados = {
            'contingencia_completa': contingencia_completa,
            'total_opiniones': len(self.df),
            'total_coincidencias': len(coincidencias),
            'pct_coincidencia_total': (len(coincidencias) / len(self.df) * 100),
            'coincidencias_por_tipo': coincidencias_por_tipo.to_dict(),
            'distribucion_frases': total_por_tipo_frases.to_dict(),
            'distribucion_llm': total_por_tipo_llm.to_dict(),
            'porcentajes_coincidencia': {}
        }
        
        # Calcular porcentaje de coincidencia para cada tipo
        for tipo in ['Subjetivo', 'Objetivo', 'Mixta']:
            if tipo in coincidencias_por_tipo and tipo in total_por_tipo_frases:
                pct = (coincidencias_por_tipo[tipo] / total_por_tipo_frases[tipo] * 100)
                resultados['porcentajes_coincidencia'][tipo] = pct
        
        return resultados
    
    def mostrar_comparacion_hf_frases(self, resultados: Dict) -> None:
        """
        Muestra los resultados de la comparación HF vs Frases.
        
        Args:
            resultados (Dict): Resultados de comparar_hf_vs_frases()
        """
        if not resultados:
            print("❌ No hay datos para mostrar la comparación HF vs Frases")
            return
        
        print("🔄 COMPARACIÓN: HuggingFace vs Análisis por Frases")
        print("=" * 60)
        
        print("\n📊 Tabla de Contingencia:")
        print(resultados['contingencia'])
        
        print(f"\n📈 Transiciones desde Subjetivo (HF): {resultados['subjetivo_hf']} opiniones")
        trans_subj = resultados['transiciones_subjetivo']
        print(f"   • Permanece Subjetivo: {trans_subj['permanece_subjetivo']} ({trans_subj['pct_permanece']:.1f}%)")
        print(f"   • Se vuelve Mixta: {trans_subj['se_vuelve_mixta']} ({trans_subj['pct_mixta']:.1f}%)")
        print(f"   • Se vuelve Objetivo: {trans_subj['se_vuelve_objetivo']} ({trans_subj['pct_objetivo']:.1f}%)")
        
        print(f"\n📉 Transiciones desde Objetivo (HF): {resultados['objetivo_hf']} opiniones")
        trans_obj = resultados['transiciones_objetivo']
        print(f"   • Permanece Objetivo: {trans_obj['permanece_objetivo']} ({trans_obj['pct_permanece']:.1f}%)")
        print(f"   • Se vuelve Mixta: {trans_obj['se_vuelve_mixta']} ({trans_obj['pct_mixta']:.1f}%)")
        print(f"   • Se vuelve Subjetivo: {trans_obj['se_vuelve_subjetivo']} ({trans_obj['pct_subjetivo']:.1f}%)")
    
    def mostrar_comparacion_frases_llm(self, resultados: Dict) -> None:
        """
        Muestra los resultados de la comparación Frases vs LLM (solo coincidencias).
        
        Args:
            resultados (Dict): Resultados de comparar_frases_vs_llm_coincidencias()
        """
        if not resultados:
            print("❌ No hay datos para mostrar la comparación Frases vs LLM")
            return
        
        print("🔄 COMPARACIÓN: Análisis por Frases vs LLM (Solo Coincidencias)")
        print("=" * 70)
        
        print("\n📊 Tabla de Contingencia Completa:")
        print(resultados['contingencia_completa'])
        
        print(f"\n🎯 Resumen de Coincidencias:")
        print(f"   • Total de opiniones: {resultados['total_opiniones']}")
        print(f"   • Coincidencias totales: {resultados['total_coincidencias']}")
        print(f"   • Porcentaje de coincidencia: {resultados['pct_coincidencia_total']:.1f}%")
        
        print(f"\n📈 Coincidencias por Tipo:")
        for tipo, cantidad in resultados['coincidencias_por_tipo'].items():
            if tipo in resultados['porcentajes_coincidencia']:
                pct = resultados['porcentajes_coincidencia'][tipo]
                print(f"   • {tipo}: {cantidad} opiniones ({pct:.1f}% de coincidencia)")
        
        print(f"\n📋 Distribución en Análisis por Frases:")
        for tipo, cantidad in resultados['distribucion_frases'].items():
            pct = (cantidad / resultados['total_opiniones'] * 100)
            print(f"   • {tipo}: {cantidad} ({pct:.1f}%)")
        
        print(f"\n📋 Distribución en LLM:")
        for tipo, cantidad in resultados['distribucion_llm'].items():
            pct = (cantidad / resultados['total_opiniones'] * 100)
            print(f"   • {tipo}: {cantidad} ({pct:.1f}%)")
    
    def visualizar_comparacion_hf_frases(self, resultados: Dict) -> None:
        """
        Crea visualizaciones para la comparación HF vs Frases.
        
        Args:
            resultados (Dict): Resultados de comparar_hf_vs_frases()
        """
        if not resultados:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Heatmap de contingencia
        contingencia_sin_totales = resultados['contingencia'].iloc[:-1, :-1]
        sns.heatmap(contingencia_sin_totales, annot=True, fmt='d', cmap='Blues', ax=ax1)
        ax1.set_title('Tabla de Contingencia: HF vs Frases')
        ax1.set_xlabel('Análisis por Frases')
        ax1.set_ylabel('HuggingFace')
        
        # 2. Transiciones desde Subjetivo
        trans_subj = resultados['transiciones_subjetivo']
        labels_subj = ['Permanece\nSubjetivo', 'Se vuelve\nMixta', 'Se vuelve\nObjetivo']
        values_subj = [trans_subj['permanece_subjetivo'], trans_subj['se_vuelve_mixta'], trans_subj['se_vuelve_objetivo']]
        colors_subj = ['#2E8B57', '#FFD700', '#CD5C5C']
        
        ax2.pie(values_subj, labels=labels_subj, colors=colors_subj, autopct='%1.1f%%', startangle=90)
        ax2.set_title(f'Transiciones desde Subjetivo (HF)\nTotal: {resultados["subjetivo_hf"]} opiniones')
        
        # 3. Transiciones desde Objetivo
        trans_obj = resultados['transiciones_objetivo']
        labels_obj = ['Permanece\nObjetivo', 'Se vuelve\nMixta', 'Se vuelve\nSubjetivo']
        values_obj = [trans_obj['permanece_objetivo'], trans_obj['se_vuelve_mixta'], trans_obj['se_vuelve_subjetivo']]
        colors_obj = ['#4682B4', '#FFD700', '#2E8B57']
        
        ax3.pie(values_obj, labels=labels_obj, colors=colors_obj, autopct='%1.1f%%', startangle=90)
        ax3.set_title(f'Transiciones desde Objetivo (HF)\nTotal: {resultados["objetivo_hf"]} opiniones')
        
        # 4. Barras comparativas de porcentajes
        tipos = ['Subjetivo→Subjetivo', 'Subjetivo→Mixta', 'Subjetivo→Objetivo', 
                'Objetivo→Objetivo', 'Objetivo→Mixta', 'Objetivo→Subjetivo']
        porcentajes = [trans_subj['pct_permanece'], trans_subj['pct_mixta'], trans_subj['pct_objetivo'],
                      trans_obj['pct_permanece'], trans_obj['pct_mixta'], trans_obj['pct_subjetivo']]
        colores = ['#2E8B57', '#FFD700', '#CD5C5C', '#4682B4', '#FFD700', '#2E8B57']
        
        bars = ax4.bar(range(len(tipos)), porcentajes, color=colores, alpha=0.7)
        ax4.set_xlabel('Tipos de Transición')
        ax4.set_ylabel('Porcentaje (%)')
        ax4.set_title('Porcentajes de Transición HF → Frases')
        ax4.set_xticks(range(len(tipos)))
        ax4.set_xticklabels(tipos, rotation=45, ha='right')
        
        # Agregar valores en las barras
        for bar, pct in zip(bars, porcentajes):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{pct:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def visualizar_comparacion_frases_llm(self, resultados: Dict) -> None:
        """
        Crea visualizaciones para la comparación Frases vs LLM.
        
        Args:
            resultados (Dict): Resultados de comparar_frases_vs_llm_coincidencias()
        """
        if not resultados:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Heatmap de contingencia completa
        contingencia_sin_totales = resultados['contingencia_completa'].iloc[:-1, :-1]
        sns.heatmap(contingencia_sin_totales, annot=True, fmt='d', cmap='Greens', ax=ax1)
        ax1.set_title('Tabla de Contingencia: Frases vs LLM')
        ax1.set_xlabel('LLM')
        ax1.set_ylabel('Análisis por Frases')
        
        # 2. Pie chart de coincidencias vs no coincidencias
        total = resultados['total_opiniones']
        coincidencias = resultados['total_coincidencias']
        no_coincidencias = total - coincidencias
        
        ax2.pie([coincidencias, no_coincidencias], 
               labels=[f'Coincidencias\n({coincidencias})', f'No Coincidencias\n({no_coincidencias})'],
               colors=['#32CD32', '#FF6347'],
               autopct='%1.1f%%', startangle=90)
        ax2.set_title(f'Coincidencias Totales\nTotal: {total} opiniones')
        
        # 3. Barras de coincidencias por tipo
        tipos = list(resultados['coincidencias_por_tipo'].keys())
        cantidades = list(resultados['coincidencias_por_tipo'].values())
        colores = ['#2E8B57', '#4682B4', '#FFD700'][:len(tipos)]
        
        bars3 = ax3.bar(tipos, cantidades, color=colores, alpha=0.7)
        ax3.set_xlabel('Tipo de Clasificación')
        ax3.set_ylabel('Cantidad de Coincidencias')
        ax3.set_title('Coincidencias por Tipo de Clasificación')
        
        for bar, cantidad in zip(bars3, cantidades):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{cantidad}', ha='center', va='bottom', fontsize=10)
        
        # 4. Porcentajes de coincidencia por tipo
        tipos_pct = list(resultados['porcentajes_coincidencia'].keys())
        porcentajes_pct = list(resultados['porcentajes_coincidencia'].values())
        
        bars4 = ax4.bar(tipos_pct, porcentajes_pct, color=colores[:len(tipos_pct)], alpha=0.7)
        ax4.set_xlabel('Tipo de Clasificación')
        ax4.set_ylabel('Porcentaje de Coincidencia (%)')
        ax4.set_title('Porcentaje de Coincidencia por Tipo')
        ax4.set_ylim(0, 100)
        
        for bar, pct in zip(bars4, porcentajes_pct):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{pct:.1f}%', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.show()
    
    def analizar_discrepancias(self, metodo1: str, metodo2: str, n_ejemplos: int = 3) -> Dict:
        """
        Analiza y muestra ejemplos de discrepancias entre dos métodos de subjetividad.
        
        Args:
            metodo1 (str): Nombre de la primera columna de subjetividad
            metodo2 (str): Nombre de la segunda columna de subjetividad
            n_ejemplos (int): Número de ejemplos a mostrar por tipo de discrepancia
            
        Returns:
            Dict: Diccionario con ejemplos de discrepancias organizados por tipo
        """
        if metodo1 not in self.df.columns or metodo2 not in self.df.columns:
            return {}
        
        # Identificar discrepancias
        discrepancias = self.df[self.df[metodo1] != self.df[metodo2]].copy()
        
        # Organizar por tipos de discrepancia
        tipos_discrepancia = {}
        
        # Obtener todas las combinaciones posibles de discrepancias
        for valor1 in self.df[metodo1].unique():
            for valor2 in self.df[metodo2].unique():
                if valor1 != valor2:
                    filtro = (discrepancias[metodo1] == valor1) & (discrepancias[metodo2] == valor2)
                    ejemplos = discrepancias[filtro]
                    
                    if len(ejemplos) > 0:
                        clave = f"{valor1} → {valor2}"
                        # Seleccionar ejemplos aleatorios
                        n_disponibles = min(n_ejemplos, len(ejemplos))
                        muestra = ejemplos.sample(n=n_disponibles, random_state=42)
                        
                        tipos_discrepancia[clave] = {
                            'total': len(ejemplos),
                            'porcentaje': (len(ejemplos) / len(discrepancias) * 100),
                            'ejemplos': muestra[['TituloReview', metodo1, metodo2]].to_dict('records')
                        }
        
        resultados = {
            'total_discrepancias': len(discrepancias),
            'total_opiniones': len(self.df),
            'porcentaje_discrepancias': (len(discrepancias) / len(self.df) * 100),
            'tipos_discrepancia': tipos_discrepancia,
            'metodos_comparados': [metodo1, metodo2]
        }
        
        return resultados
    
    def mostrar_discrepancias(self, resultados: Dict) -> None:
        """
        Muestra los resultados del análisis de discrepancias de forma organizada.
        
        Args:
            resultados (Dict): Resultados de analizar_discrepancias()
        """
        if not resultados:
            print("❌ No hay datos de discrepancias para mostrar")
            return
        
        metodo1, metodo2 = resultados['metodos_comparados']
        
        print("🔍 ANÁLISIS DE DISCREPANCIAS ENTRE MÉTODOS")
        print("=" * 70)
        print(f"📊 Métodos comparados: {metodo1} vs {metodo2}")
        print(f"📈 Total de discrepancias: {resultados['total_discrepancias']}")
        print(f"📋 Total de opiniones: {resultados['total_opiniones']}")
        print(f"📊 Porcentaje de discrepancias: {resultados['porcentaje_discrepancias']:.1f}%")
        
        print(f"\n🔄 TIPOS DE DISCREPANCIAS:")
        print("-" * 50)
        
        for tipo, datos in resultados['tipos_discrepancia'].items():
            print(f"\n🔸 {tipo}")
            print(f"   Cantidad: {datos['total']} ({datos['porcentaje']:.1f}% de las discrepancias)")
            
            print(f"   \n📝 Ejemplos:")
            for i, ejemplo in enumerate(datos['ejemplos'], 1):
                opinion_corta = ejemplo['TituloReview'][:100] + "..." if len(ejemplo['TituloReview']) > 100 else ejemplo['TituloReview']
                print(f"      {i}. \"{opinion_corta}\"")
                print(f"         {metodo1}: {ejemplo[metodo1]} | {metodo2}: {ejemplo[metodo2]}")
                print()


class AnalizadorDiscrepancias:
    """
    Analizador especializado para estudiar discrepancias entre métodos de subjetividad.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el analizador de discrepancias.
        
        Args:
            df (pd.DataFrame): Dataset con análisis de subjetividad
        """
        self.df = df.copy()
    
    def analizar_todas_discrepancias(self, n_ejemplos: int = 3) -> Dict:
        """
        Analiza discrepancias entre todos los pares de métodos disponibles.
        
        Args:
            n_ejemplos (int): Número de ejemplos por tipo de discrepancia
            
        Returns:
            Dict: Resultados de análisis para todos los pares
        """
        metodos = ['SubjetividadConHF', 'SubjetividadConFrases', 'SubjetividadConLLM']
        metodos_disponibles = [m for m in metodos if m in self.df.columns]
        
        resultados = {}
        comparador = ComparadorMetodosSubjetividad(self.df)
        
        # Analizar todos los pares posibles
        for i in range(len(metodos_disponibles)):
            for j in range(i+1, len(metodos_disponibles)):
                metodo1, metodo2 = metodos_disponibles[i], metodos_disponibles[j]
                clave = f"{metodo1}_vs_{metodo2}"
                resultados[clave] = comparador.analizar_discrepancias(metodo1, metodo2, n_ejemplos)
        
        return resultados
    
    def mostrar_todas_discrepancias(self, resultados: Dict) -> None:
        """
        Muestra el análisis de discrepancias para todos los pares de métodos.
        
        Args:
            resultados (Dict): Resultados de analizar_todas_discrepancias()
        """
        comparador = ComparadorMetodosSubjetividad(self.df)
        
        for clave, datos in resultados.items():
            if datos:
                print("\n" + "="*100)
                comparador.mostrar_discrepancias(datos)
                print("="*100)


def cargar_datos_para_comparacion(ruta_dataset: str) -> pd.DataFrame:
    """
    Carga el dataset para análisis de comparación de métodos.
    
    Args:
        ruta_dataset (str): Ruta al archivo del dataset
        
    Returns:
        pd.DataFrame: Dataset cargado
    """
    try:
        df = pd.read_csv(ruta_dataset)
        print(f"✅ Dataset cargado: {len(df)} opiniones")
        
        # Verificar columnas necesarias
        columnas_necesarias = ['SubjetividadConHF', 'SubjetividadConFrases', 'SubjetividadConLLM']
        columnas_disponibles = [col for col in columnas_necesarias if col in df.columns]
        
        print(f"📋 Columnas de subjetividad disponibles: {columnas_disponibles}")
        
        if len(columnas_disponibles) < 2:
            print("⚠️  Se necesitan al menos 2 métodos de subjetividad para comparar")
        
        return df
        
    except Exception as e:
        print(f"❌ Error al cargar dataset: {e}")
        return pd.DataFrame()


def realizar_comparacion_completa(df: pd.DataFrame) -> Dict:
    """
    Realiza todas las comparaciones disponibles según los métodos presentes.
    
    Args:
        df (pd.DataFrame): Dataset con análisis de subjetividad
        
    Returns:
        Dict: Resultados de todas las comparaciones
    """
    comparador = ComparadorMetodosSubjetividad(df)
    resultados = {}
    
    # Comparación HF vs Frases
    if 'SubjetividadConHF' in df.columns and 'SubjetividadConFrases' in df.columns:
        print("🔄 Realizando comparación HF vs Frases...")
        resultados['hf_vs_frases'] = comparador.comparar_hf_vs_frases()
        comparador.mostrar_comparacion_hf_frases(resultados['hf_vs_frases'])
        print("\n" + "="*80 + "\n")
    
    # Comparación Frases vs LLM
    if 'SubjetividadConFrases' in df.columns and 'SubjetividadConLLM' in df.columns:
        print("🔄 Realizando comparación Frases vs LLM...")
        resultados['frases_vs_llm'] = comparador.comparar_frases_vs_llm_coincidencias()
        comparador.mostrar_comparacion_frases_llm(resultados['frases_vs_llm'])
    
    return resultados


def generar_visualizaciones_completas(df: pd.DataFrame, resultados: Dict) -> None:
    """
    Genera todas las visualizaciones de comparación.
    
    Args:
        df (pd.DataFrame): Dataset con análisis de subjetividad
        resultados (Dict): Resultados de las comparaciones
    """
    comparador = ComparadorMetodosSubjetividad(df)
    
    # Visualizar HF vs Frases
    if 'hf_vs_frases' in resultados:
        print("📊 Generando visualizaciones HF vs Frases...")
        comparador.visualizar_comparacion_hf_frases(resultados['hf_vs_frases'])
    
    # Visualizar Frases vs LLM
    if 'frases_vs_llm' in resultados:
        print("📊 Generando visualizaciones Frases vs LLM...")
        comparador.visualizar_comparacion_frases_llm(resultados['frases_vs_llm'])


def analizar_discrepancias_completas(df: pd.DataFrame, n_ejemplos: int = 3) -> Dict:
    """
    Realiza análisis completo de discrepancias entre todos los métodos disponibles.
    
    Args:
        df (pd.DataFrame): Dataset con análisis de subjetividad
        n_ejemplos (int): Número de ejemplos por tipo de discrepancia
        
    Returns:
        Dict: Resultados de análisis de discrepancias
    """
    analizador = AnalizadorDiscrepancias(df)
    resultados = analizador.analizar_todas_discrepancias(n_ejemplos)
    analizador.mostrar_todas_discrepancias(resultados)
    return resultados
