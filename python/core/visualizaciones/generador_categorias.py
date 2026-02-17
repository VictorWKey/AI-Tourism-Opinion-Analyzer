"""
Generador de Análisis de Categorías
====================================
Sección 3: Categorías (visualizaciones esenciales)
"""

import ast
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
from pathlib import Path
from typing import List
from .utils import COLORES, COLORES_SENTIMIENTO, PALETA_CATEGORIAS, ESTILOS, guardar_figura
from .i18n import get_translator, get_sentiment_labels, get_category_labels, translate_categories


class GeneradorCategorias:
    """Genera visualizaciones de análisis de categorías."""
    
    def __init__(self, df: pd.DataFrame, validador, output_dir: Path):
        self.df = df
        self.validador = validador
        self.output_dir = output_dir / '03_categorias'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_todas(self) -> List[str]:
        """Genera visualizaciones esenciales de categorías."""
        generadas = []
        
        if self.validador.puede_renderizar('top_categorias')[0]:
            self._generar_top_categorias()
            generadas.append('top_categorias')
        
        if self.validador.puede_renderizar('sentimientos_por_categoria')[0]:
            self._generar_sentimientos_por_categoria()
            generadas.append('sentimientos_por_categoria')
        
        if self.validador.puede_renderizar('fortalezas_vs_debilidades')[0]:
            self._generar_fortalezas_vs_debilidades()
            generadas.append('fortalezas_vs_debilidades')
        
        if self.validador.puede_renderizar('radar_chart_360')[0]:
            if self._generar_radar_chart():  # Returns True if successfully created
                generadas.append('radar_chart_360')
        
        if self.validador.puede_renderizar('matriz_coocurrencia')[0]:
            self._generar_matriz_coocurrencia()
            generadas.append('matriz_coocurrencia')
        
        if self.validador.puede_renderizar('calificacion_por_categoria')[0]:
            self._generar_calificacion_por_categoria()
            generadas.append('calificacion_por_categoria')
        
        if self.validador.puede_renderizar('evolucion_categorias')[0]:
            self._generar_evolucion_categorias()
            generadas.append('evolucion_categorias')
        
        return generadas
    
    def _extraer_categorias_sentimientos(self):
        """Extrae categorías con sus sentimientos asociados."""
        cat_sentimientos = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})
        
        for idx, row in self.df.iterrows():
            try:
                cats_str = str(row['Categorias']).strip()
                # Excluir listas vacías explícitamente
                if cats_str in ['[]', '{}', '', 'nan', 'None']:
                    continue
                
                # Parse list string properly
                cats_list = ast.literal_eval(cats_str)
                if not isinstance(cats_list, list):
                    continue
                sentimiento = str(row['Sentimiento'])
                
                for cat in cats_list:
                    if sentimiento in cat_sentimientos[cat]:
                        cat_sentimientos[cat][sentimiento] += 1
            except:
                continue
        
        return cat_sentimientos
    
    def _generar_top_categorias(self):
        """3.1 Top Categorías Mencionadas."""
        cats_counter = {}
        for cats in self.df['Categorias'].dropna():
            try:
                cats_str = str(cats).strip()
                # Excluir listas vacías explícitamente
                if cats_str in ['[]', '{}', '']:
                    continue
                
                # Parse list string properly
                cats_list = ast.literal_eval(cats_str)
                if not isinstance(cats_list, list):
                    continue
                for cat in cats_list:
                    cats_counter[cat] = cats_counter.get(cat, 0) + 1
            except:
                continue
        
        if not cats_counter:
            return
        
        # Ordenar por frecuencia
        cats_ordenadas = sorted(cats_counter.items(), key=lambda x: x[1], reverse=True)
        categorias, valores = zip(*cats_ordenadas)
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORES['fondo'])
        
        t = get_translator()
        cat_labels = get_category_labels()
        categorias_display = translate_categories(list(categorias), cat_labels)
        
        y_pos = range(len(categorias_display))
        bars = ax.barh(y_pos, valores, color=PALETA_CATEGORIAS[:len(categorias_display)])
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categorias_display, fontsize=10)
        ax.set_xlabel(t('menciones'), **ESTILOS['etiquetas'])
        ax.set_title(t('categorias_mas_mencionadas'), **ESTILOS['titulo'])
        ax.invert_yaxis()
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Añadir valores
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(val + max(valores)*0.01, i, f'{val}', va='center', fontsize=9)
        
        guardar_figura(fig, self.output_dir / 'top_categorias.png')
    
    def _generar_sentimientos_por_categoria(self):
        """3.2 Sentimientos por Categoría (stacked bar 100%)."""
        cat_sent = self._extraer_categorias_sentimientos()
        
        # Filtrar categorías con pocas menciones
        cat_sent_filtrado = {k: v for k, v in cat_sent.items() if sum(v.values()) > 3}
        
        if not cat_sent_filtrado:
            return
        
        # Crear DataFrame
        df_cat = pd.DataFrame(cat_sent_filtrado).T
        df_cat_pct = df_cat.div(df_cat.sum(axis=1), axis=0) * 100
        df_cat_pct = df_cat_pct.sort_values('Positivo', ascending=True)
        
        t = get_translator()
        sent_labels = get_sentiment_labels()
        cat_labels = get_category_labels()
        
        # Translate column names for legend
        df_cat_pct = df_cat_pct.rename(columns=sent_labels)
        # Translate category names (index)
        df_cat_pct.index = translate_categories(df_cat_pct.index, cat_labels)
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(df_cat_pct) * 0.4)), facecolor=COLORES['fondo'])
        
        df_cat_pct.plot.barh(
            ax=ax,
            stacked=True,
            color=[COLORES_SENTIMIENTO[s] for s in ['Positivo', 'Neutro', 'Negativo'] if s in self.df['Sentimiento'].values],
            width=0.7
        )
        
        ax.set_xlabel(t('porcentaje'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('categoria'), **ESTILOS['etiquetas'])
        ax.set_title(t('sentimientos_por_categoria'), **ESTILOS['titulo'])
        ax.legend(title=t('sentimiento'), bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        guardar_figura(fig, self.output_dir / 'sentimientos_por_categoria.png')
    
    def _generar_fortalezas_vs_debilidades(self):
        """3.3 Fortalezas vs Debilidades (diverging bar chart)."""
        cat_sent = self._extraer_categorias_sentimientos()
        
        # Calcular porcentajes
        datos = []
        for cat, sents in cat_sent.items():
            total = sum(sents.values())
            if total < 5:
                continue
            
            pct_pos = (sents['Positivo'] / total) * 100
            pct_neg = (sents['Negativo'] / total) * 100
            datos.append({'categoria': cat, 'positivo': pct_pos, 'negativo': pct_neg})
        
        if not datos:
            return
        
        df_balance = pd.DataFrame(datos).sort_values('positivo', ascending=True)
        
        t = get_translator()
        cat_labels = get_category_labels()
        df_balance['categoria'] = translate_categories(df_balance['categoria'].tolist(), cat_labels)
        sent_labels = get_sentiment_labels()
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(df_balance) * 0.4)), facecolor=COLORES['fondo'])
        
        y_pos = range(len(df_balance))
        
        # Barras negativas (izquierda)
        ax.barh(y_pos, -df_balance['negativo'], color=COLORES['negativo'], alpha=0.7, label=sent_labels.get('Negativo', 'Negativo'))
        # Barras positivas (derecha)
        ax.barh(y_pos, df_balance['positivo'], color=COLORES['positivo'], alpha=0.7, label=sent_labels.get('Positivo', 'Positivo'))
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df_balance['categoria'], fontsize=10)
        ax.set_xlabel(t('negativo_positivo_axis'), **ESTILOS['etiquetas'])
        ax.set_title(t('fortalezas_vs_debilidades'), **ESTILOS['titulo'])
        ax.axvline(x=0, color=COLORES['texto'], linewidth=1)
        ax.legend(loc='lower right')
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        guardar_figura(fig, self.output_dir / 'fortalezas_vs_debilidades.png')
    
    def _generar_radar_chart(self) -> bool:
        """3.4 Radar Chart 360° del Destino.
        
        Returns:
            True if chart was successfully created, False otherwise.
        """
        cat_sent = self._extraer_categorias_sentimientos()
        
        # Filtrar categorías válidas
        cat_sent_filtrado = {k: v for k, v in cat_sent.items() if sum(v.values()) > 5}
        
        if len(cat_sent_filtrado) < 4:
            # Not enough categories with sufficient mentions
            return False
        
        # Preparar datos
        categorias_raw = list(cat_sent_filtrado.keys())
        cat_labels = get_category_labels()
        categorias = translate_categories(categorias_raw, cat_labels)
        pct_positivo = []
        pct_negativo = []
        
        for cat in categorias_raw:
            sents = cat_sent_filtrado[cat]
            total = sum(sents.values())
            pct_positivo.append((sents['Positivo'] / total) * 100)
            pct_negativo.append((sents['Negativo'] / total) * 100)
        
        # Cerrar el polígono
        pct_positivo.append(pct_positivo[0])
        pct_negativo.append(pct_negativo[0])
        
        # Ángulos
        num_vars = len(categorias)
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]
        
        t = get_translator()
        sent_labels = get_sentiment_labels()
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'), facecolor=COLORES['fondo'])
        
        # Plot líneas
        ax.plot(angles, pct_positivo, 'o-', linewidth=2, label=sent_labels.get('Positivo', 'Positivo'), color=COLORES['positivo'])
        ax.fill(angles, pct_positivo, alpha=0.25, color=COLORES['positivo'])
        
        ax.plot(angles, pct_negativo, 'o-', linewidth=2, label=sent_labels.get('Negativo', 'Negativo'), color=COLORES['negativo'])
        ax.fill(angles, pct_negativo, alpha=0.25, color=COLORES['negativo'])
        
        # Etiquetas
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categorias, size=9)
        ax.set_ylim(0, 100)
        ax.set_title(t('radar_chart_360'), **ESTILOS['titulo'], pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)
        
        guardar_figura(fig, self.output_dir / 'radar_chart_360.png')
        return True

    def _extraer_categorias_por_fila(self, row) -> List[str]:
        """Extrae lista de categorías de una fila."""
        cats = row.get('Categorias', '')
        if pd.isna(cats) or str(cats).strip() in ['', '[]', 'nan']:
            return []
        try:
            cats_str = str(cats).strip()
            # Parse list string properly
            cats_list = ast.literal_eval(cats_str)
            return cats_list if isinstance(cats_list, list) else []
        except:
            return []

    def _generar_matriz_coocurrencia(self):
        """3.5 Matriz de Co-ocurrencia de Categorías.
        
        Heatmap que muestra con qué frecuencia pares de categorías aparecen
        juntos en la misma opinión. Revela conexiones temáticas entre aspectos
        turísticos (ej. 'Gastronomía' y 'Servicio' mencionados juntos).
        """
        # Construir matriz de co-ocurrencia
        todas_cats = set()
        filas_cats = []
        for _, row in self.df.iterrows():
            cats = self._extraer_categorias_por_fila(row)
            if len(cats) >= 2:
                filas_cats.append(cats)
                todas_cats.update(cats)

        if len(todas_cats) < 3:
            return

        categorias_ordenadas = sorted(todas_cats)
        cat_labels = get_category_labels()
        categorias_ordenadas_display = translate_categories(categorias_ordenadas, cat_labels)
        cat_idx = {c: i for i, c in enumerate(categorias_ordenadas)}
        n = len(categorias_ordenadas)
        matriz = np.zeros((n, n), dtype=int)

        for cats in filas_cats:
            for i in range(len(cats)):
                for j in range(i + 1, len(cats)):
                    ci, cj = cat_idx[cats[i]], cat_idx[cats[j]]
                    matriz[ci][cj] += 1
                    matriz[cj][ci] += 1

        # Diagonal = auto-menciones (total por categoría)
        for _, row in self.df.iterrows():
            cats = self._extraer_categorias_por_fila(row)
            for cat in cats:
                if cat in cat_idx:
                    matriz[cat_idx[cat]][cat_idx[cat]] += 1

        fig, ax = plt.subplots(figsize=(max(10, n * 0.9), max(8, n * 0.75)), facecolor=COLORES['fondo'])

        t = get_translator()

        # Mask diagonal for cleaner look
        mask = np.eye(n, dtype=bool)
        sns.heatmap(
            matriz, mask=mask, annot=True, fmt='d', cmap='YlOrRd',
            xticklabels=categorias_ordenadas_display, yticklabels=categorias_ordenadas_display,
            ax=ax, linewidths=0.5, cbar_kws={'label': t('coocurrencias')},
            square=True
        )

        ax.set_title(t('matriz_coocurrencia'), **ESTILOS['titulo'], pad=15)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)

        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'matriz_coocurrencia.png')

    def _generar_calificacion_por_categoria(self):
        """3.6 Distribución de Calificaciones por Categoría (box plot).
        
        Box plot que muestra la distribución completa de calificaciones para
        cada categoría, incluyendo mediana, cuartiles y outliers. Más informativo
        que un simple promedio.
        """
        if 'Calificacion' not in self.df.columns:
            return

        # Expandir categorías
        datos = []
        for _, row in self.df.iterrows():
            cats = self._extraer_categorias_por_fila(row)
            calif = row.get('Calificacion', None)
            if calif is not None and not pd.isna(calif):
                for cat in cats:
                    datos.append({'Categoria': cat, 'Calificacion': float(calif)})

        if not datos:
            return

        df_exp = pd.DataFrame(datos)

        # Ordenar categorías por mediana de calificación descendente
        orden = df_exp.groupby('Categoria')['Calificacion'].median().sort_values(ascending=False).index
        # Limitar a top 12 para legibilidad
        orden = orden[:12]
        df_plot = df_exp[df_exp['Categoria'].isin(orden)]

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=COLORES['fondo'])

        t = get_translator()
        cat_labels = get_category_labels()

        bp = ax.boxplot(
            [df_plot[df_plot['Categoria'] == cat]['Calificacion'].values for cat in orden],
            labels=translate_categories(list(orden), cat_labels), patch_artist=True, vert=True, widths=0.6,
            medianprops=dict(color=COLORES['negativo'], linewidth=2),
            flierprops=dict(marker='o', markerfacecolor=COLORES['neutro'], markersize=4, alpha=0.5)
        )

        for i, patch in enumerate(bp['boxes']):
            patch.set_facecolor(PALETA_CATEGORIAS[i % len(PALETA_CATEGORIAS)])
            patch.set_alpha(0.7)

        ax.set_xlabel(t('categoria'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('calificacion'), **ESTILOS['etiquetas'])
        ax.set_title(t('calificacion_por_categoria'), **ESTILOS['titulo'])
        ax.set_ylim(0, 5.5)
        ax.set_xticklabels(translate_categories(list(orden), cat_labels), rotation=40, ha='right', fontsize=9)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Reference lines
        ax.axhline(y=df_exp['Calificacion'].mean(), color=COLORES['primario'],
                   linestyle='--', alpha=0.5, linewidth=1.5,
                   label=t('promedio_general', value=f'{df_exp["Calificacion"].mean():.2f}'))
        ax.legend(loc='lower right')

        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'calificacion_por_categoria.png')

    def _generar_evolucion_categorias(self):
        """3.7 Evolución Temporal de Categorías.
        
        Gráfico de áreas apiladas que muestra cómo evolucionan las menciones
        de cada categoría a lo largo del tiempo. Revela tendencias y
        estacionalidad temática.
        """
        if 'FechaEstadia' not in self.df.columns:
            return

        df_fechas = self.df[self.df['FechaEstadia'].notna()].copy()
        df_fechas['FechaEstadia'] = pd.to_datetime(df_fechas['FechaEstadia'], errors='coerce')
        df_fechas = df_fechas.dropna(subset=['FechaEstadia'])
        df_fechas['Mes'] = df_fechas['FechaEstadia'].dt.to_period('M')

        if len(df_fechas) < 20:
            return

        # Expandir categorías por mes
        datos = []
        for _, row in df_fechas.iterrows():
            cats = self._extraer_categorias_por_fila(row)
            for cat in cats:
                datos.append({'Mes': row['Mes'], 'Categoria': cat})

        if not datos:
            return

        df_exp = pd.DataFrame(datos)

        # Top 6 categorías por volumen total
        top_cats = df_exp['Categoria'].value_counts().head(6).index.tolist()
        df_top = df_exp[df_exp['Categoria'].isin(top_cats)]

        evol = df_top.groupby(['Mes', 'Categoria']).size().unstack(fill_value=0)
        evol = evol.reindex(columns=top_cats, fill_value=0)
        
        # Translate category column names for legend
        cat_labels = get_category_labels()
        evol = evol.rename(columns=cat_labels)

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=COLORES['fondo'])

        t = get_translator()

        evol.plot.area(ax=ax, color=PALETA_CATEGORIAS[:len(top_cats)], alpha=0.7, stacked=True)

        ax.set_xlabel(t('periodo'), **ESTILOS['etiquetas'])
        ax.set_ylabel(t('menciones'), **ESTILOS['etiquetas'])
        ax.set_title(t('evolucion_categorias'), **ESTILOS['titulo'])
        ax.legend(title=t('categoria'), bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        guardar_figura(fig, self.output_dir / 'evolucion_categorias.png')
