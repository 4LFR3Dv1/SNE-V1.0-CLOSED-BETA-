<template>
  <div class="trading-chart-container">
    <div class="chart-header">
      <h3 class="text-lg font-bold">{{ symbol }} - {{ timeframe }}</h3>
      <div class="chart-controls">
        <button 
          v-for="indicator in availableIndicators" 
          :key="indicator.key"
          @click="toggleIndicator(indicator.key)"
          :class="[
            'px-3 py-1 rounded text-sm',
            activeIndicators[indicator.key] 
              ? 'bg-terminal-green text-black' 
              : 'bg-terminal-dark text-terminal-green border border-terminal-green/30'
          ]"
        >
          {{ indicator.label }}
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-terminal-green">Carregando gráfico...</div>
    </div>
    
    <div v-else-if="error" class="flex items-center justify-center h-96">
      <div class="text-red-500">Erro: {{ error }}</div>
    </div>
    
    <div v-else class="w-full" style="height: 500px; min-height: 500px; position: relative; overflow: visible;">
      <div 
        ref="chartContainer" 
        class="chart-container" 
        style="width: 100%; height: 100%; min-height: 500px; background: #131722; display: block; visibility: visible; opacity: 1; position: relative; z-index: 1; overflow: visible;"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { createChart, ColorType } from 'lightweight-charts'
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

const chartContainer = ref(null)
const loading = ref(false)
const error = ref(null)

let chart = null
let candleSeries = null
let volumeSeries = null
let ema8Series = null
let ema21Series = null

const activeIndicators = ref({
  ema8: true,
  ema21: true
})

const availableIndicators = [
  { key: 'ema8', label: 'EMA 8' },
  { key: 'ema21', label: 'EMA 21' }
]

// Inicializar gráfico
const initChart = async () => {
  const container = chartContainer.value
  if (!container) {
    console.warn('⚠️ Container do gráfico não encontrado')
    return
  }
  
  // ✅ RESET TOTAL: Limpar completamente antes de criar novo gráfico
  if (chart) {
    try {
      chart.remove()
      console.log('🧹 Gráfico anterior removido')
    } catch (e) {
      console.warn('⚠️ Erro ao remover gráfico anterior:', e)
    }
    chart = null
    candleSeries = null
    volumeSeries = null
    ema8Series = null
    ema21Series = null
  }
  
  // ✅ Limpar container completamente (forçar limpeza de lixo anterior)
  if (container) {
    container.innerHTML = '' // Limpa qualquer HTML residual
    console.log('🧹 Container limpo completamente')
  }
  
  // FORÇAR dimensões do container
  container.style.width = '100%'
  container.style.height = '500px'
  container.style.minHeight = '500px'
  container.style.display = 'block'
  container.style.visibility = 'visible'
  container.style.opacity = '1'
  container.style.position = 'relative'
  container.style.backgroundColor = '#131722'
  
  // Aguardar browser aplicar estilos
  await new Promise(resolve => requestAnimationFrame(resolve))
  
  // Verificar dimensões após aplicar estilos
  const containerWidth = container.clientWidth || container.offsetWidth || 800
  const containerHeight = container.clientHeight || container.offsetHeight || 500
  
  console.log('📊 Container dimensões:', {
    width: containerWidth,
    height: containerHeight,
    offsetWidth: container.offsetWidth,
    offsetHeight: container.offsetHeight,
    clientWidth: container.clientWidth,
    clientHeight: container.clientHeight
  })
  
  if (containerHeight <= 0 || containerWidth <= 0) {
    console.error('❌ Container sem dimensões válidas após forçar estilos')
    // Tentar mais uma vez com valores absolutos
    container.style.height = '500px'
    container.style.width = '800px'
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  
  console.log('📊 Inicializando gráfico com dimensões finais:', containerWidth, 'x', containerHeight)
  
  // Criar gráfico com dimensões explícitas
  chart = createChart(container, {
    width: containerWidth,  // ✅ Width explícito
    height: containerHeight, // ✅ Height explícito
    layout: {
      background: { type: ColorType.Solid, color: '#131722' }, // ✅ Fundo sólido para garantir visibilidade
      textColor: '#d1d4dc'
    },
    grid: {
      vertLines: { color: '#333333', visible: true, style: 0 },
      horzLines: { color: '#333333', visible: true, style: 0 }
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
      borderColor: '#333333',
      rightOffset: 12, // ✅ Aumentado para melhor visualização
      barSpacing: 3, // ✅ Aumentado para melhor legibilidade
      fixLeftEdge: true, // ✅ Evita scroll acidental para o passado
      lockVisibleTimeRangeOnResize: true, // ✅ Mantém range ao redimensionar
      rightBarStaysOnScroll: true // ✅ Mantém última barra visível
    },
    rightPriceScale: {
      borderColor: '#333333',
      visible: true,
      autoScale: true,
      scaleMargins: {
        top: 0.1,
        bottom: 0.1
      }
    },
    leftPriceScale: {
      visible: false
    }
  })
  
  // Série de candlesticks
  candleSeries = chart.addCandlestickSeries({
    upColor: '#26a69a',      // ✅ Verde mais visível (igual ao exemplo que funciona)
    downColor: '#ef5350',    // ✅ Vermelho mais visível
    borderUpColor: '#26a69a',
    borderDownColor: '#ef5350',
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
    priceFormat: {
      type: 'price',
      precision: 4, // ✅ Aumentar precisão para valores pequenos (0.3876)
      minMove: 0.0001
    }
  })
  
  // Série de volume
  volumeSeries = chart.addHistogramSeries({
    color: 'rgba(255,215,0,0.6)',
    priceFormat: { type: 'volume' },
    priceScaleId: 'volume',
    scaleMargins: {
      top: 0.8,
      bottom: 0
    }
  })
  
  chart.priceScale('volume').applyOptions({
    scaleMargins: { top: 0.8, bottom: 0 }
  })
  
  // EMAs
  ema8Series = chart.addLineSeries({
    color: '#00ffff',
    lineWidth: 2,
    title: 'EMA 8',
    priceLineVisible: false,
    lastValueVisible: true
  })
  
  ema21Series = chart.addLineSeries({
    color: '#ff8c00',
    lineWidth: 2,
    title: 'EMA 21',
    priceLineVisible: false,
    lastValueVisible: true
  })
  
  console.log('✅ Gráfico inicializado')
  
  // 🧪 TESTE: Verificar se o HTML foi injetado no container
  setTimeout(() => {
    if (container) {
      console.log('📋 HTML Interno do Container:', container.innerHTML.substring(0, 200))
      const hasCanvas = container.querySelector('canvas')
      const hasTable = container.querySelector('table')
      console.log('📋 Canvas existe?', !!hasCanvas)
      console.log('📋 Table existe?', !!hasTable)
      if (hasCanvas) {
        const canvas = hasCanvas
        console.log('📋 Canvas dimensões:', {
          width: canvas.width,
          height: canvas.height,
          offsetWidth: canvas.offsetWidth,
          offsetHeight: canvas.offsetHeight,
          style: window.getComputedStyle(canvas).cssText.substring(0, 100)
        })
      }
    }
  }, 100)
}

// Carregar dados usando endpoint consolidado
const loadChartData = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('📊 Carregando dados consolidados para:', props.symbol, props.timeframe)
    
    // Usar endpoint consolidado
    const chartDataResponse = await api.getChartData(props.symbol, props.timeframe, 500)
    console.log('📊 Resposta chart-data:', chartDataResponse)
    
    // Verificar resposta
    if (typeof chartDataResponse === 'string' && chartDataResponse.includes('<!DOCTYPE')) {
      throw new Error('API retornou HTML - Flask não está rodando')
    }
    
    if (!chartDataResponse || !chartDataResponse.success || !chartDataResponse.candles) {
      throw new Error('Resposta inválida do servidor')
    }
    
    // Processar candles - CORREÇÃO CRÍTICA: Converter milissegundos para segundos
    const candlesData = chartDataResponse.candles
      .map(c => {
        // ⚠️ CORREÇÃO MÁGICA: Se timestamp tem 13 dígitos (milissegundos), dividir por 1000
        let timestamp = c.time
        if (timestamp > 2000000000) {
          // Timestamp em milissegundos (13 dígitos) - converter para segundos
          timestamp = Math.floor(timestamp / 1000)
          console.log('🔄 Timestamp convertido de ms para segundos:', c.time, '→', timestamp)
        }
        
        // ✅ Processar valores SEM usar || 0 (que mascara valores inválidos)
        const open = parseFloat(c.open)
        const high = parseFloat(c.high)
        const low = parseFloat(c.low)
        const close = parseFloat(c.close)
        
        return {
          time: timestamp, // Agora garantidamente em segundos (10 dígitos)
          open,
          high,
          low,
          close
        }
      })
      .filter(c => {
        // ✅ FILTRO DE SEGURANÇA AGRESSIVO: Remover candles com valores inválidos
        // Isso previne que valores 0, null, NaN ou Infinity "zoem" a escala de preço
        const isValid = c.time > 0 && 
                       !isNaN(c.time) && isFinite(c.time) &&
                       c.open > 0 && !isNaN(c.open) && isFinite(c.open) &&
                       c.high > 0 && !isNaN(c.high) && isFinite(c.high) &&
                       c.low > 0 && !isNaN(c.low) && isFinite(c.low) &&
                       c.close > 0 && !isNaN(c.close) && isFinite(c.close) &&
                       c.high >= c.low &&
                       c.high >= c.open &&
                       c.high >= c.close &&
                       c.low <= c.open &&
                       c.low <= c.close
        
        if (!isValid) {
          console.warn('⚠️ Candle inválido ignorado (valor 0, NaN ou Infinity):', {
            time: c.time,
            open: c.open,
            high: c.high,
            low: c.low,
            close: c.close,
            original: c
          })
        }
        return isValid
      })
      .sort((a, b) => a.time - b.time) // Ordenar por tempo (crescente)
    
    // Processar volumes - mesma correção de timestamp
    const volumesData = chartDataResponse.candles.map(c => {
      let timestamp = c.time
      if (timestamp > 2000000000) {
        timestamp = Math.floor(timestamp / 1000)
      }
      
      return {
        time: timestamp,
        value: parseFloat(c.volume) || 0,
        color: c.close >= c.open ? 'rgba(38, 166, 154, 0.6)' : 'rgba(239, 83, 80, 0.6)'
      }
    })
    
    // Log para debug
    if (candlesData.length > 0) {
      const firstCandle = candlesData[0]
      const lastCandle = candlesData[candlesData.length - 1]
      
      console.log('📊 Primeiro candle processado:', {
        time: firstCandle.time,
        timeOriginal: chartDataResponse.candles[0].time,
        isSeconds: firstCandle.time < 2000000000,
        date: new Date(firstCandle.time * 1000).toISOString(),
        open: firstCandle.open,
        high: firstCandle.high,
        low: firstCandle.low,
        close: firstCandle.close
      })
      
      console.log('📊 Último candle processado:', {
        time: lastCandle.time,
        date: new Date(lastCandle.time * 1000).toISOString(),
        open: lastCandle.open,
        high: lastCandle.high,
        low: lastCandle.low,
        close: lastCandle.close
      })
      
      console.log('📊 Span de tempo:', {
        from: new Date(firstCandle.time * 1000).toISOString(),
        to: new Date(lastCandle.time * 1000).toISOString(),
        days: ((lastCandle.time - firstCandle.time) / 86400).toFixed(1)
      })
    }
    
    console.log('📊 Dados processados:', {
      candles: candlesData.length,
      volumes: volumesData.length,
      firstTime: candlesData[0]?.time,
      lastTime: candlesData[candlesData.length - 1]?.time
    })
    
    if (candlesData.length === 0) {
      throw new Error('Nenhum dado válido para exibir')
    }
    
    // Adicionar dados ao gráfico
    if (chart && candleSeries && volumeSeries) {
      console.log('📊 Preparando para adicionar dados:', {
        chartExists: !!chart,
        candleSeriesExists: !!candleSeries,
        volumeSeriesExists: !!volumeSeries,
        candlesCount: candlesData.length,
        firstCandle: candlesData[0],
        lastCandle: candlesData[candlesData.length - 1]
      })
      
      // 1. Verificar valores de preço dos candles
      const minPrice = Math.min(...candlesData.map(c => c.low))
      const maxPrice = Math.max(...candlesData.map(c => c.high))
      console.log('💰 Valores de preço dos candles:', {
        minPrice,
        maxPrice,
        range: maxPrice - minPrice,
        firstClose: candlesData[0]?.close,
        lastClose: candlesData[candlesData.length - 1]?.close
      })
      
      // 2. Adicionar dados principais primeiro
      try {
        console.log('📊 Antes de setData - Primeiros 3 candles:', candlesData.slice(0, 3))
        console.log('📊 Últimos 3 candles:', candlesData.slice(-3))
        
        // ✅ Adicionar dados
        candleSeries.setData(candlesData)
        volumeSeries.setData(volumesData)
        
        // ✅ TESTE: Verificar se a série realmente tem os dados
        console.log('🧪 TESTE: Série de candles após setData:', {
          seriesExists: !!candleSeries,
          chartExists: !!chart,
          dataLength: candlesData.length
        })
        
        console.log('✅ Dados principais adicionados:', {
          candles: candlesData.length,
          volumes: volumesData.length,
          firstTime: candlesData[0]?.time,
          lastTime: candlesData[candlesData.length - 1]?.time,
          firstCandle: candlesData[0],
          lastCandle: candlesData[candlesData.length - 1]
        })
        
        // 3. ✅ Forçar escala de preço ANTES de fitContent
        const priceScale = chart.priceScale('right')
        priceScale.applyOptions({
          autoScale: true,
          scaleMargins: {
            top: 0.2, // ✅ Aumentar margem para garantir que candles sejam visíveis
            bottom: 0.2
          }
        })
        
        // 4. ✅ fitContent() IMEDIATAMENTE após setData (sem delays)
        chart.timeScale().fitContent()
        console.log('✅ fitContent() chamado imediatamente')
        
        
        // 4. Garantir que escala de preço está configurada corretamente
        setTimeout(() => {
          if (chart && candleSeries) {
            try {
              const priceScale = chart.priceScale('right')
              
              // Forçar autoScale e margens adequadas
              priceScale.applyOptions({
                autoScale: true,
                scaleMargins: {
                  top: 0.1,
                  bottom: 0.1
                }
              })
              
              console.log('✅ Escala de preço configurada:', {
                autoScale: true,
                priceRange: { min: minPrice, max: maxPrice },
                candleCount: candlesData.length
              })
              
              // Forçar fitContent novamente para garantir que tudo está ajustado
              requestAnimationFrame(() => {
                chart.timeScale().fitContent()
              })
              
            } catch (e) {
              console.error('❌ Erro ao configurar escala de preço:', e)
            }
          }
        }, 300)
        
        // 5. Forçar viewport manualmente se necessário
        const firstCandleTime = candlesData[0]?.time
        const lastCandleTime = candlesData[candlesData.length - 1]?.time
        
        if (firstCandleTime && lastCandleTime) {
          // Aguardar um pouco e forçar o range visível manualmente
          setTimeout(() => {
            if (chart) {
              try {
                // Tentar setVisibleRange manualmente
                chart.timeScale().setVisibleRange({
                  from: firstCandleTime - 3600, // 1 hora antes do primeiro candle
                  to: lastCandleTime + 3600     // 1 hora depois do último candle
                })
                console.log('✅ Viewport forçado manualmente:', {
                  from: firstCandleTime - 3600,
                  to: lastCandleTime + 3600,
                  fromDate: new Date((firstCandleTime - 3600) * 1000).toISOString(),
                  toDate: new Date((lastCandleTime + 3600) * 1000).toISOString()
                })
              } catch (e) {
                console.warn('⚠️ Erro ao forçar viewport manual, usando fitContent:', e)
                chart.timeScale().fitContent()
              }
              
              // Verificar range visível após ajuste
              const visibleRange = chart.timeScale().getVisibleRange()
              console.log('📊 Range visível após ajuste manual:', visibleRange)
              console.log('📊 Primeiro candle time:', firstCandleTime, new Date(firstCandleTime * 1000).toISOString())
              console.log('📊 Último candle time:', lastCandleTime, new Date(lastCandleTime * 1000).toISOString())
              
              if (visibleRange) {
                const rangeContainsData = visibleRange.from <= firstCandleTime && visibleRange.to >= lastCandleTime
                console.log('📊 Range contém os dados?', rangeContainsData)
                
                if (!rangeContainsData) {
                  console.warn('⚠️ Range ainda não contém os dados! Tentando fitContent novamente...')
                  chart.timeScale().fitContent()
                }
              }
            }
          }, 400)
        }
        
      } catch (e) {
        console.error('❌ Erro ao adicionar dados ao gráfico:', e)
        throw e
      }
      
      // 3. Adicionar indicadores - CORREÇÃO: Converter timestamps também
      if (chartDataResponse.indicators) {
        const indicators = chartDataResponse.indicators
        
        if (indicators.ema8 && indicators.ema8.length > 0 && ema8Series) {
          const ema8Data = indicators.ema8.map(item => ({
            time: item.time > 2000000000 ? Math.floor(item.time / 1000) : item.time,
            value: parseFloat(item.value) || 0
          }))
          ema8Series.setData(ema8Data)
          ema8Series.applyOptions({ visible: activeIndicators.value.ema8 })
        }
        
        if (indicators.ema21 && indicators.ema21.length > 0 && ema21Series) {
          const ema21Data = indicators.ema21.map(item => ({
            time: item.time > 2000000000 ? Math.floor(item.time / 1000) : item.time,
            value: parseFloat(item.value) || 0
          }))
          ema21Series.setData(ema21Data)
          ema21Series.applyOptions({ visible: activeIndicators.value.ema21 })
        }
      }
      
      // 4. Adicionar níveis operacionais
      if (chartDataResponse.levels && chartDataResponse.levels.operational) {
        const op = chartDataResponse.levels.operational
        
        if (op.entry && op.entry > 0) {
          candleSeries.createPriceLine({
            price: op.entry,
            color: '#ffffff',
            lineWidth: 2,
            lineStyle: 0,
            axisLabelVisible: true,
            title: 'Entry'
          })
        }
        
        if (op.stop_loss && op.stop_loss > 0) {
          candleSeries.createPriceLine({
            price: op.stop_loss,
            color: '#ef5350',
            lineWidth: 2,
            lineStyle: 0,
            axisLabelVisible: true,
            title: 'Stop Loss'
          })
        }
        
        if (op.take_profit && Array.isArray(op.take_profit)) {
          op.take_profit.forEach((tp, index) => {
            if (tp && tp > 0) {
              candleSeries.createPriceLine({
                price: tp,
                color: '#26a69a',
                lineWidth: 1.5,
                lineStyle: 1,
                axisLabelVisible: true,
                title: `TP${index + 1}`
              })
            }
          })
        }
      }
      
      // 5. Adicionar suportes e resistências
      if (chartDataResponse.levels) {
        const levels = chartDataResponse.levels
        
        if (levels.supports && Array.isArray(levels.supports)) {
          levels.supports.forEach((sup, index) => {
            if (sup && sup > 0) {
              candleSeries.createPriceLine({
                price: sup,
                color: '#26a69a',
                lineWidth: 1,
                lineStyle: 2,
                axisLabelVisible: true,
                title: `S${index + 1}`
              })
            }
          })
        }
        
        if (levels.resistances && Array.isArray(levels.resistances)) {
          levels.resistances.forEach((res, index) => {
            if (res && res > 0) {
              candleSeries.createPriceLine({
                price: res,
                color: '#ef5350',
                lineWidth: 1,
                lineStyle: 2,
                axisLabelVisible: true,
                title: `R${index + 1}`
              })
            }
          })
        }
      }
      
      console.log('✅ Todos os dados adicionados ao gráfico com sucesso')
    } else {
      console.warn('⚠️ Gráfico não inicializado ainda:', {
        chart: !!chart,
        candleSeries: !!candleSeries,
        volumeSeries: !!volumeSeries
      })
    }
    
  } catch (err) {
    error.value = err.message || 'Erro ao carregar dados do gráfico'
    console.error('❌ Erro ao carregar gráfico:', err)
  } finally {
    loading.value = false
  }
}

// Toggle indicador
const toggleIndicator = (key) => {
  activeIndicators.value[key] = !activeIndicators.value[key]
  
  if (key === 'ema8' && ema8Series) {
    ema8Series.applyOptions({ visible: activeIndicators.value.ema8 })
  } else if (key === 'ema21' && ema21Series) {
    ema21Series.applyOptions({ visible: activeIndicators.value.ema21 })
  }
}

// Resize handler
const handleResize = () => {
  if (chart && chartContainer.value) {
    const width = chartContainer.value.clientWidth || 800
    const height = chartContainer.value.clientHeight || 500
    chart.resize(width, height)
  }
}

// Watch props
watch([() => props.symbol, () => props.timeframe], async () => {
  if (!chart) {
    await nextTick()
    setTimeout(async () => {
      await initChart()
      setTimeout(() => {
        if (chart && candleSeries && volumeSeries) {
          loadChartData()
        }
      }, 200)
    }, 100)
  } else {
    loadChartData()
  }
}, { immediate: false })

// Lifecycle
onMounted(async () => {
  await nextTick()
  
  setTimeout(async () => {
    const container = chartContainer.value
    if (!container) {
      console.error('❌ Container do gráfico não encontrado')
      return
    }
    
    // FORÇAR dimensões antes de inicializar (sempre)
    container.style.width = '100%'
    container.style.height = '500px'
    container.style.minHeight = '500px'
    container.style.display = 'block'
    container.style.visibility = 'visible'
    container.style.opacity = '1'
    container.style.position = 'relative'
    container.style.backgroundColor = '#131722'
    
    console.log('📊 Container preparado:', {
      width: container.offsetWidth,
      height: container.offsetHeight,
      style: container.style.cssText
    })
    
    // Aguardar browser aplicar estilos
    await new Promise(resolve => requestAnimationFrame(resolve))
    await new Promise(resolve => setTimeout(resolve, 50))
    
    await initChart()
    
    setTimeout(() => {
      if (chart && candleSeries && volumeSeries) {
        console.log('✅ Gráfico pronto, carregando dados...')
        loadChartData()
      } else {
        console.warn('⚠️ Aguardando gráfico inicializar...')
        setTimeout(() => {
          if (chart && candleSeries && volumeSeries) {
            loadChartData()
          } else {
            error.value = 'Erro ao inicializar gráfico - séries não criadas'
            console.error('❌ Gráfico não inicializado corretamente')
          }
        }, 300)
      }
    }, 150)
  }, 100)
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  
  // ✅ LIMPEZA BRUTAL: Remover completamente o gráfico e limpar HTML
  if (chart) {
    try {
      chart.remove()
      chart = null
      candleSeries = null
      volumeSeries = null
      ema8Series = null
      ema21Series = null
      console.log('🧹 Gráfico removido no onUnmounted')
    } catch (e) {
      console.warn('⚠️ Erro ao remover gráfico no onUnmounted:', e)
    }
  }
  
  // Forçar limpeza do HTML do container
  if (chartContainer.value) {
    chartContainer.value.innerHTML = ''
    console.log('🧹 Container HTML limpo no onUnmounted')
  }
})
</script>

<style scoped>
.trading-chart-container {
  @apply w-full bg-terminal-dark rounded-lg p-4;
}

.chart-header {
  @apply flex justify-between items-center mb-4;
}

.chart-controls {
  @apply flex gap-2 flex-wrap;
}

.chart-container {
  width: 100% !important;
  height: 500px !important;
  min-height: 500px !important;
  background-color: #131722 !important;
  position: relative !important;
  overflow: visible !important;
  z-index: 1;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.chart-container :deep(.tv-lightweight-charts) {
  width: 100% !important;
  height: 100% !important;
  min-height: 500px !important;
  position: relative !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  background-color: #131722 !important;
}

/* FORÇAR A VISIBILIDADE DO CANVAS - Z-INDEX E POSIÇÃO */
.chart-container :deep(table) {
  height: 100% !important;
  width: 100% !important;
  position: relative !important;
  z-index: 5 !important;
}

.chart-container :deep(canvas) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  position: absolute !important;
  z-index: 10 !important; /* ✅ Força ficar acima de backgrounds */
  top: 0 !important;
  left: 0 !important;
  pointer-events: auto !important;
  width: 100% !important;
  height: 100% !important;
}

/* Garantir que o container pai não esconda o gráfico */
.chart-container {
  position: relative !important;
  z-index: 1 !important;
  overflow: visible !important; /* ✅ Não cortar o gráfico */
}
</style>

