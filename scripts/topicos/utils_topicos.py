"""
Utilidades para análisis de tópicos en opiniones turísticas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Tuple, Dict, Optional, Any
from fastopic import FASTopic


def mostrar_estadisticas_limpieza(df: pd.DataFrame, 
                                columna_original: str = 'TituloReview',
                                columna_limpia: str = 'TituloReviewLimpio') -> None:
    """
    Muestra estadísticas comparativas entre texto original y limpio.
    
    Args:
        df: DataFrame con los datos
        columna_original: Nombre de la columna con texto original
        columna_limpia: Nombre de la columna con texto limpio
    """
    # Filtrar filas válidas
    df_valido = df.dropna(subset=[columna_original, columna_limpia])
    
    # Calcular estadísticas
    stats_original = {
        'longitud_promedio': df_valido[columna_original].str.len().mean(),
        'palabras_promedio': df_valido[columna_original].str.split().str.len().mean(),
        'textos_vacios': df_valido[columna_original].str.strip().eq('').sum()
    }
    
    stats_limpia = {
        'longitud_promedio': df_valido[columna_limpia].str.len().mean(),
        'palabras_promedio': df_valido[columna_limpia].str.split().str.len().mean(),
        'textos_vacios': df_valido[columna_limpia].str.strip().eq('').sum()
    }
    
    print("📊 ESTADÍSTICAS DE LIMPIEZA DE TEXTO")
    print("=" * 50)
    print(f"📈 Total de textos analizados: {len(df_valido)}")
    print()
    
    print("📝 TEXTO ORIGINAL:")
    print(f"   Longitud promedio: {stats_original['longitud_promedio']:.1f} caracteres")
    print(f"   Palabras promedio: {stats_original['palabras_promedio']:.1f}")
    print(f"   Textos vacíos: {stats_original['textos_vacios']}")
    print()
    
    print("🧹 TEXTO LIMPIO:")
    print(f"   Longitud promedio: {stats_limpia['longitud_promedio']:.1f} caracteres")
    print(f"   Palabras promedio: {stats_limpia['palabras_promedio']:.1f}")
    print(f"   Textos vacíos: {stats_limpia['textos_vacios']}")
    print()
    
    # Calcular reducciones
    reduccion_longitud = ((stats_original['longitud_promedio'] - stats_limpia['longitud_promedio']) / 
                         stats_original['longitud_promedio'] * 100)
    reduccion_palabras = ((stats_original['palabras_promedio'] - stats_limpia['palabras_promedio']) / 
                         stats_original['palabras_promedio'] * 100)
    
    print("📉 REDUCCIÓN TRAS LIMPIEZA:")
    print(f"   Reducción en longitud: {reduccion_longitud:.1f}%")
    print(f"   Reducción en palabras: {reduccion_palabras:.1f}%")
    print(f"   Textos perdidos: {stats_limpia['textos_vacios'] - stats_original['textos_vacios']}")


def mostrar_ejemplos_limpieza(df: pd.DataFrame,
                            columna_original: str = 'TituloReview',
                            columna_limpia: str = 'TituloReviewLimpio',
                            n_ejemplos: int = 5) -> None:
    """
    Muestra ejemplos de texto antes y después de la limpieza.
    
    Args:
        df: DataFrame con los datos
        columna_original: Nombre de la columna con texto original
        columna_limpia: Nombre de la columna con texto limpio
        n_ejemplos: Número de ejemplos a mostrar
    """
    print(f"\n🔍 EJEMPLOS DE LIMPIEZA DE TEXTO (mostrando {n_ejemplos})")
    print("=" * 80)
    
    # Seleccionar ejemplos aleatorios
    df_muestra = df.dropna(subset=[columna_original, columna_limpia]).sample(n=min(n_ejemplos, len(df)))
    
    for i, (idx, row) in enumerate(df_muestra.iterrows(), 1):
        print(f"\n📄 EJEMPLO {i}:")
        print(f"🔸 Original: {row[columna_original]}")
        print(f"🔹 Limpio:   {row[columna_limpia]}")
        
        # Mostrar estadísticas del ejemplo
        len_orig = len(str(row[columna_original]))
        len_limpio = len(str(row[columna_limpia]))
        reduccion = ((len_orig - len_limpio) / len_orig * 100) if len_orig > 0 else 0
        print(f"📊 Reducción: {len_orig} → {len_limpio} caracteres ({reduccion:.1f}%)")
        print("-" * 80)


def validar_textos_para_topicos(df: pd.DataFrame,
                               columna_texto: str = 'TituloReviewLimpio',
                               min_palabras: int = 2) -> Tuple[pd.DataFrame, Dict]:
    """
    Valida y filtra textos para análisis de tópicos.
    
    Args:
        df: DataFrame con los datos
        columna_texto: Nombre de la columna con texto a validar
        min_palabras: Número mínimo de palabras válidas
        
    Returns:
        Tuple con DataFrame filtrado y estadísticas de validación
    """
    df_original = df.copy()
    
    # Filtrar textos válidos
    mask_valido = (
        df[columna_texto].notna() &
        (df[columna_texto].str.strip() != '') &
        (df[columna_texto].str.split().str.len() >= min_palabras)
    )
    
    df_valido = df[mask_valido].copy()
    
    # Estadísticas de validación
    stats = {
        'total_original': len(df_original),
        'textos_validos': len(df_valido),
        'textos_eliminados': len(df_original) - len(df_valido),
        'porcentaje_validos': len(df_valido) / len(df_original) * 100 if len(df_original) > 0 else 0,
        'promedio_palabras': df_valido[columna_texto].str.split().str.len().mean() if len(df_valido) > 0 else 0
    }
    
    print("✅ VALIDACIÓN DE TEXTOS PARA ANÁLISIS DE TÓPICOS")
    print("=" * 55)
    print(f"📊 Total textos originales: {stats['total_original']}")
    print(f"✅ Textos válidos: {stats['textos_validos']}")
    print(f"❌ Textos eliminados: {stats['textos_eliminados']}")
    print(f"📈 Porcentaje válidos: {stats['porcentaje_validos']:.1f}%")
    print(f"📝 Promedio palabras por texto: {stats['promedio_palabras']:.1f}")
    
    return df_valido, stats


def generar_reporte_limpieza(df_antes: pd.DataFrame,
                           df_despues: pd.DataFrame,
                           columna_original: str = 'TituloReview',
                           columna_limpia: str = 'TituloReviewLimpio') -> None:
    """
    Genera un reporte completo del proceso de limpieza.
    
    Args:
        df_antes: DataFrame antes de la limpieza
        df_despues: DataFrame después de la limpieza
        columna_original: Nombre de la columna original
        columna_limpia: Nombre de la columna limpia
    """
    print("📋 REPORTE COMPLETO DE LIMPIEZA DE TEXTO")
    print("=" * 60)
    
    # Estadísticas generales
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   Registros procesados: {len(df_antes)}")
    print(f"   Nueva columna creada: {columna_limpia}")
    print(f"   Posición en dataset: columna {df_despues.columns.get_loc(columna_limpia) + 1}")
    
    # Mostrar estadísticas detalladas
    mostrar_estadisticas_limpieza(df_despues, columna_original, columna_limpia)
    
    # Validar textos para tópicos
    print(f"\n{'='*60}")
    df_valido, stats_validacion = validar_textos_para_topicos(df_despues, columna_limpia)
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if stats_validacion['porcentaje_validos'] < 80:
        print("   ⚠️  Bajo porcentaje de textos válidos. Considera ajustar parámetros de limpieza.")
    else:
        print("   ✅ Buen porcentaje de textos válidos para análisis de tópicos.")
    
    if stats_validacion['promedio_palabras'] < 3:
        print("   ⚠️  Promedio de palabras bajo. Los tópicos pueden ser menos informativos.")
    else:
        print("   ✅ Promedio de palabras adecuado para análisis de tópicos.")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"   1. Usar columna '{columna_limpia}' para análisis de tópicos")
    print(f"   2. Dataset guardado con nueva columna")
    print(f"   3. Ejecutar BERTopic con textos limpios")


def visualizar_distribucion_palabras(df: pd.DataFrame,
                                   columna_original: str = 'TituloReview',
                                   columna_limpia: str = 'TituloReviewLimpio') -> None:
    """
    Visualiza la distribución de palabras antes y después de la limpieza.
    
    Args:
        df: DataFrame con los datos
        columna_original: Nombre de la columna original
        columna_limpia: Nombre de la columna limpia
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Calcular número de palabras
    palabras_original = df[columna_original].str.split().str.len().dropna()
    palabras_limpia = df[columna_limpia].str.split().str.len().dropna()
    
    # Histograma texto original
    axes[0].hist(palabras_original, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0].set_title(f'Distribución de Palabras - {columna_original}', fontweight='bold')
    axes[0].set_xlabel('Número de Palabras')
    axes[0].set_ylabel('Frecuencia')
    axes[0].axvline(palabras_original.mean(), color='red', linestyle='--', 
                   label=f'Media: {palabras_original.mean():.1f}')
    axes[0].legend()
    
    # Histograma texto limpio
    axes[1].hist(palabras_limpia, bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[1].set_title(f'Distribución de Palabras - {columna_limpia}', fontweight='bold')
    axes[1].set_xlabel('Número de Palabras')
    axes[1].set_ylabel('Frecuencia')
    axes[1].axvline(palabras_limpia.mean(), color='red', linestyle='--', 
                   label=f'Media: {palabras_limpia.mean():.1f}')
    axes[1].legend()
    
    plt.tight_layout()
    plt.show()
    
    # Estadísticas adicionales
    print("📊 ESTADÍSTICAS DE DISTRIBUCIÓN DE PALABRAS:")
    print(f"Original - Media: {palabras_original.mean():.1f}, Mediana: {palabras_original.median():.1f}")
    print(f"Limpio   - Media: {palabras_limpia.mean():.1f}, Mediana: {palabras_limpia.median():.1f}")


def procesar_topicos_fastopic(model: Any, 
                             doc_topic_dist: np.ndarray,
                             top_words: List,
                             topic_names: Optional[Dict[int, str]] = None) -> pd.DataFrame:
    """
    Procesa los resultados de FASTopic en un formato estándar.
    
    Args:
        model: Modelo FASTopic entrenado
        doc_topic_dist: Distribución documento-tópico
        top_words: Lista de palabras por tópico (puede ser lista de strings o lista de listas)
        topic_names: Mapeo de ID de tópico a nombres semánticos
        
    Returns:
        DataFrame con información de tópicos procesada
    """
    
    # Obtener información básica de tópicos
    num_topics = len(top_words)
    topic_info = []
    
    for topic_id in range(num_topics):
        # Obtener palabras del tópico - manejar diferentes formatos
        raw_words = top_words[topic_id] if topic_id < len(top_words) else []
        
        # Si es un string, dividir por espacios; si es lista, usar directamente
        if isinstance(raw_words, str):
            words = raw_words.split()[:10]  # Tomar máximo 10 palabras
        elif isinstance(raw_words, (list, tuple)):
            words = list(raw_words)[:10]  # Tomar máximo 10 palabras
        else:
            words = []
            
        keywords = ", ".join(words) if words else "Sin palabras"
        
        # Calcular peso del tópico (suma de probabilidades)
        topic_weight = doc_topic_dist[:, topic_id].sum()
        
        # Obtener nombre semántico
        topic_name = topic_names.get(topic_id, f"Tópico {topic_id}") if topic_names else f"Tópico {topic_id}"
        
        topic_info.append({
            'Topic': topic_id,
            'Name': topic_name,
            'Keywords': keywords,
            'Count': int((doc_topic_dist[:, topic_id] > 0.1).sum()),  # Docs con alta probabilidad
            'Weight': float(topic_weight),
            'Top_Words': words[:10] if words else []
        })
    
    return pd.DataFrame(topic_info)


def obtener_asignaciones_topicos_fastopic(doc_topic_dist: np.ndarray, 
                                        topic_names: Optional[Dict[int, str]] = None,
                                        threshold: float = 0.1) -> Tuple[List[int], List[str], List[float]]:
    """
    Obtiene las asignaciones de tópicos para cada documento.
    
    Args:
        doc_topic_dist: Distribución documento-tópico
        topic_names: Mapeo de ID de tópico a nombres
        threshold: Umbral mínimo de probabilidad para asignar tópico
        
    Returns:
        Tuple con listas de IDs de tópicos, nombres y probabilidades
    """
    
    # Obtener tópico dominante para cada documento
    topic_assignments = []
    topic_names_assigned = []
    topic_probabilities = []
    
    for doc_idx in range(doc_topic_dist.shape[0]):
        doc_probs = doc_topic_dist[doc_idx]
        max_prob_idx = np.argmax(doc_probs)
        max_prob = doc_probs[max_prob_idx]
        
        if max_prob >= threshold:
            topic_assignments.append(int(max_prob_idx))
            topic_name = topic_names.get(int(max_prob_idx), f"Tópico {max_prob_idx}") if topic_names else f"Tópico {max_prob_idx}"
            topic_names_assigned.append(topic_name)
            topic_probabilities.append(float(max_prob))
        else:
            # Tópico no asignado (probabilidad muy baja)
            topic_assignments.append(-1)
            topic_names_assigned.append("Sin Tópico Claro")
            topic_probabilities.append(float(max_prob))
    
    return topic_assignments, topic_names_assigned, topic_probabilities


def visualizar_distribucion_topicos_fastopic(topic_info: pd.DataFrame, 
                                           ciudad: str = "",
                                           top_n: int = 10) -> None:
    """
    Visualiza la distribución de tópicos de FASTopic.
    
    Args:
        topic_info: DataFrame con información de tópicos
        ciudad: Nombre de la ciudad analizada
        top_n: Número de tópicos principales a mostrar
    """
    
    # Ordenar por peso y tomar los principales
    topic_info_sorted = topic_info.sort_values('Weight', ascending=False).head(top_n)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Gráfico 1: Distribución por peso
    topic_info_sorted.plot(x='Name', y='Weight', kind='bar', ax=axes[0,0], color='lightcoral')
    axes[0,0].set_title(f'Peso de Tópicos - {ciudad}' if ciudad else 'Peso de Tópicos', 
                       fontsize=14, fontweight='bold')
    axes[0,0].set_xlabel('Tópicos')
    axes[0,0].set_ylabel('Peso del Tópico')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Gráfico 2: Distribución por conteo de documentos
    topic_info_sorted.plot(x='Name', y='Count', kind='bar', ax=axes[0,1], color='lightblue')
    axes[0,1].set_title(f'Documentos por Tópico - {ciudad}' if ciudad else 'Documentos por Tópico', 
                       fontsize=14, fontweight='bold')
    axes[0,1].set_xlabel('Tópicos')
    axes[0,1].set_ylabel('Número de Documentos')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Gráfico 3: Pie chart de distribución
    if len(topic_info_sorted) > 0:
        axes[1,0].pie(topic_info_sorted['Weight'], labels=topic_info_sorted['Name'], autopct='%1.1f%%')
        axes[1,0].set_title(f'Proporción de Tópicos - {ciudad}' if ciudad else 'Proporción de Tópicos', 
                           fontsize=14, fontweight='bold')
    
    # Gráfico 4: Relación peso vs documentos
    axes[1,1].scatter(topic_info_sorted['Count'], topic_info_sorted['Weight'], 
                     s=100, alpha=0.7, color='green')
    axes[1,1].set_xlabel('Número de Documentos')
    axes[1,1].set_ylabel('Peso del Tópico')
    axes[1,1].set_title(f'Relación Documentos-Peso - {ciudad}' if ciudad else 'Relación Documentos-Peso', 
                       fontsize=14, fontweight='bold')
    
    # Añadir etiquetas a los puntos
    for idx, row in topic_info_sorted.iterrows():
        axes[1,1].annotate(row['Name'][:10] + '...', 
                          (row['Count'], row['Weight']), 
                          xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.tight_layout()
    plt.show()


def crear_heatmap_topicos_categorias(df: pd.DataFrame,
                                   categoria_col: str,
                                   topico_col: str = 'Topico_Nombre',
                                   ciudad: str = "") -> None:
    """
    Crea un heatmap mostrando la relación entre tópicos y categorías.
    
    Args:
        df: DataFrame con los datos
        categoria_col: Nombre de la columna de categoría
        topico_col: Nombre de la columna de tópicos
        ciudad: Nombre de la ciudad para el título
    """
    
    # Crear tabla cruzada
    crosstab = pd.crosstab(df[categoria_col], df[topico_col])
    crosstab_norm = crosstab.div(crosstab.sum(axis=1), axis=0)
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(crosstab_norm, annot=True, fmt='.2f', cmap='YlOrRd', cbar_kws={'label': 'Proporción'})
    plt.title(f'Proporción de Tópicos por {categoria_col} - {ciudad}' if ciudad else f'Proporción de Tópicos por {categoria_col}', 
             fontsize=14, fontweight='bold')
    plt.xlabel('Tópicos')
    plt.ylabel(categoria_col)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()


def mostrar_ejemplos_por_topico_fastopic(df: pd.DataFrame,
                                       topico_col: str = 'Topico_Nombre',
                                       texto_col: str = 'TituloReview',
                                       n_ejemplos: int = 3,
                                       top_n_topicos: int = 5) -> None:
    """
    Muestra ejemplos de documentos para cada tópico.
    
    Args:
        df: DataFrame con los datos
        topico_col: Nombre de la columna de tópicos
        texto_col: Nombre de la columna de texto
        n_ejemplos: Número de ejemplos por tópico
        top_n_topicos: Número de tópicos principales a mostrar
    """
    
    topico_counts = df[topico_col].value_counts()
    
    print(f"📚 EJEMPLOS DE OPINIONES POR TÓPICO")
    print("=" * 70)
    
    for i, (topico_nombre, count) in enumerate(topico_counts.head(top_n_topicos).items()):
        ejemplos = df[df[topico_col] == topico_nombre][texto_col].head(n_ejemplos)
        
        print(f"\n🏷️ {i+1}. {topico_nombre}")
        print(f"📊 Total de opiniones: {count}")
        print("📝 Ejemplos:")
        
        for j, ejemplo in enumerate(ejemplos, 1):
            print(f"   {j}. {ejemplo}")
        
        print("-" * 70)


def comparar_topicos_entre_ciudades(df: pd.DataFrame,
                                  topico_col: str = 'TopicoConFASTopic',
                                  ciudad_col: str = 'Ciudad') -> None:
    """
    Compara la distribución de tópicos entre diferentes ciudades.
    
    Args:
        df: DataFrame con los datos
        topico_col: Nombre de la columna de tópicos
        ciudad_col: Nombre de la columna de ciudades
    """
    
    # Filtrar solo ciudades con tópicos asignados
    df_con_topicos = df.dropna(subset=[topico_col])
    
    if len(df_con_topicos) == 0:
        print("⚠️ No hay datos con tópicos asignados para comparar")
        return
    
    # Crear tabla cruzada
    crosstab = pd.crosstab(df_con_topicos[ciudad_col], df_con_topicos[topico_col])
    crosstab_norm = crosstab.div(crosstab.sum(axis=1), axis=0)
    
    plt.figure(figsize=(15, 10))
    sns.heatmap(crosstab_norm, annot=True, fmt='.2f', cmap='viridis', 
               cbar_kws={'label': 'Proporción de Tópicos'})
    plt.title('Comparación de Tópicos entre Ciudades', fontsize=16, fontweight='bold')
    plt.xlabel('Tópicos')
    plt.ylabel('Ciudades')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()
    
    print("📊 ESTADÍSTICAS DE COMPARACIÓN ENTRE CIUDADES:")
    print("=" * 60)
    for ciudad in crosstab.index:
        total_opiniones = crosstab.loc[ciudad].sum()
        topico_principal = crosstab_norm.loc[ciudad].idxmax()
        porcentaje_principal = crosstab_norm.loc[ciudad].max() * 100
        
        print(f"\n🏙️ {ciudad}:")
        print(f"   📝 Total opiniones: {total_opiniones}")
        print(f"   🎯 Tópico principal: {topico_principal}")
        print(f"   📊 Concentración: {porcentaje_principal:.1f}%")


def generar_reporte_fastopic(topic_info: pd.DataFrame,
                           num_documentos: int,
                           ciudad: str = "",
                           tiempo_entrenamiento: Optional[float] = None) -> None:
    """
    Genera un reporte completo del análisis con FASTopic.
    
    Args:
        topic_info: DataFrame con información de tópicos
        num_documentos: Número total de documentos analizados
        ciudad: Nombre de la ciudad analizada
        tiempo_entrenamiento: Tiempo de entrenamiento en segundos
    """
    
    print("📋 REPORTE COMPLETO - ANÁLISIS CON FASTOPIC")
    print("=" * 60)
    
    # Información general
    print(f"🎯 ANÁLISIS COMPLETADO:")
    if ciudad:
        print(f"   📍 Ciudad: {ciudad}")
    print(f"   📄 Documentos analizados: {num_documentos:,}")
    print(f"   🏷️ Tópicos identificados: {len(topic_info)}")
    if tiempo_entrenamiento:
        print(f"   ⏱️ Tiempo de entrenamiento: {tiempo_entrenamiento:.2f} segundos")
    
    # Estadísticas de tópicos
    print(f"\n📊 ESTADÍSTICAS DE TÓPICOS:")
    print(f"   🎯 Tópico más relevante: {topic_info.loc[topic_info['Weight'].idxmax(), 'Name']}")
    print(f"   📈 Peso máximo: {topic_info['Weight'].max():.3f}")
    print(f"   📉 Peso mínimo: {topic_info['Weight'].min():.3f}")
    print(f"   📊 Peso promedio: {topic_info['Weight'].mean():.3f}")
    
    # Top 5 tópicos
    top_5 = topic_info.nlargest(5, 'Weight')
    print(f"\n🏆 TOP 5 TÓPICOS POR RELEVANCIA:")
    for i, (_, row) in enumerate(top_5.iterrows(), 1):
        print(f"   {i}. {row['Name']}")
        print(f"      📊 Peso: {row['Weight']:.3f} | 📄 Documentos: {row['Count']}")
        print(f"      🔑 Palabras clave: {row['Keywords'][:50]}...")
    
    # Calidad del modelado
    print(f"\n💎 CALIDAD DEL MODELADO:")
    docs_asignados = (topic_info['Count'] > 0).sum()
    print(f"   ✅ Tópicos con documentos asignados: {docs_asignados}/{len(topic_info)}")
    
    concentracion = (topic_info['Weight'].max() / topic_info['Weight'].sum()) * 100
    if concentracion > 50:
        print(f"   ⚠️ Alta concentración en un tópico: {concentracion:.1f}%")
    else:
        print(f"   ✅ Distribución balanceada de tópicos: {concentracion:.1f}% máx.")
    
    print(f"\n🚀 PRÓXIMOS PASOS RECOMENDADOS:")
    print(f"   1. Revisar ejemplos de cada tópico principal")
    print(f"   2. Analizar relación con sentimientos y subjetividad")
    print(f"   3. Comparar resultados con BERTopic si está disponible")
    print(f"   4. Exportar resultados al dataset principal")
