#!/bin/bash

# Script de Deploy para Render - SNE Radar
echo "🚀 Deploy SNE Radar para Render..."

# Verificar se estamos no diretório correto
if [ ! -f "sne_radar_web.py" ]; then
    echo "❌ Execute este script no diretório raiz do SNE Radar"
    exit 1
fi

# Verificar se o git está configurado
if ! git status &> /dev/null; then
    echo "❌ Repositório git não encontrado"
    exit 1
fi

echo "📋 Preparando arquivos para deploy..."

# Criar arquivo de configuração de ambiente
cat > .env.production << EOF
# Configurações de Produção para Render
FLASK_ENV=production
SECRET_KEY=\$(openssl rand -hex 32)
ENABLE_COINGLASS=false
ENABLE_CMC=false
ENABLE_TA_SUMMARY=false
UPDATE_INTERVAL=30
REQUEST_TIMEOUT=12
BINANCE_CALLS_PER_WINDOW=10
BINANCE_WINDOW_SECONDS=60
EOF

# Criar arquivo de build para Render
cat > build.sh << 'EOF'
#!/bin/bash
echo "🔧 Instalando dependências..."
pip install -r requirements_render.txt
pip install psycopg2-binary
echo "✅ Dependências instaladas"
EOF

chmod +x build.sh

# Criar arquivo de start para Render
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando SNE Radar..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 sne_radar_web:app
EOF

chmod +x start.sh

# Verificar arquivos necessários
echo "🔍 Verificando arquivos necessários..."
required_files=(
    "sne_radar_web.py"
    "requirements_render.txt"
    "render.yaml"
    "config.py"
    "database_config.py"
    "services/"
    "integrations/"
    "templates/"
    "static/"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -e "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Arquivos faltando:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "✅ Todos os arquivos necessários estão presentes"

# Fazer commit das mudanças
echo "📝 Fazendo commit das mudanças..."
git add .
git commit -m "Deploy: Configuração para Render" || echo "Nenhuma mudança para commitar"

echo ""
echo "🎉 Preparação para deploy concluída!"
echo ""
echo "📋 Próximos passos no Render:"
echo "1. Acesse https://dashboard.render.com"
echo "2. Crie um novo Web Service"
echo "3. Conecte seu repositório GitHub"
echo "4. Configure as seguintes variáveis de ambiente:"
echo "   - FLASK_ENV=production"
echo "   - SECRET_KEY=(gerar uma chave aleatória)"
echo "   - ENABLE_COINGLASS=false"
echo "   - ENABLE_CMC=false"
echo "   - ENABLE_TA_SUMMARY=false"
echo "5. Configure o banco PostgreSQL"
echo "6. Use o arquivo render.yaml para configuração automática"
echo ""
echo "🔧 Comandos de build e start:"
echo "   Build Command: ./build.sh"
echo "   Start Command: ./start.sh"
echo ""
echo "💡 Dica: Use o arquivo render.yaml para deploy automático!"




