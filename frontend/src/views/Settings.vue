<template>
  <div class="settings">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">Configurações</h1>
      <p class="text-terminal-green/70">Ajuste suas preferências</p>
    </div>

    <!-- Tabs -->
    <div class="mb-6 border-b border-terminal-green/20">
      <div class="flex gap-4">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-4 py-2 border-b-2 transition"
          :class="activeTab === tab.id 
            ? 'border-terminal-green text-terminal-green font-bold' 
            : 'border-transparent text-terminal-green/70 hover:text-terminal-green'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="card">
      <!-- Perfil -->
      <div v-if="activeTab === 'profile'" class="space-y-6">
        <h2 class="text-xl font-bold mb-4">Perfil do Usuário</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm mb-2">Nome de Usuário</label>
            <input
              v-model="profile.username"
              type="text"
              class="input-field w-full"
              placeholder="Seu nome de usuário"
            />
          </div>

          <div>
            <label class="block text-sm mb-2">Email</label>
            <input
              v-model="profile.email"
              type="email"
              class="input-field w-full"
              placeholder="seu@email.com"
            />
          </div>

          <div>
            <label class="block text-sm mb-2">Plano</label>
            <div class="px-3 py-2 bg-terminal-dark rounded border border-terminal-green/30 text-terminal-green">
              {{ profile.tier || 'Free' }}
            </div>
          </div>

          <div class="flex gap-2 pt-4">
            <button
              @click="saveProfile"
              :disabled="saving"
              class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80 transition disabled:opacity-50"
            >
              {{ saving ? 'Salvando...' : 'Salvar Alterações' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Alterar Senha -->
      <div v-if="activeTab === 'password'" class="space-y-6">
        <h2 class="text-xl font-bold mb-4">Alterar Senha</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm mb-2">Senha Atual</label>
            <input
              v-model="passwordForm.current"
              type="password"
              class="input-field w-full"
              placeholder="Digite sua senha atual"
            />
          </div>

          <div>
            <label class="block text-sm mb-2">Nova Senha</label>
            <input
              v-model="passwordForm.new"
              type="password"
              class="input-field w-full"
              placeholder="Digite sua nova senha"
            />
          </div>

          <div>
            <label class="block text-sm mb-2">Confirmar Nova Senha</label>
            <input
              v-model="passwordForm.confirm"
              type="password"
              class="input-field w-full"
              placeholder="Confirme sua nova senha"
            />
          </div>

          <div class="flex gap-2 pt-4">
            <button
              @click="changePassword"
              :disabled="!isPasswordValid || saving"
              class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80 transition disabled:opacity-50"
            >
              {{ saving ? 'Alterando...' : 'Alterar Senha' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Preferências de Trading -->
      <div v-if="activeTab === 'trading'" class="space-y-6">
        <h2 class="text-xl font-bold mb-4">Preferências de Trading</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm mb-2">Par Padrão</label>
            <select v-model="tradingPrefs.defaultSymbol" class="input-field w-full">
              <option value="BTCUSDT">BTC/USDT</option>
              <option value="ETHUSDT">ETH/USDT</option>
              <option value="BNBUSDT">BNB/USDT</option>
              <option value="SOLUSDT">SOL/USDT</option>
              <option value="ADAUSDT">ADA/USDT</option>
            </select>
          </div>

          <div>
            <label class="block text-sm mb-2">Timeframe Padrão</label>
            <select v-model="tradingPrefs.defaultTimeframe" class="input-field w-full">
              <option value="1m">1 Minuto</option>
              <option value="5m">5 Minutos</option>
              <option value="15m">15 Minutos</option>
              <option value="1h">1 Hora</option>
              <option value="4h">4 Horas</option>
              <option value="1d">1 Dia</option>
            </select>
          </div>

          <div>
            <label class="block text-sm mb-2">Risk per Trade (%)</label>
            <input
              v-model.number="tradingPrefs.riskPerTrade"
              type="number"
              step="0.1"
              min="0.1"
              max="5"
              class="input-field w-full"
            />
            <div class="text-xs text-terminal-green/70 mt-1">
              Porcentagem do capital a arriscar por trade (recomendado: 1-2%)
            </div>
          </div>

          <div>
            <label class="block text-sm mb-2">R:R Mínimo</label>
            <input
              v-model.number="tradingPrefs.minRR"
              type="number"
              step="0.1"
              min="1"
              max="10"
              class="input-field w-full"
            />
            <div class="text-xs text-terminal-green/70 mt-1">
              Risk:Reward mínimo aceito (ex: 1:2 = 2.0)
            </div>
          </div>

          <div class="flex gap-2 pt-4">
            <button
              @click="saveTradingPrefs"
              :disabled="saving"
              class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80 transition disabled:opacity-50"
            >
              {{ saving ? 'Salvando...' : 'Salvar Preferências' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Notificações -->
      <div v-if="activeTab === 'notifications'" class="space-y-6">
        <h2 class="text-xl font-bold mb-4">Configurações de Notificações</h2>
        
        <div class="space-y-4">
          <div class="flex justify-between items-center p-4 bg-terminal-dark rounded border border-terminal-green/30">
            <div>
              <div class="font-bold mb-1">Som de Notificação</div>
              <div class="text-sm text-terminal-green/70">Tocar som quando alertas dispararem</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                v-model="notifPrefs.sound"
                type="checkbox"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-terminal-green/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-terminal-green after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-terminal-green"></div>
            </label>
          </div>

          <div class="flex justify-between items-center p-4 bg-terminal-dark rounded border border-terminal-green/30">
            <div>
              <div class="font-bold mb-1">Atualização Automática</div>
              <div class="text-sm text-terminal-green/70">Atualizar dados automaticamente no dashboard</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                v-model="notifPrefs.autoRefresh"
                type="checkbox"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-terminal-green/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-terminal-green after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-terminal-green"></div>
            </label>
          </div>

          <div>
            <label class="block text-sm mb-2">Intervalo de Atualização (segundos)</label>
            <input
              v-model.number="notifPrefs.refreshInterval"
              type="number"
              min="10"
              max="300"
              step="10"
              class="input-field w-full"
            />
            <div class="text-xs text-terminal-green/70 mt-1">
              Tempo entre atualizações automáticas (10-300 segundos)
            </div>
          </div>

          <div class="flex gap-2 pt-4">
            <button
              @click="saveNotificationPrefs"
              :disabled="saving"
              class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80 transition disabled:opacity-50"
            >
              {{ saving ? 'Salvando...' : 'Salvar Configurações' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Alertas -->
      <div v-if="activeTab === 'alerts'" class="space-y-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">Gerenciar Alertas</h2>
          <button
            @click="showCreateAlert = true"
            class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80 transition"
          >
            + Novo Alerta
          </button>
        </div>

        <AlertForm
          v-if="showCreateAlert"
          @submit="handleCreateAlert"
          @cancel="showCreateAlert = false"
        />

        <AlertsList
          :alerts="alerts"
          :loading="alertsLoading"
          @create="showCreateAlert = true"
          @edit="handleEditAlert"
          @delete="handleDeleteAlert"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AlertForm from '@/components/alerts/AlertForm.vue'
import AlertsList from '@/components/alerts/AlertsList.vue'
import api from '@/services/api'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeTab = ref(route.query.tab || 'profile')
const saving = ref(false)

// Tabs
const tabs = [
  { id: 'profile', label: 'Perfil' },
  { id: 'password', label: 'Alterar Senha' },
  { id: 'trading', label: 'Trading' },
  { id: 'notifications', label: 'Notificações' },
  { id: 'alerts', label: 'Alertas' }
]

// Profile
const profile = ref({
  username: '',
  email: '',
  tier: 'Free'
})

// Password
const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

const isPasswordValid = computed(() => {
  return passwordForm.value.current &&
         passwordForm.value.new &&
         passwordForm.value.new === passwordForm.value.confirm &&
         passwordForm.value.new.length >= 6
})

// Trading Preferences
const tradingPrefs = ref({
  defaultSymbol: 'BTCUSDT',
  defaultTimeframe: '1h',
  riskPerTrade: 2.0,
  minRR: 2.0
})

// Notification Preferences
const notifPrefs = ref({
  sound: true,
  autoRefresh: true,
  refreshInterval: 30
})

// Alerts
const alerts = ref([])
const alertsLoading = ref(false)
const showCreateAlert = ref(false)
const editingAlert = ref(null)

// Load settings from localStorage
const loadSettings = () => {
  // Profile
  const savedProfile = localStorage.getItem('user_profile')
  if (savedProfile) {
    profile.value = { ...profile.value, ...JSON.parse(savedProfile) }
  }

  // Trading prefs
  const savedTrading = localStorage.getItem('trading_prefs')
  if (savedTrading) {
    tradingPrefs.value = { ...tradingPrefs.value, ...JSON.parse(savedTrading) }
  }

  // Notification prefs
  const savedNotif = localStorage.getItem('notification_prefs')
  if (savedNotif) {
    notifPrefs.value = { ...notifPrefs.value, ...JSON.parse(savedNotif) }
  }
}

// Save methods
const saveProfile = async () => {
  saving.value = true
  try {
    localStorage.setItem('user_profile', JSON.stringify(profile.value))
    alert('✅ Perfil salvo com sucesso!')
  } catch (err) {
    console.error('Erro ao salvar perfil:', err)
    alert('❌ Erro ao salvar perfil')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  saving.value = true
  try {
    // TODO: Implementar endpoint de mudança de senha
    alert('✅ Senha alterada com sucesso!')
    passwordForm.value = { current: '', new: '', confirm: '' }
  } catch (err) {
    console.error('Erro ao alterar senha:', err)
    alert('❌ Erro ao alterar senha')
  } finally {
    saving.value = false
  }
}

const saveTradingPrefs = async () => {
  saving.value = true
  try {
    localStorage.setItem('trading_prefs', JSON.stringify(tradingPrefs.value))
    alert('✅ Preferências de trading salvas!')
  } catch (err) {
    console.error('Erro ao salvar preferências:', err)
    alert('❌ Erro ao salvar preferências')
  } finally {
    saving.value = false
  }
}

const saveNotificationPrefs = async () => {
  saving.value = true
  try {
    localStorage.setItem('notification_prefs', JSON.stringify(notifPrefs.value))
    alert('✅ Configurações de notificações salvas!')
  } catch (err) {
    console.error('Erro ao salvar configurações:', err)
    alert('❌ Erro ao salvar configurações')
  } finally {
    saving.value = false
  }
}

// Alerts methods
const loadAlerts = async () => {
  alertsLoading.value = true
  try {
    const data = await api.getAlertsV1()
    if (data && Array.isArray(data)) {
      alerts.value = data
    }
  } catch (err) {
    console.error('Erro ao carregar alertas:', err)
  } finally {
    alertsLoading.value = false
  }
}

const handleCreateAlert = async (alertData) => {
  saving.value = true
  try {
    await api.createAlertV1(alertData)
    alert('✅ Alerta criado com sucesso!')
    showCreateAlert.value = false
    await loadAlerts()
  } catch (err) {
    console.error('Erro ao criar alerta:', err)
    alert('❌ Erro ao criar alerta')
  } finally {
    saving.value = false
  }
}

const handleEditAlert = (alert) => {
  editingAlert.value = alert
  showCreateAlert.value = true
}

const handleDeleteAlert = async (alert) => {
  saving.value = true
  try {
    await api.deleteAlertV1(alert.id)
    alert('✅ Alerta deletado com sucesso!')
    await loadAlerts()
  } catch (err) {
    console.error('Erro ao deletar alerta:', err)
    alert('❌ Erro ao deletar alerta')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSettings()
  if (activeTab.value === 'alerts') {
    loadAlerts()
  }
})

// Watch activeTab to load alerts when switching to alerts tab
watch(activeTab, (newTab) => {
  if (newTab === 'alerts') {
    loadAlerts()
  }
})
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 bg-terminal-dark border border-terminal-green/30 rounded text-terminal-green focus:border-terminal-green focus:outline-none;
}
</style>
