<template>
  <div class="radar-legend">
    <h3 class="legend-title">Legenda</h3>
    
    <div class="legend-section">
      <div class="legend-item">
        <div class="legend-color" style="background: #00ff00;"></div>
        <span>BUY (Compra)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #ff0000;"></div>
        <span>SELL (Venda)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #ffff00;"></div>
        <span>NEUTRAL (Neutro)</span>
      </div>
    </div>
    
    <div class="legend-section">
      <h4 class="legend-subtitle">Zonas de Qualidade</h4>
      <div class="legend-item">
        <div class="legend-ring ring-1"></div>
        <span>Score 8-10 (Excelente)</span>
      </div>
      <div class="legend-item">
        <div class="legend-ring ring-2"></div>
        <span>Score 6-8 (Bom)</span>
      </div>
      <div class="legend-item">
        <div class="legend-ring ring-3"></div>
        <span>Score 4-6 (Moderado)</span>
      </div>
      <div class="legend-item">
        <div class="legend-ring ring-4"></div>
        <span>Score 0-4 (Baixo)</span>
      </div>
    </div>
    
    <div class="legend-section">
      <div class="legend-item">
        <div class="legend-center"></div>
        <span>Centro = Melhor Oportunidade</span>
      </div>
      <div class="legend-item">
        <div class="legend-sweep"></div>
        <span>Varredura = Atualização</span>
      </div>
    </div>
  </div>
</template>

<script setup>
// Componente de legenda simples
</script>

<style scoped>
.radar-legend {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid #00ff0030;
  border-radius: 6px;
  padding: 12px; /* Reduzido de 16px */
  width: 100%;
  max-width: 240px;
}

.legend-title {
  color: #00ff00;
  font-size: 12px; /* Reduzido de 16px */
  font-weight: 600;
  margin-bottom: 10px; /* Reduzido de 12px */
  border-bottom: 1px solid #00ff0030;
  padding-bottom: 6px; /* Reduzido de 8px */
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.legend-section {
  margin-bottom: 12px; /* Reduzido de 16px */
}

.legend-section:last-child {
  margin-bottom: 0;
}

.legend-subtitle {
  color: #00ff0070;
  font-size: 10px; /* Reduzido de 12px */
  margin-bottom: 6px; /* Reduzido de 8px */
  text-transform: uppercase;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.05em;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px; /* Reduzido de 8px */
  margin-bottom: 6px; /* Reduzido de 8px */
  font-size: 10px; /* Reduzido de 12px */
  color: #00ff0070;
  font-family: 'JetBrains Mono', monospace;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid #00ff0030;
}

.legend-ring {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid #00ff0030;
  background: transparent;
}

.ring-1 {
  border-color: #00ff00;
}

.ring-2 {
  border-color: #00ff0070;
}

.ring-3 {
  border-color: #00ff0040;
}

.ring-4 {
  border-color: #00ff0020;
}

.legend-center {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px dashed #00ff00;
  background: transparent;
}

.legend-sweep {
  width: 16px;
  height: 2px;
  background: #00ff00;
  position: relative;
}

.legend-sweep::after {
  content: '';
  position: absolute;
  right: -4px;
  top: -2px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00ff00;
}
</style>

