"""
Fase 02: Estadísticas Básicas del Dataset
==========================================
Genera estadísticas descriptivas básicas del dataset procesado
sin necesidad de modelos de ML. Exporta los resultados como
insights_textuales.json para que la UI pueda mostrarlos
inmediatamente después del procesamiento básico.

Datos generados:
- Total de registros
- Estadísticas de longitud de texto (promedio, mediana, min, max)
- Distribución temporal (si hay fechas)
- Distribución de calificación original (si existe en el dataset)
- Validación del dataset (columnas disponibles)
"""

import json
import logging
from datetime import datetime
from typing import Any

import pandas as pd

from config.config import ConfigDataset

logger = logging.getLogger(__name__)


class GeneradorEstadisticasBasicas:
    """
    Genera estadísticas descriptivas básicas del dataset procesado.
    No requiere modelos de ML — solo trabaja con los datos crudos
    procesados por la Fase 01.

    Exporta insights_textuales.json con la información básica disponible.
    Las fases posteriores (sentimiento, subjetividad, categorías, etc.)
    enriquecerán progresivamente este archivo cuando Phase 08 se ejecute.
    """

    def __init__(self):
        """Inicializa el generador de estadísticas básicas."""
        self.dataset_path = ConfigDataset.get_dataset_path()
        self.output_dir = ConfigDataset.get_visualizaciones_dir()
        self.df: pd.DataFrame | None = None

    def ya_procesado(self) -> bool:
        """
        Verifica si esta fase ya fue ejecutada.
        Revisa si existe el archivo insights_textuales.json.
        """
        try:
            insights_path = self.output_dir / 'insights_textuales.json'
            if not insights_path.exists():
                return False
            # Verify it has the basic_stats marker
            with open(insights_path, encoding='utf-8') as f:
                data = json.load(f)
            return data.get('estadisticas_basicas_generadas', False)
        except Exception:
            return False

    def procesar(self, forzar: bool = False):
        """
        Ejecuta la generación de estadísticas básicas.

        Args:
            forzar: Si es True, ejecuta incluso si ya fue procesado
        """
        if not forzar and self.ya_procesado():
            print('   ⏭️  Fase ya ejecutada previamente (omitiendo)')
            return

        # Cargar dataset procesado por Fase 01
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f'No se encontró el dataset procesado: {self.dataset_path}\n'
                'Ejecuta la Fase 01 (Procesamiento Básico) primero.'
            )

        self.df = pd.read_csv(self.dataset_path)
        total = len(self.df)

        # Generar todas las estadísticas básicas
        insights = {
            'fecha_generacion': datetime.now().isoformat(),
            'estadisticas_basicas_generadas': True,
            'validacion_dataset': self._generar_validacion(),
            'kpis': self._generar_kpis_basicos(),
            'fortalezas': [],
            'debilidades': [],
            'resumenes': {},
            'estadisticas_dataset': self._generar_estadisticas_dataset(),
        }

        # Crear directorio de salida si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Guardar insights
        output_path = self.output_dir / 'insights_textuales.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)

        print(f'✅ Fase 02 completada: {total} registros analizados')
        print(f'   📊 Estadísticas básicas exportadas a: {output_path}')

    def _generar_validacion(self) -> dict[str, Any]:
        """Genera el resumen de validación del dataset."""
        total = len(self.df)
        tiene_fechas = 'FechaEstadia' in self.df.columns
        tiene_calificacion = 'Calificacion' in self.df.columns

        # Calcular rango temporal si hay fechas
        rango_temporal_dias = 0
        if tiene_fechas:
            fechas = pd.to_datetime(self.df['FechaEstadia'], errors='coerce').dropna()
            if len(fechas) > 0:
                rango_temporal_dias = int((fechas.max() - fechas.min()).days)

        recomendaciones = []
        if total < 100:
            recomendaciones.append(
                'Dataset pequeño (<100 opiniones). Considera agregar más datos para análisis más robustos.'
            )
        if not tiene_fechas:
            recomendaciones.append(
                'No hay fechas válidas en el dataset. El análisis temporal no está disponible. '
                "Incluir una columna 'FechaEstadia' con fechas habilitaría las visualizaciones temporales."
            )
        if not tiene_calificacion:
            recomendaciones.append(
                "La columna 'Calificacion' no está en el dataset original. "
                'Será generada automáticamente por el modelo de sentimientos en la Fase 03.'
            )
        if total >= 100 and tiene_fechas:
            recomendaciones.append('Dataset con buen tamaño y datos temporales disponibles.')

        return {
            'total_opiniones': total,
            'tiene_fechas': tiene_fechas,
            'tiene_calificacion': tiene_calificacion,
            'rango_temporal_dias': rango_temporal_dias,
            'categorias_identificadas': 0,
            'tiene_topicos': False,
            'subtopicos_detectados': 0,
            'sentimientos': {
                'positivo': 0,
                'neutro': 0,
                'negativo': 0,
            },
            'recomendaciones': recomendaciones,
        }

    def _generar_kpis_basicos(self) -> dict[str, Any]:
        """Genera KPIs básicos disponibles sin modelos de ML."""
        total = len(self.df)
        calificacion_prom = 0.0

        if 'Calificacion' in self.df.columns:
            calificacion_prom = round(float(self.df['Calificacion'].mean()), 2)

        return {
            'total_opiniones': total,
            'porcentaje_positivo': 0,
            'porcentaje_neutro': 0,
            'porcentaje_negativo': 0,
            'calificacion_promedio': calificacion_prom,
            'mejor_categoria': 'N/A',
            'peor_categoria': 'N/A',
            'subtopico_mas_mencionado': 'N/A',
        }

    def _generar_estadisticas_dataset(self) -> dict[str, Any]:
        """
        Genera estadísticas descriptivas detalladas del dataset.
        Solo incluye datos que están disponibles sin modelos de ML.
        """
        total = len(self.df)
        stats: dict[str, Any] = {'total_registros': total}

        # ── Sentimiento (no disponible aún) ──
        if 'Sentimiento' in self.df.columns:
            sent_counts = self.df['Sentimiento'].value_counts()
            stats['sentimiento'] = {
                label: {
                    'cantidad': int(sent_counts.get(label, 0)),
                    'porcentaje': round(int(sent_counts.get(label, 0)) / total * 100, 1) if total else 0,
                }
                for label in ['Positivo', 'Neutro', 'Negativo']
            }
        else:
            stats['sentimiento'] = None

        # ── Subjetividad (no disponible aún) ──
        stats['subjetividad'] = None

        # ── Calificación (si existe en dataset original) ──
        if 'Calificacion' in self.df.columns:
            cal_counts = self.df['Calificacion'].value_counts().sort_index()
            stats['calificacion'] = {
                str(int(k)): {'cantidad': int(v), 'porcentaje': round(int(v) / total * 100, 1) if total else 0}
                for k, v in cal_counts.items()
            }
            stats['calificacion_promedio'] = round(float(self.df['Calificacion'].mean()), 2)
            stats['calificacion_mediana'] = float(self.df['Calificacion'].median())
        else:
            stats['calificacion'] = None

        # ── Categorías (no disponible aún) ──
        stats['categorias'] = None

        # ── Tópicos (no disponible aún) ──
        stats['topicos'] = None

        # ── Temporal ──
        if 'FechaEstadia' in self.df.columns:
            fechas = pd.to_datetime(self.df['FechaEstadia'], errors='coerce').dropna()
            if len(fechas) > 0:
                stats['temporal'] = {
                    'fecha_min': fechas.min().strftime('%Y-%m-%d'),
                    'fecha_max': fechas.max().strftime('%Y-%m-%d'),
                    'rango_dias': int((fechas.max() - fechas.min()).days),
                    'registros_con_fecha': len(fechas),
                    'registros_sin_fecha': int(total - len(fechas)),
                }
            else:
                stats['temporal'] = None
        else:
            stats['temporal'] = None

        # ── Longitud de texto ──
        if 'TituloReview' in self.df.columns:
            lengths = self.df['TituloReview'].dropna().str.len()
            if len(lengths) > 0:
                stats['longitud_texto'] = {
                    'promedio': int(lengths.mean()),
                    'mediana': int(lengths.median()),
                    'minimo': int(lengths.min()),
                    'maximo': int(lengths.max()),
                }
            else:
                stats['longitud_texto'] = None
        else:
            stats['longitud_texto'] = None

        return stats
