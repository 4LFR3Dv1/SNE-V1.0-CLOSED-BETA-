#!/bin/bash

echo "🚀 SNE RADAR - INSTALAÇÃO RÁPIDA"
echo "=================================="

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs
mkdir -p rupturas_detectadas
mkdir -p relatorios
mkdir -p mapeamentos

# Criar arquivos de configuração
echo "⚙️ Criando arquivos de configuração..."

# Arquivo de log de rupturas
if [ ! -f "log_rupturas.txt" ]; then
    echo "🔍 Log de Rupturas Iniciado." > log_rupturas.txt
fi

# Arquivo de códice de fluxo
if [ ! -f "codice_fluxo.txt" ]; then
    echo "📜 Códice de Fluxo Iniciado." > codice_fluxo.txt
fi

# Arquivo de catálogo magnético
if [ ! -f "catalogo_magnetico.csv" ]; then
    echo "zona,forca_total,ocorrencias,ultima_data" > catalogo_magnetico.csv
fi

# Arquivo de zonas magnéticas
if [ ! -f "zonas_magneticas.csv" ]; then
    echo "zona,forca_total,ocorrencias,ultima_data" > zonas_magneticas.csv
fi

echo ""
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "========================"
echo ""
echo "🎯 Para executar o sistema:"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo ""
echo "📱 Para configurar Telegram (opcional):"
echo "   Edite xenos_bot.py e configure TELEGRAM_TOKEN e CHAT_ID"
echo ""
echo "📊 O sistema está pronto para uso!"
echo ""
