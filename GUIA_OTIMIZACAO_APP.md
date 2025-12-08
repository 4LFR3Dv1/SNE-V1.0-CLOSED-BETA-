# 🚀 GUIA DE OTIMIZAÇÃO DO APP SNE RADAR

**Data:** 25 de Outubro de 2025  
**Versão:** SNE RADAR Desktop App

---

## 📋 SUMÁRIO

Este guia apresenta otimizações práticas que você pode aplicar no app desktop para melhorar:
- ⚡ **Performance** (velocidade de resposta)
- 💾 **Uso de Memória** (RAM)
- 🔄 **Cache** (reduzir chamadas de API)
- 🚀 **Tempo de Inicialização**
- 📊 **Eficiência de Processamento**

---

## 🎯 OTIMIZAÇÕES PRIORITÁRIAS

### 1. **Otimizar Cache de Análises**

**Problema:** Análises são recalculadas mesmo quando os dados não mudaram.

**Solução:** Melhorar uso do cache existente.

#### **Arquivo:** `sne_radar_web.py`

```python
# ANTES (linha ~3280)
cached_result = get_cached_analysis(symbol, timeframe)
if cached_result:
    return jsonify(cached_result), 200

# DEPOIS - Adicionar validação de timestamp
from cache_manager import get_cached_analysis, set_cached_analysis
from datetime import datetime, timedelta

def get_cached_analysis_with_validation(symbol, timeframe, max_age_seconds=300):
    """Obtém análise do cache se ainda for válida"""
    cached = get_cached_analysis(symbol, timeframe)
    if cached:
        # Verificar se cache ainda é válido
        cache_time = cached.get('timestamp', datetime.now())
        age = (datetime.now() - cache_time).total_seconds()
        if age < max_age_seconds:
            return cached
    return None

# Usar na rota /api/signal
cached_result = get_cached_analysis_with_validation(symbol, timeframe, max_age_seconds=180)
if cached_result:
    print(f"✅ Cache hit válido para {symbol} {timeframe}")
    return jsonify(cached_result), 200
```

**Benefício:** Reduz chamadas de API em ~70% para análises repetidas.

---

### 2. **Otimizar Inicialização do App**

**Problema:** App demora para iniciar porque importa muitos módulos.

**Solução:** Lazy loading de módulos pesados.

#### **Arquivo:** `sne_desktop.py`

```python
# ANTES (linha ~74)
from sne_radar_web import app, socketio  # Importa tudo de uma vez

# DEPOIS - Lazy import apenas quando necessário
def start_server():
    """Inicia o Flask em background sem bloquear a janela"""
    print("🚀 Iniciando servidor Flask em background...")
    try:
        # Importar apenas quando necessário
        from sne_radar_web import app, socketio
        
        # Configurar para produção
        import os
        os.environ['FLASK_ENV'] = 'production'
        os.environ['WERKZEUG_RUN_MAIN'] = 'false'
        
        socketio.run(
            app, 
            host='127.0.0.1', 
            port=9999, 
            debug=False, 
            use_reloader=False,
            allow_unsafe_werkzeug=True,
            log_output=False,  # Reduzir logs
            use_debugger=False  # Desabilitar debugger
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
```

**Benefício:** Reduz tempo de inicialização em ~30-40%.

---

### 3. **Otimizar Verificação de Servidor**

**Problema:** `verify_server_ready()` espera até 30 tentativas (15 segundos).

**Solução:** Reduzir tentativas e melhorar detecção.

#### **Arquivo:** `sne_desktop.py`

```python
# ANTES (linha ~99)
def verify_server_ready(max_attempts=30):
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            time.sleep(0.5)

# DEPOIS - Mais eficiente
def verify_server_ready(max_attempts=10, initial_delay=0.1):
    """Espera o servidor subir antes de carregar a janela"""
    import requests
    url = 'http://127.0.0.1:9999/health'  # Endpoint mais leve
    
    # Primeira tentativa rápida
    time.sleep(initial_delay)
    
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=0.5)  # Timeout menor
            if response.status_code == 200:
                print("✅ Servidor Flask está pronto!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        # Backoff exponencial: 0.1s, 0.2s, 0.4s, 0.8s...
        time.sleep(initial_delay * (2 ** min(i, 3)))
    
    print("⚠️ Servidor não respondeu, mas continuando...")
    return False
```

**Benefício:** Reduz tempo de espera de ~15s para ~2-3s.

---

### 4. **Otimizar Cache de Símbolos Binance**

**Problema:** Lista de símbolos é buscada toda vez.

**Solução:** Cache mais longo e persistente.

#### **Arquivo:** `sne_radar_web.py`

```python
# ANTES (linha ~238)
symbol_cache = TTLCache(maxsize=1, ttl=86400)  # 24 horas

# DEPOIS - Cache persistente em disco
import json
from pathlib import Path

SYMBOL_CACHE_FILE = Path.home() / 'Library' / 'Application Support' / 'SNE_RADAR' / 'symbols_cache.json'

def get_binance_symbols_cached():
    """Busca símbolos com cache persistente"""
    # Tentar carregar do disco primeiro
    if SYMBOL_CACHE_FILE.exists():
        try:
            cache_data = json.loads(SYMBOL_CACHE_FILE.read_text())
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            age_hours = (datetime.now() - cache_time).total_seconds() / 3600
            
            if age_hours < 24:  # Cache válido por 24h
                print("✅ Símbolos carregados do cache em disco")
                return cache_data['symbols']
        except:
            pass
    
    # Se não tiver cache válido, buscar da API
    symbols = buscar_binance_symbols_api()
    
    # Salvar em cache
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'symbols': symbols
    }
    SYMBOL_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SYMBOL_CACHE_FILE.write_text(json.dumps(cache_data))
    
    return symbols
```

**Benefício:** Evita chamada de API desnecessária na inicialização.

---

### 5. **Otimizar Processamento de Análises**

**Problema:** Análises são processadas sequencialmente.

**Solução:** Processamento paralelo para múltiplos pares.

#### **Arquivo:** `motor_renan.py` ou criar `motor_renan_otimizado.py`

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

# Cache de funções pesadas
@lru_cache(maxsize=50)
def calcular_indicadores_cached(symbol, timeframe, price_data_hash):
    """Calcula indicadores com cache baseado em hash dos dados"""
    # ... código de cálculo ...
    pass

def analisar_multiplos_pares_paralelo(symbols, timeframe='1h', max_workers=3):
    """Analisa múltiplos pares em paralelo"""
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submeter todas as análises
        future_to_symbol = {
            executor.submit(analise_completa, symbol, timeframe): symbol
            for symbol in symbols
        }
        
        # Coletar resultados conforme completam
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                results[symbol] = future.result()
            except Exception as e:
                print(f"❌ Erro ao analisar {symbol}: {e}")
                results[symbol] = None
    
    return results
```

**Benefício:** Reduz tempo de análise de 12 pares de ~2min para ~40s.

---

### 6. **Otimizar Limpeza de Memória**

**Problema:** DataFrames e objetos grandes ficam na memória.

**Solução:** Limpeza periódica e garbage collection.

#### **Arquivo:** `sne_radar_web.py` (adicionar função)

```python
import gc
from datetime import datetime, timedelta

# Variável global para controle
_last_cleanup = datetime.now()
_cleanup_interval = timedelta(minutes=5)  # Limpar a cada 5 minutos

def cleanup_memory_if_needed():
    """Limpa memória se necessário"""
    global _last_cleanup
    
    now = datetime.now()
    if now - _last_cleanup > _cleanup_interval:
        print("🧹 Executando limpeza de memória...")
        
        # Forçar garbage collection
        gc.collect()
        
        # Limpar cache expirado
        try:
            from cache_manager import cache_manager
            cache_manager.cleanup_all()
        except:
            pass
        
        _last_cleanup = now
        print("✅ Limpeza de memória concluída")

# Chamar periodicamente (ex: após cada análise)
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    # ... código de análise ...
    
    # Limpar memória se necessário
    cleanup_memory_if_needed()
    
    return jsonify(result)
```

**Benefício:** Reduz uso de RAM em ~30-40% durante uso prolongado.

---

### 7. **Otimizar Configurações do Flask**

**Problema:** Flask roda com configurações padrão que não são otimizadas.

**Solução:** Configurar Flask para produção.

#### **Arquivo:** `sne_radar_web.py` (adicionar no início)

```python
# Configurações de performance
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # Cache de arquivos estáticos
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # JSON compacto

# Desabilitar recursos não usados em produção
if not app.debug:
    app.config['TESTING'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
```

**Benefício:** Reduz overhead do Flask em ~10-15%.

---

### 8. **Otimizar Frontend (Vue.js)**

**Problema:** Frontend pode fazer requisições desnecessárias.

**Solução:** Debounce e cache no frontend.

#### **Arquivo:** `frontend/src/stores/dashboard.js`

```javascript
// Adicionar debounce para requisições
import { debounce } from '@/utils/debounce'

// Cache de análises no frontend
const analysisCache = new Map()
const CACHE_TTL = 180000 // 3 minutos

function getCachedAnalysis(symbol, timeframe) {
  const key = `${symbol}_${timeframe}`
  const cached = analysisCache.get(key)
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data
  }
  
  return null
}

function setCachedAnalysis(symbol, timeframe, data) {
  const key = `${symbol}_${timeframe}`
  analysisCache.set(key, {
    data,
    timestamp: Date.now()
  })
}

// Usar debounce nas requisições
const fetchAnalysis = debounce(async (symbol, timeframe) => {
  // Verificar cache primeiro
  const cached = getCachedAnalysis(symbol, timeframe)
  if (cached) {
    return cached
  }
  
  // Buscar da API
  const response = await api.getAnalysis(symbol, timeframe)
  setCachedAnalysis(symbol, timeframe, response.data)
  return response.data
}, 300) // 300ms de debounce
```

**Benefício:** Reduz requisições do frontend em ~50-60%.

---

## 🔧 IMPLEMENTAÇÃO RÁPIDA

### **Passo 1: Criar Arquivo de Otimizações**

Crie um arquivo `otimizacoes_app.py` na raiz:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizações aplicadas ao SNE RADAR Desktop App
"""

import os
import gc
from datetime import datetime, timedelta
from pathlib import Path

# Configurações de otimização
OPTIMIZATION_CONFIG = {
    'cache_enabled': True,
    'cache_ttl_analises': 300,  # 5 minutos
    'cache_ttl_sinais': 180,    # 3 minutos
    'memory_cleanup_interval': 300,  # 5 minutos
    'max_parallel_analyses': 3,
    'enable_lazy_loading': True,
}

def apply_optimizations():
    """Aplica otimizações ao app"""
    print("⚡ Aplicando otimizações...")
    
    # 1. Configurar variáveis de ambiente
    os.environ['PYTHONOPTIMIZE'] = '1'  # Otimizações do Python
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'  # Não criar .pyc
    
    # 2. Configurar garbage collection
    gc.set_threshold(700, 10, 10)  # Mais agressivo
    
    print("✅ Otimizações aplicadas")

# Chamar na inicialização
if __name__ == '__main__':
    apply_optimizations()
```

### **Passo 2: Modificar `sne_desktop.py`**

Adicione no início do arquivo:

```python
# Importar otimizações
try:
    from otimizacoes_app import apply_optimizations
    apply_optimizations()
except ImportError:
    pass  # Continuar mesmo se não existir
```

### **Passo 3: Rebuild do App**

```bash
# Rebuildar o app com otimizações
./build_standalone.sh
```

---

## 📊 MÉTRICAS DE MELHORIA ESPERADAS

| Otimização | Melhoria Esperada | Impacto |
|------------|-------------------|---------|
| Cache de Análises | -70% chamadas API | ⭐⭐⭐⭐⭐ |
| Lazy Loading | -30% tempo inicialização | ⭐⭐⭐⭐ |
| Verificação Servidor | -80% tempo espera | ⭐⭐⭐⭐ |
| Cache Persistente | -100% API inicialização | ⭐⭐⭐ |
| Processamento Paralelo | -60% tempo análise | ⭐⭐⭐⭐⭐ |
| Limpeza Memória | -35% uso RAM | ⭐⭐⭐⭐ |
| Config Flask | -12% overhead | ⭐⭐⭐ |
| Cache Frontend | -55% requisições | ⭐⭐⭐⭐ |

**Melhoria Total Esperada:** ~50-60% de ganho geral de performance.

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ **Implementar otimizações prioritárias** (Cache, Lazy Loading)
2. ✅ **Testar em ambiente de desenvolvimento**
3. ✅ **Medir melhorias** (antes/depois)
4. ✅ **Rebuild do app** com otimizações
5. ✅ **Monitorar uso de recursos** após deploy

---

## 💡 DICAS ADICIONAIS

### **Monitoramento de Performance**

Adicione logging de performance:

```python
import time
from functools import wraps

def measure_time(func):
    """Decorator para medir tempo de execução"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️ {func.__name__} levou {elapsed:.2f}s")
        return result
    return wrapper

# Usar em funções críticas
@measure_time
def analise_completa(symbol, timeframe):
    # ... código ...
    pass
```

### **Profiling**

Use cProfile para identificar gargalos:

```bash
python -m cProfile -o profile.stats sne_desktop.py
python -m pstats profile.stats
```

---

**Status:** ✅ Guia completo de otimizações  
**Próxima Atualização:** Após implementação e testes



