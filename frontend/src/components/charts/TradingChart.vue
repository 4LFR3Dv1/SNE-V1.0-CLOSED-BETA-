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
    
    <div v-else>
      <div 
        ref="chartContainer" 
        class="chart-container" 
        style="width: 100%; height: 500px; min-height: 500px; background: #0a0a0a; display: block; visibility: visible; opacity: 1; position: relative;"
      ></div>
      <!-- Debug: Verificar se canvas existe -->
      <div v-if="false" class="text-xs text-gray-500 mt-2">
        Canvas: {{ chartContainer?.querySelector('canvas') ? 'Sim' : 'Não' }}
      </div>
      
      <!-- Indicadores em subplots -->
      <div v-if="showRSI" ref="rsiContainer" class="indicator-container"></div>
      <div v-if="showMACD" ref="macdContainer" class="indicator-container"></div>
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
  },
  analysisData: {
    type: Object,
    default: null
  }
})

const chartContainer = ref(null)
const rsiContainer = ref(null)
const macdContainer = ref(null)

// Backup do container para evitar perda de referência durante re-renderizações
let containerBackup = null

const loading = ref(false)
const error = ref(null)
const candles = ref([])
const levels = ref(null)

let chart = null
let candleSeries = null
let volumeSeries = null
let ema8Series = null
let ema21Series = null
let rsiChart = null
let macdChart = null

// Função helper para obter o container (com fallback para backup)
const getContainer = () => {
  if (chartContainer.value) {
    containerBackup = chartContainer.value
    return chartContainer.value
  }
  if (containerBackup) {
    return containerBackup
  }
  // Última tentativa: buscar no DOM
  const domContainer = document.querySelector('.chart-container')
  if (domContainer) {
    containerBackup = domContainer
    chartContainer.value = domContainer
    return domContainer
  }
  return null
}

const activeIndicators = ref({
  ema8: true,
  ema21: true,
  rsi: false,
  macd: false
})

const availableIndicators = [
  { key: 'ema8', label: 'EMA 8' },
  { key: 'ema21', label: 'EMA 21' },
  { key: 'rsi', label: 'RSI' },
  { key: 'macd', label: 'MACD' }
]

const showRSI = ref(false)
const showMACD = ref(false)

// Inicializar gráfico
const initChart = async () => {
  const container = getContainer()
  if (!container) {
    console.warn('⚠️ Container do gráfico não encontrado')
    return
  }
  
  // Atualizar ref se necessário
  if (!chartContainer.value) {
    chartContainer.value = container
  }

  // Limpar gráfico anterior se existir
  if (chart) {
    try {
      chart.remove()
    } catch (e) {
      console.warn('⚠️ Erro ao remover gráfico anterior:', e)
    }
    chart = null
    candleSeries = null
    volumeSeries = null
    ema8Series = null
    ema21Series = null
  }
  
  // Limpar container antes de criar novo gráfico
  if (container) {
    container.innerHTML = ''
  }

  // Garantir que o container tenha altura definida (width será calculado automaticamente)
  // O Lightweight Charts funciona melhor quando você especifica apenas height
  if (container.clientHeight <= 0 && container.offsetHeight <= 0) {
    console.warn('⚠️ Container sem altura, forçando altura...')
    container.style.height = '500px'
    container.style.minHeight = '500px'
    
    // Aguardar um frame para o browser aplicar as mudanças
    await new Promise(resolve => requestAnimationFrame(resolve))
  }
  
  // Verificar apenas a altura (width será calculado automaticamente pelo Lightweight Charts)
  const containerHeight = container.clientHeight || container.offsetHeight || 500
  console.log('📊 Inicializando gráfico, altura:', containerHeight)
  
  // Garantir que o container tem altura válida
  if (containerHeight <= 0) {
    console.error('❌ Container sem altura válida após forçar:', {
      clientHeight: container.clientHeight,
      offsetHeight: container.offsetHeight,
      style: container.style.cssText
    })
    return
  }

  // IMPORTANTE: Lightweight Charts funciona melhor quando você especifica apenas height
  // e deixa o width ser calculado automaticamente pelo container
  // Isso evita problemas quando o container ainda não tem dimensões definidas
  chart = createChart(container, {
    height: 500, // Altura fixa, width será calculado automaticamente
    layout: {
      background: { type: ColorType.Solid, color: '#0a0a0a' },
      textColor: '#d0d0d0'
    },
    grid: {
      vertLines: { color: '#333333', visible: true, style: 0 },
      horzLines: { color: '#333333', visible: true, style: 0 }
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
      borderColor: '#333333',
      rightOffset: 10,
      barSpacing: 2,
      rightBarStaysOnScroll: true
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
  
  // Garantir que o wrapper seja visível após criação
  setTimeout(() => {
    const wrapper = container.querySelector('.tv-lightweight-charts')
    if (wrapper) {
      wrapper.style.display = 'block'
      wrapper.style.visibility = 'visible'
      wrapper.style.opacity = '1'
      wrapper.style.width = '100%'
      wrapper.style.height = '100%'
      console.log('✅ Wrapper do gráfico configurado para visibilidade')
    }
  }, 50)
  
  // Verificar se o canvas foi criado
  setTimeout(() => {
    const container = getContainer()
    if (!container) return
    
    const allCanvases = container.querySelectorAll('canvas')
    console.log('📊 Total de canvases criados:', allCanvases?.length || 0)
    if (allCanvases && allCanvases.length > 0) {
      Array.from(allCanvases).forEach((canvas, i) => {
        console.log(`   - Canvas ${i} width:`, canvas.width)
        console.log(`   - Canvas ${i} height:`, canvas.height)
        console.log(`   - Canvas ${i} style:`, canvas.style.width, 'x', canvas.style.height)
      })
    }
    
    // Verificar estrutura do container
    console.log('📊 Estrutura do container:')
    console.log('   - Children:', container.children.length)
    Array.from(container.children || []).forEach((child, i) => {
      console.log(`   - Child ${i}:`, child.tagName, child.className)
    })
  }, 100)

  console.log('✅ Gráfico criado')

  // Série de candlesticks
  candleSeries = chart.addCandlestickSeries({
    upColor: '#00ff88',
    downColor: '#ff4444',
    borderUpColor: '#00ff88',
    borderDownColor: '#ff4444',
    wickUpColor: '#00ff88',
    wickDownColor: '#ff4444',
    priceFormat: {
      type: 'price',
      precision: 2,
      minMove: 0.01
    }
  })
  
  console.log('✅ Série de candlesticks criada:', !!candleSeries)
  
  // Verificar se a série foi criada corretamente
  if (!candleSeries) {
    console.error('❌ Erro ao criar série de candlesticks')
  }

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
}

// Carregar dados
const loadChartData = async () => {
  loading.value = true
  error.value = null

  try {
    // Usar endpoint consolidado /api/v1/chart-data
    console.log('📊 Carregando dados consolidados para:', props.symbol, props.timeframe)
    
    try {
      const chartDataResponse = await api.getChartData(props.symbol, props.timeframe, 500)
      console.log('📊 Resposta chart-data:', chartDataResponse)
      
      // Verificar se a resposta é HTML (erro de proxy)
      if (typeof chartDataResponse === 'string' && chartDataResponse.includes('<!DOCTYPE')) {
        throw new Error('API retornou HTML - Flask não está rodando ou proxy não configurado')
      }
      
      // Verificar se é objeto com success
      if (chartDataResponse && chartDataResponse.success && chartDataResponse.candles) {
        const candlesData = candlesResponse.data.candles.map(c => {
          // Lightweight Charts espera timestamp em segundos (Unix timestamp)
          // Se o backend retorna em ms, dividir por 1000
          let timestamp = c.time
          if (timestamp > 1000000000000) {
            // Se está em milissegundos (13 dígitos), converter para segundos
            timestamp = Math.floor(timestamp / 1000)
          }
          
          // Garantir que é um número válido
          const timeValue = Number(timestamp)
          if (isNaN(timeValue) || timeValue <= 0) {
            console.warn('Timestamp inválido:', timestamp)
            return null
          }
          
          // Lightweight Charts aceita timestamp como número (segundos Unix)
          return {
            time: timeValue,
            open: parseFloat(c.open) || 0,
            high: parseFloat(c.high) || 0,
            low: parseFloat(c.low) || 0,
            close: parseFloat(c.close) || 0
          }
        }).filter(c => c !== null) // Remover entradas inválidas

        const volumesData = candlesResponse.data.candles.map(c => {
          let timestamp = c.time
          if (timestamp > 1000000000000) {
            timestamp = Math.floor(timestamp / 1000)
          }
          
          return {
            time: timestamp,
            value: parseFloat(c.volume),
            color: c.close >= c.open ? 'rgba(38, 166, 154, 0.6)' : 'rgba(239, 83, 80, 0.6)'
          }
        })

        console.log('📊 Candles processados:', candlesData.length, 'primeiro:', candlesData[0])
        console.log('📊 Volumes processados:', volumesData.length)

        if (candlesData.length === 0) {
          console.error('❌ Nenhum candle válido processado')
          error.value = 'Nenhum dado válido para exibir'
          loading.value = false
          return
        }

        candles.value = candlesData

        if (candleSeries && volumeSeries && chart) {
          console.log('📊 Adicionando dados ao gráfico...')
          console.log('   - Candles:', candlesData.length)
          console.log('   - Volumes:', volumesData.length)
          console.log('   - Primeiro candle:', candlesData[0])
          console.log('   - Último candle:', candlesData[candlesData.length - 1])
          
          try {
            // Verificar formato dos dados antes de adicionar
            const firstCandle = candlesData[0]
            const lastCandle = candlesData[candlesData.length - 1]
            
            console.log('📊 Verificando formato dos dados:')
            console.log('   - Primeiro candle time:', firstCandle.time, typeof firstCandle.time)
            console.log('   - Último candle time:', lastCandle.time, typeof lastCandle.time)
            console.log('   - Primeiro candle preços:', { open: firstCandle.open, high: firstCandle.high, low: firstCandle.low, close: firstCandle.close })
            
            // Obter container (com fallback para backup)
            const container = getContainer()
            if (!container) {
              console.error('   ❌ Container não encontrado antes de adicionar dados!')
              error.value = 'Container do gráfico não encontrado'
              return
            }
            
            // Verificar canvas ANTES de adicionar dados
            // IMPORTANTE: O wrapper pode não existir ainda se o gráfico não foi totalmente inicializado
            const wrapperBefore = container.querySelector('.tv-lightweight-charts')
            const canvasBefore = wrapperBefore?.querySelectorAll('canvas') || container.querySelectorAll('canvas')
            console.log('   📊 Canvases ANTES de adicionar dados:', canvasBefore?.length || 0)
            console.log('   📊 Wrapper existe antes?', !!wrapperBefore)
            console.log('   📊 Container existe?', !!container)
            
            // Verificar se o gráfico e as séries estão prontos
            if (!chart || !candleSeries || !volumeSeries) {
              console.error('   ❌ Gráfico ou séries não estão prontos!')
              error.value = 'Gráfico não inicializado corretamente'
              return
            }
            
            // Adicionar dados às séries - usar TODOS os dados
            console.log('   📊 Adicionando', candlesData.length, 'candles')
            
            // Adicionar dados diretamente (sem limpar primeiro)
            candleSeries.setData(candlesData)
            console.log('   ✅ Candles adicionados à série')
            
            volumeSeries.setData(volumesData)
            console.log('   ✅ Volumes adicionados à série')
            
            // Verificar se os dados foram realmente adicionados
            const checkData = candleSeries.data()
            console.log('   📊 Dados confirmados na série:', checkData?.length || 0)
            
            // Forçar resize imediatamente após adicionar dados
            if (container && chart) {
              const width = container.clientWidth || 800
              const height = container.clientHeight || 500
              chart.resize(width, height)
              console.log('   ✅ Gráfico redimensionado imediatamente:', width, 'x', height)
            }
            
            // Verificar canvas após adicionar dados
            // Aguardar um pouco mais para o Lightweight Charts processar os dados
            setTimeout(() => {
              // Obter container (com fallback para backup)
              const container = getContainer()
              if (!container) {
                console.error('   ❌ Container não encontrado após adicionar dados!')
                return
              }
              
              // Buscar dentro do wrapper do Lightweight Charts
              const wrapper = container.querySelector('.tv-lightweight-charts')
              const canvasAfter = wrapper?.querySelectorAll('canvas') || container.querySelectorAll('canvas')
              console.log('   📊 Canvases após adicionar dados:', canvasAfter?.length || 0)
              console.log('   📊 Wrapper existe?', !!wrapper)
              console.log('   📊 Container children:', container.children.length)
              
              if (canvasAfter && canvasAfter.length > 0) {
                console.log('   ✅ Canvases encontrados!')
                Array.from(canvasAfter).forEach((canvas, i) => {
                  console.log(`   - Canvas ${i} após dados:`, canvas.width, 'x', canvas.height)
                })
              } else {
                console.warn('   ⚠️ Nenhum canvas encontrado após adicionar dados!')
                
                // Tentar forçar renderização múltiplas vezes
                if (chart && container) {
                  const width = container.clientWidth || 800
                  const height = container.clientHeight || 500
                  chart.resize(width, height)
                  console.log('   🔄 Tentando forçar renderização com resize:', width, 'x', height)
                  
                  // Tentar novamente após resize
                  setTimeout(() => {
                    const wrapper2 = container.querySelector('.tv-lightweight-charts')
                    const canvasAfter2 = wrapper2?.querySelectorAll('canvas') || container.querySelectorAll('canvas')
                    console.log('   📊 Canvases após resize forçado:', canvasAfter2?.length || 0)
                  }, 100)
                }
              }
            }, 200)
            
            // Aguardar um pouco antes de ajustar viewport
            setTimeout(() => {
              try {
                // Obter container (com fallback para backup)
                const container = getContainer()
                if (!container) {
                  console.error('   ❌ Container não encontrado durante verificação!')
                  return
                }
                
                // Verificar canvas - buscar dentro do wrapper do Lightweight Charts
                const wrapper = container.querySelector('.tv-lightweight-charts')
                const allCanvases = wrapper?.querySelectorAll('canvas') || container.querySelectorAll('canvas')
                console.log('   📊 Total de canvases encontrados:', allCanvases?.length || 0)
                console.log('   📊 Wrapper existe?', !!wrapper)
                
                if (allCanvases && allCanvases.length > 0) {
                  Array.from(allCanvases).forEach((canvas, i) => {
                    console.log(`   - Canvas ${i}:`, canvas.width, 'x', canvas.height)
                    console.log(`   - Canvas ${i} style:`, canvas.style.width, 'x', canvas.style.height)
                  })
                }
                
                // Verificar se há elementos SVG também
                const svgs = container.querySelectorAll('svg')
                console.log('   📊 Total de SVGs encontrados:', svgs?.length || 0)
                
                // Verificar se há dados na série antes de ajustar
                const seriesData = candleSeries.data()
                console.log('   📊 Dados na série:', seriesData?.length || 0)
                
                if (!seriesData || seriesData.length === 0) {
                  console.error('   ❌ Nenhum dado na série!')
                  return
                }
                
                // Ajustar viewport para mostrar todos os dados
                chart.timeScale().fitContent()
                console.log('   ✅ Viewport ajustado (fitContent)')
                
                // Aguardar um pouco e verificar/adjustar range
                setTimeout(() => {
                  const visibleRange = chart.timeScale().getVisibleRange()
                  console.log('   📊 Range visível após fitContent:', visibleRange)
                  
                  // Se ainda não estiver correto, ajustar manualmente
                  if (visibleRange && candlesData.length > 0) {
                    const firstTime = candlesData[0].time
                    const lastTime = candlesData[candlesData.length - 1].time
                    
                    if (firstTime < visibleRange.from || lastTime > visibleRange.to) {
                      console.log('   ⚠️ Ainda fora do range após fitContent, ajustando manualmente...')
                      try {
                        chart.timeScale().setVisibleRange({
                          from: firstTime,
                          to: lastTime
                        })
                        console.log('   ✅ Range ajustado manualmente')
                      } catch (e) {
                        console.error('   ❌ Erro ao ajustar:', e)
                      }
                    }
                  }
                }, 100)
                
                // Verificar range inicial
                const visibleRange = chart.timeScale().getVisibleRange()
                console.log('   📊 Range visível inicial:', visibleRange)
                
                // Verificar se os dados estão no range e ajustar se necessário
                if (visibleRange && candlesData.length > 0) {
                  const firstTime = candlesData[0].time
                  const lastTime = candlesData[candlesData.length - 1].time
                  console.log('   📊 Range dos dados:', { from: firstTime, to: lastTime })
                  console.log('   📊 Range visível atual:', visibleRange)
                  console.log('   📊 Dados dentro do range?', 
                    firstTime >= visibleRange.from && lastTime <= visibleRange.to)
                  
                  // Se não estiver no range, ajustar manualmente
                  if (firstTime < visibleRange.from || lastTime > visibleRange.to) {
                    console.log('   ⚠️ Dados fora do range! Ajustando manualmente...')
                    try {
                      chart.timeScale().setVisibleRange({
                        from: firstTime,
                        to: lastTime
                      })
                      console.log('   ✅ Range ajustado manualmente para:', { from: firstTime, to: lastTime })
                      
                      // Verificar novo range
                      const newRange = chart.timeScale().getVisibleRange()
                      console.log('   📊 Novo range visível:', newRange)
                    } catch (rangeErr) {
                      console.error('   ❌ Erro ao ajustar range:', rangeErr)
                    }
                  }
                } else if (candlesData.length > 0) {
                  // Se não há range visível, definir manualmente
                  const firstTime = candlesData[0].time
                  const lastTime = candlesData[candlesData.length - 1].time
                  console.log('   ⚠️ Sem range visível, definindo manualmente...')
                  try {
                    chart.timeScale().setVisibleRange({
                      from: firstTime,
                      to: lastTime
                    })
                    console.log('   ✅ Range definido manualmente')
                  } catch (rangeErr) {
                    console.error('   ❌ Erro ao definir range:', rangeErr)
                  }
                }
                
                // Forçar atualização visual
                chart.timeScale().scrollToPosition(0, false)
                console.log('   ✅ Viewport scrollado para início')
                
                // Forçar redesenho - importante fazer resize após adicionar dados
                // Usar a variável container já declarada no escopo superior
                if (container && chart) {
                  const width = container.clientWidth || 800
                  const height = container.clientHeight || 500
                  
                  // Resize força uma re-renderização completa
                  chart.resize(width, height)
                  console.log('   ✅ Gráfico redimensionado:', width, 'x', height)
                  
                  // Aguardar resize e forçar fitContent novamente
                  setTimeout(async () => {
                    chart.timeScale().fitContent()
                    console.log('   ✅ Viewport re-ajustado após resize')
                    
                    // Verificar canvas novamente após resize
                    const wrapper = container.querySelector('.tv-lightweight-charts')
                    const canvasesAfter = wrapper?.querySelectorAll('canvas') || container.querySelectorAll('canvas')
                    console.log('   📊 Canvases após resize:', canvasesAfter?.length || 0)
                    
                    // Verificar se o canvas principal tem conteúdo renderizado
                    if (canvasesAfter && canvasesAfter.length > 0) {
                      const mainCanvas = Array.from(canvasesAfter).find(c => c.width > 100 && c.height > 100)
                      if (mainCanvas) {
                        try {
                          const ctx = mainCanvas.getContext('2d', { willReadFrequently: true })
                          const imageData = ctx.getImageData(0, 0, Math.min(50, mainCanvas.width), Math.min(50, mainCanvas.height))
                          const hasContent = imageData.data.some((p, i) => i % 4 !== 3 && p !== 0)
                          console.log('   📊 Canvas principal tem conteúdo renderizado?', hasContent)
                          
                          // Verificar visibilidade do container e wrapper
                          // IMPORTANTE: Usar offsetWidth/offsetHeight em vez de clientWidth/clientHeight
                          // porque offsetWidth/offsetHeight incluem padding e bordas
                          const wrapper = container.querySelector('.tv-lightweight-charts')
                          const containerVisible = container.offsetWidth > 0 && container.offsetHeight > 0
                          const wrapperVisible = wrapper ? (wrapper.offsetWidth > 0 && wrapper.offsetHeight > 0) : false
                          
                          console.log('   📊 Container visível?', containerVisible)
                          console.log('   📊 Container dimensões (offset):', container.offsetWidth, 'x', container.offsetHeight)
                          console.log('   📊 Container dimensões (client):', container.clientWidth, 'x', container.clientHeight)
                          console.log('   📊 Container dimensões (scroll):', container.scrollWidth, 'x', container.scrollHeight)
                          console.log('   📊 Wrapper visível?', wrapperVisible)
                          console.log('   📊 Wrapper dimensões:', wrapper ? `${wrapper.offsetWidth}x${wrapper.offsetHeight}` : 'N/A')
                          console.log('   📊 Canvas dimensões:', mainCanvas.width, 'x', mainCanvas.height)
                          
                          // Se o container não está visível, forçar dimensões
                          if (!containerVisible) {
                            console.warn('   ⚠️ Container não está visível! Forçando dimensões...')
                            
                            // Buscar o container novamente do DOM para garantir que temos a referência correta
                            const domContainer = document.querySelector('.chart-container')
                            if (domContainer) {
                              domContainer.style.width = '100%'
                              domContainer.style.height = '500px'
                              domContainer.style.minHeight = '500px'
                              domContainer.style.display = 'block'
                              domContainer.style.visibility = 'visible'
                              domContainer.style.opacity = '1'
                              domContainer.style.position = 'relative'
                              
                              // Atualizar referências
                              containerBackup = domContainer
                              if (chartContainer.value !== domContainer) {
                                chartContainer.value = domContainer
                              }
                              
                              // Aguardar um frame para o browser aplicar as mudanças
                              await new Promise(resolve => requestAnimationFrame(resolve))
                              
                              // Verificar novamente
                              const newWidth = domContainer.offsetWidth || domContainer.clientWidth || 800
                              const newHeight = domContainer.offsetHeight || domContainer.clientHeight || 500
                              console.log('   📊 Novas dimensões do container:', newWidth, 'x', newHeight)
                              
                              // Forçar resize do gráfico
                              if (chart) {
                                chart.resize(newWidth, newHeight)
                                console.log('   ✅ Gráfico redimensionado para:', newWidth, 'x', newHeight)
                                
                                // Forçar fitContent novamente após resize
                                setTimeout(() => {
                                  chart.timeScale().fitContent()
                                  console.log('   ✅ Viewport ajustado após forçar dimensões')
                                }, 100)
                              }
                            } else {
                              console.error('   ❌ Container não encontrado no DOM!')
                            }
                          }
                          
                          const canvasStyle = window.getComputedStyle(mainCanvas)
                          console.log('   📊 Canvas style display:', canvasStyle.display)
                          console.log('   📊 Canvas style visibility:', canvasStyle.visibility)
                          console.log('   📊 Canvas style opacity:', canvasStyle.opacity)
                          
                          if (!hasContent) {
                            console.warn('   ⚠️ Canvas existe mas não tem conteúdo! Forçando renderização...')
                            // Forçar renderização novamente
                            chart.timeScale().fitContent()
                            chart.resize(container.clientWidth, container.clientHeight)
                          }
                        } catch (e) {
                          console.warn('   ⚠️ Erro ao verificar conteúdo do canvas:', e)
                        }
                      }
                    }
                  }, 100)
                }
              } catch (viewportErr) {
                console.error('❌ Erro ao ajustar viewport:', viewportErr)
                console.error('   Stack:', viewportErr.stack)
              }
            }, 100)
            
            console.log('✅ Dados adicionados ao gráfico com sucesso')
          } catch (err) {
            console.error('❌ Erro ao adicionar dados:', err)
            console.error('   Stack:', err.stack)
            error.value = `Erro ao renderizar: ${err.message}`
          }
        } else {
          console.warn('⚠️ Gráfico não inicializado ainda')
          console.warn('   - candleSeries:', !!candleSeries)
          console.warn('   - volumeSeries:', !!volumeSeries)
          console.warn('   - chart:', !!chart)
        }

        // Calcular EMAs
        calculateEMAs()
      } else {
        console.error('❌ Resposta inválida:', candlesResponse)
        error.value = 'Formato de dados inválido'
      }
    } catch (apiError) {
      console.error('❌ Erro na requisição API:', apiError)
      
      // Verificar tipo de erro
      const errorMessage = apiError.message || String(apiError)
      
      if (errorMessage.includes('HTML') || errorMessage.includes('Flask')) {
        error.value = '⚠️ Flask não está rodando. Execute: ./iniciar_servidores.sh'
      } else if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
        error.value = '⚠️ Não autenticado. Faça login primeiro.'
      } else if (errorMessage.includes('Network') || errorMessage.includes('ECONNREFUSED')) {
        error.value = '⚠️ Não foi possível conectar ao servidor. Verifique se o Flask está rodando na porta 9999.'
      } else {
        error.value = `Erro: ${errorMessage}`
      }
    }

    // Carregar níveis
    try {
      const levelsResponse = await api.getChartLevels(props.symbol, props.timeframe)
      if (levelsResponse.success) {
        levels.value = levelsResponse.data
        addLevels()
      }
    } catch (e) {
      console.warn('Erro ao carregar níveis:', e)
    }

    // Carregar indicadores avançados
    try {
      const indicatorsResponse = await api.getAdvancedIndicators(props.symbol, props.timeframe, 500)
      if (indicatorsResponse.success) {
        const indicators = indicatorsResponse.data.indicators
        updateIndicators(indicators)
      }
    } catch (e) {
      console.warn('Erro ao carregar indicadores:', e)
    }

  } catch (err) {
    error.value = err.message || 'Erro ao carregar dados do gráfico'
    console.error('Erro ao carregar gráfico:', err)
  } finally {
    loading.value = false
  }
}

// Calcular EMAs
const calculateEMAs = () => {
  if (!candles.value.length) return

  const closes = candles.value.map(c => c.close)
  
  // EMA 8
  const ema8 = calculateEMA(closes, 8)
  const ema8Data = candles.value.slice(7).map((c, i) => ({
    time: c.time,
    value: ema8[i]
  }))
  if (ema8Series) ema8Series.setData(ema8Data)

  // EMA 21
  const ema21 = calculateEMA(closes, 21)
  const ema21Data = candles.value.slice(20).map((c, i) => ({
    time: c.time,
    value: ema21[i]
  }))
  if (ema21Series) ema21Series.setData(ema21Data)
}

// Função para calcular EMA
const calculateEMA = (prices, period) => {
  const multiplier = 2 / (period + 1)
  const ema = []
  let sum = 0

  for (let i = 0; i < prices.length; i++) {
    if (i === 0) {
      sum = prices[i]
    } else {
      sum = (prices[i] - sum) * multiplier + sum
    }
    ema.push(sum)
  }

  return ema
}

// Adicionar níveis ao gráfico
const addLevels = () => {
  if (!levels.value || !chart || !candleSeries) return

  const { suportes, resistencias, operacionais } = levels.value

  // Suportes
  suportes?.forEach((preco, index) => {
    if (preco && preco > 0) {
      candleSeries.createPriceLine({
        price: preco,
        color: '#26a69a',
        lineWidth: 1,
        lineStyle: 2, // Dashed
        axisLabelVisible: true,
        title: `S${index + 1}`
      })
    }
  })

  // Resistências
  resistencias?.forEach((preco, index) => {
    if (preco && preco > 0) {
      candleSeries.createPriceLine({
        price: preco,
        color: '#ef5350',
        lineWidth: 1,
        lineStyle: 2, // Dashed
        axisLabelVisible: true,
        title: `R${index + 1}`
      })
    }
  })

  // Níveis operacionais
  if (operacionais) {
    if (operacionais.entry && operacionais.entry > 0) {
      candleSeries.createPriceLine({
        price: operacionais.entry,
        color: '#ffffff',
        lineWidth: 2,
        lineStyle: 0, // Solid
        axisLabelVisible: true,
        title: 'Entry'
      })
    }

    if (operacionais.stop_loss && operacionais.stop_loss > 0) {
      candleSeries.createPriceLine({
        price: operacionais.stop_loss,
        color: '#ef5350',
        lineWidth: 2,
        lineStyle: 0, // Solid
        axisLabelVisible: true,
        title: 'Stop Loss'
      })
    }

    if (operacionais.tp1 && operacionais.tp1 > 0) {
      candleSeries.createPriceLine({
        price: operacionais.tp1,
        color: '#26a69a',
        lineWidth: 1.5,
        lineStyle: 1, // Dotted
        axisLabelVisible: true,
        title: 'TP1'
      })
    }

    if (operacionais.tp2 && operacionais.tp2 > 0) {
      candleSeries.createPriceLine({
        price: operacionais.tp2,
        color: '#26a69a',
        lineWidth: 1.5,
        lineStyle: 1,
        axisLabelVisible: true,
        title: 'TP2'
      })
    }

    if (operacionais.tp3 && operacionais.tp3 > 0) {
      candleSeries.createPriceLine({
        price: operacionais.tp3,
        color: '#26a69a',
        lineWidth: 1.5,
        lineStyle: 1,
        axisLabelVisible: true,
        title: 'TP3'
      })
    }
  }
}

// Atualizar indicadores
const updateIndicators = (indicators) => {
  // Implementar RSI e MACD se necessário
  // Por enquanto, apenas EMAs são calculados localmente
}

// Toggle indicador
const toggleIndicator = (key) => {
  activeIndicators.value[key] = !activeIndicators.value[key]

  if (key === 'ema8') {
    ema8Series?.applyOptions({ visible: activeIndicators.value.ema8 })
  } else if (key === 'ema21') {
    ema21Series?.applyOptions({ visible: activeIndicators.value.ema21 })
  } else if (key === 'rsi') {
    showRSI.value = activeIndicators.value.rsi
    // TODO: Implementar gráfico RSI
  } else if (key === 'macd') {
    showMACD.value = activeIndicators.value.macd
    // TODO: Implementar gráfico MACD
  }
}

// Resize handler
const handleResize = () => {
  const container = getContainer()
  if (chart && container) {
    chart.applyOptions({ width: container.clientWidth })
  }
}

// Watch props
watch([() => props.symbol, () => props.timeframe], async () => {
  // Se o gráfico não existe, inicializar primeiro
  if (!chart || !candleSeries || !volumeSeries) {
    console.log('📊 Gráfico não existe, inicializando...')
    await nextTick()
    setTimeout(() => {
      const container = getContainer()
      if (!container) return
      if (!chart) {
        initChart()
      }
      setTimeout(() => {
        if (chart && candleSeries && volumeSeries) {
          loadChartData()
        }
      }, 200)
    }, 100)
  } else {
    // Gráfico já existe, apenas recarregar dados
    loadChartData()
  }
}, { immediate: false })

// Lifecycle
onMounted(async () => {
  await nextTick()
  
  // Aguardar um pouco para garantir que o container está renderizado
  setTimeout(async () => {
    const container = getContainer()
    if (!container) {
      console.error('❌ Container do gráfico não encontrado')
      return
    }
    
    // Verificar e forçar dimensões do container
    if (container.clientWidth <= 0 || container.clientHeight <= 0) {
      console.warn('⚠️ Container sem dimensões no onMounted, forçando...')
      container.style.width = '100%'
      container.style.height = '500px'
      container.style.minHeight = '500px'
      container.style.display = 'block'
      container.style.visibility = 'visible'
      container.style.opacity = '1'
      container.style.position = 'relative'
      
      // Aguardar um frame antes de inicializar
      await new Promise(resolve => requestAnimationFrame(resolve))
    }
    
    await initChart()
    
    // Aguardar gráfico inicializar completamente antes de carregar dados
    setTimeout(() => {
      if (chart && candleSeries && volumeSeries) {
        console.log('✅ Gráfico pronto, carregando dados...')
        loadChartData()
      } else {
        console.warn('⚠️ Gráfico não inicializado, tentando novamente...')
        setTimeout(() => {
          if (chart && candleSeries && volumeSeries) {
            loadChartData()
          } else {
            error.value = 'Erro ao inicializar gráfico'
          }
        }, 200)
      }
    }, 100)
  }, 100)
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.remove()
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
  @apply w-full;
  height: 500px;
  min-height: 500px;
  background-color: #0a0a0a;
  position: relative;
  overflow: visible;
  z-index: 1;
}

/* Garantir que o wrapper do Lightweight Charts seja visível */
.chart-container :deep(.tv-lightweight-charts) {
  width: 100% !important;
  height: 100% !important;
  position: relative !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

/* Garantir que todos os canvases sejam visíveis */
.chart-container :deep(canvas) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  position: absolute !important;
  pointer-events: auto !important;
}

/* Garantir que o canvas principal seja visível */
.chart-container :deep(.tv-lightweight-charts canvas) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.indicator-container {
  @apply w-full mt-4;
  height: 150px;
}
</style>

