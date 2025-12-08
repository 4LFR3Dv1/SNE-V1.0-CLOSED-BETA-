# 🚀 COMO INICIAR O FLASK

## ⚠️ PROBLEMA

O gráfico não funciona porque o **Flask não está rodando** na porta 9999.

---

## ✅ SOLUÇÃO

### **1. Iniciar o Flask**

Abra um terminal e execute:

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
python3 sne_radar_web.py
```

**Deve mostrar:**
```
🚀 Iniciando SNE Radar Web...
✅ Banco de dados inicializado
 * Running on http://127.0.0.1:9999
```

---

### **2. Manter Flask rodando**

**IMPORTANTE:** Deixe este terminal aberto enquanto usa o frontend!

O Flask precisa estar rodando para:
- ✅ API `/api/v1/candles` funcionar
- ✅ API `/api/analyze` funcionar
- ✅ API `/api/chart/levels` funcionar

---

### **3. Iniciar o Frontend (Vite)**

Em **outro terminal**, execute:

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm run dev
```

**Deve mostrar:**
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

---

## 📋 RESUMO

### **Terminal 1: Flask (Backend)**
```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
python3 sne_radar_web.py
# Deve mostrar: Running on http://127.0.0.1:9999
```

### **Terminal 2: Vite (Frontend)**
```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm run dev
# Deve mostrar: Local: http://localhost:5173/
```

---

## 🧪 VERIFICAR SE ESTÁ FUNCIONANDO

### **1. Verificar Flask**
```bash
# Em outro terminal:
curl http://localhost:9999/health

# Deve retornar JSON, não HTML
```

### **2. Verificar no navegador**
- Acesse: http://localhost:5173
- Abra DevTools (F12) → Network
- Faça uma análise
- Verifique se `/api/v1/candles` retorna JSON (não HTML)

---

## 🔧 SCRIPT PARA INICIAR TUDO

Crie um script `rodar_tudo.sh`:

```bash
#!/bin/bash

# Terminal 1: Flask
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
python3 sne_radar_web.py &
FLASK_PID=$!

# Terminal 2: Vite
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm run dev &
VITE_PID=$!

echo "✅ Flask rodando (PID: $FLASK_PID)"
echo "✅ Vite rodando (PID: $VITE_PID)"
echo "Pressione Ctrl+C para parar"

wait
```

---

## ⚠️ PROBLEMAS COMUNS

### **1. Porta 9999 já em uso**
```bash
# Verificar o que está usando:
lsof -i :9999

# Matar processo se necessário:
kill -9 <PID>
```

### **2. Erro de módulo Python**
```bash
# Instalar dependências:
pip3 install -r requirements.txt
```

### **3. Erro de autenticação**
- Faça login no sistema primeiro
- Verifique cookies no navegador (DevTools → Application → Cookies)

---

**Status:** ✅ Instruções completas - Inicie o Flask e teste novamente!

