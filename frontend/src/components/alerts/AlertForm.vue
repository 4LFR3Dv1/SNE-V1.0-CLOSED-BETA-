<template>
  <div class="alert-form">
    <div class="mb-4">
      <h3 class="text-lg font-bold mb-4">{{ editing ? 'Editar Alerta' : 'Criar Novo Alerta' }}</h3>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Símbolo -->
      <div>
        <label class="block text-sm mb-2">Par de Negociação</label>
        <select 
          v-model="form.symbol" 
          class="input-field w-full"
          required
        >
          <option value="">Selecione um par</option>
          <option value="BTCUSDT">BTC/USDT</option>
          <option value="ETHUSDT">ETH/USDT</option>
          <option value="BNBUSDT">BNB/USDT</option>
          <option value="SOLUSDT">SOL/USDT</option>
          <option value="ADAUSDT">ADA/USDT</option>
          <option value="XRPUSDT">XRP/USDT</option>
          <option value="DOGEUSDT">DOGE/USDT</option>
          <option value="DOTUSDT">DOT/USDT</option>
        </select>
      </div>

      <!-- Tipo de Alerta -->
      <div>
        <label class="block text-sm mb-2">Tipo de Alerta</label>
        <select 
          v-model="form.type" 
          class="input-field w-full"
          required
          @change="updateConditionOptions"
        >
          <option value="">Selecione um tipo</option>
          <option value="price">Preço</option>
          <option value="rsi">RSI</option>
          <option value="volume">Volume</option>
          <option value="funding">Funding Rate</option>
          <option value="oi">Open Interest</option>
        </select>
      </div>

      <!-- Condição -->
      <div v-if="form.type">
        <label class="block text-sm mb-2">Condição</label>
        <select 
          v-model="form.condition_operator" 
          class="input-field w-full"
          required
        >
          <option value="">Selecione uma condição</option>
          <option 
            v-for="op in conditionOptions" 
            :key="op.value"
            :value="op.value"
          >
            {{ op.label }}
          </option>
        </select>
      </div>

      <!-- Valor -->
      <div v-if="form.type && form.condition_operator">
        <label class="block text-sm mb-2">Valor</label>
        <input
          v-model.number="form.condition_value"
          type="number"
          step="0.01"
          class="input-field w-full"
          :placeholder="getPlaceholder()"
          required
        />
        <div class="text-xs text-terminal-green/70 mt-1">
          {{ getDescription() }}
        </div>
      </div>

      <!-- Descrição (Opcional) -->
      <div>
        <label class="block text-sm mb-2">Descrição (Opcional)</label>
        <input
          v-model="form.description"
          type="text"
          class="input-field w-full"
          placeholder="Ex: Alerta de alta do BTC"
        />
      </div>

      <!-- Ações -->
      <div class="flex gap-2 justify-end pt-4 border-t border-terminal-green/20">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 rounded bg-terminal-dark border border-terminal-green/30 text-terminal-green hover:bg-terminal-dark/80 transition"
        >
          Cancelar
        </button>
        <button
          type="submit"
          :disabled="!isFormValid || saving"
          class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ saving ? 'Salvando...' : (editing ? 'Salvar' : 'Criar Alerta') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  alert: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const editing = computed(() => !!props.alert)

const form = ref({
  symbol: '',
  type: '',
  condition_operator: '',
  condition_value: null,
  description: ''
})

const conditionOptions = ref([])
const saving = ref(false)

// Condições por tipo
const conditionOptionsMap = {
  price: [
    { value: 'above', label: 'Acima de' },
    { value: 'below', label: 'Abaixo de' },
    { value: 'crosses_above', label: 'Cruza para cima' },
    { value: 'crosses_below', label: 'Cruza para baixo' }
  ],
  rsi: [
    { value: 'above', label: 'Acima de (Overbought)' },
    { value: 'below', label: 'Abaixo de (Oversold)' },
    { value: 'crosses_above', label: 'Cruza para cima' },
    { value: 'crosses_below', label: 'Cruza para baixo' }
  ],
  volume: [
    { value: 'above', label: 'Acima de' },
    { value: 'below', label: 'Abaixo de' },
    { value: 'spike', label: 'Spike (x2 do normal)' }
  ],
  funding: [
    { value: 'above', label: 'Acima de' },
    { value: 'below', label: 'Abaixo de' }
  ],
  oi: [
    { value: 'above', label: 'Acima de' },
    { value: 'below', label: 'Abaixo de' },
    { value: 'change_above', label: 'Mudança acima de %' }
  ]
}

const updateConditionOptions = () => {
  if (form.value.type && conditionOptionsMap[form.value.type]) {
    conditionOptions.value = conditionOptionsMap[form.value.type]
    form.value.condition_operator = ''
    form.value.condition_value = null
  } else {
    conditionOptions.value = []
  }
}

const getPlaceholder = () => {
  if (form.value.type === 'price') return 'Ex: 50000'
  if (form.value.type === 'rsi') return 'Ex: 70 (para overbought) ou 30 (para oversold)'
  if (form.value.type === 'volume') return 'Ex: 1000000'
  if (form.value.type === 'funding') return 'Ex: 0.01 (1%)'
  if (form.value.type === 'oi') return 'Ex: 1000000000'
  return ''
}

const getDescription = () => {
  if (form.value.type === 'price') return 'Preço em USDT'
  if (form.value.type === 'rsi') return 'RSI de 0 a 100'
  if (form.value.type === 'volume') return 'Volume 24h em USDT'
  if (form.value.type === 'funding') return 'Funding Rate em decimal (0.01 = 1%)'
  if (form.value.type === 'oi') return 'Open Interest em USDT'
  return ''
}

const isFormValid = computed(() => {
  return form.value.symbol && 
         form.value.type && 
         form.value.condition_operator && 
         form.value.condition_value !== null &&
         form.value.condition_value !== ''
})

const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  saving.value = true
  
  try {
    // Construir objeto de alerta no formato esperado pelo backend
    const alertData = {
      symbol: form.value.symbol,
      type: form.value.type,
      condition: `${form.value.condition_operator}:${form.value.condition_value}`,
      description: form.value.description || `${form.value.symbol} ${form.value.condition_operator} ${form.value.condition_value}`,
      status: 'active'
    }
    
    emit('submit', alertData)
  } catch (error) {
    console.error('Erro ao salvar alerta:', error)
  } finally {
    saving.value = false
  }
}

// Carregar dados do alerta se estiver editando
watch(() => props.alert, (newAlert) => {
  if (newAlert) {
    form.value = {
      symbol: newAlert.symbol || '',
      type: newAlert.type || '',
      condition_operator: newAlert.condition?.split(':')[0] || '',
      condition_value: parseFloat(newAlert.condition?.split(':')[1]) || null,
      description: newAlert.description || ''
    }
    updateConditionOptions()
  }
}, { immediate: true })
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 bg-terminal-dark border border-terminal-green/30 rounded text-terminal-green focus:border-terminal-green focus:outline-none;
}
</style>

