<template>
  <div class="terminal-log">
    <div class="terminal-header">
      <span class="terminal-title">📺 TERMINAL DE LOG</span>
      <button @click="clearLogs" class="btn-clear">Limpar</button>
    </div>
    <div class="terminal-content" ref="terminalRef">
      <div 
        v-for="log in logs" 
        :key="log.id"
        class="log-line"
        :class="log.type.toLowerCase()"
      >
        <span class="log-time">[{{ log.timestamp }}]</span>
        <span class="log-message">{{ log.message }}</span>
      </div>
      <div v-if="logs.length === 0" class="log-empty">
        Nenhum log ainda...
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'

const props = defineProps({
  logs: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['clear'])

const terminalRef = ref(null)

const clearLogs = () => {
  emit('clear')
}

// Auto-scroll para o final quando novos logs chegarem
watch(() => props.logs.length, () => {
  nextTick(() => {
    if (terminalRef.value) {
      terminalRef.value.scrollTop = terminalRef.value.scrollHeight
    }
  })
})

onMounted(() => {
  if (terminalRef.value) {
    terminalRef.value.scrollTop = terminalRef.value.scrollHeight
  }
})
</script>

<style scoped>
.terminal-log {
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(0, 255, 0, 0.2);
}

.terminal-title {
  color: #00ff00;
  font-weight: bold;
  font-size: 11px;
  text-transform: uppercase;
}

.btn-clear {
  padding: 4px 8px;
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.3);
  color: #ff0000;
  border-radius: 4px;
  cursor: pointer;
  font-size: 10px;
}

.btn-clear:hover {
  background: rgba(255, 0, 0, 0.3);
}

.terminal-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  max-height: 400px;
}

.log-line {
  padding: 2px 0;
  display: flex;
  gap: 8px;
  line-height: 1.4;
}

.log-time {
  color: rgba(0, 255, 0, 0.6);
  font-size: 11px;
  min-width: 80px;
}

.log-message {
  color: #00ff00;
  flex: 1;
}

.log-line.info .log-message {
  color: #00ff00;
}

.log-line.success .log-message {
  color: #00ff00;
  font-weight: bold;
}

.log-line.warning .log-message {
  color: #ffff00;
}

.log-line.error .log-message {
  color: #ff0000;
  font-weight: bold;
}

.log-empty {
  color: rgba(0, 255, 0, 0.4);
  text-align: center;
  padding: 20px;
  font-style: italic;
}

/* Scrollbar styling */
.terminal-content::-webkit-scrollbar {
  width: 6px;
}

.terminal-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.5);
}

.terminal-content::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 0, 0.3);
  border-radius: 3px;
}

.terminal-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 0, 0.5);
}
</style>


