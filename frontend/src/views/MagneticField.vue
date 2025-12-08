<template>
  <div class="magnetic-field">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">
        🧲 Liquidity Heatmap
      </h1>
      <p class="text-terminal-green/70">
        Mapa de Calor de Liquidez - Visualize onde o dinheiro está esperando
      </p>
    </div>

    <LiquidityHeatmap :symbol="symbol" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LiquidityHeatmap from '@/components/magnetic/LiquidityHeatmap.vue'

const symbol = ref('BTCUSDT')
</script>

