#!/bin/bash

# Caminho para o projeto
PROJECT_PATH="$HOME/Desktop/SNEv1"

# Navegar até o diretório do projeto
echo "📂 Navegando para o diretório do projeto..."
cd "$PROJECT_PATH" || { echo "❌ Caminho não encontrado: $PROJECT_PATH"; exit 1; }

# Verificar permissões da pasta
echo "🔎 Verificando permissões..."
chmod -R 755 "$PROJECT_PATH"

# Remover ambiente virtual antigo (se existir)
if [ -d "venv" ]; then
    echo "🧹 Removendo ambiente virtual antigo..."
    rm -rf venv
fi

# Criar um novo ambiente virtual
echo "🌱 Criando um novo ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install requests pandas numpy matplotlib mplfinance pytz
pip install python-telegram-bot

# Garantir permissões de execução para o main.py
chmod +x main.py

# Executar o main.py
echo "🚀 Iniciando o SNE..."
python3 main.py