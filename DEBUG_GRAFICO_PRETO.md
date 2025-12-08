# 🔧 DEBUG: GRÁFICO PRETO COM DADOS

## 🐛 PROBLEMA

O gráfico está totalmente preto mesmo com dados sendo carregados corretamente (500 candles processados).

---

## ✅ CORREÇÕES APLICADAS

### **1. Logs Melhorados**
- ✅ Logs detalhados de cada etapa
- ✅ Validação de dados antes de adicionar
- ✅ Verificação de séries e chart

### **2. Inicialização Melhorada**
- ✅ Aguarda gráfico inicializar completamente
- ✅ Verifica se todas as séries existem antes de adicionar dados
- ✅ Retry automático se gráfico não inicializar

### **3. CSS Ajustado**
- ✅ Canvas forçado a ser visível
- ✅ Overflow hidden para evitar problemas de renderização

---

## 🧪 VERIFICAR NO CONSOLE

Após recarregar, você deve ver:

```
📊 Inicializando gráfico, largura: 1182
✅ Gráfico criado
📊 Carregando candles para: BTCUSDT 1h
📊 Resposta candles: {success: true, data: {...}}
📊 Candles processados: 500 primeiro: {time: 1762398000, ...}
📊 Adicionando dados ao gráfico...
   - Candles: 500
   - Volumes: 500
   ✅ Candles adicionados à série
   ✅ Volumes adicionados à série
   ✅ Viewport ajustado (fitContent)
✅ Dados adicionados ao gráfico com sucesso
```

---

## 🔍 POSSÍVEIS CAUSAS

### **1. Timestamp Inválido**
- Verificar se timestamps são números válidos
- Lightweight Charts espera segundos Unix (10 dígitos)

### **2. Dados Fora do Viewport**
- `fitContent()` deve ajustar automaticamente
- Verificar se há erro ao chamar `fitContent()`

### **3. Canvas Não Renderizando**
- Verificar se o canvas está visível no DOM
- Verificar se há erros de WebGL

### **4. Série Não Visível**
- Verificar se `candleSeries` está criada corretamente
- Verificar se há erros ao chamar `setData()`

---

## 🧪 TESTE MANUAL

No console do navegador, execute:

```javascript
// Verificar se o gráfico existe
console.log('Chart:', window.chart)

// Verificar dados
console.log('Candles:', candlesData)

// Tentar forçar redesenho
chart.timeScale().fitContent()
```

---

## 📝 PRÓXIMOS PASSOS

1. **Recarregar a página** (F5)
2. **Verificar logs** no console
3. **Verificar se há erros** no console
3. **Inspecionar elemento** do gráfico (ver se canvas existe)

---

**Status:** ✅ Logs melhorados - Verifique o console para mais detalhes!

