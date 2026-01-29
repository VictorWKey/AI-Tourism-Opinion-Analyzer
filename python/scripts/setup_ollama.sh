#!/bin/bash

# Script de instalación y configuración de Ollama
# Para sistemas Linux/macOS

set -e  # Detener en caso de error

echo "============================================="
echo "  Instalación de Ollama para LLM Local"
echo "============================================="
echo ""

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "❌ Sistema operativo no soportado: $OSTYPE"
    echo "💡 Para Windows, descarga desde: https://ollama.ai/download"
    exit 1
fi

echo "📌 Sistema operativo detectado: $OS"
echo ""

# Verificar si Ollama ya está instalado
if command -v ollama &> /dev/null; then
    echo "✅ Ollama ya está instalado"
    ollama --version
else
    echo "📥 Instalando Ollama..."
    
    if [[ "$OS" == "linux" ]]; then
        # Instalación para Linux
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OS" == "macos" ]]; then
        # Instalación para macOS con Homebrew
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew no está instalado"
            echo "💡 Instala Homebrew desde: https://brew.sh"
            echo "💡 O descarga Ollama manualmente desde: https://ollama.ai/download"
            exit 1
        fi
        
        brew install ollama
    fi
    
    echo "✅ Ollama instalado correctamente"
fi

echo ""
echo "============================================="
echo "  Descarga de Modelos"
echo "============================================="
echo ""

# Función para descargar modelo
download_model() {
    local model=$1
    echo "📥 Descargando modelo: $model"
    ollama pull "$model"
    echo "✅ Modelo $model descargado"
    echo ""
}

# Menú de selección
echo "Selecciona el modelo a descargar:"
echo ""
echo "1) llama3.2:1b   - Muy ligero (1GB RAM)   - Rápido"
echo "2) llama3.2:3b   - Balanceado (2GB RAM)   - RECOMENDADO"
echo "3) llama3.1:8b   - Alta calidad (4.7GB)   - Lento"
echo "4) gemma2:2b     - Alternativa (1.6GB)    - Rápido"
echo "5) Todos los anteriores"
echo "6) Saltar descarga"
echo ""

read -p "Opción [2]: " choice
choice=${choice:-2}

case $choice in
    1)
        download_model "llama3.2:1b"
        SELECTED_MODEL="llama3.2:1b"
        ;;
    2)
        download_model "llama3.2:3b"
        SELECTED_MODEL="llama3.2:3b"
        ;;
    3)
        download_model "llama3.1:8b"
        SELECTED_MODEL="llama3.1:8b"
        ;;
    4)
        download_model "gemma2:2b"
        SELECTED_MODEL="gemma2:2b"
        ;;
    5)
        download_model "llama3.2:1b"
        download_model "llama3.2:3b"
        download_model "llama3.1:8b"
        download_model "gemma2:2b"
        SELECTED_MODEL="llama3.2:3b"
        ;;
    6)
        echo "⏭️  Descarga omitida"
        SELECTED_MODEL="llama3.2:3b"
        ;;
    *)
        echo "❌ Opción inválida, descargando modelo recomendado..."
        download_model "llama3.2:3b"
        SELECTED_MODEL="llama3.2:3b"
        ;;
esac

echo ""
echo "============================================="
echo "  Configuración de Variables de Entorno"
echo "============================================="
echo ""

# Verificar si ya existe .env
if [ -f ".env" ]; then
    echo "⚠️  Archivo .env ya existe"
    read -p "¿Deseas sobrescribirlo? (s/N): " overwrite
    overwrite=${overwrite:-n}
    
    if [[ ! $overwrite =~ ^[Ss]$ ]]; then
        echo "✅ Configuración conservada"
        exit 0
    fi
fi

# Crear archivo .env
cat > .env << EOF
# ============================================
# Configuración del Sistema LLM
# ============================================

# Modo de LLM: 'api' o 'local'
LLM_MODE=local

# ============================================
# Configuración Ollama (Modo Local)
# ============================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=$SELECTED_MODEL

# ============================================
# Parámetros de Generación
# ============================================
LLM_TEMPERATURE=0
LLM_MAX_TOKENS=2000

# ============================================
# Configuración OpenAI (Solo si cambias a modo API)
# ============================================
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# OPENAI_MODEL=gpt-4o-mini
EOF

echo "✅ Archivo .env creado con modo LOCAL"
echo "   Modelo configurado: $SELECTED_MODEL"
echo ""

echo "============================================="
echo "  Iniciar Servidor de Ollama"
echo "============================================="
echo ""

echo "Para usar el sistema, necesitas iniciar el servidor de Ollama:"
echo ""
echo "  En una terminal separada, ejecuta:"
echo "  $ ollama serve"
echo ""
echo "O si prefieres ejecutarlo en segundo plano:"
echo "  $ nohup ollama serve > ollama.log 2>&1 &"
echo ""

read -p "¿Deseas iniciar el servidor ahora? (S/n): " start_server
start_server=${start_server:-s}

if [[ $start_server =~ ^[Ss]$ ]]; then
    echo "🚀 Iniciando servidor de Ollama..."
    
    # Verificar si ya está ejecutándose
    if pgrep -x "ollama" > /dev/null; then
        echo "✅ Ollama ya está ejecutándose"
    else
        # Iniciar en segundo plano
        nohup ollama serve > ollama.log 2>&1 &
        OLLAMA_PID=$!
        
        # Esperar a que el servidor inicie
        sleep 2
        
        if ps -p $OLLAMA_PID > /dev/null; then
            echo "✅ Servidor de Ollama iniciado (PID: $OLLAMA_PID)"
            echo "   Ver logs: tail -f ollama.log"
        else
            echo "❌ Error al iniciar servidor"
            echo "💡 Intenta manualmente: ollama serve"
        fi
    fi
fi

echo ""
echo "============================================="
echo "  ✅ Instalación Completada"
echo "============================================="
echo ""
echo "Pasos siguientes:"
echo ""
echo "1. Verifica que Ollama esté ejecutándose:"
echo "   $ ollama list"
echo ""
echo "2. Instala las dependencias de Python:"
echo "   $ pip install -r requirements.txt"
echo ""
echo "3. Ejecuta el pipeline:"
echo "   $ python main.py"
echo ""
echo "Para más información, consulta: LLM_SETUP.md"
echo ""
