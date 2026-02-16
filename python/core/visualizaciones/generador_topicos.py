"""
Generador de Análisis de Tópicos
==================================
Sección 4: Tópicos (visualizaciones esenciales)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from pathlib import Path
from typing import List
import ast
from .utils import COLORES, COLORES_SENTIMIENTO, PALETA_CATEGORIAS, ESTILOS, guardar_figura


class GeneradorTopicos:
    """Genera visualizaciones de análisis de tópicos."""
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '04_topicos'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_todas(self) -> List[str]:
        """Genera visualizaciones esenciales de tópicos."""
        generadas = []
        
        if self.validador.puede_renderizar('top_subtopicos_mencionados')[0]:
            self._generar_top_subtopicos()
            generadas.append('top_subtopicos_mencionados')
        
        if self.validador.puede_renderizar('top_subtopicos_problematicos')[0]:
            self._generar_subtopicos_problematicos()
            generadas.append('top_subtopicos_problematicos')
        
        if self.validador.puede_renderizar('distribucion_subtopicos')[0]:
            self._generar_subtopicos_sentimiento_heatmap()
            generadas.append('distribucion_subtopicos')
        
        return generadas
    
    def _extraer_subtopicos_con_categoria(self):
        """Extrae subtópicos con su categoría padre."""
        subtopicos_data = []
        
        for idx, row in self.df.iterrows():
            topico_str = row.get('Topico', '{}')
            sentimiento = row.get('Sentimiento', 'Neutro')
            
            try:
                if topico_str and str(topico_str).strip() not in ['{}', 'nan', 'None', '']:
                    topico_dict = ast.literal_eval(str(topico_str))
                    for categoria, subtopico in topico_dict.items():
                        subtopicos_data.append({
                            'categoria': categoria,
                            'subtopico': subtopico,
                            'sentimiento': sentimiento
                        })
            except:
                continue
        
        return subtopicos_data
    
    def _generar_top_subtopicos(self):
        """4.1 Top 10 Sub-tópicos Más Mencionados."""
        subtopicos_data = self._extraer_subtopicos_con_categoria()
        
        if not subtopicos_data:
            return
        
        # Contar menciones
        contador = Counter([(d['categoria'], d['subtopico']) for d in subtopicos_data])
        top_10 = contador.most_common(10)
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORES['fondo'])
        
        etiquetas = [f"{cat}\n{sub}" for (cat, sub), _ in top_10]
        valores = [count for _, count in top_10]
        y_pos = range(len(etiquetas))
        
        bars = ax.barh(y_pos, valores, color=PALETA_CATEGORIAS[:len(etiquetas)])
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(etiquetas, fontsize=9)
        ax.set_xlabel('Menciones', **ESTILOS['etiquetas'])
        ax.set_title('Top 10 Sub-tópicos Más Mencionados', **ESTILOS['titulo'])
        ax.invert_yaxis()
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Añadir valores
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(val + max(valores)*0.01, i, f'{val}', va='center', fontsize=9)
        
        guardar_figura(fig, self.output_dir / 'top_subtopicos_mencionados.png')
    
    def _generar_subtopicos_problematicos(self):
        """4.2 Top 10 Sub-tópicos Problemáticos."""
        subtopicos_data = self._extraer_subtopicos_con_categoria()
        
        if not subtopicos_data:
            return
        
        # Agrupar por subtópico y calcular % negativo
        from collections import defaultdict
        
        subtopico_sentimientos = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0, 'total': 0})
        
        for data in subtopicos_data:
            key = f"{data['categoria']} | {data['subtopico']}"
            subtopico_sentimientos[key][data['sentimiento']] += 1
            subtopico_sentimientos[key]['total'] += 1
        
        # Calcular % negativo y filtrar
        problematicos = []
        for subtopico, sents in subtopico_sentimientos.items():
            if sents['total'] < 3:  # Filtrar subtópicos con pocas menciones
                continue
            pct_neg = (sents['Negativo'] / sents['total']) * 100
            if pct_neg > 0:
                problematicos.append({
                    'subtopico': subtopico,
                    'pct_negativo': pct_neg,
                    'total': sents['total']
                })
        
        if not problematicos:
            return
        
        # Ordenar por % negativo
        problematicos.sort(key=lambda x: x['pct_negativo'], reverse=True)
        top_10 = problematicos[:10]
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORES['fondo'])
        
        etiquetas = [d['subtopico'] for d in top_10]
        valores = [d['pct_negativo'] for d in top_10]
        y_pos = range(len(etiquetas))
        
        bars = ax.barh(y_pos, valores, color=COLORES['negativo'], alpha=0.7)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(etiquetas, fontsize=9)
        ax.set_xlabel('% Sentimiento Negativo', **ESTILOS['etiquetas'])
        ax.set_title('Top 10 Sub-tópicos Problemáticos', **ESTILOS['titulo'])
        ax.invert_yaxis()
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Añadir valores
        for i, d in enumerate(top_10):
            ax.text(d['pct_negativo'] + 2, i, f"{d['pct_negativo']:.1f}% (n={d['total']})", 
                   va='center', fontsize=9)
        
        guardar_figura(fig, self.output_dir / 'top_subtopicos_problematicos.png')

    def _generar_subtopicos_sentimiento_heatmap(self):
        """4.3 Heatmap de Sentimiento por Sub-tópico.
        
        Muestra una matriz de calor con los sub-tópicos principales (filas)
        y su distribución de sentimiento (columnas), facilitando la
        identificación rápida de temas conflictivos vs satisfactorios.
        """
        subtopicos_data = self._extraer_subtopicos_con_categoria()

        if not subtopicos_data:
            return

        from collections import defaultdict

        # Agrupar por subtópico
        subtopico_sent = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})
        for data in subtopicos_data:
            label = f"{data['categoria']} | {data['subtopico']}"
            subtopico_sent[label][data['sentimiento']] += 1

        # Filtrar por volumen y tomar top 15
        subtopico_sent = {k: v for k, v in subtopico_sent.items() if sum(v.values()) >= 3}
        if len(subtopico_sent) < 3:
            return

        # Ordenar por total de menciones
        ordenados = sorted(subtopico_sent.items(), key=lambda x: sum(x[1].values()), reverse=True)[:15]

        etiquetas = [k for k, _ in ordenados]
        sentimientos_orden = ['Positivo', 'Neutro', 'Negativo']
        matriz = [[v.get(s, 0) for s in sentimientos_orden] for _, v in ordenados]

        df_heatmap = pd.DataFrame(matriz, index=etiquetas, columns=sentimientos_orden)

        # Normalizar por filas (porcentaje)
        df_pct = df_heatmap.div(df_heatmap.sum(axis=1), axis=0) * 100

        fig, ax = plt.subplots(figsize=(10, max(6, len(etiquetas) * 0.5)), facecolor=COLORES['fondo'])

        # Crear colormap personalizado: rojo → blanco → verde
        from matplotlib.colors import LinearSegmentedColormap
        cmap = LinearSegmentedColormap.from_list(
            'sent', [COLORES['negativo'], COLORES['fondo'], COLORES['positivo']]
        )

        sns.heatmap(
            df_pct, annot=df_heatmap.values, fmt='d', cmap=cmap,
            center=50, ax=ax, linewidths=0.5,
            cbar_kws={'label': '% del total'},
            vmin=0, vmax=100
        )

        ax.set_title('Sentimiento por Sub-tópico (color: %, valor: conteo)', **ESTILOS['titulo'], pad=15)
        ax.set_xticklabels(sentimientos_orden, fontsize=10)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)

        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'distribucion_subtopicos.png')
