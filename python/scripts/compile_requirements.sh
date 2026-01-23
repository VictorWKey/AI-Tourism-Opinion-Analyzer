#!/bin/bash

# Script para compilar requirements.in a requirements.txt
# Requiere pip-tools instalado: pip install pip-tools

echo "============================================="
echo "  Compilación de Dependencias"
echo "============================================="
echo ""

# Verificar si pip-compile está instalado
if ! command -v pip-compile &> /dev/null; then
    echo "❌ pip-compile no está instalado"
    echo ""
    echo "Instalando pip-tools..."
    pip install pip-tools
    echo ""
fi

# Compilar requirements
echo "📦 Compilando requirements.in..."
pip-compile requirements.in --resolver=backtracking

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ requirements.txt actualizado exitosamente"
    echo ""
    echo "Para instalar las dependencias:"
    echo "  pip install -r requirements.txt"
else
    echo ""
    echo "❌ Error al compilar requirements"
    exit 1
fi
