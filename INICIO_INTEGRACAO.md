# 🚀 INÍCIO DA INTEGRAÇÃO - SNE RADAR → SNE 1.0 CLOUD

## ✅ SECRETS ATUALIZADOS

**Data**: 25 de Novembro de 2025

### Secrets do Telegram
- ✅ **Telegram Bot Token**: Atualizado
- ✅ **Telegram Chat ID**: Atualizado

### Secrets da Binance
- ⚠️ **Binance API Key**: Não encontrada nos arquivos (atualizar manualmente se necessário)
- ⚠️ **Binance Secret Key**: Não encontrada nos arquivos (atualizar manualmente se necessário)

---

## 📋 PRÓXIMOS PASSOS PARA INTEGRAÇÃO

### 1. Criar Estrutura Compartilhada

```bash
mkdir -p services/shared
```

**services/shared/__init__.py**
```python
# Módulo compartilhado
```

**services/shared/binance_client.py**
```python
import os
from binance.client import Client
from google.cloud import secretmanager

def get_binance_client():
    """Obtém cliente Binance configurado"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'sne-v1')
    
    client = secretmanager.SecretManagerServiceClient()
    
    try:
        api_key = client.access_secret_version(
            name=f"projects/{project_id}/secrets/sne-binance-api-key/versions/latest"
        ).payload.data.decode('UTF-8')
        
        secret_key = client.access_secret_version(
            name=f"projects/{project_id}/secrets/sne-binance-secret-key/versions/latest"
        ).payload.data.decode('UTF-8')
        
        return Client(api_key, secret_key)
    except:
        # Fallback: cliente sem autenticação (apenas leitura)
        return Client()
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

### 2. Integrar motor_renan.py em sne-web

**Passos:**
1. Copiar `motor_renan.py` para `services/sne-web/app/motor.py`
2. Adaptar imports para usar `shared.binance_client`
3. Atualizar `services/sne-web/app/api.py` para usar o motor real

**Exemplo:**
```python
# services/sne-web/app/api.py
from app.motor import MotorRenan

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    pair = data.get('pair', 'BTCUSDT')
    
    motor = MotorRenan()
    analysis = motor.analisar_par(pair)
    
    return jsonify(analysis)
```

---

### 3. Integrar xenos_bot.py em sne-telegram

**Passos:**
1. Copiar código relevante de `xenos_bot.py` para `services/sne-telegram/app/webhook.py`
2. Adaptar para webhook (não polling)
3. Usar secrets do Secret Manager

---

### 4. Integrar backtest.py em sne-worker

**Passos:**
1. Copiar `backtest.py` para `services/sne-worker/app/backtest.py`
2. Adaptar para Cloud Run (sem interface gráfica)
3. Salvar resultados no Cloud Storage

---

### 5. Integrar auto_analise.py em sne-auto

**Passos:**
1. Copiar `auto_analise.py` para `services/sne-auto/app/scanner.py`
2. Adaptar para Cloud Scheduler
3. Configurar pares a escanear

---

## 🎯 ORDEM DE INTEGRAÇÃO RECOMENDADA

1. **sne-web** (API Principal)
   - Integrar `motor_renan.py`
   - Integrar módulos de análise técnica
   - Testar endpoints

2. **sne-telegram** (Webhook)
   - Integrar código do bot
   - Testar webhook

3. **sne-auto** (Automação)
   - Integrar scanner automático
   - Configurar Cloud Scheduler

4. **sne-worker** (Backtesting)
   - Integrar backtest
   - Criar jobs assíncronos

---

## 📝 COMANDOS ÚTEIS

```bash
# Ver secrets atualizados
gcloud secrets versions list sne-telegram-bot-token --project=sne-v1
gcloud secrets versions list sne-telegram-chat-id --project=sne-v1

# Atualizar Binance keys (se necessário)
echo -n "API_KEY" | gcloud secrets versions add sne-binance-api-key --data-file=-
echo -n "SECRET_KEY" | gcloud secrets versions add sne-binance-secret-key --data-file=-

# Testar serviços
curl https://sne-web-pqhownilea-uc.a.run.app/health
```

---

## ✅ CHECKLIST

- [x] Secrets do Telegram atualizados
- [ ] Estrutura compartilhada criada
- [ ] motor_renan.py integrado em sne-web
- [ ] Módulos de análise técnica integrados
- [ ] xenos_bot.py integrado em sne-telegram
- [ ] backtest.py integrado em sne-worker
- [ ] auto_analise.py integrado em sne-auto
- [ ] Testes realizados
- [ ] Deploy completo

---

**💡 Próximo passo**: Criar a estrutura compartilhada e começar a integrar o `motor_renan.py` em `sne-web`!



