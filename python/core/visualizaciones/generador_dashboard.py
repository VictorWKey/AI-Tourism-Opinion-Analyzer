"""
Generador de Dashboard y Resumen Ejecutivo
===========================================
Sección 1: Dashboard (3 visualizaciones)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List
from .utils import COLORES, COLORES_SENTIMIENTO, ESTILOS, guardar_figura


class GeneradorDashboard:
    """Genera visualizaciones de dashboard ejecutivo."""
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '01_dashboard'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_todas(self) -> List[str]:
        """Genera todas las visualizaciones de dashboard."""
        generadas = []
        
        # 1.1 Resumen de validación
        if self.validador.puede_renderizar('resumen_validacion')[0]:
            self._generar_resumen_validacion()
            generadas.append('resumen_validacion')
        
        # 1.2 Dashboard ejecutivo
        if self.validador.puede_renderizar('dashboard_ejecutivo')[0]:
            self._generar_dashboard_ejecutivo()
            generadas.append('dashboard_ejecutivo')
        
        # 1.3 KPIs principales
        if self.validador.puede_renderizar('kpis_principales')[0]:
            self._generar_kpis_principales()
            generadas.append('kpis_principales')
        
        return generadas
    
    def _generar_resumen_validacion(self):
        """1.1 Resumen de Validación del Dataset."""
        resumen = self.validador.get_resumen()
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')
        ax.axis('off')
        
        # Título
        ax.text(0.5, 0.95, 'RESUMEN DE VALIDACIÓN DEL DATASET', 
                ha='center', **ESTILOS['titulo'])
        
        # Información general
        y_pos = 0.85
        info_lines = [
            f"📊 Total de opiniones analizadas: {resumen['total_opiniones']}",
            f"📅 Fechas válidas: {'✓ Sí' if resumen['tiene_fechas'] else '✗ No'}",
        ]
        
        if resumen['tiene_fechas']:
            info_lines.append(f"   └─ Rango temporal: {resumen['rango_temporal_dias']} días")
        
        info_lines.extend([
            f"🏷️  Categorías identificadas: {resumen['categorias_validas']}",
            f"🔍 Tópicos detectados: {'✓ Sí' if resumen['tiene_topicos'] else '✗ No'}",
            "",
            "DISTRIBUCIÓN DE SENTIMIENTOS:",
            f"   🟢 Positivo: {resumen['diversidad_sentimientos']['positivo']}",
            f"   ⚪ Neutro: {resumen['diversidad_sentimientos']['neutro']}",
            f"   🔴 Negativo: {resumen['diversidad_sentimientos']['negativo']}",
        ])
        
        for line in info_lines:
            ax.text(0.1, y_pos, line, fontsize=12, va='top', family='monospace')
            y_pos -= 0.05
        
        # Recomendaciones
        y_pos -= 0.05
        ax.text(0.1, y_pos, 'RECOMENDACIONES:', **ESTILOS['subtitulo'])
        y_pos -= 0.05
        
        recomendaciones = []
        if resumen['total_opiniones'] < 100:
            recomendaciones.append("⚠️  Dataset pequeño (<100). Algunas visualizaciones no serán generadas.")
        if not resumen['tiene_fechas']:
            recomendaciones.append("⚠️  Sin fechas válidas. Análisis temporal no disponible.")
        if not resumen['tiene_topicos']:
            recomendaciones.append("⚠️  Sin tópicos detectados. Análisis jerárquico limitado.")
        if resumen['total_opiniones'] >= 100:
            recomendaciones.append("✓ Volumen adecuado para análisis robusto.")
        
        for rec in recomendaciones:
            ax.text(0.1, y_pos, f"  • {rec}", fontsize=11, va='top')
            y_pos -= 0.05
        
        guardar_figura(fig, self.output_dir / 'resumen_validacion.png')
    
    def _generar_dashboard_ejecutivo(self):
        """1.2 Dashboard Ejecutivo (4 cuadrantes)."""
        fig = plt.figure(figsize=(16, 10), facecolor='white')
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Título principal
        fig.suptitle('DASHBOARD EJECUTIVO - ANÁLISIS DE OPINIONES TURÍSTICAS', 
                     **ESTILOS['titulo'], y=0.98)
        
        # Cuadrante 1: Distribución de sentimientos (donut)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_sentimientos_donut(ax1)
        
        # Cuadrante 2: Top 5 categorías
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_top_categorias(ax2)
        
        # Cuadrante 3: Fortalezas
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_fortalezas(ax3)
        
        # Cuadrante 4: Debilidades
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_debilidades(ax4)
        
        guardar_figura(fig, self.output_dir / 'dashboard_ejecutivo.png')
    
    def _plot_sentimientos_donut(self, ax):
        """Donut chart de sentimientos."""
        sentimientos = self.df['Sentimiento'].value_counts()
        colores = [COLORES_SENTIMIENTO.get(s, '#666666') for s in sentimientos.index]
        
        wedges, texts, autotexts = ax.pie(
            sentimientos.values, 
            labels=sentimientos.index,
            autopct='%1.1f%%',
            colors=colores,
            startangle=90,
            pctdistance=0.85,
            wedgeprops=dict(width=0.5, edgecolor='white')
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
        
        ax.set_title('Distribución de Sentimientos', **ESTILOS['subtitulo'], pad=20)
    
    def _plot_top_categorias(self, ax):
        """Top 5 categorías más mencionadas."""
        cats_counter = {}
        for cats in self.df['Categorias'].dropna():
            try:
                cats_str = str(cats).strip("[]'\"").replace("'", "").replace('"', '')
                cats_list = [c.strip() for c in cats_str.split(',') if c.strip()]
                for cat in cats_list:
                    cats_counter[cat] = cats_counter.get(cat, 0) + 1
            except:
                continue
        
        if not cats_counter:
            ax.text(0.5, 0.5, 'Sin datos de categorías', ha='center', va='center')
            ax.axis('off')
            return
        
        top_cats = sorted(cats_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        categorias, valores = zip(*top_cats)
        
        y_pos = range(len(categorias))
        bars = ax.barh(y_pos, valores, color=COLORES['primario'])
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categorias, fontsize=10)
        ax.set_xlabel('Menciones', fontsize=10)
        ax.set_title('Top 5 Categorías Mencionadas', **ESTILOS['subtitulo'], pad=20)
        ax.invert_yaxis()
        
        # Añadir valores en barras
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(val, i, f' {val}', va='center', fontsize=10, fontweight='bold')
    
    def _plot_fortalezas(self, ax):
        """Top 5 fortalezas (categorías con más sentimientos positivos)."""
        fortalezas = self._calcular_fortalezas_debilidades()['fortalezas']
        
        ax.axis('off')
        ax.set_title('✓ TOP 5 FORTALEZAS DEL DESTINO', 
                     fontsize=ESTILOS['subtitulo']['fontsize'], 
                     fontweight=ESTILOS['subtitulo']['fontweight'],
                     pad=20, color=COLORES['positivo'])
        
        y_pos = 0.85
        for i, (cat, pct) in enumerate(fortalezas[:5], 1):
            texto = f"{i}. {cat}: {pct:.1f}% positivas"
            ax.text(0.1, y_pos, texto, fontsize=11, va='top', 
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
            y_pos -= 0.15
    
    def _plot_debilidades(self, ax):
        """Top 5 debilidades (categorías con más sentimientos negativos)."""
        debilidades = self._calcular_fortalezas_debilidades()['debilidades']
        
        ax.axis('off')
        ax.set_title('✗ TOP 5 DEBILIDADES DEL DESTINO', 
                     fontsize=ESTILOS['subtitulo']['fontsize'],
                     fontweight=ESTILOS['subtitulo']['fontweight'],
                     pad=20, color=COLORES['negativo'])
        
        y_pos = 0.85
        for i, (cat, pct) in enumerate(debilidades[:5], 1):
            texto = f"{i}. {cat}: {pct:.1f}% negativas"
            ax.text(0.1, y_pos, texto, fontsize=11, va='top',
                   bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))
            y_pos -= 0.15
    
    def _calcular_fortalezas_debilidades(self) -> Dict:
        """Calcula fortalezas y debilidades por categoría."""
        from collections import defaultdict
        
        cat_sentimientos = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})
        
        for idx, row in self.df.iterrows():
            try:
                cats_str = str(row['Categorias']).strip("[]'\"").replace("'", "").replace('"', '')
                cats_list = [c.strip() for c in cats_str.split(',') if c.strip()]
                sentimiento = row['Sentimiento']
                
                for cat in cats_list:
                    cat_sentimientos[cat][sentimiento] += 1
            except:
                continue
        
        # Calcular porcentajes
        fortalezas = []
        debilidades = []
        
        for cat, sents in cat_sentimientos.items():
            total = sum(sents.values())
            if total < 5:  # Filtrar categorías con pocas menciones
                continue
            
            pct_pos = (sents['Positivo'] / total) * 100
            pct_neg = (sents['Negativo'] / total) * 100
            
            fortalezas.append((cat, pct_pos))
            debilidades.append((cat, pct_neg))
        
        fortalezas.sort(key=lambda x: x[1], reverse=True)
        debilidades.sort(key=lambda x: x[1], reverse=True)
        
        return {'fortalezas': fortalezas, 'debilidades': debilidades}
    
    def _generar_kpis_principales(self):
        """1.3 KPIs Principales (cards con métricas clave)."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor='white')
        ax.axis('off')
        
        # Título
        ax.text(0.5, 0.95, 'KPIS PRINCIPALES', ha='center', **ESTILOS['titulo'])
        
        # Calcular KPIs
        total_opiniones = len(self.df)
        pct_positivo = (self.df['Sentimiento'] == 'Positivo').sum() / total_opiniones * 100
        calificacion_prom = self.df['Calificacion'].mean() if 'Calificacion' in self.df.columns else 0
        
        fortalezas_debilidades = self._calcular_fortalezas_debilidades()
        mejor_categoria = fortalezas_debilidades['fortalezas'][0][0] if fortalezas_debilidades['fortalezas'] else 'N/A'
        peor_categoria = fortalezas_debilidades['debilidades'][0][0] if fortalezas_debilidades['debilidades'] else 'N/A'
        
        # Subtópico más mencionado
        subtopico_top = self._obtener_subtopico_top()
        
        # Posiciones de las cards (2 filas x 3 columnas)
        cards = [
            (0.15, 0.75, 'Total Opiniones', f'{total_opiniones}', COLORES['primario']),
            (0.5, 0.75, 'Sentimiento Positivo', f'{pct_positivo:.1f}%', COLORES['positivo']),
            (0.85, 0.75, 'Calificación Promedio', f'{calificacion_prom:.2f}/5', COLORES['secundario']),
            (0.15, 0.35, 'Mejor Categoría', mejor_categoria[:20], COLORES['positivo']),
            (0.5, 0.35, 'Categoría Problemática', peor_categoria[:20], COLORES['negativo']),
            (0.85, 0.35, 'Subtópico Top', subtopico_top[:20], COLORES['primario']),
        ]
        
        for x, y, titulo, valor, color in cards:
            # Rectángulo de fondo
            rect = mpatches.FancyBboxPatch(
                (x - 0.12, y - 0.12), 0.24, 0.24,
                boxstyle="round,pad=0.01", 
                facecolor=color, alpha=0.1,
                edgecolor=color, linewidth=2
            )
            ax.add_patch(rect)
            
            # Título
            ax.text(x, y + 0.08, titulo, ha='center', fontsize=11, fontweight='bold', color=COLORES['texto'])
            # Valor
            ax.text(x, y - 0.02, valor, ha='center', fontsize=16, fontweight='bold', color=color)
        
        guardar_figura(fig, self.output_dir / 'kpis_principales.png')
    
    def _obtener_subtopico_top(self) -> str:
        """Obtiene el subtópico más mencionado."""
        if 'Topico' not in self.df.columns:
            return 'N/A'
        
        from collections import Counter
        import ast
        
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
