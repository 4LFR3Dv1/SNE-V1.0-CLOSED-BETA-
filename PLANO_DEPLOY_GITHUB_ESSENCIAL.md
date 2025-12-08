# 📋 PLANO: DEPLOY GITHUB - VERSÃO ESSENCIAL
## 🎯 Objetivo: Repositório mínimo para build em outros computadores

**Data**: 15 de Janeiro de 2025  
**Status**: 📝 PLANEJAMENTO (não executar ainda)

---

## 📊 ANÁLISE ATUAL

### **Estatísticas do Projeto**
- **Tamanho Total**: ~4.0 GB
- **Arquivos Python**: 8.295 arquivos `.py`
- **Documentação**: 1.219 arquivos `.md` ⚠️ **EXCESSIVO**
- **Builds**: `dist/` (~276 MB apenas do app)
- **Node Modules**: `frontend/node_modules/` (centenas de MB)

### **Problemas Identificados**
1. ⚠️ **Documentação duplicada**: 1.219 arquivos MD (muitos são correções antigas)
2. ⚠️ **Builds incluídos**: `dist/`, `build/` (devem ser gerados)
3. ⚠️ **Dependências**: `node_modules/`, `__pycache__/` (devem ser ignorados)
4. ⚠️ **Secrets**: `config_env_template.txt` contém tokens reais ⚠️
5. ⚠️ **Dados gerados**: `backtest_results/`, `exports/`, `ml_models/`
6. ⚠️ **Scripts temporários**: Muitos `fix_*.sh`, `corrigir_*.sh`

---

## ✅ O QUE DEVE IR PARA O GITHUB

### **1. CÓDIGO FONTE (ESSENCIAL)**

#### **Backend Python**
```
✅ sne_radar_web.py          # Aplicação Flask principal
✅ sne_desktop.py            # Launcher desktop
✅ motor_renan.py            # Motor de análise
✅ config.py                 # Configurações (sem secrets)
✅ database_config.py        # Config DB
✅ config_seguro.py          # Config segurança (sem secrets)

✅ app/                      # Estrutura Flask modular
   ├── __init__.py
   ├── api/
   ├── models/
   ├── routes/
   ├── services/
   ├── tasks/
   └── utils/

✅ Módulos de Análise:
   ├── contexto_global.py
   ├── estrutura_mercado.py
   ├── multi_timeframe.py
   ├── confluencia.py
   ├── fluxo_ativo.py
   ├── catalogo_magnetico.py
   ├── padroes_graficos.py
   ├── indicadores.py
   ├── indicadores_avancados.py
   ├── analise_candles_detalhada.py
   ├── gestao_risco_profissional.py
   ├── relatorio_profissional.py
   ├── calcular_suportes_resistencias.py
   └── niveis_operacionais.py

✅ Integrações:
   ├── integrations/
   │   ├── cmc.py
   │   └── coinglass.py
   └── services/
       ├── ta_summary.py
       ├── advanced_indicators.py
       ├── professional_indicators.py
       ├── ml_predictions.py
       └── advanced_backtesting.py

✅ Monitores e Scanners:
   ├── monitors/
   │   └── opportunity_monitor.py
   └── scanners/
       ├── volume_scanner.py
       └── pavio_scanner.py

✅ Notificações:
   └── notifications/
       ├── telegram_notifier.py
       └── alert_formatter.py

✅ Backtesting:
   ├── backtest.py
   ├── backtest_sne.py
   └── backtest_sne_mtf.py
```

#### **Frontend Vue.js**
```
✅ frontend/
   ├── package.json          # Dependências Node.js
   ├── package-lock.json     # Lock file (opcional, mas recomendado)
   ├── vite.config.js        # Config Vite
   ├── tailwind.config.js    # Config Tailwind
   ├── postcss.config.js     # Config PostCSS
   ├── electron-builder.yml  # Config Electron (se usar)
   ├── .gitignore            # Gitignore do frontend
   │
   ├── src/                  # Código fonte Vue.js
   │   ├── main.js
   │   ├── App.vue
   │   ├── router/
   │   ├── stores/
   │   ├── services/
   │   ├── components/
   │   ├── views/
   │   └── utils/
   │
   ├── public/               # Assets públicos
   └── index.html            # Template HTML

❌ frontend/dist/            # Build gerado (NÃO incluir)
❌ frontend/node_modules/    # Dependências (NÃO incluir)
```

#### **Microserviços Cloud**
```
✅ services/
   ├── sne-web/
   │   ├── app/
   │   ├── Dockerfile
   │   ├── requirements.txt
   │   └── README.md
   ├── sne-worker/
   │   ├── app/
   │   ├── Dockerfile
   │   ├── requirements.txt
   │   └── README.md
   ├── sne-auto/
   │   ├── app/
   │   ├── Dockerfile
   │   ├── requirements.txt
   │   └── README.md
   ├── sne-telegram/
   │   ├── app/
   │   ├── Dockerfile
   │   ├── requirements.txt
   │   └── README.md
   └── shared/
       ├── database.py
       └── binance_client.py
```

### **2. CONFIGURAÇÕES E BUILD**

#### **Arquivos de Build**
```
✅ build_mac.spec            # PyInstaller spec macOS
✅ build_windows.spec        # PyInstaller spec Windows
✅ build_mac_with_launcher.spec  # Versão alternativa

✅ Scripts de Build:
   ├── build_completo.sh     # Build completo (macOS/Linux)
   ├── build_windows.ps1     # Build Windows PowerShell
   ├── build_windows.bat     # Build Windows Batch
   └── build_frontend.sh     # Build frontend apenas

❌ build/                    # Diretório de build (NÃO incluir)
❌ dist/                     # Builds gerados (NÃO incluir)
```

#### **Configurações**
```
✅ requirements.txt          # Dependências Python
✅ alembic.ini               # Config Alembic
✅ alembic/                  # Migrações de banco
   ├── env.py
   └── versions/
       ├── 0001_initial.py
       ├── 0002_add_performance_indexes.py
       ├── 0003_add_trading_models.py
       ├── 0004_rename_binance_to_exchange.py
       └── 0005_add_capital_pools_and_global_config.py

✅ .gitignore                # Gitignore principal (ATUALIZAR)
✅ .env.example              # Template de variáveis (CRIAR)
✅ config_env_template.txt   # Template (REMOVER SECRETS)

✅ Assets:
   └── assets/
       ├── logo_sne.icns     # Ícone macOS
       ├── logo_sne.png      # Logo
       └── logo_sne.iconset/ # Ícones macOS
```

#### **Docker e Infraestrutura**
```
✅ Dockerfile.cloud          # Dockerfile produção
✅ docker-compose.dev.yml    # Docker Compose dev
✅ cloudbuild.yaml           # Cloud Build CI/CD
✅ deploy/                   # Scripts de deploy
   └── [scripts essenciais]

✅ infra/                    # Terraform (se existir)
   └── terraform/
```

### **3. DOCUMENTAÇÃO ESSENCIAL**

#### **Documentação a Manter** (Consolidar)
```
✅ README.md                 # README principal (ATUALIZAR)
✅ BUILD_WINDOWS_COMPLETO.md # Guia build Windows
✅ GUIA_PROTECAO_IP_DISTRIBUICAO.md  # Proteção IP
✅ COMO_FUNCIONA_TRADING_AUTOMATIZADO.md  # Trading
✅ DEPLOYMENT_GUIDE.md       # Guia de deploy
✅ CHANGELOG.md              # Histórico (CRIAR)

✅ docs/                     # Documentação organizada (CRIAR)
   ├── architecture.md
   ├── api.md
   ├── development.md
   └── deployment.md
```

#### **Documentação a Remover** (1.219 arquivos → ~10-15)
```
❌ ANALISE_*.md              # Análises antigas (manter apenas 1-2 recentes)
❌ CORRECAO_*.md             # Correções antigas (histórico)
❌ CORRIGIR_*.md             # Guias de correção antigos
❌ DEBUG_*.md                # Debugs antigos
❌ SOLUCAO_*.md              # Soluções antigas
❌ DEPLOY_*.md               # Múltiplos guias (consolidar)
❌ COMO_*.md                 # Múltiplos guias (consolidar)
❌ GUIA_*.md                 # Múltiplos guias (consolidar)
```

### **4. SCRIPTS ESSENCIAIS**

```
✅ Scripts de Build:
   ├── build_completo.sh
   ├── build_frontend.sh
   ├── build_windows.ps1
   └── build_windows.bat

✅ Scripts de Setup:
   ├── setup.sh              # Setup inicial (CRIAR)
   └── install_dependencies.sh  # Instalar deps (CRIAR)

❌ Scripts Temporários:
   ├── fix_*.sh              # Correções temporárias
   ├── corrigir_*.sh         # Correções temporárias
   └── commit_*.sh           # Scripts específicos
```

---

## ❌ O QUE NÃO DEVE IR PARA O GITHUB

### **1. Builds e Artefatos Gerados**
```
❌ dist/                     # Builds PyInstaller
❌ build/                    # Build temporário
❌ frontend/dist/            # Build frontend
❌ frontend/node_modules/    # Dependências Node.js
❌ *.egg-info/               # Metadados Python
❌ __pycache__/              # Cache Python
❌ *.pyc, *.pyo              # Bytecode Python
```

### **2. Dados e Runtime**
```
❌ data/                     # Banco de dados local
❌ *.db, *.sqlite            # Bancos de dados
❌ logs/                     # Logs
❌ *.log                     # Arquivos de log
❌ exports/                  # Exports gerados
❌ backtest_results/         # Resultados de backtest
❌ backtest_data/            # Dados de backtest (opcional)
❌ ml_models/                # Modelos ML treinados
❌ *.pkl, *.joblib           # Modelos serializados
```

### **3. Secrets e Credenciais**
```
❌ .env                      # Variáveis de ambiente
❌ .env.local                # Variáveis locais
❌ .env.production           # Secrets produção
❌ config_secrets.py         # Secrets hardcoded
❌ secrets.json              # Arquivo de secrets
❌ credentials.json          # Credenciais
❌ config_producao.txt       # Config com secrets
```

**⚠️ CRÍTICO**: `config_env_template.txt` contém tokens reais! Deve ser limpo.

### **4. Cache e Temporários**
```
❌ .cache/                   # Cache
❌ *.cache                   # Arquivos de cache
❌ temp/                     # Arquivos temporários
❌ tmp/                      # Arquivos temporários
❌ *.tmp, *.temp             # Arquivos temporários
❌ *.bak, *.backup           # Backups
```

### **5. Ambiente Virtual**
```
❌ venv/                     # Virtual environment
❌ venv_new/                 # Virtual environment
❌ env/                      # Virtual environment
❌ ENV/                      # Virtual environment
```

### **6. IDE e OS**
```
❌ .vscode/                  # Config VS Code (exceto settings recomendados)
❌ .idea/                    # Config IntelliJ
❌ .DS_Store                 # macOS
❌ Thumbs.db                 # Windows
❌ *.swp, *.swo              # Vim
```

---

## 🔧 ATUALIZAÇÕES NECESSÁRIAS NO .gitignore

### **Adicionar ao .gitignore**

```gitignore
# ===========================================
# BUILD E DISTRIBUIÇÃO
# ===========================================
dist/
build/
*.egg-info/
*.dist-info/

# Frontend builds
frontend/dist/
frontend/dist-ssr/
frontend/.vite/

# ===========================================
# NODE.JS
# ===========================================
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
.pnpm-store/

# ===========================================
# DADOS E RUNTIME
# ===========================================
data/
*.db
*.sqlite
*.sqlite3
logs/
*.log
exports/
backtest_results/
backtest_data/
ml_models/
*.pkl
*.joblib

# ===========================================
# SECRETS E CREDENCIAIS
# ===========================================
.env
.env.*
!.env.example
config_secrets.py
secrets.json
credentials.json
config_producao.txt
*.key
*.pem
*.cert

# ===========================================
# DOCUMENTAÇÃO TEMPORÁRIA
# ===========================================
# Manter apenas documentação essencial
# Remover análises antigas manualmente

# ===========================================
# SCRIPTS TEMPORÁRIOS
# ===========================================
fix_*.sh
corrigir_*.sh
commit_*.sh
```

---

## 📝 ESTRUTURA FINAL DO REPOSITÓRIO

```
SNE_RADAR/
├── README.md                    # README principal atualizado
├── CHANGELOG.md                 # Histórico de versões
├── LICENSE                      # Licença
├── .gitignore                   # Gitignore atualizado
├── requirements.txt             # Dependências Python
├── .env.example                 # Template de variáveis (CRIAR)
│
├── alembic.ini                  # Config Alembic
├── alembic/                     # Migrações
│   ├── env.py
│   └── versions/
│
├── assets/                      # Assets (ícones, logos)
│   ├── logo_sne.icns
│   ├── logo_sne.png
│   └── logo_sne.iconset/
│
├── app/                         # Aplicação Flask modular
│   ├── __init__.py
│   ├── api/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── tasks/
│   └── utils/
│
├── frontend/                    # Frontend Vue.js
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   └── public/
│
├── services/                    # Microserviços
│   ├── sne-web/
│   ├── sne-worker/
│   ├── sne-auto/
│   ├── sne-telegram/
│   └── shared/
│
├── integrations/                # Integrações externas
│   ├── cmc.py
│   └── coinglass.py
│
├── monitors/                    # Monitores
│   └── opportunity_monitor.py
│
├── scanners/                    # Scanners
│   ├── volume_scanner.py
│   └── pavio_scanner.py
│
├── notifications/               # Notificações
│   ├── telegram_notifier.py
│   └── alert_formatter.py
│
├── services/                    # Serviços de análise
│   ├── ta_summary.py
│   ├── advanced_indicators.py
│   ├── professional_indicators.py
│   ├── ml_predictions.py
│   └── advanced_backtesting.py
│
├── [Módulos Python Core]        # Módulos principais
│   ├── sne_radar_web.py
│   ├── sne_desktop.py
│   ├── motor_renan.py
│   ├── config.py
│   ├── database_config.py
│   └── [outros módulos]
│
├── build_mac.spec               # Build specs
├── build_windows.spec
│
├── build_completo.sh            # Scripts de build
├── build_frontend.sh
├── build_windows.ps1
├── build_windows.bat
│
├── Dockerfile.cloud             # Docker
├── docker-compose.dev.yml
│
├── cloudbuild.yaml              # CI/CD
│
├── deploy/                      # Scripts de deploy
│   └── [scripts essenciais]
│
└── docs/                        # Documentação consolidada
    ├── architecture.md
    ├── api.md
    ├── development.md
    ├── deployment.md
    └── BUILD_WINDOWS_COMPLETO.md
```

---

## 🚀 PLANO DE EXECUÇÃO

### **FASE 1: Preparação (Análise e Limpeza)**

1. **Criar `.env.example`** (template sem secrets)
   ```bash
   # Copiar config_env_template.txt
   # Remover todos os valores reais
   # Deixar apenas variáveis vazias ou exemplos
   ```

2. **Atualizar `.gitignore`**
   - Adicionar todas as exclusões necessárias
   - Verificar se está completo

3. **Identificar arquivos a remover**
   - Listar todos os `.md` duplicados
   - Identificar scripts temporários
   - Listar builds e artefatos

### **FASE 2: Limpeza de Secrets**

1. **Limpar `config_env_template.txt`**
   - Remover tokens reais
   - Deixar apenas placeholders
   - Renomear para `.env.example`

2. **Verificar outros arquivos com secrets**
   - Buscar por padrões: `API_KEY=`, `TOKEN=`, `SECRET=`
   - Limpar ou adicionar ao `.gitignore`

### **FASE 3: Consolidação de Documentação**

1. **Criar estrutura `docs/`**
   ```bash
   mkdir -p docs
   ```

2. **Mover documentação essencial**
   - `BUILD_WINDOWS_COMPLETO.md` → `docs/`
   - `DEPLOYMENT_GUIDE.md` → `docs/`
   - Outros guias essenciais → `docs/`

3. **Remover documentação antiga**
   - Analisar quais `.md` são realmente necessários
   - Mover restante para `docs/archive/` ou deletar

### **FASE 4: Atualização do README**

1. **Criar README.md completo**
   - Visão geral do projeto
   - Requisitos
   - Instalação
   - Build
   - Uso
   - Contribuição

2. **Criar CHANGELOG.md**
   - Histórico de versões
   - Mudanças principais

### **FASE 5: Teste Local**

1. **Clonar em diretório temporário**
   ```bash
   cd /tmp
   git clone <repo> sne_test
   cd sne_test
   ```

2. **Testar build**
   ```bash
   # Instalar dependências
   pip install -r requirements.txt
   cd frontend && npm install && cd ..
   
   # Build frontend
   ./build_frontend.sh
   
   # Testar build (macOS)
   python -m PyInstaller build_mac.spec --clean
   ```

3. **Verificar que tudo funciona**
   - Imports funcionam
   - Builds geram corretamente
   - Nenhum arquivo essencial faltando

### **FASE 6: Commit e Push**

1. **Verificar status**
   ```bash
   git status
   git status --ignored  # Verificar que .gitignore está funcionando
   ```

2. **Adicionar arquivos**
   ```bash
   git add .
   ```

3. **Commit inicial**
   ```bash
   git commit -m "feat: Versão essencial para GitHub

   - Código fonte completo
   - Configurações de build
   - Documentação consolidada
   - Removidos builds, secrets e arquivos temporários"
   ```

4. **Push**
   ```bash
   git push origin main
   ```

---

## 📋 CHECKLIST FINAL

### **Antes do Commit**

- [ ] `.gitignore` atualizado e completo
- [ ] `.env.example` criado (sem secrets)
- [ ] `config_env_template.txt` limpo ou removido
- [ ] Todos os secrets removidos do código
- [ ] `dist/` e `build/` não estão no repositório
- [ ] `node_modules/` não está no repositório
- [ ] `__pycache__/` não está no repositório
- [ ] Documentação consolidada (máximo 15-20 arquivos MD)
- [ ] README.md atualizado e completo
- [ ] CHANGELOG.md criado
- [ ] Scripts de build funcionando
- [ ] Testado build local em diretório limpo

### **Estrutura de Arquivos**

- [ ] Todos os módulos Python essenciais incluídos
- [ ] Frontend source incluído (sem dist/)
- [ ] Assets incluídos (ícones, logos)
- [ ] Migrações Alembic incluídas
- [ ] Dockerfiles incluídos
- [ ] Scripts de build incluídos
- [ ] Configurações de build (.spec) incluídas

### **Documentação**

- [ ] README.md completo
- [ ] CHANGELOG.md criado
- [ ] Guias essenciais em `docs/`
- [ ] Documentação antiga removida ou arquivada

---

## ⚠️ AVISOS IMPORTANTES

1. **NUNCA commitar secrets**: Verificar todos os arquivos antes do commit
2. **Testar build limpo**: Clonar em diretório novo e testar
3. **Backup antes**: Fazer backup completo antes de limpar
4. **Commits incrementais**: Fazer commits pequenos e testados
5. **Branch de teste**: Criar branch `github-cleanup` para testar

---

## 📊 ESTIMATIVA DE REDUÇÃO

### **Antes**
- **Tamanho**: ~4.0 GB
- **Arquivos**: ~10.000+ arquivos
- **Documentação**: 1.219 arquivos MD

### **Depois**
- **Tamanho**: ~50-100 MB (estimado)
- **Arquivos**: ~500-800 arquivos essenciais
- **Documentação**: ~15-20 arquivos MD

### **Redução**
- **Tamanho**: ~95% de redução
- **Arquivos**: ~90% de redução
- **Documentação**: ~98% de redução

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ **Análise completa** (FEITO)
2. ⏳ **Revisar e aprovar plano**
3. ⏳ **Criar backup completo**
4. ⏳ **Executar FASE 1-6**
5. ⏳ **Testar build em ambiente limpo**
6. ⏳ **Fazer commit e push**

---

**Status**: 📝 PLANEJAMENTO COMPLETO - AGUARDANDO APROVAÇÃO PARA EXECUÇÃO

