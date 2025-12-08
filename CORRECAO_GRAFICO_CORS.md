# 🔧 CORREÇÃO: Erro no Gráfico - CORS e HTML em vez de Imagem

## 🐛 PROBLEMAS IDENTIFICADOS

1. **CORS Error**: Frontend (localhost:5173) não consegue acessar backend (localhost:9999)
2. **HTML em vez de Imagem**: Servidor retorna HTML ao invés de PNG
3. **Content-Type errado**: Retorna `text/html` ao invés de `image/png`
4. **Rota catch-all interceptando**: A rota `/<path:path>` está capturando antes do endpoint de API

---

## 🔍 DIAGNÓSTICO

### **Erro no Console:**
```
Origin http://localhost:5173 is not allowed by Access-Control-Allow-Origin
Status code: 200
Content-Type: "text/html"
Resposta: "<!DOCTYPE html>..."
```

### **Causa Raiz:**
1. Flask não tem CORS configurado para requisições de imagem
2. Rota catch-all está interceptando `/api/v1/chart-image`
3. Vite proxy pode não estar funcionando corretamente para imagens

---

## ✅ SOLUÇÕES

### **SOLUÇÃO 1: Adicionar CORS ao Flask (Rápida)**

Modificar `sne_radar_web.py` para adicionar headers CORS:

```python
from flask_cors import CORS

# Após criar app
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:9999"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})
```

**Ou manualmente adicionar headers:**

```python
@app.after_request
def after_request(response):
    """Adiciona headers CORS"""
    if request.path.startswith('/api/'):
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
```

---

### **SOLUÇÃO 2: Verificar Ordem das Rotas**

A rota `/api/v1/chart-image` deve estar **ANTES** da rota catch-all:

```python
# ✅ CORRETO: API routes ANTES da catch-all
@app.route('/api/v1/chart-image')  # Linha 1991
def api_v1_chart_image():
    # ...

@app.route('/', defaults={'path': ''})  # Linha 2183 - DEPOIS das APIs
@app.route('/<path:path>')
def serve_frontend(path):
    # ...
```

**Verificar se está nesta ordem!**

---

### **SOLUÇÃO 3: Usar Vite Proxy (Recomendado)**

O Vite já tem proxy configurado, mas pode precisar ajustar para imagens:

```javascript
// frontend/vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:9999',
        changeOrigin: true,
        secure: false,
        // Adicionar para imagens
        configure: (proxy, _options) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            // Garantir que headers CORS estão presentes
            proxyRes.headers['Access-Control-Allow-Origin'] = '*';
          });
        }
      }
    }
  }
})
```

---

### **SOLUÇÃO 4: Ajustar Componente Vue**

O componente `SimpleChart.vue` pode precisar ajustes:

```javascript
// Usar URL relativa para usar proxy do Vite
const getChartUrl = () => {
  const timestamp = new Date().getTime()
  // ✅ Usar URL relativa (usa proxy do Vite)
  const url = `/api/v1/chart-image?symbol=${props.symbol}&interval=${props.timeframe}&t=${timestamp}`
  console.log('📊 Carregando gráfico da URL:', url)
  return url
}
```

**Remover URL absoluta com `http://localhost:9999`**

---

## 🚀 CORREÇÃO COMPLETA

### **Passo 1: Adicionar CORS ao Flask**

```python
# Adicionar no topo do sne_radar_web.py
from flask_cors import CORS

# Após linha 125 (após criar socketio)
CORS(app, 
     resources={
         r"/api/*": {
             "origins": ["http://localhost:5173", "http://localhost:9999"],
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type"],
             "supports_credentials": True
         }
     })

# Ou adicionar manualmente com after_request
@app.after_request
def after_request(response):
    """Adiciona headers CORS para todas as rotas /api/*"""
    if request.path.startswith('/api/'):
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:5173', 'http://localhost:9999']:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, HEAD'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
```

---

### **Passo 2: Garantir que Endpoint Retorna Imagem**

```python
@app.route('/api/v1/chart-image')
# @login_required  # Já está comentado
def api_v1_chart_image():
    # ... código existente ...
    
    # IMPORTANTE: Garantir headers corretos
    response = make_response(image_bytes)
    response.headers['Content-Type'] = 'image/png'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Content-Length'] = str(len(image_bytes))
    
    # Adicionar CORS headers manualmente
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response
```

---

### **Passo 3: Ajustar Componente Vue**

```vue
// frontend/src/components/charts/SimpleChart.vue

// Alterar getChartUrl() para usar URL relativa
const getChartUrl = () => {
  const timestamp = new Date().getTime()
  // ✅ URL relativa usa proxy do Vite automaticamente
  const url = `/api/v1/chart-image?symbol=${props.symbol}&interval=${props.timeframe}&t=${timestamp}`
  console.log('📊 Carregando gráfico da URL:', url)
  return url
}
```

---

### **Passo 4: Verificar Ordem das Rotas**

Garantir que a rota de API está ANTES da catch-all:

```python
# ✅ Ordem CORRETA:

# 1. APIs primeiro (linha ~1991)
@app.route('/api/v1/chart-image')
def api_v1_chart_image():
    # ...

# 2. Outras rotas de API
@app.route('/api/analyze')
# ...

# 3. Catch-all por último (linha ~2183)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Verificar se NÃO é rota de API
    if path.startswith('api/'):
        return jsonify({"error": "API route not found"}), 404
    # ...
```

---

## 🧪 TESTAR

### **1. Testar Endpoint Diretamente:**

```bash
# No navegador ou curl
curl -I http://localhost:9999/api/v1/chart-image?symbol=BTCUSDT&interval=1h

# Deve retornar:
# Content-Type: image/png
# Access-Control-Allow-Origin: http://localhost:5173
```

### **2. Testar via Vite Proxy:**

```bash
# Com Vite rodando em localhost:5173
curl -I http://localhost:5173/api/v1/chart-image?symbol=BTCUSDT&interval=1h
```

### **3. Testar no Componente Vue:**

```javascript
// No console do navegador
fetch('/api/v1/chart-image?symbol=BTCUSDT&interval=1h')
  .then(r => {
    console.log('Status:', r.status)
    console.log('Content-Type:', r.headers.get('content-type'))
    return r.blob()
  })
  .then(blob => {
    console.log('Blob size:', blob.size)
    console.log('É imagem?', blob.type.startsWith('image/'))
  })
```

---

## 📋 CHECKLIST DE CORREÇÃO

- [ ] Adicionar CORS headers ao Flask
- [ ] Verificar ordem das rotas (API antes de catch-all)
- [ ] Ajustar componente Vue para usar URL relativa
- [ ] Testar endpoint diretamente
- [ ] Testar via proxy do Vite
- [ ] Verificar Content-Type da resposta
- [ ] Verificar se imagem é gerada corretamente

---

## 🎯 PRIORIDADE

**URGENTE:** Este erro impede o gráfico de funcionar completamente!

1. **Adicionar CORS** - Mais rápido
2. **Ajustar componente Vue** - Usar URL relativa
3. **Verificar ordem de rotas** - Garantir que não está sendo interceptada

---

**Documento criado:** Janeiro 2025  
**Status:** 🔴 Aguardando correção

