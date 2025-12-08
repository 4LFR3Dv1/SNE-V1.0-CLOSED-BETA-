# 🚀 SNE PROFESSIONAL ALERT SYSTEM

## 📋 **SISTEMA IMPLEMENTADO**

Sistema de alertas em tempo real profissional integrado ao SNE Radar.

### 🎯 **CARACTERÍSTICAS:**

- ✅ **Threading Background** - Roda em paralelo com o terminal
- ✅ **Configuração JSON** - Fácil personalização
- ✅ **Rate Limiting** - Evita spam de alertas
- ✅ **Cooldowns** - Intervalos inteligentes entre alertas
- ✅ **Horário Silencioso** - Configurável (padrão: 22h-6h)
- ✅ **Logging Profissional** - Logs estruturados
- ✅ **Múltiplos Pares** - BTC, ETH, SOL configurados
- ✅ **Multi-Timeframe** - 1h e 4h por padrão

### 🔧 **COMANDOS DISPONÍVEIS:**

```
A  - Status dos Alertas Profissionais
AS - Iniciar Alertas Automáticos  
AP - Parar Alertas Automáticos
AC - Configurar Alertas
```

### ⚙️ **CONFIGURAÇÃO:**

Arquivo: `config/alerts_config.json`

```json
{
    "enabled": true,
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    "timeframes": ["1h", "4h"],
    "alert_rules": {
        "min_confluence": 7.0,
        "min_volume_spike": 1.5,
        "max_volatility": 5.0
    },
    "rate_limits": {
        "cooldown_minutes": 5
    },
    "quiet_hours": [22, 6]
}
```

### 🚨 **TIPOS DE ALERTAS:**

1. **🎯 ALTA CONFLUÊNCIA** - Score ≥ 7.0/10
2. **🔄 MUDANÇA DE REGIME** - CONSOLIDATION → BULL_TREND, etc.
3. **⚠️ VOLATILIDADE EXTREMA** - > 5.0%
4. **📈 SPIKE DE VOLUME** - > 1.5x volume anterior

### 📱 **EXEMPLO DE ALERTA:**

```
🚨 SNE PROFESSIONAL ALERT

🎯 ALTA CONFLUÊNCIA: BTCUSDT (1h) - Score: 8.2/10

Prioridade: HIGH
Tipo: HIGH_CONFLUENCE
Horário: 14:30:15

---
SNE Professional Alert System
```

### 🚀 **COMO USAR:**

1. **Iniciar sistema:** `python main.py`
2. **Ver status:** Digite `A`
3. **Iniciar alertas:** Digite `AS`
4. **Configurar:** Digite `AC`
5. **Parar:** Digite `AP`

### 📊 **LOGS:**

- Arquivo: `logs/sne_alerts.log`
- Nível: INFO
- Formato: Timestamp - Logger - Level - Message

### ✅ **STATUS:**

**Sistema implementado e funcionando!** 🎯✨













