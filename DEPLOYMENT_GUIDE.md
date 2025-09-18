# 🚀 Guia de Deploy - SNE RADAR

## ✅ Status do Deploy

**Último Deploy**: `7322887` - Fix: Atualizar scikit-learn para versão compatível com Python 3.13

**Branch**: `production-functional`

**Repositório**: https://github.com/4LFR3Dv1/SNE-RADAR

## 🔧 Configuração do Render

### Variáveis de Ambiente Necessárias

Configure as seguintes variáveis no painel do Render:

#### **Obrigatórias:**
- `SECRET_KEY` - Chave secreta do Flask (gerada automaticamente)
- `FLASK_ENV=production`

#### **APIs Externas:**
- `COINGLASS_API_KEY` - Chave da API CoinGlass
- `COINMARKETCAP_API_KEY` - Chave da API CoinMarketCap
- `COINGECKO_KEY` - Chave da API CoinGecko
- `SCRAPERAPI_KEY` - Chave da API ScraperAPI

#### **Telegram (Opcional):**
- `TELEGRAM_TOKEN` - Token do bot Telegram
- `CHAT_ID` - ID do chat para notificações

#### **Feature Flags:**
- `ENABLE_COINGLASS=true`
- `ENABLE_CMC=true`
- `ENABLE_TA_SUMMARY=true`

#### **Configurações Avançadas:**
- `DEBUG=false`
- `PORT=10000`
- `UPDATE_INTERVAL=30`
- `BINANCE_CALLS_PER_WINDOW=1200`
- `BINANCE_WINDOW_SECONDS=60`

## 📊 Funcionalidades Implementadas

### ✅ **Indicadores Técnicos**
- **Básicos**: EMA, SMA, RSI, MACD
- **Avançados**: Bollinger Bands, Stochastic, Williams %R, ATR, CCI, OBV, ADX
- **Profissionais**: Ichimoku Cloud, Fibonacci Retracements, Pivot Points, Volume Profile

### ✅ **Machine Learning**
- **Modelos**: Random Forest, Gradient Boosting, Linear Regression, Ridge
- **Ensemble**: Combinação de múltiplos modelos
- **Features**: 20+ indicadores técnicos
- **Auto-retraining**: Retreinamento automático

### ✅ **Backtesting**
- **Estratégias**: MA Crossover, RSI, Bollinger Bands
- **Otimização**: Parâmetros automáticos
- **Métricas**: Sharpe Ratio, Drawdown, Win Rate
- **Multi-strategy**: Combinação de estratégias

### ✅ **APIs Externas**
- **CoinGlass**: Funding Rate, Open Interest, Long/Short Ratio, Liquidations
- **CoinMarketCap**: Market Cap, Dominance, Listings por tag
- **Binance**: Dados de mercado em tempo real

### ✅ **Sistema de Alertas**
- **Tipos**: Preço, RSI, Volume, Funding, OI, Liquidations
- **Condições**: Above, Below, Crosses
- **Notificações**: Socket.IO em tempo real

### ✅ **Exportação**
- **Formatos**: CSV, PDF
- **Dados**: Market data, Candles, Relatórios completos
- **Gestão**: Sistema de arquivos

## 🔍 Endpoints Disponíveis

### **Health Checks**
- `GET /health` - Status da aplicação
- `GET /ready` - Prontidão para receber tráfego

### **APIs de Dados**
- `GET /api/v1/ta-summary` - Resumo de análise técnica
- `GET /api/v1/global-metrics` - Métricas globais do mercado
- `GET /api/v1/derivatives` - Dados de derivativos
- `GET /api/v1/listings` - Listagens de criptomoedas
- `GET /api/v1/candles` - Dados de velas

### **Indicadores**
- `GET /api/v1/advanced-indicators` - Indicadores avançados
- `GET /api/v1/professional-indicators` - Indicadores profissionais

### **Machine Learning**
- `POST /api/v1/ml/train` - Treinar modelos
- `GET /api/v1/ml/predict` - Predições
- `GET /api/v1/ml/performance` - Performance dos modelos

### **Backtesting**
- `POST /api/v1/backtest/run` - Executar backtest
- `POST /api/v1/backtest/optimize` - Otimizar parâmetros

### **Alertas**
- `GET /api/v1/alerts` - Listar alertas
- `POST /api/v1/alerts` - Criar alerta

### **Exportação**
- `GET /api/v1/export/market-data` - Exportar dados de mercado
- `GET /api/v1/export/candles` - Exportar velas
- `GET /api/v1/export/report` - Exportar relatório PDF

## 🧪 Testando o Deploy

Execute o script de teste:

```bash
python test_deployment.py
```

Ou teste manualmente:

```bash
# Health check
curl https://sne-radar.onrender.com/health

# TA Summary
curl "https://sne-radar.onrender.com/api/v1/ta-summary?symbol=BTCUSDT"

# Global Metrics
curl https://sne-radar.onrender.com/api/v1/global-metrics
```

## 📈 Monitoramento

### **Logs do Render**
- Acesse o painel do Render
- Vá em "Logs" para ver os logs em tempo real
- Monitore erros e performance

### **Métricas**
- **Uptime**: Verifique se a aplicação está online
- **Response Time**: Tempo de resposta dos endpoints
- **Error Rate**: Taxa de erros

### **Alertas**
- Configure alertas no Render para downtime
- Monitore logs de erro
- Verifique uso de recursos

## 🔄 Atualizações

Para fazer atualizações:

1. **Desenvolvimento Local**:
   ```bash
   git checkout production-functional
   # Faça suas alterações
   git add .
   git commit -m "feat: Nova funcionalidade"
   git push origin production-functional
   ```

2. **Deploy Automático**:
   - O Render fará deploy automático do branch `production-functional`
   - Monitore os logs durante o deploy
   - Teste as funcionalidades após o deploy

## 🚨 Troubleshooting

### **Problemas Comuns**

1. **Erro de Dependências**:
   - Verifique se todas as dependências estão no `requirements.txt`
   - Teste localmente antes do deploy

2. **Timeout de Build**:
   - O Render tem limite de tempo para build
   - Otimize dependências se necessário

3. **Erro de Variáveis de Ambiente**:
   - Verifique se todas as variáveis estão configuradas
   - Use `sync: false` para variáveis sensíveis

4. **Erro de Memória**:
   - Upgrade do plano se necessário
   - Otimize uso de memória no código

### **Logs Importantes**

```bash
# Verificar logs de erro
grep "ERROR" logs/

# Verificar performance
grep "slow" logs/

# Verificar APIs externas
grep "API" logs/
```

## 📞 Suporte

- **GitHub Issues**: https://github.com/4LFR3Dv1/SNE-RADAR/issues
- **Render Docs**: https://render.com/docs
- **Logs**: Painel do Render > Logs

---

**Última Atualização**: 18/09/2025
**Versão**: 2.0.0 - Sistema Completo de Análise Técnica
