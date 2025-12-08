# 📊 COMO O GRÁFICO É GERADO NA PÁGINA DE ANÁLISE

## 🎯 VISÃO GERAL

O gráfico na página de **Analysis** é gerado através de um processo que vai do frontend Vue.js até o backend Flask, que cria uma imagem PNG usando `mplfinance` e `matplotlib`.

---

## 🔄 FLUXO COMPLETO

```
┌─────────────────────────────────────────────────────────────┐
│  1. FRONTEND (Analysis.vue)                                 │
│     └─► Usa componente SimpleChart.vue                      │
│              │                                               │
│              ▼                                               │
│  2. SIMPLECHART.VUE                                         │
│     └─► Faz fetch para /api/v1/chart-image                 │
│              │                                               │
│              ▼                                               │
│  3. BACKEND (sne_radar_web.py)                              │
│     └─► Endpoint /api/v1/chart-image                        │
│         ├─► Busca dados da Binance                          │
│         ├─► Calcula indicadores (EMA8, EMA21)               │
│         ├─► Gera gráfico com mplfinance                     │
│         ├─► Converte para PNG (BytesIO)                     │
│         └─► Retorna imagem PNG                              │
│              │                                               │
│              ▼                                               │
│  4. FRONTEND (SimpleChart.vue)                              │
│     └─► Recebe blob da imagem                               │
│         ├─► Cria URL de objeto (blob URL)                   │
│         └─► Exibe no <img> tag                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 1. FRONTEND: COMPONENTE ANALYSIS.VUE

### **Localização:** `frontend/src/views/Analysis.vue`

**O que faz:**
- Renderiza o componente `SimpleChart.vue`
- Passa `symbol` e `timeframe` como props

**Código relevante:**
```vue
<SimpleChart 
  :key="`${marketStore.currentSymbol}-${marketStore.currentTimeframe}`"
  :symbol="marketStore.currentSymbol"
  :timeframe="marketStore.currentTimeframe"
/>
```

---

## 📝 2. FRONTEND: COMPONENTE SIMPLECHART.VUE

### **Localização:** `frontend/src/components/charts/SimpleChart.vue`

**O que faz:**
1. Monta a URL do endpoint do gráfico
2. Faz fetch da imagem como blob
3. Cria blob URL para exibir
4. Gerencia loading/error states

**Fluxo:**

#### **A. Construção da URL:**
```javascript
const getChartUrl = () => {
  const timestamp = new Date().getTime()  // Cache busting
  const isDev = import.meta.env.DEV
  
  // Em dev: acessa Flask diretamente (porta 9999)
  // Em prod: usa URL relativa
  const baseUrl = isDev ? 'http://localhost:9999' : ''
  const url = `${baseUrl}/api/v1/chart-image?symbol=${props.symbol}&interval=${props.timeframe}&t=${timestamp}`
  return url
}
```

#### **B. Carregamento da Imagem:**
```javascript
const loadChart = async () => {
  // 1. Faz fetch da URL
  const response = await fetch(url, {
    method: 'GET',
    mode: 'cors',
    credentials: 'omit',
    cache: 'no-cache'
  })
  
  // 2. Valida Content-Type (deve ser image/png)
  const contentType = response.headers.get('content-type')
  if (!contentType || !contentType.includes('image')) {
    error.value = 'Servidor não retornou uma imagem'
    return
  }
  
  // 3. Converte para blob
  const blob = await response.blob()
  
  // 4. Cria blob URL (evita problemas de CORS/proxy)
  const blobUrl = URL.createObjectURL(blob)
  
  // 5. Atribui ao chartImageUrl para exibir no <img>
  chartImageUrl.value = blobUrl
}
```

#### **C. Exibição:**
```vue
<img 
  :src="chartImageUrl" 
  :alt="`Gráfico ${symbol} ${timeframe}`"
  class="chart-image"
  @error="handleImageError"
  @load="handleImageLoad"
/>
```

**Por que usar Blob URL?**
- ✅ Evita problemas de CORS com imagens
- ✅ Funciona com proxy do Vite
- ✅ Não expõe URL real do servidor

---

## 📝 3. BACKEND: ENDPOINT /api/v1/chart-image

### **Localização:** `sne_radar_web.py` (linha ~2013)

### **Processo Completo:**

#### **Passo 1: Receber Requisição**
```python
@app.route('/api/v1/chart-image')
def api_v1_chart_image():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
```

#### **Passo 2: Importar Bibliotecas**
```python
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo
import matplotlib.pyplot as plt
import mplfinance as mpf
```

#### **Passo 3: Buscar Dados**
```python
# Tenta usar grafico_candlestick.py primeiro
try:
    from grafico_candlestick import obter_dados_candlestick, calcular_indicadores_grafico
    df = obter_dados_candlestick(symbol, interval, limit=200)
    df = calcular_indicadores_grafico(df)  # Adiciona EMAs
except:
    # Fallback: buscar_dados_binance
    df = buscar_dados_binance(symbol, interval, 200)
    df['EMA8'] = df['close'].ewm(span=8).mean()
    df['EMA21'] = df['close'].ewm(span=21).mean()
```

**Dados obtidos:**
- DataFrame com colunas: `open`, `high`, `low`, `close`, `volume`
- EMA8 e EMA21 calculadas
- ~200 candles (últimos períodos)

#### **Passo 4: Configurar Estilo**
```python
# Cores do mercado
mc = mpf.make_marketcolors(
    up='#00ff88',      # Verde para velas de alta
    down='#ff4444',    # Vermelho para velas de baixa
    wick={'up':'#00ff88', 'down':'#ff4444'},
    volume='in',
    alpha=0.9
)

# Estilo completo
s = mpf.make_mpf_style(
    marketcolors=mc,
    gridstyle='',
    facecolor='#1a1a1a',      # Fundo escuro
    figcolor='#0a0a0a',        # Cor da figura
    gridcolor='#333333',       # Grid
    # Cores de texto
    rc={
        'font.size': 11,
        'axes.labelcolor': 'white',
        'axes.edgecolor': 'white',
        'xtick.color': 'white',
        'ytick.color': 'white',
        'text.color': 'white'
    }
)
```

#### **Passo 5: Preparar Indicadores Adicionais**
```python
apds = []  # Additional plots

# EMA8 em ciano
if 'EMA8' in df.columns:
    apds.append(mpf.make_addplot(
        df['EMA8'], 
        color='cyan', 
        width=1.5, 
        label='EMA 8'
    ))

# EMA21 em laranja
if 'EMA21' in df.columns:
    apds.append(mpf.make_addplot(
        df['EMA21'], 
        color='orange', 
        width=1.5, 
        label='EMA 21'
    ))
```

#### **Passo 6: Gerar Gráfico**
```python
fig, axes = mpf.plot(
    df_plot,                    # DataFrame com OHLCV
    type='candle',              # Tipo: candlestick
    style=s,                    # Estilo configurado
    title=f'{symbol} - {interval}',
    ylabel='Preço (USDT)',
    volume=True,                # Mostrar volume
    ylabel_lower='Volume',
    addplot=apds,               # EMAs sobrepostas
    figsize=(16, 10),           # Tamanho (largura, altura)
    returnfig=True,             # Retornar figura
    show_nontrading=False,      # Não mostrar períodos não-negociados
    warn_too_much_data=False    # Suprimir avisos
)
```

**O que é gerado:**
- Gráfico de candlestick
- Volume abaixo
- EMA8 (linha ciano)
- EMA21 (linha laranja)
- Estilo escuro (terminal)

#### **Passo 7: Converter para PNG**
```python
# Criar buffer em memória
buffer = io.BytesIO()

# Salvar figura no buffer
plt.savefig(
    buffer,
    format='png',               # Formato PNG
    dpi=150,                    # Resolução
    bbox_inches='tight',        # Ajustar bordas
    facecolor='#0a0a0a',        # Fundo
    edgecolor='white',          # Borda
    pad_inches=0.2              # Padding
)

buffer.seek(0)                  # Voltar ao início
plt.close(fig)                  # Fechar figura (liberar memória)
```

#### **Passo 8: Retornar Resposta**
```python
# Obter bytes da imagem
image_bytes = buffer.getvalue()

# Criar resposta Flask
response = make_response(image_bytes)
response.headers['Content-Type'] = 'image/png'
response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
response.headers['Content-Length'] = str(len(image_bytes))

# Headers CORS
response.headers['Access-Control-Allow-Origin'] = origin or '*'
response.headers['Access-Control-Allow-Credentials'] = 'true'

return response
```

---

## 🎨 4. CARACTERÍSTICAS DO GRÁFICO

### **Elementos Visuais:**
- ✅ **Candlesticks** com cores verde/vermelho
- ✅ **Volume** no subplot inferior
- ✅ **EMA8** (linha ciano)
- ✅ **EMA21** (linha laranja)
- ✅ **Tema escuro** (terminal style)
- ✅ **Título** com símbolo e timeframe

### **Parâmetros:**
- **Tamanho:** 16x10 polegadas
- **Resolução:** 150 DPI
- **Candles:** ~200 períodos
- **Formato:** PNG

---

## 🔧 5. BIBLIOTECAS UTILIZADAS

### **Backend:**
- **mplfinance** - Geração de gráficos de candlestick profissionais
- **matplotlib** - Visualização e renderização
- **pandas** - Manipulação de dados
- **numpy** - Cálculos numéricos

### **Frontend:**
- **Vue.js 3** - Framework
- **Fetch API** - Requisições HTTP
- **Blob API** - Manipulação de binários

---

## ⚡ 6. OTIMIZAÇÕES

### **1. Cache Busting:**
- Timestamp na URL (`&t=timestamp`) evita cache do navegador

### **2. Blob URL:**
- Carrega imagem como blob primeiro
- Cria URL de objeto para exibição
- Evita problemas de CORS/proxy

### **3. Lazy Loading:**
- Gráfico só carrega quando componente é montado
- Recarrega quando `symbol` ou `timeframe` mudam

### **4. Error Handling:**
- Validação de Content-Type
- Imagem de erro se falhar
- Mensagens claras de erro

---

## 🐛 7. TRATAMENTO DE ERROS

### **Erro: Dados não disponíveis**
```python
return create_error_image(f"Dados não disponíveis para {symbol} ({interval})")
```

### **Erro: Formato inválido**
```python
return create_error_image("Formato de dados inválido")
```

### **Erro: Falha na geração**
```python
return create_error_image(f"Erro ao criar gráfico: {str(e)}")
```

**Função `create_error_image()`:**
- Cria imagem PNG simples com mensagem de erro
- Estilo consistente com o gráfico
- Retorna como PNG (mesmo formato)

---

## 📊 8. EXEMPLO DE FLUXO COMPLETO

```
1. Usuário acessa Analysis.vue
   └─► Seleciona BTCUSDT, 1h

2. SimpleChart.vue monta URL:
   └─► http://localhost:9999/api/v1/chart-image?symbol=BTCUSDT&interval=1h&t=1234567890

3. Fetch para o endpoint

4. Backend processa:
   ├─► Busca dados Binance (200 candles)
   ├─► Calcula EMA8, EMA21
   ├─► Gera gráfico com mplfinance
   ├─► Converte para PNG (BytesIO)
   └─► Retorna PNG (image/png)

5. Frontend recebe:
   ├─► Valida Content-Type
   ├─► Converte para blob
   ├─► Cria blob URL
   └─► Exibe no <img>

6. Usuário vê gráfico na tela! ✅
```

---

## 🔍 9. PONTOS IMPORTANTES

### **Por que não usar Chart.js/TradingView?**
- Gráfico é gerado no **servidor** (server-side rendering)
- Vantagem: Funciona mesmo sem JavaScript no cliente
- Vantagem: Controle total sobre o estilo
- Vantagem: Pode ser usado em outros contextos (Telegram, PDF, etc.)

### **Por que Blob URL?**
- Evita problemas de CORS com imagens
- Funciona com proxy do Vite em desenvolvimento
- Não expõe URL real do servidor

### **Por que mplfinance?**
- Biblioteca especializada em gráficos financeiros
- Suporte nativo a candlesticks
- Fácil de adicionar indicadores
- Estilização profissional

---

## 📝 10. MUDANÇAS RECENTES

### **Cache Busting:**
- Adicionado timestamp na URL para evitar cache

### **Blob URL:**
- Implementado para resolver problemas de CORS/proxy

### **Error Handling:**
- Validação de Content-Type
- Imagens de erro personalizadas

---

## ✅ CONCLUSÃO

O gráfico na página de Analysis é gerado através de:

1. **Frontend Vue.js** → Componente SimpleChart.vue
2. **Requisição HTTP** → GET `/api/v1/chart-image`
3. **Backend Flask** → Endpoint que gera PNG
4. **Bibliotecas Python:**
   - `mplfinance` para candlesticks
   - `matplotlib` para renderização
5. **Retorno** → Imagem PNG via blob URL

**Todo o processo é otimizado para performance e compatibilidade!** 🚀

---

**Documento criado em:** Janeiro 2025
**Componentes envolvidos:** Analysis.vue, SimpleChart.vue, `/api/v1/chart-image`

