#!/bin/bash

# Script de Deploy para SNE RADAR
echo "🚀 Iniciando deploy do SNE RADAR..."

# Configurar Git se necessário
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositório Git..."
    git init
    git remote add origin https://github.com/4LFR3Dv1/SNE-RADAR.git
fi

# Adicionar arquivos
echo "📝 Adicionando arquivos ao Git..."
git add .

# Fazer commit
echo "💾 Fazendo commit..."
git commit -m "feat: Implementação completa de indicadores avançados, ML e backtesting

- ✅ Indicadores Profissionais: Ichimoku, Fibonacci, Pivot Points, Volume Profile
- ✅ Sistema de Machine Learning: 4 modelos (RF, GB, LR, Ridge) com ensemble
- ✅ Backtesting Avançado: Múltiplas estratégias com otimização de parâmetros
- ✅ APIs Reais: CoinGlass e CoinMarketCap integradas
- ✅ Sistema de Alertas: Baseado em thresholds com notificações em tempo real
- ✅ Exportação: CSV e PDF com relatórios completos
- ✅ Interface Atualizada: Novos painéis para ML, backtesting e indicadores

Funcionalidades implementadas:
- Indicadores: Bollinger, Stochastic, Williams %R, ATR, CCI, OBV, ADX
- ML: Predições de preço com confiança e ensemble
- Backtesting: MA Crossover, RSI, Bollinger strategies
- Alertas: Preço, RSI, Volume com condições avançadas
- Exportação: Dados de mercado, candles, relatórios PDF"

# Push para GitHub
echo "🌐 Enviando para GitHub..."
git push -u origin main

echo "✅ Deploy concluído com sucesso!"
echo "🔗 Repositório: https://github.com/4LFR3Dv1/SNE-RADAR"