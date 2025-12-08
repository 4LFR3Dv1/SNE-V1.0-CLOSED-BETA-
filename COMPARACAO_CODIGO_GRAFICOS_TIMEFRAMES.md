# 🔍 COMPARAÇÃO: Código que Gera Gráficos - Timeframes Antigos vs Novos

## 📊 Timeframes

**Antigos (6):** `1m`, `5m`, `15m`, `1h`, `4h`, `1d`  
**Novos (9):** `3m`, `30m`, `2h`, `6h`, `8h`, `12h`, `3d`, `1w`, `1M`

---

## 1️⃣ BUSCA DE DADOS (`buscar_dados_binance`)

### **ANTES (Timeframes Antigos):**

```python
# sne_radar_web.py - ANTES
# Não havia mapeamento explícito - intervalos eram passados diretamente
interval_mapping = {
    "1m": "1m",
    "5m": "5m", 
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d"
}

# Requisição direta à Binance
url = f"https://api.binance.com/api/v3/klines"
params = {
    "symbol": symbol,
    "interval": interval,  # Passado diretamente
    "limit": limit
}
response = requests.get(url, params=params, timeout=10)
```

### **AGORA (Todos os Timeframes):**

```python
# sne_radar_web.py - AGORA
interval_mapping = {
    # ANTIGOS (mantidos)
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    
    # NOVOS (adicionados)
    "3m": "3m",
    "30m": "30m",
    "2h": "2h",
    "6h": "6h",
    "8h": "8h",
    "12h": "12h",
    "3d": "1d",  # ⚠️ ESPECIAL: Binance não suporta 3d - usar 1d e agregar
    "1w": "1w",
    "1M": "1M"
}

# Validação adicional
valid_binance_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "1w", "1M"]
if binance_interval not in valid_binance_intervals:
    binance_interval = "1h"  # Fallback seguro

# Requisição com mapeamento
binance_interval = interval_mapping.get(interval, interval)
params = {
    "symbol": symbol,
    "interval": binance_interval,  # Mapeado
    "limit": limit
}
```

**Diferenças:**
- ✅ **Novos:** Mapeamento explícito para todos os intervalos
- ✅ **Novos:** Validação de intervalos suportados pela Binance
- ✅ **Novos:** Fallback seguro se intervalo inválido
- ⚠️ **3d:** Requer tratamento especial (agregação)

---

## 2️⃣ AGREGAÇÃO DE DADOS (Específico para `3d`)

### **ANTES:**
```python
# Não havia agregação - todos os timeframes eram suportados diretamente pela Binance
# 3d não existia
```

### **AGORA:**
```python
# sne_radar_web.py - Linha 1288-1396
needs_aggregation = (interval == "3d")

if needs_aggregation and len(df) > 0:
    print(f"📊 [BINANCE] Agregando dados de 1d para 3d...")
    # Agrupar por períodos de 3 dias
    df['date_group'] = df.index.to_period('3D')
    df_agg = df.groupby('date_group').agg({
        'open': 'first',    # Primeiro preço de abertura
        'high': 'max',      # Máxima do período
        'low': 'min',       # Mínima do período
        'close': 'last',    # Último preço de fechamento
        'volume': 'sum',    # Volume total
        'trades': 'sum'     # Total de trades
    }).reset_index()
    df_agg['time'] = pd.to_datetime(df_agg['date_group'].astype(str))
    df_agg.set_index('time', inplace=True)
    df = df_agg
```

**Diferenças:**
- ⚠️ **3d:** Único timeframe que requer agregação manual
- ⚠️ **3d:** Busca dados de `1d` e agrupa em períodos de 3 dias
- ⚠️ **3d:** Aumenta `limit` em 3x para ter dados suficientes

---

## 3️⃣ AJUSTE DE LIMITE (`api_v1_chart_data`)

### **ANTES:**
```python
# sne_radar_web.py - ANTES
limit = int(request.args.get('limit', '500'))
# Sem ajustes baseados no intervalo
```

### **AGORA:**
```python
# sne_radar_web.py - Linha 3529-3536
# Ajustar limit baseado no intervalo para evitar problemas com intervalos longos
limit_adjustments = {
    '3d': min(requested_limit, 200),   # 200 candles = ~600 dias
    '1w': min(requested_limit, 150),   # 150 candles = ~1050 dias (~3 anos)
    '1M': min(requested_limit, 100)    # 100 candles = ~100 meses (~8 anos)
}
limit = limit_adjustments.get(interval, min(requested_limit, 1000))
```

**Diferenças:**
- ✅ **Novos longos:** Limite reduzido para evitar sobrecarga
- ✅ **3d, 1w, 1M:** Limites específicos para cada intervalo longo
- ✅ **Outros:** Mantém limite padrão de 1000

---

## 4️⃣ NORMALIZAÇÃO DE INTERVALO (`coletar_dados` - motor_renan.py)

### **ANTES:**
```python
# motor_renan.py - ANTES
interval = interval.lower()  # ❌ PROBLEMA: Convertia 1M para 1m!
# Sem tratamento especial para 1M ou 1w
```

### **AGORA:**
```python
# motor_renan.py - Linha 231-243
# IMPORTANTE: Preservar 'M' maiúsculo para mês (1M) vs 'm' minúsculo para minuto (1m)
original_interval = interval
interval_upper = interval.upper()

# Se for 1M, preservar maiúscula (Binance requer 1M para mês)
if interval_upper == '1M':
    interval = '1M'
else:
    # Para todos os outros (incluindo 1w, 3d, 12h), converter para minúscula
    interval = interval.lower()

# Tratamento especial para 3d
needs_aggregation = (interval == "3d")
if needs_aggregation:
    interval = "1d"  # Usar 1d como base
    limit = limit * 3  # Aumentar limit para ter dados suficientes
```

**Diferenças:**
- ✅ **1M:** Preserva maiúscula (corrige bug crítico)
- ✅ **1w:** Converte para minúscula (Binance aceita `1w`, não `1W`)
- ✅ **3d:** Tratamento especial com agregação
- ✅ **Outros novos:** Normalização correta

---

## 5️⃣ CONFIGURAÇÃO DE ESTRATÉGIA (`gerar_sintese` - motor_renan.py)

### **ANTES:**
```python
# motor_renan.py - ANTES
tf_config = {
    '1m':  {'sl_atr': 0.25, 'tp1_atr': 0.35, 'tp2_atr': 0.5,  'tp3_atr': 0.75, 'tipo': 'SCALP'},
    '5m':  {'sl_atr': 0.35, 'tp1_atr': 0.5,  'tp2_atr': 0.75, 'tp3_atr': 1.0,  'tipo': 'SCALP'},
    '15m': {'sl_atr': 0.5,  'tp1_atr': 0.75, 'tp2_atr': 1.0,  'tp3_atr': 1.5,  'tipo': 'DAY'},
    '1h':  {'sl_atr': 1.0,  'tp1_atr': 1.5,  'tp2_atr': 2.0,  'tp3_atr': 3.0,  'tipo': 'INTRA'},
    '4h':  {'sl_atr': 1.5,  'tp1_atr': 2.0,  'tp2_atr': 3.0,  'tp3_atr': 4.5,  'tipo': 'SWING'},
    '1d':  {'sl_atr': 3.0,  'tp1_atr': 4.0,  'tp2_atr': 6.0,  'tp3_atr': 9.0,  'tipo': 'POSITION'},
}
```

### **AGORA:**
```python
# motor_renan.py - Linha 473-490
tf_config = {
    # ANTIGOS (mantidos)
    '1m':  {'sl_atr': 0.25, 'tp1_atr': 0.35, 'tp2_atr': 0.5,  'tp3_atr': 0.75, 'tipo': 'SCALP'},
    '5m':  {'sl_atr': 0.35, 'tp1_atr': 0.5,  'tp2_atr': 0.75, 'tp3_atr': 1.0,  'tipo': 'SCALP'},
    '15m': {'sl_atr': 0.5,  'tp1_atr': 0.75, 'tp2_atr': 1.0,  'tp3_atr': 1.5,  'tipo': 'DAY'},
    '1h':  {'sl_atr': 1.0,  'tp1_atr': 1.5,  'tp2_atr': 2.0,  'tp3_atr': 3.0,  'tipo': 'INTRA'},
    '4h':  {'sl_atr': 1.5,  'tp1_atr': 2.0,  'tp2_atr': 3.0,  'tp3_atr': 4.5,  'tipo': 'SWING'},
    '1d':  {'sl_atr': 3.0,  'tp1_atr': 4.0,  'tp2_atr': 6.0,  'tp3_atr': 9.0,  'tipo': 'POSITION'},
    
    # NOVOS (adicionados)
    '3m':  {'sl_atr': 0.3,  'tp1_atr': 0.4,  'tp2_atr': 0.6,  'tp3_atr': 0.9,  'tipo': 'SCALP'},
    '30m': {'sl_atr': 0.7,  'tp1_atr': 1.0,  'tp2_atr': 1.5,  'tp3_atr': 2.0,  'tipo': 'INTRA'},
    '2h':  {'sl_atr': 1.2,  'tp1_atr': 1.8,  'tp2_atr': 2.5,  'tp3_atr': 3.5,  'tipo': 'INTRA'},
    '6h':  {'sl_atr': 1.8,  'tp1_atr': 2.3,  'tp2_atr': 3.5,  'tp3_atr': 5.0,  'tipo': 'SWING'},
    '8h':  {'sl_atr': 2.0,  'tp1_atr': 2.5,  'tp2_atr': 4.0,  'tp3_atr': 6.0,  'tipo': 'SWING'},
    '12h': {'sl_atr': 2.5,  'tp1_atr': 3.5,  'tp2_atr': 5.0,  'tp3_atr': 7.5,  'tipo': 'POSITION'},
    '3d':  {'sl_atr': 3.5,  'tp1_atr': 4.5,  'tp2_atr': 7.0,  'tp3_atr': 10.0, 'tipo': 'POSITION'},
    '1w':  {'sl_atr': 4.0,  'tp1_atr': 5.0,  'tp2_atr': 8.0,  'tp3_atr': 12.0, 'tipo': 'POSITION'},
    '1M':  {'sl_atr': 5.0,  'tp1_atr': 6.0,  'tp2_atr': 10.0, 'tp3_atr': 15.0, 'tipo': 'POSITION'}
}
```

**Diferenças:**
- ✅ **Novos:** Configurações específicas de SL/TP para cada novo timeframe
- ✅ **Novos:** Tipos de estratégia apropriados (SCALP, INTRA, SWING, POSITION)
- ✅ **Novos:** Valores de ATR escalonados proporcionalmente ao intervalo

---

## 6️⃣ PROCESSAMENTO NO FRONTEND (`InteractiveChart.vue`)

### **ANTES:**
```javascript
// InteractiveChart.vue - ANTES
// Fallback fixo de 1 hora para candles sem timestamp
if (!timeValue) {
    timeValue = Math.floor(Date.now() / 1000) - (chartDataResponse.candles.length - index) * 3600
}
```

### **AGORA:**
```javascript
// InteractiveChart.vue - Linha 820-830
// Fallback baseado no timeframe real
if (!timeValue) {
    const timeframeIntervals = {
        '1m': 60, '3m': 180, '5m': 300, '15m': 900, '30m': 1800,
        '1h': 3600, '2h': 7200, '4h': 14400, '6h': 21600, '8h': 28800, '12h': 43200,
        '1d': 86400, '3d': 259200, '1w': 604800, '1M': 2592000
    }
    const intervalSeconds = timeframeIntervals[props.timeframe] || 3600
    timeValue = Math.floor(Date.now() / 1000) - (chartDataResponse.candles.length - index) * intervalSeconds
}
```

**Diferenças:**
- ✅ **Novos:** Fallback usa intervalo correto baseado no timeframe
- ✅ **Todos:** Suporte para todos os 15 timeframes no cálculo de fallback

---

## 📋 RESUMO DAS DIFERENÇAS

| Aspecto | Antigos | Novos |
|---------|---------|-------|
| **Mapeamento** | Direto (sem validação) | Mapeamento explícito + validação |
| **Agregação** | Não necessária | `3d` requer agregação manual |
| **Limite** | Fixo (500) | Ajustado por intervalo longo |
| **Normalização** | `lower()` (bug em 1M) | Preserva `1M`, trata `1w` |
| **Estratégia** | 6 configs | 15 configs (todos os novos) |
| **Fallback Frontend** | Fixo 1h | Baseado no timeframe real |

---

## ⚠️ TRATAMENTOS ESPECIAIS

### **1. `3d` (3 Dias)**
- ❌ Binance não suporta diretamente
- ✅ Busca dados de `1d` e agrega manualmente
- ✅ Aumenta `limit` em 3x antes da busca
- ✅ Agrupa por períodos de 3 dias usando pandas

### **2. `1M` (1 Mês)**
- ⚠️ Binance requer `1M` (maiúsculo)
- ✅ Preserva maiúscula na normalização
- ✅ Não converte para `1m` (minuto)

### **3. `1w` (1 Semana)**
- ⚠️ Binance requer `1w` (minúsculo)
- ✅ Converte para minúscula na normalização
- ✅ Não converte para `1W` (maiúsculo)

### **4. Intervalos Longos (`1w`, `1M`)**
- ✅ Limite reduzido para evitar sobrecarga
- ✅ `1w`: máximo 150 candles (~3 anos)
- ✅ `1M`: máximo 100 candles (~8 anos)

---

## ✅ CONCLUSÃO

**Código Antigo:**
- Simples, direto
- Sem validações
- Bug em `1M` (convertia para `1m`)
- Sem suporte para novos intervalos

**Código Novo:**
- ✅ Validação completa
- ✅ Tratamento especial para `3d`, `1M`, `1w`
- ✅ Ajustes de limite para intervalos longos
- ✅ Configurações de estratégia para todos os timeframes
- ✅ Fallback correto no frontend

**Todos os timeframes (antigos e novos) agora usam o mesmo código base, com tratamentos especiais apenas onde necessário.**

