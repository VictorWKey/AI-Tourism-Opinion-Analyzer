"""
Módulo para exploración de datos turísticos.
REFACTORIZADO: Este módulo usa la nueva estructura modular.
Para mantener compatibilidad, expone las funciones principales.
"""

from exploracion import (
    AnalizadorGeneral,
    AnalizadorCategorico,
    AnalizadorTemporal,
    AnalizadorTexto,
    DetectorProblemas,
    cargar_dataset_completo,
    resumen_ejecutivo,
    analisis_final_completo
)


# Funciones de compatibilidad que mantienen la interfaz original
def analizar_informacion_general(df):
    """Función de compatibilidad - usa AnalizadorGeneral"""
    analizador = AnalizadorGeneral(df)
    return analizador.analizar_informacion_general()


def analizar_valores_nulos(df):
    """Función de compatibilidad - usa AnalizadorGeneral"""
    analizador = AnalizadorGeneral(df)
    return analizador.analizar_valores_nulos()


def analizar_duplicados(df):
    """Función de compatibilidad - usa AnalizadorGeneral"""
    analizador = AnalizadorGeneral(df)
    return analizador.analizar_duplicados()


def analizar_distribuciones_categoricas(df):
    """Función de compatibilidad - usa AnalizadorCategorico"""
    analizador = AnalizadorCategorico(df)
    return analizador.analizar_distribuciones_categoricas()


def analizar_calificaciones(df):
    """Función de compatibilidad - usa AnalizadorCategorico"""
    analizador = AnalizadorCategorico(df)
    return analizador.analizar_calificaciones()


def analizar_longitud_textos(df):
    """Función de compatibilidad - usa AnalizadorTexto"""
    analizador = AnalizadorTexto(df)
    return analizador.analizar_longitud_textos()


def analizar_temporal(df):
    """Función de compatibilidad - usa AnalizadorTemporal"""
    analizador = AnalizadorTemporal(df)
    return analizador.analizar_temporal()


def analizar_origen_autor(df):
    """Función de compatibilidad - usa AnalizadorCategorico"""
    analizador = AnalizadorCategorico(df)
    return analizador.analizar_origen_autor()


def detectar_contenidos_mal_ubicados(df, min_longitud=10):
    """Función de compatibilidad - usa DetectorProblemas"""
    detector = DetectorProblemas(df)
    return detector.detectar_contenidos_mal_ubicados(min_longitud)
