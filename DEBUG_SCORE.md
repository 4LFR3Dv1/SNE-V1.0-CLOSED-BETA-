# 🔍 DEBUG: Inconsistência de Score

## 🎯 PROBLEMA

Endpoint `/api/signal` retorna score diferente da análise detalhada.

---

## 📊 O QUE ESTÁ ACONTECENDO

### **Dashboard mostra:**
- Score: **-2** (ou negativo)

### **Análise detalhada mostra:**
- Score: **7.0/10**

---

## 🔧 CORREÇÃO APLICADA

Ajustei o endpoint para usar **`score_combinado`** da síntese (mesmo que análise detalhada).

### **Lógica de Prioridade:**

1. ✅ `sintese.score_combinado` (prioridade máxima)
2. ✅ `sintese.score_confianca` (fallback)
3. ✅ `sintese.score` (fallback)
4. ✅ `confluencia.score` (último recurso, normalizado)

---

## ⚠️ IMPORTANTE

**O Flask PRECISA ser reiniciado para aplicar a correção!**

```bash
# Parar Flask (Ctrl+C)
# Reiniciar:
python3 sne_radar_web.py
```

---

## ✅ TESTE APÓS REINICIAR

```bash
curl "http://localhost:9999/api/signal?symbol=BTCUSDT&timeframe=1h"
```

**Resultado esperado:**
```json
{
  "score": 7.0,
  "signal": "SELL",
  ...
}
```

---

**Reinicie o Flask e teste novamente!**

