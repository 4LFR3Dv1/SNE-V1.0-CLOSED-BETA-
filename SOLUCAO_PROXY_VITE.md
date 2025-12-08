# 🔧 SOLUÇÃO: Problema com Proxy do Vite

## 🐛 PROBLEMA

O gráfico está retornando **HTML do Vue.js** em vez de **imagem PNG**. Isso acontece porque:

1. ✅ A rota `/api/v1/chart-image` está definida no Flask (linha 2005)
2. ✅ A rota catch-all está DEPOIS (linha 2204)
3. ❌ **Mas o Vite proxy está interceptando e retornando HTML**

---

## 🎯 SOLUÇÃO

### **Opção 1: Acessar Flask Diretamente (Mais Simples)**

Quando em desenvolvimento com Vite, acessar o Flask diretamente em `http://localhost:9999` em vez de usar o proxy.

**No componente Vue:**
```javascript
const getChartUrl = () => {
  const timestamp = new Date().getTime()
  // Em desenvolvimento: acessar Flask diretamente
  // Em produção: usar URL relativa
  const isDev = import.meta.env.DEV
  const baseUrl = isDev ? 'http://localhost:9999' : ''
  const url = `${baseUrl}/api/v1/chart-image?symbol=${props.symbol}&interval=${props.timeframe}&t=${timestamp}`
  return url
}
```

### **Opção 2: Ajustar Proxy do Vite**

Melhorar configuração do proxy para garantir que funcione corretamente:

```javascript
// frontend/vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:9999',
    changeOrigin: true,
    secure: false,
    rewrite: (path) => path, // Não reescrever o path
    configure: (proxy, _options) => {
      proxy.on('proxyReq', (proxyReq, req, res) => {
        console.log(`🔄 Proxying: ${req.method} ${req.url}`)
      })
      proxy.on('proxyRes', (proxyRes, req, res) => {
        console.log(`✅ Response: ${proxyRes.statusCode} for ${req.url}`)
      })
    }
  }
}
```

### **Opção 3: Build Frontend e Servir pelo Flask**

Buildar o frontend e servir tudo pelo Flask (sem Vite dev server):

```bash
cd frontend
npm run build
cd ..
python3 sne_radar_web.py
# Acessar: http://localhost:9999
```

---

## 🚀 IMPLEMENTAÇÃO RÁPIDA

A solução mais rápida é ajustar o componente Vue para acessar o Flask diretamente em desenvolvimento:

```vue
// frontend/src/components/charts/SimpleChart.vue

const getChartUrl = () => {
  const timestamp = new Date().getTime()
  // Detectar se está em desenvolvimento (Vite dev server)
  const isDev = import.meta.env.DEV
  // Em dev: acessar Flask diretamente (evita problemas de proxy)
  // Em prod: usar URL relativa (servido pelo mesmo servidor)
  const baseUrl = isDev ? 'http://localhost:9999' : ''
  const url = `${baseUrl}/api/v1/chart-image?symbol=${props.symbol}&interval=${props.timeframe}&t=${timestamp}`
  console.log('📊 Carregando gráfico da URL:', url)
  return url
}
```

**Vantagens:**
- ✅ Funciona imediatamente
- ✅ Evita problemas de proxy
- ✅ CORS já está configurado
- ✅ Em produção funciona normalmente

---

**Aplicar esta correção agora?**

