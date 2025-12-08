# 📐 PLANO: PRANCHETA DE ESTUDOS INTERATIVA

**Data:** 02 de Janeiro de 2025  
**Objetivo:** Transformar o gráfico em uma prancheta de estudos onde o usuário pode desenhar, anotar e salvar análises

---

## 🎯 OBJETIVO

Transformar o gráfico de um **visualizador passivo** em uma **prancheta de estudos interativa** onde o usuário pode:

- ✏️ **Desenhar** linhas, retângulos, círculos
- 📏 **Traçar Fibonacci** retracements
- 📝 **Anotar** textos em pontos específicos
- 🎯 **Marcar zonas** (FVG, Order Blocks, etc.)
- 💾 **Salvar** tudo e carregar depois
- 🔄 **Persistir** entre sessões

---

## 📊 ANÁLISE DO ESTADO ATUAL

### **Biblioteca Atual:**
- **Lightweight Charts v4.1.0** (TradingView)
- **Componente Principal:** `InteractiveChart.vue`
- **Características:**
  - ✅ Performance excelente
  - ✅ Leve e rápida
  - ✅ Suporta múltiplas séries
  - ❌ **NÃO tem ferramentas de desenho nativas**
  - ❌ **NÃO suporta anotações**
  - ❌ **NÃO tem overlay de desenho**

### **Estrutura Atual:**
```vue
<InteractiveChart.vue>
  ├── Lightweight Charts (canvas)
  ├── ChartLevelLines (overlay SVG - níveis S/R)
  ├── ChartInfoPanel (painel de informações)
  └── Cursor price indicator
```

---

## 🔍 OPÇÕES DE IMPLEMENTAÇÃO

### **OPÇÃO 1: TradingView Advanced Charts** ⭐ RECOMENDADO

#### **Vantagens:**
- ✅ **Ferramentas de desenho completas** (já prontas)
- ✅ **Barra de ferramentas nativa** (lápis, linhas, Fibonacci, etc.)
- ✅ **Anotações de texto** nativas
- ✅ **Templates de desenho** (salvar/load)
- ✅ **Ondas de Elliott** prontas
- ✅ **Retração de Fibonacci** automática
- ✅ **Persistência nativa** (salvar/load estado)
- ✅ **Profissional** (mesma biblioteca do TradingView.com)

#### **Desvantagens:**
- ⚠️ **Mais pesado** (~2-3 MB vs ~200 KB do Lightweight)
- ⚠️ **Mais complexo** de integrar
- ⚠️ **Requer licença** para uso comercial (gratuito para uso pessoal)
- ⚠️ **Menos customizável** visualmente

#### **Implementação:**
```javascript
// Substituir Lightweight Charts por TradingView Widget
new TradingView.widget({
  container_id: "tv_chart_container",
  library_path: "/charting_library/",
  enabled_features: [
    "drawing_templates",
    "left_toolbar",      // Barra de ferramentas
    "control_bar",
    "study_templates",
    "side_toolbar_in_fullscreen_mode"
  ],
  saved_data: loadSavedDrawings(),  // Carregar desenhos salvos
  auto_save_delay: 5,               // Auto-save a cada 5s
  // ...
})
```

#### **Custo:**
- **Uso Pessoal:** Gratuito
- **Uso Comercial:** Requer licença (contatar TradingView)

#### **Complexidade:** 🟡 MÉDIA
- Substituir componente atual
- Configurar biblioteca
- Integrar persistência

---

### **OPÇÃO 2: Lightweight Charts + Overlay SVG Customizado** ⭐⭐ FLEXÍVEL

#### **Vantagens:**
- ✅ **Mantém performance** do Lightweight Charts
- ✅ **Totalmente customizável** (você controla tudo)
- ✅ **Leve** (mantém ~200 KB)
- ✅ **Sem licenças** (open source)
- ✅ **Ferramentas únicas** (você cria o que quiser)
- ✅ **Visual personalizado** (estilo SNE)

#### **Desvantagens:**
- ⚠️ **Mais trabalho** (implementar tudo do zero)
- ⚠️ **Lógica matemática** (Fibonacci, etc. precisa calcular)
- ⚠️ **Mais código** para manter

#### **Implementação:**
```vue
<template>
  <div class="chart-sandbox">
    <!-- Canvas do Lightweight Charts -->
    <div ref="chartContainer"></div>
    
    <!-- Overlay SVG para desenhos -->
    <svg 
      ref="drawingOverlay"
      class="drawing-overlay"
      @mousedown="handleDrawingStart"
      @mousemove="handleDrawingMove"
      @mouseup="handleDrawingEnd"
    >
      <!-- Linhas desenhadas -->
      <line v-for="line in drawings.lines" :key="line.id" ... />
      
      <!-- Retângulos (zonas) -->
      <rect v-for="zone in drawings.zones" :key="zone.id" ... />
      
      <!-- Textos (anotações) -->
      <text v-for="note in drawings.notes" :key="note.id" ... />
      
      <!-- Fibonacci -->
      <g v-for="fib in drawings.fibonacci" :key="fib.id">
        <!-- Linhas de retração -->
      </g>
    </svg>
    
    <!-- Barra de ferramentas customizada -->
    <DrawingToolbar 
      :active-tool="activeTool"
      @tool-selected="selectTool"
    />
  </div>
</template>
```

#### **Complexidade:** 🔴 ALTA
- Implementar sistema de desenho
- Calcular coordenadas (preço ↔ pixel)
- Implementar ferramentas (linha, retângulo, etc.)
- Implementar Fibonacci (cálculo matemático)
- Sistema de persistência

---

### **OPÇÃO 3: Híbrido (Lightweight + Biblioteca de Desenho)**

#### **Vantagens:**
- ✅ Mantém Lightweight Charts
- ✅ Usa biblioteca de desenho pronta (ex: Fabric.js, Konva.js)
- ✅ Menos trabalho que Opção 2
- ✅ Mais flexível que Opção 1

#### **Desvantagens:**
- ⚠️ Duas bibliotecas (mais peso)
- ⚠️ Integração entre bibliotecas
- ⚠️ Sincronização de coordenadas

#### **Bibliotecas Possíveis:**
- **Fabric.js** - Canvas interativo
- **Konva.js** - Canvas 2D com eventos
- **Paper.js** - Desenho vetorial

#### **Complexidade:** 🟡 MÉDIA-ALTA

---

## 📋 COMPARAÇÃO DAS OPÇÕES

| Critério | TradingView | Lightweight + Custom | Híbrido |
|----------|-------------|---------------------|---------|
| **Ferramentas Prontas** | ✅ Sim | ❌ Não | 🟡 Parcial |
| **Performance** | 🟡 Boa | ✅ Excelente | 🟡 Boa |
| **Tamanho** | 🔴 ~2-3 MB | ✅ ~200 KB | 🟡 ~500 KB |
| **Customização** | 🟡 Média | ✅ Total | ✅ Alta |
| **Complexidade** | 🟡 Média | 🔴 Alta | 🟡 Média-Alta |
| **Licença** | ⚠️ Comercial | ✅ Livre | ✅ Livre |
| **Tempo Dev** | 🟡 2-3 dias | 🔴 1-2 semanas | 🟡 4-5 dias |
| **Manutenção** | 🟡 Baixa | 🔴 Alta | 🟡 Média |

---

## 🎯 RECOMENDAÇÃO

### **Para MVP Rápido:**
**Opção 1: TradingView Advanced Charts**

- Ferramentas prontas
- Implementação rápida
- Profissional

### **Para Solução Customizada:**
**Opção 2: Lightweight + SVG Overlay**

- Total controle
- Visual personalizado
- Sem dependências externas

---

## 🏗️ ARQUITETURA PROPOSTA (Opção 2 - Custom)

### **Estrutura de Componentes:**

```
InteractiveChart.vue (atual)
    ↓
StudyChart.vue (novo - prancheta de estudos)
    ├── Lightweight Charts (canvas - dados)
    ├── DrawingOverlay.vue (SVG - desenhos)
    ├── DrawingToolbar.vue (barra de ferramentas)
    ├── DrawingManager.js (lógica de desenho)
    └── DrawingStorage.js (persistência)
```

### **Camadas:**

```
┌─────────────────────────────────────────┐
│  DrawingToolbar (barra de ferramentas)  │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │  SVG Overlay (desenhos)          │  │
│  │  - Linhas                         │  │
│  │  - Retângulos                     │  │
│  │  - Textos                         │  │
│  │  - Fibonacci                      │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Lightweight Charts (canvas)      │  │
│  │  - Candles                        │  │
│  │  - Indicadores                    │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🛠️ FUNCIONALIDADES PLANEJADAS

### **1. Ferramentas de Desenho**

#### **1.1. Linha Simples**
- Clicar e arrastar para desenhar
- Mostrar coordenadas (preço, tempo)
- Editar (mover pontos)
- Deletar

#### **1.2. Linha Horizontal (S/R)**
- Clicar em um preço
- Linha horizontal infinita
- Mostrar preço na linha
- Editar (mover para cima/baixo)

#### **1.3. Linha Vertical (Tempo)**
- Clicar em um tempo
- Linha vertical
- Mostrar timestamp

#### **1.4. Retângulo (Zona)**
- Clicar e arrastar para criar retângulo
- Usar para marcar FVG, Order Blocks
- Preencher com cor semitransparente
- Mostrar preço min/max

#### **1.5. Círculo/Ellipse**
- Clicar e arrastar
- Marcar áreas de interesse

#### **1.6. Lápis (Freehand)**
- Desenhar livremente
- Capturar movimento do mouse
- Suavizar traço

#### **1.7. Texto (Anotação)**
- Clicar no gráfico
- Abrir input de texto
- Posicionar texto
- Editar texto
- Mover texto

#### **1.8. Régua (Medição)**
- Clicar em dois pontos
- Mostrar:
  - Distância em preço ($)
  - Distância em %
  - Distância em tempo
  - Número de candles

#### **1.9. Fibonacci Retracement**
- Clicar em dois pontos (alta → baixa ou baixa → alta)
- Calcular automaticamente:
  - 0% (ponto inicial)
  - 23.6%
  - 38.2%
  - 50%
  - 61.8%
  - 78.6%
  - 100% (ponto final)
- Desenhar linhas horizontais
- Mostrar % em cada linha

#### **1.10. Ondas de Elliott (Futuro)**
- Marcar ondas 1-2-3-4-5
- Calcular projeções

---

### **2. Barra de Ferramentas**

```
┌─────────────────────────────────────┐
│ [✏️] [─] [│] [▭] [○] [✎] [📝] [📏] [📊] │
└─────────────────────────────────────┘
```

**Ferramentas:**
- ✏️ **Selecionar** - Selecionar/mover desenhos
- ─ **Linha Horizontal** - S/R
- │ **Linha Vertical** - Tempo
- ▭ **Retângulo** - Zona
- ○ **Círculo** - Área
- ✎ **Lápis** - Freehand
- 📝 **Texto** - Anotação
- 📏 **Régua** - Medição
- 📊 **Fibonacci** - Retracement

**Controles:**
- 🎨 **Cor** - Seletor de cor
- 📏 **Espessura** - Espessura da linha
- 🗑️ **Deletar** - Deletar selecionado
- 💾 **Salvar** - Salvar desenhos
- 📂 **Carregar** - Carregar desenhos

---

### **3. Sistema de Coordenadas**

#### **Conversão Preço ↔ Pixel:**

```javascript
// Preço → Pixel Y
function priceToPixel(price) {
  const priceRange = chart.priceScale().getVisibleRange()
  const pixelRange = chart.height()
  const ratio = (price - priceRange.min) / (priceRange.max - priceRange.min)
  return pixelRange - (ratio * pixelRange) // Invertido (Y cresce para baixo)
}

// Pixel Y → Preço
function pixelToPrice(pixelY) {
  const priceRange = chart.priceScale().getVisibleRange()
  const pixelRange = chart.height()
  const ratio = (pixelRange - pixelY) / pixelRange // Invertido
  return priceRange.min + (ratio * (priceRange.max - priceRange.min))
}

// Tempo → Pixel X
function timeToPixel(time) {
  const timeRange = chart.timeScale().getVisibleRange()
  const pixelRange = chart.width()
  const ratio = (time - timeRange.from) / (timeRange.to - timeRange.from)
  return ratio * pixelRange
}

// Pixel X → Tempo
function pixelToTime(pixelX) {
  const timeRange = chart.timeScale().getVisibleRange()
  const pixelRange = chart.width()
  const ratio = pixelX / pixelRange
  return timeRange.from + (ratio * (timeRange.to - timeRange.from))
}
```

---

### **4. Estrutura de Dados**

#### **4.1. Formato de Desenho:**

```typescript
interface Drawing {
  id: string                    // UUID único
  type: 'line' | 'rectangle' | 'text' | 'fibonacci' | 'freehand'
  symbol: string                // BTCUSDT
  timeframe: string             // 1h
  created_at: number            // Timestamp
  updated_at: number            // Timestamp
  
  // Estilo
  color: string                 // #00ff00
  strokeWidth: number           // 2
  opacity: number               // 0.8
  
  // Dados específicos por tipo
  data: LineData | RectangleData | TextData | FibonacciData | FreehandData
}

interface LineData {
  start: { price: number, time: number }
  end: { price: number, time: number }
  style: 'solid' | 'dashed' | 'dotted'
}

interface RectangleData {
  topLeft: { price: number, time: number }
  bottomRight: { price: number, time: number }
  fill: boolean
  fillColor: string
  fillOpacity: number
}

interface TextData {
  position: { price: number, time: number }
  text: string
  fontSize: number
  fontFamily: string
  backgroundColor: string
}

interface FibonacciData {
  start: { price: number, time: number }
  end: { price: number, time: number }
  levels: number[]              // [0, 23.6, 38.2, 50, 61.8, 78.6, 100]
  direction: 'up' | 'down'      // Alta → Baixa ou Baixa → Alta
}

interface FreehandData {
  points: Array<{ price: number, time: number }>
  smoothed: boolean
}
```

#### **4.2. Estrutura de Armazenamento:**

```json
{
  "version": "1.0.0",
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "drawings": [
    {
      "id": "uuid-1",
      "type": "line",
      "color": "#00ff00",
      "data": { ... }
    },
    {
      "id": "uuid-2",
      "type": "text",
      "data": {
        "position": { "price": 42500, "time": 1704067200 },
        "text": "OLHA ESSE FVG AQUI"
      }
    }
  ],
  "metadata": {
    "created_at": 1704067200,
    "updated_at": 1704067300
  }
}
```

---

### **5. Persistência**

#### **5.1. Armazenamento Local (Electron):**

```javascript
// Salvar no sistema de arquivos do Electron
const fs = require('fs')
const path = require('path')

// Diretório de estudos
const studiesDir = path.join(
  app.getPath('userData'),
  'chart_studies'
)

// Estrutura:
// chart_studies/
//   ├── BTCUSDT_1h.json
//   ├── BTCUSDT_4h.json
//   ├── ETHUSDT_1h.json
//   └── ...
```

#### **5.2. Auto-Save:**

```javascript
// Auto-save a cada 5 segundos
setInterval(() => {
  saveDrawings()
}, 5000)

// Save manual (Ctrl+S)
window.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 's') {
    e.preventDefault()
    saveDrawings()
  }
})
```

#### **5.3. Sincronização Cloud (Opcional):**

```javascript
// Salvar no backend (se autenticado)
if (isAuthenticated) {
  await api.post('/api/chart/studies', {
    symbol: 'BTCUSDT',
    timeframe: '1h',
    drawings: drawings.value
  })
}
```

---

## 🎨 INTERFACE DO USUÁRIO

### **Layout Proposto:**

```
┌─────────────────────────────────────────────────────────┐
│  [BTCUSDT] [1h]  [🔄]  [💾 Salvar]  [📂 Carregar]      │
├─────────────────────────────────────────────────────────┤
│  ┌───┐                                                   │
│  │ ✏️│  ┌───────────────────────────────────────────┐   │
│  │ ─ │  │                                           │   │
│  │ │ │  │         GRÁFICO + DESENHOS                │   │
│  │ ▭ │  │                                           │   │
│  │ ○ │  │                                           │   │
│  │ ✎ │  │                                           │   │
│  │ 📝│  │                                           │   │
│  │ 📏│  │                                           │   │
│  │ 📊│  │                                           │   │
│  │ 🎨│  └───────────────────────────────────────────┘   │
│  │ 🗑️│                                                   │
│  └───┘                                                   │
└─────────────────────────────────────────────────────────┘
```

### **Barra Lateral de Ferramentas:**

- **Posição:** Esquerda do gráfico
- **Estilo:** Minimalista, estilo terminal
- **Ferramentas:** Ícones grandes, fácil de clicar
- **Ativo:** Destaque visual na ferramenta selecionada

---

## 🔄 FLUXO DE USO

### **1. Desenhar Linha:**

```
1. Clicar em "─" (linha horizontal)
2. Clicar no gráfico (preço desejado)
3. Linha aparece
4. Arrastar para mover
5. Clicar na linha → menu: Editar | Deletar
```

### **2. Anotar Texto:**

```
1. Clicar em "📝" (texto)
2. Clicar no gráfico (posição)
3. Input aparece
4. Digitar: "OLHA ESSE FVG AQUI"
5. Enter para confirmar
6. Texto aparece no gráfico
```

### **3. Fibonacci:**

```
1. Clicar em "📊" (Fibonacci)
2. Clicar no ponto de início (ex: topo)
3. Clicar no ponto de fim (ex: fundo)
4. Linhas de retração aparecem automaticamente
5. Mostrar % em cada linha
```

### **4. Salvar:**

```
1. Clicar em "💾 Salvar"
2. Ou Ctrl+S
3. Salva automaticamente em:
   ~/Library/Application Support/SNE_RADAR/chart_studies/BTCUSDT_1h.json
4. Confirmação: "✅ Desenhos salvos!"
```

### **5. Carregar:**

```
1. Ao abrir gráfico BTCUSDT 1h
2. Sistema busca: chart_studies/BTCUSDT_1h.json
3. Se existir, carrega automaticamente
4. Desenhos aparecem no gráfico
```

---

## 📦 COMPONENTES NECESSÁRIOS

### **Novos Componentes:**

1. **`StudyChart.vue`** - Componente principal (substitui InteractiveChart)
2. **`DrawingOverlay.vue`** - SVG overlay para desenhos
3. **`DrawingToolbar.vue`** - Barra de ferramentas
4. **`DrawingManager.js`** - Lógica de desenho
5. **`DrawingStorage.js`** - Persistência
6. **`CoordinateConverter.js`** - Conversão preço ↔ pixel
7. **`FibonacciCalculator.js`** - Cálculo de Fibonacci
8. **`TextAnnotation.vue`** - Componente de texto editável

### **Utilitários:**

1. **`drawingUtils.js`** - Funções auxiliares
2. **`drawingTypes.js`** - Definições de tipos
3. **`drawingValidators.js`** - Validações

---

## 🗄️ ESTRUTURA DE ARMAZENAMENTO

### **Local (Electron):**

```
~/Library/Application Support/SNE_RADAR/
  └── chart_studies/
      ├── BTCUSDT_1h.json
      ├── BTCUSDT_4h.json
      ├── ETHUSDT_1h.json
      └── ...
```

### **Formato JSON:**

```json
{
  "version": "1.0.0",
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "drawings": [
    {
      "id": "line-001",
      "type": "line",
      "color": "#00ff00",
      "strokeWidth": 2,
      "data": {
        "start": { "price": 42500, "time": 1704067200 },
        "end": { "price": 42500, "time": 1704070800 },
        "style": "solid"
      },
      "created_at": 1704067200
    },
    {
      "id": "text-001",
      "type": "text",
      "color": "#ffffff",
      "data": {
        "position": { "price": 43000, "time": 1704069000 },
        "text": "OLHA ESSE FVG AQUI",
        "fontSize": 14
      },
      "created_at": 1704069000
    },
    {
      "id": "fib-001",
      "type": "fibonacci",
      "color": "#ffff00",
      "data": {
        "start": { "price": 45000, "time": 1704067200 },
        "end": { "price": 40000, "time": 1704070800 },
        "direction": "down",
        "levels": [0, 23.6, 38.2, 50, 61.8, 78.6, 100]
      },
      "created_at": 1704070000
    }
  ]
}
```

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### **1. Sistema de Coordenadas**

#### **Desafio:**
Lightweight Charts usa canvas, SVG overlay precisa sincronizar coordenadas.

#### **Solução:**
```javascript
// Converter coordenadas do gráfico para SVG
class CoordinateConverter {
  constructor(chart) {
    this.chart = chart
  }
  
  priceToY(price) {
    // Usar priceScale do chart
    const priceScale = this.chart.priceScale('right')
    const coordinate = priceScale.priceToCoordinate(price)
    return coordinate
  }
  
  timeToX(time) {
    // Usar timeScale do chart
    const timeScale = this.chart.timeScale()
    const coordinate = timeScale.timeToCoordinate(time)
    return coordinate
  }
  
  pixelToPrice(y) {
    const priceScale = this.chart.priceScale('right')
    return priceScale.coordinateToPrice(y)
  }
  
  pixelToTime(x) {
    const timeScale = this.chart.timeScale()
    return timeScale.coordinateToTime(x)
  }
}
```

### **2. Sistema de Desenho**

#### **Estados:**
```javascript
const drawingState = {
  mode: 'select' | 'line' | 'rectangle' | 'text' | 'fibonacci' | 'freehand',
  isDrawing: false,
  startPoint: null,
  currentPoint: null,
  selectedDrawing: null
}
```

#### **Event Handlers:**
```javascript
// Mouse down - Iniciar desenho
function handleMouseDown(event) {
  if (drawingState.mode === 'select') {
    // Selecionar desenho existente
    selectDrawing(event)
  } else {
    // Iniciar novo desenho
    startDrawing(event)
  }
}

// Mouse move - Continuar desenho
function handleMouseMove(event) {
  if (drawingState.isDrawing) {
    updateDrawing(event)
  }
}

// Mouse up - Finalizar desenho
function handleMouseUp(event) {
  if (drawingState.isDrawing) {
    finishDrawing(event)
  }
}
```

### **3. Renderização SVG**

#### **Sincronização com Chart:**
```javascript
// SVG overlay deve ter mesmo tamanho do chart
watch([chartWidth, chartHeight], () => {
  drawingOverlay.value.setAttribute('width', chartWidth.value)
  drawingOverlay.value.setAttribute('height', chartHeight.value)
})

// Reposicionar desenhos quando chart zoom/pan
chart.value.subscribeCrosshairMove((param) => {
  // Atualizar posições dos desenhos
  redrawDrawings()
})
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### **FASE 1: Fundação**
- [ ] Criar `StudyChart.vue` (wrapper)
- [ ] Criar `DrawingOverlay.vue` (SVG overlay)
- [ ] Implementar `CoordinateConverter.js`
- [ ] Sincronizar SVG com chart (tamanho, zoom, pan)

### **FASE 2: Ferramentas Básicas**
- [ ] Criar `DrawingToolbar.vue`
- [ ] Implementar seleção de ferramenta
- [ ] Implementar linha horizontal
- [ ] Implementar linha vertical
- [ ] Implementar retângulo

### **FASE 3: Ferramentas Avançadas**
- [ ] Implementar texto (anotação)
- [ ] Implementar régua (medição)
- [ ] Implementar Fibonacci retracement
- [ ] Implementar lápis (freehand)

### **FASE 4: Interatividade**
- [ ] Selecionar desenho (clicar)
- [ ] Mover desenho (arrastar)
- [ ] Editar desenho (propriedades)
- [ ] Deletar desenho

### **FASE 5: Persistência**
- [ ] Criar `DrawingStorage.js`
- [ ] Implementar salvar (local)
- [ ] Implementar carregar (local)
- [ ] Auto-save (a cada 5s)
- [ ] Save manual (Ctrl+S)

### **FASE 6: UI/UX**
- [ ] Estilizar barra de ferramentas
- [ ] Adicionar feedback visual
- [ ] Adicionar tooltips
- [ ] Adicionar atalhos de teclado

---

## 🎯 DECISÃO: QUAL OPÇÃO ESCOLHER?

### **Recomendação por Cenário:**

#### **Cenário 1: MVP Rápido (1-2 dias)**
→ **Opção 1: TradingView Advanced Charts**
- Ferramentas prontas
- Implementação rápida
- Profissional

#### **Cenário 2: Solução Customizada (1-2 semanas)**
→ **Opção 2: Lightweight + SVG Overlay**
- Total controle
- Visual personalizado
- Sem licenças

#### **Cenário 3: Meio Termo (3-5 dias)**
→ **Opção 3: Híbrido (Lightweight + Konva.js)**
- Mantém performance
- Biblioteca de desenho pronta
- Customizável

---

## 📊 ESTIMATIVA DE ESFORÇO

### **Opção 1: TradingView**
- **Tempo:** 2-3 dias
- **Complexidade:** Média
- **Linhas de código:** ~500-800

### **Opção 2: Custom (SVG)**
- **Tempo:** 1-2 semanas
- **Complexidade:** Alta
- **Linhas de código:** ~2000-3000

### **Opção 3: Híbrido (Konva)**
- **Tempo:** 4-5 dias
- **Complexidade:** Média-Alta
- **Linhas de código:** ~1000-1500

---

## 🚀 PRÓXIMOS PASSOS (Após Decisão)

1. **Escolher opção** (TradingView vs Custom vs Híbrido)
2. **Criar branch** de desenvolvimento
3. **Implementar FASE 1** (fundação)
4. **Testar** sincronização coordenadas
5. **Implementar FASE 2** (ferramentas básicas)
6. **Iterar** e melhorar

---

## 💡 CONSIDERAÇÕES FINAIS

### **Vantagens da Solução Custom:**
- ✅ Visual 100% personalizado (estilo SNE)
- ✅ Ferramentas únicas (você decide o que criar)
- ✅ Sem dependências externas
- ✅ Performance máxima
- ✅ Sem licenças

### **Vantagens do TradingView:**
- ✅ Ferramentas profissionais prontas
- ✅ Implementação rápida
- ✅ Testado e confiável
- ✅ Suporte da comunidade

### **Recomendação Final:**
Para um produto comercial como o SNE Radar, recomendo começar com **Opção 2 (Custom)** para ter controle total e criar uma experiência única. Se precisar de velocidade, começar com **Opção 1 (TradingView)** e migrar depois.

---

**Status:** 📋 Plano Completo - Aguardando Decisão

**Próximo Passo:** Escolher opção e iniciar implementação


