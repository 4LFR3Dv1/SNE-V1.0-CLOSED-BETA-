# 📊 COMO FUNCIONA O DASHBOARD INICIAL

**Arquivo:** `frontend/src/views/Dashboard.vue`  
**Tecnologia:** Vue.js 3 (Composition API)

---

## 🎯 VISÃO GERAL

O Dashboard é a página principal do sistema. Ele exibe:
- **Métricas globais do mercado** (Market Cap, Dominance, Volume)
- **Preço do BTC** em tempo real
- **Top oportunidades de trading** (sinais BUY/SELL)
- **Status do sistema**
- **Alertas ativos**

---

## 🔄 FLUXO DE CARREGAMENTO

### **1. Quando a página carrega (`onMounted`):**

```javascript
onMounted(() => {
  refreshAll()  // ← Carrega TODOS os dados
  
  // Auto-refresh a cada 60 segundos
  refreshInterval = setInterval(() => {
    loadOpportunities()  // ← Apenas oportunidades
    loadGlobalMetrics()  // ← Métricas globais
    loadBTCPrice()       // ← Preço BTC
  }, 60000)
})
```

**O que acontece:**
1. ✅ Executa `refreshAll()` imediatamente
2. ✅ Configura auto-refresh a cada 60 segundos
3. ✅ Limpa intervalo quando componente é destruído (`onUnmounted`)

---

### **2. Função `refreshAll()` - Carregamento Completo:**

```javascript
const refreshAll = async () => {
  loading.value = true
  try {
    // Sequencial para evitar rate limit
    await loadGlobalMetrics()    // 1. Métricas globais
    await loadSystemStatus()     // 2. Status do sistema
    await loadAlerts()           // 3. Alertas ativos
    await loadBTCPrice()         // 4. Preço BTC
    await loadOpportunities()    // 5. Oportunidades (tem delay interno)
  } finally {
    loading.value = false
  }
}
```

**Ordem das requisições:**
1. 🔹 Métricas globais (`/api/v1/global-metrics`)
2. 🔹 Status do sistema (`/api/v1/system/status`)
3. 🔹 Alertas ativos (`/api/v1/alerts`)
4. 🔹 Preço BTC (`/api/v1/ta-summary` ou `/api/signal`)
5. 🔹 Oportunidades (5 símbolos sequenciais)

---

## 📦 COMPONENTES DO DASHBOARD

### **1. Métricas Globais (4 cards)**

**Função:** `loadGlobalMetrics()`
- **Endpoint:** `GET /api/v1/global-metrics`
- **Dados exibidos:**
  - Market Cap Total (com variação 24h)
  - BTC Dominance (com variação 24h)
  - ETH Dominance (com variação 24h)
  - Volume 24h Total

**Formatação:**
- Moedas: `$1.5T` (trilhão), `$500B` (bilhão), `$1.2M` (milhão)
- Porcentagens: `+2.45%` ou `-1.23%`
- Indicadores visuais: `↗` (alta) ou `↘` (baixa)

---

### **2. Cards de Resumo (3 cards)**

#### **Card 1: BTC/USDT**
- **Função:** `loadBTCPrice()`
- **Endpoints tentados (em ordem):**
  1. `/api/v1/ta-summary?symbol=BTCUSDT` (preferencial)
  2. `/api/signal?symbol=BTCUSDT&timeframe=1h` (fallback)
- **Dados:**
  - Preço atual formatado: `$45,234.56`
  - Variação 24h: `+2.45%` (verde) ou `-1.23%` (vermelho)

#### **Card 2: Sinais Hoje**
- **Computed:** `signalsCount`
- **Valor:** Número de oportunidades filtradas (`filteredOpportunities.length`)

#### **Card 3: Score Médio**
- **Computed:** `averageScore`
- **Cálculo:** Média dos scores de todas as oportunidades
- **Exemplo:** Se 3 oportunidades têm scores 7, 8, 6 → média = 7.0

---

### **3. Top Oportunidades (Lista com Filtros)**

**Função:** `loadOpportunities()`

#### **Como funciona:**

```javascript
// 1. Lista de símbolos a buscar
const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']

// 2. Para cada símbolo (SEQUENCIAL, não paralelo):
for (const symbol of symbols) {
  // Delay de 500ms entre requisições
  await delay(500)
  
  // Buscar sinal
  const data = await api.getSignal(symbol, '1h')
  
  // Adicionar aos resultados
  results.push({
    symbol,
    timeframe: '1h',
    signal: data.signal,      // BUY, SELL ou NEUTRAL
    score: data.score         // 0-10
  })
}

// 3. Ordenar por score (maior primeiro)
opportunities.value = results.sort((a, b) => b.score - a.score)
```

**Endpoint usado:** `GET /api/signal?symbol=BTCUSDT&timeframe=1h`

**Por que sequencial?**
- ✅ Evita rate limit (Flask-Limiter: 500 req/hora em dev)
- ✅ Delay de 500ms entre requisições
- ✅ Se erro 429, aguarda 2 segundos e tenta novamente

---

#### **Filtros Disponíveis:**

**1. Busca por Símbolo:**
```javascript
if (searchQuery.value) {
  filtered = filtered.filter(opp => 
    opp.symbol.includes(searchQuery.value.toUpperCase())
  )
}
```

**2. Filtro de Sinal:**
- Opções: Todos, BUY, SELL, NEUTRAL

**3. Filtro de Score Mínimo:**
- Opções: 0, 5, 7, 8
- Padrão: 5

**4. Filtro de Timeframe:**
- Opções: Todos, 1m, 5m, 15m, 1h, 4h, 1d

**Computed Property:**
```javascript
const filteredOpportunities = computed(() => {
  // Aplica TODOS os filtros
  // Retorna lista filtrada e ordenada por score
})
```

---

### **4. Status do Sistema**

**Função:** `loadSystemStatus()`
- **Endpoint:** `GET /api/v1/system/status`
- **Dados exibidos:**
  - API Status: Online/Offline (com indicador visual)
  - Última Atualização: Hora formatada
  - Uptime: Tempo que o sistema está rodando

---

### **5. Alertas Ativos**

**Função:** `loadAlerts()`
- **Endpoint:** `GET /api/v1/alerts`
- **Dados exibidos:**
  - Primeiros 3 alertas ativos
  - Símbolo e tipo de alerta
  - Link para "Gerenciar →" (vai para Settings)

---

## 🔄 AUTO-REFRESH

### **Configuração:**

```javascript
refreshInterval = setInterval(() => {
  loadOpportunities()   // Atualiza lista de oportunidades
  loadGlobalMetrics()   // Atualiza métricas globais
  loadBTCPrice()        // Atualiza preço BTC
}, 60000) // 60 segundos
```

**Por que 60 segundos?**
- ✅ Evita sobrecarregar o servidor
- ✅ Respeita rate limits
- ✅ Balanceia atualização vs performance

**Limpeza:**
```javascript
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval) // Limpa quando sai da página
  }
})
```

---

## 🎨 INTERAÇÕES DO USUÁRIO

### **1. Botão "Atualizar"**

```javascript
@click="refreshAll"
```

**O que faz:**
- Ativa loading state (`loading = true`)
- Executa `refreshAll()` (carrega tudo)
- Desativa loading quando termina

**Feedback visual:**
- Mostra "⏳ Atualizando..." enquanto carrega
- Desabilita botão durante carregamento

---

### **2. Clique em Oportunidade**

```javascript
@click="selectOpportunity(opp)"

const selectOpportunity = (opp) => {
  router.push({
    name: 'Analysis',
    query: { symbol: opp.symbol, timeframe: opp.timeframe }
  })
}
```

**O que acontece:**
- Redireciona para página de Análise
- Passa símbolo e timeframe como query params
- Exemplo: `/analysis?symbol=BTCUSDT&timeframe=1h`

---

### **3. Filtros (Reatividade Automática)**

**Como funciona:**
- Usa `v-model` para bind com variáveis reativas
- `filteredOpportunities` é um **computed property**
- Quando filtro muda → lista atualiza automaticamente

**Exemplo:**
```javascript
// Usuário seleciona "BUY" no filtro
filterSignal.value = 'BUY'

// computed property recalcula automaticamente
filteredOpportunities.value // ← Só tem oportunidades BUY
```

---

## 📊 ESTRUTURA DE DADOS

### **Oportunidade:**

```javascript
{
  symbol: 'BTCUSDT',           // Par de negociação
  timeframe: '1h',             // Timeframe da análise
  signal: 'BUY',               // BUY, SELL ou NEUTRAL
  score: 7.5                   // Score de confluência (0-10)
}
```

### **Métricas Globais:**

```javascript
{
  market_cap_usd: 2500000000000,      // Market cap em USD
  market_cap_change_24h: 2.5,         // Variação %
  btc_dominance: 52.5,                // BTC dominance %
  btc_dominance_change_24h: 0.3,      // Variação %
  eth_dominance: 18.2,                // ETH dominance %
  eth_dominance_change_24h: -0.1,     // Variação %
  volume_24h_usd: 50000000000         // Volume 24h em USD
}
```

### **Status do Sistema:**

```javascript
{
  api_status: 'online',        // online ou offline
  uptime: 3600,                // Segundos desde início
  // ... outros campos
}
```

---

## 🛠️ TRATAMENTO DE ERROS

### **1. Rate Limit (429):**

```javascript
if (err.response?.status === 429) {
  console.warn('Rate limit atingido, aguardando...')
  await delay(2000)  // Aguarda 2 segundos
  // Tenta novamente
}
```

### **2. Erros Gerais:**

- ✅ `try/catch` em todas as funções async
- ✅ Logs no console (`console.warn`)
- ✅ Não quebra a interface (mostra "--" ou lista vazia)
- ✅ Fallback: se TA Summary falhar, tenta Signal

---

## 🔧 OTIMIZAÇÕES

### **1. Requisições Sequenciais:**

**Por quê?**
- Evita rate limit
- Controla carga no servidor
- Melhor tratamento de erros

### **2. Delay entre Requisições:**

```javascript
await delay(500) // 500ms entre cada requisição
```

**Por quê?**
- Dá tempo ao servidor processar
- Respeita rate limits
- Evita sobrecarga

### **3. Computed Properties:**

**Exemplo:**
```javascript
const filteredOpportunities = computed(() => {
  // Só recalcula quando filtros mudam
  // Cache automático pelo Vue
})
```

**Benefício:**
- Performance (não recalcula desnecessariamente)
- Reatividade automática

---

## 📝 RESUMO DO FLUXO

```
Usuário acessa /dashboard
        ↓
onMounted() executa
        ↓
refreshAll() inicia
        ↓
├─ loadGlobalMetrics()    → GET /api/v1/global-metrics
├─ loadSystemStatus()     → GET /api/v1/system/status
├─ loadAlerts()           → GET /api/v1/alerts
├─ loadBTCPrice()         → GET /api/v1/ta-summary
└─ loadOpportunities()    → GET /api/signal (5x sequencial)
        ↓
Dados carregados e exibidos
        ↓
Auto-refresh a cada 60s
        ↓
Quando usuário sai: onUnmounted() limpa intervalo
```

---

## 🎯 FUNCIONALIDADES PRINCIPAIS

1. ✅ **Carregamento inicial completo** de todos os dados
2. ✅ **Auto-refresh** a cada 60 segundos
3. ✅ **Filtros interativos** (busca, sinal, score, timeframe)
4. ✅ **Navegação** para análise detalhada
5. ✅ **Tratamento de erros** robusto
6. ✅ **Loading states** em todas as operações
7. ✅ **Rate limit handling** com retry automático

---

**Documento criado:** Janeiro 2025  
**Última atualização:** Após implementação da Fase 1

