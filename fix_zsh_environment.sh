#!/bin/bash

# Script para corrigir problemas do zsh e configurar ambiente SNE Radar
echo "🔧 Corrigindo ambiente zsh e configurando SNE Radar..."

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ Execute este script no diretório raiz do SNE Radar"
    exit 1
fi

# Corrigir problema do dump_zsh_state
echo "🔄 Corrigindo configuração do zsh..."

# Backup do .zshrc se existir
if [ -f ~/.zshrc ]; then
    cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup do .zshrc criado"
fi

# Remover linhas problemáticas do .zshrc
if [ -f ~/.zshrc ]; then
    sed -i '' '/dump_zsh_state/d' ~/.zshrc
    sed -i '' '/cursor_snap/d' ~/.zshrc
    echo "✅ Linhas problemáticas removidas do .zshrc"
fi

# Configurar ambiente Python
echo "🐍 Configurando ambiente Python..."

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instalando via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install python3
    else
        echo "❌ Homebrew não encontrado. Instale Python 3 manualmente."
        exit 1
    fi
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

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p logs
mkdir -p instance
mkdir -p exports
mkdir -p relatorios
mkdir -p rupturas_detectadas

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

# Testar configuração do banco
echo "🗄️ Testando configuração do banco..."
python3 -c "
from database_config import print_config_status
print_config_status()
"

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "📋 Para usar o sistema:"
echo "1. Ative o ambiente virtual: source venv/bin/activate"
echo "2. Execute o sistema principal: python3 main.py"
echo "3. Ou execute a aplicação web: python3 sne_radar_web.py"
echo ""
echo "💡 Para desativar o ambiente virtual: deactivate"
echo ""
echo "🔧 Se ainda houver problemas com o zsh, reinicie o terminal ou execute:"
echo "   source ~/.zshrc"