# 📚 Guia de Uso da API SNE 1.0 Cloud

## 🌐 Base URL

```
https://sne-web-pqhownilea-ew.a.run.app
```

---

## 🔍 Endpoints Disponíveis

### 1. Health Check

Verifica se o serviço está online.

```bash
curl https://sne-web-pqhownilea-ew.a.run.app/health
```

**Resposta:**
```json
{
  "service": "sne-web",
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### 2. Análise Completa

Retorna análise técnica completa de um par de trading.

**Endpoint:** `POST /api/analyze`

**Request:**
```bash
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "timeframe": "1h"
  }'
```

**Parâmetros:**
- `symbol` (string, opcional): Par de trading (padrão: "BTCUSDT")
- `timeframe` (string, opcional): Timeframe (padrão: "15m")
  - Valores aceitos: "1m", "5m", "15m", "1h", "4h"

**Resposta:**
```json
{
  "status": "ok",
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "analysis": {
    "confluence_score": 6.4,
    "bias": "NEUTRAL",
    "recommendation": "SHORT ESPECULATIVO",
    "entry": 92750.47,
    "stop_loss": 93307.53,
    "take_profit": 90054.30,
    "rr_ratio": "1:6.5"
  },
  "full_analysis": {
    // Análise completa com todos os dados
  }
}
```

**Exemplos:**

```bash
# BTCUSDT em 1h
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'

# ETHUSDT em 15m
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "ETHUSDT", "timeframe": "15m"}'

# SOLUSDT em 4h
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "SOLUSDT", "timeframe": "4h"}'
```

---

### 3. Obter Sinal

Retorna sinal de trading formatado e simplificado.

**Endpoint:** `GET /api/signal`

**Request:**
```bash
curl "https://sne-web-pqhownilea-ew.a.run.app/api/signal?symbol=BTCUSDT&timeframe=1h"
```

**Query Parameters:**
- `symbol` (string, opcional): Par de trading (padrão: "BTCUSDT")
- `timeframe` (string, opcional): Timeframe (padrão: "15m")

**Resposta:**
```json
{
  "status": "ok",
  "signal": {
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "type": "SHORT ESPECULATIVO",
    "confidence": 0.79,
    "entry": 92750.47,
    "stop_loss": 93307.53,
    "take_profit": 90057.72,
    "timestamp": ""
  }
}
```

**Exemplos:**

```bash
# BTCUSDT em 1h
curl "https://sne-web-pqhownilea-ew.a.run.app/api/signal?symbol=BTCUSDT&timeframe=1h"

# ETHUSDT em 15m
curl "https://sne-web-pqhownilea-ew.a.run.app/api/signal?symbol=ETHUSDT&timeframe=15m"

# SOLUSDT em 4h
curl "https://sne-web-pqhownilea-ew.a.run.app/api/signal?symbol=SOLUSDT&timeframe=4h"
```

---

## 📊 Estrutura da Resposta Completa

A resposta de `/api/analyze` inclui:

### `analysis` (Resumo)
- `confluence_score`: Score de confluência (0-10)
- `bias`: Viés do mercado (BULLISH/BEARISH/NEUTRAL)
- `recommendation`: Recomendação de trading
- `entry`: Preço de entrada sugerido
- `stop_loss`: Stop Loss sugerido
- `take_profit`: Take Profit sugerido
- `rr_ratio`: Risk/Reward ratio

### `full_analysis` (Análise Completa)
- `analise_avancada`: Indicadores avançados (ADX, CCI, MFI, OBV, PSAR, Williams %R)
- `candles_detalhados`: Análise detalhada dos candles
- `confluencia`: Score de confluência por camada
- `contexto`: Contexto de mercado (regime, sessão, volatilidade)
- `estrutura`: Estrutura de mercado (suportes, resistências, tendência)
- `fluxo`: Análise de fluxo DOM (Order Book)
- `indicadores`: Indicadores técnicos (RSI, MACD, EMAs, etc.)
- `mtf`: Análise multi-timeframe (5 timeframes simultâneos)
- `niveis_operacionais`: Níveis de entrada, SL e TP
- `padroes`: Padrões gráficos detectados
- `sintese`: Síntese final da análise

---

## 💡 Exemplos de Uso

### Python

```python
import requests

# Análise completa
response = requests.post(
    'https://sne-web-pqhownilea-ew.a.run.app/api/analyze',
    json={'symbol': 'BTCUSDT', 'timeframe': '1h'}
)
data = response.json()

print(f"Score: {data['analysis']['confluence_score']}")
print(f"Recomendação: {data['analysis']['recommendation']}")
print(f"Entry: ${data['analysis']['entry']:.2f}")

# Obter sinal
response = requests.get(
    'https://sne-web-pqhownilea-ew.a.run.app/api/signal',
    params={'symbol': 'BTCUSDT', 'timeframe': '1h'}
)
signal = response.json()['signal']
print(f"Confidence: {signal['confidence']*100:.0f}%")
```

### JavaScript/Node.js

```javascript
// Análise completa
const response = await fetch('https://sne-web-pqhownilea-ew.a.run.app/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbol: 'BTCUSDT', timeframe: '1h' })
});
const data = await response.json();

console.log(`Score: ${data.analysis.confluence_score}`);
console.log(`Recomendação: ${data.analysis.recommendation}`);

// Obter sinal
const signalResponse = await fetch(
  'https://sne-web-pqhownilea-ew.a.run.app/api/signal?symbol=BTCUSDT&timeframe=1h'
);
const signal = await signalResponse.json();
console.log(`Confidence: ${signal.signal.confidence * 100}%`);
```

---

## 🎯 Pares Suportados

A API suporta todos os pares disponíveis na Binance. Exemplos:

- `BTCUSDT` - Bitcoin
- `ETHUSDT` - Ethereum
- `SOLUSDT` - Solana
- `BNBUSDT` - Binance Coin
- `ADAUSDT` - Cardano
- `XRPUSDT` - Ripple
- `DOGEUSDT` - Dogecoin
- E muitos outros...

---

## ⏱️ Timeframes Suportados

- `1m` - 1 minuto (scalp)
- `5m` - 5 minutos (day trade)
- `15m` - 15 minutos (intraday)
- `1h` - 1 hora (swing)
- `4h` - 4 horas (position)

---

## ⚠️ Limitações e Observações

1. **Rate Limiting**: Atualmente sem limite, mas use com moderação
2. **Timeout**: Requisições podem levar alguns segundos (análise completa)
3. **Erro em gestao_risco**: Há um erro menor que não impede o funcionamento
4. **Acesso Público**: API está pública (sem autenticação)

---

## 🔧 Troubleshooting

### Erro 403 Forbidden
- Verifique se o acesso público está habilitado
- Execute: `./habilitar_acesso_publico.sh sne-v1 europe-west1`

### Erro de Serialização
- Já corrigido na versão atual
- Se persistir, verifique os logs

### Timeout
- Análises completas podem levar 5-10 segundos
- Considere usar `/api/signal` para respostas mais rápidas

---

## 📈 Monitoramento

### Ver Logs
```bash
gcloud run services logs read sne-web \
    --region=europe-west1 \
    --project=sne-v1 \
    --limit=50
```

### Logs em Tempo Real
```bash
gcloud run services logs tail sne-web \
    --region=europe-west1 \
    --project=sne-v1
```

---

## 🎉 Status

**✅ API 100% Operacional**

- Health check: ✅ Funcionando
- Análise completa: ✅ Funcionando
- Obter sinal: ✅ Funcionando
- Múltiplos pares: ✅ Testado
- Múltiplos timeframes: ✅ Testado

---

**Sistema SNE 1.0 Cloud - API de Análise Técnica Profissional** 🚀

