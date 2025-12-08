# 🚀 SISTEMA SNE RADAR - COMPLETO

## 📋 Visão Geral

Sistema Neural Estratégico completo com **3 novos módulos avançados** para day-trading profissional:

1. **Multi-Pair Radar Interface** - Interface visual para múltiplos pares
2. **Sistema de Priorização Automática** - Seleção inteligente de pares
3. **Sistema de Alertas Inteligentes** - Alertas contextuais com recomendações

## 🎯 Novos Módulos Implementados

### 1. Multi-Pair Radar Interface (`multi_pair_radar_interface.py`)

Interface visual completa para monitoramento simultâneo de múltiplos pares.

**Funcionalidades:**
- 📊 Layout em grid com par principal + 4 secundários
- 🎨 Cores dinâmicas baseadas em score e regime
- 🏆 Ranking de oportunidades em tempo real
- 🚨 Painel de alertas importantes
- 📈 Estatísticas do mercado
- 💡 Recomendações de trading

**Como Usar:**
```python
from multi_pair_radar_interface import iniciar_multi_pair_radar

# Iniciar interface (atualização a cada 30 segundos)
iniciar_multi_pair_radar(intervalo=30)
```

**Layout da Interface:**
```
┌─────────────────────┬──────────┬──────────┐
│                     │  Sec 1   │  Sec 2   │
│   Par Principal     ├──────────┼──────────┤
│     (Grande)        │  Sec 3   │  Sec 4   │
├─────────────────────┴──────────┴──────────┤
│  Ranking de Oportunidades  │  Alertas    │
├────────────────────────────┼─────────────┤
│  Estatísticas              │ Recomendações│
└────────────────────────────┴─────────────┘
```

### 2. Sistema de Priorização Automática (`priorizacao_automatica.py`)

Sistema inteligente que prioriza pares baseado em múltiplos critérios.

**Critérios de Priorização:**
- 🎯 Opportunity Score (30%)
- 📊 Volatilidade (20%)
- 📈 Volume (15%)
- 💪 Força da Tendência (15%)
- ⚖️ Relação Risco/Retorno (10%)
- 🚀 Momentum (10%)

**Funcionalidades:**
- Cálculo de score de priorização (0-100)
- Identificação de pontos de entrada/saída
- Histórico de performance por par
- Blacklist temporária para pares problemáticos
- Ajuste automático baseado em resultados

**Como Usar:**
```python
from priorizacao_automatica import priorizar_pares_automaticamente

# Priorizar pares
pares_priorizados, relatorio = priorizar_pares_automaticamente(resultados)

# Top 5 prioridades
for par in pares_priorizados[:5]:
    print(f"{par['symbol']}: Prioridade {par['priority_score']:.0f}")
```

**Exemplo de Saída:**
```
🏆 TOP 5 PRIORIDADES:
1. BTCUSDT - Prioridade: 85.2/100
   Score de Oportunidade: 78.5
   Regime: bull_trend | Risco: BAIXO
   Recomendação: 🔥 PRIORIDADE MÁXIMA

2. ETHUSDT - Prioridade: 78.3/100
   Score de Oportunidade: 72.1
   Regime: bull_trend | Risco: MÉDIO
   Recomendação: ⭐ ALTA PRIORIDADE
```

### 3. Sistema de Alertas Inteligentes (`alertas_inteligentes.py`)

Sistema avançado de alertas contextuais com análise e recomendações.

**Tipos de Alertas:**
- 🔥 Oportunidade Alta (Score ≥ 80)
- ⭐ Oportunidade Média (Score ≥ 70)
- ⚠️ Risco Alto
- 💥 Ruptura
- 🔄 Reversão
- 🚀 Breakout
- 📊 Volume Anômalo
- 🌪️ Volatilidade Extrema
- 🎯 Zona Crítica
- 📉 Divergência

**Prioridades:**
- 🔴 CRÍTICA
- 🟠 ALTA
- 🟡 MÉDIA
- 🟢 BAIXA
- ⚪ INFO

**Funcionalidades:**
- Análise contextual automática
- Recomendações específicas por alerta
- Cooldown para evitar spam
- Histórico de alertas
- Marcação de lidos/acionados

**Como Usar:**
```python
from alertas_inteligentes import sistema_alertas_global

# Gerar alertas para um par
alertas = sistema_alertas_global.analisar_e_gerar_alertas(dados_par)

# Exibir alertas
for alerta in alertas:
    print(alerta)
    for rec in alerta.recomendacoes:
        print(f"  • {rec}")
```

**Exemplo de Alerta:**
```
🔥 [CRITICA] BTCUSDT: Oportunidade excepcional detectada! Score 85/100

Contexto:
  • Score: 85.2
  • Regime: bull_trend
  • Preço: $67,450.00
  • Risco: BAIXO

Recomendações:
  • Considerar entrada em BTCUSDT com stop loss rigoroso
  • Preço atual: $67,450.00
  • Regime: bull_trend - Tendência: FORTE ALTA
  • Monitorar volume e volatilidade antes da entrada
  • Definir take profit em níveis de resistência
```

## 🔧 Sistema Integrado

### Arquivo Principal: `sistema_integrado.py`

Integra todos os módulos em um sistema coeso.

**Fases de Execução:**
1. 📊 Análise Multi-Pair (12 pares)
2. 🎯 Priorização Automática
3. 🚨 Geração de Alertas Inteligentes
4. 🖥️ Atualização Interface Visual
5. 📱 Envio Telegram

**Como Usar:**
```python
from sistema_integrado import iniciar_sistema_integrado

# Iniciar sistema completo
iniciar_sistema_integrado(
    intervalo=30,    # Atualização a cada 30s
    telegram=True,   # Enviar alertas para Telegram
    visual=True      # Ativar interface visual
)
```

## 🚀 Início Rápido

### Opção 1: Script Interativo (Recomendado)

```bash
python3 iniciar_sistema_completo.py
```

Menu interativo com 6 opções:
1. Sistema Completo (Visual + Alertas + Telegram)
2. Apenas Análise Multi-Pair
3. Alertas + Telegram
4. Análise Única
5. Configuração Personalizada
6. Sair

### Opção 2: Linha de Comando

```bash
# Sistema completo
python3 iniciar_sistema_completo.py

# Sem interface visual
python3 iniciar_sistema_completo.py --no-visual

# Sem Telegram
python3 iniciar_sistema_completo.py --no-telegram

# Intervalo personalizado (60 segundos)
python3 iniciar_sistema_completo.py --intervalo 60

# Análise única e sair
python3 iniciar_sistema_completo.py --unico
```

### Opção 3: Importar em Código

```python
from sistema_integrado import sistema_integrado

# Executar um ciclo único
resultado = sistema_integrado.executar_ciclo_unico()

# Acessar resultados
print(f"Pares analisados: {len(resultado['resultados'])}")
print(f"Alertas gerados: {len(resultado['alertas'])}")

# Top 3 prioridades
for par in resultado['pares_priorizados'][:3]:
    print(f"{par['symbol']}: {par['priority_score']:.0f}")
```

## 📊 Fluxo de Dados

```
┌─────────────────────────────────────────────────────────┐
│                    BINANCE API                          │
│              (12 pares, dados em tempo real)            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           ANÁLISE DE CONTEXTO DE MERCADO                │
│  • Regime de mercado (5 tipos)                          │
│  • Score de oportunidade (0-100)                        │
│  • Análise de risco, volatilidade, volume              │
│  • Interpretação algorítmica                            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│         SISTEMA DE PRIORIZAÇÃO AUTOMÁTICA               │
│  • Cálculo de prioridade (6 critérios)                 │
│  • Pontos de entrada/saída                             │
│  • Ajuste por performance histórica                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│         SISTEMA DE ALERTAS INTELIGENTES                 │
│  • 10 tipos de alertas                                  │
│  • 5 níveis de prioridade                              │
│  • Recomendações contextuais                            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ├─────────────┬─────────────┐
                       ▼             ▼             ▼
              ┌────────────┐  ┌──────────┐  ┌──────────┐
              │  Interface │  │ Telegram │  │   Logs   │
              │   Visual   │  │  Alerts  │  │  System  │
              └────────────┘  └──────────┘  └──────────┘
```

## 🎯 Casos de Uso

### 1. Day Trader Profissional
```python
# Monitoramento completo com interface visual
iniciar_sistema_integrado(intervalo=15, telegram=True, visual=True)
```

### 2. Swing Trader
```python
# Análise menos frequente, sem interface
iniciar_sistema_integrado(intervalo=300, telegram=True, visual=False)
```

### 3. Análise Pontual
```python
# Executar uma análise e tomar decisão
resultado = sistema_integrado.executar_ciclo_unico()
melhor_par = resultado['pares_priorizados'][0]
print(f"Melhor oportunidade: {melhor_par['symbol']}")
```

### 4. Bot Automatizado
```python
# Integrar com bot de trading
while True:
    resultado = sistema_integrado.executar_ciclo_unico()
    
    # Verificar alertas críticos
    alertas_criticos = [a for a in resultado['alertas'] 
                       if a.prioridade.value == 1]
    
    if alertas_criticos:
        # Executar ação automatizada
        executar_trade(alertas_criticos[0])
    
    time.sleep(30)
```

## 📈 Métricas e Performance

### Pares Analisados
- **Total**: 12 pares principais
- **Frequência**: Configurável (padrão: 30s)
- **Tempo de análise**: ~5-10 segundos por ciclo

### Alertas
- **Tipos**: 10 diferentes
- **Prioridades**: 5 níveis
- **Cooldown**: 15 minutos (configurável)
- **Taxa de acerto**: Baseada em histórico

### Priorização
- **Critérios**: 6 fatores ponderados
- **Ajuste automático**: Baseado em performance
- **Blacklist**: Temporária para pares problemáticos

## 🔧 Configuração Avançada

### Ajustar Pesos de Priorização
```python
from priorizacao_automatica import priorizador_global

priorizador_global.pesos = {
    'opportunity_score': 0.40,  # Aumentar peso do score
    'volatility': 0.20,
    'volume': 0.15,
    'trend_strength': 0.10,
    'risk_reward': 0.10,
    'momentum': 0.05
}
```

### Configurar Alertas
```python
from alertas_inteligentes import sistema_alertas_global

sistema_alertas_global.configuracoes = {
    'min_score_oportunidade': 75,  # Aumentar threshold
    'max_risk_level': 'MÉDIO',     # Mais conservador
    'cooldown_minutos': 30         # Menos alertas
}
```

### Adicionar Pares Personalizados
```python
from multi_pair_context import MultiPairContextAnalyzer

analyzer = MultiPairContextAnalyzer()
analyzer.pairs = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT",
    "BNBUSDT", "XRPUSDT", "DOGEUSDT"  # Adicionar novos
]
```

## 🐛 Troubleshooting

### Interface não abre
```bash
# Verificar matplotlib
pip install matplotlib --upgrade

# Verificar backend
export MPLBACKEND=TkAgg
```

### Telegram não envia
```bash
# Verificar configuração em xenos_bot.py
TELEGRAM_TOKEN = "seu_token_aqui"
CHAT_ID = "seu_chat_id"
```

### Erro de API Binance
```bash
# Verificar conexão
ping api.binance.com

# Verificar rate limit (1200 calls/min)
```

## 📚 Documentação Adicional

- `README.md` - Documentação geral do SNE
- `STATUS_IMPLEMENTACOES.md` - Status de todas as implementações
- `DEPLOYMENT_GUIDE.md` - Guia de deploy
- `ADMIN_USAGE.md` - Uso administrativo

## 🎓 Exemplos Práticos

Ver pasta `examples/` (a ser criada) com:
- `example_basic.py` - Uso básico
- `example_advanced.py` - Uso avançado
- `example_bot.py` - Integração com bot
- `example_custom.py` - Configuração personalizada

## 🤝 Contribuindo

Para contribuir com melhorias:
1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto é proprietário e confidencial.

## 👨‍💻 Autor

Desenvolvido por Renan Melo
- Sistema Neural Estratégico (SNE)
- sne-radar.com

---

**Última atualização**: 13/10/2025
**Versão**: 2.0.0 - Sistema Completo Integrado




