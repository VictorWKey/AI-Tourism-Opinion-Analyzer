"""
Fase 08: Generación de Visualizaciones
=======================================
Sistema inteligente y adaptativo de generación de visualizaciones profesionales.

Genera visualizaciones gráficas puras organizadas en 8 secciones:
1. Dashboard Ejecutivo (1 - 4 cuadrantes gráficos)
2. Análisis de Sentimientos (8 - donut, area, stacked bar, word clouds, etc.)
2b. Análisis de Subjetividad (3 - donut, stacked bar, stacked area)
3. Análisis de Categorías (7 - bar, stacked bar, diverging bar, radar, heatmap, box plot, area)
4. Análisis Jerárquico de Tópicos (3 - bar charts, heatmap)
5. Análisis Temporal (4 - bar, line, trend, seasonality heatmap)
6. Análisis de Texto (4 - word cloud, histogram, bigrams, trigrams)
7. Análisis Cruzado (5 - heatmap, grouped bar, scatter, violin, stacked bar)

Los datos textuales (KPIs, resúmenes LLM, fortalezas/debilidades, validación)
se exportan a insights_textuales.json para ser mostrados en la UI por separado.

Características:
- 🧠 Adaptativo: Valida volumen de datos antes de generar
- 📊 Solo gráficos puros: Sin texto renderizado como imagen
- 💾 Exporta a PNG de alta calidad (300 DPI)
- 📁 Organiza por carpetas temáticas
- 📋 Exporta insights textuales a JSON
"""

import pandas as pd
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')

from .visualizaciones.validador import ValidadorVisualizaciones
from .visualizaciones.generador_dashboard import GeneradorDashboard
from .visualizaciones.generador_sentimientos import GeneradorSentimientos
from .visualizaciones.generador_categorias import GeneradorCategorias
from .visualizaciones.generador_topicos import GeneradorTopicos
from .visualizaciones.generador_temporal import GeneradorTemporal
from .visualizaciones.generador_texto import GeneradorTexto
from .visualizaciones.generador_combinados import GeneradorCombinados
from .visualizaciones.generador_subjetividad import GeneradorSubjetividad
from .visualizaciones.exportador_insights import ExportadorInsights
from .visualizaciones.utils import configurar_estilo_grafico, configurar_tema


class GeneradorVisualizaciones:
    """
    Generador adaptativo de visualizaciones para análisis turístico.
    
    Valida el dataset y genera solo las visualizaciones viables según el volumen
    y características de los datos disponibles.
    """
    
    def __init__(self, dataset_path=None, output_dir=None):
        """
        Inicializa el generador de visualizaciones.
        
        Args:
            dataset_path: Ruta al dataset CSV procesado (default: from ConfigDataset)
            output_dir: Directorio de salida para las visualizaciones (default: from ConfigDataset)
        """
        from config.config import ConfigDataset
        self.dataset_path = Path(dataset_path) if dataset_path else ConfigDataset.get_dataset_path()
        self.output_dir = Path(output_dir) if output_dir else ConfigDataset.get_visualizaciones_dir()
        self.df = None
        self.validador = None
        self.visualizaciones_generadas = []
        self.visualizaciones_omitidas = []
    
    def ya_procesado(self):
        """
        Verifica si esta fase ya fue ejecutada.
        Revisa si existen los directorios light/dark con archivos PNG.
        """
        light_dir = self.output_dir / 'light'
        dark_dir = self.output_dir / 'dark'
        return (
            light_dir.exists() and len(list(light_dir.rglob('*.png'))) > 0
            and dark_dir.exists() and len(list(dark_dir.rglob('*.png'))) > 0
        )
    
    def _limpiar_visualizaciones_previas(self):
        """
        Elimina todas las visualizaciones anteriores para evitar confusión
        con resultados de datasets previos.
        """
        if self.output_dir.exists():
            print("\n🧹 Limpiando visualizaciones previas...")
            try:
                # Eliminar todo el contenido del directorio
                shutil.rmtree(self.output_dir)
                print("   ✓ Visualizaciones previas eliminadas")
            except Exception as e:
                print(f"   ⚠️  Error al limpiar visualizaciones: {e}")
        
        # Recrear el directorio limpio
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def procesar(self, forzar=False):
        """
        Pipeline principal de generación de visualizaciones.
        
        1. Carga y valida datos
        2. Configura estilo gráfico
        3. Crea estructura de carpetas
        4. Genera visualizaciones por sección
        5. Genera reporte final
        
        Args:
            forzar: Si es True, ejecuta incluso si ya fue procesado
        """
        if not forzar and self.ya_procesado():
            print("   ⏭️  Fase ya ejecutada previamente (omitiendo)")
            return
        print("\n" + "="*60)
        print("FASE 08: GENERACIÓN DE VISUALIZACIONES")
        print("="*60)
        
        # 0. Limpiar visualizaciones previas (importante para evitar confusión con datasets anteriores)
        self._limpiar_visualizaciones_previas()
        
        # 1. Cargar datos
        self._cargar_datos()
        
        # 2. Validar dataset
        self._validar_dataset()
        
        # 3. Configurar estilo
        configurar_estilo_grafico()
        
        # 4. Crear estructura de carpetas
        self._crear_carpetas()
        
        # 5. Generar visualizaciones por sección (light y dark)
        print("\n📊 Generando visualizaciones...")
        
        # Lista de secciones a generar (solo gráficos puros)
        secciones = [
            ('Dashboard', GeneradorDashboard),
            ('Sentimientos', GeneradorSentimientos),
            ('Subjetividad', GeneradorSubjetividad),
            ('Categorías', GeneradorCategorias),
            ('Tópicos', GeneradorTopicos),
            ('Temporal', GeneradorTemporal),
            ('Texto', GeneradorTexto),
            ('Análisis Cruzado', GeneradorCombinados),
        ]
        
        # Build a flat list of (theme, section_name, generator_class) for a single progress bar
        tareas = []
        for tema in ['light', 'dark']:
            for nombre, generador_class in secciones:
                tareas.append((tema, nombre, generador_class))
        
        tema_actual = None
        for tema, nombre, generador_class in tqdm(tareas, desc="   Progreso"):
            if tema != tema_actual:
                print(f"\n🎨 Generando versión [{tema}]...")
                configurar_tema(tema)
                configurar_estilo_grafico()
                tema_actual = tema
            tema_output_dir = self.output_dir / tema
            self._generar_seccion(nombre, generador_class, tema_output_dir)
        
        # Restaurar tema light como default
        configurar_tema('light')
        
        # 6. Exportar insights textuales a JSON (KPIs, resúmenes, fortalezas, etc.)
        self._exportar_insights()
        
        # 7. Generar reporte final
        self._generar_reporte_final()
        
        print("\n" + "="*60)
        print("✅ Visualizaciones generadas exitosamente")
        print(f"   • Total generadas: {len(self.visualizaciones_generadas)}")
        print(f"   • Total omitidas: {len(self.visualizaciones_omitidas)}")
        print(f"   • Versión light: {self.output_dir}/light/")
        print(f"   • Versión dark:  {self.output_dir}/dark/")
        print(f"   • Insights textuales: {self.output_dir}/insights_textuales.json")
        print(f"   • Reporte: {self.output_dir}/reporte_generacion.json")
        print("="*60)
    
    def _cargar_datos(self):
        """Carga el dataset procesado."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset no encontrado: {self.dataset_path}\n"
                "Asegúrate de ejecutar las Fases 01-07 primero."
            )
        
        self.df = pd.read_csv(self.dataset_path)
        print(f"\n📂 Dataset cargado: {len(self.df)} opiniones")
    
    def _validar_dataset(self):
        """Valida el dataset y muestra resumen."""
        self.validador = ValidadorVisualizaciones(self.df)
        resumen = self.validador.get_resumen()
        
        print(f"\n🔍 Validación del dataset:")
        print(f"   • Total opiniones: {resumen['total_opiniones']}")
        print(f"   • Fechas válidas: {'✓' if resumen['tiene_fechas'] else '✗ (análisis temporal no disponible)'}")
        print(f"   • Calificación: {'✓' if resumen['tiene_calificacion'] else '✗ (generada por el modelo de sentimientos)'}")
        
        if resumen['tiene_fechas']:
            print(f"   • Rango temporal: {resumen['rango_temporal_dias']} días")
        
        print(f"   • Categorías válidas: {resumen['categorias_validas']}")
        print(f"   • Tópicos detectados: {'✓' if resumen['tiene_topicos'] else '✗'}")
        print(f"   • Sentimientos:")
        print(f"     - Positivo: {resumen['diversidad_sentimientos']['positivo']}")
        print(f"     - Neutro: {resumen['diversidad_sentimientos']['neutro']}")
        print(f"     - Negativo: {resumen['diversidad_sentimientos']['negativo']}")
    
    def _crear_carpetas(self):
        """Crea la estructura de carpetas para las visualizaciones (light y dark)."""
        carpetas = [
            '01_dashboard',
            '02_sentimientos',
            '02b_subjetividad',
            '03_categorias',
            '04_topicos',
            '05_temporal',
            '06_texto',
            '07_combinados'
        ]
        
        for tema in ['light', 'dark']:
            tema_dir = self.output_dir / tema
            tema_dir.mkdir(parents=True, exist_ok=True)
            for carpeta in carpetas:
                (tema_dir / carpeta).mkdir(parents=True, exist_ok=True)
    
    def _generar_seccion(self, nombre: str, GeneradorClass, output_dir: Path = None):
        """
        Genera visualizaciones de una sección específica.
        
        Args:
            nombre: Nombre de la sección
            GeneradorClass: Clase del generador especializado
            output_dir: Directorio de salida (si None, usa self.output_dir)
        """
        target_dir = output_dir or self.output_dir
        print(f"\n   [{nombre}] Generando visualizaciones...")
        
        try:
            generador = GeneradorClass(self.df, self.validador, target_dir)
            generadas = generador.generar_todas()
            
            self.visualizaciones_generadas.extend(generadas)
            
            print(f"   ✓ {nombre}: {len(generadas)} visualizaciones generadas")
            
        except Exception as e:
            print(f"   ⚠️  Error en {nombre}: {e}")
    
    def _exportar_insights(self):
        """Exporta insights textuales a JSON para la UI."""
        print("\n   [Insights] Exportando datos textuales...")
        try:
            exportador = ExportadorInsights(self.df, self.validador, self.output_dir)
            nombre = exportador.exportar()
            print(f"   ✓ Insights textuales exportados: {nombre}")
        except Exception as e:
            print(f"   ⚠️  Error exportando insights: {e}")

    def _generar_reporte_final(self):
        """Genera reporte JSON con resumen de la generación."""
        resumen_validacion = self.validador.get_resumen()
        
        # Agrupar por sección
        por_seccion = {
            'dashboard': len([v for v in self.visualizaciones_generadas if 'dashboard' in v]),
            'sentimientos': len([v for v in self.visualizaciones_generadas if 'sentimiento' in v or 'wordcloud_p' in v or 'wordcloud_n' in v or 'wordcloud_ne' in v]),
            'categorias': len([v for v in self.visualizaciones_generadas if 'categoria' in v or 'radar' in v or 'fortaleza' in v or 'coocurrencia' in v or 'calificacion_por' in v or 'evolucion_categorias' in v]),
            'topicos': len([v for v in self.visualizaciones_generadas if 'topico' in v or 'subtopico' in v or 'distribucion_subtopicos' in v]),
            'temporal': len([v for v in self.visualizaciones_generadas if 'temporal' in v or 'volumen' in v or 'evolucion' in v or 'tendencia' in v or 'estacionalidad' in v]),
            'texto': len([v for v in self.visualizaciones_generadas if 'wordcloud_general' in v or 'longitud' in v or 'grama' in v]),
            'combinados': len([v for v in self.visualizaciones_generadas if 'subjetividad' in v or 'correlacion' in v or 'scatter' in v or 'distribucion_categorias' in v or 'calificacion_categoria' in v]),
        }
        
        reporte = {
            "fecha_generacion": datetime.now().isoformat(),
            "dataset": {
                "total_opiniones": int(resumen_validacion['total_opiniones']),
                "tiene_fechas": bool(resumen_validacion['tiene_fechas']),
                "tiene_calificacion": bool(resumen_validacion.get('tiene_calificacion', False)),
                "rango_temporal_dias": int(resumen_validacion['rango_temporal_dias']) if resumen_validacion['rango_temporal_dias'] is not None else 0,
                "categorias_identificadas": int(resumen_validacion['categorias_validas']),
                "cobertura_topicos": bool(resumen_validacion['tiene_topicos'])
            },
            "visualizaciones": {
                "total_generadas": len(self.visualizaciones_generadas),
                "total_omitidas": len(self.visualizaciones_omitidas),
                "por_seccion": por_seccion,
                "lista_generadas": self.visualizaciones_generadas
            },
            "omitidas": self.visualizaciones_omitidas,
            "recomendaciones": self._generar_recomendaciones(resumen_validacion)
        }
        
        # Guardar reporte
        reporte_path = self.output_dir / 'reporte_generacion.json'
        with open(reporte_path, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)
    
    def _generar_recomendaciones(self, resumen: Dict) -> List[str]:
        """Genera recomendaciones basadas en el dataset."""
        recomendaciones = []
        
        if resumen['total_opiniones'] < 100:
            recomendaciones.append(
                "Dataset pequeño (<100 opiniones). Algunas visualizaciones avanzadas no fueron generadas. "
                "Considera agregar más datos para análisis más robustos."
            )
        
        if not resumen['tiene_fechas']:
            recomendaciones.append(
                "No hay fechas válidas en el dataset. El análisis temporal no está disponible. "
                "Incluir una columna 'FechaEstadia' con fechas habilitaría las visualizaciones temporales."
            )
        
        if not resumen.get('tiene_calificacion', False):
            recomendaciones.append(
                "La columna 'Calificacion' no estaba en el dataset original. "
                "Fue generada automáticamente por el modelo de sentimientos (1-5 estrellas)."
            )
        
        if not resumen['tiene_topicos']:
            recomendaciones.append(
                "No se detectaron tópicos en el dataset. El análisis jerárquico está limitado. "
                "Ejecuta la Fase 06 para identificar tópicos antes de generar visualizaciones."
            )
        
        if resumen['total_opiniones'] >= 100 and resumen['tiene_fechas'] and resumen['tiene_topicos']:
            recomendaciones.append(
                "✓ Dataset completo y robusto. Todas las visualizaciones principales fueron generadas exitosamente."
            )
        
        if resumen['categorias_validas'] < 5:
            recomendaciones.append(
                "Pocas categorías identificadas. Esto puede limitar la granularidad del análisis por categoría."
            )
        
        return recomendaciones
