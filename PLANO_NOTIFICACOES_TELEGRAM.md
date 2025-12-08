# 📱 PLANO DE IMPLEMENTAÇÃO: NOTIFICAÇÕES TELEGRAM - CAÇADOR DE PAVIO

**Data:** 25 de Outubro de 2025  
**Objetivo:** Implementar sistema de notificações automáticas do Telegram para alertas de oportunidades baseados em Volume Explosivo + RSI Extremo

---

## 🎯 VISÃO GERAL

Transformar o SNE RADAR de um "painel de indicadores" para um **"Scanner de Oportunidades"** que:
- ✅ Monitora múltiplos pares em background
- ✅ Filtra 282 velas de "lixo" automaticamente
- ✅ Alerta apenas nas 5-6 velas de ouro por dia
- ✅ Economiza tempo e evita fadiga mental

---

## 📋 ESTRATÉGIA PROPOSTA

### **Algoritmo "Caçador de Pavio"**

#### **Fase 1: Alerta Simples (RVOL > 2.0)**
- **Objetivo:** Eliminar 80% do tempo olhando gráficos
- **Condição:** Volume Relativo > 2.0x
- **Complexidade:** Baixa
- **Impacto:** Alto

#### **Fase 2: Alerta Completo (Volume M30 + RSI M5)**
- **Objetivo:** Detectar "Agulhadas" em formação
- **Condições:**
  1. Volume M30 > 2.5x média dos últimos 20 períodos
  2. RSI M5 > 75 (Short) ou < 25 (Long)
- **Complexidade:** Média
- **Impacto:** Muito Alto

---

## 🏗️ ARQUITETURA PROPOSTA

### **Estrutura de Módulos**

```
SNE_RADAR_CORE/
│
├── scanners/
│   ├── __init__.py
│   ├── volume_scanner.py          # Scanner de volume (Fase 1)
│   ├── pavio_scanner.py            # Scanner completo (Fase 2)
│   └── scanner_base.py             # Classe base para scanners
│
├── notifications/
│   ├── __init__.py
│   ├── telegram_notifier.py       # Envio de notificações Telegram
│   ├── alert_formatter.py          # Formatação de mensagens
│   └── notification_manager.py     # Gerenciador de notificações
│
└── monitors/
    ├── __init__.py
    ├── opportunity_monitor.py      # Monitor contínuo de oportunidades
    └── cooldown_manager.py          # Controle de cooldown entre alertas
```

---

## 📊 LÓGICA DE DETECÇÃO

### **Fase 1: Alerta RVOL Simples**

```python
def detectar_volume_explosivo(symbol: str, timeframe: str = '5m') -> Dict:
    """
    Detecta volume explosivo (RVOL > 2.0)
    
    Retorna:
    {
        'triggered': bool,
        'rvol': float,
        'volume_atual': float,
        'volume_medio': float,
        'timestamp': datetime
    }
    """
    # 1. Buscar dados
    df = buscar_dados_binance(symbol, timeframe, limit=21)
    
    # 2. Calcular volume médio (últimos 20 períodos)
    volume_medio = df['volume'].iloc[:-1].mean()  # Excluir última vela
    
    # 3. Volume atual (última vela)
    volume_atual = df['volume'].iloc[-1]
    
    # 4. Calcular RVOL (Relative Volume)
    rvol = volume_atual / volume_medio if volume_medio > 0 else 0
    
    # 5. Verificar condição
    triggered = rvol > 2.0
    
    return {
        'triggered': triggered,
        'rvol': rvol,
        'volume_atual': volume_atual,
        'volume_medio': volume_medio,
        'timestamp': datetime.now(),
        'symbol': symbol,
        'timeframe': timeframe
    }
```

### **Fase 2: Alerta Completo "Caçador de Pavio"**

```python
def detectar_agulhada_formacao(symbol: str) -> Dict:
    """
    Detecta "Agulhada em Formação" baseado em:
    - Volume M30 > 2.5x média
    - RSI M5 extremo (>75 ou <25)
    
    Retorna:
    {
        'triggered': bool,
        'tipo': 'LONG' | 'SHORT' | None,
        'rvol_m30': float,
        'rsi_m5': float,
        'preco_atual': float,
        'timestamp': datetime
    }
    """
    # 1. Buscar dados M30 (para volume)
    df_m30 = buscar_dados_binance(symbol, '30m', limit=21)
    
    # 2. Buscar dados M5 (para RSI)
    df_m5 = buscar_dados_binance(symbol, '5m', limit=15)
    
    # 3. Calcular Volume M30
    volume_medio_m30 = df_m30['volume'].iloc[:-1].mean()
    volume_atual_m30 = df_m30['volume'].iloc[-1]
    rvol_m30 = volume_atual_m30 / volume_medio_m30 if volume_medio_m30 > 0 else 0
    
    # 4. Calcular RSI M5
    rsi_m5 = calcular_rsi(df_m5['close'], period=14)
    rsi_atual = rsi_m5.iloc[-1]
    
    # 5. Verificar condições
    volume_ok = rvol_m30 > 2.5
    rsi_extremo_long = rsi_atual < 25
    rsi_extremo_short = rsi_atual > 75
    
    triggered = False
    tipo = None
    
    if volume_ok and rsi_extremo_long:
        triggered = True
        tipo = 'LONG'
    elif volume_ok and rsi_extremo_short:
        triggered = True
        tipo = 'SHORT'
    
    return {
        'triggered': triggered,
        'tipo': tipo,
        'rvol_m30': rvol_m30,
        'rsi_m5': rsi_atual,
        'preco_atual': df_m5['close'].iloc[-1],
        'timestamp': datetime.now(),
        'symbol': symbol
    }
```

---

## 🔔 SISTEMA DE NOTIFICAÇÕES

### **Formato de Mensagem Telegram**

#### **Fase 1: Alerta RVOL Simples**
```
🚨 VOLUME EXPLOSIVO DETECTADO

📊 BTCUSDT - 5m
💥 RVOL: 2.8x
📈 Volume: 1,234,567 BTC
📊 Média: 440,202 BTC

⏰ 14:35:22
💡 Possível movimento significativo em formação
```

#### **Fase 2: Alerta Completo**
```
🎯 AGULHADA EM FORMAÇÃO

📊 BTCUSDT
🟢 SINAL: LONG
💰 Preço: $65,432.10

📊 Volume M30: 3.2x média
📉 RSI M5: 22.5 (Sobre-vendido)

⏰ 14:35:22
💡 Entrada na ponta do pavio mensal
⚠️ Confirmar com análise adicional antes de operar
```

---

## ⚙️ IMPLEMENTAÇÃO TÉCNICA

### **1. Módulo: `scanners/volume_scanner.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner de Volume Explosivo
Detecta RVOL > 2.0 (Fase 1)
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Optional, List
from sne_radar_web import buscar_dados_binance

class VolumeScanner:
    """Scanner de volume explosivo"""
    
    def __init__(self, rvol_threshold: float = 2.0):
        self.rvol_threshold = rvol_threshold
        self.last_scans = {}  # Cache de últimos scans
    
    def scan_symbol(self, symbol: str, timeframe: str = '5m') -> Optional[Dict]:
        """
        Escaneia um símbolo para volume explosivo
        
        Returns:
            Dict com dados do alerta ou None se não disparou
        """
        try:
            # Buscar dados
            df = buscar_dados_binance(symbol, timeframe, limit=21, skip_rate_limit=True)
            
            if df is None or len(df) < 21:
                return None
            
            # Calcular volume médio (excluindo última vela)
            volume_medio = df['volume'].iloc[:-1].mean()
            volume_atual = df['volume'].iloc[-1]
            
            # Calcular RVOL
            rvol = volume_atual / volume_medio if volume_medio > 0 else 0
            
            # Verificar condição
            if rvol >= self.rvol_threshold:
                return {
                    'triggered': True,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'rvol': rvol,
                    'volume_atual': float(volume_atual),
                    'volume_medio': float(volume_medio),
                    'preco_atual': float(df['close'].iloc[-1]),
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao escanear {symbol}: {e}")
            return None
    
    def scan_multiple(self, symbols: List[str], timeframe: str = '5m') -> List[Dict]:
        """Escaneia múltiplos símbolos"""
        alerts = []
        
        for symbol in symbols:
            result = self.scan_symbol(symbol, timeframe)
            if result and result.get('triggered'):
                alerts.append(result)
        
        return alerts
```

### **2. Módulo: `scanners/pavio_scanner.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner "Caçador de Pavio"
Detecta Volume M30 Explosivo + RSI M5 Extremo
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from sne_radar_web import buscar_dados_binance
from indicadores import calcular_indicadores

class PavioScanner:
    """Scanner completo de agulhadas"""
    
    def __init__(self, 
                 volume_threshold: float = 2.5,
                 rsi_long_threshold: float = 25,
                 rsi_short_threshold: float = 75):
        self.volume_threshold = volume_threshold
        self.rsi_long_threshold = rsi_long_threshold
        self.rsi_short_threshold = rsi_short_threshold
    
    def calcular_rsi(self, closes: pd.Series, period: int = 14) -> pd.Series:
        """Calcula RSI"""
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def scan_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Escaneia símbolo para agulhada em formação
        
        Returns:
            Dict com dados do alerta ou None
        """
        try:
            # 1. Buscar dados M30 (volume)
            df_m30 = buscar_dados_binance(symbol, '30m', limit=21, skip_rate_limit=True)
            if df_m30 is None or len(df_m30) < 21:
                return None
            
            # 2. Buscar dados M5 (RSI)
            df_m5 = buscar_dados_binance(symbol, '5m', limit=15, skip_rate_limit=True)
            if df_m5 is None or len(df_m5) < 15:
                return None
            
            # 3. Calcular Volume M30
            volume_medio_m30 = df_m30['volume'].iloc[:-1].mean()
            volume_atual_m30 = df_m30['volume'].iloc[-1]
            rvol_m30 = volume_atual_m30 / volume_medio_m30 if volume_medio_m30 > 0 else 0
            
            # 4. Calcular RSI M5
            rsi_series = self.calcular_rsi(df_m5['close'], period=14)
            rsi_atual = rsi_series.iloc[-1]
            
            # 5. Verificar condições
            volume_ok = rvol_m30 >= self.volume_threshold
            rsi_extremo_long = rsi_atual <= self.rsi_long_threshold
            rsi_extremo_short = rsi_atual >= self.rsi_short_threshold
            
            triggered = False
            tipo = None
            
            if volume_ok and rsi_extremo_long:
                triggered = True
                tipo = 'LONG'
            elif volume_ok and rsi_extremo_short:
                triggered = True
                tipo = 'SHORT'
            
            if triggered:
                return {
                    'triggered': True,
                    'symbol': symbol,
                    'tipo': tipo,
                    'rvol_m30': float(rvol_m30),
                    'rsi_m5': float(rsi_atual),
                    'preco_atual': float(df_m5['close'].iloc[-1]),
                    'volume_atual_m30': float(volume_atual_m30),
                    'volume_medio_m30': float(volume_medio_m30),
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao escanear {symbol}: {e}")
            return None
```

### **3. Módulo: `notifications/telegram_notifier.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notificador Telegram para Alertas de Oportunidades
"""

from datetime import datetime
from typing import Dict, Optional
import requests
import os

# Importar função de envio existente
try:
    from xenos_bot import enviar_oraculo
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ xenos_bot não disponível")

class TelegramNotifier:
    """Notificador Telegram para alertas"""
    
    def __init__(self):
        self.enabled = TELEGRAM_AVAILABLE
        self.cooldown_minutes = 5  # Cooldown entre alertas do mesmo símbolo
        self.last_alerts = {}  # {symbol: timestamp}
    
    def format_volume_alert(self, data: Dict) -> str:
        """Formata mensagem de alerta de volume"""
        symbol = data['symbol']
        timeframe = data.get('timeframe', '5m')
        rvol = data['rvol']
        volume_atual = data['volume_atual']
        volume_medio = data['volume_medio']
        preco = data['preco_atual']
        timestamp = data['timestamp'].strftime('%H:%M:%S')
        
        return f"""🚨 <b>VOLUME EXPLOSIVO DETECTADO</b>

📊 <b>{symbol}</b> - {timeframe}
💥 <b>RVOL: {rvol:.2f}x</b>
📈 Volume: {volume_atual:,.0f}
📊 Média: {volume_medio:,.0f}
💰 Preço: ${preco:,.2f}

⏰ {timestamp}
💡 Possível movimento significativo em formação"""

    def format_pavio_alert(self, data: Dict) -> str:
        """Formata mensagem de alerta de agulhada"""
        symbol = data['symbol']
        tipo = data['tipo']
        rvol = data['rvol_m30']
        rsi = data['rsi_m5']
        preco = data['preco_atual']
        timestamp = data['timestamp'].strftime('%H:%M:%S')
        
        emoji = '🟢' if tipo == 'LONG' else '🔴'
        direcao = 'COMPRAR' if tipo == 'LONG' else 'VENDER'
        rsi_status = 'Sobre-vendido' if tipo == 'LONG' else 'Sobre-comprado'
        
        return f"""🎯 <b>AGULHADA EM FORMAÇÃO</b>

📊 <b>{symbol}</b>
{emoji} <b>SINAL: {direcao}</b>
💰 Preço: ${preco:,.2f}

📊 Volume M30: <b>{rvol:.2f}x</b> média
📉 RSI M5: {rsi:.1f} ({rsi_status})

⏰ {timestamp}
💡 Entrada na ponta do pavio mensal
⚠️ Confirmar com análise adicional antes de operar"""

    def can_send_alert(self, symbol: str) -> bool:
        """Verifica se pode enviar alerta (cooldown)"""
        if symbol not in self.last_alerts:
            return True
        
        last_alert = self.last_alerts[symbol]
        elapsed = (datetime.now() - last_alert).total_seconds() / 60
        
        return elapsed >= self.cooldown_minutes
    
    def send_volume_alert(self, data: Dict) -> bool:
        """Envia alerta de volume"""
        if not self.enabled:
            print("⚠️ Telegram não disponível")
            return False
        
        symbol = data['symbol']
        
        # Verificar cooldown
        if not self.can_send_alert(symbol):
            print(f"⏳ Alerta de {symbol} em cooldown")
            return False
        
        # Formatar e enviar
        mensagem = self.format_volume_alert(data)
        sucesso = enviar_oraculo(mensagem)
        
        if sucesso:
            self.last_alerts[symbol] = datetime.now()
            print(f"✅ Alerta de volume enviado: {symbol}")
        
        return sucesso
    
    def send_pavio_alert(self, data: Dict) -> bool:
        """Envia alerta de agulhada"""
        if not self.enabled:
            print("⚠️ Telegram não disponível")
            return False
        
        symbol = data['symbol']
        
        # Verificar cooldown
        if not self.can_send_alert(symbol):
            print(f"⏳ Alerta de {symbol} em cooldown")
            return False
        
        # Formatar e enviar
        mensagem = self.format_pavio_alert(data)
        sucesso = enviar_oraculo(mensagem)
        
        if sucesso:
            self.last_alerts[symbol] = datetime.now()
            print(f"✅ Alerta de agulhada enviado: {symbol} ({data['tipo']})")
        
        return sucesso
```

### **4. Módulo: `monitors/opportunity_monitor.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Contínuo de Oportunidades
Roda em background e dispara alertas quando detecta condições
"""

import time
import threading
from datetime import datetime
from typing import List, Dict
from scanners.volume_scanner import VolumeScanner
from scanners.pavio_scanner import PavioScanner
from notifications.telegram_notifier import TelegramNotifier

class OpportunityMonitor:
    """Monitor contínuo de oportunidades"""
    
    def __init__(self, 
                 symbols: List[str] = None,
                 scan_interval: int = 60,  # 1 minuto
                 enable_volume_scanner: bool = True,
                 enable_pavio_scanner: bool = False):
        
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
        self.scan_interval = scan_interval
        self.running = False
        self.thread = None
        
        # Scanners
        self.volume_scanner = VolumeScanner(rvol_threshold=2.0) if enable_volume_scanner else None
        self.pavio_scanner = PavioScanner() if enable_pavio_scanner else None
        
        # Notificador
        self.notifier = TelegramNotifier()
        
        # Estatísticas
        self.stats = {
            'scans_total': 0,
            'alerts_volume': 0,
            'alerts_pavio': 0,
            'last_scan': None
        }
    
    def start(self):
        """Inicia monitoramento"""
        if self.running:
            print("⚠️ Monitor já está rodando")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"✅ Monitor de oportunidades iniciado")
        print(f"   Símbolos: {', '.join(self.symbols)}")
        print(f"   Intervalo: {self.scan_interval}s")
        print(f"   Volume Scanner: {'✅' if self.volume_scanner else '❌'}")
        print(f"   Pavio Scanner: {'✅' if self.pavio_scanner else '❌'}")
    
    def stop(self):
        """Para monitoramento"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🛑 Monitor de oportunidades parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                # Escanear todos os símbolos
                for symbol in self.symbols:
                    if not self.running:
                        break
                    
                    # Scanner de Volume (Fase 1)
                    if self.volume_scanner:
                        result = self.volume_scanner.scan_symbol(symbol, timeframe='5m')
                        if result and result.get('triggered'):
                            self.notifier.send_volume_alert(result)
                            self.stats['alerts_volume'] += 1
                    
                    # Scanner de Pavio (Fase 2)
                    if self.pavio_scanner:
                        result = self.pavio_scanner.scan_symbol(symbol)
                        if result and result.get('triggered'):
                            self.notifier.send_pavio_alert(result)
                            self.stats['alerts_pavio'] += 1
                    
                    self.stats['scans_total'] += 1
                    
                    # Pequeno delay entre símbolos
                    time.sleep(1)
                
                self.stats['last_scan'] = datetime.now()
                
                # Aguardar próximo ciclo
                time.sleep(self.scan_interval)
                
            except Exception as e:
                print(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(10)  # Aguardar antes de tentar novamente
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do monitor"""
        return {
            **self.stats,
            'running': self.running,
            'symbols_count': len(self.symbols)
        }
```

---

## 🔄 INTEGRAÇÃO COM SISTEMA EXISTENTE

### **Opção 1: Integrar no `main.py` (Terminal)**

```python
# Adicionar ao main.py
from monitors.opportunity_monitor import OpportunityMonitor

# Inicializar monitor
monitor = OpportunityMonitor(
    symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT'],
    scan_interval=60,  # 1 minuto
    enable_volume_scanner=True,
    enable_pavio_scanner=False  # Ativar depois
)

# Iniciar em background
monitor.start()
```

### **Opção 2: Serviço Separado (Recomendado)**

Criar `scanner_service.py` que roda independente:

```python
#!/usr/bin/env python3
# scanner_service.py
"""
Serviço de Scanner de Oportunidades
Roda em background e envia notificações Telegram
"""

from monitors.opportunity_monitor import OpportunityMonitor
import signal
import sys

def signal_handler(sig, frame):
    print('\n🛑 Parando scanner...')
    monitor.stop()
    sys.exit(0)

if __name__ == '__main__':
    # Configurar handler de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Criar e iniciar monitor
    monitor = OpportunityMonitor(
        symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT'],
        scan_interval=60,  # 1 minuto
        enable_volume_scanner=True,
        enable_pavio_scanner=False
    )
    
    monitor.start()
    
    # Manter rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
```

---

## 📝 PLANO DE IMPLEMENTAÇÃO

### **Fase 1: Alerta RVOL Simples (1-2 dias)**

1. ✅ Criar `scanners/volume_scanner.py`
2. ✅ Criar `notifications/telegram_notifier.py`
3. ✅ Testar com 1 símbolo (BTCUSDT)
4. ✅ Validar envio de notificações
5. ✅ Adicionar cooldown entre alertas
6. ✅ Testar com múltiplos símbolos

**Resultado Esperado:**
- Alerta quando RVOL > 2.0
- Notificação Telegram formatada
- Cooldown de 5 minutos entre alertas do mesmo símbolo

---

### **Fase 2: Alerta Completo "Caçador de Pavio" (2-3 dias)**

1. ✅ Criar `scanners/pavio_scanner.py`
2. ✅ Implementar lógica M30 + M5
3. ✅ Integrar com notificador
4. ✅ Testar detecção de LONG/SHORT
5. ✅ Validar com dados reais
6. ✅ Ajustar thresholds se necessário

**Resultado Esperado:**
- Alerta quando Volume M30 > 2.5x E RSI M5 extremo
- Identificação de LONG/SHORT
- Notificação detalhada com contexto

---

### **Fase 3: Monitor Contínuo (1 dia)**

1. ✅ Criar `monitors/opportunity_monitor.py`
2. ✅ Implementar loop de monitoramento
3. ✅ Adicionar estatísticas
4. ✅ Integrar com sistema existente
5. ✅ Testar em background

**Resultado Esperado:**
- Monitor roda em background
- Escaneia múltiplos símbolos automaticamente
- Envia alertas quando detecta oportunidades

---

### **Fase 4: Otimizações (Opcional)**

1. ✅ Cache de dados para reduzir chamadas API
2. ✅ Rate limiting inteligente
3. ✅ Logs e estatísticas
4. ✅ Configuração via arquivo
5. ✅ Dashboard de monitoramento

---

## ⚙️ CONFIGURAÇÃO

### **Arquivo: `config/scanner_config.json`**

```json
{
  "scanner": {
    "enabled": true,
    "scan_interval_seconds": 60,
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
      "rsi_short_threshold": 75
    }
  },
  "notifications": {
    "telegram": {
      "enabled": true,
      "cooldown_minutes": 5
    }
  }
}
```

---

## 🧪 TESTES

### **Teste 1: Volume Scanner**

```python
from scanners.volume_scanner import VolumeScanner

scanner = VolumeScanner(rvol_threshold=2.0)
result = scanner.scan_symbol('BTCUSDT', '5m')

if result and result['triggered']:
    print(f"✅ Alerta disparado!")
    print(f"   RVOL: {result['rvol']:.2f}x")
else:
    print("❌ Nenhum alerta")
```

### **Teste 2: Pavio Scanner**

```python
from scanners.pavio_scanner import PavioScanner

scanner = PavioScanner()
result = scanner.scan_symbol('BTCUSDT')

if result and result['triggered']:
    print(f"✅ Agulhada detectada!")
    print(f"   Tipo: {result['tipo']}")
    print(f"   RVOL M30: {result['rvol_m30']:.2f}x")
    print(f"   RSI M5: {result['rsi_m5']:.1f}")
```

### **Teste 3: Notificador**

```python
from notifications.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()

# Teste alerta de volume
data = {
    'symbol': 'BTCUSDT',
    'timeframe': '5m',
    'rvol': 2.8,
    'volume_atual': 1234567,
    'volume_medio': 440202,
    'preco_atual': 65432.10,
    'timestamp': datetime.now()
}

notifier.send_volume_alert(data)
```

---

## 📊 MÉTRICAS E ESTATÍSTICAS

### **O que Monitorar:**

1. **Taxa de Detecção:**
   - Quantos alertas por dia
   - Quantos falsos positivos
   - Quantos verdadeiros positivos

2. **Performance:**
   - Tempo de resposta do scanner
   - Uso de API (rate limits)
   - Uso de memória

3. **Eficácia:**
   - % de alertas que resultaram em movimento
   - Tempo médio entre alerta e movimento
   - R:R médio das oportunidades detectadas

---

## 🎯 RESULTADO ESPERADO

### **Antes:**
- ❌ Olhar 288 velas de 5min por dia
- ❌ Fadiga mental após 50-100 velas
- ❌ Perder oportunidades por cansaço
- ❌ Ver padrões que não existem (alucinação)

### **Depois:**
- ✅ SNE filtra automaticamente
- ✅ Apenas 5-6 alertas por dia (velas de ouro)
- ✅ Notificação Telegram quando detecta
- ✅ Foco apenas nas oportunidades reais
- ✅ Entrada na ponta do pavio mensal

---

## ⚠️ CONSIDERAÇÕES IMPORTANTES

### **1. Rate Limiting da Binance**
- Limite: 1200 requests/minuto
- Scanner precisa respeitar limites
- Usar cache quando possível

### **2. Cooldown Entre Alertas**
- Evitar spam de notificações
- Cooldown de 5 minutos por símbolo
- Cooldown global opcional

### **3. Falsos Positivos**
- Volume alto pode ser manipulação
- RSI extremo pode continuar extremo
- Sempre confirmar com análise adicional

### **4. Configuração Flexível**
- Thresholds ajustáveis
- Ativar/desativar scanners
- Adicionar/remover símbolos

---

## 🚀 PRÓXIMOS PASSOS (QUANDO APROVADO)

1. ✅ Revisar este plano
2. ✅ Aprovar arquitetura proposta
3. ✅ Implementar Fase 1 (RVOL simples)
4. ✅ Testar e validar
5. ✅ Implementar Fase 2 (Pavio completo)
6. ✅ Integrar com sistema existente
7. ✅ Documentar uso

---

**Status:** 📋 Plano Completo - Aguardando Aprovação  
**Próxima Ação:** Revisar e aprovar antes de implementar



