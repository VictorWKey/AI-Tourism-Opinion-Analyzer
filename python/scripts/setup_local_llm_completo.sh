#!/bin/bash

# ============================================================
# Script de Configuración Completa de LLM Local (Ollama)
# ============================================================
# Este script automatiza TODO el proceso de configuración:
# 1. Instala Ollama si no está instalado
# 2. Descarga el modelo recomendado
# 3. Configura el archivo .env para modo local
# 4. Prueba que todo funcione correctamente
# ============================================================

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}"
echo "============================================================"
echo "  CONFIGURACIÓN COMPLETA DE LLM LOCAL (OLLAMA)"
echo "============================================================"
echo -e "${NC}"

# ============================================================
# PASO 1: Verificar/Instalar Ollama
# ============================================================

echo -e "${YELLOW}[PASO 1/5]${NC} Verificando instalación de Ollama..."

if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama ya está instalado"
    ollama --version
else
    echo -e "${YELLOW}⚠${NC} Ollama no está instalado. Instalando..."
    
    # Detectar sistema operativo
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Instalando Ollama en Linux..."
        curl -fsSL https://ollama.com/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Instalando Ollama en macOS..."
        brew install ollama
    else
        echo -e "${RED}✗${NC} Sistema operativo no soportado automáticamente"
        echo "Por favor, visita https://ollama.com/download para instalar manualmente"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Ollama instalado correctamente"
fi

# ============================================================
# PASO 2: Iniciar Servicio Ollama
# ============================================================

echo ""
echo -e "${YELLOW}[PASO 2/5]${NC} Iniciando servicio Ollama..."

# Verificar si Ollama ya está corriendo
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama ya está corriendo"
else
    echo "Iniciando Ollama en segundo plano..."
    nohup ollama serve > "$PROJECT_DIR/ollama.log" 2>&1 &
    sleep 3
    
    if pgrep -x "ollama" > /dev/null; then
        echo -e "${GREEN}✓${NC} Ollama iniciado correctamente"
        echo "   Log disponible en: $PROJECT_DIR/ollama.log"
    else
        echo -e "${RED}✗${NC} Error al iniciar Ollama"
        echo "   Revisa el log: cat $PROJECT_DIR/ollama.log"
        exit 1
    fi
fi

# ============================================================
# PASO 3: Descargar Modelo Recomendado
# ============================================================

echo ""
echo -e "${YELLOW}[PASO 3/5]${NC} Descargando modelo de LLM..."

# Pregunta al usuario qué modelo quiere
echo ""
echo "Modelos disponibles:"
echo "  1. llama3.2:3b  - Recomendado para desarrollo (4GB RAM, rápido)"
echo "  2. llama3.1:8b  - Mejor calidad (8GB RAM, más lento)"
echo "  3. gemma2:2b    - Más ligero (2GB RAM, muy rápido)"
echo ""
read -p "Selecciona el modelo [1-3] (presiona Enter para usar llama3.2:3b): " MODEL_CHOICE

case $MODEL_CHOICE in
    2)
        MODELO="llama3.1:8b"
        ;;
    3)
        MODELO="gemma2:2b"
        ;;
    *)
        MODELO="llama3.2:3b"
        ;;
esac

echo ""
echo "Descargando modelo: $MODELO"
echo "Esto puede tardar varios minutos dependiendo de tu conexión..."

if ollama pull $MODELO; then
    echo -e "${GREEN}✓${NC} Modelo $MODELO descargado correctamente"
else
    echo -e "${RED}✗${NC} Error al descargar el modelo"
    exit 1
fi

# Verificar que el modelo está disponible
echo ""
echo "Modelos instalados:"
ollama list

# ============================================================
# PASO 4: Configurar archivo .env
# ============================================================

echo ""
echo -e "${YELLOW}[PASO 4/5]${NC} Configurando archivo .env..."

ENV_FILE="$PROJECT_DIR/.env"

# Hacer backup del .env actual si existe
if [ -f "$ENV_FILE" ]; then
    BACKUP_FILE="$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$ENV_FILE" "$BACKUP_FILE"
    echo -e "${YELLOW}⚠${NC} Backup del .env actual guardado en: $(basename $BACKUP_FILE)"
fi

# Crear nuevo archivo .env para modo local
cat > "$ENV_FILE" << EOF
# ============================================================
# Configuración LLM - Modo Local (Ollama)
# Generado automáticamente por setup_local_llm_completo.sh
# Fecha: $(date)
# ============================================================

# MODO DE OPERACIÓN
LLM_MODE=local

# CONFIGURACIÓN OLLAMA (Modelo Local)
OLLAMA_MODEL=$MODELO
OLLAMA_BASE_URL=http://localhost:11434
LLM_TEMPERATURE=0.0

# CONFIGURACIÓN OPENAI (No se usa en modo local, pero se mantiene por compatibilidad)
# OPENAI_API_KEY=sk-proj-...
# OPENAI_MODEL=gpt-4o-mini

# RUTAS DE DATOS
DATASET_PATH=data/dataset.csv
OUTPUT_PATH=data/shared

# ============================================================
# NOTAS:
# - Para cambiar a modo API, cambia LLM_MODE=api y configura OPENAI_API_KEY
# - Para cambiar el modelo local, edita OLLAMA_MODEL
# - Modelos disponibles: llama3.2:3b, llama3.1:8b, gemma2:2b
# ============================================================
EOF

echo -e "${GREEN}✓${NC} Archivo .env configurado para modo local"
echo "   Modelo: $MODELO"
echo "   URL: http://localhost:11434"

# ============================================================
# PASO 5: Probar Configuración
# ============================================================

echo ""
echo -e "${YELLOW}[PASO 5/5]${NC} Probando configuración..."
echo ""

cd "$PROJECT_DIR"

# Verificar que Python puede importar los módulos
echo "Verificando módulos Python..."
if python -c "from core.llm_provider import LLMProvider; from config.config import ConfigLLM" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Módulos Python importados correctamente"
else
    echo -e "${RED}✗${NC} Error al importar módulos Python"
    echo "   Asegúrate de tener instaladas las dependencias: pip install -r requirements.txt"
    exit 1
fi

# Ejecutar test de configuración
echo ""
echo "Ejecutando test de configuración LLM..."
echo ""

if python scripts/test_llm_setup.py; then
    echo ""
    echo -e "${GREEN}"
    echo "============================================================"
    echo "  ✅ CONFIGURACIÓN COMPLETA EXITOSA"
    echo "============================================================"
    echo -e "${NC}"
    echo ""
    echo "Tu sistema está listo para usar LLM local con Ollama!"
    echo ""
    echo "Próximos pasos:"
    echo "  1. Ejecutar el pipeline completo:"
    echo -e "     ${BLUE}python main.py${NC}"
    echo ""
    echo "  2. Ver configuración actual:"
    echo -e "     ${BLUE}python -c \"from core.llm_provider import LLMProvider; print(LLMProvider.get_info())\"${NC}"
    echo ""
    echo "  3. Cambiar de modelo (editar .env):"
    echo -e "     ${BLUE}nano .env${NC}"
    echo ""
    echo "Información del sistema:"
    echo "  • Modelo: $MODELO"
    echo "  • Servicio Ollama: Corriendo en http://localhost:11434"
    echo "  • Configuración: $ENV_FILE"
    echo "  • Log Ollama: $PROJECT_DIR/ollama.log"
    echo ""
else
    echo ""
    echo -e "${RED}"
    echo "============================================================"
    echo "  ✗ ERROR EN LA CONFIGURACIÓN"
    echo "============================================================"
    echo -e "${NC}"
    echo ""
    echo "Algo salió mal durante las pruebas."
    echo ""
    echo "Diagnóstico:"
    echo "  1. Verifica que Ollama esté corriendo:"
    echo -e "     ${BLUE}pgrep ollama${NC}"
    echo ""
    echo "  2. Revisa el log de Ollama:"
    echo -e "     ${BLUE}cat $PROJECT_DIR/ollama.log${NC}"
    echo ""
    echo "  3. Prueba manualmente la conexión:"
    echo -e "     ${BLUE}curl http://localhost:11434/api/tags${NC}"
    echo ""
    echo "  4. Si necesitas reiniciar Ollama:"
    echo -e "     ${BLUE}pkill ollama && ollama serve &${NC}"
    echo ""
    exit 1
fi

# ============================================================
# Información adicional
# ============================================================

echo "Comandos útiles:"
echo ""
echo "  • Detener Ollama:"
echo -e "    ${BLUE}pkill ollama${NC}"
echo ""
echo "  • Reiniciar Ollama:"
echo -e "    ${BLUE}pkill ollama && nohup ollama serve > ollama.log 2>&1 &${NC}"
echo ""
echo "  • Ver modelos instalados:"
echo -e "    ${BLUE}ollama list${NC}"
echo ""
echo "  • Descargar otro modelo:"
echo -e "    ${BLUE}ollama pull <nombre-modelo>${NC}"
echo ""
echo "  • Restaurar backup de .env:"
echo -e "    ${BLUE}cp .env.backup.* .env${NC}"
echo ""
