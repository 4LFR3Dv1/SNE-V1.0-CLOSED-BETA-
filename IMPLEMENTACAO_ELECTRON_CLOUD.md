# 🚀 GUIA RÁPIDO: IMPLEMENTAR ELECTRON + CLOUD

**Arquitetura:** Cliente Desktop (Electron) + Backend Cloud (Google Cloud Run)

---

## ⚡ INÍCIO RÁPIDO (5 minutos)

### **1. Configurar Electron no Frontend**

```bash
./setup_electron.sh
```

Isso vai:
- ✅ Instalar Electron e dependências
- ✅ Criar arquivos de configuração
- ✅ Adicionar scripts ao package.json

### **2. Testar em Desenvolvimento**

```bash
cd frontend
npm run electron:serve
```

Isso abre o app Electron conectado ao backend local.

### **3. Build Executável**

```bash
cd frontend
npm run electron:build
```

Resultado em `frontend/dist_electron/`:
- Windows: `SNE_RADAR Setup 1.0.0.exe`
- macOS: `SNE_RADAR-1.0.0.dmg`
- Linux: `SNE_RADAR-1.0.0.AppImage`

---

## 📋 CHECKLIST COMPLETO

### **FASE 1: Backend API** ✅

- [x] Criar `app/api/cloud_api.py` (API REST pura)
- [ ] Adicionar JWT authentication
- [ ] Testar endpoints com Postman
- [ ] Configurar CORS

### **FASE 2: Deploy Cloud** ☁️

- [ ] Criar projeto Google Cloud
- [ ] Build Docker image: `docker build -f Dockerfile.cloud -t gcr.io/PROJECT_ID/sne-api .`
- [ ] Push para Container Registry: `docker push gcr.io/PROJECT_ID/sne-api`
- [ ] Deploy no Cloud Run: `gcloud run deploy sne-api --image gcr.io/PROJECT_ID/sne-api --region us-central1 --allow-unauthenticated`
- [ ] Testar API pública: `curl https://api.sne-radar.com/api/v1/health`

### **FASE 3: Frontend Electron** 🖥️

- [x] Criar `frontend/src/background.js`
- [x] Criar `frontend/src/preload.js`
- [ ] Executar `./setup_electron.sh`
- [ ] Atualizar `frontend/src/services/api.js` para usar API cloud
- [ ] Testar: `npm run electron:serve`

### **FASE 4: Build e Distribuição** 📦

- [ ] Criar ícones (`.ico`, `.icns`, `.png`)
- [ ] Build: `npm run electron:build`
- [ ] Testar instalação
- [ ] Distribuir executáveis

---

## 🔧 COMANDOS ÚTEIS

### **Backend (Local)**

```bash
# Rodar Flask local
export FLASK_APP=app.main:app
export FLASK_ENV=development
flask run --port 5000

# Ou usar gunicorn
gunicorn --bind 0.0.0.0:5000 app.main:app
```

### **Frontend (Electron)**

```bash
cd frontend

# Desenvolvimento
npm run electron:serve

# Build produção
npm run electron:build

# Build específico
npm run electron:build:win
npm run electron:build:mac
npm run electron:build:linux
```

### **Cloud Run**

```bash
# Build e push
docker build -f Dockerfile.cloud -t gcr.io/PROJECT_ID/sne-api .
docker push gcr.io/PROJECT_ID/sne-api

# Deploy
gcloud run deploy sne-api \
  --image gcr.io/PROJECT_ID/sne-api \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

# Ver logs
gcloud run services logs read sne-api --region us-central1
```

---

## 🔐 CONFIGURAR AUTENTICAÇÃO JWT

### **1. Instalar dependências:**

```bash
pip install flask-jwt-extended
```

### **2. Configurar no `app/__init__.py`:**

```python
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'change-me-in-production')
    jwt = JWTManager(app)
    # ...
```

### **3. Usar no frontend:**

```javascript
// Login
const response = await api.post('/auth/login', { username, password })
localStorage.setItem('jwt_token', response.data.token)

// Requisições autenticadas (já configurado no api.js)
const data = await api.get('/trading/positions')
```

---

## 📊 ESTRUTURA FINAL

```
SNE_BACKUP_CLEAN/
├── app/
│   └── api/
│       └── cloud_api.py          # ✅ API REST pura
├── frontend/
│   ├── src/
│   │   ├── background.js         # ✅ Electron main process
│   │   ├── preload.js            # ✅ Preload script
│   │   └── services/
│   │       └── api.js            # ✅ Cliente API
│   ├── dist_electron/            # 📦 Executáveis gerados
│   └── package.json              # ✅ Scripts Electron
├── Dockerfile.cloud              # ✅ Docker para Cloud Run
└── setup_electron.sh             # ✅ Script de setup
```

---

## 🎯 PRÓXIMOS PASSOS

1. **Executar setup:** `./setup_electron.sh`
2. **Testar localmente:** `cd frontend && npm run electron:serve`
3. **Deploy backend:** Seguir FASE 2
4. **Build executável:** `npm run electron:build`
5. **Distribuir:** Enviar executáveis para usuários

---

**Status:** ✅ Estrutura Pronta - Próximo: Executar Setup


