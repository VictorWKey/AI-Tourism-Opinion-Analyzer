"""
Módulo para visualización de resultados de clasificación.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def configurar_estilo_graficos():
    """
    Configura el estilo general para los gráficos.
    """
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 12


def crear_visualizaciones(df_clean):
    """
    Crea gráficos para visualizar los resultados de clasificación.
    
    Args:
        df_clean (pandas.DataFrame): DataFrame limpio con clasificaciones
    """
    if df_clean is None or len(df_clean) == 0:
        print("❌ No hay datos para visualizar")
        return
    
    # Configurar el estilo de los gráficos
    configurar_estilo_graficos()
    
    # Crear figura con subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análisis de Clasificación de Subjetividad en Reseñas Turísticas', 
                 fontsize=16, fontweight='bold')
    
    # 1. Gráfico de barras - Distribución general
    ax1 = axes[0, 0]
    conteo_general = df_clean['SubjetividadConLLM'].value_counts()
    colores = ['#2E8B57', '#FF6B6B', '#4ECDC4']  # Verde, Rojo coral, Turquesa
    
    bars1 = ax1.bar(conteo_general.index, conteo_general.values, color=colores)
    ax1.set_title('Distribución General de Clasificaciones', fontweight='bold')
    ax1.set_ylabel('Número de Reseñas')
    ax1.set_xlabel('Tipo de Clasificación')
    
    # Añadir valores en las barras
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom')
    
    # 2. Gráfico de pastel - Porcentajes generales
    ax2 = axes[0, 1]
    ax2.pie(conteo_general.values, labels=conteo_general.index, autopct='%1.1f%%',
            colors=colores, startangle=90)
    ax2.set_title('Distribución Porcentual de Clasificaciones', fontweight='bold')
    
    # 3. Gráfico de barras agrupadas - Por ciudad
    ax3 = axes[1, 0]
    df_pivot = df_clean.groupby(['Ciudad', 'SubjetividadConLLM']).size().unstack(fill_value=0)
    
    df_pivot.plot(kind='bar', ax=ax3, color=colores, width=0.8)
    ax3.set_title('Clasificaciones por Ciudad', fontweight='bold')
    ax3.set_ylabel('Número de Reseñas')
    ax3.set_xlabel('Ciudad')
    ax3.legend(title='Clasificación')
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Gráfico de barras apiladas normalizadas - Porcentajes por ciudad
    ax4 = axes[1, 1]
    df_pivot_pct = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100
    
    df_pivot_pct.plot(kind='bar', stacked=True, ax=ax4, color=colores, width=0.8)
    ax4.set_title('Distribución Porcentual por Ciudad', fontweight='bold')
    ax4.set_ylabel('Porcentaje (%)')
    ax4.set_xlabel('Ciudad')
    ax4.legend(title='Clasificación')
    ax4.tick_params(axis='x', rotation=45)
    
    # Ajustar layout
    plt.tight_layout()
    plt.show()
    
    # Crear un gráfico adicional más detallado
    crear_grafico_detallado(df_clean, colores)


def crear_grafico_detallado(df_clean, colores):
    """
    Crea un gráfico detallado de comparación por ciudad.
    
    Args:
        df_clean (pandas.DataFrame): DataFrame limpio con clasificaciones
        colores (list): Lista de colores para los gráficos
    """
    fig2, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Gráfico de barras horizontales con detalles
    categorias = ['Objetiva', 'Subjetiva', 'Mixta']
    ciudades = df_clean['Ciudad'].unique()
    
    x = np.arange(len(categorias))
    width = 0.35
    
    for i, ciudad in enumerate(ciudades):
        df_ciudad = df_clean[df_clean['Ciudad'] == ciudad]
        valores = [len(df_ciudad[df_ciudad['SubjetividadConLLM'] == cat]) for cat in categorias]
        
        offset = width * (i - len(ciudades)/2 + 0.5)
        bars = ax.bar(x + offset, valores, width, label=ciudad, alpha=0.8)
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel('Tipo de Clasificación')
    ax.set_ylabel('Número de Reseñas')
    ax.set_title('Comparación Detallada de Clasificaciones por Ciudad')
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def crear_grafico_simple(df_clean, tipo='barras'):
    """
    Crea un gráfico simple para visualización rápida.
    
    Args:
        df_clean (pandas.DataFrame): DataFrame limpio con clasificaciones
        tipo (str): Tipo de gráfico ('barras' o 'pastel')
    """
    if df_clean is None or len(df_clean) == 0:
        print("❌ No hay datos para visualizar")
        return
    
    configurar_estilo_graficos()
    
    conteo_general = df_clean['SubjetividadConLLM'].value_counts()
    colores = ['#2E8B57', '#FF6B6B', '#4ECDC4']
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    if tipo == 'barras':
        bars = ax.bar(conteo_general.index, conteo_general.values, color=colores)
        ax.set_title('Distribución de Clasificaciones de Subjetividad', fontweight='bold')
        ax.set_ylabel('Número de Reseñas')
        ax.set_xlabel('Tipo de Clasificación')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{int(height)}', ha='center', va='bottom')
    
    elif tipo == 'pastel':
        ax.pie(conteo_general.values, labels=conteo_general.index, autopct='%1.1f%%',
               colors=colores, startangle=90)
        ax.set_title('Distribución Porcentual de Clasificaciones de Subjetividad', fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def mostrar_ejemplos_detallados(df, n_ejemplos=2):
    """
    Muestra ejemplos de opiniones con desglose detallado por categoría.
    
    Args:
        df (pandas.DataFrame): DataFrame con clasificaciones
        n_ejemplos (int): Número de ejemplos por categoría
    """
    if df is None or 'SubjetividadConLLM' not in df.columns:
        print("❌ No hay datos con clasificación LLM disponibles")
        return
    
    print("🔍 EJEMPLOS DE OPINIONES CON DESGLOSE DETALLADO")
    print("=" * 60)
    
    tipos = ['Objetiva', 'Subjetiva', 'Mixta']
    
    for tipo in tipos:
        opiniones_tipo = df[df['SubjetividadConLLM'] == tipo]
        
        if len(opiniones_tipo) > 0:
            print(f"\n🎯 EJEMPLOS DE OPINIONES {tipo.upper()}S")
            print("-" * 40)
            
            ejemplos = opiniones_tipo.sample(min(n_ejemplos, len(opiniones_tipo)), random_state=42)
            
            for i, (_, ejemplo) in enumerate(ejemplos.iterrows(), 1):
                print(f"\n📌 Ejemplo {i}:")
                print(f"🏛️ {ejemplo['Atraccion']} - {ejemplo['Ciudad']}")
                print(f"⭐ Calificación: {ejemplo['Calificacion']}/5")
                print(f"💬 \"{ejemplo['TituloReview']}\"")
                
                # Mostrar análisis comparativo
                print(f"🤖 Clasificaciones:")
                if 'SubjetividadConHF' in ejemplo.index:
                    print(f"   • HuggingFace: {ejemplo['SubjetividadConHF']}")
                if 'SubjetividadConFrases' in ejemplo.index:
                    print(f"   • Por frases: {ejemplo['SubjetividadConFrases']}")
                print(f"   • LLM (GPT): {ejemplo['SubjetividadConLLM']}")
                
                # Desglose por frases si está disponible
                if 'TotalFrases' in ejemplo.index and ejemplo['TotalFrases'] is not None:
                    print(f"\n📊 Desglose por frases:")
                    print(f"   • Total: {int(ejemplo['TotalFrases'])}")
                    print(f"   • Subjetivas: {int(ejemplo['FrasesSubjetivas'])} ({ejemplo['PorcentajeSubjetivo']:.1f}%)")
                    print(f"   • Objetivas: {int(ejemplo['FrasesObjetivas'])} ({ejemplo['PorcentajeObjetivo']:.1f}%)")


def analisis_avanzado_frases(df, n_ejemplos=2):
    """
    Muestra análisis avanzado de frases usando el módulo de subjetividad.
    
    Args:
        df (pandas.DataFrame): DataFrame con clasificaciones
        n_ejemplos (int): Número de ejemplos a analizar
    """
    if df is None:
        print("❌ No hay datos disponibles")
        return
    
    try:
        from subjetividad import AnalizadorOpinionesMixtas
    except ImportError:
        print("❌ No se pudo importar el módulo de subjetividad")
        return
    
    print("\n🔬 ANÁLISIS AVANZADO DE FRASES")
    print("=" * 50)
    
    analizador_mixtas = AnalizadorOpinionesMixtas()
    analizador_mixtas.configurar_modelos()
    
    # Seleccionar ejemplos mixtos o aleatorios
    ejemplos_mixtos = df[df.get('EsMixta', False) == True] if 'EsMixta' in df.columns else df.sample(n_ejemplos)
    ejemplos = ejemplos_mixtos.head(n_ejemplos) if len(ejemplos_mixtos) > 0 else df.sample(n_ejemplos)
    
    for i, (_, opinion) in enumerate(ejemplos.iterrows(), 1):
        print(f"\n🎯 OPINIÓN {i}:")
        print(f"💬 \"{opinion['TituloReview']}\"")
        print(f"🏛️ {opinion['Atraccion']} - {opinion['Ciudad']}")
        
        # Analizar por frases
        resultado = analizador_mixtas.analizar_opinion_por_frases(opinion['TituloReview'])
        
        print(f"\n📊 DESGLOSE:")
        print(f"   • Total: {resultado['total_frases']} frases")
        print(f"   • Subjetivas: {resultado['frases_subjetivas']} ({resultado['porcentaje_subjetivo']:.1f}%)")
        print(f"   • Objetivas: {resultado['frases_objetivas']} ({resultado['porcentaje_objetivo']:.1f}%)")
        print(f"   • Clasificación: {resultado['clasificacion_final']}")
        
        print(f"\n📝 FRASES:")
        for j, (frase, clasificacion) in enumerate(zip(resultado['frases'], resultado['clasificaciones_frases']), 1):
            icono = "💭" if clasificacion == 'Subjetivo' else "📊"
            frase_corta = frase[:80] + "..." if len(frase) > 80 else frase
            print(f"   {icono} {j}. [{clasificacion}] \"{frase_corta}\"")
