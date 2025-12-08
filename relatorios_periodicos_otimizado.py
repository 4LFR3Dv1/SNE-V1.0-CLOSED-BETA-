#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIOS PERIÓDICOS OTIMIZADOS - Horário, Diário, Semanal
Nova estrutura profissional com cenários hipotéticos
"""

from datetime import datetime
import os


def relatorio_horario(symbol="BTCUSDT"):
    """Relatório técnico horário otimizado - Nova estrutura profissional"""
    print("\n📈 GERANDO RELATÓRIO HORÁRIO - FOCO INTRADAY...")
    
    # Timeframes para scalping e day trade
    timeframes = ['1m', '5m', '15m', '30m', '1h']
    
    # Simular dados para demonstração
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    preco_atual = 106678.74
    
    relatorio_completo = f"""
================================================================================
📊 RELATÓRIO HORÁRIO MULTI-TIMEFRAME - {symbol} (TÉCNICO)
================================================================================
🕐 {timestamp}

---
### 1. CONTEXTO GERAL (1m–1h)
| Timeframe | Regime      | Tendência | Confluência | Recomendação Técnica |
|-----------|-------------|-----------|-------------|---------------------|
| 1m        | Consolidação| Baixa     | 7.0/10      | SHORT (rejeitado: R:R 0.5) |
| 5m        | Consolidação| Baixa     | 7.0/10      | SHORT (rejeitado: R:R 0.5) |
| 15m       | Consolidação| Lateral   | 7.6/10      | LONG (rejeitado: volume baixo) |
| 30m       | Consolidação| Lateral   | 8.1/10      | LONG (rejeitado: RSI neutro) |
| 1h        | Consolidação| Lateral   | 4.0/10      | LONG (rejeitado: confluência baixa) |

---
### 2. NÍVEIS-CHAVE CONSOLIDADOS (15m–1h)
| Tipo       | Preço     | Base Técnica                     |
|-------------|-----------|----------------------------------|
| Resistência | $106,451.78 | R1 + EMA 21 (15m) + Cluster de Volume |
| Suporte    | $106,341.68 | S1 + EMA 8 (15m) + Mínima Recente   |
| Pivot      | $106,401.89 | Ponto central do range (1h)          |

---
### 3. INDICADORES TÉCNICOS CONSOLIDADOS
| Timeframe | EMA 8   | EMA 21  | SMA 50  | SMA 200 | RSI (14) | Volume  | DOM Ratio |
|-----------|---------|---------|---------|---------|----------|---------|-----------|
| 15m       | $106,380| $106,420| $106,350| $106,500| 52       | $110M   | 0.820     |
| 1h        | $106,400| $106,450| $106,500| $106,700| 48       | $220M   | 0.850     |

---
### 4. CENÁRIOS HIPOTÉTICOS (AGUARDAR CONFIRMAÇÃO)
🎯 CENÁRIO LONG:
| Nível | Preço     | Justificativa Técnica          | R:R  |
|-------|-----------|--------------------------------|------|
| Entry | $106,451.78| Quebra de resistência ($106,451.78) | —    |
| Stop  | $106,341.68| Abaixo do suporte ($106,341.68)   | —    |
| TP1   | $106,561.78| R:R 1:2                        | 1:2  |
| TP2   | $106,671.78| Extensão Fibonacci 1.618        | 1:4  |

⚠️ CONDIÇÕES PARA ENTRY (LONG):
☐ Quebra de $106,451.78 com volume > $200M
☐ RSI > 70 (sobrecompra)
☐ DOM: Ratio > 1.2 (pressão de compra)
☐ Confirmação de padrão bullish

---
🎯 CENÁRIO SHORT:
| Nível | Preço     | Justificativa Técnica          | R:R  |
|-------|-----------|--------------------------------|------|
| Entry | $106,341.68| Quebra de suporte ($106,341.68)   | —    |
| Stop  | $106,451.78| Acima da resistência ($106,451.78) | —    |
| TP1   | $106,221.68| R:R 1:2                        | 1:2  |
| TP2   | $106,111.68| Extensão Fibonacci 1.618        | 1:4  |

⚠️ CONDIÇÕES PARA ENTRY (SHORT):
☐ Quebra de $106,341.68 com volume > $200M
☐ RSI < 30 (sobrevenda)
☐ DOM: Ratio < 0.7 (pressão de venda)
☐ Confirmação de padrão bearish

---
### 5. CONFLUÊNCIA CONSOLIDADA
| Fator               | Status          | Peso | Detalhes Técnicos               |
|---------------------|-----------------|------|---------------------------------|
| Volume > $200M      | ❌ $110M        | 3.0/10| Volume abaixo da média          |
| RSI < 30 ou > 70    | ❌ Neutro (52)  | 2.0/10| Sem sobrecompra/sobrevenda     |
| Padrão Gráfico      | ❌ Sem formação  | 2.0/10| Sem wedge/flag/divergência      |
| Alinhamento Multi-TF| ✅ 15m/1h lateral| 1.0/10| Sem tendência clara            |
| Confluência Total   | 4.0/10          | —    | —                               |

---
### 6. GESTÃO DE RISCO (TÉCNICA)
- Risco por operação: 1.0% do capital (padrão técnico)
- Posição: 30% do tamanho padrão (devido à baixa confluência)
- Status: ❌ Rejeitado (confluência < 7/10)
- Critérios para Aprovação:
  - Confluência mínima: 7/10
  - Volume > $200M
  - RSI < 30 ou > 70
  - Padrão gráfico claro (wedge, flag, divergência)

---
### 7. RECOMENDAÇÃO FINAL (TÉCNICA)
❌ Não operar nenhum dos setups atuais.

Motivos Técnicos:
1. Volume insuficiente em todos os timeframes (< $200M)
2. RSI neutro (45–52), sem sobrecompra/sobrevenda
3. Ausência de padrões gráficos (wedge, flag, divergência)
4. Confluência baixa (4.0–7.6/10, mínimo aceitável: 7/10)

Aguardar:
- Quebra confirmada de $106,341.68 (suporte) ou $106,451.78 (resistência) com:
  - Volume > $200M
  - RSI < 30 (sobrevenda) ou > 70 (sobrecompra)
  - Formação de padrão gráfico (ex.: wedge bearish)
- Reavaliar confluência após atendimento das condições acima

🎯 CONCLUSÃO PARA O OPERADOR:
> "Mercado em consolidação lateral com confluência 4.0/10. Não operar no momento.
> 
> CENÁRIOS HIPOTÉTICOS:
> 
> LONG:
> - Quebra de $106,451.78 com volume > $200M e RSI > 70
> - DOM: Ratio > 1.2 (pressão de compra)
> 
> SHORT:
> - Quebra de $106,341.68 com volume > $200M e RSI < 30
> - DOM: Ratio < 0.7 (pressão de venda)
> 
> Risco: 1.0% do capital. Tamanho da posição: 30%."

================================================================================
"""
    
    # Salvar relatório
    os.makedirs('reports/horario', exist_ok=True)
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M")
    arquivo_relatorio = f'reports/horario/{symbol}_{timestamp_file}_intraday.txt'
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio_completo)
    
    print(f"   ✅ Salvo: {arquivo_relatorio}")
    
    # Gerar gráfico
    try:
        from grafico_candlestick import gerar_grafico_candlestick
        grafico_path = gerar_grafico_candlestick(symbol, '15m')
        if grafico_path:
            print(f"✅ Gráfico salvo: {grafico_path}")
    except Exception as e:
        print(f"⚠️ Erro ao gerar gráfico: {e}")
    
    # Enviar para Telegram
    try:
        from telegram_utils import enviar_relatorio_telegram
        enviar_relatorio_telegram(relatorio_completo, "RELATÓRIO HORÁRIO")
        print("✅ Relatório enviado para Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Telegram: {e}")
    
    return relatorio_completo


def relatorio_diario(symbol="BTCUSDT"):
    """Relatório técnico diário otimizado - Nova estrutura profissional"""
    print("\n📈 GERANDO RELATÓRIO DIÁRIO - FOCO SWING TRADE...")
    
    # Timeframes para swing trade
    timeframes = ['4h', '8h', '12h', '1d']
    
    # Simular dados para demonstração
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    preco_atual = 106678.74
    
    relatorio_completo = f"""
================================================================================
📊 RELATÓRIO DIÁRIO MULTI-TIMEFRAME - {symbol} (SWING TRADE)
================================================================================
🕐 {timestamp}

---
### 1. CONTEXTO GERAL (4h–1d)
| Timeframe | Regime      | Tendência | Confluência | Recomendação Técnica |
|-----------|-------------|-----------|-------------|---------------------|
| 4h        | Consolidação| Baixa     | 6.5/10      | SHORT (rejeitado: volume baixo) |
| 8h        | Consolidação| Lateral   | 7.2/10      | LONG (rejeitado: RSI neutro) |
| 12h       | Consolidação| Lateral   | 7.8/10      | LONG (rejeitado: padrão não confirmado) |
| 1d        | Consolidação| Lateral   | 5.5/10      | LONG (rejeitado: confluência baixa) |

---
### 2. NÍVEIS-CHAVE CONSOLIDADOS (4h–1d)
| Tipo       | Preço     | Base Técnica                     |
|-------------|-----------|----------------------------------|
| Resistência | $107,200.00 | R2 + SMA 200 (1d) + Cluster de Volume |
| Suporte    | $106,000.00 | S2 + EMA 21 (4h) + Mínima Recente   |
| Pivot      | $106,600.00 | Ponto central do range (1d)          |

---
### 3. INDICADORES TÉCNICOS CONSOLIDADOS
| Timeframe | EMA 8   | EMA 21  | SMA 50  | SMA 200 | RSI (14) | Volume  | DOM Ratio |
|-----------|---------|---------|---------|---------|----------|---------|-----------|
| 4h        | $106,500| $106,600| $106,700| $107,000| 45       | $450M   | 0.920     |
| 1d        | $106,600| $106,700| $106,800| $107,200| 48       | $1.2B   | 0.850     |

---
### 4. CENÁRIOS HIPOTÉTICOS (AGUARDAR CONFIRMAÇÃO)
🎯 CENÁRIO LONG:
| Nível | Preço     | Justificativa Técnica          | R:R  |
|-------|-----------|--------------------------------|------|
| Entry | $107,200.00| Quebra de resistência ($107,200.00) | —    |
| Stop  | $106,000.00| Abaixo do suporte ($106,000.00)   | —    |
| TP1   | $108,400.00| R:R 1:2                        | 1:2  |
| TP2   | $109,600.00| Extensão Fibonacci 1.618        | 1:4  |

⚠️ CONDIÇÕES PARA ENTRY (LONG):
☐ Quebra de $107,200.00 com volume > $2B
☐ RSI > 70 (sobrecompra)
☐ DOM: Ratio > 1.2 (pressão de compra)
☐ Confirmação de padrão bullish

---
🎯 CENÁRIO SHORT:
| Nível | Preço     | Justificativa Técnica          | R:R  |
|-------|-----------|--------------------------------|------|
| Entry | $106,000.00| Quebra de suporte ($106,000.00)   | —    |
| Stop  | $107,200.00| Acima da resistência ($107,200.00) | —    |
| TP1   | $104,800.00| R:R 1:2                        | 1:2  |
| TP2   | $103,600.00| Extensão Fibonacci 1.618        | 1:4  |

⚠️ CONDIÇÕES PARA ENTRY (SHORT):
☐ Quebra de $106,000.00 com volume > $2B
☐ RSI < 30 (sobrevenda)
☐ DOM: Ratio < 0.7 (pressão de venda)
☐ Confirmação de padrão bearish

---
### 5. CONFLUÊNCIA CONSOLIDADA
| Fator               | Status          | Peso | Detalhes Técnicos               |
|---------------------|-----------------|------|---------------------------------|
| Volume > $2B        | ❌ $1.2B        | 3.0/10| Volume abaixo da média          |
| RSI < 30 ou > 70    | ❌ Neutro (48)  | 2.0/10| Sem sobrecompra/sobrevenda     |
| Padrão Gráfico      | ❌ Sem formação  | 2.0/10| Sem wedge/flag/divergência      |
| Alinhamento Multi-TF| ✅ 4h/1d lateral| 1.5/10| Sem tendência clara            |
| Confluência Total   | 5.5/10          | —    | —                               |

---
### 6. GESTÃO DE RISCO (SWING TRADE)
- Risco por operação: 2.0% do capital (padrão swing)
- Posição: 50% do tamanho padrão (devido à confluência moderada)
- Status: ❌ Rejeitado (confluência < 7/10)
- Critérios para Aprovação:
  - Confluência mínima: 7/10
  - Volume > $2B
  - RSI < 30 ou > 70
  - Padrão gráfico claro (wedge, flag, divergência)

---
### 7. RECOMENDAÇÃO FINAL (SWING TRADE)
❌ Não operar nenhum dos setups atuais.

Motivos Técnicos:
1. Volume insuficiente em todos os timeframes (< $2B)
2. RSI neutro (45–48), sem sobrecompra/sobrevenda
3. Ausência de padrões gráficos (wedge, flag, divergência)
4. Confluência baixa (5.5–7.8/10, mínimo aceitável: 7/10)

Aguardar:
- Quebra confirmada de $106,000.00 (suporte) ou $107,200.00 (resistência) com:
  - Volume > $2B
  - RSI < 30 (sobrevenda) ou > 70 (sobrecompra)
  - Formação de padrão gráfico (ex.: wedge bearish)
- Reavaliar confluência após atendimento das condições acima

🎯 CONCLUSÃO PARA O OPERADOR:
> "Mercado em consolidação lateral com confluência 5.5/10. Não operar no momento.
> 
> CENÁRIOS HIPOTÉTICOS:
> 
> LONG:
> - Quebra de $107,200.00 com volume > $2B e RSI > 70
> - DOM: Ratio > 1.2 (pressão de compra)
> 
> SHORT:
> - Quebra de $106,000.00 com volume > $2B e RSI < 30
> - DOM: Ratio < 0.7 (pressão de venda)
> 
> Risco: 2.0% do capital. Tamanho da posição: 50%."

================================================================================
"""
    
    # Salvar relatório
    os.makedirs('reports/diario', exist_ok=True)
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M")
    arquivo_relatorio = f'reports/diario/{symbol}_{timestamp_file}_swing.txt'
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio_completo)
    
    print(f"   ✅ Salvo: {arquivo_relatorio}")
    
    # Gerar gráfico
    try:
        from grafico_candlestick import gerar_grafico_candlestick
        grafico_path = gerar_grafico_candlestick(symbol, '4h')
        if grafico_path:
            print(f"✅ Gráfico salvo: {grafico_path}")
    except Exception as e:
        print(f"⚠️ Erro ao gerar gráfico: {e}")
    
    # Enviar para Telegram
    try:
        from telegram_utils import enviar_relatorio_telegram
        enviar_relatorio_telegram(relatorio_completo, "RELATÓRIO DIÁRIO")
        print("✅ Relatório enviado para Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Telegram: {e}")
    
    return relatorio_completo


def relatorio_semanal(symbol="BTCUSDT"):
    """Relatório técnico semanal otimizado - Nova estrutura profissional"""
    print("\n📈 GERANDO RELATÓRIO SEMANAL - FOCO POSITION TRADE...")
    
    # Timeframes para position trade
    timeframes = ['1d', '3d', '1w']
    
    # Simular dados para demonstração
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    preco_atual = 106678.74
    
    relatorio_completo = f"""
================================================================================
📊 RELATÓRIO SEMANAL MULTI-TIMEFRAME - {symbol} (POSITION TRADE)
================================================================================
🕐 {timestamp}

---
### 1. CONTEXTO GERAL (1d–1w)
| Timeframe | Regime      | Tendência | Confluência | Recomendação Técnica |
|-----------|-------------|-----------|-------------|---------------------|
| 1d        | Consolidação| Lateral   | 6.8/10      | LONG (rejeitado: volume baixo) |
| 3d        | Consolidação| Lateral   | 7.5/10      | LONG (rejeitado: RSI neutro) |
| 1w        | Consolidação| Lateral   | 6.2/10      | LONG (rejeitado: confluência baixa) |

---
### 2. NÍVEIS-CHAVE CONSOLIDADOS (1d–1w)
| Tipo       | Preço     | Base Técnica                     |
|-------------|-----------|----------------------------------|
| Resistência | $110,000.00 | R3 + SMA 200 (1w) + Cluster de Volume |
| Suporte    | $105,000.00 | S3 + EMA 21 (1d) + Mínima Recente   |
| Pivot      | $107,500.00 | Ponto central do range (1w)          |

---
### 3. INDICADORES TÉCNICOS CONSOLIDADOS
| Timeframe | EMA 8   | EMA 21  | SMA 50  | SMA 200 | RSI (14) | Volume  | DOM Ratio |
|-----------|---------|---------|---------|---------|----------|---------|-----------|
| 1d        | $106,800| $107,000| $107,200| $108,000| 50       | $3.5B   | 0.880     |
| 1w        | $107,000| $107,200| $107,500| $108,500| 52       | $8.2B   | 0.850     |

---
### 4. CENÁRIOS HIPOTÉTICOS (AGUARDAR CONFIRMAÇÃO)
🎯 CENÁRIO LONG:
| Nível | Preço     | Justificativa Técnica          | R:R  |
|-------|-----------|--------------------------------|------|
| Entry | $110,000.00| Quebra de resistência ($110,000.00) | —    |
| Stop  | $105,000.00| Abaixo do suporte ($105,000.00)   | —    |
| TP1   | $115,000.00| R:R 1:2                        | 1:2  |
| TP2   | $120,000.00| Extensão Fibonacci 1.618        | 1:4  |

⚠️ CONDIÇÕES PARA ENTRY (LONG):
☐ Quebra de $110,000.00 com volume > $10B
☐ RSI > 70 (sobrecompra)
☐ DOM: Ratio > 1.2 (pressão de compra)
☐ Confirmação de padrão bullish

---
🎯 CENÁRIO SHORT:
| Nível | Preço     | Justificativa Técnica          | R:R  |
|-------|-----------|--------------------------------|------|
| Entry | $105,000.00| Quebra de suporte ($105,000.00)   | —    |
| Stop  | $110,000.00| Acima da resistência ($110,000.00) | —    |
| TP1   | $100,000.00| R:R 1:2                        | 1:2  |
| TP2   | $95,000.00 | Extensão Fibonacci 1.618        | 1:4  |

⚠️ CONDIÇÕES PARA ENTRY (SHORT):
☐ Quebra de $105,000.00 com volume > $10B
☐ RSI < 30 (sobrevenda)
☐ DOM: Ratio < 0.7 (pressão de venda)
☐ Confirmação de padrão bearish

---
### 5. CONFLUÊNCIA CONSOLIDADA
| Fator               | Status          | Peso | Detalhes Técnicos               |
|---------------------|-----------------|------|---------------------------------|
| Volume > $10B       | ❌ $8.2B        | 3.0/10| Volume abaixo da média          |
| RSI < 30 ou > 70    | ❌ Neutro (52)  | 2.0/10| Sem sobrecompra/sobrevenda     |
| Padrão Gráfico      | ❌ Sem formação  | 2.0/10| Sem wedge/flag/divergência      |
| Alinhamento Multi-TF| ✅ 1d/1w lateral| 1.2/10| Sem tendência clara            |
| Confluência Total   | 6.2/10          | —    | —                               |

---
### 6. GESTÃO DE RISCO (POSITION TRADE)
- Risco por operação: 3.0% do capital (padrão position)
- Posição: 70% do tamanho padrão (devido à confluência moderada)
- Status: ❌ Rejeitado (confluência < 7/10)
- Critérios para Aprovação:
  - Confluência mínima: 7/10
  - Volume > $10B
  - RSI < 30 ou > 70
  - Padrão gráfico claro (wedge, flag, divergência)

---
### 7. RECOMENDAÇÃO FINAL (POSITION TRADE)
❌ Não operar nenhum dos setups atuais.

Motivos Técnicos:
1. Volume insuficiente em todos os timeframes (< $10B)
2. RSI neutro (50–52), sem sobrecompra/sobrevenda
3. Ausência de padrões gráficos (wedge, flag, divergência)
4. Confluência baixa (6.2–7.5/10, mínimo aceitável: 7/10)

Aguardar:
- Quebra confirmada de $105,000.00 (suporte) ou $110,000.00 (resistência) com:
  - Volume > $10B
  - RSI < 30 (sobrevenda) ou > 70 (sobrecompra)
  - Formação de padrão gráfico (ex.: wedge bearish)
- Reavaliar confluência após atendimento das condições acima

🎯 CONCLUSÃO PARA O OPERADOR:
> "Mercado em consolidação lateral com confluência 6.2/10. Não operar no momento.
> 
> CENÁRIOS HIPOTÉTICOS:
> 
> LONG:
> - Quebra de $110,000.00 com volume > $10B e RSI > 70
> - DOM: Ratio > 1.2 (pressão de compra)
> 
> SHORT:
> - Quebra de $105,000.00 com volume > $10B e RSI < 30
> - DOM: Ratio < 0.7 (pressão de venda)
> 
> Risco: 3.0% do capital. Tamanho da posição: 70%."

================================================================================
"""
    
    # Salvar relatório
    os.makedirs('reports/semanal', exist_ok=True)
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M")
    arquivo_relatorio = f'reports/semanal/{symbol}_{timestamp_file}_position.txt'
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio_completo)
    
    print(f"   ✅ Salvo: {arquivo_relatorio}")
    
    # Gerar gráfico
    try:
        from grafico_candlestick import gerar_grafico_candlestick
        grafico_path = gerar_grafico_candlestick(symbol, '1d')
        if grafico_path:
            print(f"✅ Gráfico salvo: {grafico_path}")
    except Exception as e:
        print(f"⚠️ Erro ao gerar gráfico: {e}")
    
    # Enviar para Telegram
    try:
        from telegram_utils import enviar_relatorio_telegram
        enviar_relatorio_telegram(relatorio_completo, "RELATÓRIO SEMANAL")
        print("✅ Relatório enviado para Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Telegram: {e}")
    
    return relatorio_completo


if __name__ == "__main__":
    # Teste dos relatórios
    print("🧪 TESTANDO RELATÓRIOS PERIÓDICOS OTIMIZADOS")
    print("=" * 60)
    
    # Teste relatório horário
    print("\n1. RELATÓRIO HORÁRIO:")
    relatorio_horario()
    
    # Teste relatório diário
    print("\n2. RELATÓRIO DIÁRIO:")
    relatorio_diario()
    
    # Teste relatório semanal
    print("\n3. RELATÓRIO SEMANAL:")
    relatorio_semanal()
    
    print("\n✅ TODOS OS RELATÓRIOS OTIMIZADOS COM SUCESSO!")
