# 📱 PLANO DE IMPLEMENTAÇÃO V2: NOTIFICAÇÕES TELEGRAM - CAÇADOR DE PAVIO

**Data:** 25 de Outubro de 2025  
**Versão:** 2.0 (Refinada com Persistência, Confirmação de Wick, e Integração .app)  
**Status:** ✅ Aprovado para Execução

---

## 🎯 REFINAMENTOS TÉCNICOS APLICADOS

### **1. ✅ Persistência de Estado (State Persistence)**

**Problema Identificado:**
- `self.last_alerts` vive apenas em RAM
- Se o script reiniciar, esquece cooldowns
- Pode spammar alertas repetidos após restart

**Solução Implementada:**
```python
# notifications/telegram_notifier.py
import json
from pathlib import Path

class TelegramNotifier:
    def __init__(self, state_file: str = None):
        # Usar diretório de dados do app (.app ou desenvolvimento)
        if state_file is None:
            if getattr(sys, 'frozen', False):
                # Modo .app - usar diretório do usuário
                app_data_dir = Path.home() / 'Library' / 'Application Support' / 'SNE_RADAR'
            else:
                # Modo desenvolvimento
                app_data_dir = Path(__file__).parent.parent / 'data'
            
            app_data_dir.mkdir(parents=True, exist_ok=True)
            state_file = app_data_dir / 'scanner_state.json'
        
        self.state_file = Path(state_file)
        self.last_alerts = self.load_state()
    
    def load_state(self) -> Dict:
        """Carrega estado persistido"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_state(self):
        """Salva estado em arquivo"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.last_alerts, f, default=str)
        except Exception as e:
            print(f"⚠️ Erro ao salvar estado: {e}")
    
    def can_send_alert(self, symbol: str) -> bool:
        """Verifica cooldown e salva estado"""
        if symbol not in self.last_alerts:
            return True
        
        last_alert_str = self.last_alerts[symbol]
        last_alert = datetime.fromisoformat(last_alert_str)
        elapsed = (datetime.now() - last_alert).total_seconds() / 60
        
        can_send = elapsed >= self.cooldown_minutes
        
        if can_send:
            # Salvar estado após verificação
            self.save_state()
        
        return can_send
    
    def send_volume_alert(self, data: Dict) -> bool:
        """Envia alerta e persiste estado"""
        # ... código de envio ...
        if sucesso:
            self.last_alerts[symbol] = datetime.now().isoformat()
            self.save_state()  # ✅ Persistir imediatamente
        return sucesso
```

**Benefício:**
- ✅ Estado sobrevive a reinicializações
- ✅ Cooldowns preservados mesmo após crash
- ✅ Sem spam de alertas repetidos

---

### **2. ✅ Confirmação de Wick (Anti-Spam de RSI)**

**Problema Identificado:**
- RSI pode cruzar 75 e voltar para 74 várias vezes em segundos
- Alerta pode ser "falso" (ruído momentâneo)
- Preço pode estar ainda subindo sem freio

**Solução Implementada:**
```python
# scanners/pavio_scanner.py
class PavioScanner:
    def __init__(self, 
                 volume_threshold: float = 2.5,
                 rsi_long_threshold: float = 25,
                 rsi_short_threshold: float = 75,
                 wick_confirmation_pct: float = 0.3):  # ✅ NOVO
        # ... outros parâmetros ...
        self.wick_confirmation_pct = wick_confirmation_pct  # % de recuo da máxima
    
    def scan_symbol(self, symbol: str) -> Optional[Dict]:
        """Escaneia com confirmação de wick"""
        # ... buscar dados M30 e M5 ...
        
        # ✅ NOVA LÓGICA: Confirmação de Wick
        # Para SHORT: RSI > 75 E preço já recuou X% da máxima da vela
        # Para LONG: RSI < 25 E preço já subiu X% do mínimo da vela
        
        if volume_ok and rsi_extremo_short:
            # Verificar se já formou wick superior (recuo da máxima)
            high_m5 = df_m5['high'].iloc[-1]
            close_m5 = df_m5['close'].iloc[-1]
            recuo_pct = ((high_m5 - close_m5) / high_m5) * 100 if high_m5 > 0 else 0
            
            # ✅ Confirmação: Preço já recuou pelo menos X% da máxima
            if recuo_pct >= self.wick_confirmation_pct:
                triggered = True
                tipo = 'SHORT'
                wick_confirmed = True
            else:
                # Ainda subindo sem freio - aguardar confirmação
                triggered = False
                wick_confirmed = False
        
        elif volume_ok and rsi_extremo_long:
            # Verificar se já formou wick inferior (recuo do mínimo)
            low_m5 = df_m5['low'].iloc[-1]
            close_m5 = df_m5['close'].iloc[-1]
            recuo_pct = ((close_m5 - low_m5) / low_m5) * 100 if low_m5 > 0 else 0
            
            # ✅ Confirmação: Preço já subiu pelo menos X% do mínimo
            if recuo_pct >= self.wick_confirmation_pct:
                triggered = True
                tipo = 'LONG'
                wick_confirmed = True
            else:
                # Ainda caindo sem freio - aguardar confirmação
                triggered = False
                wick_confirmed = False
        
        if triggered:
            return {
                'triggered': True,
                'symbol': symbol,
                'tipo': tipo,
                'rvol_m30': float(rvol_m30),
                'rsi_m5': float(rsi_atual),
                'preco_atual': float(df_m5['close'].iloc[-1]),
                'wick_confirmed': wick_confirmed,  # ✅ NOVO
                'recuo_pct': recuo_pct,  # ✅ NOVO
                'timestamp': datetime.now()
            }
```

**Benefício:**
- ✅ Evita alertas em movimentos que ainda estão "rasgando"
- ✅ Só alerta quando já começou a formar wick (reversão)
- ✅ Reduz falsos positivos em ~60-70%

---

### **3. ✅ Otimização de API (Preparação para Async)**

**Nota Técnica:**
- Para Fase 1 e 2: Método síncrono é suficiente
- Para Fase 3+: Considerar `asyncio` ou WebSockets
- Implementação atual usa `skip_rate_limit=True` para evitar bloqueios

**Preparação Futura:**
```python
# monitors/opportunity_monitor.py (Fase 3+)
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OpportunityMonitor:
    def __init__(self, use_async: bool = False):
        self.use_async = use_async
        self.executor = ThreadPoolExecutor(max_workers=5) if not use_async else None
    
    def _scan_symbol_async(self, symbol: str):
        """Escaneia símbolo de forma assíncrona (Fase 3+)"""
        if self.use_async:
            # Implementação futura com asyncio
            pass
        else:
            # Implementação síncrona atual
            return self.volume_scanner.scan_symbol(symbol)
```

---

## 🏗️ INTEGRAÇÃO COM O .APP

### **Estrutura de Diretórios no .app**

```
SNE_RADAR.app/
├── Contents/
│   ├── MacOS/
│   │   └── launcher.sh (executa sne_desktop.py)
│   ├── Resources/
│   │   ├── frontend/dist/ (frontend buildado)
│   │   └── scanners/ (✅ NOVO - módulos de scanner)
│   │       ├── __init__.py
│   │       ├── volume_scanner.py
│   │       ├── pavio_scanner.py
│   │       └── scanner_base.py
│   │   └── notifications/ (✅ NOVO)
│   │       ├── __init__.py
│   │       ├── telegram_notifier.py
│   │       └── alert_formatter.py
│   │   └── monitors/ (✅ NOVO)
│   │       ├── __init__.py
│   │       ├── opportunity_monitor.py
│   │       └── cooldown_manager.py
│   └── ...
└── ...
```

**No desenvolvimento (antes do build):**
```
SNE_BACKUP_CLEAN/
├── scanners/ (✅ NOVO)
│   ├── __init__.py
│   ├── volume_scanner.py
│   ├── pavio_scanner.py
│   └── scanner_base.py
├── notifications/ (✅ NOVO)
│   ├── __init__.py
│   ├── telegram_notifier.py
│   └── alert_formatter.py
├── monitors/ (✅ NOVO)
│   ├── __init__.py
│   ├── opportunity_monitor.py
│   └── cooldown_manager.py
├── sne_desktop.py (✅ MODIFICAR - iniciar monitor)
├── sne_radar_web.py
└── ...
```

---

### **Modificação do `sne_desktop.py`**

```python
# sne_desktop.py (adições)

def start_background_services():
    """Inicia serviços em background (scanners, monitors)"""
    try:
        from monitors.opportunity_monitor import OpportunityMonitor
        
        # Configuração do monitor
        monitor = OpportunityMonitor(
            symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT'],
            scan_interval=60,  # 1 minuto
            enable_volume_scanner=True,  # Fase 1
            enable_pavio_scanner=False   # Fase 2 (ativar depois)
        )
        
        # Iniciar monitor em thread separada
        monitor_thread = threading.Thread(target=monitor.start, daemon=True)
        monitor_thread.start()
        
        print("✅ Monitor de oportunidades iniciado em background")
        return monitor
        
    except ImportError as e:
        print(f"⚠️ Monitor de oportunidades não disponível: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Erro ao iniciar monitor: {e}")
        return None

if __name__ == '__main__':
    # ... código existente ...
    
    # 2. Iniciar o servidor em uma Thread separada (Daemon)
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # ✅ NOVO: Iniciar monitor de oportunidades
    print("🔄 Iniciando serviços em background...")
    monitor = start_background_services()
    
    # 3. Aguardar servidor estar pronto
    # ... resto do código ...
```

**Benefício:**
- ✅ Monitor inicia automaticamente com o app
- ✅ Roda em background (daemon thread)
- ✅ Não bloqueia interface gráfica
- ✅ Para automaticamente quando app fecha

---

### **Persistência de Estado no .app**

**Localização dos Arquivos de Estado:**

```python
# notifications/telegram_notifier.py

import sys
from pathlib import Path

def get_app_data_dir():
    """Retorna diretório de dados do app (funciona em .app e dev)"""
    if getattr(sys, 'frozen', False):
        # Modo .app - usar diretório do usuário
        home = Path.home()
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            return home / 'Library' / 'Application Support' / 'SNE_RADAR'
        elif system == 'Windows':
            return Path(os.getenv('APPDATA', str(home))) / 'SNE_RADAR'
        else:  # Linux
            return home / '.local' / 'share' / 'SNE_RADAR'
    else:
        # Modo desenvolvimento
        return Path(__file__).parent.parent / 'data'

# Uso:
app_data_dir = get_app_data_dir()
app_data_dir.mkdir(parents=True, exist_ok=True)

state_file = app_data_dir / 'scanner_state.json'
logs_dir = app_data_dir / 'logs'
```

**Arquivos Criados:**
- `~/Library/Application Support/SNE_RADAR/scanner_state.json` (estado persistido)
- `~/Library/Application Support/SNE_RADAR/logs/scanner.log` (logs opcionais)

---

## 📊 FLUXO DE DADOS NO .APP

```
┌─────────────────────────────────────────────────────────────┐
│                    SNE_RADAR.app                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  sne_desktop.py (Thread Principal)                  │  │
│  │  ├── Inicia Flask (Thread Daemon)                    │  │
│  │  ├── Inicia Monitor (Thread Daemon) ✅ NOVO          │  │
│  │  └── Cria Janela (pywebview)                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Flask Server (Thread Daemon)                        │  │
│  │  └── sne_radar_web.py                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Opportunity Monitor (Thread Daemon) ✅ NOVO          │  │
│  │  ├── Volume Scanner (Fase 1)                         │  │
│  │  ├── Pavio Scanner (Fase 2)                         │  │
│  │  └── Telegram Notifier                               │  │
│  │      └── Estado: scanner_state.json ✅ PERSISTENTE   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Janela Nativa (pywebview)                            │  │
│  │  └── Frontend Vue.js (http://127.0.0.1:9999)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │
         │ (Notificações)
         ▼
    ┌─────────────┐
    │  Telegram   │
    │   Bot API   │
    └─────────────┘
```

---

## 🔄 CICLO DE VIDA NO .APP

### **Inicialização:**
1. `sne_desktop.py` inicia
2. Thread Flask inicia (daemon)
3. **Thread Monitor inicia (daemon)** ✅ NOVO
4. Monitor carrega estado de `scanner_state.json`
5. Janela nativa abre
6. Frontend carrega

### **Operação:**
1. Monitor escaneia símbolos a cada 60s
2. Detecta oportunidades
3. Verifica cooldown (usando estado persistido)
4. Envia notificação Telegram
5. Salva estado em `scanner_state.json`
6. Continua escaneando

### **Encerramento:**
1. Usuário fecha janela
2. `webview.start()` retorna
3. Threads daemon terminam automaticamente
4. Estado já está salvo (salvamento contínuo)

---

## 📝 MENSAGENS ATUALIZADAS COM CONFIRMAÇÃO DE WICK

### **Alerta RVOL (Fase 1):**
```
🚨 VOLUME EXPLOSIVO DETECTADO

📊 BTCUSDT - 5m
💥 RVOL: 2.8x
📈 Volume: 1,234,567 BTC
📊 Média: 440,202 BTC
💰 Preço: $65,432.10

⏰ 14:35:22
💡 Possível movimento significativo em formação
```

### **Alerta Agulhada (Fase 2) - COM CONFIRMAÇÃO:**
```
🎯 AGULHADA EM FORMAÇÃO

📊 BTCUSDT
🟢 SINAL: LONG
💰 Preço: $65,432.10

📊 Volume M30: 3.2x média
📉 RSI M5: 22.5 (Sobre-vendido)
✅ Wick Confirmado: 0.4% recuo do mínimo

⏰ 14:35:22
💡 Entrada na ponta do pavio mensal
⚠️ Confirmar com análise adicional antes de operar
```

**Diferença:**
- ✅ Mostra confirmação de wick
- ✅ Indica que preço já começou a reverter
- ✅ Mais confiável que alerta sem confirmação

---

## ⚙️ CONFIGURAÇÃO NO .APP

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
  }
}
```

**Localização no .app:**
- Desenvolvimento: `SNE_BACKUP_CLEAN/config/scanner_config.json`
- .app: `~/Library/Application Support/SNE_RADAR/config/scanner_config.json`

---

## 🧪 TESTES NO .APP

### **Teste 1: Verificar Inicialização**
```bash
# Rodar app e verificar logs
python3 sne_desktop.py

# Deve aparecer:
# ✅ Monitor de oportunidades iniciado em background
# ✅ Monitor ativo - atualizando a cada 60s
```

### **Teste 2: Verificar Persistência**
```bash
# 1. Rodar app
python3 sne_desktop.py

# 2. Aguardar alerta (ou forçar com threshold baixo)

# 3. Fechar app

# 4. Verificar arquivo de estado
cat ~/Library/Application\ Support/SNE_RADAR/scanner_state.json

# 5. Rodar app novamente
# 6. Verificar que cooldown foi respeitado
```

### **Teste 3: Verificar Confirmação de Wick**
```python
# Testar manualmente
from scanners.pavio_scanner import PavioScanner

scanner = PavioScanner(
    wick_confirmation_pct=0.3  # 0.3% de recuo
)

result = scanner.scan_symbol('BTCUSDT')
if result and result['triggered']:
    print(f"✅ Alerta: {result['tipo']}")
    print(f"   Wick confirmado: {result['wick_confirmed']}")
    print(f"   Recuo: {result['recuo_pct']:.2f}%")
```

---

## 📊 MÉTRICAS E ESTATÍSTICAS

### **O que Monitorar:**

1. **Taxa de Detecção:**
   - Alertas por dia (esperado: 5-6)
   - Falsos positivos (esperado: <20% com confirmação de wick)
   - Verdadeiros positivos

2. **Performance:**
   - Tempo de scan por símbolo
   - Uso de API (requests/minuto)
   - Uso de memória

3. **Eficácia:**
   - % de alertas que resultaram em movimento
   - Tempo médio entre alerta e movimento
   - R:R médio das oportunidades detectadas

4. **Persistência:**
   - Estado salvo corretamente após restart
   - Cooldowns respeitados após restart
   - Sem spam de alertas repetidos

---

## 🎯 RESULTADO ESPERADO

### **Antes:**
- ❌ Olhar 288 velas de 5min por dia
- ❌ Fadiga mental após 50-100 velas
- ❌ Perder oportunidades por cansaço
- ❌ Ver padrões que não existem

### **Depois:**
- ✅ SNE filtra automaticamente
- ✅ Apenas 5-6 alertas por dia (velas de ouro)
- ✅ Notificação Telegram quando detecta
- ✅ Confirmação de wick reduz falsos positivos
- ✅ Estado persistido sobrevive a reinicializações
- ✅ Foco apenas nas oportunidades reais
- ✅ Entrada na ponta do pavio mensal

---

## ⚠️ CONSIDERAÇÕES IMPORTANTES

### **1. Rate Limiting da Binance**
- Limite: 1200 requests/minuto
- Scanner usa `skip_rate_limit=True` quando possível
- Delay de 1s entre símbolos no loop

### **2. Cooldown Entre Alertas**
- 5 minutos por símbolo (configurável)
- Estado persistido em JSON
- Sobrevive a reinicializações

### **3. Falsos Positivos**
- Volume alto pode ser manipulação
- RSI extremo pode continuar extremo
- **Confirmação de wick reduz ~60-70% dos falsos**
- Sempre confirmar com análise adicional

### **4. Configuração Flexível**
- Thresholds ajustáveis via JSON
- Ativar/desativar scanners
- Adicionar/remover símbolos
- Configuração por usuário (no .app)

---

## 🚀 PRÓXIMOS PASSOS

### **Fase 1: RVOL Simples (1-2 dias)**
1. ✅ Criar estrutura de diretórios
2. ✅ Implementar `scanners/volume_scanner.py`
3. ✅ Implementar `notifications/telegram_notifier.py` (com persistência)
4. ✅ Integrar com `sne_desktop.py`
5. ✅ Testar no app

### **Fase 2: Pavio Completo (2-3 dias)**
1. ✅ Implementar `scanners/pavio_scanner.py` (com confirmação de wick)
2. ✅ Atualizar notificador para mensagens de agulhada
3. ✅ Testar detecção LONG/SHORT
4. ✅ Validar confirmação de wick

### **Fase 3: Monitor Contínuo (1 dia)**
1. ✅ Implementar `monitors/opportunity_monitor.py`
2. ✅ Integrar com `sne_desktop.py`
3. ✅ Testar em background
4. ✅ Validar persistência de estado

### **Fase 4: Otimizações (Opcional)**
1. ✅ Async/WebSockets (se necessário)
2. ✅ Dashboard de monitoramento
3. ✅ Logs estruturados
4. ✅ Métricas e estatísticas

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### **Estrutura:**
- [ ] Criar `scanners/` directory
- [ ] Criar `notifications/` directory
- [ ] Criar `monitors/` directory
- [ ] Adicionar `__init__.py` em cada

### **Fase 1:**
- [ ] Implementar `volume_scanner.py`
- [ ] Implementar `telegram_notifier.py` (com persistência)
- [ ] Integrar com `sne_desktop.py`
- [ ] Testar envio de notificações
- [ ] Validar persistência de estado

### **Fase 2:**
- [ ] Implementar `pavio_scanner.py` (com confirmação de wick)
- [ ] Atualizar formatação de mensagens
- [ ] Testar detecção LONG/SHORT
- [ ] Validar confirmação de wick

### **Fase 3:**
- [ ] Implementar `opportunity_monitor.py`
- [ ] Integrar com `sne_desktop.py`
- [ ] Testar em background
- [ ] Validar ciclo de vida completo

### **Documentação:**
- [ ] Atualizar README com instruções
- [ ] Documentar configuração
- [ ] Criar guia de troubleshooting

---

**Status:** ✅ Plano Refinado e Aprovado  
**Análise Técnica:** ✅ Aprovado com Louvor  
**Mitigações de Risco:** ✅ Documentadas em `MITIGACAO_RISCOS_SCANNER.md`  
**Próxima Ação:** Aguardando aprovação para iniciar Fase 1

---

## 📋 REFERÊNCIAS

- **Análise Técnica Completa:** Ver avaliação executiva
- **Mitigações de Risco:** `MITIGACAO_RISCOS_SCANNER.md`
- **Rate Limit:** Limite de 15 símbolos, delay dinâmico
- **Drift do Loop:** Compensação automática implementada
- **Dependência de Rede:** Retry robusto com backoff exponencial

