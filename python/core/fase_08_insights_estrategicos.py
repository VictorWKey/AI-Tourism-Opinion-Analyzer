"""
Fase 08: Strategic Insights Generation
=======================================
Generates a single comprehensive strategic insight by combining:
- All dataset statistics and metrics (sentiment, subjectivity, categories, topics, etc.)
- The structured summary from Phase 07
- KPIs, strengths, weaknesses, and validation data

Uses a single LLM call to produce a professional, data-driven strategic analysis
with actionable recommendations for tourism decision-makers.
"""

import pandas as pd
import json
import os
import ast
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import Counter, defaultdict
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

from .llm_provider import get_llm, crear_chain
from .llm_utils import RetryConfig

logger = logging.getLogger(__name__)


class GeneradorInsightsEstrategicos:
    """
    Generates a single comprehensive strategic insight by synthesizing all pipeline data:
    - Dataset statistics (Phase 02)
    - Sentiment distribution (Phase 03)
    - Subjectivity distribution (Phase 04)
    - Category classification (Phase 05)
    - Hierarchical topics (Phase 06)
    - Structured summary (Phase 07)

    Produces one holistic strategic analysis via a single LLM call.
    """

    def __init__(self):
        from config.config import ConfigDataset
        self.dataset_path = str(ConfigDataset.get_dataset_path())
        self.shared_dir = ConfigDataset.get_shared_dir()
        self.scores_path = str(self.shared_dir / 'categorias_scores.json')
        self.resumenes_path = self.shared_dir / 'resumenes.json'
        self.output_path = self.shared_dir / 'insights_estrategicos.json'

        self.df = None
        self.scores = None
        self.structured_summary = None
        self.llm = None

    # ── Data Loading ─────────────────────────────────────────────────

    def _cargar_datos(self):
        """Load the enriched dataset and all supporting data."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        self.df = pd.read_csv(self.dataset_path)

        required = ['TituloReview', 'Sentimiento', 'Subjetividad']
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            raise KeyError(
                f"Required columns missing: {', '.join(missing)}\n"
                "   Ensure Phases 01, 03 and 04 have been executed."
            )

        # Load category scores
        if os.path.exists(self.scores_path):
            with open(self.scores_path, 'r', encoding='utf-8') as f:
                self.scores = json.load(f)
        else:
            self.scores = {}

        # Load structured summary from Phase 07
        if self.resumenes_path.exists():
            with open(self.resumenes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            resumenes = data.get('resumenes', {})
            self.structured_summary = resumenes.get('estructurado', None)
        else:
            self.structured_summary = None

        print(f"   • Dataset loaded: {len(self.df)} reviews")
        print(f"   • Category scores: {len(self.scores)} records")
        print(f"   • Structured summary: {'available' if self.structured_summary else 'not available'}")

    # ── Metrics Compilation ──────────────────────────────────────────

    def _compile_all_metrics(self) -> str:
        """
        Compile ALL statistics and metrics into a formatted markdown context
        that mirrors (and extends) what the Metrics screen displays.
        """
        total = len(self.df)
        sections: List[str] = []

        # ── 1. Overview KPIs ──
        pct_pos = round((self.df['Sentimiento'] == 'Positivo').sum() / total * 100, 1)
        pct_neu = round((self.df['Sentimiento'] == 'Neutro').sum() / total * 100, 1)
        pct_neg = round((self.df['Sentimiento'] == 'Negativo').sum() / total * 100, 1)
        avg_rating = round(float(self.df['Calificacion'].mean()), 2) if 'Calificacion' in self.df.columns else 'N/A'
        median_rating = float(self.df['Calificacion'].median()) if 'Calificacion' in self.df.columns else 'N/A'

        sections.append(
            f"## Overview KPIs\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Total Reviews | {total} |\n"
            f"| Positive Sentiment | {pct_pos}% |\n"
            f"| Neutral Sentiment | {pct_neu}% |\n"
            f"| Negative Sentiment | {pct_neg}% |\n"
            f"| Avg Rating | {avg_rating} / 5 |\n"
            f"| Median Rating | {median_rating} |"
        )

        # ── 2. Sentiment Distribution ──
        sent_counts = self.df['Sentimiento'].value_counts()
        rows = []
        for label in ['Positivo', 'Neutro', 'Negativo']:
            cnt = int(sent_counts.get(label, 0))
            pct = round(cnt / total * 100, 1) if total else 0
            rows.append(f"| {label} | {cnt} | {pct}% |")
        sections.append(
            f"## Sentiment Distribution\n"
            f"| Sentiment | Count | Percentage |\n|---|---|---|\n" + "\n".join(rows)
        )

        # ── 3. Subjectivity Distribution ──
        if 'Subjetividad' in self.df.columns:
            subj_counts = self.df['Subjetividad'].value_counts()
            rows = []
            for label in sorted(subj_counts.index):
                cnt = int(subj_counts.get(label, 0))
                pct = round(cnt / total * 100, 1) if total else 0
                rows.append(f"| {label} | {cnt} | {pct}% |")
            sections.append(
                f"## Subjectivity Distribution\n"
                f"| Type | Count | Percentage |\n|---|---|---|\n" + "\n".join(rows)
            )

        # ── 4. Rating Distribution ──
        if 'Calificacion' in self.df.columns:
            cal_counts = self.df['Calificacion'].value_counts().sort_index()
            rows = []
            for k, v in cal_counts.items():
                cnt = int(v)
                pct = round(cnt / total * 100, 1) if total else 0
                rows.append(f"| {int(k)} stars | {cnt} | {pct}% |")
            sections.append(
                f"## Rating Distribution\n"
                f"| Rating | Count | Percentage |\n|---|---|---|\n" + "\n".join(rows) +
                f"\n\nAvg: {avg_rating}, Median: {median_rating}"
            )

        # ── 5. Category Distribution & Sentiment per Category ──
        if 'Categorias' in self.df.columns:
            cat_counter: Counter = Counter()
            cat_sentimientos: Dict[str, Dict[str, int]] = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})

            for _, row in self.df.iterrows():
                try:
                    cats_raw = str(row['Categorias']).strip()
                    if cats_raw in ['[]', '{}', '', 'nan', 'None']:
                        continue
                    cats_list = ast.literal_eval(cats_raw) if cats_raw.startswith('[') else [c.strip() for c in cats_raw.split(',') if c.strip()]
                    sentiment = row['Sentimiento']
                    cat_counter.update(cats_list)
                    for cat in cats_list:
                        cat_sentimientos[cat][sentiment] += 1
                except Exception:
                    continue

            total_assignments = sum(cat_counter.values())
            cats_per_review = round(total_assignments / total, 2) if total else 0

            rows = []
            for cat, count in cat_counter.most_common():
                pct = round(count / total * 100, 1)
                rows.append(f"| {cat} | {count} | {pct}% |")
            sections.append(
                f"## Category Distribution\n"
                f"Categories per review (avg): {cats_per_review} | Unique categories: {len(cat_counter)} | Total assignments: {total_assignments}\n\n"
                f"| Category | Reviews | Percentage |\n|---|---|---|\n" + "\n".join(rows)
            )

            # Sentiment per category (strengths & weaknesses)
            rows_strength = []
            rows_weakness = []
            for cat in cat_counter:
                s = cat_sentimientos[cat]
                cat_total = sum(s.values())
                if cat_total < 3:
                    continue
                pct_p = round(s['Positivo'] / cat_total * 100, 1)
                pct_n = round(s['Negativo'] / cat_total * 100, 1)
                rows_strength.append((cat, pct_p, cat_total))
                rows_weakness.append((cat, pct_n, cat_total))

            rows_strength.sort(key=lambda x: x[1], reverse=True)
            rows_weakness.sort(key=lambda x: x[1], reverse=True)

            strength_rows = [f"| {cat} | {pct}% | {tot} |" for cat, pct, tot in rows_strength[:10]]
            weakness_rows = [f"| {cat} | {pct}% | {tot} |" for cat, pct, tot in rows_weakness[:10]]

            sections.append(
                f"## Strengths (Top Categories by Positive Sentiment)\n"
                f"| Category | % Positive | Total Mentions |\n|---|---|---|\n" + "\n".join(strength_rows)
            )
            sections.append(
                f"## Weaknesses (Top Categories by Negative Sentiment)\n"
                f"| Category | % Negative | Total Mentions |\n|---|---|---|\n" + "\n".join(weakness_rows)
            )

        # ── 6. Top Sub-topics ──
        if 'Topico' in self.df.columns:
            subtopic_counter: Counter = Counter()
            subtopic_sentiment: Dict[str, Dict[str, int]] = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})

            for _, row in self.df.iterrows():
                try:
                    topico_str = str(row.get('Topico', '')).strip()
                    if topico_str in ['{}', 'nan', 'None', '']:
                        continue
                    topico_dict = ast.literal_eval(topico_str)
                    sentiment = row['Sentimiento']
                    for subtopic in topico_dict.values():
                        if subtopic:
                            subtopic_counter[subtopic] += 1
                            subtopic_sentiment[subtopic][sentiment] += 1
                except Exception:
                    continue

            if subtopic_counter:
                rows = []
                for name, count in subtopic_counter.most_common(20):
                    pct = round(count / total * 100, 1)
                    s = subtopic_sentiment[name]
                    stotal = sum(s.values())
                    pct_p = round(s['Positivo'] / stotal * 100, 1) if stotal else 0
                    pct_n = round(s['Negativo'] / stotal * 100, 1) if stotal else 0
                    rows.append(f"| {name} | {count} | {pct}% | {pct_p}% | {pct_n}% |")
                sections.append(
                    f"## Top Sub-topics\n"
                    f"| Sub-topic | Mentions | % of Total | % Positive | % Negative |\n|---|---|---|---|---|\n" +
                    "\n".join(rows)
                )

        # ── 7. Temporal Analysis ──
        if 'FechaEstadia' in self.df.columns:
            fechas = pd.to_datetime(self.df['FechaEstadia'], errors='coerce').dropna()
            if len(fechas) > 0:
                sections.append(
                    f"## Temporal Analysis\n"
                    f"| Metric | Value |\n|---|---|\n"
                    f"| Date Range | {fechas.min().strftime('%Y-%m-%d')} to {fechas.max().strftime('%Y-%m-%d')} |\n"
                    f"| Total Days | {(fechas.max() - fechas.min()).days} |\n"
                    f"| Reviews with Date | {len(fechas)} |\n"
                    f"| Reviews without Date | {total - len(fechas)} |"
                )

        # ── 8. Text Length Statistics ──
        if 'TituloReview' in self.df.columns:
            lengths = self.df['TituloReview'].dropna().str.len()
            if len(lengths) > 0:
                sections.append(
                    f"## Review Text Length\n"
                    f"| Metric | Value |\n|---|---|\n"
                    f"| Average | {int(lengths.mean())} chars |\n"
                    f"| Median | {int(lengths.median())} chars |\n"
                    f"| Min | {int(lengths.min())} chars |\n"
                    f"| Max | {int(lengths.max())} chars |"
                )

        return "\n\n".join(sections)

    def _compile_structured_summary(self) -> str:
        """Format the structured summary for LLM context."""
        if not self.structured_summary:
            return "(No structured summary available from Phase 07)"

        parts = []

        # Global summary
        if self.structured_summary.get('global'):
            parts.append(f"### Global Structured Summary\n{self.structured_summary['global']}")

        # Per-category summaries
        if self.structured_summary.get('por_categoria'):
            for cat, text in self.structured_summary['por_categoria'].items():
                parts.append(f"### Category: {cat}\n{text}")

        return "\n\n".join(parts) if parts else "(Structured summary is empty)"

    # ── LLM Invocation ───────────────────────────────────────────────

    def _inicializar_llm(self):
        """Initialize the LLM provider."""
        self.llm = get_llm()

    def _invocar_llm_con_retry(
        self,
        template: str,
        input_data: dict,
        max_retries: int = 3,
        descripcion: str = "LLM operation"
    ) -> str:
        """Invoke LLM with retry logic."""
        config = RetryConfig(max_retries=max_retries)
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                chain = crear_chain(template)
                result = chain.invoke(input_data)

                if result and str(result).strip():
                    return str(result)

                raise ValueError("Empty LLM response")

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed for {descripcion}: {str(e)[:100]}"
                )
                if attempt < max_retries:
                    delay = config.get_delay(attempt)
                    time.sleep(delay)

        logger.error(f"All retries exhausted for {descripcion}: {last_error}")
        return ""

    # ── Insight Generation ───────────────────────────────────────────

    def _generar_insight_global(
        self,
        metrics_context: str,
        summary_context: str,
    ) -> str:
        """Generate a single comprehensive strategic insight report."""
        analysis_language = os.environ.get('ANALYSIS_LANGUAGE', 'es')

        if analysis_language == 'en':
            template = """You are a chief tourism strategy officer producing the executive strategic report for a destination.

## COMPLETE DATASET METRICS AND STATISTICS
{metricas}

## STRUCTURED SUMMARY (ALL CATEGORIES)
{resumen_estructurado}

CRITICAL INSTRUCTIONS:
1. ONLY use data from the metrics above - NEVER invent or assume numbers
2. EVERY claim must cite specific percentages, counts, or ratings from the data
3. If a metric isn't in the data, DO NOT mention it
4. Extract actual baseline values from the metrics for KPI recommendations

EXAMPLE OF GOOD DATA-DRIVEN WRITING:
❌ BAD: "The destination shows positive sentiment"
✅ GOOD: "67.3% of reviews express positive sentiment (402 of 597 total reviews)"

❌ BAD: "Food is a competitive advantage"
✅ GOOD: "Food & Dining leads with 78.4% positive sentiment (156 mentions, avg rating 4.3/5)"

❌ BAD: "Baseline: 75%"
✅ GOOD: "Baseline: 67.3% positive sentiment (from current data)"

Synthesize ALL the above data into a comprehensive STRATEGIC INSIGHTS REPORT (800-1200 words).

Your report MUST contain:

### Executive Summary
Start with exact numbers: "Analysis of [X] reviews shows [Y%] positive, [Z%] negative sentiment..."
Include: total reviews, sentiment breakdown (%), average rating from the data
NO generic statements - only data-backed observations

### Overall Performance Dashboard
- Sentiment health: State exact % positive, neutral, negative
- Ratings: State actual avg and median ratings from the metrics
- Subjectivity: State actual distribution % from the data
- Alignment: Compare sentiment % vs rating patterns with specific numbers

### Cross-Category Strategic Analysis
For EACH category mentioned:
- State exact sentiment % (positive/negative)
- State number of mentions
- State average rating if available
- Reference specific sub-topics from the data

Rank top 3 strengths and top 3 weaknesses by actual sentiment %.
Example format: "Service (85.2% positive, 234 mentions, 4.5 avg rating)"

### Priority Action Matrix
Each action must reference specific data points:
- **URGENT:** "Address [Category] with only [X%] positive sentiment and [Y] negative mentions"
- Link each action to a specific weak metric from the data

### Risk Register
Each risk must cite specific problematic metrics:
- Risk: "[Category name] dissatisfaction"
- Evidence: "[X%] negative sentiment, [Y] mentions, rating [Z]/5"
- Calculate probability from % negative sentiment
- Calculate impact from volume of mentions

### KPI Dashboard Recommendations
For EACH KPI, provide the ACTUAL baseline from current data:
- KPI: "Positive sentiment rate"
  Baseline: [X%] (from current dataset)
  Target: [X+10%]
- Extract values directly from the metrics tables above

This is a board-level strategic document. Use an executive-report tone with precise data."""
        else:
            template = """Eres el director de estrategia turística produciendo el reporte estratégico ejecutivo para un destino.

## MÉTRICAS Y ESTADÍSTICAS COMPLETAS DEL DATASET
{metricas}

## RESUMEN ESTRUCTURADO (TODAS LAS CATEGORÍAS)
{resumen_estructurado}

INSTRUCCIONES CRÍTICAS:
1. SOLO usa datos de las métricas anteriores - NUNCA inventes o asumas números
2. CADA afirmación debe citar porcentajes, conteos o calificaciones específicas de los datos
3. Si una métrica no está en los datos, NO la menciones
4. Extrae valores base reales de las métricas para las recomendaciones de KPIs

EJEMPLO DE BUENA ESCRITURA BASADA EN DATOS:
❌ MAL: "El destino muestra sentimiento positivo"
✅ BIEN: "67.3% de las reseñas expresan sentimiento positivo (402 de 597 reseñas totales)"

❌ MAL: "La comida es una ventaja competitiva"
✅ BIEN: "Gastronomía lidera con 78.4% de sentimiento positivo (156 menciones, calificación promedio 4.3/5)"

❌ MAL: "Valor base: 75%"
✅ BIEN: "Valor base: 67.3% sentimiento positivo (de los datos actuales)"

Sintetiza TODOS los datos anteriores en un REPORTE DE INSIGHTS ESTRATÉGICOS integral (800-1200 palabras).

Tu reporte DEBE contener:

### Resumen Ejecutivo
Inicia con números exactos: "Análisis de [X] reseñas muestra [Y%] positivas, [Z%] negativas..."
Incluye: total de reseñas, desglose de sentimiento (%), calificación promedio de los datos
SIN declaraciones genéricas - solo observaciones respaldadas por datos

### Panel de Rendimiento General
- Salud del sentimiento: Indica % exacto positivo, neutral, negativo
- Calificaciones: Indica promedio y mediana reales de las métricas
- Subjetividad: Indica distribución % real de los datos
- Alineación: Compara % de sentimiento vs patrones de calificación con números específicos

### Análisis Estratégico Transversal
Para CADA categoría mencionada:
- Indica % exacto de sentimiento (positivo/negativo)
- Indica número de menciones
- Indica calificación promedio si está disponible
- Referencia subtemas específicos de los datos

Clasifica top 3 fortalezas y top 3 debilidades por % real de sentimiento.
Formato ejemplo: "Servicio (85.2% positivo, 234 menciones, calificación promedio 4.5)"

### Matriz de Acciones Prioritarias
Cada acción debe referenciar puntos de datos específicos:
- **URGENTE:** "Atender [Categoría] con solo [X%] sentimiento positivo y [Y] menciones negativas"
- Vincula cada acción a una métrica débil específica de los datos

### Registro de Riesgos
Cada riesgo debe citar métricas problemáticas específicas:
- Riesgo: "Insatisfacción en [Nombre categoría]"
- Evidencia: "[X%] sentimiento negativo, [Y] menciones, calificación [Z]/5"
- Calcula probabilidad desde % sentimiento negativo
- Calcula impacto desde volumen de menciones

### Recomendaciones de Panel de KPIs
Para CADA KPI, proporciona el valor base REAL de los datos actuales:
- KPI: "Tasa de sentimiento positivo"
  Valor base: [X%] (del dataset actual)
  Objetivo: [X+10%]
- Extrae valores directamente de las tablas de métricas anteriores

Este es un documento estratégico de nivel directivo. Usa un tono de reporte ejecutivo con datos precisos."""

        result = self._invocar_llm_con_retry(
            template=template,
            input_data={
                "metricas": metrics_context,
                "resumen_estructurado": summary_context,
            },
            max_retries=3,
            descripcion="strategic insights",
        )

        return result.strip() if result else "[Could not generate strategic insights]"

    # ── Orchestration ────────────────────────────────────────────────

    def _generar_insights(self) -> Dict[str, Any]:
        """Orchestrate the insights generation pipeline."""
        print("\n   Compiling all metrics and statistics...")
        metrics_context = self._compile_all_metrics()

        print("   Preparing structured summary context...")
        summary_context = self._compile_structured_summary()

        print("\n   Initializing LLM...")
        self._inicializar_llm()

        print("   Generating comprehensive strategic insights report...")
        global_insights = self._generar_insight_global(metrics_context, summary_context)

        result = {
            "metadata": {
                "fecha_generacion": datetime.now().isoformat(),
                "total_reviews": len(self.df),
                "structured_summary_available": self.structured_summary is not None,
                "phase": "08_strategic_insights",
            },
            "insights": {
                "global": global_insights,
            },
        }

        return result

    def _guardar_resultado(self, resultado: Dict):
        """Save the insights result to JSON."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print(f"\n   ✓ Strategic insights saved to: {self.output_path}")

    def ya_procesado(self):
        """Check if this phase has already been executed."""
        return self.output_path.exists()

    def procesar(self, forzar: bool = False):
        """
        Execute the strategic insights generation pipeline.

        Args:
            forzar: If True, re-run even if output already exists
        """
        if not forzar and self.ya_procesado():
            print("   ⏭️  Phase already executed (skipping)")
            return

        print("   Starting strategic insights generation...")

        # 1. Load all data
        self._cargar_datos()

        # 2. Generate insights
        resultado = self._generar_insights()

        # 3. Save result
        self._guardar_resultado(resultado)

        print(f"\n✅ Strategic insights generated successfully")
        print(f"   • Comprehensive report: generated")
