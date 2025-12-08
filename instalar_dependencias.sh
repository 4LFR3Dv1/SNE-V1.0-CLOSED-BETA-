#!/bin/bash

# Script para instalar dependências Python

echo "📦 Instalando dependências Python..."
echo ""

# Verificar se requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt não encontrado!"
    exit 1
fi

# Verificar se pip está disponível
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado!"
    echo "   Instale pip primeiro"
    exit 1
fi

# Usar pip3 se disponível, senão pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "✅ Usando: $PIP_CMD"
echo ""

# Instalar dependências
echo "📥 Instalando dependências do requirements.txt..."
$PIP_CMD install -r requirements.txt

echo ""
echo "✅ Dependências instaladas!"
echo ""
echo "💡 Agora você pode rodar:"
echo "   python3 sne_radar_web.py"

