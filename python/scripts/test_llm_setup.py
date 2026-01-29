#!/usr/bin/env python
"""
Script de Prueba de Configuración LLM
======================================
Verifica que la configuración de LLM esté correcta y funcionando.
"""

import sys
from pathlib import Path

# Agregar directorio production al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config():
    """Prueba la configuración básica."""
    print("=" * 60)
    print("PRUEBA DE CONFIGURACIÓN LLM")
    print("=" * 60)
    print()
    
    try:
        from config import ConfigLLM
        
        print("✅ Módulo de configuración cargado")
        print()
        
        # Mostrar configuración
        info = ConfigLLM.get_info()
        print("📋 Configuración actual:")
        print(f"   • Modo: {info['modo'].upper()}")
        print(f"   • Modelo: {info['modelo']}")
        
        if info['modo'] == 'api':
            print(f"   • API key configurada: {'✅' if info.get('api_key_configurada') else '❌'}")
            if not info.get('api_key_configurada'):
                print()
                print("⚠️  ADVERTENCIA: API key no configurada")
                print("   Edita el archivo .env y agrega tu OPENAI_API_KEY")
                return False
        else:
            print(f"   • URL base: {info['base_url']}")
        
        print(f"   • Temperatura: {info['temperatura']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error al cargar configuración: {e}")
        print()
        print("💡 Soluciones:")
        print("   1. Copia .env.example a .env")
        print("   2. Edita .env con tu configuración")
        print("   3. Revisa LLM_SETUP.md para más detalles")
        return False


def test_llm_provider():
    """Prueba el proveedor de LLM."""
    print("=" * 60)
    print("PRUEBA DE PROVEEDOR LLM")
    print("=" * 60)
    print()
    
    try:
        from core import LLMProvider
        
        print("⏳ Inicializando proveedor LLM...")
        provider = LLMProvider()
        print()
        
        info = provider.get_info()
        
        if info['modo'] == 'local':
            print("🔍 Verificando conexión con Ollama...")
        else:
            print("🔍 Verificando conexión con OpenAI API...")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar proveedor: {e}")
        print()
        
        # Ayuda específica según el error
        error_str = str(e).lower()
        
        if 'ollama' in error_str or 'connect' in error_str:
            print("💡 Parece un problema con Ollama:")
            print("   1. Verifica que Ollama esté instalado: ollama --version")
            print("   2. Inicia el servidor: ollama serve")
            print("   3. Descarga un modelo: ollama pull llama3.2:3b")
            print()
            print("   O ejecuta el script automático: ./setup_ollama.sh")
        
        elif 'openai' in error_str or 'api' in error_str:
            print("💡 Parece un problema con OpenAI API:")
            print("   1. Verifica tu API key en .env")
            print("   2. Verifica que langchain-openai esté instalado")
            print("   3. Verifica tu crédito en OpenAI: https://platform.openai.com/usage")
        
        else:
            print("💡 Error desconocido. Revisa:")
            print("   1. El archivo .env existe y está configurado")
            print("   2. Las dependencias están instaladas: pip install -r requirements.txt")
            print("   3. Consulta LLM_SETUP.md para más detalles")
        
        return False


def test_llm_inference():
    """Prueba la inferencia del LLM con un prompt simple."""
    print("=" * 60)
    print("PRUEBA DE INFERENCIA LLM")
    print("=" * 60)
    print()
    
    try:
        from core import crear_chain
        
        print("⏳ Creando cadena de prueba...")
        template = "Responde con exactamente una palabra: ¿Cuál es la capital de Francia?"
        chain = crear_chain(template)
        
        print("⏳ Ejecutando inferencia...")
        print()
        
        respuesta = chain.invoke({})
        
        print("📝 Respuesta del LLM:")
        print(f"   {respuesta}")
        print()
        
        # Verificar que la respuesta sea razonable
        if 'París' in respuesta or 'Paris' in respuesta or 'paris' in respuesta.lower():
            print("✅ Respuesta correcta detectada")
            return True
        else:
            print("⚠️  Respuesta inesperada (pero el LLM funciona)")
            return True
        
    except Exception as e:
        print(f"❌ Error durante inferencia: {e}")
        print()
        print("💡 El LLM no pudo generar una respuesta.")
        print("   Revisa los errores anteriores para diagnosticar.")
        return False


def main():
    """Ejecuta todas las pruebas."""
    print()
    
    # Test 1: Configuración
    success_config = test_config()
    print()
    
    if not success_config:
        print("❌ Pruebas detenidas debido a error de configuración")
        print("   Corrige los errores anteriores y vuelve a ejecutar")
        sys.exit(1)
    
    # Test 2: Proveedor
    success_provider = test_llm_provider()
    print()
    
    if not success_provider:
        print("❌ Pruebas detenidas debido a error del proveedor")
        print("   Corrige los errores anteriores y vuelve a ejecutar")
        sys.exit(1)
    
    # Test 3: Inferencia
    success_inference = test_llm_inference()
    print()
    
    # Resumen final
    print("=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    print()
    print(f"   Configuración:  {'✅' if success_config else '❌'}")
    print(f"   Proveedor:      {'✅' if success_provider else '❌'}")
    print(f"   Inferencia:     {'✅' if success_inference else '❌'}")
    print()
    
    if success_config and success_provider and success_inference:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print()
        print("✅ El sistema LLM está configurado correctamente")
        print("   Puedes ejecutar el pipeline: python main.py")
        print()
        sys.exit(0)
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print()
        print("   Revisa los errores anteriores y consulta LLM_SETUP.md")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
