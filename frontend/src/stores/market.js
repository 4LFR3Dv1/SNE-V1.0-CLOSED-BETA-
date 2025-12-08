import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useMarketStore = defineStore('market', () => {
  // State
  const currentSymbol = ref('BTCUSDT')
  const currentTimeframe = ref('1h')
  const analysisData = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)

  // Getters
  const signal = computed(() => {
    if (!analysisData.value) return 'NEUTRAL'
    
    // Prioridade 1: Sintese (mais confiável)
    const sintese = analysisData.value?.sintese
    if (sintese?.acao) {
      const acao = sintese.acao.toUpperCase()
      if (acao.includes('LONG') || acao.includes('BUY') || acao.includes('🟢')) return 'BUY'
      if (acao.includes('SHORT') || acao.includes('SELL') || acao.includes('🔴')) return 'SELL'
    }
    
    // Prioridade 2: Recomendação da síntese
    if (sintese?.recomendacao) {
      const rec = sintese.recomendacao.toUpperCase()
      if (rec.includes('BUY') || rec.includes('LONG') || rec.includes('COMPRAR')) return 'BUY'
      if (rec.includes('SELL') || rec.includes('SHORT') || rec.includes('VENDER')) return 'SELL'
    }
    
    // Prioridade 3: Sinal completo
    const sinal_completo = analysisData.value?.indicadores?.sinal_completo
    if (sinal_completo?.recomendacao) {
      const rec = sinal_completo.recomendacao.toUpperCase()
      if (rec.includes('BUY') || rec.includes('LONG')) return 'BUY'
      if (rec.includes('SELL') || rec.includes('SHORT')) return 'SELL'
    }
    
    // Prioridade 4: Multi-Timeframe
    const mtf = analysisData.value?.mtf?.confluencia
    if (mtf?.direcao) {
      if (mtf.direcao === 'ALTA') return 'BUY'
      if (mtf.direcao === 'BAIXA') return 'SELL'
    }
    
    return analysisData.value.signal || 'NEUTRAL'
  })

  const score = computed(() => {
    if (!analysisData.value) return 0
    
    // Prioridade 1: Confluência (mais confiável)
    const confluencia = analysisData.value.confluencia
    if (confluencia?.score !== undefined && confluencia.score !== null) {
      return parseFloat(confluencia.score) || 0
    }
    
    // Prioridade 2: Score combinado da síntese
    const sintese = analysisData.value?.sintese
    if (sintese?.score_combinado !== undefined && sintese.score_combinado !== null) {
      return parseFloat(sintese.score_combinado) || 0
    }
    
    // Prioridade 3: Score de confiança
    if (sintese?.score_confianca !== undefined && sintese.score_confianca !== null) {
      return parseFloat(sintese.score_confianca) || 0
    }
    
    // Prioridade 4: Confluência avançada
    const confluencia_avancada = analysisData.value?.indicadores?.confluencia_avancada
    if (confluencia_avancada?.confluencia_score !== undefined) {
      return parseFloat(confluencia_avancada.confluencia_score) || 0
    }
    
    return parseFloat(analysisData.value.confluence_score || analysisData.value.score || 0) || 0
  })

  const isBullish = computed(() => signal.value === 'BUY')
  const isBearish = computed(() => signal.value === 'SELL')

  // Actions
  const analyze = async (symbol, timeframe) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await api.analyze(symbol, timeframe)
      analysisData.value = data
      currentSymbol.value = symbol
      currentTimeframe.value = timeframe
      lastUpdate.value = new Date()
      return data
    } catch (err) {
      console.error(`❌ [STORE] Erro ao buscar análise:`, err)
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSignal = async (symbol, timeframe) => {
    try {
      const data = await api.getSignal(symbol, timeframe)
      return data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const reset = () => {
    analysisData.value = null
    error.value = null
    loading.value = false
  }

  return {
    // State
    currentSymbol,
    currentTimeframe,
    analysisData,
    loading,
    error,
    lastUpdate,
    
    // Getters
    signal,
    score,
    isBullish,
    isBearish,
    
    // Actions
    analyze,
    getSignal,
    reset
  }
})

