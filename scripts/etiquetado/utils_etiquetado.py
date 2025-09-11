"""
Utilidades y funciones de conveniencia para el etiquetado de subjetividad.
"""

import warnings


def configurar_entorno():
    """
    Configura el entorno de trabajo con las librerías necesarias.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Configuración de visualización
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 12
    
    # Suprimir warnings
    warnings.filterwarnings('ignore')


def mostrar_comandos_utiles():
    """
    Muestra los comandos útiles disponibles en el módulo.
    """
    print("💡 COMANDOS ÚTILES:")
    print("   • verificar_checkpoint() - Ver estado del progreso guardado")
    print("   • reiniciar_clasificacion() - Limpiar progreso y empezar de nuevo")
    print("   • limpiar_checkpoint() - Eliminar archivo de progreso")
    print("   • prueba_rapida(df_reviews, clasificador, n_samples=5) - Probar con pocas reseñas")


def proceso_completo_clasificacion(df_reviews, clasificador, df_existente=None, batch_size=10, save_frequency=50):
    """
    Ejecuta el proceso completo de clasificación con todas las etapas.
    
    Args:
        df_reviews (pandas.DataFrame): DataFrame con las reseñas a clasificar
        clasificador: Clasificador configurado
        df_existente (pandas.DataFrame): DataFrame con clasificaciones previas (opcional)
        batch_size (int): Tamaño del lote para mostrar progreso
        save_frequency (int): Frecuencia de guardado automático
        
    Returns:
        tuple: (df_clasificado_final, df_analizado, guardado_exitoso)
    """
    from .clasificador import clasificar_reviews
    from .analizador import analizar_resultados
    from .visualizador import crear_visualizaciones
    from .guardador import guardar_resultados, generar_resumen_final
    
    # Si no hay datos nuevos para clasificar, usar los existentes
    if df_reviews is None:
        if df_existente is not None:
            df_analizado = analizar_resultados(df_existente)
            return df_existente, df_analizado, True
        else:
            return None, None, False
    
    if clasificador is None:
        return None, None, False
    
    try:
        # 1. Clasificar reseñas nuevas (SOLO maneja checkpoint, NO guarda CSV)
        df_clasificado_nuevo = clasificar_reviews(df_reviews, clasificador, batch_size, save_frequency)
        
        if df_clasificado_nuevo is None:
            return None, None, False
        
        # 2. Solo guardar al CSV si la clasificación está 100% completa
        # Verificar que no haya interrupciones y que todos los datos estén procesados
        if len(df_clasificado_nuevo) == len(df_reviews):
            print("\n🎯 Clasificación completada exitosamente")
            print("💾 Procediendo a guardar en el dataset final...")
            guardado_exitoso = guardar_resultados(df_clasificado_nuevo, df_existente)
        else:
            print(f"\n⚠️ Clasificación incompleta: {len(df_clasificado_nuevo)}/{len(df_reviews)} procesadas")
            print("💾 Los datos parciales están guardados en checkpoint")
            print("🔄 Ejecute nuevamente para continuar desde donde se quedó")
            guardado_exitoso = False
        
        # Determinar el dataset final para análisis
        if df_existente is not None:
            # Combinar para análisis
            import pandas as pd
            df_final = pd.concat([df_existente, df_clasificado_nuevo], ignore_index=True)
            df_final = df_final.drop_duplicates(subset=['TituloReview'], keep='last')
        else:
            df_final = df_clasificado_nuevo
        
        # 3. Analizar resultados combinados
        df_analizado = analizar_resultados(df_final)
        
        if df_analizado is None:
            return df_final, None, guardado_exitoso
        
        # 4. Crear visualizaciones
        crear_visualizaciones(df_analizado)
        
        # 5. Generar resumen final
        generar_resumen_final(df_analizado)
        
        return df_final, df_analizado, guardado_exitoso
        
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por el usuario")
        print("💾 Los datos parciales están guardados en checkpoint")
        print("🔄 Para continuar desde donde se quedó, ejecute nuevamente la clasificación")
        print("📋 Para verificar el progreso, use: verificar_checkpoint()")
        return None, None, False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("💾 Revise si hay datos guardados en checkpoint con: verificar_checkpoint()")
        return None, None, False


def validar_dependencias():
    """
    Valida que todas las dependencias necesarias estén instaladas.
    
    Returns:
        bool: True si todas las dependencias están disponibles
    """
    dependencias = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('matplotlib.pyplot', 'plt'),
        ('seaborn', 'sns'),
        ('langchain_openai', None),
        ('langchain_core.output_parsers', None),
        ('langchain_core.prompts', None),
        ('pydantic', None),
        ('tqdm', None),
        ('dotenv', None)
    ]
    
    faltantes = []
    
    for dep, alias in dependencias:
        try:
            if alias:
                exec(f"import {dep} as {alias}")
            else:
                exec(f"import {dep}")
        except ImportError:
            faltantes.append(dep)
    
    if faltantes:
        print(f"❌ Faltan dependencias: {', '.join(faltantes)}")
        return False
    return True


def obtener_info_sistema():
    """
    Obtiene información del sistema para debugging.
    """
    import sys
    import platform
    
    print("🔧 INFORMACIÓN DEL SISTEMA:")
    print(f"   • Python: {sys.version}")
    print(f"   • Plataforma: {platform.system()} {platform.release()}")
    print(f"   • Arquitectura: {platform.machine()}")
    
    try:
        import pandas as pd
        print(f"   • Pandas: {pd.__version__}")
    except:
        print("   • Pandas: No disponible")
    
    try:
        import numpy as np
        print(f"   • NumPy: {np.__version__}")
    except:
        print("   • NumPy: No disponible")
    
    try:
        import matplotlib
        print(f"   • Matplotlib: {matplotlib.__version__}")
    except:
        print("   • Matplotlib: No disponible")
