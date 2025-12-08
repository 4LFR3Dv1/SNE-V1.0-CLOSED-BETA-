<template>
  <div class="analysis">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">Análise Técnica</h1>
      <p class="text-terminal-green/70">Análise completa do mercado</p>
    </div>

    <!-- Seletores - Uma linha compacta -->
    <div class="card mb-8">
      <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div class="flex-1 w-full sm:w-auto">
          <SymbolAutocomplete
            v-model="selectedSymbol" 
            placeholder="Digite 3 letras (ex: BTC, ETH)..."
            @select="handleSymbolSelect"
          />
        </div>
        <div class="flex-shrink-0">
          <TimeframeSelector
            v-model="selectedTimeframe" 
            @change="handleTimeframeChange"
          />
      </div>
      <button 
        @click="loadAnalysis" 
          class="btn-primary flex-shrink-0"
        :disabled="marketStore.loading"
      >
        {{ marketStore.loading ? 'Analisando...' : 'Analisar' }}
      </button>
      </div>
    </div>

    <!-- Gráfico Interativo (Imagem com Zoom/Pan) -->
    <div class="card mb-8 w-full" style="min-height: 550px;">
      <InteractiveChart 
        :key="`${selectedSymbol}-${selectedTimeframe}`"
        :symbol="selectedSymbol"
        :timeframe="selectedTimeframe"
      />
    </div>

    <!-- Resultados -->
    <div v-if="marketStore.loading" class="text-center py-8">
      <LoadingSpinner />
    </div>

    <div v-else-if="marketStore.error" class="card mb-8">
      <div class="text-red-500">
        Erro: {{ marketStore.error }}
      </div>
    </div>

    <div v-else-if="marketStore.analysisData" class="space-y-4">
      <!-- Sinal Hero - Componente Novo -->
      <SignalHero
        :signal="marketStore.signal"
        :score="marketStore.score"
        :recommendation="marketStore.analysisData?.sintese?.recomendacao"
        :entryPrice="marketStore.analysisData?.niveis_operacionais?.entry_price"
        :riskLevel="marketStore.analysisData?.sintese?.risco"
        :riskMessage="getRiskMessage(marketStore.analysisData?.sintese?.risco)"
        :signalType="getSignalType(marketStore.analysisData?.sintese?.recomendacao)"
        :timeframe="selectedTimeframe"
        @action-click="handleSignalAction"
      />

      <!-- Confluência - Componente Novo -->
      <ConfluenceGrid
        v-if="marketStore.analysisData?.confluencia"
        :score="marketStore.analysisData.confluencia.score || 0"
        :interpretation="marketStore.analysisData.confluencia.interpretacao"
        :validations="marketStore.analysisData.confluencia.validacoes || []"
      />

      <!-- Resumo da Análise -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <!-- Contexto -->
        <div class="card">
          <h3 class="text-lg font-bold mb-2">Contexto</h3>
          <div class="space-y-1 text-sm">
            <div><span class="text-terminal-green/70">Regime:</span> {{ marketStore.analysisData?.contexto?.regime || '--' }}</div>
            <div><span class="text-terminal-green/70">Volatilidade:</span> {{ marketStore.analysisData?.contexto?.volatilidade_status || '--' }}</div>
            <div><span class="text-terminal-green/70">Volume:</span> {{ marketStore.analysisData?.contexto?.volume_status || '--' }}</div>
            <div><span class="text-terminal-green/70">Preço:</span> ${{ marketStore.analysisData?.contexto?.preco_atual?.toLocaleString() || '--' }}</div>
          </div>
        </div>

        <!-- Estrutura -->
        <div class="card">
          <h3 class="text-lg font-bold mb-2">Estrutura</h3>
          <div class="space-y-1 text-sm">
            <div><span class="text-terminal-green/70">Tendência:</span> {{ marketStore.analysisData?.estrutura?.tendencia || '--' }}</div>
            <div><span class="text-terminal-green/70">Tipo:</span> {{ marketStore.analysisData?.estrutura?.tipo_estrutura || '--' }}</div>
            <div><span class="text-terminal-green/70">Suportes:</span> {{ marketStore.analysisData?.estrutura?.suportes?.length || 0 }}</div>
            <div><span class="text-terminal-green/70">Resistências:</span> {{ marketStore.analysisData?.estrutura?.resistencias?.length || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- Multi-Timeframe - Componente Novo -->
      <MultiTimeframeTimeline
        v-if="marketStore.analysisData?.mtf"
        :timeframes="marketStore.analysisData.mtf.timeframes || {}"
        :summary="marketStore.analysisData.mtf.resumo"
        :confluence="marketStore.analysisData.mtf.confluencia"
      />

      <!-- Indicadores - Usando MetricCard -->
      <div class="card mb-4">
        <h3 class="text-lg font-bold mb-4 tech-heading">INDICADORES</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <MetricCard
            icon="📈"
            label="RSI"
            :value="marketStore.analysisData?.indicadores?.rsi"
            :showProgress="true"
            :progressPercent="getRSIProgress(marketStore.analysisData?.indicadores?.rsi)"
            :progressClass="getRSIProgressClass(marketStore.analysisData?.indicadores?.rsi)"
            format="number"
          />
          <MetricCard
            icon="📊"
            label="EMA8"
            :value="marketStore.analysisData?.indicadores?.ema8"
            format="price"
          />
          <MetricCard
            icon="📊"
            label="EMA21"
            :value="marketStore.analysisData?.indicadores?.ema21"
            format="price"
          />
          <MetricCard
            icon="💰"
            label="Preço"
            :value="marketStore.analysisData?.indicadores?.preco"
            format="price"
          />
        </div>
      </div>

      <!-- Níveis Operacionais - Componente Novo -->
      <OperationalLevels
        v-if="marketStore.analysisData?.niveis_operacionais"
        :entryPrice="marketStore.analysisData.niveis_operacionais.entry_price"
        :stopLoss="marketStore.analysisData.niveis_operacionais.stop_loss"
        :takeProfits="[
          marketStore.analysisData.niveis_operacionais.tp1,
          marketStore.analysisData.niveis_operacionais.tp2,
          marketStore.analysisData.niveis_operacionais.tp3
        ].filter(tp => tp)"
        :riskReward="marketStore.analysisData.niveis_operacionais.rr_ratio"
      />

      <!-- Detalhes Completos (Colapsável) -->
      <div class="card">
        <details class="cursor-pointer">
          <summary class="text-lg font-bold mb-2">Detalhes Completos (JSON)</summary>
          <pre class="text-xs overflow-auto max-h-96 mt-2 p-2 bg-terminal-dark rounded">{{ JSON.stringify(marketStore.analysisData, null, 2) }}</pre>
        </details>
      </div>
    </div>

    <div v-else class="card text-center py-8 text-terminal-green/70">
      Selecione um par e timeframe e clique em "Analisar"
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMarketStore } from '@/stores/market'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import InteractiveChart from '@/components/charts/InteractiveChart.vue'
import SymbolAutocomplete from '@/components/common/SymbolAutocomplete.vue'
import TimeframeSelector from '@/components/common/TimeframeSelector.vue'
import SignalHero from '@/components/analysis/SignalHero.vue'
import ConfluenceGrid from '@/components/analysis/ConfluenceGrid.vue'
import MultiTimeframeTimeline from '@/components/analysis/MultiTimeframeTimeline.vue'
import OperationalLevels from '@/components/analysis/OperationalLevels.vue'
import MetricCard from '@/components/analysis/MetricCard.vue'

const route = useRoute()
const marketStore = useMarketStore()

const selectedSymbol = ref(route.query.symbol || 'BTCUSDT')
const selectedTimeframe = ref(route.query.timeframe || '1h')

const loadAnalysis = async () => {
  try {
    await marketStore.analyze(selectedSymbol.value, selectedTimeframe.value)
  } catch (error) {
    console.error('Erro ao carregar análise:', error)
  }
}

const handleSymbolSelect = (symbol) => {
  // Símbolo selecionado, pode carregar análise automaticamente se desejado
  // Por enquanto, apenas atualiza o valor
  selectedSymbol.value = symbol.symbol
}

const handleTimeframeChange = (timeframe) => {
  // Timeframe alterado, pode carregar análise automaticamente se desejado
  // Por enquanto, apenas atualiza o valor
  selectedTimeframe.value = timeframe
}

const handleSignalAction = (data) => {
  console.log('Ação de sinal clicada:', data)
  // Aqui você pode adicionar lógica para copiar níveis, abrir ordem, etc.
}

const getRiskMessage = (riskLevel) => {
  if (!riskLevel) return null
  
  // Se o riskLevel já contém a mensagem completa (ex: "BAIXO - Pode aumentar posição")
  // Extrair apenas a parte após o hífen
  if (riskLevel.includes(' - ')) {
    const parts = riskLevel.split(' - ')
    if (parts.length > 1) {
      return parts.slice(1).join(' - ') // Retorna tudo após o primeiro " - "
    }
  }
  
  // Se não tem hífen, gerar mensagem baseada no nível
  if (riskLevel.includes('BAIXO')) return 'Pode aumentar posição'
  if (riskLevel.includes('MÉDIO')) return 'Posição moderada recomendada'
  if (riskLevel.includes('ALTO')) return 'Posição reduzida recomendada'
  return null
}

const getSignalType = (recomendacao) => {
  if (!recomendacao) return 'ESPECULATIVO'
  if (recomendacao.includes('LONG')) return 'LONG'
  if (recomendacao.includes('SHORT')) return 'SHORT'
  return 'ESPECULATIVO'
}

const getRSIProgress = (rsi) => {
  if (!rsi || isNaN(rsi)) return 0
  return (rsi / 100) * 100
}

const getRSIProgressClass = (rsi) => {
  if (!rsi || isNaN(rsi)) return 'progress-neutral'
  if (rsi >= 70) return 'progress-low' // Sobrecomprado
  if (rsi <= 30) return 'progress-excellent' // Sobrevendido
  if (rsi >= 50) return 'progress-medium'
  return 'progress-good'
}

onMounted(() => {
  if (route.query.symbol && route.query.timeframe) {
    loadAnalysis()
  }
})
</script>

