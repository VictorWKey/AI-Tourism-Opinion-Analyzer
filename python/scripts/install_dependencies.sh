#!/bin/bash

# ============================================================
# Script de Instalación de Dependencias
# AI Tourism Opinion Analyzer - Production Pipeline
# ============================================================

set -e  # Salir si hay algún error

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "============================================================"
echo "  INSTALACIÓN DE DEPENDENCIAS - PIPELINE DE PRODUCCIÓN"
echo "============================================================"
echo -e "${NC}"
echo ""

# Verificar Python
echo -e "${YELLOW}[1/5]${NC} Verificando Python..."
if ! command -v python &> /dev/null; then
    echo -e "❌ Python no encontrado. Por favor instala Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "✅ Python $PYTHON_VERSION detectado"
echo ""

# Verificar pip
echo -e "${YELLOW}[2/5]${NC} Verificando pip..."
if ! command -v pip &> /dev/null; then
    echo -e "❌ pip no encontrado. Instalando..."
    python -m ensurepip --upgrade
fi

PIP_VERSION=$(pip --version 2>&1 | awk '{print $2}')
echo -e "✅ pip $PIP_VERSION detectado"
echo ""

# Actualizar pip
echo -e "${YELLOW}[3/5]${NC} Actualizando pip..."
python -m pip install --upgrade pip
echo -e "✅ pip actualizado"
echo ""

# Instalar dependencias
echo -e "${YELLOW}[4/5]${NC} Instalando dependencias desde requirements.txt..."
echo "Esto puede tardar varios minutos..."
echo ""

if pip install -r requirements.txt; then
    echo ""
    echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
else
    echo ""
    echo -e "❌ Error al instalar dependencias"
    exit 1
fi
echo ""

# Descargar datos de NLTK
echo -e "${YELLOW}[5/5]${NC} Descargando datos de NLTK..."
python -c "
import nltk
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    print('✅ Datos de NLTK descargados')
except Exception as e:
    print(f'⚠️  Error al descargar NLTK: {e}')
    print('   Puedes descargarlos manualmente después')
"
echo ""

# Resumen
echo -e "${GREEN}"
echo "============================================================"
echo "  ✅ INSTALACIÓN COMPLETADA"
echo "============================================================"
echo -e "${NC}"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Configurar LLM:"
echo -e "   ${BLUE}# Para modo local (gratuito):${NC}"
echo -e "   ${BLUE}./scripts/setup_local_llm_completo.sh${NC}"
echo ""
echo -e "   ${BLUE}# Para modo API (OpenAI):${NC}"
echo -e "   ${BLUE}cp .env.example .env${NC}"
echo -e "   ${BLUE}nano .env  # Configurar OPENAI_API_KEY${NC}"
echo ""
echo "2. Ejecutar el pipeline:"
echo -e "   ${BLUE}python main.py${NC}"
echo ""
echo "3. Ver documentación:"
echo -e "   ${BLUE}cat README.md${NC}"
echo -e "   ${BLUE}cat docs/LLM_SETUP.md${NC}"
echo ""
