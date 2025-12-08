# 🔄 COMO FUNCIONA O SISTEMA DE LOADING

## 📅 Data: Janeiro 2025

---

## 📊 VISÃO GERAL

O sistema de loading atual tem **2 níveis**:

1. **Loading da Análise** (`Analysis.vue`) - Quando busca dados da API
2. **Loading do Gráfico** (`InteractiveChart.vue`) - Quando carrega/renderiza o gráfico

---

## 🔍 1. LOADING DA ANÁLISE

### **Localização:** `frontend/src/views/Analysis.vue`

### **Como Funciona:**

```vue
<!-- Resultados -->
<div v-if="marketStore.loading" class="text-center py-8">
  <LoadingSpinner />
</div>

<div v-else-if="marketStore.error" class="card mb-8">
  <div class="text-red-500">Erro: {{ marketStore.error }}</div>
</div>

<div v-else-if="marketStore.analysisData" class="space-y-4">
  <!-- Conteúdo da análise -->
</div>
```

### **Fluxo:**

1. **Usuário clica em "Analisar"**
   ```javascript
   const loadAnalysis = async () => {
     await marketStore.analyze(selectedSymbol.value, selectedTimeframe.value)
   }
   ```

2. **Store define `loading = true`**
   ```javascript
   // market.js
   const analyze = async (symbol, timeframe) => {
     loading.value = true  // ✅ Ativa loading
     error.value = null
     
     try {
       const data = await api.analyze(symbol, timeframe)
       analysisData.value = data
       return data
     } catch (err) {
       error.value = err.message
       throw err
     } finally {
       loading.value = false  // ✅ Desativa loading
     }
   }
   ```

3. **Vue reage e mostra `LoadingSpinner`**
   - `v-if="marketStore.loading"` → Mostra spinner
   - `v-else-if="marketStore.error"` → Mostra erro
   - `v-else-if="marketStore.analysisData"` → Mostra dados

### **Componente LoadingSpinner:**

**Arquivo:** `frontend/src/components/common/LoadingSpinner.vue`

```vue
<template>
  <div class="flex justify-center items-center py-8">
    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-terminal-green"></div>
  </div>
</template>
```

**Características:**
- ✅ Spinner simples (círculo animado)
- ✅ Cor terminal-green
- ✅ Animação CSS (`animate-spin` do Tailwind)

---

## 📈 2. LOADING DO GRÁFICO

### **Localização:** `frontend/src/components/charts/InteractiveChart.vue`

### **Como Funciona:**

```vue
<div v-show="loading" class="flex items-center justify-center h-96 absolute inset-0 z-50 bg-terminal-dark/80">
  <div class="text-terminal-green">Carregando gráfico...</div>
</div>

<div v-show="error" class="flex items-center justify-center h-96 absolute inset-0 z-50 bg-terminal-dark/80">
  <div class="text-red-500 mb-4">Erro: {{ error }}</div>
  <button @click="refreshChart">Tentar Novamente</button>
</div>

<div 
  ref="chartWrapper"
  class="chart-sandbox"
  :style="{ display: loading || error ? 'none' : 'block' }"
>
  <!-- Gráfico aqui -->
</div>
```

### **Fluxo:**

1. **Componente monta ou props mudam**
   ```javascript
   watch([() => props.symbol, () => props.timeframe], () => {
     loading.value = true
     loadChartData()
   })
   ```

2. **Carrega dados do gráfico**
   ```javascript
   const loadChartData = async () => {
     loading.value = true
     try {
       const response = await api.getChartData(props.symbol, props.timeframe)
       chartData.value = response.data
       // Renderiza gráfico...
     } catch (err) {
       error.value = err.message
     } finally {
       loading.value = false
     }
   }
   ```

3. **Overlay de loading aparece**
   - Overlay absoluto sobre o gráfico
   - Fundo semi-transparente (`bg-terminal-dark/80`)
   - Texto "Carregando gráfico..."

---

## 🎨 3. COMPONENTES DE LOADING

### **A. LoadingSpinner.vue**

**Atual:**
```vue
<template>
  <div class="flex justify-center items-center py-8">
    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-terminal-green"></div>
  </div>
</template>
```

**Características:**
- ✅ Simples e funcional
- ⚠️ Sem mensagem personalizada
- ⚠️ Sem skeleton loading

### **B. Loading do Gráfico (Inline)**

**Atual:**
```vue
<div v-show="loading" class="flex items-center justify-center h-96 absolute inset-0 z-50 bg-terminal-dark/80">
  <div class="text-terminal-green">Carregando gráfico...</div>
</div>
```

**Características:**
- ✅ Overlay sobre o gráfico
- ✅ Fundo semi-transparente
- ⚠️ Apenas texto, sem spinner

---

## 🔄 4. FLUXO COMPLETO

```
1. USUÁRIO CLICA "ANALISAR"
   │
   ▼
2. marketStore.analyze() chamado
   │
   ├─ loading.value = true
   │
   ▼
3. API REQUEST (/api/analyze)
   │
   ├─ Backend processa análise (2-5s)
   │
   ▼
4. RESPOSTA RECEBIDA
   │
   ├─ analysisData.value = data
   ├─ loading.value = false
   │
   ▼
5. VUE REATIVO ATUALIZA
   │
   ├─ v-if="loading" → false (esconde spinner)
   ├─ v-else-if="analysisData" → true (mostra dados)
   │
   ▼
6. INTERACTIVECHART RECEBE PROPS
   │
   ├─ watch detecta mudança
   ├─ loading.value = true (gráfico)
   │
   ▼
7. CARREGA DADOS DO GRÁFICO
   │
   ├─ API request (/api/v1/chart-data)
   ├─ Renderiza gráfico (Lightweight Charts)
   │
   ▼
8. GRÁFICO PRONTO
   │
   └─ loading.value = false (gráfico)
```

---

## ⚠️ 5. LIMITAÇÕES ATUAIS

1. **Loading Spinner Simples:**
   - Apenas círculo animado
   - Sem mensagem contextual
   - Sem progresso

2. **Sem Skeleton Loading:**
   - Não mostra estrutura do conteúdo que virá
   - Usuário não sabe o que esperar

3. **Loading Separado:**
   - Análise e gráfico têm loading independente
   - Pode confundir usuário (2 loadings diferentes)

4. **Sem Feedback de Progresso:**
   - Não mostra etapas (ex: "Coletando dados...", "Analisando...")

---

## 💡 6. MELHORIAS SUGERIDAS

### **A. Loading Spinner Melhorado**

```vue
<template>
  <div class="loading-container">
    <div class="spinner"></div>
    <p class="loading-text">{{ message || 'Carregando...' }}</p>
    <p v-if="submessage" class="loading-subtext">{{ submessage }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: 'Carregando...' },
  submessage: { type: String, default: '' }
})
</script>
```

### **B. Skeleton Loading**

```vue
<template>
  <div class="skeleton-container">
    <div class="skeleton-card">
      <div class="skeleton-line w-1/3"></div>
      <div class="skeleton-line w-2/3"></div>
    </div>
    <div class="skeleton-card">
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
    </div>
  </div>
</template>
```

### **C. Loading com Etapas**

```vue
<template>
  <div class="loading-steps">
    <div v-for="(step, index) in steps" :key="index" 
         :class="{ 'active': currentStep === index, 'completed': currentStep > index }">
      <div class="step-icon">{{ currentStep > index ? '✓' : '○' }}</div>
      <div class="step-label">{{ step }}</div>
    </div>
  </div>
</template>
```

---

## 📝 7. RESUMO

### **Estado Atual:**

✅ **Funcional:**
- Loading spinner básico funciona
- Loading do gráfico funciona
- Estados de erro tratados

⚠️ **Melhorias Possíveis:**
- Adicionar mensagens contextuais
- Implementar skeleton loading
- Mostrar progresso/etapas
- Unificar loading de análise + gráfico

### **Arquivos Envolvidos:**

1. `frontend/src/components/common/LoadingSpinner.vue` - Spinner básico
2. `frontend/src/views/Analysis.vue` - Usa `marketStore.loading`
3. `frontend/src/stores/market.js` - Gerencia estado `loading`
4. `frontend/src/components/charts/InteractiveChart.vue` - Loading do gráfico

---

**Documento criado em:** Janeiro 2025
**Status:** ✅ Documentação completa do sistema de loading atual

