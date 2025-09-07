# Módulo de Etiquetado de Subjetividad

Este módulo contiene todas las funciones necesarias para clasificar reseñas turísticas según su nivel de subjetividad usando LangChain y GPT-4o-mini.

## Estructura del Módulo

```
etiquetado/
├── __init__.py                     # Importaciones principales del módulo
├── configuracion.py               # Configuración de modelos y API
├── cargador_datos.py              # Funciones para cargar datasets
├── clasificador.py                # Lógica de clasificación con checkpoints
├── analizador.py                  # Análisis estadístico de resultados
├── visualizador.py                # Creación de gráficos y visualizaciones
├── guardador.py                   # Guardado de resultados y reportes
├── utils_etiquetado.py            # Utilidades y funciones de conveniencia
├── demo_etiquetado.py             # Script de demostración
└── README.md                      # Este archivo
```

## Categorías de Clasificación

El módulo clasifica las reseñas en tres categorías:

- **Objetiva**: Contiene únicamente hechos verificables, datos concretos o información medible
- **Subjetiva**: Contiene opiniones, juicios personales, sentimientos o percepciones del turista
- **Mixta**: Combina hechos verificables con opiniones o percepciones del turista

## Uso Básico

### Importación del módulo

```python
import sys
sys.path.append('../scripts')

from etiquetado import (
    cargar_datasets, configurar_clasificador,
    proceso_completo_clasificacion
)
```

### Uso completo (recomendado)

```python
# 1. Cargar datos
df_reviews = cargar_datasets()

# 2. Configurar clasificador
clasificador = configurar_clasificador()

# 3. Proceso completo automático
df_clasificado, df_analizado, guardado_ok = proceso_completo_clasificacion(
    df_reviews, clasificador
)
```

### Uso paso a paso

```python
# Configuración
configurar_entorno()
verificar_api_key()

# Carga de datos
df_reviews = cargar_datasets()
clasificador = configurar_clasificador()

# Clasificación
df_clasificado = clasificar_reviews(df_reviews, clasificador)

# Análisis
df_analizado = analizar_resultados(df_clasificado)

# Visualización
crear_visualizaciones(df_analizado)

# Guardado
guardar_resultados(df_clasificado)
generar_resumen_final(df_analizado)
```

## Funciones Principales

### Configuración
- `configurar_entorno()`: Configura matplotlib y suprimi warnings
- `verificar_api_key()`: Verifica la configuración de OpenAI
- `configurar_clasificador()`: Configura el modelo GPT-4o-mini

### Datos
- `cargar_datasets()`: Carga datasets de Cancún y CDMX
- `cargar_muestra_prueba(df, n)`: Crea muestra para pruebas

### Clasificación
- `clasificar_reviews(df, clasificador)`: Clasifica todas las reseñas
- `prueba_rapida(df, clasificador, n)`: Prueba con pocas reseñas
- `verificar_checkpoint()`: Verifica progreso guardado
- `limpiar_checkpoint()`: Elimina progreso guardado

### Análisis
- `analizar_resultados(df)`: Análisis estadístico completo
- `mostrar_opiniones_por_categoria(df)`: Muestra opiniones por categoría

### Visualización
- `crear_visualizaciones(df)`: Crea gráficos completos
- `crear_grafico_simple(df, tipo)`: Gráfico simple ('barras' o 'pastel')

### Guardado
- `guardar_resultados(df)`: Guarda CSV con clasificaciones
- `generar_resumen_final(df)`: Muestra resumen en consola
- `generar_reporte_completo(df1, df2)`: Genera reporte TXT
- `exportar_estadisticas_json(df)`: Exporta estadísticas JSON

## Características Especiales

### Guardado Automático
El módulo incluye un sistema de checkpoints que guarda el progreso automáticamente:
- Guardado cada 50 reseñas clasificadas (configurable)
- Recuperación automática en caso de interrupción
- Gestión de errores sin pérdida de progreso

### Manejo de Errores
- Reintento automático en caso de errores de API
- Clasificación de errores para análisis posterior
- Continuación del proceso sin interrupciones críticas

### Optimización
- Procesamiento por lotes para mejor rendimiento
- Configuración de temperatura=0 para resultados determinísticos
- Límite de tokens optimizado para clasificación

## Requisitos

### Dependencias Python
```
pandas
numpy
matplotlib
seaborn
langchain-openai
langchain-core
pydantic
tqdm
python-dotenv
```

### Configuración de API
Crear archivo `.env` en la raíz del proyecto:
```
OPENAI_API_KEY=tu_api_key_aqui
```

## Archivos de Salida

El módulo genera los siguientes archivos:

- `reviews_clasificadas_subjetividad.csv`: Dataset con clasificaciones
- `reporte_clasificacion.txt`: Reporte completo en texto
- `estadisticas_clasificacion.json`: Estadísticas en formato JSON
- `checkpoint_clasificacion.pkl`: Archivo temporal de progreso

## Ejemplo de Script

Ver `demo_etiquetado.py` para un ejemplo completo de uso del módulo.

## Integración con Notebook

El módulo está diseñado para ser usado desde el notebook `03-etiquetado-opiones-subjetividad.ipynb`, que ahora es mucho más compacto y fácil de usar.

## Notas de Desarrollo

- Cada script es independiente y modular
- Funciones bien documentadas con docstrings
- Manejo consistente de errores
- Logging informativo para el usuario
- Código optimizado para reutilización

## Soporte

Para problemas o dudas:
1. Verifica que todas las dependencias estén instaladas
2. Confirma que la API key de OpenAI esté configurada
3. Revisa los archivos de log para errores específicos
4. Usa `validar_dependencias()` para diagnosticar problemas
