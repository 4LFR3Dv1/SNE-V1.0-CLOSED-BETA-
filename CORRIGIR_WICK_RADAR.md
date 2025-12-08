# 🔧 CORREÇÃO: Wick Radar Não Mostra Dados

## ✅ Problema Identificado

O Wick Radar não está mostrando dados porque:

1. **Monitor não inicia automaticamente** quando acessado via web
2. **Histórico não está sendo salvo** corretamente
3. **API pode não estar respondendo** corretamente

## 🔧 Correções Aplicadas

### 1. Monitor Inicia Automaticamente

Atualizado `sne_radar_web.py` para iniciar o monitor automaticamente quando criado via web.

### 2. Verificar se Monitor Está Rodando

**Via Terminal:**
```bash
# Verificar se monitor está ativo
curl http://127.0.0.1:9999/api/v1/notifications/monitor/status

# Ver estatísticas
curl http://127.0.0.1:9999/api/v1/notifications/stats

# Ver histórico
curl http://127.0.0.1:9999/api/v1/notifications/history
```

**Via Interface:**
1. Acesse: `http://127.0.0.1:9999/wick-radar`
2. Clique em "▶️ Iniciar" se o monitor estiver parado
3. Aguarde alguns minutos para o monitor escanear os símbolos

### 3. Verificar Logs

```bash
# Ver logs do scanner
tail -f ~/Library/Application\ Support/SNE_RADAR/logs/scanner.log

# Ver se há alertas sendo gerados
grep "Alerta" ~/Library/Application\ Support/SNE_RADAR/logs/scanner.log
```

### 4. Verificar Arquivos de Estado

```bash
# Verificar se arquivos existem
ls -la ~/Library/Application\ Support/SNE_RADAR/

# Deve mostrar:
# - scanner_state.json (cooldowns)
# - scanner_history.json (histórico detalhado)
```

## 🧪 Teste Manual

### Teste 1: Verificar Monitor

```bash
# No terminal, execute:
python3 -c "
from monitors.opportunity_monitor import OpportunityMonitor
monitor = OpportunityMonitor(
    symbols=['BTCUSDT'],
    scan_interval=30,
    enable_volume_scanner=True,
    enable_pavio_scanner=True
)
monitor.start()
print('✅ Monitor iniciado')
import time
time.sleep(60)  # Aguardar 1 minuto
print('📊 Stats:', monitor.get_stats())
monitor.stop()
"
```

### Teste 2: Verificar API

```bash
# Testar endpoints
curl http://127.0.0.1:9999/api/v1/notifications/monitor/status | python3 -m json.tool
curl http://127.0.0.1:9999/api/v1/notifications/stats | python3 -m json.tool
curl http://127.0.0.1:9999/api/v1/notifications/history | python3 -m json.tool
```

## 📊 O Que Esperar

### Quando Monitor Está Funcionando:

1. **Logs mostram scans:**
   ```
   INFO - Escaneando BTCUSDT...
   INFO - Escaneando ETHUSDT...
   ```

2. **Estatísticas aumentam:**
   - `scans_total` aumenta
   - `last_scan` é atualizado

3. **Alertas aparecem quando detectados:**
   - Volume explosivo (RVOL > 2.5x)
   - Agulhadas (Volume M30 + RSI M5 extremo + Wick confirmado)

### Quando Há Dados no Wick Radar:

- Cards de ativos aparecem
- Gráficos candlestick são exibidos
- Overlay com informações do wick
- Estatísticas atualizadas

## ⚠️ Troubleshooting

### Monitor Não Inicia

1. Verificar se módulos estão disponíveis:
   ```bash
   python3 -c "from monitors.opportunity_monitor import OpportunityMonitor; print('OK')"
   ```

2. Verificar se Telegram está configurado:
   ```bash
   python3 -c "from xenos_bot import enviar_oraculo; print('OK')"
   ```

### Histórico Vazio

1. Verificar se arquivo está sendo criado:
   ```bash
   ls -la ~/Library/Application\ Support/SNE_RADAR/scanner_history.json
   ```

2. Verificar permissões:
   ```bash
   chmod 755 ~/Library/Application\ Support/SNE_RADAR/
   ```

### API Não Responde

1. Verificar se servidor está rodando:
   ```bash
   lsof -i :9999
   ```

2. Verificar logs do Flask:
   ```bash
   # Se rodando via terminal, ver saída
   # Se rodando via .app, ver logs em:
   tail -f ~/Library/Application\ Support/SNE_RADAR/logs/*.log
   ```

## 🎯 Próximos Passos

1. **Aguardar alguns minutos** após iniciar o monitor
2. **Verificar logs** para confirmar que está escaneando
3. **Aguardar alertas** serem detectados (pode levar tempo)
4. **Verificar Wick Radar** na interface web

---

**Status:** ✅ Correções aplicadas  
**Ação Necessária:** Reiniciar o app e aguardar alguns minutos para o monitor escanear



