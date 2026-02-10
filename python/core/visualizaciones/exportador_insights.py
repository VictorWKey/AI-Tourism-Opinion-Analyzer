"""
Exportador de Insights de Texto
================================
Recopila todos los datos textuales (KPIs, fortalezas, debilidades,
resúmenes, validación del dataset) en un archivo JSON estructurado
para ser consumido por la UI en una sección separada.

Este módulo sustituye las visualizaciones que antes renderizaban
texto como imágenes PNG, proporcionando la misma información 
en formato de datos para una presentación más flexible y profesional.
"""

import pandas as pd
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter, defaultdict


class ExportadorInsights:
    """
    Recopila y exporta todos los insights textuales del análisis
    a un archivo JSON estructurado.
    """
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ruta para resúmenes generados por LLM (Fase 06)
        from config.config import ConfigDataset
        self.resumenes_path = ConfigDataset.get_shared_dir() / 'resumenes.json'
    
    def exportar(self) -> str:
        """
        Exporta todos los insights textuales a un archivo JSON.
        
        Returns:
            Nombre del archivo generado
        """
        insights = {
            "fecha_generacion": datetime.now().isoformat(),
            "validacion_dataset": self._exportar_validacion(),
            "kpis": self._exportar_kpis(),
            "fortalezas": self._exportar_fortalezas(),
            "debilidades": self._exportar_debilidades(),
            "resumenes": self._exportar_resumenes(),
        }
        
        output_path = self.output_dir / 'insights_textuales.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
        
        return 'insights_textuales'
    
    def _exportar_validacion(self) -> Dict[str, Any]:
        """Exporta el resumen de validación del dataset."""
        resumen = self.validador.get_resumen()
        
        recomendaciones = []
        if resumen['total_opiniones'] < 100:
            recomendaciones.append(
                "Dataset pequeño (<100 opiniones). Algunas visualizaciones avanzadas "
                "no fueron generadas. Considera agregar más datos para análisis más robustos."
            )
        if not resumen['tiene_fechas']:
            recomendaciones.append(
                "No hay fechas válidas en el dataset. El análisis temporal no está disponible. "
                "Asegúrate de que la columna 'FechaEstadia' tenga fechas en formato válido."
            )
        if not resumen['tiene_topicos']:
            recomendaciones.append(
                "No se detectaron tópicos en el dataset. El análisis jerárquico está limitado. "
                "Ejecuta la Fase 05 para identificar tópicos antes de generar visualizaciones."
            )
        if resumen['total_opiniones'] >= 100 and resumen['tiene_fechas'] and resumen['tiene_topicos']:
            recomendaciones.append(
                "Dataset completo y robusto. Todas las visualizaciones principales fueron "
                "generadas exitosamente."
            )
        if resumen['categorias_validas'] < 5:
            recomendaciones.append(
                "Pocas categorías identificadas. Esto puede limitar la granularidad "
                "del análisis por categoría."
            )
        
        return {
            "total_opiniones": int(resumen['total_opiniones']),
            "tiene_fechas": bool(resumen['tiene_fechas']),
            "rango_temporal_dias": int(resumen['rango_temporal_dias']) if resumen['rango_temporal_dias'] else 0,
            "categorias_identificadas": int(resumen['categorias_validas']),
            "tiene_topicos": bool(resumen['tiene_topicos']),
            "sentimientos": {
                "positivo": int(resumen['diversidad_sentimientos']['positivo']),
                "neutro": int(resumen['diversidad_sentimientos']['neutro']),
                "negativo": int(resumen['diversidad_sentimientos']['negativo']),
            },
            "recomendaciones": recomendaciones,
        }
    
    def _exportar_kpis(self) -> Dict[str, Any]:
        """Exporta los KPIs principales."""
        total_opiniones = len(self.df)
        pct_positivo = (self.df['Sentimiento'] == 'Positivo').sum() / total_opiniones * 100
        pct_neutro = (self.df['Sentimiento'] == 'Neutro').sum() / total_opiniones * 100
        pct_negativo = (self.df['Sentimiento'] == 'Negativo').sum() / total_opiniones * 100
        calificacion_prom = float(self.df['Calificacion'].mean()) if 'Calificacion' in self.df.columns else 0.0
        
        fortalezas_debilidades = self._calcular_fortalezas_debilidades()
        mejor_categoria = fortalezas_debilidades['fortalezas'][0]['categoria'] if fortalezas_debilidades['fortalezas'] else 'N/A'
        peor_categoria = fortalezas_debilidades['debilidades'][0]['categoria'] if fortalezas_debilidades['debilidades'] else 'N/A'
        subtopico_top = self._obtener_subtopico_top()
        
        return {
            "total_opiniones": total_opiniones,
            "porcentaje_positivo": round(pct_positivo, 1),
            "porcentaje_neutro": round(pct_neutro, 1),
            "porcentaje_negativo": round(pct_negativo, 1),
            "calificacion_promedio": round(calificacion_prom, 2),
            "mejor_categoria": mejor_categoria,
            "peor_categoria": peor_categoria,
            "subtopico_mas_mencionado": subtopico_top,
        }
    
    def _exportar_fortalezas(self) -> List[Dict[str, Any]]:
        """Exporta las fortalezas (categorías con más sentimiento positivo)."""
        return self._calcular_fortalezas_debilidades()['fortalezas']
    
    def _exportar_debilidades(self) -> List[Dict[str, Any]]:
        """Exporta las debilidades (categorías con más sentimiento negativo)."""
        return self._calcular_fortalezas_debilidades()['debilidades']
    
    def _exportar_resumenes(self) -> Dict[str, Any]:
        """Exporta los resúmenes inteligentes generados por LLM (Fase 06)."""
        if not self.resumenes_path.exists():
            return {}
        
        try:
            with open(self.resumenes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            resumenes_raw = data.get('resumenes', {})
            resultado = {}
            
            if 'descriptivo' in resumenes_raw:
                resultado['descriptivo'] = resumenes_raw['descriptivo']
            
            if 'estructurado' in resumenes_raw:
                resultado['estructurado'] = resumenes_raw['estructurado']
            
            if 'insights' in resumenes_raw:
                resultado['insights'] = resumenes_raw['insights']
            
            return resultado
        
        except Exception:
            return {}
    
    def _calcular_fortalezas_debilidades(self) -> Dict[str, List[Dict]]:
        """Calcula fortalezas y debilidades por categoría."""
        cat_sentimientos = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})
        
        for _, row in self.df.iterrows():
            try:
                cats_str = str(row['Categorias']).strip("[]'\"").replace("'", "").replace('"', '')
                cats_list = [c.strip() for c in cats_str.split(',') if c.strip()]
                sentimiento = row['Sentimiento']
                
                for cat in cats_list:
                    cat_sentimientos[cat][sentimiento] += 1
            except:
                continue
        
        fortalezas = []
        debilidades = []
        
        for cat, sents in cat_sentimientos.items():
            total = sum(sents.values())
            if total < 5:
                continue
            
            pct_pos = (sents['Positivo'] / total) * 100
            pct_neg = (sents['Negativo'] / total) * 100
            
            fortalezas.append({
                "categoria": cat,
                "porcentaje_positivo": round(pct_pos, 1),
                "total_menciones": total,
            })
            debilidades.append({
                "categoria": cat,
                "porcentaje_negativo": round(pct_neg, 1),
                "total_menciones": total,
            })
        
        fortalezas.sort(key=lambda x: x['porcentaje_positivo'], reverse=True)
        debilidades.sort(key=lambda x: x['porcentaje_negativo'], reverse=True)
        
        return {'fortalezas': fortalezas, 'debilidades': debilidades}
    
    def _obtener_subtopico_top(self) -> str:
        """Obtiene el subtópico más mencionado."""
        if 'Topico' not in self.df.columns:
            return 'N/A'
        
        todos_subtopicos = []
        for topico_str in self.df['Topico'].dropna():
            try:
                if topico_str and str(topico_str).strip() not in ['{}', 'nan', 'None', '']:
                    topico_dict = ast.literal_eval(str(topico_str))
                    todos_subtopicos.extend(topico_dict.values())
            except:
                continue
        
        if not todos_subtopicos:
            return 'N/A'
        
        return Counter(todos_subtopicos).most_common(1)[0][0]
