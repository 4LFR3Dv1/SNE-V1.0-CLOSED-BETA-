import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const CACHE_KEY = 'sne_radar_dashboard_cache'
const CACHE_TTL = 5 * 60 * 1000 // 5 minutos em milissegundos

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const opportunities = ref([])
  const btcPrice = ref(null)
  const btcChange = ref(null)
  const lastUpdate = ref(null)
  const cacheTimestamp = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isCacheValid = computed(() => {
    if (!cacheTimestamp.value) return false
    const now = Date.now()
    const age = now - cacheTimestamp.value
    return age < CACHE_TTL
  })

  const cacheAge = computed(() => {
    if (!cacheTimestamp.value) return null
    const now = Date.now()
    const age = now - cacheTimestamp.value
    const minutes = Math.floor(age / 60000)
    const seconds = Math.floor((age % 60000) / 1000)
    return { minutes, seconds, total: age }
  })

  // Actions
  const loadFromCache = () => {
    try {
      const cached = localStorage.getItem(CACHE_KEY)
      if (!cached) return false

      const data = JSON.parse(cached)
      
      // Verificar se o cache ainda é válido
      const now = Date.now()
      const age = now - data.timestamp
      
      if (age < CACHE_TTL) {
        opportunities.value = data.opportunities || []
        btcPrice.value = data.btcPrice || null
        btcChange.value = data.btcChange || null
        lastUpdate.value = data.lastUpdate || null
        cacheTimestamp.value = data.timestamp
        
        console.log('✅ Cache carregado:', {
          opportunities: opportunities.value.length,
          age: `${Math.floor(age / 60000)}min ${Math.floor((age % 60000) / 1000)}s`
        })
        return true
      } else {
        console.log('⏰ Cache expirado, removendo...')
        clearCache()
        return false
      }
    } catch (err) {
      console.error('❌ Erro ao carregar cache:', err)
      clearCache()
      return false
    }
  }

  const saveToCache = (opps, btc, change, updateTime) => {
    try {
      const data = {
        opportunities: opps,
        btcPrice: btc,
        btcChange: change,
        lastUpdate: updateTime,
        timestamp: Date.now()
      }
      
      localStorage.setItem(CACHE_KEY, JSON.stringify(data))
      opportunities.value = opps
      btcPrice.value = btc
      btcChange.value = change
      lastUpdate.value = updateTime
      cacheTimestamp.value = data.timestamp
      
      console.log('💾 Cache salvo:', {
        opportunities: opps.length,
        timestamp: new Date(data.timestamp).toLocaleTimeString('pt-BR')
      })
    } catch (err) {
      console.error('❌ Erro ao salvar cache:', err)
    }
  }

  const clearCache = () => {
    try {
      localStorage.removeItem(CACHE_KEY)
      cacheTimestamp.value = null
      console.log('🗑️ Cache limpo')
    } catch (err) {
      console.error('❌ Erro ao limpar cache:', err)
    }
  }

  const updateOpportunities = (opps) => {
    opportunities.value = opps
  }

  const updateBTCPrice = (price, change) => {
    btcPrice.value = price
    btcChange.value = change
  }

  const setLastUpdate = (time) => {
    lastUpdate.value = time
  }

  return {
    // State
    opportunities,
    btcPrice,
    btcChange,
    lastUpdate,
    cacheTimestamp,
    loading,
    error,
    
    // Getters
    isCacheValid,
    cacheAge,
    
    // Actions
    loadFromCache,
    saveToCache,
    clearCache,
    updateOpportunities,
    updateBTCPrice,
    setLastUpdate
  }
})

