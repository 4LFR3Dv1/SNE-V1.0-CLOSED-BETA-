#!/bin/bash

# Script para testar o sistema localmente
echo "🚀 Testando SNE RADAR localmente..."

# Usar bash em vez de zsh
export SHELL=/bin/bash

# Navegar para o diretório
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

echo "📁 Diretório: $(pwd)"

# Verificar se o ambiente virtual existe
if [ -d "venv" ]; then
    echo "✅ Ambiente virtual encontrado"
    echo "🔧 Ativando ambiente virtual..."
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
    
    # Verificar dependências
    echo "📦 Verificando dependências..."
    python3 -c "import pandas; print('✅ pandas OK')" 2>/dev/null || echo "❌ pandas não instalado"
    python3 -c "import numpy; print('✅ numpy OK')" 2>/dev/null || echo "❌ numpy não instalado"
    python3 -c "import flask; print('✅ flask OK')" 2>/dev/null || echo "❌ flask não instalado"
    
    # Instalar dependências se necessário
    echo "📥 Instalando dependências..."
    pip install -r requirements.txt
    
    # Testar importações
    echo "🧪 Testando importações..."
    python3 -c "
try:
    from services.advanced_indicators import calculate_all_indicators
    print('✅ Advanced indicators OK')
except Exception as e:
    print(f'❌ Advanced indicators: {e}')

try:
    from integrations.coinglass import get_funding
    print('✅ CoinGlass integration OK')
except Exception as e:
    print(f'❌ CoinGlass integration: {e}')

try:
    from integrations.cmc import get_global_metrics
    print('✅ CoinMarketCap integration OK')
except Exception as e:
    print(f'❌ CoinMarketCap integration: {e}')
"
    
    echo "🎯 Testando configuração do banco..."
    python3 -c "
from database_config import get_database_url, test_connection
url = get_database_url()
print(f'📊 URL do banco: {url}')
if test_connection('local'):
    print('✅ Conexão com banco local OK')
else:
    print('❌ Problema com banco local')
"
    
    echo "🚀 Iniciando aplicação..."
    echo "💡 Acesse: http://localhost:5000"
    echo "⏹️  Para parar: Ctrl+C"
    
    # Iniciar aplicação
    python3 sne_radar_web.py
    
else
    echo "❌ Ambiente virtual não encontrado"
    echo "💡 Execute: python3 -m venv venv"
    echo "💡 Depois: source venv/bin/activate"
    echo "💡 E: pip install -r requirements.txt"
fi



