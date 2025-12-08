# 🤔 POR QUE PRECISA RODAR O FLASK?

## 📋 Explicação

O **frontend Vue.js** (Vite) é apenas a **interface visual**. Ele precisa de um **backend** para:

1. **APIs REST** - Análise técnica, sinais, dados de mercado
2. **WebSocket** - Updates em tempo real
3. **Processamento** - Cálculos pesados, análises

## 🏗️ Arquitetura

```
┌─────────────────────────────────┐
│   FRONTEND (Vue.js + Vite)      │
│   http://localhost:5173          │
│   ────────────────────────────   │
│   • Interface visual             │
│   • Componentes Vue              │
│   • Navegação                    │
└─────────────────────────────────┘
              ↓ HTTP/WebSocket
┌─────────────────────────────────┐
│   BACKEND (Flask)                │
│   http://localhost:9999          │
│   ────────────────────────────   │
│   • APIs REST (/api/*)           │
│   • WebSocket (/socket.io)       │
│   • Análise técnica               │
│   • Processamento de dados       │
└─────────────────────────────────┘
```

## 🔧 Por que `sne_radar_web.py`?

O arquivo `sne_radar_web.py` é o **servidor Flask completo** que:
- ✅ Serve as APIs que o frontend precisa
- ✅ Faz análises técnicas
- ✅ Processa dados de mercado
- ✅ Gerencia WebSocket para tempo real
- ✅ Serve o frontend buildado (quando buildado)

## ⚡ Alternativa: Servidor Flask Simples

Se você só quer testar o frontend sem todas as funcionalidades, podemos criar um servidor Flask mínimo apenas para APIs básicas.

---

**Resumo:** Frontend = Interface | Backend = Lógica e Dados

