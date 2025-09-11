# Módulo de Análisis de Subjetividad

Este módulo proporciona herramientas completas para el análisis de subjetividad en opiniones turísticas, incluyendo análisis granular por frases para identificar opiniones mixtas.

## Estructura del Módulo

### Módulos Principales

- **`analizador_huggingface_subjetividad.py`**: Análisis básico de subjetividad usando modelos de HuggingFace
- **`analizador_opiniones_mixtas.py`**: Análisis granular por frases para identificar contenido mixto
- **`cargador_datos.py`**: Utilidades para cargar y preparar datasets
- **`visualizaciones_mixtas.py`**: Visualizaciones específicas para opiniones mixtas
- **`utils_subjetividad.py`**: Funciones auxiliares y utilidades generales

### Configuración

- **`base_subjetividad.py`**: Configuraciones base y constantes
- **`visualizaciones_subjetividad.py`**: Visualizaciones generales de subjetividad

## Uso Principal

### Análisis Completo de Opiniones Mixtas

```python
from subjetividad import analizar_opiniones_mixtas, cargar_dataset_para_subjetividad

# Cargar dataset
df, fuente = cargar_dataset_para_subjetividad('../data/processed/')

# Análisis completo con visualizaciones
df_resultado = analizar_opiniones_mixtas(
    df,
    columna_texto='TituloReview',
    mostrar_ejemplos=True,
    n_ejemplos=3
)
```

### Análisis Paso a Paso

```python
from subjetividad import (
    AnalizadorOpinionesMixtas,
    mostrar_resumen_ejecutivo,
    mostrar_conclusiones_hipotesis,
    visualizar_distribucion_tipos
)

# Configurar analizador
analizador = AnalizadorOpinionesMixtas()
analizador.configurar_modelos()

# Procesar dataset
df_analisis = analizador.procesar_dataset(df)

# Obtener estadísticas
estadisticas = analizador.obtener_estadisticas_mixtas(df_analisis)
validacion = analizador.validar_hipotesis(estadisticas)

# Visualizaciones y resúmenes
visualizar_distribucion_tipos(df_analisis)
mostrar_resumen_ejecutivo(estadisticas)
mostrar_conclusiones_hipotesis(validacion, estadisticas)
```

## Funciones Disponibles

### Carga de Datos
- `cargar_dataset_para_subjetividad()`: Carga automática del dataset más apropiado
- `mostrar_info_dataset()`: Información básica del dataset
- `verificar_compatibilidad_cuda()`: Verificación de aceleración GPU

### Análisis
- `analizar_opiniones_mixtas()`: Función principal para análisis completo
- `AnalizadorOpinionesMixtas`: Clase principal para análisis granular
- `AnalizadorHuggingFaceSubjetividad`: Análisis básico de subjetividad

### Visualizaciones
- `visualizar_distribucion_tipos()`: Gráficos de distribución de tipos de opiniones
- `mostrar_resumen_ejecutivo()`: Resumen estadístico completo
- `mostrar_conclusiones_hipotesis()`: Conclusiones sobre validación de hipótesis

### Utilidades
- `exportar_dataset_con_subjetividad()`: Exportar resultados
- `limpiar_texto_opiniones()`: Limpieza de textos

## Tipos de Opiniones Identificadas

1. **Subjetivo**: Solo contiene frases subjetivas (opiniones, emociones)
2. **Objetivo**: Solo contiene frases objetivas (información factual)
3. **Mixta**: Contiene al menos una frase subjetiva Y una objetiva

## Metodología de Análisis Mixto

1. **Segmentación**: División automática en frases usando WtP-Split
2. **Clasificación**: Análisis individual de cada frase con modelos de subjetividad
3. **Agregación**: Determinación del tipo de opinión basado en composición de frases
4. **Validación**: Evaluación estadística de la hipótesis de opiniones mixtas

## Dependencias Principales

- `transformers`: Modelos de HuggingFace para clasificación
- `wtpsplit`: Segmentación inteligente de oraciones
- `torch`: Aceleración GPU (opcional)
- `pandas`: Manipulación de datos
- `matplotlib`: Visualizaciones

## Ejemplo de Resultado

El análisis produce un DataFrame con las siguientes columnas adicionales:

- `TotalFrases`: Número total de frases en la opinión
- `FrasesSubjetivas`: Número de frases clasificadas como subjetivas
- `FrasesObjetivas`: Número de frases clasificadas como objetivas
- `TipoOpinion`: Clasificación final (Subjetivo/Objetivo/Mixta)
- `EsMixta`: Booleano indicando si es una opinión mixta
- `PorcentajeSubjetivo`: Porcentaje de contenido subjetivo
- `PorcentajeObjetivo`: Porcentaje de contenido objetivo
