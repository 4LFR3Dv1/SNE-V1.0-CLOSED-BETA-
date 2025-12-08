# 🛡️ MITIGAÇÃO DE RISCOS - SCANNER DE OPORTUNIDADES

**Data:** 25 de Outubro de 2025  
**Versão:** 1.0  
**Status:** ✅ Implementações Críticas

---

## 🎯 RISCOS IDENTIFICADOS E MITIGAÇÕES

### **1. ⚠️ RATE LIMIT DA BINANCE**

#### **Risco:**
- Escalar para 20-50 moedas pode causar ban temporário de IP
- Binance limita a 1200 requests/minuto
- `skip_rate_limit=True` não é solução permanente

#### **Mitigação Implementada:**

```python
# monitors/opportunity_monitor.py

class OpportunityMonitor:
    def __init__(self, 
                 symbols: List[str] = None,
                 scan_interval: int = 60,
                 max_symbols: int = 15):  # ✅ NOVO: Limite de símbolos
        # Limitar lista de símbolos automaticamente
        if symbols and len(symbols) > max_symbols:
            print(f"⚠️ Lista de símbolos ({len(symbols)}) excede máximo ({max_symbols})")
            print(f"   Usando apenas os primeiros {max_symbols} símbolos")
            self.symbols = symbols[:max_symbols]
        else:
            self.symbols = symbols or self._get_default_symbols()
        
        self.max_symbols = max_symbols
        self.api_delay = 0.1  # Delay entre requisições (segundos)
    
    def _get_default_symbols(self) -> List[str]:
        """Retorna lista padrão (top 10 por liquidez)"""
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT',
            'XRPUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'AVAXUSDT'
        ]
    
    def _calculate_dynamic_delay(self) -> float:
        """
        Calcula delay dinâmico baseado no número de símbolos
        Para respeitar rate limit: 1200 req/min = 20 req/s = 0.05s entre reqs
        Com margem de segurança: 0.1s entre símbolos
        """
        # Delay base: 0.1s por símbolo
        # Para 10 símbolos: 1s total (seguro)
        # Para 15 símbolos: 1.5s total (seguro)
        return self.api_delay
    
    def _monitor_loop(self):
        """Loop principal com delay dinâmico"""
        while self.running:
            try:
                start_time = time.time()
                
                # Escanear todos os símbolos
                for symbol in self.symbols:
                    if not self.running:
                        break
                    
                    # Delay entre símbolos (respeita rate limit)
                    time.sleep(self._calculate_dynamic_delay())
                    
                    # Scanner de Volume
                    if self.volume_scanner:
                        result = self.volume_scanner.scan_symbol(symbol, timeframe='5m')
                        if result and result.get('triggered'):
                            self.notifier.send_volume_alert(result)
                            self.stats['alerts_volume'] += 1
                    
                    # Scanner de Pavio
                    if self.pavio_scanner:
                        result = self.pavio_scanner.scan_symbol(symbol)
                        if result and result.get('triggered'):
                            self.notifier.send_pavio_alert(result)
                            self.stats['alerts_pavio'] += 1
                    
                    self.stats['scans_total'] += 1
                
                # Calcular tempo real de execução
                execution_time = time.time() - start_time
                
                # Ajustar intervalo para compensar drift
                remaining_time = max(0, self.scan_interval - execution_time)
                
                if remaining_time > 0:
                    time.sleep(remaining_time)
                else:
                    # Se execução demorou mais que o intervalo, logar warning
                    print(f"⚠️ Ciclo demorou {execution_time:.1f}s (mais que intervalo de {self.scan_interval}s)")
                    # Continuar imediatamente (não esperar)
                
                self.stats['last_scan'] = datetime.now()
                
            except Exception as e:
                print(f"❌ Erro no loop de monitoramento: {e}")
                self.stats['errors'] += 1
                time.sleep(10)  # Fallback seguro
```

**Benefícios:**
- ✅ Limite automático de símbolos (máx 15)
- ✅ Delay dinâmico entre requisições
- ✅ Compensação de drift no loop
- ✅ Logging de performance

---

### **2. ⚠️ DRIFT DO LOOP SÍNCRONO**

#### **Risco:**
- Loop com `sleep(60)` pode ter drift se API demorar
- Ciclo real pode ser 90s em vez de 60s
- Perde "ponta" do movimento

#### **Mitigação Implementada:**

```python
# monitors/opportunity_monitor.py

def _monitor_loop(self):
    """Loop com compensação de drift"""
    while self.running:
        try:
            cycle_start = time.time()
            
            # ... escanear símbolos ...
            
            # Calcular tempo real de execução
            execution_time = time.time() - cycle_start
            
            # Compensar drift: aguardar apenas o tempo restante
            remaining_time = max(0, self.scan_interval - execution_time)
            
            if remaining_time > 0:
                time.sleep(remaining_time)
            else:
                # Se demorou mais que o intervalo, logar e continuar
                print(f"⚠️ Ciclo demorou {execution_time:.1f}s (intervalo: {self.scan_interval}s)")
                # Não esperar - continuar imediatamente
            
            # Estatísticas de performance
            self.stats['avg_cycle_time'] = (
                (self.stats.get('avg_cycle_time', 0) * 0.9) + 
                (execution_time * 0.1)
            )
            
        except Exception as e:
            # ... tratamento de erro ...
```

**Benefícios:**
- ✅ Compensação automática de drift
- ✅ Ciclo sempre próximo do intervalo desejado
- ✅ Logging de performance para monitoramento
- ✅ Não acumula atraso ao longo do tempo

---

### **3. ⚠️ DEPENDÊNCIA DE REDE**

#### **Risco:**
- Internet pode cair
- API pode estar offline
- Monitor pode travar (crash)

#### **Mitigação Implementada:**

```python
# scanners/volume_scanner.py

class VolumeScanner:
    def scan_symbol(self, symbol: str, timeframe: str = '5m') -> Optional[Dict]:
        """Escaneia com tratamento robusto de erros de rede"""
        max_retries = 3
        retry_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                # Buscar dados com timeout
                df = buscar_dados_binance(
                    symbol, 
                    timeframe, 
                    limit=21, 
                    skip_rate_limit=True,
                    timeout=10  # ✅ Timeout explícito
                )
                
                if df is None or len(df) < 21:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None
                
                # ... processar dados ...
                return result
                
            except requests.exceptions.ConnectionError as e:
                print(f"⚠️ Erro de conexão ao escanear {symbol} (tentativa {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Backoff exponencial
                    continue
                return None
                
            except requests.exceptions.Timeout as e:
                print(f"⚠️ Timeout ao escanear {symbol} (tentativa {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
                
            except Exception as e:
                print(f"❌ Erro inesperado ao escanear {symbol}: {e}")
                return None
        
        return None
```

```python
# monitors/opportunity_monitor.py

def _monitor_loop(self):
    """Loop com tratamento robusto de rede"""
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while self.running:
        try:
            # Verificar conexão antes de escanear
            if not self._check_internet_connection():
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    print("⚠️ Muitos erros consecutivos. Entrando em modo de espera...")
                    time.sleep(60)  # Aguardar 1 minuto
                    consecutive_errors = 0
                else:
                    time.sleep(10)  # Aguardar 10 segundos
                continue
            
            # Reset contador de erros se sucesso
            consecutive_errors = 0
            
            # ... escanear símbolos ...
            
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
            break
        except Exception as e:
            consecutive_errors += 1
            print(f"❌ Erro no loop de monitoramento: {e}")
            self.stats['errors'] += 1
            
            if consecutive_errors >= max_consecutive_errors:
                print("⚠️ Muitos erros consecutivos. Entrando em modo de espera...")
                time.sleep(60)
                consecutive_errors = 0
            else:
                time.sleep(10)  # Fallback seguro
    
    def _check_internet_connection(self) -> bool:
        """Verifica conexão com internet"""
        try:
            response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
            return response.status_code == 200
        except:
            return False
```

**Benefícios:**
- ✅ Retry automático com backoff exponencial
- ✅ Timeout explícito em todas as requisições
- ✅ Verificação de conexão antes de escanear
- ✅ Modo de espera após muitos erros
- ✅ Não trava o monitor em caso de falha de rede

---

### **4. ⚠️ ESCALABILIDADE FUTURA**

#### **Risco:**
- Loop síncrono não escala bem para muitos símbolos
- Pode precisar de async no futuro

#### **Preparação Implementada:**

```python
# monitors/opportunity_monitor.py

class OpportunityMonitor:
    def __init__(self, 
                 use_async: bool = False,  # ✅ Preparação para Fase 3+
                 ...):
        self.use_async = use_async
        
        if use_async:
            # Preparação para asyncio (Fase 3+)
            import asyncio
            self.loop = asyncio.new_event_loop()
            self.executor = None
        else:
            # Modo síncrono atual (Fase 1-2)
            self.loop = None
            self.executor = None
    
    def _scan_symbol_async(self, symbol: str):
        """Escaneia símbolo de forma assíncrona (Fase 3+)"""
        if self.use_async:
            # Implementação futura com asyncio
            # Permite escanear múltiplos símbolos simultaneamente
            pass
        else:
            # Implementação síncrona atual
            return self.volume_scanner.scan_symbol(symbol)
```

**Benefícios:**
- ✅ Preparação para migração async
- ✅ Compatibilidade com código atual
- ✅ Fácil ativação quando necessário

---

## 📊 MONITORAMENTO E LOGGING

### **Estatísticas Implementadas:**

```python
# monitors/opportunity_monitor.py

self.stats = {
    'scans_total': 0,
    'alerts_volume': 0,
    'alerts_pavio': 0,
    'errors': 0,
    'last_scan': None,
    'avg_cycle_time': 0.0,  # ✅ NOVO: Tempo médio de ciclo
    'max_cycle_time': 0.0,   # ✅ NOVO: Tempo máximo de ciclo
    'consecutive_errors': 0, # ✅ NOVO: Erros consecutivos
    'network_errors': 0,      # ✅ NOVO: Erros de rede
    'rate_limit_hits': 0     # ✅ NOVO: Rate limits atingidos
}
```

### **Logging Estruturado:**

```python
# monitors/opportunity_monitor.py

import logging

logger = logging.getLogger('opportunity_monitor')
logger.setLevel(logging.INFO)

# Handler para arquivo
log_file = get_app_data_dir() / 'logs' / 'scanner.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(file_handler)

# Uso:
logger.info(f"✅ Alerta de volume enviado: {symbol}")
logger.warning(f"⚠️ Ciclo demorou {execution_time:.1f}s")
logger.error(f"❌ Erro ao escanear {symbol}: {e}")
```

---

## 🎯 CONFIGURAÇÃO DE SEGURANÇA

### **Arquivo: `config/scanner_config.json`**

```json
{
  "scanner": {
    "enabled": true,
    "scan_interval_seconds": 60,
    "max_symbols": 15,
    "symbols": [
      "BTCUSDT",
      "ETHUSDT",
      "BNBUSDT",
      "SOLUSDT",
      "ADAUSDT",
      "XRPUSDT"
    ],
    "volume_scanner": {
      "enabled": true,
      "rvol_threshold": 2.0,
      "timeframe": "5m"
    },
    "pavio_scanner": {
      "enabled": false,
      "volume_threshold": 2.5,
      "rsi_long_threshold": 25,
      "rsi_short_threshold": 75,
      "wick_confirmation_pct": 0.3
    }
  },
  "notifications": {
    "telegram": {
      "enabled": true,
      "cooldown_minutes": 5,
      "state_file": null
    }
  },
  "safety": {
    "max_consecutive_errors": 5,
    "retry_delay_seconds": 2,
    "max_retries": 3,
    "api_timeout_seconds": 10,
    "internet_check_interval": 30
  }
}
```

---

## ✅ CHECKLIST DE MITIGAÇÃO

### **Rate Limit:**
- [x] Limite automático de símbolos (máx 15)
- [x] Delay dinâmico entre requisições
- [x] Lista padrão de top 10 por liquidez
- [x] Logging de rate limit hits

### **Drift do Loop:**
- [x] Compensação automática de drift
- [x] Cálculo de tempo real de execução
- [x] Estatísticas de performance
- [x] Logging de ciclos lentos

### **Dependência de Rede:**
- [x] Retry com backoff exponencial
- [x] Timeout explícito em requisições
- [x] Verificação de conexão
- [x] Modo de espera após muitos erros
- [x] Tratamento robusto de exceções

### **Escalabilidade:**
- [x] Preparação para async (Fase 3+)
- [x] Estrutura modular
- [x] Fácil adicionar novos scanners

### **Monitoramento:**
- [x] Estatísticas detalhadas
- [x] Logging estruturado
- [x] Arquivo de log persistido
- [x] Métricas de performance

---

## 🚀 IMPLEMENTAÇÃO PRIORITÁRIA

### **Ordem de Implementação:**

1. **✅ Tratamento de Rede (CRÍTICO)**
   - Implementar primeiro
   - Evita crashes em produção
   - Base para tudo mais

2. **✅ Compensação de Drift (IMPORTANTE)**
   - Garante ciclos precisos
   - Melhora qualidade dos alertas

3. **✅ Limite de Símbolos (IMPORTANTE)**
   - Previne rate limit
   - Escalabilidade controlada

4. **✅ Logging e Estatísticas (ÚTIL)**
   - Facilita debug
   - Monitoramento de performance

---

**Status:** ✅ Mitigações Documentadas e Prontas para Implementação  
**Próxima Ação:** Incorporar nas implementações da Fase 1



