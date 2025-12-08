# 🔍 DEBUG: Escala de Preço

## 🚨 PROBLEMA

**Sintomas:**
- ✅ Range de tempo está correto
- ✅ Dados foram adicionados
- ✅ Viewport contém os dados
- ❌ Apenas retângulo azulado (sem candles visíveis)

**Causa Provável:**
- **Escala de preço não inclui os valores dos candles**
- Os candles estão sendo plotados fora do range visível de preços

---

## 🔍 DIAGNÓSTICO

### **Verificar no Console:**

1. **Expandir objeto:** `💰 Valores de preço dos candles`
   - `minPrice`: ?
   - `maxPrice`: ?

2. **Expandir objeto:** `💰 Range de preço visível`
   - `from`: ?
   - `to`: ?

3. **Verificar:** `💰 Preços dos candles estão no range visível?`
   - `pricesInRange`: true ou false?

---

## ✅ SOLUÇÃO

### **Se `pricesInRange` for `false`:**

Os preços dos candles estão fora do range visível da escala. Isso significa que:
- Os candles estão sendo plotados em valores de preço que não estão visíveis
- A escala de preço precisa ser ajustada

### **Se `visiblePriceRange` for `null`:**

A escala de preço não tem range visível. Isso significa que:
- A biblioteca ainda não calculou o range
- Precisamos forçar o ajuste da escala

---

## 🛠️ CORREÇÃO SUGERIDA

Se os preços estiverem fora do range, vou ajustar a escala de preço para incluir todos os valores dos candles com uma margem.

---

**Status:** 🔍 Aguardando valores do console para diagnóstico preciso

