#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FORMATAÇÃO MELHORADA PARA TELEGRAM
Sistema de formatação otimizado para mensagens do Telegram
"""

class FormatadorTelegram:
    """Classe para formatar mensagens do Telegram de forma mais legível"""
    
    def __init__(self):
        """Inicializa o formatador"""
        self.max_chars_per_block = 1000  # Limite do Telegram
        self.max_lines_per_block = 15    # Linhas por bloco
    
    def formatar_mensagem_completa(self, resultado):
        """Formata mensagem completa em blocos organizados"""
        try:
            # Extrair dados do resultado
            symbol = resultado.get('symbol', 'UNKNOWN')
            timeframe = resultado.get('timeframe', '1h')
            contexto = resultado.get('contexto', {})
            estrutura = resultado.get('estrutura', {})
            mtf = resultado.get('mtf', {})
            fluxo = resultado.get('fluxo', {})
            sintese = resultado.get('sintese', {})
            candles_detalhados = resultado.get('candles_detalhados', {})
            niveis_operacionais = resultado.get('niveis_operacionais', {})
            gestao_risco = resultado.get('gestao_risco', {})
            
            preco_atual = resultado.get('indicadores', {}).get('preco', 0)
            
            # Dividir em blocos
            blocos = []
            
            # BLOCO 1: CABEÇALHO E RESUMO EXECUTIVO
            blocos.append(self._gerar_bloco_cabecalho(symbol, timeframe, preco_atual, contexto, estrutura))
            
            # BLOCO 2: ANÁLISE TÉCNICA
            blocos.append(self._gerar_bloco_analise_tecnica(contexto, estrutura, mtf, fluxo))
            
            # BLOCO 3: CANDLE ATUAL
            blocos.append(self._gerar_bloco_candle_atual(candles_detalhados))
            
            # BLOCO 4: SETUP OPERACIONAL
            blocos.append(self._gerar_bloco_setup_operacional(sintese, niveis_operacionais, gestao_risco))
            
            # BLOCO 5: CENÁRIOS E CONDIÇÕES
            blocos.append(self._gerar_bloco_cenarios_condicoes(sintese, contexto, fluxo, timeframe))
            
            # BLOCO 6: RECOMENDAÇÃO FINAL
            blocos.append(self._gerar_bloco_recomendacao_final(sintese, gestao_risco))
            
            return blocos
            
        except Exception as e:
            return [f"❌ Erro ao formatar mensagem: {str(e)}"]
    
    def _gerar_bloco_cabecalho(self, symbol, timeframe, preco_atual, contexto, estrutura):
        """Gera bloco do cabeçalho e resumo executivo"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        regime = contexto.get('regime', 'UNKNOWN')
        forca_regime = contexto.get('forca_regime', 0)
        tendencia = estrutura.get('tendencia', 'UNKNOWN')
        
        # Emojis para regime
        emoji_regime = {
            'CONSOLIDATION': '📊',
            'BULL_TREND': '🐂',
            'BEAR_TREND': '🐻',
            'VOLATILE': '⚡'
        }.get(regime, '📈')
        
        # Emojis para tendência
        emoji_tendencia = {
            'ALTA': '📈',
            'BAIXA': '📉',
            'LATERAL': '➡️'
        }.get(tendencia, '📊')
        
        return f"""🎯 **SNE RADAR | {symbol} ({timeframe})**
📅 {timestamp} | 💰 **${preco_atual:,.2f}**

📊 **RESUMO EXECUTIVO:**
{emoji_regime} **Regime:** {regime} ({forca_regime}/10)
{emoji_tendencia} **Tendência:** {tendencia}
📊 **Confluência:** {contexto.get('confluencia_score', 0):.1f}/10

---
"""
    
    def _gerar_bloco_analise_tecnica(self, contexto, estrutura, mtf, fluxo):
        """Gera bloco da análise técnica"""
        volatilidade = contexto.get('volatilidade', 0)
        liquidez = contexto.get('liquidez', 0)
        rsi = contexto.get('rsi', 50)
        
        # Análise multi-timeframe
        mtf_alta = mtf.get('alta', 0)
        mtf_baixa = mtf.get('baixa', 0)
        mtf_lateral = mtf.get('lateral', 0)
        
        # Fluxo DOM
        ratio_dom = fluxo.get('ratio', 1.0)
        pressao_dom = fluxo.get('pressao', 'NEUTRO')
        
        return f"""🔍 **ANÁLISE TÉCNICA:**

📊 **Indicadores:**
• Volatilidade: {volatilidade:.2f}% ({'Alta' if volatilidade > 2 else 'Moderada' if volatilidade > 1 else 'Baixa'})
• Liquidez: {liquidez}/10
• RSI: {rsi:.0f} ({'Sobrecompra' if rsi > 70 else 'Sobrevenda' if rsi < 30 else 'Neutro'})

⏰ **Multi-Timeframe:**
• Alta: {mtf_alta} TFs
• Baixa: {mtf_baixa} TFs  
• Lateral: {mtf_lateral} TFs

🌊 **Fluxo DOM:**
• Pressão: {pressao_dom}
• Ratio: {ratio_dom:.3f}

---
"""
    
    def _gerar_bloco_candle_atual(self, candles_detalhados):
        """Gera bloco da análise da candle atual"""
        if not candles_detalhados:
            return "🕯️ **CANDLE ATUAL:**\nDados não disponíveis\n\n---\n"
        
        candle_info = candles_detalhados.get('candle_atual', {})
        precos = candles_detalhados.get('precos', {})
        classificacao = candles_detalhados.get('classificacao', {})
        
        tipo_candle = classificacao.get('tipo', 'N/A')
        significado = classificacao.get('significado', 'N/A')
        tempo_restante = candle_info.get('tempo_restante', 'N/A')
        
        return f"""🕯️ **CANDLE ATUAL:**

📊 **Tipo:** {tipo_candle} - {significado}
⏱️ **Restante:** {tempo_restante}

💰 **OHLC:**
• Open: ${precos.get('open', 0):,.2f}
• High: ${precos.get('high', 0):,.2f}
• Low: ${precos.get('low', 0):,.2f}
• Close: ${precos.get('close', 0):,.2f}

📏 **Range:** ${precos.get('range', 0):,.2f} ({precos.get('range_percentual', 0):.2f}%)

---
"""
    
    def _gerar_bloco_setup_operacional(self, sintese, niveis_operacionais, gestao_risco):
        """Gera bloco do setup operacional"""
        acao = sintese.get('acao', 'N/A')
        vies = sintese.get('vies', 'N/A')
        score = sintese.get('score_confianca', 0)
        
        # Níveis operacionais
        entry = niveis_operacionais.get('entry_price', 0)
        stop = niveis_operacionais.get('stop_loss', 0)
        tp1 = niveis_operacionais.get('tp1', 0)
        tp2 = niveis_operacionais.get('tp2', 0)
        rr_ratio = niveis_operacionais.get('rr_ratio', 'N/A')
        
        # Gestão de risco
        status_risco = gestao_risco.get('status', 'N/A')
        risco_percentual = gestao_risco.get('risco_percentual', 0)
        
        return f"""🎯 **SETUP OPERACIONAL:**

📊 **Ação:** {acao}
🎯 **Viés:** {vies}
⭐ **Score:** {score}/10

📍 **NÍVEIS:**
• Entry: ${entry:,.2f}
• Stop: ${stop:,.2f}
• TP1: ${tp1:,.2f}
• TP2: ${tp2:,.2f}
• R:R: {rr_ratio}

🛡️ **GESTÃO DE RISCO:**
• Status: {status_risco}
• Risco: {risco_percentual:.1f}% do capital

---
"""
    
    def _gerar_bloco_cenarios_condicoes(self, sintese, contexto, fluxo, timeframe):
        """Gera bloco dos cenários e condições"""
        regime = contexto.get('regime', 'UNKNOWN')
        preco_atual = contexto.get('preco_atual', 0)
        volatilidade = contexto.get('volatilidade', 0)
        ratio_dom = fluxo.get('ratio', 1.0)
        
        # Calcular níveis baseados no regime
        if regime == 'CONSOLIDATION':
            resistencia = preco_atual * 1.001
            suporte = preco_atual * 0.999
            
            return f"""🎯 **CENÁRIO CONSOLIDAÇÃO - {timeframe.upper()}:**

🟢 **LONG (Quebra de Consolidação):**
• Entry: ${resistencia:,.0f} (Quebra de resistência)
• Stop: ${preco_atual * 0.998:,.0f} (Retorno à consolidação)
• TP1: ${preco_atual * 1.005:,.0f} (R:R 1:1.6)
• TP2: ${preco_atual * 1.010:,.0f} (Extensão 1.5 ATR)

🔴 **SHORT (Quebra de Consolidação):**
• Entry: ${suporte:,.0f} (Quebra de suporte)
• Stop: ${preco_atual * 1.002:,.0f} (Retorno à consolidação)
• TP1: ${preco_atual * 0.995:,.0f} (R:R 1:1.6)
• TP2: ${preco_atual * 0.990:,.0f} (Extensão 1.5 ATR)

⚠️ **CONDIÇÕES ESPECÍFICAS:**
☐ Volume > 1.5x média (confirmação de quebra)
☐ RSI > 60 (LONG) ou < 40 (SHORT)
☐ DOM: Ratio > 1.1 (LONG) ou < 0.9 (SHORT)
☐ Confirmação em timeframe superior

---
"""
        else:
            return f"""🎯 **CENÁRIO {regime} - {timeframe.upper()}:**

📊 **Regime:** {regime} | ATR: ${volatilidade * preco_atual / 100:,.0f} | DOM Ratio: {ratio_dom:.3f}

⚠️ **CONDIÇÕES ESPECÍFICAS:**
☐ Volume > 1.5x média
☐ Confirmação de direção clara
☐ RSI em zona adequada
☐ DOM Ratio favorável

---
"""
    
    def _gerar_bloco_recomendacao_final(self, sintese, gestao_risco):
        """Gera bloco da recomendação final"""
        score = sintese.get('score_confianca', 0)
        recomendacao = sintese.get('recomendacao', 'N/A')
        
        # Determinar status da recomendação
        if score >= 8:
            status = "✅ **APROVADO**"
            cor = "🟢"
        elif score >= 6:
            status = "⚠️ **CUIDADO**"
            cor = "🟡"
        else:
            status = "❌ **REJEITADO**"
            cor = "🔴"
        
        return f"""💡 **RECOMENDAÇÃO FINAL:**

{cor} **Status:** {status}
⭐ **Score:** {score}/10
📊 **Recomendação:** {recomendacao}

🎯 **CONCLUSÃO:**
{'✅ Execute com confiança' if score >= 8 else '⚠️ Execute com cautela' if score >= 6 else '❌ Aguardar melhor oportunidade'}

---
📈 **Gráfico técnico anexado acima**
⏰ **Próxima atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""


def formatar_mensagem_telegram_melhorada(resultado):
    """Função principal para formatar mensagem do Telegram em blocos"""
    try:
        formatador = FormatadorTelegram()
        return formatador.formatar_mensagem_completa(resultado)
    except Exception as e:
        return [f"❌ Erro ao formatar mensagem: {str(e)}"]


if __name__ == "__main__":
    # Teste do formatador
    print("🚀 Formatador de Telegram criado!")
    print("📱 Mensagens serão divididas em blocos organizados")
    print("✅ Formatação otimizada para legibilidade")









