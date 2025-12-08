<template>
  <div class="simple-chart-container">
    <div class="chart-header">
      <h3 class="text-lg font-bold">{{ symbol }} - {{ timeframe }}</h3>
      <button 
        @click="refreshChart" 
        class="px-3 py-1 rounded text-sm bg-terminal-green text-black hover:opacity-80"
        :disabled="loading"
      >
        {{ loading ? 'Carregando...' : 'Atualizar' }}
      </button>
    </div>
    
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-terminal-green">Carregando gráfico...</div>
    </div>
    
    <div v-else-if="error" class="flex flex-col items-center justify-center h-96">
      <div class="text-red-500 mb-4">Erro: {{ error }}</div>
      <button 
        @click="refreshChart" 
        class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80"
      >
        Tentar Novamente
      </button>
    </div>
    
    <div v-else class="chart-image-container">
      <img 
        v-if="chartImageUrl"
        :src="chartImageUrl" 
        :alt="`Gráfico ${symbol} ${timeframe}`"
        class="chart-image"
        @error="handleImageError"
        @load="handleImageLoad"
        crossorigin="anonymous"
        referrerpolicy="no-referrer"
      />
      <div v-else class="text-terminal-green">Aguardando URL do gráfico...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import api from '../../services/api'

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  },
  timeframe: {
    type: String,
    default: '1h'
  }
})

const loading = ref(false)
const error = ref(null)
const chartImageUrl = ref('')

// URL do gráfico com cache busting
// IMPORTANTE: Em desenvolvimento, acessar Flask diretamente para evitar problemas de proxy do Vite
const getChartUrl = () => {
  const timestamp = new Date().getTime()
  
  // Detectar se está em desenvolvimento (Vite dev server)
  const isDev = import.meta.env.DEV
  
  // Em dev: acessar Flask diretamente (evita problemas de proxy com imagens)
  // Em prod: usar URL relativa (servido pelo mesmo servidor Flask)
  const baseUrl = isDev ? 'http://localhost:9999' : ''
  const url = `${baseUrl}/api/v1/chart-image?symbol=${props.symbol}&interval=${props.timeframe}&t=${timestamp}`
  console.log('📊 Carregando gráfico da URL:', url)
  console.log('   Ambiente:', isDev ? 'Desenvolvimento (Flask direto)' : 'Produção (mesmo servidor)')
  return url
}

// Carregar gráfico
const loadChart = async () => {
  loading.value = true
  error.value = null
  
  try {
    const url = getChartUrl()
    console.log('🔍 Carregando gráfico da URL:', url)
    
    // Carregar imagem via fetch e criar blob URL (evita problemas de CORS/proxy)
    const response = await fetch(url, {
      method: 'GET',
      mode: 'cors',
      credentials: 'omit',
      cache: 'no-cache'
    })
    
    console.log('   Status:', response.status, response.statusText)
    console.log('   Content-Type:', response.headers.get('content-type'))
    
    if (!response.ok) {
      const text = await response.text()
      console.error('   Resposta de erro:', text.substring(0, 300))
      
      if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
        error.value = 'Servidor retornou HTML. Verifique se o Flask está rodando na porta 9999.'
      } else {
        error.value = `Erro ${response.status}: ${response.statusText}`
      }
      loading.value = false
      return
    }
    
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('image')) {
      const text = await response.text()
      console.error('   Resposta não é uma imagem:', text.substring(0, 200))
      error.value = `Servidor não retornou uma imagem (Content-Type: ${contentType}). Verifique se o endpoint está funcionando.`
      loading.value = false
      return
    }
    
    // Converter resposta para blob e criar URL de objeto
    // Limpar blob URL anterior se existir (evitar memory leak)
    if (chartImageUrl.value && chartImageUrl.value.startsWith('blob:')) {
      URL.revokeObjectURL(chartImageUrl.value)
    }
    
    const blob = await response.blob()
    const blobUrl = URL.createObjectURL(blob)
    
    console.log('✅ Imagem carregada, criando blob URL...')
    chartImageUrl.value = blobUrl
    loading.value = false  // Imagem já foi carregada no blob
  } catch (err) {
    error.value = err.message || 'Erro ao carregar gráfico'
    console.error('❌ Erro ao carregar gráfico:', err)
    loading.value = false
  }
}

// Atualizar gráfico
const refreshChart = () => {
  loadChart()
}

// Handlers de imagem
const handleImageError = async (e) => {
  console.error('❌ Erro ao carregar imagem do gráfico:', e)
  console.error('   URL tentada:', chartImageUrl.value)
  
  // Tentar verificar se é um erro de rede ou de servidor
  try {
    // Usar fetch com credentials e headers apropriados
    const response = await fetch(chartImageUrl.value, {
      method: 'GET',
      mode: 'cors',
      credentials: 'omit', // Não enviar cookies para evitar problemas
      cache: 'no-cache'
    })
    
    console.log('   Status da resposta:', response.status, response.statusText)
    console.log('   Content-Type:', response.headers.get('content-type'))
    
    if (!response.ok) {
      const text = await response.text()
      console.error('   Resposta do servidor (primeiros 500 chars):', text.substring(0, 500))
      
      // Verificar se é HTML (provavelmente página de erro ou login)
      if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
        error.value = 'Servidor retornou HTML em vez de imagem. Verifique se o Flask está rodando na porta 9999 e se o endpoint está acessível.'
      } else {
        error.value = `Erro ${response.status}: ${response.statusText}`
      }
    } else {
      // Se a resposta está OK mas a imagem não carrega, pode ser formato inválido
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('image')) {
        const text = await response.text()
        console.error('   Resposta não é uma imagem:', text.substring(0, 200))
        error.value = 'Servidor não retornou uma imagem válida. Verifique se o endpoint está funcionando corretamente.'
      } else {
        error.value = 'Erro desconhecido ao carregar imagem'
      }
    }
  } catch (err) {
    console.error('   Erro de rede:', err)
    if (err.message.includes('CORS') || err.message.includes('fetch')) {
      error.value = 'Erro de CORS. Verifique se o Flask está rodando e se os headers CORS estão configurados.'
    } else {
      error.value = 'Erro ao conectar com o servidor. Verifique se o Flask está rodando na porta 9999.'
    }
  }
  
  loading.value = false
}

const handleImageLoad = () => {
  console.log('✅ Imagem do gráfico carregada com sucesso')
  error.value = null
  loading.value = false
}

// Limpar blob URLs quando componente for desmontado (evitar memory leak)
onUnmounted(() => {
  if (chartImageUrl.value && chartImageUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(chartImageUrl.value)
  }
})

// Watch props para recarregar quando mudarem
watch([() => props.symbol, () => props.timeframe], () => {
  loadChart()
})

// Carregar ao montar
onMounted(() => {
  loadChart()
})
</script>

<style scoped>
.simple-chart-container {
  @apply w-full bg-terminal-dark rounded-lg p-4;
}

.chart-header {
  @apply flex justify-between items-center mb-4;
}

.chart-image-container {
  @apply w-full bg-terminal-gray rounded border border-terminal-green/30 overflow-hidden;
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-image {
  width: 100%;
  height: auto;
  display: block;
  max-width: 100%;
}
</style>

