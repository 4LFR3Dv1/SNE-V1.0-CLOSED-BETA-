# 🔧 CORREÇÃO: Wick Radar Não Funciona

## 🔍 DIAGNÓSTICO

O Wick Radar pode não estar funcionando por alguns motivos:

1. **Monitor não está rodando** - O monitor precisa estar ativo para escanear e detectar alertas
2. **Não há dados ainda** - O monitor precisa de tempo para escanear e detectar alertas
3. **Monitor não iniciou automaticamente** - Pode precisar iniciar manualmente

---

## ✅ SOLUÇÃO RÁPIDA

### **1. Verificar se o Monitor está Rodando**

Abra o Wick Radar no app e verifique:
- **Status:** Deve mostrar "Monitor Ativo" (verde)
- **Botão:** Deve mostrar "⏸️ Parar" (não "▶️ Iniciar")

### **2. Se o Monitor NÃO estiver Rodando:**

1. Clique no botão **"▶️ Iniciar"** no Wick Radar
2. Aguarde alguns segundos
3. O status deve mudar para "Monitor Ativo"

### **3. Aguardar Dados**

O monitor precisa de tempo para:
- Escanear os símbolos (BTCUSDT, ETHUSDT, etc.)
- Detectar volume explosivo (RVOL > 2.5x)
- Detectar agulhadas (Volume M30 + RSI M5 + Wick)

**Tempo estimado:** 1-5 minutos para começar a ver dados

---

## 🧪 TESTE MANUAL VIA TERMINAL

### **Teste 1: Verificar Status do Monitor**

```bash
curl http://127.0.0.1:9999/api/v1/notifications/monitor/status
```

**Resultado esperado:**
```json
{
  "success": true,
  "status": {
    "available": true,
    "running": true,
    "symbols": ["BTCUSDT", "ETHUSDT", ...],
    "scan_interval": 60,
    "volume_scanner_enabled": true,
    "pavio_scanner_enabled": true
  }
}
```

**Se `running: false`:** O monitor não está rodando. Inicie via interface ou API.

### **Teste 2: Iniciar Monitor via API**

```bash
curl -X POST http://127.0.0.1:9999/api/v1/notifications/monitor/start
```

**Resultado esperado:**
```json
{
  "success": true,
  "message": "Monitor iniciado com sucesso"
}
```

### **Teste 3: Verificar Estatísticas**

```bash
curl http://127.0.0.1:9999/api/v1/notifications/stats
```

**Resultado esperado:**
```json
{
  "success": true,
  "stats": {
    "scans_total": 10,
    "alerts_volume": 2,
    "alerts_pavio": 1,
    "last_scan": "2025-12-02T11:55:00"
  }
}
```

### **Teste 4: Verificar Histórico**

```bash
curl http://127.0.0.1:9999/api/v1/notifications/history
```

**Resultado esperado:**
```json
{
  "success": true,
  "history": [
    {
      "symbol": "BTCUSDT",
      "timestamp": "2025-12-02T11:55:00",
      "type": "volume",
      "preco_atual": 65000,
      "rvol": 2.8
    }
  ]
}
```

---

## 🔧 CORREÇÕES ESPECÍFICAS

### **Problema 1: Monitor Não Inicia Automaticamente**

**Sintoma:** Status mostra "Monitor Inativo" mesmo após abrir o app

**Solução:**
1. Abra o Wick Radar
2. Clique em **"▶️ Iniciar"**
3. Aguarde alguns segundos
4. O status deve mudar para "Monitor Ativo"

**OU via API:**
```bash
curl -X POST http://127.0.0.1:9999/api/v1/notifications/monitor/start
```

### **Problema 2: Histórico Vazio**

**Sintoma:** Wick Radar não mostra nenhum ativo/card

**Causas possíveis:**
1. Monitor não está rodando
2. Monitor está rodando mas ainda não detectou alertas
3. Arquivos de histórico não existem

**Solução:**
1. Verificar se monitor está rodando (ver acima)
2. Aguardar 2-5 minutos para o monitor escanear
3. Verificar se arquivos existem:
   ```bash
   ls -la ~/Library/Application\ Support/SNE_RADAR/scanner_state.json
   ls -la ~/Library/Application\ Support/SNE_RADAR/scanner_history.json
   ```

### **Problema 3: Erro ao Carregar Dados**

**Sintoma:** Console do navegador mostra erros ao carregar Wick Radar

**Solução:**
1. Abrir Console do Navegador (F12)
2. Verificar erros específicos
3. Verificar se APIs estão respondendo (ver testes acima)

### **Problema 4: Monitor Para Automaticamente**

**Sintoma:** Monitor inicia mas para logo em seguida

**Possíveis causas:**
1. Erro no código do monitor
2. Problema com módulos (scanners, notifications)
3. Erro de conexão com Binance

**Solução:**
1. Verificar logs:
   ```bash
   tail -f ~/Library/Application\ Support/SNE_RADAR/logs/scanner.log
   ```
2. Verificar se há erros nos logs
3. Reiniciar o app

---

## 📊 O QUE ESPERAR QUANDO FUNCIONA

### **Interface do Wick Radar:**

1. **Status:** "Monitor Ativo" (verde)
2. **Estatísticas:**
   - Total de Scans: número aumenta
   - Alertas de Volume: número aumenta quando detecta
   - Alertas de Agulhada: número aumenta quando detecta
   - Última Análise: timestamp atualizado

3. **Cards de Ativos:**
   - Aparecem quando alertas são detectados
   - Mostram símbolo, preço, RVOL, RSI, etc.
   - Gráficos candlestick são exibidos

### **Logs Esperados:**

```bash
tail -f ~/Library/Application\ Support/SNE_RADAR/logs/scanner.log
```

**Deve mostrar:**
```
INFO - Escaneando BTCUSDT...
INFO - Escaneando ETHUSDT...
INFO - Volume explosivo detectado: BTCUSDT (RVOL: 2.8x)
INFO - Agulhada detectada: ETHUSDT (LONG)
```

---

## 🎯 CHECKLIST DE DIAGNÓSTICO

- [ ] App está rodando (janela aberta)
- [ ] Servidor Flask está ativo (porta 9999)
- [ ] Wick Radar abre na interface
- [ ] Status do monitor verificado
- [ ] Monitor iniciado (se não estava rodando)
- [ ] Aguardado 2-5 minutos para escaneamento
- [ ] Estatísticas aparecem (mesmo que zero)
- [ ] Histórico verificado via API
- [ ] Logs verificados para erros

---

## 💡 DICAS

1. **O monitor precisa de tempo:** Aguarde pelo menos 2-5 minutos após iniciar
2. **Alertas não são instantâneos:** Dependem de condições de mercado
3. **Volume explosivo é raro:** Pode levar tempo para detectar
4. **Agulhadas são mais comuns:** Mas ainda dependem de condições específicas

---

## 🚀 PRÓXIMOS PASSOS

1. **Iniciar o monitor** (se não estiver rodando)
2. **Aguardar alguns minutos** para escaneamento
3. **Verificar estatísticas** na interface
4. **Verificar histórico** via API ou interface
5. **Verificar logs** se ainda não funcionar

---

**Última atualização:** 2025-12-02  
**Status:** Guia de diagnóstico criado



