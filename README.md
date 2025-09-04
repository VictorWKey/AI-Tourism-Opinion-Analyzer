# 🏖️ Análisis Automatizado de Opiniones Turísticas

Un sistema completo de **extracción, procesamiento y análisis de opiniones turísticas** de TripAdvisor para destinos mexicanos, diseñado para obtener insights valiosos sobre experiencias de visitantes.

## 📋 Descripción del Proyecto

Este proyecto implementa un **pipeline end-to-end** para el análisis automatizado de opiniones turísticas que incluye:

- **🕷️ Web Scraping**: Extracción automatizada de reseñas de TripAdvisor
- **🧹 Procesamiento de Datos**: Limpieza, normalización y consolidación de información
- **📊 Análisis Exploratorio**: Análisis descriptivo y estadístico comprehensivo
- **📝 Preparación para ML**: Generación de datasets listos para análisis de sentimientos

### 🎯 Objetivos

1. **Automatizar la recolección** de opiniones turísticas de múltiples atracciones
2. **Procesar y limpiar** los datos para garantizar calidad y consistencia
3. **Analizar patrones** en las experiencias de los visitantes
4. **Preparar datasets** optimizados para análisis de sentimientos y machine learning
5. **Generar insights** accionables para el sector turístico

## 🏗️ Arquitectura del Sistema

```
📁 analisis-automatizado-de-opiniones-turisticas/
├── 📊 data/                          # Datos sin procesar y procesados
│   ├── cancun/                       # Opiniones de atracciones de Cancún
│   ├── cdmx/                         # Opiniones de atracciones de CDMX
│   └── dataset_opiniones_consolidado.csv  # Dataset final procesado
├── 📓 notebooks/                     # Análisis y exploración
│   └── 01-analisis_exploratorio_y_procesamiento_basico-de-datos.ipynb  # Notebook principal
├── 🔧 scripts/                       # Código fuente modular
│   ├── web_scrapping.py             # Extractor de datos de TripAdvisor
│   ├── procesamiento_datos.py       # Pipeline de limpieza y transformación
│   ├── exploracion_datos.py         # Funciones de análisis exploratorio
│   └── README.md                    # Documentación técnica
└── 📋 requirements.txt              # Dependencias del proyecto
```

## 🚀 Características Principales

### 🕷️ **Web Scraping Inteligente**
- Extracción automatizada de reseñas de TripAdvisor
- Manejo de rate limiting y detección anti-bot
- Extracción de metadatos completos (fechas, calificaciones, tipos de viaje)
- Soporte para múltiples atracciones y ciudades

### 🧹 **Procesamiento Basico de Datos**
- **Limpieza automática** de campos de texto
- **Normalización de fechas** en español a formato estándar
- **Filtrado inteligente** de información personal vs. geográfica
- **Detección y corrección** de contenidos mal ubicados
- **Eliminación de duplicados** y completado de valores faltantes

### 📊 **Análisis Exploratorio Comprehensivo**
- Análisis de **calidad y completitud** de datos
- **Distribuciones** por ciudades, atracciones y tipos de viaje
- Análisis **temporal** de tendencias en opiniones
- **Estadísticas descriptivas** de calificaciones y longitudes de texto
- **Detección de patrones** en comportamientos de usuarios

### 🤖 **Preparación para Machine Learning**
- Generación de **texto consolidado** para análisis de sentimientos
- **Datasets estructurados** listos para modelado
- **Features engineered** optimizadas para ML
- **Formato estándar** compatible con bibliotecas populares

## 📊 Datos del Proyecto

### 🏙️ **Ciudades Cubiertas**
- **Cancún**: 10 atracciones principales
- **Ciudad de México**: 10 atracciones principales

### 🏛️ **Tipos de Atracciones**
- Museos y sitios arqueológicos
- Playas y parques acuáticos
- Centros comerciales y entretenimiento
- Jardines y espacios naturales
- Experiencias culturales

### 📈 **Volumen de Datos**
- **1,314 opiniones** procesadas
- **20 atracciones** analizadas
- **2 ciudades** principales
- **10 campos** de información por opinión

### 📝 **Campos de Datos**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| `Titulo` | Título de la reseña | Texto |
| `Review` | Contenido completo de la opinión | Texto |
| `TipoViaje` | Tipo de viaje (Familia, Pareja, Amigos, etc.) | Categórico |
| `Calificacion` | Puntuación de 1-5 estrellas | Numérico |
| `OrigenAutor` | Ubicación geográfica del autor | Geográfico |
| `FechaOpinion` | Fecha de publicación de la reseña | Fecha |
| `FechaEstadia` | Fecha de visita | Fecha |
| `ciudad` | Ciudad de la atracción | Categórico |
| `atraccion` | Nombre de la atracción | Categórico |
| `texto_consolidado` | **Narrativa completa** para ML | Texto |

## 🛠️ Instalación y Configuración

### 📋 Requisitos Previos
- Python 3.8+
- pip o conda
- Jupyter Notebook/Lab

### ⚡ Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/VictorWKey/AI-Tourism-Opinion-Analyzer.git
cd analisis-automatizado-de-opiniones-turisticas

# Instalar dependencias
pip install -r requirements.txt

# Iniciar Jupyter
jupyter notebook notebooks/01-analisis_exploratorio_y_procesamiento_basico-de-datos.ipynb
```

### 📦 Dependencias Principales
```txt
pandas>=2.0.0          # Manipulación de datos
numpy>=1.24.0          # Cálculos numéricos
matplotlib>=3.6.0      # Visualización
seaborn>=0.12.0        # Visualización estadística
beautifulsoup4>=4.11.0 # Web scraping
requests>=2.28.0       # HTTP requests
jupyter>=1.0.0         # Notebook environment
```

## 🚀 Uso del Sistema

### 1️⃣ **Extracción de Datos (Web Scraping)**
```bash
# Extraer opiniones de una atracción específica
python scripts/web_scrapping.py data ciudad-atraccion URL_TRIPADVISOR
```

### 2️⃣ **Procesamiento Completo**
```python
import sys
sys.path.append('scripts')
import procesamiento_datos as proc

# Pipeline completo de procesamiento
df_limpio = proc.procesar_dataset_completo('data/')
```

### 3️⃣ **Análisis Exploratorio**
```python
import exploracion_datos as exp

# Análisis comprehensivo
exp.analizar_informacion_general(df_limpio)
exp.analizar_distribuciones_categoricas(df_limpio)
exp.analisis_final_completo(df_limpio)
```

### 4️⃣ **Notebook Interactivo**
Ejecutar `notebooks/01-analisis_exploratorio_y_procesamiento_basico-de-datos.ipynb` para análisis completo con visualizaciones.

## 📊 Resultados y Insights

### 🎯 **Métricas de Calidad**
- **100% completitud**: Sin valores faltantes
- **0 duplicados**: Datos únicos garantizados
- **Fechas normalizadas**: Formato estándar datetime
- **Texto consolidado**: Listo para análisis de sentimientos

### 📈 **Insights Principales**
- **Calificación promedio**: 4.26/5 estrellas
- **Tipo de viaje predominante**: Familia (35.8%)
- **Distribución geográfica**: Cancún 53.3%, CDMX 46.7%
- **Longitud promedio de texto**: 366 caracteres

### 🏆 **Top Atracciones**
1. Acuario Michin (CDMX) - 74 opiniones
2. Puerto Maya (Cancún) - 73 opiniones
3. Ventura Park (Cancún) - 72 opiniones

## 🔧 Arquitectura Técnica

### 🏗️ **Diseño Modular**
El sistema está diseñado con **separación clara de responsabilidades**:

- **`web_scrapping.py`**: Extracción de datos
- **`procesamiento_datos.py`**: Transformación y limpieza
- **`exploracion_datos.py`**: Análisis y visualización
- **`01-analisis_exploratorio_y_procesamiento_basico-de-datos.ipynb`**: Interface interactiva

### 🔄 **Pipeline de Datos**
```mermaid
graph LR
A[TripAdvisor] --> B[Web Scraping]
B --> C[Datos Crudos]
C --> D[Procesamiento]
D --> E[Dataset Limpio]
E --> F[Análisis Exploratorio]
F --> G[Insights & ML Ready]
```

### 🛡️ **Características de Robustez**
- **Manejo de errores** en scraping
- **Validación de datos** automática
- **Logging detallado** de procesos
- **Recuperación de fallos** en extracción

## 🔮 Casos de Uso

### 🏨 **Sector Hotelero y Turístico**
- Análisis de percepción de atracciones
- Identificación de puntos de mejora
- Benchmarking competitivo
- Estrategias de marketing basadas en datos

### 🎓 **Investigación Académica**
- Estudios de comportamiento turístico
- Análisis de sentimientos a gran escala
- Investigación en turismo digital
- Datasets para machine learning

### 💼 **Consultoría en Turismo**
- Reportes automáticos de satisfacción
- Análisis de tendencias temporales
- Segmentación de mercados
- Recomendaciones basadas en datos

## 🚧 Próximos Desarrollos

### 🤖 **Análisis de Sentimientos**
- Implementación de modelos NLP
- Clasificación automática de emociones
- Detección de aspectos específicos
- Scoring de satisfacción

### 📊 **Dashboard Interactivo**
- Interface web para exploración
- Visualizaciones dinámicas
- Filtros por múltiples dimensiones
- Exportación de reportes

### 🌐 **Expansión Geográfica**
- Más ciudades mexicanas
- Destinos internacionales
- Diversificación de fuentes
- APIs de múltiples plataformas

### 🔮 **Machine Learning Avanzado**
- Predicción de calificaciones
- Recomendaciones personalizadas
- Detección de anomalías
- Clustering de perfiles de usuario

## 🤝 Contribución

### 🔧 **Cómo Contribuir**
1. **Fork** el repositorio
2. **Crear branch** para nueva funcionalidad
3. **Implementar** cambios con tests
4. **Documentar** nuevas funciones
5. **Submit Pull Request**

### 📋 **Guidelines de Contribución**
- Seguir estándares PEP 8
- Incluir docstrings en funciones
- Agregar tests para nuevo código
- Actualizar documentación

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT** - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Victor W. Key**
- GitHub: [@VictorWKey](https://github.com/VictorWKey)
- Proyecto: [AI-Tourism-Opinion-Analyzer](https://github.com/VictorWKey/AI-Tourism-Opinion-Analyzer)

## 🙏 Agradecimientos

- **TripAdvisor** por proporcionar datos públicos de opiniones
- **Comunidad Python** por las excelentes bibliotecas de análisis de datos
- **Jupyter Project** por el ambiente de desarrollo interactivo

---

⭐ **Si este proyecto te resulta útil, ¡considera darle una estrella!** ⭐

📊 **Para reportar bugs o solicitar funcionalidades, abre un [Issue](https://github.com/VictorWKey/AI-Tourism-Opinion-Analyzer/issues)**
