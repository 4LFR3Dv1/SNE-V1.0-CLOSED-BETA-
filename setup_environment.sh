#!/bin/bash

# Script para configurar o ambiente SNE Radar
echo "🚀 Configurando ambiente SNE Radar..."

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Verificar versão do Python
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version encontrado"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️ Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Verificar instalação
echo "🔍 Verificando instalação..."
python3 -c "
import sys
try:
    import pandas, numpy, matplotlib, flask, requests
    print('✅ Dependências principais instaladas com sucesso!')
except ImportError as e:
    print(f'❌ Erro ao importar dependências: {e}')
    sys.exit(1)
"

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p logs
mkdir -p instance
mkdir -p exports
mkdir -p relatorios
mkdir -p rupturas_detectadas

# Verificar configuração do banco
echo "🗄️ Verificando configuração do banco..."
python3 -c "
from database_config import print_config_status
print_config_status()
"

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Ative o ambiente virtual: source venv/bin/activate"
echo "2. Execute o sistema principal: python3 main.py"
echo "3. Ou execute a aplicação web: python3 sne_radar_web.py"
echo ""
echo "💡 Para desativar o ambiente virtual: deactivate"




