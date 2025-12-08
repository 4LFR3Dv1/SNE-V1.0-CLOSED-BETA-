# ⚠️ IMPORTANTE: Reiniciar Flask para Aplicar Correção

## 🔄 CORREÇÃO APLICADA

Ajustei o endpoint `/api/signal` para usar **`score_combinado`** (mesmo que análise detalhada).

---

## 🚀 REINICIAR FLASK

**O Flask PRECISA ser reiniciado para aplicar a mudança!**

### **1. Parar Flask:**
- Pressione `Ctrl+C` no terminal onde Flask está rodando

### **2. Reiniciar:**
```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
source venv/bin/activate
python3 sne_radar_web.py
```

---

## ✅ DEPOIS DE REINICIAR

### **Teste o endpoint:**
```bash
curl "http://localhost:9999/api/signal?symbol=BTCUSDT&timeframe=1h"
```

**Agora deve retornar:**
- Score entre **0-10** (não mais negativo)
- **Mesmo score** que a análise detalhada mostra

### **Teste no Dashboard:**
1. Recarregue o dashboard (`http://localhost:5173/`)
2. Verifique o score exibido
3. Clique em uma oportunidade
4. **Scores devem ser iguais!**

---

**Após reiniciar, os scores devem estar consistentes!** ✅

