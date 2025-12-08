# 🔄 REINICIAR FLASK PARA APLICAR MUDANÇAS

## ⚠️ IMPORTANTE

As alterações no rate limit **só terão efeito após reiniciar o Flask**.

---

## 🚀 COMO REINICIAR

### **1. Parar Flask atual:**
```bash
# Encontrar processo do Flask
lsof -i :9999

# Matar processo (substitua PID pelo número do processo)
kill -9 <PID>
```

Ou simplesmente: `Ctrl+C` no terminal onde o Flask está rodando.

### **2. Reiniciar Flask:**
```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
source venv/bin/activate
python3 sne_radar_web.py
```

---

## ✅ MUDANÇAS APLICADAS

1. **Limite padrão aumentado em desenvolvimento:**
   - Antes: 50 por hora
   - Depois: 200 por hora (em desenvolvimento)

2. **Limite específico para `/api/signal`:**
   - 100 requisições por hora

3. **Limite específico para `/api/analyze`:**
   - 50 requisições por hora

---

## 📊 NOVOS LIMITES

| Rota | Limite |
|------|--------|
| `/api/signal` | 100/hour |
| `/api/analyze` | 50/hour |
| Outras rotas | 200/hour (dev) ou 50/hour (prod) |

---

**Após reiniciar:** O dashboard deve funcionar sem erros 429!

