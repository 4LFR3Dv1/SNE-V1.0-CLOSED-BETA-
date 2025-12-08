# 🚀 GUIA COMPLETO DE INTEGRAÇÃO - SNE RADAR → SNE 1.0 CLOUD

## 📋 ÍNDICE

1. [Atualizar Secrets](#1-atualizar-secrets)
2. [Estrutura de Integração](#2-estrutura-de-integração)
3. [Integração por Serviço](#3-integração-por-serviço)
4. [Testes](#4-testes)
5. [Deploy](#5-deploy)

---

## 1. ATUALIZAR SECRETS

### Opção A: Script Interativo (Recomendado)

```bash
./atualizar_secrets.sh sne-v1
```

O script vai perguntar quais secrets você quer atualizar e pedir os valores.

### Opção B: Script Rápido (Via Argumentos)

```bash
./atualizar_secrets_rapido.sh sne-v1 \
  "SEU_TELEGRAM_BOT_TOKEN" \
  "SEU_TELEGRAM_CHAT_ID" \
  "SEU_BINANCE_API_KEY" \
  "SEU_BINANCE_SECRET_KEY"
```

### Opção C: Manual (Um por Um)

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Telegram Bot Token
echo -n "SEU_TELEGRAM_BOT_TOKEN" | gcloud secrets versions add sne-telegram-bot-token --data-file=-

# Telegram Chat ID
echo -n "SEU_TELEGRAM_CHAT_ID" | gcloud secrets versions add sne-telegram-chat-id --data-file=-

# Binance API Key
echo -n "SEU_BINANCE_API_KEY" | gcloud secrets versions add sne-binance-api-key --data-file=-

# Binance Secret Key
echo -n "SEU_BINANCE_SECRET_KEY" | gcloud secrets versions add sne-binance-secret-key --data-file=-
```

### Verificar Secrets

```bash
# Listar todos os secrets
gcloud secrets list --project=sne-v1

# Ver versões de um secret
gcloud secrets versions list sne-telegram-bot-token --project=sne-v1
gcloud secrets versions list sne-binance-api-key --project=sne-v1
```

---

## 2. ESTRUTURA DE INTEGRAÇÃO

### Criar Módulo Compartilhado

```bash
mkdir -p services/shared
```

**services/shared/__init__.py**
```python
# Módulo compartilhado entre serviços
```

**services/shared/binance_client.py**
```python
import os
from binance.client import Client
from google.cloud import secretmanager

def get_binance_client():
    """Obtém cliente Binance configurado"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'sne-v1')
    
    # Obter secrets
    client = secretmanager.SecretManagerServiceClient()
    
    api_key = client.access_secret_version(
        name=f"projects/{project_id}/secrets/sne-binance-api-key/versions/latest"
    ).payload.data.decode('UTF-8')
    
    secret_key = client.access_secret_version(
        name=f"projects/{project_id}/secrets/sne-binance-secret-key/versions/latest"
    ).payload.data.decode('UTF-8')
    
    return Client(api_key, secret_key)
```

**services/shared/database.py**
```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Obtém conexão PostgreSQL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL não configurado")
    
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
```

---

## 3. INTEGRAÇÃO POR SERVIÇO

### 3.1 sne-web (API Principal)

**Módulos a Integrar:**
- `motor_renan.py` → `services/sne-web/app/motor.py`
- `indicadores.py` → `services/sne-web/app/indicadores.py`
- `estrutura_mercado.py` → `services/sne-web/app/estrutura.py`
- `multi_timeframe.py` → `services/sne-web/app/multi_tf.py`
- `contexto_mercado.py` → `services/sne-web/app/contexto.py`

**Passos:**
1. Copiar módulos para `services/sne-web/app/`
2. Adaptar imports (usar `shared.binance_client`, `shared.database`)
3. Atualizar `services/sne-web/app/api.py` para usar os módulos reais
4. Testar localmente

**Exemplo de Integração:**
```python
# services/sne-web/app/api.py
from app.motor import MotorRenan
from shared.binance_client import get_binance_client

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    pair = data.get('pair', 'BTCUSDT')
    
    # Usar motor real
    motor = MotorRenan()
    analysis = motor.analisar_par(pair)
    
    return jsonify(analysis)
```

---

### 3.2 sne-worker (Backtesting)

**Módulos a Integrar:**
- `backtest.py` → `services/sne-worker/app/backtest.py`
- `backtest_sne.py` → `services/sne-worker/app/backtest_sne.py`

**Passos:**
1. Copiar módulos de backtest
2. Adaptar para Cloud Run (sem interface gráfica)
3. Criar job assíncrono
4. Salvar resultados no Cloud Storage

---

### 3.3 sne-auto (Automação)

**Módulos a Integrar:**
- `auto_analise.py` → `services/sne-auto/app/scanner.py`
- `alertas_inteligentes.py` → `services/sne-auto/app/alertas.py`

**Passos:**
1. Copiar módulos de automação
2. Adaptar para Cloud Scheduler
3. Configurar pares a escanear
4. Integrar com Telegram

---

### 3.4 sne-telegram (Webhook)

**Módulos a Integrar:**
- `xenos_bot.py` → `services/sne-telegram/app/webhook.py`
- `formatador_telegram_melhorado.py` → `services/sne-telegram/app/formatador.py`

**Passos:**
1. Copiar código do bot Telegram
2. Adaptar para webhook (não polling)
3. Processar comandos
4. Chamar APIs dos outros serviços

---

## 4. TESTES

### Testar Localmente

```bash
# Rodar com docker-compose
docker-compose -f docker-compose.dev.yml up

# Testar endpoints
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"pair": "BTCUSDT"}'
```

### Testar na Nuvem

```bash
# Após deploy
curl https://sne-web-pqhownilea-uc.a.run.app/health
curl -X POST https://sne-web-pqhownilea-uc.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"pair": "BTCUSDT"}'
```

---

## 5. DEPLOY

### Deploy Incremental

```bash
# 1. Atualizar código
# 2. Testar localmente
# 3. Build e deploy
./deploy_cloud_build.sh sne-v1 us-central1

# Ou deploy individual
./deploy/deploy_web.sh sne-v1 us-central1
```

---

## 📝 CHECKLIST DE INTEGRAÇÃO

### Fase 1: Secrets
- [ ] Atualizar Telegram Bot Token
- [ ] Atualizar Telegram Chat ID
- [ ] Atualizar Binance API Key
- [ ] Atualizar Binance Secret Key
- [ ] Verificar secrets no Secret Manager

### Fase 2: Estrutura
- [ ] Criar módulo `shared/`
- [ ] Criar `shared/binance_client.py`
- [ ] Criar `shared/database.py`
- [ ] Testar conexões

### Fase 3: sne-web
- [ ] Integrar `motor_renan.py`
- [ ] Integrar módulos de análise
- [ ] Atualizar endpoints
- [ ] Testar localmente
- [ ] Deploy e testar

### Fase 4: sne-worker
- [ ] Integrar backtest
- [ ] Criar jobs
- [ ] Testar
- [ ] Deploy

### Fase 5: sne-auto
- [ ] Integrar automação
- [ ] Configurar scans
- [ ] Testar
- [ ] Deploy

### Fase 6: sne-telegram
- [ ] Integrar bot
- [ ] Adaptar webhook
- [ ] Testar comandos
- [ ] Deploy

---

## 🎯 PRÓXIMOS PASSOS

1. **AGORA**: Atualizar secrets
   ```bash
   ./atualizar_secrets.sh sne-v1
   ```

2. **DEPOIS**: Criar estrutura compartilhada
   ```bash
   mkdir -p services/shared
   # Criar arquivos compartilhados
   ```

3. **ENTÃO**: Integrar módulos gradualmente
   - Começar com `sne-web`
   - Testar cada integração
   - Deploy incremental

---

**💡 Comece atualizando os secrets agora, depois vamos integrando o código módulo por módulo!**



