# 📊 COMO O GRÁFICO É GERADO NA PÁGINA DE ANALYSIS

## 🎯 RESUMO RÁPIDO

O gráfico na página de **Analysis** é gerado **no servidor** (Flask) usando Python (`mplfinance` + `matplotlib`) e retornado como **imagem PNG** para o frontend Vue.js.

---

## 🔄 FLUXO VISUAL

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vue.js)                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Analysis.vue                                                 │
│    └─► <SimpleChart                                          │
│         :symbol="BTCUSDT"                                    │
│         :timeframe="1h" />                                   │
│                                                               │
│         │                                                     │
│         ▼                                                     │
│                                                               │
│  SimpleChart.vue                                              │
│    └─► fetch('/api/v1/chart-image?...')                     │
│         │                                                     │
│         ├─► Converte para blob                               │
│         ├─► Cria blob URL                                    │
│         └─► <img :src="blobUrl" />                          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                        │
                        │ HTTP GET
                        │ /api/v1/chart-image?symbol=BTCUSDT&interval=1h
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask)                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  @app.route('/api/v1/chart-image')                           │
│                                                               │
│  1. Buscar Dados                                              │
│     └─► Binance API → DataFrame (200 candles)                │
│                                                               │
│  2. Calcular Indicadores                                      │
│     ├─► EMA8  (média exponencial 8 períodos)                │
│     └─► EMA21 (média exponencial 21 períodos)                │
│                                                               │
│  3. Gerar Gráfico                                             │
│     ├─► mplfinance.plot()                                    │
│     ├─► Candlesticks (verde/vermelho)                        │
│     ├─► Volume (subplot inferior)                            │
│     ├─► EMA8 (linha ciano)                                   │
│     └─► EMA21 (linha laranja)                                │
│                                                               │
│  4. Converter para PNG                                        │
│     ├─► matplotlib.savefig() → BytesIO                       │
│     └─► Retorna bytes da imagem                              │
│                                                               │
│  5. Resposta HTTP                                             │
│     └─► Content-Type: image/png                              │
│         Body: [bytes da imagem]                              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                        │
                        │ PNG Image
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vue.js)                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  SimpleChart.vue                                              │
│    └─► Recebe blob                                            │
│         ├─► URL.createObjectURL(blob)                        │
│         └─► <img src="blob:http://..." />                    │
│                                                               │
│  ✅ GRÁFICO EXIBIDO!                                          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 📝 DETALHAMENTO TÉCNICO

### **1. Frontend: Analysis.vue**

**Arquivo:** `frontend/src/views/Analysis.vue`

**O que faz:**
- Renderiza o componente `SimpleChart`
- Passa props: `symbol` e `timeframe`

**Código:**
```vue
<SimpleChart 
  :symbol="marketStore.currentSymbol"
  :timeframe="marketStore.currentTimeframe"
/>
```

---

### **2. Frontend: SimpleChart.vue**

**Arquivo:** `frontend/src/components/charts/SimpleChart.vue`

**Processo:**

#### **A. Construir URL:**
```javascript
const getChartUrl = () => {
  const timestamp = Date.now()  // Cache busting
  const isDev = import.meta.env.DEV
  const baseUrl = isDev ? 'http://localhost:9999' : ''
  
  return `${baseUrl}/api/v1/chart-image?symbol=${symbol}&interval=${timeframe}&t=${timestamp}`
}
```

#### **B. Carregar Imagem:**
```javascript
const loadChart = async () => {
  // 1. Fetch da imagem
  const response = await fetch(url, {
    method: 'GET',
    mode: 'cors',
    cache: 'no-cache'
  })
  
  // 2. Validar Content-Type
  if (!response.headers.get('content-type').includes('image')) {
    error.value = 'Não é uma imagem!'
    return
  }
  
  // 3. Converter para blob
  const blob = await response.blob()
  
  // 4. Criar blob URL
  const blobUrl = URL.createObjectURL(blob)
  
  // 5. Atribuir para exibição
  chartImageUrl.value = blobUrl
}
```

#### **C. Exibir:**
```vue
<img 
  :src="chartImageUrl" 
  alt="Gráfico"
  @error="handleImageError"
  @load="handleImageLoad"
/>
```

**Por que Blob URL?**
- ✅ Evita problemas de CORS
- ✅ Funciona com proxy do Vite
- ✅ Não expõe URL real

---

### **3. Backend: Endpoint /api/v1/chart-image**

**Arquivo:** `sne_radar_web.py` (linha 2013)

#### **Passo 1: Extrair Parâmetros**
```python
symbol = request.args.get('symbol', 'BTCUSDT')
interval = request.args.get('interval', '1h')
```

#### **Passo 2: Buscar Dados**

**Opção A (Preferida):**
```python
from grafico_candlestick import obter_dados_candlestick, calcular_indicadores_grafico

df = obter_dados_candlestick(symbol, interval, limit=200)
df = calcular_indicadores_grafico(df)  # Adiciona EMAs
```

**Opção B (Fallback):**
```python
df = buscar_dados_binance(symbol, interval, 200)
df['EMA8'] = df['close'].ewm(span=8).mean()
df['EMA21'] = df['close'].ewm(span=21).mean()
```

**O que é obtido:**
- DataFrame com colunas: `open`, `high`, `low`, `close`, `volume`
- EMA8 e EMA21 calculadas
- ~200 candles (últimos períodos)
- Índice datetime

#### **Passo 3: Configurar Estilo**
```python
import mplfinance as mpf

# Cores
mc = mpf.make_marketcolors(
    up='#00ff88',      # Verde para alta
    down='#ff4444',    # Vermelho para baixa
    wick={'up':'#00ff88', 'down':'#ff4444'},
    volume='in',
    alpha=0.9
)

# Estilo completo
s = mpf.make_mpf_style(
    marketcolors=mc,
    facecolor='#1a1a1a',    # Fundo escuro
    figcolor='#0a0a0a',     # Cor da figura
    gridcolor='#333333',    # Grid
    rc={
        'font.size': 11,
        'axes.labelcolor': 'white',
        'text.color': 'white'
    }
)
```

#### **Passo 4: Preparar Indicadores**
```python
apds = []

# EMA8 (linha ciano)
if 'EMA8' in df.columns:
    apds.append(mpf.make_addplot(
        df['EMA8'], 
        color='cyan', 
        width=1.5, 
        label='EMA 8'
    ))

# EMA21 (linha laranja)
if 'EMA21' in df.columns:
    apds.append(mpf.make_addplot(
        df['EMA21'], 
        color='orange', 
        width=1.5, 
        label='EMA 21'
    ))
```

#### **Passo 5: Gerar Gráfico**
```python
fig, axes = mpf.plot(
    df_plot,                    # DataFrame OHLCV
    type='candle',              # Tipo: candlestick
    style=s,                    # Estilo configurado
    title=f'{symbol} - {interval}',
    ylabel='Preço (USDT)',
    volume=True,                # Mostrar volume
    ylabel_lower='Volume',
    addplot=apds,               # EMAs sobrepostas
    figsize=(16, 10),           # 16x10 polegadas
    returnfig=True,             # Retornar figura
    show_nontrading=False,
    warn_too_much_data=False
)
```

**Resultado:**
- Gráfico de candlestick profissional
- Volume no subplot inferior
- EMA8 e EMA21 plotadas
- Tema escuro (terminal style)

#### **Passo 6: Converter para PNG**
```python
import io

# Buffer em memória
buffer = io.BytesIO()

# Salvar figura no buffer
plt.savefig(
    buffer,
    format='png',           # Formato PNG
    dpi=150,                # 150 DPI (alta qualidade)
    bbox_inches='tight',    # Ajustar bordas
    facecolor='#0a0a0a',    # Fundo escuro
    edgecolor='white',      # Borda branca
    pad_inches=0.2          # Padding
)

buffer.seek(0)              # Voltar ao início
plt.close(fig)              # Fechar figura (liberar memória)

# Obter bytes
image_bytes = buffer.getvalue()
```

#### **Passo 7: Retornar Resposta**
```python
response = make_response(image_bytes)
response.headers['Content-Type'] = 'image/png'
response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
response.headers['Content-Length'] = str(len(image_bytes))

# CORS headers
response.headers['Access-Control-Allow-Origin'] = origin or '*'
response.headers['Access-Control-Allow-Credentials'] = 'true'

return response
```

---

## 🎨 CARACTERÍSTICAS DO GRÁFICO

### **Elementos Visuais:**
- ✅ **Candlesticks:** Verde (#00ff88) / Vermelho (#ff4444)
- ✅ **Volume:** Subplot inferior com cores
- ✅ **EMA8:** Linha ciano (média exponencial 8 períodos)
- ✅ **EMA21:** Linha laranja (média exponencial 21 períodos)
- ✅ **Tema:** Escuro (terminal style)
- ✅ **Título:** Símbolo + Timeframe

### **Especificações:**
- **Tamanho:** 16x10 polegadas
- **Resolução:** 150 DPI
- **Candles:** ~200 períodos
- **Formato:** PNG
- **Tamanho médio:** ~200-500 KB

---

## 🔧 BIBLIOTECAS UTILIZADAS

### **Backend (Python):**
- **`mplfinance`** - Geração de gráficos financeiros profissionais
- **`matplotlib`** - Renderização de gráficos
- **`pandas`** - Manipulação de dados (DataFrames)
- **`numpy`** - Cálculos numéricos

### **Frontend (JavaScript):**
- **`Vue.js 3`** - Framework
- **`Fetch API`** - Requisições HTTP
- **`Blob API`** - Manipulação de binários

---

## ⚡ OTIMIZAÇÕES IMPLEMENTADAS

1. **Cache Busting:**
   - Timestamp na URL (`&t=timestamp`)
   - Evita cache do navegador

2. **Blob URL:**
   - Carrega como blob primeiro
   - Cria URL de objeto
   - Evita problemas de CORS/proxy

3. **Lazy Loading:**
   - Só carrega quando componente monta
   - Recarrega quando props mudam

4. **Error Handling:**
   - Valida Content-Type
   - Imagens de erro personalizadas
   - Mensagens claras

---

## 📊 EXEMPLO COMPLETO

```
1. Usuário acessa /analysis?symbol=BTCUSDT&timeframe=1h

2. Analysis.vue renderiza SimpleChart.vue

3. SimpleChart.vue constrói URL:
   → http://localhost:9999/api/v1/chart-image?symbol=BTCUSDT&interval=1h&t=1736123456789

4. Fetch para o endpoint

5. Backend processa:
   ├─► Busca 200 candles da Binance para BTCUSDT 1h
   ├─► Calcula EMA8 = média exponencial 8 períodos
   ├─► Calcula EMA21 = média exponencial 21 períodos
   ├─► Configura estilo escuro (terminal)
   ├─► Gera gráfico com mplfinance:
   │   ├─► Candlesticks (verde/vermelho)
   │   ├─► Volume (subplot inferior)
   │   ├─► EMA8 (linha ciano)
   │   └─► EMA21 (linha laranja)
   ├─► Salva em BytesIO como PNG (150 DPI)
   └─► Retorna bytes da imagem

6. Frontend recebe:
   ├─► Valida Content-Type = image/png ✅
   ├─► Converte response para blob
   ├─► Cria blob URL: blob:http://localhost:5173/abc123...
   └─► Atribui ao <img src="blob:...">

7. Gráfico aparece na tela! ✅
```

---

## 🐛 TRATAMENTO DE ERROS

### **Erro: Dados não disponíveis**
```python
return create_error_image("Dados não disponíveis para BTCUSDT (1h)")
```
→ Gera imagem PNG com mensagem de erro

### **Erro: Formato inválido**
```python
return create_error_image("Formato de dados inválido")
```

### **Erro: Falha na geração**
```python
return create_error_image(f"Erro ao criar gráfico: {str(e)}")
```

**Função `create_error_image()`:**
- Cria figura matplotlib simples
- Exibe mensagem de erro
- Retorna como PNG (mesmo formato)

---

## 💡 POR QUE ESSA ABORDAGEM?

### **Vantagens:**
- ✅ **Server-side rendering:** Controle total sobre estilo
- ✅ **Reutilizável:** Pode ser usado em outros contextos (Telegram, PDF, etc.)
- ✅ **Consistente:** Sempre renderiza igual
- ✅ **Não depende de JS:** Funciona mesmo sem JavaScript no cliente
- ✅ **Performance:** Processamento no servidor

### **Desvantagens:**
- ⚠️ **Carga no servidor:** Processamento de imagem
- ⚠️ **Tamanho:** PNGs podem ser grandes (~200-500 KB)
- ⚠️ **Não interativo:** Gráfico estático (não é interativo)

---

## 🔍 ARQUIVOS ENVOLVIDOS

### **Frontend:**
- `frontend/src/views/Analysis.vue` - Página de análise
- `frontend/src/components/charts/SimpleChart.vue` - Componente de gráfico

### **Backend:**
- `sne_radar_web.py` (linha ~2013) - Endpoint `/api/v1/chart-image`
- `grafico_candlestick.py` - Funções auxiliares para dados e indicadores

---

## ✅ CONCLUSÃO

O gráfico é gerado completamente **no servidor** usando:
1. Dados da Binance (200 candles)
2. Cálculo de indicadores (EMA8, EMA21)
3. Geração com `mplfinance`
4. Conversão para PNG
5. Retorno como imagem

O frontend apenas:
- Faz a requisição
- Recebe a imagem PNG
- Exibe no navegador

**Processo otimizado e funcional!** 🚀

---

**Documento criado em:** Janeiro 2025
**Componentes:** Analysis.vue → SimpleChart.vue → `/api/v1/chart-image`

