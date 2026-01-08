<template>
  <WidgetBase 
    title="VOLUME SURGE"
    :initial-x="20"
    :initial-y="200"
    @close="$emit('close')"
  >
    <div v-if="volumeSurge" class="volume-alert-content">
      <div class="alert-icon">⚡</div>
      <div class="alert-stats">
        <div class="stat-row">
          <span class="label">RATIO:</span>
          <span class="value">{{ volumeSurge.ratio.toFixed(1) }}x</span>
        </div>
        <div class="stat-row">
          <span class="label">COUNT:</span>
          <span class="value">{{ volumeSurge.count }} alvos</span>
        </div>
        <div class="stat-row">
          <span class="label">MAX VOL:</span>
          <span class="value">{{ volumeSurge.maxSymbol }}</span>
        </div>
      </div>
      
      <button class="action-button" @click="filterBySurge">
        FILTRAR SURGES →
      </button>
    </div>
    
    <div v-else class="no-alert">
      <span>✓ Volume Normal</span>
    </div>
  </WidgetBase>
</template>

<script setup>
import { computed } from 'vue'
import WidgetBase from './WidgetBase.vue'

const props = defineProps({
  opportunities: { 
    type: Array, 
    default: () => [] 
  }
})

const emit = defineEmits(['close', 'filter-surge'])

const volumeSurge = computed(() => {
  // Usar rvol_m30 ou rvol (dados do Wick Radar) em vez de volume_ratio
  const highVolumeTargets = props.opportunities.filter(opp => {
    const rvol = opp.rvol_m30 || opp.rvol || 0
    return rvol > 2.0
  })
  
  if (highVolumeTargets.length === 0) return null
  
  const maxVolume = Math.max(...highVolumeTargets.map(t => t.rvol_m30 || t.rvol || 0))
  const maxTarget = highVolumeTargets.find(t => (t.rvol_m30 || t.rvol) === maxVolume)
  
  return {
    count: highVolumeTargets.length,
    ratio: maxVolume,
    maxSymbol: maxTarget?.symbol || '---'
  }
})

const filterBySurge = () => {
  emit('filter-surge')
}
</script>

<style scoped>
.volume-alert-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-icon {
  font-size: 32px;
  text-align: center;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.alert-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

.label {
  opacity: 0.7;
  font-size: 10px;
}

.value {
  font-weight: bold;
  color: #00ff41;
}

.action-button {
  background: transparent;
  border: 1px solid #00ff41;
  color: #00ff41;
  padding: 8px 12px;
  cursor: pointer;
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.2s;
  border-radius: 4px;
}

.action-button:hover {
  background: rgba(0, 255, 65, 0.1);
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
}

.no-alert {
  text-align: center;
  opacity: 0.6;
  padding: 12px;
}
</style>
