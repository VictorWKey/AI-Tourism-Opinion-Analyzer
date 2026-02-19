# TourlyAI - Production Pipeline

Sistema automatizado de análisis de opiniones turísticas con soporte para LLM local o API.

## 🚀 Inicio Rápido

### ⭐ Opción 1: Setup Automático Completo (TODO EN UNO) - RECOMENDADO

Este script hace **TODO** por ti automáticamente:
- ✅ Instala todas las dependencias Python
- ✅ Instala Ollama (LLM local)
- ✅ Descarga el modelo LLM que elijas
- ✅ Configura el archivo `.env`
- ✅ Descarga datos necesarios (NLTK)
- ✅ Prueba que todo funcione

```bash
cd production
# Paso 1: Instalar dependencias Python
./scripts/install_dependencies.sh

# Paso 2: Configurar LLM local
./scripts/setup_local_llm_completo.sh

# Paso 3: ¡Listo! Ejecutar pipeline
python main.py
```

**¡Eso es todo!** En unos minutos tendrás todo funcionando 100% gratis.

### 🔧 Opción 2: Instalación Manual por Pasos

Si prefieres hacerlo paso a paso:

```bash
# 1. Ejecutar script de instalación Ollama
./scripts/setup_ollama.sh

# 2. Descargar modelo
ollama pull llama3.2:3b

# 3. Configurar .env para modo local
cp .env.example .env
# Editar .env: USE_API=false, OLLAMA_MODEL=llama3.2:3b

# 4. Instalar dependencias Python
pip install -r requirements.txt

# 5. Ejecutar pipeline
python main.py
```

### 🎯 Control de Ejecución de Fases

El pipeline ahora permite controlar qué fases se ejecutan mediante el diccionario `CONFIG_FASES` en `main.py`:

```python
CONFIG_FASES = {
    'fase_01': True,   # Procesamiento Básico
    'fase_02': True,   # Análisis de Sentimientos
    'fase_03': True,   # Análisis de Subjetividad
    'fase_04': True,   # Clasificación de Categorías
    'fase_05': True,   # Análisis Jerárquico de Tópicos
    'fase_06': True,   # Resumen Inteligente
    'fase_07': True,   # Generación de Visualizaciones
}
```

**Comportamiento:**
- `True` = La fase se ejecuta siempre (incluso si ya fue ejecutada)
- `False` = La fase se omite SI ya fue ejecutada previamente
- **Inteligente:** Si una fase NO ha sido ejecutada nunca, se ejecutará automáticamente sin importar la configuración

Esto permite:
- ✅ Re-ejecutar solo fases específicas sin procesar todo
- ✅ Ahorrar tiempo omitiendo fases ya completadas
- ✅ Desarrollo iterativo más eficiente

### 💳 Opción 3: Modo API (OpenAI - Pago)

```bash
# 1. Copiar archivo de configuración
cp .env.example .env

# 2. Editar .env y configurar:
#    - LLM_MODE=api
#    - OPENAI_API_KEY=tu-api-key

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Ejecutar pipeline
python main.py
```

## 📋 Requisitos

### Requisitos Comunes
- Python 3.10+
- 4GB RAM mínimo (8GB recomendado)
- GPU NVIDIA (opcional, mejora velocidad)

### Requisitos Adicionales por Modo

#### Modo Local (Ollama)
- **Espacio en disco**: 2-5 GB para modelos
- **RAM adicional**: 1-5 GB según modelo
- Sin costo por uso ✅

#### Modo API (OpenAI)
- **Internet**: Conexión estable
- **API Key**: Cuenta de OpenAI
- Costo por uso (~$0.15 por 1M tokens) 💰

## 📚 Documentación Completa

Para configuración detallada de LLM, consulta: **[docs/LLM_SETUP.md](./docs/LLM_SETUP.md)**

## 🔧 Estructura del Proyecto

```
production/
├── main.py                 # Script principal del pipeline
├── README.md               # Esta documentación
├── requirements.txt        # Dependencias Python necesarias
├── .env.example            # Plantilla de configuración
├── .env                    # Tu configuración (no en git)
│
├── config/                 # Configuraciones
│   └── config.py          # Config centralizada
│
├── core/                   # Módulos del pipeline
│   ├── llm_provider.py    # Proveedor de LLM
│   ├── fase_01_*.py       # Procesamiento básico
│   ├── fase_02_*.py       # Análisis de sentimientos
│   ├── fase_03_*.py       # Análisis de subjetividad
│   ├── fase_04_*.py       # Clasificación categorías
│   ├── fase_05_*.py       # Análisis de tópicos (usa LLM)
│   └── fase_06_*.py       # Resúmenes (usa LLM)
│
├── scripts/                # Scripts de utilidad
│   ├── install_dependencies.sh      # Script de instalación automática
│   ├── setup_local_llm_completo.sh  # 🆕 Setup TODO-EN-UNO (recomendado)
│   ├── setup_ollama.sh              # Instalación Ollama básica
│   ├── test_llm_setup.py            # Test de configuración
│   └── compile_requirements.sh      # Compilar dependencias
│
├── docs/                   # Documentación
│   ├── INSTALL.md         # Guía de instalación detallada
│   ├── LLM_SETUP.md       # Guía LLM completa
│   └── CHANGELOG.md       # Historial de cambios
│
├── data/                   # Datos de entrada/salida
│   ├── dataset.csv
│   └── shared/
│
└── models/                 # Modelos BERT entrenados
    ├── multilabel_task/
    └── subjectivity_task/
```

## 🔧 Estructura del Pipeline

El sistema ejecuta 7 fases secuenciales:

1. **Procesamiento Básico**: Limpieza y normalización de datos
2. **Análisis de Sentimientos**: Clasificación Positivo/Negativo/Neutro
3. **Análisis de Subjetividad**: Identificación de opiniones subjetivas
4. **Clasificación de Categorías**: Etiquetado multi-etiqueta con BERT
5. **Análisis de Tópicos**: Identificación de sub-temas con BERTopic + LLM ⭐
6. **Resumen Inteligente**: Generación de resúmenes con LLM ⭐
7. **Visualizaciones**: Generación de gráficos profesionales (dashboard, sentimientos, categorías, tópicos, temporal)

⭐ = Fases que utilizan LLM configurable

## 📁 Archivos de Configuración

- **`.env`**: Configuración de LLM y variables de entorno
- **`.env.example`**: Plantilla de configuración
- **`config.py`**: Configuración centralizada del sistema
- **`llm_provider.py`**: Abstracción de proveedores LLM

## 🛠️ Comandos Útiles

### Gestión de Ollama

```bash
# Listar modelos instalados
ollama list

# Descargar un modelo
ollama pull llama3.2:3b

# Iniciar servidor
ollama serve

# Probar modelo
ollama run llama3.2:3b
```

### Verificar Configuración

```bash
# Ver configuración actual de LLM
python -c "from core.llm_provider import LLMProvider; print(LLMProvider.get_info())"

# Probar conexión con LLM
python -c "from core.llm_provider import get_llm; llm = get_llm(); print(llm.invoke('Hola'))"
```

## 🐛 Solución de Problemas

### Error: "Error al inicializar Ollama"

1. Verifica que Ollama esté ejecutándose:
   ```bash
   ollama serve
   ```

2. Verifica que el modelo esté descargado:
   ```bash
   ollama list
   ollama pull llama3.2:3b
   ```

### Error: "OPENAI_API_KEY no está configurado"

1. Crea/edita el archivo `.env` en `/production/`
2. Agrega tu API key:
   ```env
   LLM_MODE=api
   OPENAI_API_KEY=sk-proj-...
   ```

### Rendimiento Lento

1. **Para Ollama**: Usa un modelo más ligero
   ```bash
   ollama pull llama3.2:1b
   ```
   
2. **Para API**: Usa un modelo más rápido
   ```env
   OPENAI_MODEL=gpt-3.5-turbo
   ```

## 📊 Salidas del Sistema

El pipeline genera los siguientes archivos:

- **`data/dataset.csv`**: Dataset procesado con todas las columnas añadidas
- **`data/shared/categorias_scores.json`**: Probabilidades de categorías
- **`data/shared/resumenes.json`**: Resúmenes generados por LLM

## 🔄 Cambiar entre Modos

Para cambiar entre API y Local:

1. Edita `.env`:
   ```env
   # Para usar Ollama local
   LLM_MODE=local
   
   # Para usar OpenAI API
   LLM_MODE=api
   ```

2. Reinicia el pipeline

## 📝 Ejemplo de Uso Programático

```python
from core.llm_provider import crear_chain, LLMProvider

# Ver configuración actual
print(LLMProvider.get_info())

# Crear una cadena simple
template = "Analiza esta opinión turística: {opinion}"
chain = crear_chain(template)

# Invocar
resultado = chain.invoke({
    "opinion": "El hotel es excelente, muy limpio y buena atención"
})
print(resultado)
```

## 🤝 Contribuciones

Para más información sobre el proyecto completo, consulta el README principal en el directorio raíz.

## 📄 Licencia

Este proyecto es parte del AI Tourism Opinion Analyzer.
