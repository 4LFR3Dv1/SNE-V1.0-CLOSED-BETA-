# ✅ CORREÇÃO: Filtro de Score Bloqueando Oportunidades

## 🎯 PROBLEMA IDENTIFICADO

- **Oportunidades carregadas:** 5 ✅
- **Oportunidades filtradas:** 0 ❌

O filtro de score mínimo estava configurado como **"Score ≥ 0"** por padrão, mas as oportunidades têm **scores negativos** (ex: -4.0), então todas eram filtradas!

---

## ✅ CORREÇÃO APLICADA

### **1. Mudado valor padrão do filtro:**
- ❌ Antes: `filterMinScore = ref('0')` (bloqueava scores negativos)
- ✅ Agora: `filterMinScore = ref('-10')` (aceita todos os scores)

### **2. Adicionado opção "Todos os Scores":**
- ✅ Opção no dropdown: "Todos os Scores" (value: -10)
- ✅ Aceita scores negativos e positivos

### **3. Ajustada lógica de filtragem:**
- ✅ Quando minScore é -10, aceita TODOS os scores
- ✅ Quando minScore é outro valor, filtra normalmente

---

## 📊 RESULTADO ESPERADO

Agora você deve ver:
- ✅ **Total de oportunidades:** 5
- ✅ **Oportunidades filtradas:** 5 (todas visíveis)
- ✅ Lista completa de oportunidades exibida

---

## 🔄 TESTE

1. **Recarregue a página** (F5 ou Ctrl+R)
2. **Verifique:**
   - As 5 oportunidades devem aparecer
   - O filtro de score deve estar em "Todos os Scores"
   - Todos os símbolos devem estar visíveis

---

**Problema resolvido!** As oportunidades agora devem aparecer. 🎉

