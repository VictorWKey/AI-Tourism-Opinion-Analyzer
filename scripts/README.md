# 🔧 Módulos Técnicos - Análisis de Datos Turísticos

Este directorio contiene los **módulos core** del sistema de análisis automatizado de opiniones turísticas. Implementa una arquitectura modular que separa claramente las responsabilidades de procesamiento y análisis.

## 📁 Estructura de Módulos

### 📊 `procesamiento_datos.py`
**Funciones que SÍ modifican el dataset**

Este módulo contiene todas las funciones necesarias para limpiar, transformar y procesar los datos:

#### Funciones principales:
- `cargar_datos_turisticos()`: Carga y consolida archivos CSV de todas las ciudades
- `convertir_fechas()`: Convierte fechas en español a formato datetime
- `limpiar_columna_origen_autor()`: Limpia nombres personales de la columna OrigenAutor
- `completar_valores_nulos()`: Rellena valores nulos con valores descriptivos
- `eliminar_duplicados()`: Elimina registros duplicados
- `examinar_y_corregir_contenidos_mal_ubicados()`: Corrige contenidos mal ubicados entre columnas
- `agregar_texto_consolidado()`: Crea columna con texto narrativo consolidado
- `guardar_dataset_procesado()`: Guarda el dataset final procesado
- **`procesar_dataset_completo()`**: **Pipeline completo que ejecuta todos los pasos**

#### Uso típico:
```python
import procesamiento_datos as proc

# Ejecutar pipeline completo
df_limpio = proc.procesar_dataset_completo('../data')

# O usar funciones individuales
df = proc.cargar_datos_turisticos('../data')
df = proc.convertir_fechas(df)
df = proc.limpiar_columna_origen_autor(df)
# ... etc
```

### 🔍 `exploracion_datos.py`
**Funciones que NO modifican el dataset**

Este módulo contiene funciones para análisis descriptivo y exploratorio sin modificar los datos:

#### Funciones principales:
- `analizar_informacion_general()`: Información básica del dataset
- `analizar_valores_nulos()`: Análisis de valores faltantes
- `analizar_duplicados()`: Detección de duplicados (sin eliminar)
- `analizar_distribuciones_categoricas()`: Distribuciones por ciudad, atracción, tipo de viaje
- `analizar_calificaciones()`: Estadísticas de calificaciones
- `analizar_longitud_textos()`: Análisis de longitud de títulos y reviews
- `analizar_temporal()`: Análisis de fechas y tendencias temporales
- `detectar_contenidos_mal_ubicados()`: Detecta contenidos mal ubicados entre columnas
- `resumen_ejecutivo()`: Resumen general del análisis
- `analisis_final_completo()`: Análisis exhaustivo del dataset limpio
- `verificar_ejemplos_texto_consolidado()`: Verifica ejemplos de texto consolidado

#### Uso típico:
```python
import exploracion_datos as exp

# Análisis individual
exp.analizar_informacion_general(df)
exp.analizar_distribuciones_categoricas(df)
exp.analizar_calificaciones(df)

# Análisis completo
exp.analisis_final_completo(df)
```

## Flujo de Trabajo Recomendado

### 1. Procesamiento (Una sola vez)
```python
import procesamiento_datos as proc

# Ejecutar pipeline completo de procesamiento
df_limpio = proc.procesar_dataset_completo('../data')
```

### 2. Análisis Exploratorio (Repetible)
```python
import exploracion_datos as exp

# Crear copia para análisis
df_analisis = df_limpio.copy()

# Ejecutar análisis específicos
exp.analizar_informacion_general(df_analisis)
exp.analizar_distribuciones_categoricas(df_analisis)
exp.resumen_ejecutivo(df_analisis)
```

## ⚙️ Arquitectura del Sistema

### 🧩 **Separación de Responsabilidades**

El diseño modular implementa el principio de **separación de responsabilidades** (SoC):

- **🔄 Procesamiento**: Funciones que **modifican** el estado de los datos
- **📊 Exploración**: Funciones que **analizan** sin modificar los datos
- **🕷️ Extracción**: Funciones de **web scraping** y recolección
- **📓 Interface**: Notebooks para **interacción** y visualización

### 🏗️ **Patrón de Diseño**

```
📊 datos_crudos → 🔄 procesamiento → 📊 datos_limpios → 📈 análisis → 💡 insights
```

## 📄 Documentación de Módulos

### ✅ **Código Modular**
- Funciones especializadas por propósito
- Fácil mantenimiento y actualización
- Reutilización en diferentes proyectos

### ✅ **Separación de Responsabilidades**
- **Procesamiento**: Solo modifica datos
- **Exploración**: Solo analiza datos
- Evita modificaciones accidentales

### ✅ **Notebook Más Limpio**
- Código reducido de ~50 celdas a ~10 celdas
- Enfoque en resultados, no en implementación
- Más fácil de leer y entender

### ✅ **Escalabilidad**
- Fácil agregar nuevas funciones de análisis
- Pipeline de procesamiento extensible
- Documentación centralizada

## Archivos Generados

### `dataset_opiniones_consolidado.csv`
Dataset final procesado que incluye:
- **Datos limpios**: Sin duplicados, valores nulos completados
- **Fechas convertidas**: Formato datetime estándar
- **OrigenAutor limpio**: Solo ubicaciones geográficas válidas
- **texto_consolidado**: Narrativa completa para análisis de sentimientos

### Columnas del dataset final:
1. `Titulo`: Título de la opinión
2. `Review`: Texto completo de la reseña
3. `TipoViaje`: Tipo de viaje (Familia, Pareja, Amigos, etc.)
4. `Calificacion`: Calificación numérica (1-5)
5. `OrigenAutor`: Origen geográfico del autor
6. `FechaOpinion`: Fecha de la opinión (datetime)
7. `FechaEstadia`: Fecha de la estadía (datetime)
8. `ciudad`: Ciudad de la atracción
9. `atraccion`: Nombre de la atracción
10. `texto_consolidado`: **Nueva columna** con narrativa completa

## Próximos Pasos

Con el dataset procesado, ahora se puede proceder a:

1. **Análisis de sentimientos** usando la columna `texto_consolidado`
2. **Modelado de machine learning** para predicción de calificaciones
3. **Visualizaciones avanzadas** con los datos limpios
4. **Reportes automáticos** usando las funciones de exploración

## Ejemplo de Uso Completo

```python
# 1. Importar módulos
import sys
sys.path.append('../scripts')
import procesamiento_datos as proc
import exploracion_datos as exp

# 2. Procesar datos (una vez)
df_opiniones = proc.procesar_dataset_completo('../data')

# 3. Análisis exploratorio
df_analisis = df_opiniones.copy()
exp.analizar_informacion_general(df_analisis)
exp.analizar_distribuciones_categoricas(df_analisis)
exp.analisis_final_completo(df_analisis)
```
