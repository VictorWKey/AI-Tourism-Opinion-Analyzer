"""
Módulo para la clasificación de reseñas con gestión de checkpoints.
"""

import os
import pickle
import time
from tqdm import tqdm


def verificar_checkpoint(checkpoint_file="../data/processed/checkpoint_clasificacion.pkl"):
    """
    Verifica el estado del checkpoint actual.
    
    Args:
        checkpoint_file (str): Ruta del archivo de checkpoint
        
    Returns:
        tuple: (bool, dict) - Estado del checkpoint y datos si existen
    """
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            last_index = checkpoint_data['last_index']
            clasificaciones = checkpoint_data['clasificaciones']
            errores = checkpoint_data['errores']
            timestamp = checkpoint_data.get('timestamp', 0)
            
            print("📄 INFORMACIÓN DEL CHECKPOINT")
            print("=" * 40)
            print(f"📅 Fecha: {time.ctime(timestamp)}")
            print(f"📊 Último índice procesado: {last_index}")
            print(f"✅ Reseñas clasificadas: {len(clasificaciones)}")
            print(f"❌ Errores encontrados: {len(errores)}")
            
            if errores:
                print("\n⚠️ Últimos errores:")
                for i, error in enumerate(errores[-3:]):
                    print(f"  {i+1}. Índice {error['index']}: {error['error'][:50]}...")
            
            return True, checkpoint_data
            
        except Exception as e:
            print(f"❌ Error al leer checkpoint: {e}")
            return False, None
    else:
        print("ℹ️ No hay checkpoint guardado")
        return False, None


def limpiar_checkpoint(checkpoint_file="../data/processed/checkpoint_clasificacion.pkl"):
    """
    Función para limpiar manualmente el checkpoint si es necesario.
    
    Args:
        checkpoint_file (str): Ruta del archivo de checkpoint
    """
    try:
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            print("✅ Checkpoint eliminado exitosamente")
        else:
            print("ℹ️ No hay checkpoint para eliminar")
    except Exception as e:
        print(f"❌ Error al eliminar checkpoint: {e}")


def reiniciar_clasificacion():
    """
    Limpia el checkpoint para reiniciar la clasificación desde el principio.
    """
    respuesta = input("⚠️ ¿Estás seguro que quieres reiniciar la clasificación? (sí/no): ")
    if respuesta.lower() in ['sí', 'si', 'yes', 'y']:
        limpiar_checkpoint()
        print("🔄 Clasificación reiniciada. La próxima ejecución empezará desde el principio.")
    else:
        print("❌ Operación cancelada")


def clasificar_reviews(df, clasificador, batch_size=10, save_frequency=50, 
                      checkpoint_file="../data/processed/checkpoint_clasificacion.pkl"):
    """
    Clasifica las reseñas usando el modelo GPT-4o-mini con guardado automático.
    
    Args:
        df (pandas.DataFrame): DataFrame con las reseñas
        clasificador: Cadena de LangChain configurada
        batch_size (int): Número de reseñas a procesar antes de mostrar progreso
        save_frequency (int): Frecuencia de guardado automático (cada N reseñas)
        checkpoint_file (str): Archivo para guardar el progreso
    
    Returns:
        pandas.DataFrame: DataFrame con las clasificaciones añadidas
    """
    if df is None or len(df) == 0:
        print("❌ No hay datos para clasificar")
        return None
    
    # Verificar si existe un checkpoint previo
    start_index = 0
    clasificaciones = []
    errores = []
    
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'rb') as f:
                checkpoint_data = pickle.load(f)
                start_index = checkpoint_data['last_index'] + 1
                clasificaciones = checkpoint_data['clasificaciones']
                errores = checkpoint_data['errores']
            
            print(f"🔄 Recuperando desde checkpoint: índice {start_index}")
            print(f"📋 Ya procesadas: {len(clasificaciones)} reseñas")
            
            if start_index >= len(df):
                print("✅ Todas las reseñas ya han sido procesadas!")
                df_resultado = df.copy()
                df_resultado['SubjetividadConLLM'] = clasificaciones
                return df_resultado
                
        except Exception as e:
            print(f"⚠️ Error al cargar checkpoint: {e}")
            print("🔄 Iniciando desde el principio...")
            start_index = 0
            clasificaciones = []
            errores = []
    
    # Crear copia del dataframe
    df_resultado = df.copy()
    
    print(f"🚀 Iniciando clasificación desde índice {start_index}")
    print(f"📊 Total a procesar: {len(df) - start_index} reseñas restantes")
    print("📝 Cada reseña se procesa de manera independiente (sin historial)")
    print(f"💾 Guardado automático cada {save_frequency} reseñas")
    
    # Función para guardar checkpoint
    def guardar_checkpoint(index, clases, errores_lista):
        try:
            checkpoint_data = {
                'last_index': index,
                'clasificaciones': clases,
                'errores': errores_lista,
                'timestamp': time.time()
            }
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            print(f"   💾 Checkpoint guardado en índice {index}")
        except Exception as e:
            print(f"   ⚠️ Error al guardar checkpoint: {e}")
    
    try:
        # Procesar cada reseña individualmente desde start_index
        for idx in tqdm(range(start_index, len(df)), desc="Clasificando reseñas", initial=start_index, total=len(df)):
            try:
                # Obtener la reseña
                row = df.iloc[idx]
                review_text = row['TituloReview']
                
                # Clasificar usando el modelo (cada llamada es independiente)
                resultado = clasificador.invoke({"review": review_text})
                
                # Extraer la categoría
                categoria = resultado.categoria
                clasificaciones.append(categoria)
                
                # Mostrar progreso cada batch_size reseñas
                if (idx + 1) % batch_size == 0:
                    print(f"   ✅ Procesadas {idx + 1}/{len(df)} reseñas")
                
                # Guardar checkpoint cada save_frequency reseñas
                if (idx + 1) % save_frequency == 0:
                    guardar_checkpoint(idx, clasificaciones, errores)
                    
            except Exception as e:
                print(f"   ⚠️ Error en reseña {idx + 1}: {str(e)[:100]}...")
                clasificaciones.append("Error")
                errores.append({"index": idx, "review": review_text[:100], "error": str(e)})
                
                # Guardar checkpoint también cuando hay errores
                if len(errores) % 5 == 0:  # Guardar cada 5 errores
                    guardar_checkpoint(idx, clasificaciones, errores)
        
        # Guardar checkpoint final
        if len(df) > 0:
            guardar_checkpoint(len(df) - 1, clasificaciones, errores)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Proceso interrumpido por el usuario")
        print(f"💾 Guardando progreso hasta índice {len(clasificaciones) + start_index - 1}...")
        
        # Guardar checkpoint de forma segura
        try:
            if clasificaciones:  # Solo guardar si hay datos
                guardar_checkpoint(len(clasificaciones) + start_index - 1, clasificaciones, errores)
                print(f"✅ Checkpoint guardado exitosamente")
                print(f"📊 Progreso guardado: {len(clasificaciones)} reseñas procesadas")
                print(f"🔄 Para continuar, ejecute nuevamente la clasificación")
            
            # NO crear dataframe parcial para evitar sobrescribir datos
            # El usuario debe usar verificar_checkpoint() para ver el progreso
            print(f"\n📋 Para verificar el progreso guardado, use:")
            print(f"   verificar_checkpoint()")
            
        except Exception as checkpoint_error:
            print(f"❌ Error al guardar checkpoint durante interrupción: {checkpoint_error}")
        
        return None  # Retornar None para indicar interrupción sin datos parciales
        
    except Exception as e:
        print(f"\n❌ Error crítico durante la clasificación: {e}")
        print(f"💾 Guardando progreso hasta donde se pudo...")
        
        try:
            if clasificaciones:
                guardar_checkpoint(len(clasificaciones) + start_index - 1, clasificaciones, errores)
                print(f"✅ Checkpoint de emergencia guardado")
                print(f"📊 Datos parciales preservados: {len(clasificaciones)} reseñas")
            print(f"🔄 Para continuar, ejecute nuevamente la clasificación")
        except Exception as checkpoint_error:
            print(f"❌ Error adicional al guardar checkpoint de emergencia: {checkpoint_error}")
        
        return None
    
    # Añadir clasificaciones al dataframe
    df_resultado['SubjetividadConLLM'] = clasificaciones
    
    # Mostrar resumen de errores
    if errores:
        print(f"\n⚠️ Se encontraron {len(errores)} errores durante la clasificación")
        print("Primeros 3 errores:")
        for i, error in enumerate(errores[:3]):
            print(f"  {i+1}. Índice {error['index']}: {error['error']}")
    
    print(f"\n🎉 Clasificación completada!")
    print(f"📊 Total procesado: {len(df_resultado)} reseñas")
    print(f"❌ Errores: {len(errores)} reseñas")
    
    # Limpiar checkpoint al completar exitosamente
    try:
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            print(f"🗑️ Checkpoint eliminado (proceso completado)")
    except:
        pass
    
    return df_resultado


def prueba_rapida(df_reviews, clasificador, n_samples=5):
    """
    Realiza una prueba rápida con pocas reseñas para verificar el funcionamiento.
    
    Args:
        df_reviews (pandas.DataFrame): DataFrame con las reseñas
        clasificador: Clasificador configurado
        n_samples (int): Número de muestras para la prueba
        
    Returns:
        pandas.DataFrame: DataFrame con las clasificaciones de prueba
    """
    if df_reviews is None:
        print("❌ No hay datos cargados")
        return None
    
    print(f"🧪 PRUEBA RÁPIDA - Clasificando {n_samples} reseñas de muestra")
    print("=" * 50)
    
    # Tomar una muestra pequeña
    df_muestra = df_reviews.head(n_samples)
    
    # Clasificar la muestra (sin checkpoint para pruebas rápidas)
    df_prueba = clasificar_reviews(
        df_muestra, 
        clasificador, 
        batch_size=1,
        save_frequency=1000,  # No guardar checkpoint para pruebas pequeñas
        checkpoint_file="../data/processed/checkpoint_prueba.pkl"
    )
    
    if df_prueba is not None:
        print("\n📋 RESULTADOS DE LA PRUEBA:")
        for idx, row in df_prueba.iterrows():
            print(f"\n{idx+1}. Ciudad: {row['Ciudad']}")
            print(f"   Reseña: {row['TituloReview'][:100]}...")
            print(f"   Clasificación: {row['SubjetividadConLLM']}")
        
        # Mostrar conteo de la prueba
        conteo_prueba = df_prueba['SubjetividadConLLM'].value_counts()
        print(f"\n📊 Conteo de clasificaciones en la prueba:")
        for categoria, count in conteo_prueba.items():
            print(f"   {categoria}: {count}")
        
        # Limpiar checkpoint de prueba
        try:
            checkpoint_prueba = "../data/processed/checkpoint_prueba.pkl"
            if os.path.exists(checkpoint_prueba):
                os.remove(checkpoint_prueba)
        except:
            pass
    
    return df_prueba
