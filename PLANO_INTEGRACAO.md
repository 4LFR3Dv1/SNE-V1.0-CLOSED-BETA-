# 🔄 PLANO DE INTEGRAÇÃO - SNE RADAR → SNE 1.0 CLOUD

## 🎯 OBJETIVO

Migrar o código real do SNE RADAR para os microserviços Cloud Run, mantendo toda a funcionalidade e melhorando a arquitetura.

---

## 📊 MAPEAMENTO DE MÓDULOS

### 1. **sne-web** (API Principal)

**Responsabilidades:**
- Endpoints de análise técnica
- Motor de análise (`motor_renan.py`)
- Contexto de mercado
- Multi-timeframe

**Módulos a Integrar:**
```
sne-web/
├── app/
│   ├── main.py (Flask app)
│   ├── api.py (endpoints)
│   ├── motor.py (motor_renan.py adaptado)
│   ├── contexto.py (contexto_mercado.py, contexto_global.py)
│   ├── indicadores.py (indicadores.py, indicadores_avancados.py)
│   ├── estrutura.py (estrutura_mercado.py)
│   ├── multi_tf.py (multi_timeframe.py)
│   ├── padroes.py (padroes_graficos.py)
│   └── suportes_resistencias.py (calcular_suportes_resistencias.py)
```

**Endpoints:**
- `POST /api/analyze` → `motor_renan.analisar_par()`
- `GET /api/signal` → `motor_renan.obter_sinal()`
- `GET /api/context` → `contexto_mercado.obter_contexto()`
- `GET /api/multi-tf` → `multi_timeframe.analisar_multi_tf()`

---

### 2. **sne-worker** (Backtesting & Jobs Pesados)

**Responsabilidades:**
- Backtesting
- Análises pesadas
- Processamento assíncrono

**Módulos a Integrar:**
```
sne-worker/
├── app/
│   ├── main.py (Flask app)
│   ├── jobs.py (jobs assíncronos)
│   ├── backtest.py (backtest.py, backtest_sne.py)
│   ├── analise_pesada.py (análises que consomem CPU)
│   └── relatorios.py (geração de relatórios)
```

**Jobs:**
- `run_backtest` → Executa backtest completo
- `analise_multi_pair` → Análise de múltiplos pares
- `gerar_relatorio` → Gera relatórios PDF

---

### 3. **sne-auto** (Automação & Scans)

**Responsabilidades:**
- Scans automáticos periódicos
- Alertas automáticos
- Monitoramento 24/7

**Módulos a Integrar:**
```
sne-auto/
├── app/
│   ├── main.py (Flask app)
│   ├── scanner.py (auto_analise.py, coin_scanner.py)
│   ├── alertas.py (alertas_inteligentes.py, alertas_tecnicos.py)
│   └── monitor.py (market_monitor_pro.py)
```

**Funcionalidades:**
- `run_scan` → Escaneia pares configurados
- `check_alerts` → Verifica alertas
- `monitor_market` → Monitora mercado

---

### 4. **sne-telegram** (Webhook Telegram)

**Responsabilidades:**
- Receber webhooks do Telegram
- Processar comandos
- Enviar mensagens

**Módulos a Integrar:**
```
sne-telegram/
├── app/
│   ├── main.py (Flask app)
│   ├── webhook.py (xenos_bot.py adaptado)
│   ├── comandos.py (processar comandos)
│   └── formatador.py (formatador_telegram_melhorado.py)
```

**Funcionalidades:**
- `POST /webhook/telegram` → Recebe webhook
- Processa comandos do Telegram
- Envia análises formatadas

---

## 🔧 DEPENDÊNCIAS COMPARTILHADAS

**Criar módulo compartilhado:**
```
shared/
├── __init__.py
├── binance_client.py (cliente Binance)
├── database.py (conexão PostgreSQL)
├── config.py (configurações)
└── utils.py (utilitários)
```

---

## 📋 PLANO DE EXECUÇÃO

### Fase 1: Preparação (1-2 dias)
- [ ] Criar estrutura de módulos compartilhados
- [ ] Adaptar conexão Binance para Cloud
- [ ] Configurar conexão PostgreSQL
- [ ] Atualizar secrets (Telegram, Binance)

### Fase 2: sne-web (2-3 dias)
- [ ] Integrar `motor_renan.py`
- [ ] Integrar módulos de análise técnica
- [ ] Adaptar endpoints
- [ ] Testar localmente

### Fase 3: sne-worker (1-2 dias)
- [ ] Integrar `backtest.py`
- [ ] Criar jobs assíncronos
- [ ] Testar backtesting

### Fase 4: sne-auto (1-2 dias)
- [ ] Integrar `auto_analise.py`
- [ ] Configurar scans automáticos
- [ ] Testar automação

### Fase 5: sne-telegram (1 dia)
- [ ] Integrar `xenos_bot.py`
- [ ] Adaptar webhook
- [ ] Testar comandos

### Fase 6: Deploy & Testes (1-2 dias)
- [ ] Build e deploy
- [ ] Testes de integração
- [ ] Ajustes finais

**Total Estimado**: 7-12 dias

---

## 🔐 SECRETS NECESSÁRIOS

1. **Telegram**
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

2. **Binance**
   - `BINANCE_API_KEY`
   - `BINANCE_SECRET_KEY`

3. **Outros**
   - `SECRET_KEY` (Flask)
   - `DATABASE_URL` (já configurado)

---

## 📝 PRÓXIMOS PASSOS

1. **Atualizar Secrets** (agora)
2. **Criar estrutura compartilhada**
3. **Integrar módulos gradualmente**
4. **Testar cada serviço**
5. **Deploy incremental**

---

**💡 Comece atualizando os secrets, depois vamos integrando o código módulo por módulo!**



