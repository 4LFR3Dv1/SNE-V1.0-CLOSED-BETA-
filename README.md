# SNE RADAR - BACKUP LIMPO

## 📋 Descrição
Backup limpo do Sistema Neural Estratégico (SNE Radar) contendo apenas os arquivos essenciais para funcionamento.

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Telegram (Opcional)
Editar `xenos_bot.py` e configurar:
- `TELEGRAM_TOKEN`: Seu token do bot
- `CHAT_ID`: Seu ID do chat

### 3. Executar o Sistema
```bash
python3 main.py
```

## 📁 Arquivos Incluídos

### Core System
- `main.py` - Sistema principal com interface gráfica
- `backtest.py` - Sistema de backtest e análise
- `xenos_bot.py` - Integração com Telegram

### Módulos Estratégicos
- `mente_fluida.py` - Sistema de ressonância neural
- `mente_fluida_ciclica.py` - Detecção de ciclos
- `catalogo_magnetico.py` - Mapeamento de zonas
- `fluxo_mental.py` - Análise de fluxo de mercado
- `mapeamento_gravitacional.py` - Detecção de zonas críticas
- `previsao_magnetica.py` - Previsões de movimento
- `pulso_magnetico.py` - Detecção de pulsos de massa
- `memoria_neural.py` - Sistema de memória neural

### Configuração
- `requirements.txt` - Dependências Python
- `setup.sh` - Script de instalação

## 🔧 Funcionalidades

### Sistema Principal (main.py)
- Gráficos de candlestick em tempo real
- Médias móveis (EMA8, EMA21, SMA200)
- Detecção de rupturas gravitacionais
- Book de ordens (DOM)
- HUDs informativos
- Integração com Telegram

### Análise Estratégica
- Detecção de padrões históricos
- Mapeamento de zonas de suporte/resistência
- Sistema de alertas automáticos
- Backtest de estratégias
- Gestão de risco

### Indicadores Técnicos
- Densidade gravitacional (customizado)
- RSI
- Volume analysis
- Momentum indicators

## 📊 Parâmetros de Configuração

### Trading
- Take Profit: 2%
- Stop Loss: 1%
- Cooldown: 15 minutos
- Position Size: Máximo 2% por trade

### Detecção
- Sensibilidade Gravitacional: 0.95
- Sensibilidade Magnética: 0.98
- Intervalo de Atualização: 60 segundos

## 🎯 Como Usar

1. **Iniciar Sistema**: Execute `python3 main.py`
2. **Terminal Interativo**: Use comandos 1-4 no terminal
3. **Modo Silêncio**: Alternar alertas sonoros
4. **Encerrar**: Comando 3 para finalizar

## ⚠️ Observações

- Sistema funciona com dados da Binance
- Requer conexão com internet
- Telegram opcional para alertas
- Logs são salvos automaticamente

## 🔄 Atualizações

Para atualizar o sistema:
1. Substitua os arquivos .py pelos novos
2. Mantenha configurações personalizadas
3. Reinicie o sistema

---
**SNE Radar v1.0** - Sistema Neural Estratégico de Análise de Mercado
