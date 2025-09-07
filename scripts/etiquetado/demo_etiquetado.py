"""
Script de demostración del módulo de etiquetado de subjetividad.

Este script muestra cómo usar el módulo de etiquetado para clasificar 
reseñas turísticas de manera programática.
"""

import sys
import os

# Añadir el directorio padre al path para importar el módulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etiquetado import (
    configurar_entorno, validar_dependencias, verificar_api_key,
    cargar_datasets, configurar_clasificador,
    proceso_completo_clasificacion, prueba_rapida
)


def main():
    """
    Función principal que ejecuta el proceso completo de clasificación.
    """
    print("🚀 DEMO: Clasificación de Subjetividad en Reseñas Turísticas")
    print("=" * 60)
    
    # 1. Configurar entorno
    print("\n1️⃣ Configurando entorno...")
    configurar_entorno()
    
    # 2. Validar dependencias
    print("\n2️⃣ Validando dependencias...")
    if not validar_dependencias():
        print("❌ Instala las dependencias faltantes y vuelve a ejecutar")
        return False
    
    # 3. Verificar API key
    print("\n3️⃣ Verificando configuración de OpenAI...")
    if not verificar_api_key():
        print("❌ Configura tu API key de OpenAI en el archivo .env")
        return False
    
    # 4. Cargar datos
    print("\n4️⃣ Cargando datasets...")
    df_reviews = cargar_datasets()
    if df_reviews is None:
        print("❌ Error al cargar los datos")
        return False
    
    # 5. Configurar clasificador
    print("\n5️⃣ Configurando clasificador...")
    clasificador = configurar_clasificador()
    if clasificador is None:
        print("❌ Error al configurar el clasificador")
        return False
    
    # 6. Opción de prueba rápida
    respuesta = input("\n🤔 ¿Quieres hacer una prueba rápida primero? (sí/no): ")
    if respuesta.lower() in ['sí', 'si', 'yes', 'y']:
        print("\n🧪 Ejecutando prueba rápida...")
        df_prueba = prueba_rapida(df_reviews, clasificador, n_samples=3)
        if df_prueba is not None:
            print("✅ Prueba completada exitosamente")
        
        continuar = input("\n🤔 ¿Continuar con el proceso completo? (sí/no): ")
        if continuar.lower() not in ['sí', 'si', 'yes', 'y']:
            print("👋 Proceso terminado")
            return True
    
    # 7. Proceso completo
    print("\n6️⃣ Ejecutando proceso completo...")
    try:
        df_clasificado, df_analizado, guardado_exitoso = proceso_completo_clasificacion(
            df_reviews, 
            clasificador,
            batch_size=10,
            save_frequency=50
        )
        
        if df_clasificado is not None:
            print("\n🎉 ¡Proceso completado exitosamente!")
            return True
        else:
            print("\n❌ Error en el proceso de clasificación")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por el usuario")
        print("💾 El progreso se ha guardado automáticamente")
        return True
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False


def demo_funciones_individuales():
    """
    Demostración del uso de funciones individuales del módulo.
    """
    print("\n🔧 DEMO: Uso de funciones individuales")
    print("=" * 40)
    
    # Importar funciones específicas
    from etiquetado import (
        analizar_resultados, crear_grafico_simple,
        guardar_resultados, generar_resumen_final
    )
    
    print("✅ Funciones importadas correctamente")
    print("💡 Estas funciones se pueden usar individualmente después de la clasificación")
    
    # Mostrar ejemplos de uso
    ejemplos = [
        "# Análizar resultados",
        "df_analizado = analizar_resultados(df_clasificado)",
        "",
        "# Crear gráfico simple",
        "crear_grafico_simple(df_analizado, 'barras')",
        "",
        "# Guardar resultados",
        "guardar_resultados(df_clasificado)",
        "",
        "# Generar resumen",
        "generar_resumen_final(df_analizado)"
    ]
    
    print("\n📝 Ejemplos de uso:")
    for ejemplo in ejemplos:
        print(f"   {ejemplo}")


if __name__ == "__main__":
    # Ejecutar demo principal
    exito = main()
    
    if exito:
        # Mostrar demo de funciones individuales
        demo_funciones_individuales()
        
        print("\n🎯 Demo completado")
        print("📚 Consulta el notebook para más detalles sobre cada función")
    else:
        print("\n❌ Demo terminado con errores")
        print("🔧 Revisa la configuración y vuelve a intentar")
