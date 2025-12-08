# 🔍 DEBUG: Gráfico Não Visível

## 📊 **SITUAÇÃO ATUAL**

**Logs confirmam:**
- ✅ Canvas existe: `1182x472`
- ✅ Dados válidos: `500 candles`
- ✅ Range de preço: `minPrice: 0.3876, maxPrice: 0.6069`
- ✅ Viewport contém os dados: `true`
- ✅ Timestamps corretos: `1762455600` a `1764252000` (segundos)

**PROBLEMA:** Gráfico não aparece (apenas retângulo azulado).

---

## 🔍 **DIAGNÓSTICO**

### **Possíveis Causas:**

1. **Escala de Preço Não Ajustando**
   - Mesmo com `autoScale: true`, pode não estar funcionando
   - Valores pequenos (0.38-0.60) podem estar causando problemas

2. **Candles Renderizados Mas Invisíveis**
   - Cores muito escuras
   - Z-index/Overflow
   - Canvas sendo desenhado mas não visível

3. **Série Não Conectada Corretamente**
   - Série pode não estar anexada ao gráfico
   - Dados podem estar sendo adicionados antes da série estar pronta

---

## ✅ **CORREÇÕES APLICADAS**

### **1. Cores Mais Visíveis**
```javascript
upColor: '#26a69a',      // Verde mais visível
downColor: '#ef5350',    // Vermelho mais visível
```

### **2. Precisão Ajustada para Valores Pequenos**
```javascript
priceFormat: {
  type: 'price',
  precision: 4,        // ✅ Aumentar precisão (era 2)
  minMove: 0.0001      // ✅ Ajustar minMove (era 0.01)
}
```

### **3. Forçar Escala de Preço ANTES de fitContent**
```javascript
// Forçar escala de preço ANTES de fitContent
const priceScale = chart.priceScale('right')
priceScale.applyOptions({
  autoScale: true,
  scaleMargins: {
    top: 0.2,    // ✅ Aumentar margem
    bottom: 0.2
  }
})
```

### **4. Background Sólido (não transparente)**
```javascript
background: { type: ColorType.Solid, color: '#131722' }
```

---

## 🧪 **PRÓXIMOS PASSOS**

Se ainda não funcionar:

1. **Verificar no console:**
   - Quantos candles foram realmente adicionados?
   - Há algum erro após `setData`?
   - A série existe e está conectada?

2. **Testar com dados manuais simples:**
   ```javascript
   const testData = [
     { time: 1762455600, open: 0.4, high: 0.5, low: 0.35, close: 0.45 },
     { time: 1762459200, open: 0.45, high: 0.5, low: 0.4, close: 0.42 }
   ]
   candleSeries.setData(testData)
   ```

3. **Verificar se há conflito com outras séries:**
   - Volume pode estar sobrepondo
   - Indicadores podem estar causando problema

---

**Status:** ✅ Correções aplicadas. Aguardando teste.



