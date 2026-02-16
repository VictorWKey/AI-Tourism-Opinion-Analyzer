# 📊 Módulo de Visualizaciones - Fase 08

## Arquitectura Modular

El módulo genera **solo visualizaciones gráficas puras** (charts, plots, word clouds).
Los datos textuales (KPIs, resúmenes, fortalezas/debilidades, validación del dataset)
se exportan a `insights_textuales.json` para ser consumidos por una sección separada en la UI.

```
core/
├── fase_08_visualizaciones.py      # 🎯 ORQUESTADOR PRINCIPAL
└── visualizaciones/
    ├── __init__.py                 # Exportaciones del módulo
    ├── utils.py                    # 🎨 Colores, estilos, utilidades
    ├── validador.py                # ✅ Sistema de validación inteligente
    ├── exportador_insights.py      # 📝 Exportador de insights textuales a JSON
    ├── generador_dashboard.py      # 📈 Sección 1: Dashboard (1 viz, 4 cuadrantes)
    ├── generador_sentimientos.py   # 😊 Sección 2: Sentimientos (8 viz)
    ├── generador_categorias.py     # 🏷️  Sección 3: Categorías (4 viz)
    ├── generador_topicos.py        # 🔍 Sección 4: Tópicos (2 viz)
    ├── generador_temporal.py       # 📅 Sección 5: Temporal (2 viz)
    ├── generador_texto.py          # 📝 Sección 6: Texto (4 viz)
    └── generador_combinados.py     # 🔗 Sección 7: Combinados (5 viz)
```

## 🎯 Componentes Principales

### 1. **Orquestador Principal** (`fase_08_visualizaciones.py`)
Clase `GeneradorVisualizaciones` que:
- Carga y valida el dataset
- Coordina todos los generadores especializados
- Gestiona la creación de carpetas de salida
- Genera el reporte final en JSON

### 2. **Sistema de Validación** (`validador.py`)
Clase `ValidadorVisualizaciones` que:
- Analiza características del dataset (volumen, fechas, tópicos, etc.)
- Decide qué visualizaciones son viables
- Evita generar gráficos vacíos o poco significativos
- Proporciona razones cuando una visualización es omitida

### 3. **Generadores Especializados**
Cada generador se enfoca en un tipo de análisis:

#### `GeneradorDashboard`
- ✅ Resumen de validación del dataset
- 📊 Dashboard ejecutivo (4 cuadrantes)
- 🎯 KPIs principales

#### `GeneradorSentimientos`
- 🥧 Distribución de sentimientos (donut chart)
- 📈 Evolución temporal de sentimientos
- 📊 Sentimientos por calificación
- ☁️ Nubes de palabras por sentimiento (3)
- 🔄 Comparación de palabras positivas vs negativas
- 📊 Sentimiento vs subjetividad

#### `GeneradorCategorias`
- 📊 Top categorías mencionadas
- 🎨 Sentimientos por categoría (stacked bars)
- ⚖️ Fortalezas vs debilidades (diverging bars)
- 🕸️ Radar chart 360° del destino

#### `GeneradorTopicos`
- 🔝 Top 10 subtópicos más mencionados
- ⚠️ Top 10 subtópicos problemáticos

#### `GeneradorTemporal`
- 📅 Volumen de opiniones en el tiempo
- 📈 Evolución de sentimientos temporales

### 4. **Exportador de Insights** (`exportador_insights.py`)
- 📝 Exporta KPIs, fortalezas, debilidades a JSON
- 📋 Exporta validación del dataset y recomendaciones
- 📄 Incluye resúmenes LLM (descriptivo, estructurado, insights)
- 🎯 Todo en `insights_textuales.json` para la UI

### 5. **Utilidades** (`utils.py`)
- 🎨 Paletas de colores consistentes
- 📐 Estilos y configuraciones de exportación
- 🛠️ Funciones helper (guardar_figura, truncar_texto, etc.)

## 📂 Estructura de Salida

```
data/visualizaciones/
├── insights_textuales.json         # 📝 KPIs, resúmenes, fortalezas/debilidades
├── reporte_generacion.json         # 📋 Reporte de generación
├── 01_sentimientos/
│   ├── distribucion_sentimientos.png
│   ├── evolucion_temporal_sentimientos.png
│   ├── sentimientos_por_calificacion.png
│   ├── wordcloud_positivo.png
│   ├── wordcloud_neutro.png
│   ├── wordcloud_negativo.png
│   ├── top_palabras_comparacion.png
│   └── sentimiento_vs_subjetividad.png
├── 03_categorias/
│   ├── top_categorias.png
│   ├── sentimientos_por_categoria.png
│   ├── fortalezas_vs_debilidades.png
│   └── radar_chart_360.png
├── 04_topicos/
│   ├── top_subtopicos_mencionados.png
│   └── top_subtopicos_problematicos.png
├── 05_temporal/
│   ├── volumen_opiniones_tiempo.png
│   └── evolucion_sentimientos.png
├── 06_texto/
│   ├── wordcloud_general.png
│   ├── distribucion_longitud.png
│   ├── top_bigramas.png
│   └── top_trigramas.png
└── 07_combinados/
    ├── sentimiento_subjetividad_categoria.png
    ├── calificacion_categoria_sentimiento.png
    ├── volumen_vs_sentimiento_scatter.png
    ├── correlacion_calificacion_sentimiento.png
    └── distribucion_categorias_calificacion.png
```

## 🚀 Uso

### Desde el Pipeline Completo
```python
# En main.py (ya integrado)
from core import GeneradorVisualizaciones

generador_viz = GeneradorVisualizaciones()
generador_viz.procesar()
```

### Uso Standalone
```python
from core.fase_08_visualizaciones import GeneradorVisualizaciones

# Generar con dataset específico
generador = GeneradorVisualizaciones(
    dataset_path='data/dataset.csv',
    output_dir='data/visualizaciones'
)
generador.procesar()
```

## 🧠 Sistema de Validación Inteligente

El validador analiza el dataset y decide qué visualizaciones generar según:

### Criterios de Validación
- **Volumen mínimo**: Cada visualización tiene un umbral mínimo de opiniones
- **Datos requeridos**: Verifica columnas necesarias (fechas, tópicos, etc.)
- **Calidad de datos**: Valida rango temporal, diversidad de sentimientos, etc.

### Ejemplos de Reglas
```python
# Evolución temporal requiere:
- Mínimo 30 opiniones
- Columna 'FechaEstadia' válida
- Rango temporal > 60 días

# Radar chart 360° requiere:
- Mínimo 50 opiniones
- Al menos 4 categorías activas
- Menciones suficientes por categoría

# Word clouds requieren:
- Mínimo 15 opiniones del sentimiento específico
```

## 📊 Reporte de Generación

Al finalizar, se genera `reporte_generacion.json`:

```json
{
  "fecha_generacion": "2025-11-09T...",
  "dataset": {
    "total_opiniones": 485,
    "tiene_fechas": true,
    "rango_temporal_dias": 240,
    "categorias_identificadas": 12,
    "cobertura_topicos": true
  },
  "visualizaciones": {
    "total_generadas": 18,
    "total_omitidas": 4,
    "por_seccion": {
      "dashboard": 3,
      "sentimientos": 7,
      "categorias": 4,
      "topicos": 2,
      "temporal": 2
    }
  },
  "omitidas": [
    {
      "nombre": "calendar_heatmap",
      "razon": "Requiere ≥100 opiniones y rango >90 días"
    }
  ],
  "recomendaciones": [
    "✓ Dataset completo y robusto..."
  ]
}
```

## 🎨 Personalización

### Modificar Colores
Edita `visualizaciones/utils.py`:
```python
COLORES = {
    'positivo': '#4CAF50',  # Cambiar verde
    'negativo': '#F44336',  # Cambiar rojo
    # ...
}
```

### Ajustar Umbrales de Validación
Edita `visualizaciones/validador.py`:
```python
reglas = {
    'evolucion_temporal': (
        self.tiene_fechas and self.n_opiniones >= 30,  # Cambiar 30
        'Requiere...'
    ),
    # ...
}
```

### Agregar Nueva Visualización
1. Edita el generador correspondiente
2. Añade la función `_generar_nueva_viz()`
3. Llámala desde `generar_todas()`
4. Añade regla de validación en `validador.py`

## 🔧 Dependencias Requeridas

Todas las dependencias de visualización están incluidas en el `requirements.txt` del proyecto:

```bash
pip install -r requirements.txt
```

Esto instalará:
- matplotlib>=3.7.0
- seaborn>=0.12.0
- plotly>=5.14.0
- kaleido>=0.2.1
- wordcloud>=1.9.0

## ✅ Testing

Probar con dataset mínimo:
```python
# Dataset con solo 20 opiniones
generador = GeneradorVisualizaciones(dataset_path='data/dataset_mini.csv')
generador.procesar()
# Solo generará visualizaciones básicas
```

Probar con dataset completo:
```python
# Dataset con 500+ opiniones
generador = GeneradorVisualizaciones(dataset_path='data/dataset.csv')
generador.procesar()
# Generará todas las visualizaciones avanzadas
```

## 🎯 Próximas Expansiones

El diseño modular permite agregar fácilmente:

- **Fase 09**: Generación de PDF compilando todas las visualizaciones
- **Fase 10**: Interfaz web interactiva (Streamlit/Gradio)
- **Sección 6**: Análisis de texto (bigramas, trigramas)
- **Sección 7**: Análisis combinados (matrices de correlación)

## 📝 Notas Técnicas

- **Memoria**: Las visualizaciones se generan y guardan una por una
- **Formato**: PNG de alta calidad (300 DPI)
- **Estilo**: Configurable globalmente en `utils.py`
- **Escalabilidad**: Funciona desde 10 hasta 100,000+ opiniones

---

**Versión**: 1.0  
**Fecha**: Noviembre 2025
