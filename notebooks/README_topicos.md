# Análisis de Tópicos - BERTopic vs FASTopic

Esta carpeta contiene dos implementaciones de modelado de tópicos para el análisis de opiniones turísticas:

## 📋 Notebooks Disponibles

### 07-modelado-de-topicos-con-bertopic.ipynb
- **Método**: BERTopic (clustering-based)
- **Características**:
  - Usa UMAP + HDBSCAN para clustering
  - Genera visualizaciones interactivas
  - Configuración automática inteligente
  - Integración con LLM para nomenclatura

### 08-modelado-de-topicos-con-fastopic.ipynb  
- **Método**: FASTopic (optimal transport-based)
- **Características**:
  - Más rápido en entrenamiento
  - Basado en transporte óptimo
  - Mejor para textos cortos
  - Configuración automática adaptativa
  - Comparación directa con BERTopic

## 🚀 Cómo Usar

### Prerequisitos
```bash
# Instalar dependencias adicionales
pip install fastopic topmost
```

### Uso Básico
1. **Seleccionar ciudad** en la variable `CIUDAD_ANALIZAR`
2. **Ejecutar notebook** completo  
3. **Resultados se guardan** automáticamente en el dataset principal

### Configuración por Ciudad
```python
CIUDAD_ANALIZAR = "Puerto_vallarta"  # Cambiar aquí
# Opciones: "Cancun", "CDMX", "Mazatlan", "Puebla", "Puerto_vallarta"
```

## 📊 Comparación de Métodos

| Aspecto | BERTopic | FASTopic |
|---------|----------|----------|
| **Velocidad** | Más lento | ⚡ Más rápido |
| **Textos cortos** | Bueno | 🎯 Excelente |
| **Visualizaciones** | Ricas e interactivas | Específicas y claras |
| **Configuración** | Automática | 🤖 Ultra-inteligente |
| **Estabilidad** | Dependiente de clustering | ✅ Más estable |

## 🔧 Arquitectura Modular

### Scripts Utilizados
```
scripts/topicos/
├── configurador_fastopic.py     # Configuración automática FASTopic
├── analizador_caracteristicas.py # Configuración automática BERTopic  
├── clasificador_topicos_llm.py  # Nomenclatura con LLM
├── utils_topicos.py             # Utilidades compartidas
└── limpieza_texto_mejorado.py   # Preprocesamiento avanzado
```

### Flujo de Procesamiento
1. **Carga de datos** → Filtro por ciudad
2. **Limpieza de texto** → spaCy + lematización
3. **Configuración automática** → Análisis del corpus
4. **Entrenamiento** → BERTopic o FASTopic
5. **Nomenclatura LLM** → GPT-4o-mini para nombres
6. **Visualizaciones** → Gráficos + comparaciones
7. **Guardado** → Dataset actualizado automáticamente

## 📈 Resultados

### Columnas Generadas
- `TopicoConBERTopic`: Nombres de tópicos de BERTopic
- `TopicoConFASTopic`: Nombres de tópicos de FASTopic  
- `TituloReviewLimpio`: Texto preprocesado (si no existe)

### Estadísticas Mostradas
- Distribución de tópicos por ciudad
- Relación con sentimientos y subjetividad
- Comparación entre métodos
- Ejemplos representativos por tópico
- Métricas de calidad y tiempo

## 💡 Recomendaciones de Uso

### Cuándo usar BERTopic
- Análisis exploratorio inicial
- Datasets grandes (>1000 textos)
- Necesitas visualizaciones interactivas detalladas
- Textos largos y diversos

### Cuándo usar FASTopic  
- Análisis rápido y eficiente
- Textos cortos (títulos, reseñas breves)
- Comparación con otros métodos
- Producción con restricciones de tiempo

### Flujo Recomendado
1. **Ejecutar BERTopic** primero para análisis base
2. **Ejecutar FASTopic** para comparación
3. **Analizar diferencias** en distribuciones
4. **Seleccionar método** según necesidades

## 🔄 Procesamiento por Ciudades

### Estado de Progreso
- ✅ Puerto Vallarta (completo en ambos)
- ⏳ Otras ciudades (ejecutar manualmente)

### Procesamiento Masivo
Para procesar todas las ciudades:
```python
ciudades = ["Cancun", "CDMX", "Mazatlan", "Puebla", "Puerto_vallarta"]
for ciudad in ciudades:
    CIUDAD_ANALIZAR = ciudad
    # Ejecutar análisis...
```

## 📋 Próximos Pasos

1. **Comparar resultados** entre BERTopic y FASTopic
2. **Analizar concordancia** en tópicos identificados  
3. **Evaluar calidad** con métricas específicas
4. **Implementar ensemble** de ambos métodos
5. **Crear dashboard** con resultados integrados