<template>
  <div class="alerts-list">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-bold">Alertas Ativos</h3>
      <button
        @click="$emit('create')"
        class="px-3 py-1 rounded bg-terminal-green text-black hover:opacity-80 transition text-sm"
      >
        + Novo Alerta
      </button>
    </div>

    <div v-if="loading" class="text-center py-8">
      <LoadingSpinner />
    </div>

    <div v-else-if="alerts.length === 0" class="text-center py-8 text-terminal-green/70">
      Nenhum alerta ativo. Crie um alerta para começar!
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="p-4 bg-terminal-dark rounded border border-terminal-green/30 hover:border-terminal-green transition"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-bold text-lg">{{ alert.symbol }}</span>
              <span 
                class="text-xs px-2 py-1 rounded"
                :class="getStatusClass(alert.status)"
              >
                {{ getStatusLabel(alert.status) }}
              </span>
            </div>
            
            <div class="text-sm text-terminal-green/70 mb-1">
              <span class="font-semibold">Tipo:</span> {{ getTypeLabel(alert.type) }}
            </div>
            
            <div class="text-sm text-terminal-green/70 mb-1">
              <span class="font-semibold">Condição:</span> {{ formatCondition(alert.condition) }}
            </div>
            
            <div v-if="alert.description" class="text-xs text-terminal-green/60 mt-2 italic">
              {{ alert.description }}
            </div>
            
            <div v-if="alert.triggered_at" class="text-xs text-terminal-green/60 mt-2">
              Disparado em: {{ formatDate(alert.triggered_at) }}
            </div>
          </div>
          
          <div class="flex gap-2 ml-4">
            <button
              @click="$emit('edit', alert)"
              class="px-2 py-1 rounded bg-terminal-green/20 text-terminal-green hover:bg-terminal-green/30 transition text-sm"
              title="Editar"
            >
              ✏️
            </button>
            <button
              @click="handleDelete(alert)"
              class="px-2 py-1 rounded bg-red-500/20 text-red-500 hover:bg-red-500/30 transition text-sm"
              title="Deletar"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const props = defineProps({
  alerts: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'create', 'delete'])

const getStatusClass = (status) => {
  const classes = {
    active: 'bg-terminal-green/20 text-terminal-green',
    triggered: 'bg-yellow-500/20 text-yellow-500',
    paused: 'bg-terminal-green/20 text-terminal-green/70',
    disabled: 'bg-terminal-green/10 text-terminal-green/50'
  }
  return classes[status] || classes.active
}

const getStatusLabel = (status) => {
  const labels = {
    active: 'Ativo',
    triggered: 'Disparado',
    paused: 'Pausado',
    disabled: 'Desabilitado'
  }
  return labels[status] || 'Desconhecido'
}

const getTypeLabel = (type) => {
  const labels = {
    price: 'Preço',
    rsi: 'RSI',
    volume: 'Volume',
    funding: 'Funding Rate',
    oi: 'Open Interest'
  }
  return labels[type] || type
}

const formatCondition = (condition) => {
  if (!condition) return '--'
  
  // Formato esperado: "above:50000" ou "below:30000"
  const parts = condition.split(':')
  if (parts.length !== 2) return condition
  
  const [operator, value] = parts
  const operatorLabels = {
    above: 'Acima de',
    below: 'Abaixo de',
    crosses_above: 'Cruza para cima',
    crosses_below: 'Cruza para baixo',
    spike: 'Spike',
    change_above: 'Mudança acima de'
  }
  
  const operatorLabel = operatorLabels[operator] || operator
  return `${operatorLabel} ${parseFloat(value).toLocaleString('pt-BR')}`
}

const formatDate = (dateString) => {
  if (!dateString) return '--'
  try {
    return format(new Date(dateString), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })
  } catch {
    return dateString
  }
}

const handleDelete = (alert) => {
  if (confirm(`Tem certeza que deseja deletar o alerta para ${alert.symbol}?`)) {
    emit('delete', alert)
  }
}
</script>

<style scoped>
.alerts-list {
  @apply w-full;
}
</style>

