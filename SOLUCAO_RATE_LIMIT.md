# ✅ SOLUÇÃO DEFINITIVA: Rate Limit 429

## 🎯 PROBLEMA

Flask-Limiter está bloqueando requisições com **429 (TOO MANY REQUESTS)** porque:
- Limite padrão: **50 requisições por hora**
- Dashboard faz muitas requisições simultâneas
- Limite global aplicado a todas as rotas

---

## ✅ CORREÇÕES APLICADAS

### **1. Limite Aumentado no Código:**

```python
# Limites em desenvolvimento:
default_limits = ["5000 per day", "500 per hour"]  # Muito mais alto!

# Limite específico para /api/signal:
@limiter.limit("500 per hour")  # Em desenvolvimento
```

### **2. IMPORTANTE: Reiniciar Flask!**

As mudanças só têm efeito após **reiniciar o Flask**:

```bash
# 1. Parar Flask (Ctrl+C no terminal ou):
kill -9 77204  # Substitua pelo PID do Flask

# 2. Reiniciar Flask:
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
source venv/bin/activate
python3 sne_radar_web.py
```

---

## 🔧 ALTERNATIVA: Desabilitar Rate Limit Temporariamente

Se quiser desabilitar completamente em desenvolvimento:

```python
# Em sne_radar_web.py, linha ~116:
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["999999 per hour"] if not IS_PRODUCTION else ["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# E comentar o decorator na rota:
# @limiter.limit("500 per hour")  # Temporariamente desabilitado
```

---

## 📊 NOVOS LIMITES (Após Reiniciar)

| Ambiente | Limite Padrão | Limite /api/signal |
|----------|---------------|-------------------|
| **Desenvolvimento** | 500/hour | 500/hour |
| **Produção** | 50/hour | 100/hour |

---

## 🧪 TESTE

Após reiniciar Flask:

1. Recarregar página do dashboard
2. Verificar console - não deve ter mais erros 429
3. Oportunidades devem carregar normalmente

---

## ⚠️ NOTA

Se ainda houver erros 429 após reiniciar:
- Verificar se Flask realmente foi reiniciado
- Ver logs do Flask para confirmar novos limites
- Pode ser que o limite anterior ainda esteja "pendurado" na memória

**Solução:** Aguardar 1 hora ou reiniciar completamente o sistema.

---

**Status:** ✅ Correções aplicadas - **REINICIAR FLASK PARA APLICAR**

