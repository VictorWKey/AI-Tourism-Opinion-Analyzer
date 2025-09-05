"""
Módulo para procesamiento de datos turísticos.
REFACTORIZADO: Este módulo usa la nueva estructura modular.
Para mantener compatibilidad, expone las funciones principales.
"""

from procesamiento import (
    CargadorDatos,
    LimpiadorDatos,
    TransformadorDatos,
    ValidadorDatos,
    capitalizar_palabras,
    extraer_nombre_atraccion,
    procesar_dataset_completo
)


# Funciones de compatibilidad que mantienen la interfaz original
def cargar_datos_turisticos(ruta_data='../data'):
    """Función de compatibilidad - usa CargadorDatos"""
    cargador = CargadorDatos(ruta_data)
    return cargador.cargar_datos_turisticos()


def convertir_fechas(df):
    """Función de compatibilidad - usa TransformadorDatos"""
    transformador = TransformadorDatos(df)
    return transformador.convertir_fechas()


def limpiar_columna_origen_autor(df):
    """Función de compatibilidad - usa LimpiadorDatos"""
    limpiador = LimpiadorDatos(df)
    return limpiador.limpiar_columna_origen_autor()


def completar_valores_nulos(df):
    """Función de compatibilidad - usa LimpiadorDatos"""
    limpiador = LimpiadorDatos(df)
    return limpiador.completar_valores_nulos()


def eliminar_duplicados(df):
    """Función de compatibilidad - usa LimpiadorDatos"""
    limpiador = LimpiadorDatos(df)
    return limpiador.eliminar_duplicados()


def examinar_y_corregir_contenidos_mal_ubicados(df):
    """Función de compatibilidad - usa ValidadorDatos"""
    validador = ValidadorDatos(df)
    return validador.examinar_y_corregir_contenidos_mal_ubicados()


def agregar_texto_consolidado(df):
    """Función de compatibilidad - usa TransformadorDatos"""
    transformador = TransformadorDatos(df)
    return transformador.agregar_texto_consolidado()


def guardar_dataset_procesado(df, nombre_archivo='dataset_opiniones_consolidado.csv', ruta='../data/processed/'):
    """Función de compatibilidad - usa ValidadorDatos"""
    validador = ValidadorDatos(df)
    return validador.guardar_dataset_procesado(nombre_archivo, ruta)


# Funciones auxiliares adicionales para conversión de fechas (compatibilidad)
def convertir_fecha_opinion(fecha_str):
    """Función de compatibilidad - usa TransformadorDatos internamente"""
    import pandas as pd
    transformador = TransformadorDatos(pd.DataFrame())
    return transformador.convertir_fecha_opinion(fecha_str)


def convertir_fecha_estadia(fecha_str):
    """Función de compatibilidad - usa TransformadorDatos internamente"""
    import pandas as pd
    transformador = TransformadorDatos(pd.DataFrame())
    return transformador.convertir_fecha_estadia(fecha_str)


def limpiar_origen_autor(valor):
    """Función de compatibilidad - usa LimpiadorDatos internamente"""
    import pandas as pd
    limpiador = LimpiadorDatos(pd.DataFrame())
    return limpiador.limpiar_origen_autor(valor)


def crear_texto_consolidado(row):
    """Función de compatibilidad - usa TransformadorDatos internamente"""
    import pandas as pd
    transformador = TransformadorDatos(pd.DataFrame())
    return transformador.crear_texto_consolidado(row)
