# 🌐 DASHBOARDS WEB DISPONÍVEIS - SNE RADAR

**Data:** Janeiro 2025  
**Status:** ✅ Todos funcionais

---

## 📊 RESUMO EXECUTIVO

O sistema SNE RADAR possui **MÚLTIPLOS dashboards web** funcionais, cada um com propósitos específicos:

1. ✅ **Frontend Vue.js 3** (Moderno, SPA)
2. ✅ **Dashboard Terminal** (Comandos interativos)
3. ✅ **Dashboard Profissional** (Funcionalidades avançadas)
4. ✅ **Dashboard Admin** (Administração)
5. ✅ **Páginas de Autenticação** (Login/Register)

---

## 🎯 DASHBOARD 1: Frontend Vue.js 3 (Principal)

### **Acesso:**
- **URL:** `http://localhost:9999/` (root)
- **Porta:** 9999
- **Requer:** Frontend buildado (`frontend/dist/`)

### **Tecnologias:**
- Vue.js 3 (Composition API)
- Vite (Build tool)
- Pinia (State management)
- Vue Router (Roteamento)
- Tailwind CSS (Estilização)
- Lightweight Charts (Gráficos)
- Three.js (Visualização 3D)

### **Como Acessar:**

#### **Opção A: Desenvolvimento (Vite Dev Server)**
```bash
# Terminal 1: Frontend
cd frontend
npm run dev
# Acessar: http://localhost:5173

# Terminal 2: Backend Flask
python3 sne_radar_web.py
# Backend: http://localhost:9999
```

**Proxy configurado:** Vite faz proxy de `/api` e `/socket.io` para Flask

#### **Opção B: Produção (Flask serve frontend)**
```bash
# Build frontend primeiro
cd frontend
npm run build

# Rodar Flask (serve automaticamente o frontend)
python3 sne_radar_web.py
# Acessar: http://localhost:9999
```

### **Páginas Disponíveis (Vue Router):**

```
/                    → Dashboard.vue (Principal)
/analysis            → Analysis.vue (Análise técnica)
/backtesting         → Backtesting.vue (Backtesting visual)
/magnetic            → MagneticField.vue (Campo magnético 3D)
/settings            → Settings.vue (Configurações)
```

### **Funcionalidades:**
- ✅ Dashboard interativo em tempo real
- ✅ Gráficos TradingView integrados
- ✅ Análise multi-timeframe visual
- ✅ Visualização 3D do campo magnético
- ✅ Backtesting com interface visual
- ✅ Sistema de alertas
- ✅ WebSocket em tempo real
- ✅ Responsivo (mobile/desktop)

### **Componentes Principais:**
- `Dashboard.vue` - Dashboard principal
- `Analysis.vue` - Análise técnica
- `Backtesting.vue` - Backtesting visual
- `MagneticField.vue` - Visualização 3D
- `TradingChart.vue` - Gráficos de trading
- `SimpleChart.vue` - Gráficos simples

---

## 🖥️ DASHBOARD 2: Terminal Interativo

### **Acesso:**
- **URL:** `http://localhost:9999/dashboard` ou `http://localhost:9999/terminal`
- **Template:** `templates/dashboard_terminal.html`
- **Requer Login:** ✅ Sim (`@login_required`)

### **Como Acessar:**

```bash
# 1. Rodar Flask
python3 sne_radar_web.py

# 2. Acessar
http://localhost:9999/dashboard
# ou
http://localhost:9999/terminal

# 3. Login
Usuário: admin
Senha: admin
```

### **Funcionalidades:**

#### **🔍 ANÁLISE TÉCNICA:**
- **🔍 Scanner** - Scanner técnico completo
- **🌍 Contexto** - Contexto de mercado macro
- **📊 Multi-Pair** - Análise multi-pair
- **🧲 Campo Magnético** - Visualização campo magnético

#### **📊 RELATÓRIOS:**
- **📄 RT** - Relatório técnico completo
- **📈 RH** - Relatório horário
- **📅 RD** - Relatório diário
- **📅 RS** - Relatório semanal

#### **🎛️ OUTROS:**
- Interface visual com cards clicáveis
- Painel de output para resultados
- Botões de ação (Limpar, Atualizar, Sair)
- Mobile-responsive
- Execução de comandos sob demanda (AJAX)

### **Endpoints API:**
```
POST /api/dashboard/execute/<command>  - Executa comando
GET  /api/dashboard/commands           - Lista comandos disponíveis
```

### **Comandos Disponíveis:**
- `R` - Scanner técnico
- `CTX` - Contexto de mercado
- `MULT` - Multi-pair análise
- `CM` - Campo magnético
- `RT`, `RH`, `RD`, `RS` - Relatórios

---

## 💼 DASHBOARD 3: Profissional

### **Acesso:**
- **URL:** `http://localhost:9999/professional`
- **Template:** `templates/professional_dashboard.html`
- **Requer Login:** ✅ Sim

### **Como Acessar:**

```bash
# 1. Rodar Flask
python3 sne_radar_web.py

# 2. Login primeiro
http://localhost:9999/login

# 3. Acessar dashboard profissional
http://localhost:9999/professional
```

### **Funcionalidades:**
- ✅ Indicadores profissionais avançados
- ✅ Machine Learning Predictions
- ✅ Backtesting com interface visual
- ✅ Export de dados (CSV, JSON, PDF)
- ✅ Análise de derivativos
- ✅ Gráficos TradingView integrados
- ✅ Global metrics (CoinMarketCap)
- ✅ Funding rates (CoinGlass)
- ✅ Heatmap de correlações
- ✅ Professional indicators

### **Endpoints Utilizados:**
```
GET  /api/v1/professional-indicators
POST /api/v1/ml/train
GET  /api/v1/ml/predict
GET  /api/v1/ml/performance
POST /api/v1/backtest/run
POST /api/v1/backtest/optimize
GET  /api/v1/global-metrics
GET  /api/v1/derivatives
GET  /api/v1/candles
GET  /api/v1/advanced-indicators
```

---

## 👨‍💼 DASHBOARD 4: Admin

### **Acesso:**
- **URL:** `http://localhost:9999/admin`
- **Template:** `templates/admin_dashboard.html`
- **Requer:** ✅ Login + Permissões de admin

### **Como Acessar:**

```bash
# 1. Rodar Flask
python3 sne_radar_web.py

# 2. Login como admin
http://localhost:9999/login
Usuário: admin (ou usuário configurado em ADMIN_USERS)
Senha: admin

# 3. Acessar painel admin
http://localhost:9999/admin
```

### **Funcionalidades:**
- ✅ Gestão de usuários
- ✅ Estatísticas do sistema
- ✅ Configurações administrativas
- ✅ Visualização de logs
- ✅ Gerenciamento de planos/tiers
- ✅ API de administração

### **Endpoints Admin:**
```
GET  /api/admin/users
GET  /api/admin/users/stats
GET  /api/users
```

---

## 🔐 PÁGINAS DE AUTENTICAÇÃO

### **Login:**
- **URL:** `http://localhost:9999/login`
- **Template:** `templates/login.html`
- **Métodos:** GET, POST
- **Funcionalidade:** Autenticação de usuários

### **Register:**
- **URL:** `http://localhost:9999/register`
- **Template:** `templates/register.html`
- **Métodos:** GET, POST
- **Funcionalidade:** Registro de novos usuários

### **Logout:**
- **URL:** `http://localhost:9999/logout`
- **Funcionalidade:** Logout e limpeza de sessão

---

## 📄 OUTRAS PÁGINAS

### **Pricing:**
- **URL:** `http://localhost:9999/pricing` ou `/legacy`
- **Template:** `templates/pricing.html`
- **Funcionalidade:** Exibe planos e preços

### **Upgrade:**
- **URL:** `http://localhost:9999/upgrade/<tier>`
- **Template:** `templates/upgrade.html`
- **Funcionalidade:** Upgrade de plano

---

## 🚀 COMO RODAR TUDO

### **Passo 1: Preparar Ambiente**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Ativar venv (se tiver)
source venv/bin/activate

# Instalar dependências (se necessário)
pip install -r requirements.txt
```

### **Passo 2: Opção A - Frontend Vue.js (Recomendado)**

```bash
# Terminal 1: Build frontend
cd frontend
npm install
npm run build
cd ..

# Terminal 1: Rodar Flask (serve frontend automaticamente)
python3 sne_radar_web.py

# Acessar: http://localhost:9999
```

### **Passo 3: Opção B - Desenvolvimento Frontend**

```bash
# Terminal 1: Vite dev server
cd frontend
npm run dev
# Frontend: http://localhost:5173

# Terminal 2: Flask backend
python3 sne_radar_web.py
# Backend: http://localhost:9999
```

### **Passo 4: Opção C - Apenas Templates HTML**

```bash
# Rodar Flask (sem frontend buildado)
python3 sne_radar_web.py

# Acessar dashboards HTML:
http://localhost:9999/dashboard      # Terminal
http://localhost:9999/professional   # Profissional
http://localhost:9999/admin          # Admin
```

---

## 🔄 FLUXO DE ACESSO

### **Usuário Não Autenticado:**
```
/ → Redireciona para /pricing (ou frontend Vue.js se buildado)
/login → Página de login
/register → Página de registro
/dashboard → Redireciona para /login
/professional → Redireciona para /login
/admin → Redireciona para /login
```

### **Usuário Autenticado:**
```
/ → Dashboard Vue.js (se buildado) ou Pricing
/dashboard → Terminal Interativo
/professional → Dashboard Profissional
/admin → Dashboard Admin (se for admin)
```

### **Admin:**
```
/admin → Dashboard Admin
/api/admin/* → APIs administrativas
```

---

## 📊 COMPARAÇÃO DOS DASHBOARDS

| Dashboard | Tecnologia | Requer Login | Mobile | Tempo Real | Foco |
|-----------|------------|--------------|--------|------------|------|
| **Vue.js 3** | Vue, Vite, SPA | Opcional | ✅ | ✅ | Interface moderna |
| **Terminal** | HTML/JS | ✅ | ✅ | ⚠️ | Comandos interativos |
| **Profissional** | HTML/JS | ✅ | ✅ | ⚠️ | Funcionalidades avançadas |
| **Admin** | HTML/JS | ✅ Admin | ✅ | ❌ | Administração |

---

## 🎯 RECOMENDAÇÕES

### **Para Desenvolvimento:**
- Use **Frontend Vue.js** em modo dev (Vite dev server)
- Mais rápido para desenvolvimento
- Hot reload automático

### **Para Produção:**
- Build do frontend (`npm run build`)
- Flask serve tudo
- Uma única porta (9999)

### **Para Usuários Finais:**
- **Dashboard Terminal** - Mais simples e direto
- **Dashboard Profissional** - Funcionalidades avançadas
- **Frontend Vue.js** - Experiência moderna

---

## ✅ CHECKLIST DE ACESSO

### **Verificar se está funcionando:**

- [ ] Flask rodando na porta 9999
- [ ] Frontend buildado (se usar Vue.js) ou templates HTML disponíveis
- [ ] Banco de dados inicializado
- [ ] Usuário admin criado (automático no init)
- [ ] Conectividade com APIs externas (Binance, etc.)

### **Acessar cada dashboard:**

- [ ] `/` - Frontend Vue.js ou Pricing
- [ ] `/dashboard` - Terminal Interativo
- [ ] `/professional` - Dashboard Profissional
- [ ] `/admin` - Dashboard Admin
- [ ] `/login` - Página de Login
- [ ] `/register` - Página de Registro

---

## 🆘 TROUBLESHOOTING

### **Problema: Frontend não aparece**

**Solução:**
```bash
# Verificar se frontend está buildado
ls -la frontend/dist/

# Se não existir, fazer build
cd frontend
npm run build
```

### **Problema: Erro de login**

**Solução:**
- Verificar se banco de dados foi inicializado
- Criar usuário em `/register`
- Ou usar usuário admin padrão (admin/admin)

### **Problema: Templates não carregam**

**Solução:**
```bash
# Verificar se templates existem
ls -la templates/

# Verificar permissões
chmod -R 755 templates/
```

---

## 🎉 CONCLUSÃO

O sistema possui **MÚLTIPLOS dashboards web funcionais**, cada um adequado para diferentes necessidades:

1. ✅ **Frontend Vue.js** - Interface moderna e completa
2. ✅ **Dashboard Terminal** - Comandos interativos
3. ✅ **Dashboard Profissional** - Funcionalidades avançadas
4. ✅ **Dashboard Admin** - Administração

**Todos estão operacionais e prontos para uso!** 🚀

---

**Documento criado em:** Janeiro 2025  
**Última atualização:** Janeiro 2025

