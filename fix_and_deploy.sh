#!/bin/bash

# Script para resolver problema do zsh e fazer deploy
echo "🔧 Resolvendo problema do zsh e fazendo deploy..."

# Usar bash em vez de zsh para evitar o erro
export SHELL=/bin/bash

# Navegar para o diretório correto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Verificar se estamos no diretório correto
echo "📁 Diretório atual: $(pwd)"
echo "📋 Arquivos no diretório:"
ls -la | head -10

# Configurar Git
echo "🔧 Configurando Git..."
git config --global user.name "SNE RADAR"
git config --global user.email "sne@radar.com"

# Inicializar repositório se necessário
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositório Git..."
    git init
    git remote add origin https://github.com/4LFR3Dv1/SNE-RADAR.git
fi

# Verificar status
echo "📊 Status do Git:"
git status --porcelain | head -10

# Adicionar arquivos importantes
echo "📝 Adicionando arquivos..."
git add config.py
git add services/
git add integrations/
git add .gitignore
git add requirements.txt
git add sne_radar_web.py
git add templates/dashboard.html
git add deploy.sh

# Fazer commit
echo "💾 Fazendo commit..."
git commit -m "feat: Sistema completo de análise técnica avançada

🚀 NOVAS FUNCIONALIDADES:
- Indicadores Profissionais: Ichimoku, Fibonacci, Pivot Points
- Machine Learning: 4 modelos com predições ensemble
- Backtesting: Múltiplas estratégias com otimização
- APIs Reais: CoinGlass e CoinMarketCap
- Sistema de Alertas: Thresholds com notificações
- Exportação: CSV/PDF com relatórios

📊 INDICADORES IMPLEMENTADOS:
- Ichimoku Cloud (Tenkan, Kijun, Senkou, Chikou)
- Fibonacci Retracements e Extensions
- Pivot Points (Standard, Fibonacci, Camarilla, Woodie)
- Volume Profile (POC, VAH, VAL)
- Market Structure Analysis

🤖 MACHINE LEARNING:
- Random Forest, Gradient Boosting, Linear/Ridge Regression
- Ensemble predictions com confiança
- 20+ features técnicas
- Auto-retraining

📈 BACKTESTING:
- MA Crossover, RSI, Bollinger Bands strategies
- Parameter optimization
- Professional metrics (Sharpe, Drawdown, Win Rate)
- Multi-strategy combination

🔔 ALERTAS:
- Price, RSI, Volume alerts
- Cross conditions (above/below/crosses)
- Real-time notifications via Socket.IO

📤 EXPORTAÇÃO:
- Market data CSV
- Candlestick data CSV  
- Complete PDF reports
- File management system"

# Push para GitHub
echo "🌐 Enviando para GitHub..."
git branch -M main
git push -u origin main

echo "✅ Deploy concluído com sucesso!"
echo "🔗 Repositório: https://github.com/4LFR3Dv1/SNE-RADAR"
echo "📊 Status: Sistema completo de análise técnica implementado"



