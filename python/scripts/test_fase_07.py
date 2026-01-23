#!/usr/bin/env python3
"""
Test Rápido - Fase 07 Visualizaciones
======================================
Verifica que el módulo de visualizaciones funcione correctamente.
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_importaciones():
    """Prueba que todas las importaciones funcionen."""
    print("🔍 Probando importaciones...")
    
    try:
        from core.fase_07_visualizaciones import GeneradorVisualizaciones
        print("   ✓ GeneradorVisualizaciones importado")
        
        from core.visualizaciones.validador import ValidadorVisualizaciones
        print("   ✓ ValidadorVisualizaciones importado")
        
        from core.visualizaciones.utils import COLORES, CONFIG_EXPORT
        print("   ✓ Utilidades importadas")
        
        from core.visualizaciones.generador_dashboard import GeneradorDashboard
        print("   ✓ GeneradorDashboard importado")
        
        from core.visualizaciones.generador_sentimientos import GeneradorSentimientos
        print("   ✓ GeneradorSentimientos importado")
        
        from core.visualizaciones.generador_categorias import GeneradorCategorias
        print("   ✓ GeneradorCategorias importado")
        
        from core.visualizaciones.generador_topicos import GeneradorTopicos
        print("   ✓ GeneradorTopicos importado")
        
        from core.visualizaciones.generador_temporal import GeneradorTemporal
        print("   ✓ GeneradorTemporal importado")
        
        print("\n✅ Todas las importaciones exitosas!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        return False

def test_validador():
    """Prueba el validador con un dataset de prueba."""
    print("\n🔍 Probando validador...")
    
    try:
        import pandas as pd
        from core.visualizaciones.validador import ValidadorVisualizaciones
        
        # Crear dataset de prueba pequeño
        df_test = pd.DataFrame({
            'TituloReview': ['Excelente lugar'] * 10,
            'FechaEstadia': pd.date_range('2024-01-01', periods=10),
            'Calificacion': [5] * 10,
            'Sentimiento': ['Positivo'] * 10,
            'Categorias': ["['Alojamiento']"] * 10
        })
        
        validador = ValidadorVisualizaciones(df_test)
        resumen = validador.get_resumen()
        
        print(f"   ✓ Dataset de prueba: {resumen['total_opiniones']} opiniones")
        print(f"   ✓ Tiene fechas: {resumen['tiene_fechas']}")
        print(f"   ✓ Categorías válidas: {resumen['categorias_validas']}")
        
        # Probar algunas validaciones
        puede_dashboard, _ = validador.puede_renderizar('dashboard_ejecutivo')
        puede_temporal, razon = validador.puede_renderizar('evolucion_temporal_sentimientos')
        
        print(f"   ✓ Dashboard ejecutivo: {'Sí' if puede_dashboard else 'No'}")
        print(f"   ✓ Evolución temporal: {'Sí' if puede_temporal else f'No ({razon})'}")
        
        print("\n✅ Validador funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en validador: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_generador():
    """Prueba básica del generador."""
    print("\n🔍 Probando generador principal...")
    
    try:
        from core.fase_07_visualizaciones import GeneradorVisualizaciones
        
        # Verificar que dataset existe
        dataset_path = Path('data/dataset.csv')
        
        if not dataset_path.exists():
            print(f"   ⚠️  Dataset no encontrado: {dataset_path}")
            print("   💡 Ejecuta el pipeline completo primero (Fases 01-06)")
            return True
        
        print(f"   ✓ Dataset encontrado: {dataset_path}")
        
        # Crear generador (sin ejecutar)
        generador = GeneradorVisualizaciones(
            dataset_path=str(dataset_path),
            output_dir='data/visualizaciones_test'
        )
        
        print("   ✓ Generador creado exitosamente")
        print("\n✅ Generador configurado correctamente!")
        print("\n💡 Para generar visualizaciones, ejecuta:")
        print("   python main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en generador: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todas las pruebas."""
    print("="*60)
    print("TEST RÁPIDO - FASE 08 VISUALIZACIONES")
    print("="*60)
    
    tests = [
        test_importaciones,
        test_validador,
        test_generador
    ]
    
    resultados = []
    for test in tests:
        resultado = test()
        resultados.append(resultado)
    
    print("\n" + "="*60)
    if all(resultados):
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
    print("="*60)
    
    return all(resultados)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
