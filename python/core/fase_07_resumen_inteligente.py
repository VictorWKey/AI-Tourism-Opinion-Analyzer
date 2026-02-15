"""
Fase 07: Resumen Inteligente de Reseñas
========================================
Genera resúmenes estratégicos seleccionando reseñas representativas
y usando LLM para crear insights profesionales para turismólogos.
"""

import pandas as pd
import json
import os
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
from datetime import datetime
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')

# Importar proveedor de LLM unificado y utilidades robustas
from .llm_provider import get_llm, crear_chain, LLMRetryExhaustedError
from .llm_utils import RetryConfig

# Configurar logging
logger = logging.getLogger(__name__)


class ResumidorInteligente:
    """
    Genera resúmenes estratégicos de reseñas turísticas usando:
    1. Selección inteligente de reseñas representativas
    2. Categoría dominante basada en probabilidades del modelo
    3. Resúmenes recursivos por categoría usando LLM
    4. Múltiples formatos de resumen configurables
    """
    
    def __init__(self, top_n_subtopicos: int = 3, incluir_neutros: bool = False):
        """
        Inicializa el resumidor.
        
        Args:
            top_n_subtopicos: Número máximo de subtópicos a incluir por categoría.
                             Solo se seleccionan los N subtópicos con más reseñas.
                             Default: 3 (reduce significativamente el uso de tokens)
            incluir_neutros: Si True, incluye reseñas con sentimiento Neutro.
                            Si False, solo usa Positivo y Negativo (más eficiente).
                            Default: False (recomendado para resúmenes accionables)
        """
        from config.config import ConfigDataset
        self.dataset_path = str(ConfigDataset.get_dataset_path())
        self.scores_path = str(ConfigDataset.get_shared_dir() / 'categorias_scores.json')
        self.output_path = ConfigDataset.get_shared_dir() / 'resumenes.json'
        self.top_n_subtopicos = top_n_subtopicos
        self.incluir_neutros = incluir_neutros
        
        self.df = None
        self.scores = None
        self.llm = None
        
    def _cargar_datos(self):
        """Carga el dataset y las probabilidades de categorías."""
        # Cargar dataset
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset no encontrado: {self.dataset_path}")
        
        self.df = pd.read_csv(self.dataset_path)
        
        # Verificar columnas requeridas
        columnas_requeridas = ['TituloReview', 'Sentimiento', 'Subjetividad']
        columnas_faltantes = [col for col in columnas_requeridas if col not in self.df.columns]
        
        if columnas_faltantes:
            raise KeyError(
                f"Columnas requeridas no encontradas: {', '.join(columnas_faltantes)}\n"
                "   Asegúrate de ejecutar las fases previas:\n"
                "   - Fase 01: Procesamiento Básico (agrega TituloReview)\n"
                "   - Fase 03: Análisis de Sentimientos (agrega Sentimiento)\n"
                "   - Fase 04: Análisis de Subjetividad (agrega Subjetividad)"
            )
        
        # Cargar scores de categorías
        if not os.path.exists(self.scores_path):
            raise FileNotFoundError(
                f"Probabilidades de categorías no encontradas: {self.scores_path}\n"
                "Asegúrate de ejecutar primero la Fase 05 (Clasificación de Categorías)."
            )
        
        with open(self.scores_path, 'r', encoding='utf-8') as f:
            self.scores = json.load(f)
        
        # Verificar si hay scores válidos
        if not self.scores or len(self.scores) == 0:
            print("   ⚠️  Advertencia: No se encontraron probabilidades de categorías")
            print("      El archivo existe pero está vacío. Esto puede ocurrir si:")
            print("      - El modelo de categorías no pudo procesar las reseñas")
            print("      - Todas las categorías tienen probabilidad 0")
        
        print(f"   • Dataset cargado: {len(self.df)} reseñas")
        print(f"   • Probabilidades cargadas: {len(self.scores)} registros")
        
        # Advertir si falta la columna Topico (fase 06)
        if 'Topico' not in self.df.columns:
            print("   ⚠️  Advertencia: Columna 'Topico' no encontrada")
            print("      Los resúmenes no incluirán información de subtópicos")
            print("      Ejecuta la Fase 06 (Análisis Jerárquico de Tópicos) para mejorar los resúmenes")
    
    def _obtener_categoria_dominante(self, idx: int) -> Optional[str]:
        """
        Obtiene la categoría dominante basada en las probabilidades del modelo.
        
        Args:
            idx: Índice de la reseña
            
        Returns:
            Nombre de la categoría con mayor probabilidad, o None si no hay
        """
        if str(idx) not in self.scores:
            return None
        
        categoria_scores = self.scores[str(idx)]
        
        if not categoria_scores:
            return None
        
        # Obtener categoría con mayor probabilidad
        categoria_dominante = max(categoria_scores.items(), key=lambda x: x[1])
        
        return categoria_dominante[0]
    
    def _obtener_topico_para_categoria(self, idx: int, categoria: str) -> Optional[str]:
        """
        Obtiene el tópico específico de una categoría para una reseña.
        
        Args:
            idx: Índice de la reseña
            categoria: Nombre de la categoría
            
        Returns:
            Nombre del tópico para esa categoría, o None si no hay
        """
        # Verificar si la columna Topico existe
        if 'Topico' not in self.df.columns:
            return None
        
        topico_str = self.df.loc[idx, 'Topico']
        
        if pd.isna(topico_str) or topico_str == '{}':
            return None
        
        try:
            # Parsear el diccionario string
            import ast
            topico_dict = ast.literal_eval(topico_str)
            return topico_dict.get(categoria, None)
        except:
            return None
    
    # ── Configurable thresholds ──────────────────────────────────────
    # Minimum number of reviews that must survive each filter stage.
    # When a filter would reduce the pool below this threshold the
    # filter is automatically relaxed (see _seleccionar_reseñas_representativas).
    MIN_RESEÑAS_POR_ETAPA = 5

    def _seleccionar_reseñas_representativas(self) -> pd.DataFrame:
        """
        Selects representative reviews using an **adaptive filtering strategy**.

        The method applies a sequence of increasingly selective filters.
        After every filter it checks whether enough reviews remain; if the
        pool falls below ``MIN_RESEÑAS_POR_ETAPA`` the filter is rolled back
        or relaxed automatically.  This guarantees that the method always
        returns a non-empty result for any dataset size (≥ 1 review).

        Filtering stages
        ─────────────────
        1. Subjectivity filter   – prefer 'Mixta', fall back to all
        2. Sentiment filter      – exclude 'Neutro' (configurable)
        3. Dominant-category     – from ``categorias_scores.json``
        4. Relevant topic        – from ``Topico`` column (optional)
        5. Top-N subtopic prune  – keep only most frequent subtopics
        6. De-duplication        – one review per Sentiment × Category (× Topic)

        Returns
        -------
        pd.DataFrame
            Subset of ``self.df`` enriched with helper columns
            ``CategoriaDominante``, ``TopicoRelevante`` and ``Longitud``.
        """
        total = len(self.df)
        print(f"\n   Seleccionando reseñas representativas ({total} reseñas)...")

        # ── helpers ────────────────────────────────────────────────────
        def _hay_suficientes(df: pd.DataFrame) -> bool:
            return len(df) >= self.MIN_RESEÑAS_POR_ETAPA

        filtros_aplicados: List[str] = []
        filtros_relajados: List[str] = []

        # ── Stage 1: Subjectivity ──────────────────────────────────────
        df_filtrado = self.df[self.df['Subjetividad'] == 'Mixta'].copy()

        if _hay_suficientes(df_filtrado):
            filtros_aplicados.append("Subjetividad = 'Mixta'")
        else:
            # Fall back: include 'Subjetiva' too
            df_filtrado = self.df[
                self.df['Subjetividad'].isin(['Mixta', 'Subjetiva'])
            ].copy()

            if _hay_suficientes(df_filtrado):
                filtros_aplicados.append("Subjetividad ∈ {'Mixta', 'Subjetiva'}")
                filtros_relajados.append(
                    f"Subjetividad: se incluyeron Subjetivas (solo {self.df['Subjetividad'].eq('Mixta').sum()} Mixtas)"
                )
            else:
                # Fall back: use everything
                df_filtrado = self.df.copy()
                filtros_relajados.append(
                    "Subjetividad: sin filtrar (dataset muy pequeño)"
                )

        # ── Stage 2: Sentiment ─────────────────────────────────────────
        if not self.incluir_neutros:
            df_sin_neutros = df_filtrado[
                df_filtrado['Sentimiento'].isin(['Positivo', 'Negativo'])
            ]

            if _hay_suficientes(df_sin_neutros):
                eliminadas = len(df_filtrado) - len(df_sin_neutros)
                df_filtrado = df_sin_neutros
                filtros_aplicados.append(f"Sentimiento ≠ 'Neutro' (−{eliminadas})")
            else:
                filtros_relajados.append(
                    f"Sentimiento: se mantuvieron Neutros ({len(df_filtrado) - len(df_sin_neutros)} neutros preservados)"
                )

        # ── Stage 3: Dominant category ─────────────────────────────────
        df_filtrado['CategoriaDominante'] = df_filtrado.index.map(
            lambda idx: self._obtener_categoria_dominante(idx)
        )

        df_con_categoria = df_filtrado[df_filtrado['CategoriaDominante'].notna()]

        if _hay_suficientes(df_con_categoria):
            df_filtrado = df_con_categoria
            filtros_aplicados.append("Tiene categoría dominante")
        else:
            # Assign a fallback category so the pipeline can continue
            df_filtrado['CategoriaDominante'] = df_filtrado['CategoriaDominante'].fillna('General')
            filtros_relajados.append(
                f"Categoría: {df_filtrado['CategoriaDominante'].eq('General').sum()} reseñas asignadas a 'General'"
            )

        # ── Stage 4: Relevant topic ───────────────────────────────────
        topicos_relevantes = []
        for idx, row in df_filtrado.iterrows():
            topico = self._obtener_topico_para_categoria(idx, row['CategoriaDominante'])
            topicos_relevantes.append(topico if topico else 'General')
        df_filtrado = df_filtrado.copy()
        df_filtrado['TopicoRelevante'] = topicos_relevantes

        # ── Stage 5: Top-N subtopic pruning ────────────────────────────
        df_top = self._filtrar_top_subtopicos(df_filtrado)

        if _hay_suficientes(df_top):
            df_filtrado = df_top
            filtros_aplicados.append(f"Top {self.top_n_subtopicos} subtópicos por categoría")
        else:
            filtros_relajados.append(
                "Subtópicos: sin filtro top-N (insuficientes reseñas)"
            )

        # ── Stage 6: Length & date helpers ─────────────────────────────
        df_filtrado['Longitud'] = df_filtrado['TituloReview'].str.len()

        tiene_fecha = 'FechaEstadia' in df_filtrado.columns
        if tiene_fecha:
            df_filtrado['FechaEstadia'] = pd.to_datetime(
                df_filtrado['FechaEstadia'], errors='coerce'
            )

        # ── Stage 7: De-duplication (one per combination) ─────────────
        # Build groupby columns adaptively
        columnas_grupo = ['Sentimiento', 'CategoriaDominante']
        tiene_topicos_reales = (df_filtrado['TopicoRelevante'] != 'General').any()
        if tiene_topicos_reales:
            columnas_grupo.append('TopicoRelevante')

        reseñas_seleccionadas = []
        agrupaciones = df_filtrado.groupby(columnas_grupo, dropna=False)

        for _, grupo in agrupaciones:
            sort_cols = ['Longitud']
            sort_asc = [False]
            if tiene_fecha:
                sort_cols.append('FechaEstadia')
                sort_asc.append(False)

            grupo_ordenado = grupo.sort_values(by=sort_cols, ascending=sort_asc)
            reseñas_seleccionadas.append(grupo_ordenado.iloc[0])

        df_seleccionado = pd.DataFrame(reseñas_seleccionadas)

        # ── Final safety net ──────────────────────────────────────────
        # If STILL empty after all relaxations, take the longest reviews
        if len(df_seleccionado) == 0:
            n_fallback = min(10, len(self.df))
            df_seleccionado = self.df.copy()
            df_seleccionado['Longitud'] = df_seleccionado['TituloReview'].str.len()
            df_seleccionado = df_seleccionado.nlargest(n_fallback, 'Longitud')
            df_seleccionado['CategoriaDominante'] = 'General'
            df_seleccionado['TopicoRelevante'] = 'General'
            filtros_relajados.append(
                f"Fallback: se usaron las {n_fallback} reseñas más largas sin filtrar"
            )

        # ── Report ────────────────────────────────────────────────────
        print(f"   ✓ Reseñas seleccionadas: {len(df_seleccionado)} de {total}")
        print(f"   ✓ Reducción: {total - len(df_seleccionado)} reseñas filtradas")

        if filtros_aplicados:
            print(f"   • Filtros aplicados ({len(filtros_aplicados)}):")
            for f in filtros_aplicados:
                print(f"     ✓ {f}")

        if filtros_relajados:
            print(f"   • Filtros relajados ({len(filtros_relajados)}):")
            for f in filtros_relajados:
                print(f"     ⚠️  {f}")

        print(f"   • Por categoría:")
        for categoria, count in df_seleccionado['CategoriaDominante'].value_counts().items():
            if 'TopicoRelevante' in df_seleccionado.columns:
                n_sub = df_seleccionado[
                    df_seleccionado['CategoriaDominante'] == categoria
                ]['TopicoRelevante'].nunique()
                print(f"     - {categoria}: {count} reseñas, {n_sub} subtópicos")
            else:
                print(f"     - {categoria}: {count} reseñas")

        return df_seleccionado
    
    def _filtrar_top_subtopicos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra el DataFrame para quedarse solo con los top N subtópicos 
        más frecuentes de cada categoría.
        
        Args:
            df: DataFrame con columnas 'CategoriaDominante' y 'TopicoRelevante'
            
        Returns:
            DataFrame filtrado con solo los subtópicos más representativos.
            Returns the original df unchanged if it is empty or has no valid
            categories/topics.
        """
        if len(df) == 0:
            return df

        if 'CategoriaDominante' not in df.columns or 'TopicoRelevante' not in df.columns:
            return df

        dfs_filtrados = []
        
        for categoria in df['CategoriaDominante'].unique():
            # Filtrar reseñas de esta categoría
            df_categoria = df[df['CategoriaDominante'] == categoria].copy()
            
            # Contar frecuencia de subtópicos
            conteo_subtopicos = df_categoria['TopicoRelevante'].value_counts()
            
            # Seleccionar top N subtópicos
            top_subtopicos = conteo_subtopicos.head(self.top_n_subtopicos).index.tolist()
            
            # Filtrar solo esos subtópicos
            df_top = df_categoria[df_categoria['TopicoRelevante'].isin(top_subtopicos)]
            
            dfs_filtrados.append(df_top)
        
        if not dfs_filtrados:
            return df

        # Concatenar todos los DataFrames filtrados
        df_resultado = pd.concat(dfs_filtrados, ignore_index=False)
        
        return df_resultado
    
    def _inicializar_llm(self):
        """Inicializa el modelo LLM para generación de resúmenes."""
        self.llm = get_llm()
    
    def _generar_resumen_categoria(
        self, 
        reseñas: List[Dict], 
        categoria: str,
        tipo_resumen: str
    ) -> str:
        """
        Genera un resumen para una categoría específica.
        
        Args:
            reseñas: Lista de reseñas de la categoría
            categoria: Nombre de la categoría
            tipo_resumen: 'descriptivo', 'estructurado' o 'insights'
            
        Returns:
            Texto del resumen
        """
        # Preparar contexto de reseñas
        contexto_reseñas = ""
        for i, reseña in enumerate(reseñas, 1):
            sentimiento = reseña.get('Sentimiento', 'Desconocido')
            topico = reseña.get('TopicoRelevante', 'General')
            texto = reseña.get('TituloReview', '')[:500]  # Limitar longitud
            
            contexto_reseñas += f"\n[Reseña {i}] Sentimiento: {sentimiento} | Subtópico: {topico}\n{texto}\n"
        
        # Plantillas según tipo de resumen
        if tipo_resumen == 'descriptivo':
            template = """Eres un experto turismólogo analizando opiniones de turistas.

Categoría: {categoria}

Reseñas representativas:
{reseñas}

Genera un resumen narrativo y descriptivo (150-200 palabras) que sintetice las experiencias de los turistas en esta categoría. 
Describe qué aspectos valoran positivamente, qué les disgusta, y qué experiencias reportan.
Usa un tono profesional pero accesible."""

        elif tipo_resumen == 'estructurado':
            template = """Eres un experto turismólogo analizando opiniones de turistas.

Categoría: {categoria}

Reseñas representativas:
{reseñas}

Genera un resumen estructurado con los siguientes apartados:
1. **Aspectos Positivos**: Qué valoran los turistas
2. **Aspectos Negativos**: Principales quejas y problemas
3. **Subtemas Identificados**: Menciona los subtópicos específicos encontrados

Máximo 200 palabras. Usa un tono profesional."""

        else:  # insights
            template = """Eres un turismólogo profesional realizando análisis estratégico.

Categoría: {categoria}

Reseñas representativas:
{reseñas}

Genera un análisis con insights estratégicos para profesionales del turismo (150-200 palabras):
1. **Hallazgos clave**: Patrones importantes identificados
2. **Oportunidades de mejora**: Áreas específicas que requieren atención
3. **Recomendaciones estratégicas**: Acciones concretas para gestores turísticos

Enfócate en información accionable y relevante para la toma de decisiones."""

        # Usar el proveedor de LLM con reintentos
        resumen = self._invocar_llm_con_retry(
            template=template,
            input_data={
                "categoria": categoria,
                "reseñas": contexto_reseñas
            },
            max_retries=3,
            descripcion=f"resumen {tipo_resumen} para {categoria}"
        )
        
        return resumen.strip() if resumen else f"[No se pudo generar resumen para {categoria}]"
    
    def _invocar_llm_con_retry(
        self,
        template: str,
        input_data: dict,
        max_retries: int = 3,
        descripcion: str = "operación LLM"
    ) -> str:
        """
        Invoca el LLM con reintentos y manejo de errores.
        
        Args:
            template: Template del prompt
            input_data: Datos de entrada
            max_retries: Número de reintentos
            descripcion: Descripción para logs
            
        Returns:
            Respuesta del LLM o string vacío
        """
        config = RetryConfig(max_retries=max_retries)
        ultimo_error = None
        
        for intento in range(max_retries + 1):
            try:
                chain = crear_chain(template)
                resultado = chain.invoke(input_data)
                
                if resultado and str(resultado).strip():
                    return str(resultado)
                
                raise ValueError("Respuesta vacía del LLM")
                
            except Exception as e:
                ultimo_error = e
                logger.warning(
                    f"Intento {intento + 1}/{max_retries + 1} falló para {descripcion}: {str(e)[:100]}"
                )
                
                if intento < max_retries:
                    delay = config.get_delay(intento)
                    time.sleep(delay)
        
        logger.error(f"Todos los reintentos fallaron para {descripcion}: {ultimo_error}")
        return ""
    
    def _generar_resumen_global(
        self, 
        resumenes_por_categoria: Dict[str, str],
        tipo_resumen: str
    ) -> str:
        """
        Genera un resumen global combinando los resúmenes por categoría.
        
        Args:
            resumenes_por_categoria: Diccionario {categoria: resumen}
            tipo_resumen: 'descriptivo', 'estructurado' o 'insights'
            
        Returns:
            Texto del resumen global
        """
        # Preparar contexto
        contexto = ""
        for categoria, resumen in resumenes_por_categoria.items():
            contexto += f"\n**{categoria}**:\n{resumen}\n"
        
        # Plantillas según tipo
        if tipo_resumen == 'descriptivo':
            template = """Eres un experto turismólogo sintetizando opiniones turísticas.

Resúmenes por categoría:
{resumenes}

Genera un resumen global descriptivo y cohesivo (250-300 palabras) que integre las experiencias de los turistas 
en todas las categorías analizadas. Presenta una visión general de la percepción turística del destino.
Tono profesional y narrativo."""

        elif tipo_resumen == 'estructurado':
            template = """Eres un experto turismólogo sintetizando opiniones turísticas.

Resúmenes por categoría:
{resumenes}

Genera un resumen ejecutivo estructurado (250-300 palabras):
1. **Resumen General**: Panorama global de la percepción turística
2. **Fortalezas del Destino**: Categorías mejor valoradas
3. **Áreas de Oportunidad**: Categorías con más quejas
4. **Aspectos Destacados**: Menciones específicas importantes

Tono profesional y conciso."""

        else:  # insights
            template = """Eres un turismólogo profesional realizando análisis estratégico integral.

Resúmenes por categoría:
{resumenes}

Genera un análisis estratégico global (300-350 palabras) orientado a gestores turísticos:
1. **Diagnóstico General**: Estado actual de la percepción turística
2. **Insights Críticos**: Hallazgos más importantes y tendencias detectadas
3. **Prioridades de Acción**: Áreas que requieren intervención urgente
4. **Recomendaciones Estratégicas**: Plan de acción con acciones concretas

Enfócate en información accionable para la toma de decisiones de gestión turística."""

        # Usar el proveedor de LLM con reintentos
        resumen_global = self._invocar_llm_con_retry(
            template=template,
            input_data={"resumenes": contexto},
            max_retries=3,
            descripcion=f"resumen global {tipo_resumen}"
        )
        
        return resumen_global.strip() if resumen_global else "[No se pudo generar resumen global]"
    
    def _generar_resumenes(
        self, 
        df_seleccionado: pd.DataFrame,
        tipos_resumen: List[str]
    ) -> Dict:
        """
        Genera resúmenes recursivos por categoría y globales.
        
        Args:
            df_seleccionado: DataFrame con reseñas seleccionadas
            tipos_resumen: Lista de tipos ['descriptivo', 'estructurado', 'insights']
            
        Returns:
            Diccionario con todos los resúmenes generados
        """
        print("\n   Generando resúmenes con LLM...")
        
        # Inicializar LLM
        self._inicializar_llm()
        
        resultado = {
            "metadata": {
                "fecha_generacion": datetime.now().isoformat(),
                "total_reseñas_dataset": len(self.df),
                "reseñas_seleccionadas": len(df_seleccionado),
                "tipos_resumen": tipos_resumen,
                "top_subtopicos_por_categoria": self.top_n_subtopicos,
                "incluir_neutros": self.incluir_neutros,
                "sentimientos_incluidos": ['Positivo', 'Neutro', 'Negativo'] if self.incluir_neutros else ['Positivo', 'Negativo'],
                "reduccion_porcentaje": round(
                    (1 - len(df_seleccionado) / len(self.df)) * 100, 2
                )
            },
            "resumenes": {}
        }
        
        # Agrupar reseñas por categoría dominante
        reseñas_por_categoria = defaultdict(list)
        
        for _, row in df_seleccionado.iterrows():
            categoria = row['CategoriaDominante']
            reseñas_por_categoria[categoria].append(row.to_dict())
        
        # Calcular total de tareas para la barra de progreso
        total_tareas = len(tipos_resumen) * (len(reseñas_por_categoria) + 1)  # +1 por resumen global
        
        # Generar resúmenes para cada tipo solicitado con una sola barra de progreso
        with tqdm(total=total_tareas, desc="   Progreso") as pbar:
            for tipo in tipos_resumen:
                print(f"   • Generando resumen tipo: {tipo}")
                
                resultado["resumenes"][tipo] = {
                    "por_categoria": {},
                    "global": None
                }
                
                # Resúmenes por categoría
                resumenes_categoria = {}
                for categoria, reseñas in reseñas_por_categoria.items():
                    resumen = self._generar_resumen_categoria(
                        reseñas, 
                        categoria, 
                        tipo
                    )
                    
                    resumenes_categoria[categoria] = resumen
                    resultado["resumenes"][tipo]["por_categoria"][categoria] = resumen
                    pbar.update(1)
                
                # Resumen global
                resumen_global = self._generar_resumen_global(
                    resumenes_categoria, 
                    tipo
                )
                resultado["resumenes"][tipo]["global"] = resumen_global
                pbar.update(1)
        
        return resultado
    
    def _guardar_resultado(self, resultado: Dict):
        """
        Guarda el resultado en JSON.
        
        Args:
            resultado: Diccionario con los resúmenes generados
        """
        # Crear carpeta shared si no existe
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print(f"\n   ✓ Resúmenes guardados en: {self.output_path}")
    
    def ya_procesado(self):
        """
        Verifica si esta fase ya fue ejecutada.
        Revisa si existe el archivo de resúmenes.
        """
        return self.output_path.exists()
    
    def procesar(self, tipos_resumen: Optional[List[str]] = None, forzar: bool = False):
        """
        Ejecuta el pipeline completo de generación de resúmenes.
        
        Args:
            tipos_resumen: Lista de tipos de resumen a generar.
                          Opciones: 'descriptivo', 'estructurado', 'insights'
                          Por defecto: ['descriptivo', 'estructurado', 'insights']
            forzar: Si es True, ejecuta incluso si ya fue procesado
        """
        if not forzar and self.ya_procesado():
            print("   ⏭️  Fase ya ejecutada previamente (omitiendo)")
            return
        # Validar tipos de resumen
        tipos_validos = {'descriptivo', 'estructurado', 'insights'}
        
        if tipos_resumen is None:
            tipos_resumen = ['descriptivo', 'estructurado', 'insights']
        
        # Validar que sean tipos válidos
        tipos_invalidos = set(tipos_resumen) - tipos_validos
        if tipos_invalidos:
            raise ValueError(
                f"Tipos de resumen inválidos: {tipos_invalidos}\n"
                f"Tipos válidos: {tipos_validos}"
            )
        
        print(f"Tipos de resumen solicitados: {', '.join(tipos_resumen)}")
        
        # 1. Cargar datos
        self._cargar_datos()
        
        # 2. Seleccionar reseñas representativas
        # The adaptive strategy guarantees a non-empty result for any dataset ≥ 1 review
        df_seleccionado = self._seleccionar_reseñas_representativas()
        
        if len(df_seleccionado) == 0:
            print("⚠️  No se encontraron reseñas representativas. Verifica el dataset.")
            return
        
        # 3. Generar resúmenes
        resultado = self._generar_resumenes(df_seleccionado, tipos_resumen)
        
        # 4. Guardar resultado
        self._guardar_resultado(resultado)
        
        print(f"\n✅ Resúmenes generados exitosamente")
        print(f"   • Categorías resumidas: {len(resultado['resumenes'][tipos_resumen[0]]['por_categoria'])}")
        print(f"   • Tipos de resumen: {len(tipos_resumen)}")
