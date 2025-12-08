# 🚀 SNE FRONTEND - Vue.js 3

Frontend moderno para o SNE RADAR usando Vue.js 3 + Vite.

## 📋 Pré-requisitos

- Node.js >= 18.0.0
- npm >= 9.0.0

## 🛠️ Setup

### 1. Instalar Dependências

```bash
cd frontend
npm install
```

### 2. Desenvolvimento

```bash
# Terminal 1: Frontend (Vite dev server)
cd frontend
npm run dev
# Acessar: http://localhost:5173

# Terminal 2: Backend (Flask)
python3 sne_radar_web.py
# Acessar: http://localhost:9999
```

O Vite está configurado para fazer proxy das requisições `/api` e `/socket.io` para o Flask.

### 3. Build para Produção

```bash
cd frontend
npm run build
```

Isso gera os arquivos em `frontend/dist/` que serão servidos pelo Flask.

### 4. Testar Build Localmente

```bash
# Build frontend
cd frontend
npm run build

# Rodar Flask (já serve o frontend automaticamente)
python3 sne_radar_web.py
# Acessar: http://localhost:9999
```

## 📁 Estrutura

```
frontend/
├── src/
│   ├── components/    # Componentes Vue
│   ├── views/         # Páginas
│   ├── stores/        # Pinia stores
│   ├── services/      # API, WebSocket
│   ├── router/        # Vue Router
│   └── assets/        # CSS, imagens
├── public/            # Arquivos estáticos
├── dist/              # Build output (gitignored)
└── package.json
```

## 🚀 Deploy

```bash
./deploy_frontend.sh
```

Ou manualmente:

```bash
cd frontend
npm run build
cd ..
gcloud run deploy sne-web --source . --region europe-west1 --project sne-v1
```

## 📚 Tecnologias

- **Vue.js 3** - Framework frontend
- **Vite** - Build tool
- **Pinia** - State management
- **Vue Router** - Roteamento
- **Tailwind CSS** - Estilização
- **Axios** - HTTP client
- **Socket.IO Client** - WebSocket
- **Lightweight Charts** - Gráficos trading
- **Three.js** - Visualização 3D

## 🎯 Status

✅ Estrutura base criada
✅ Componentes básicos implementados
✅ Integração com Flask configurada
⏳ Funcionalidades avançadas em desenvolvimento

