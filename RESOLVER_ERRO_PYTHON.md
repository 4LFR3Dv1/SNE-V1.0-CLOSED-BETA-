# 🔧 RESOLVER ERRO: ModuleNotFoundError

## ❌ Erro Atual

```
ModuleNotFoundError: No module named 'requests'
```

**Causa:** Dependências Python não estão instaladas.

---

## ✅ Solução 1: Instalar Todas as Dependências (Recomendado)

### Opção A: Script Automático

```bash
./instalar_dependencias.sh
```

### Opção B: Manual

```bash
pip3 install -r requirements.txt
```

**Tempo:** ~2-5 minutos (dependendo da conexão)

**Nota:** Se der erro de permissão, use:
```bash
pip3 install --user -r requirements.txt
```

---

## ✅ Solução 2: Servidor Flask Simples (Para Testar Frontend)

Se você só quer **testar o frontend** sem instalar todas as dependências pesadas:

```bash
# Instalar apenas o mínimo
pip3 install flask flask-socketio flask-cors

# Rodar servidor simples
python3 server_simples.py
```

**Vantagem:** Instalação rápida (~30 segundos)  
**Desvantagem:** APIs retornam dados mock (não reais)

---

## 🎯 Qual Escolher?

### Use Solução 1 se:
- ✅ Quer funcionalidades completas
- ✅ Vai desenvolver o sistema
- ✅ Precisa de análises reais

### Use Solução 2 se:
- ✅ Só quer testar o frontend
- ✅ Não precisa de análises reais agora
- ✅ Quer algo rápido

---

## 📋 Depois de Instalar

### Com Dependências Completas:
```bash
python3 sne_radar_web.py
```

### Com Servidor Simples:
```bash
python3 server_simples.py
```

Ambos vão rodar em **http://localhost:9999**

---

**Recomendação:** Use Solução 1 para desenvolvimento completo, ou Solução 2 para testar rapidamente o frontend.

