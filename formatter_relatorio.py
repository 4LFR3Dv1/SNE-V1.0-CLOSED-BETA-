#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FORMATTER DE RELATÓRIO
Formata relatório técnico em texto profissional
"""

from datetime import datetime


def montar_relatorio(symbol, contexto, estrutura, mtf, indicadores, zonas, fluxo, padroes, wedges, sentiment, cenarios, confluencia, candles_detalhados=None, gestao_risco=None):
    """Monta relatório final formatado"""
    
    timestamp = datetime.now().strftime("%d de %B, %Y às %H:%M:%S UTC")
    report_id = datetime.now().strftime("SNE-%Y%m%d-%H%M")
    
    relatorio = f"""
============================================================
📊 ANÁLISE TÉCNICA COMPLETA - {symbol}
============================================================
🕐 {timestamp}

📈 CONTEXTO MACRO:
   Regime:          {contexto['regime']} (Força {contexto['forca_regime']}/10)
   Volatilidade:    {contexto['volatilidade']}% ({contexto['volatilidade_status']})
   Volume 24h:      ${contexto['volume_24h']/1e9:.1f}B ({contexto['volume_status']})
   Sessão:          {contexto['sessao']} ({contexto['participacao_sessao']})
   Horário Ideal:   {'✅ SIM' if contexto['horario_ideal'] else '❌ NÃO'}
   Liquidez Score:  {contexto['liquidez_score']}/10

📊 ESTRUTURA DE MERCADO:
   Tendência:       {estrutura['tendencia']}
   Tipo:            {estrutura['tipo_estrutura']}
   
   🔴 RESISTÊNCIAS:
{formatar_niveis(estrutura['resistencias'], 'resistencia')}
   
   🟢 SUPORTES:
{formatar_niveis(estrutura['suportes'], 'suporte')}

🔍 ANÁLISE MULTI-TIMEFRAME:
{formatar_mtf(mtf)}

📊 INDICADORES TÉCNICOS:
   EMA8:     ${indicadores.get('ema8', 0):,.2f}
   EMA21:    ${indicadores.get('ema21', 0):,.2f}
   RSI:      {indicadores.get('rsi', 0):.1f}
   
🧲 ZONAS MAGNÉTICAS:
{formatar_zonas(zonas)}

🌊 FLUXO DE LIQUIDEZ (DOM):
{formatar_fluxo(fluxo)}

📉 PADRÕES TÉCNICOS:
{formatar_padroes(padroes)}

🔺 ANÁLISE DE WEDGES:
{formatar_wedges(wedges)}

🕐 ANÁLISE DETALHADA DO CANDLE ATUAL:
{formatar_candles_detalhados(candles_detalhados) if candles_detalhados else "   Análise de candles não disponível"}

🛡️ GESTÃO DE RISCO PROFISSIONAL:
{formatar_gestao_risco(gestao_risco) if gestao_risco else "   Gestão de risco não disponível"}

😨 SENTIMENT:
   Fear & Greed:  {sentiment['fear_greed']['valor']}/100 ({sentiment['fear_greed']['classificacao']})
   Funding Rate:  {sentiment['funding_rate']['rate']}% ({sentiment['funding_rate']['viés']})
   
🔮 PROJEÇÕES:
{formatar_cenarios(cenarios)}

💡 SCORE DE CONFLUÊNCIA: {confluencia['score']}/10
   {confluencia['interpretacao']}
   
{formatar_validacoes(confluencia['validacoes'])}

⏰ Validade: 2 horas
🆔 {report_id}
============================================================
"""
    return relatorio


def formatar_niveis(niveis, tipo):
    """Formata níveis de S/R"""
    if not niveis:
        return "   Nenhum nível detectado"
    
    texto = ""
    for n in niveis[:3]:
        texto += f"   ${n['preco']:,.2f} (Força: {n['forca']}, Dist: {n['distancia_pct']}%)\n"
    return texto.rstrip()


def formatar_mtf(mtf):
    """Formata multi-timeframe"""
    if not mtf or 'timeframes' not in mtf:
        return "   Dados indisponíveis"
    
    texto = ""
    for tf, dados in mtf['timeframes'].items():
        texto += f"   {tf}: {dados['status']} (EMA8: {dados['ema8']}, RSI: {dados['rsi']})\n"
    texto += f"\n   {mtf['resumo']}\n"
    return texto.rstrip()


def formatar_zonas(zonas):
    """Formata zonas magnéticas"""
    if not zonas or 'zona_proxima' not in zonas:
        return "   Sem zonas próximas"
    
    return f"""   Zona Próxima: ${zonas['zona_proxima']:,.2f} ({zonas['distancia_pct']}%)
   {zonas['motivo']}"""


def formatar_fluxo(fluxo):
    """Formata fluxo DOM"""
    if not fluxo or 'erro' in fluxo:
        return "   Dados indisponíveis"
    
    return f"""   Bid/Ask Ratio:  {fluxo['fluxo_ratio']:.3f}
   Pressão:        {fluxo['pressao']} ({fluxo['intensidade']:.0f}%)
   Desequilíbrio:  {fluxo['desequilibrio_top10']:+.2f}"""


def formatar_padroes(padroes):
    """Formata padrões"""
    if not padroes:
        return "   Nenhum padrão detectado"
    
    texto = ""
    if 'divergencias' in padroes and padroes['divergencias']['detectada']:
        texto += f"   Divergência: {padroes['divergencias']['descricao']}\n"
    if 'candlestick' in padroes:
        texto += f"   Candlestick: {padroes['candlestick']['padrao']}\n"
    if 'chartpatterns' in padroes:
        texto += f"   Chart Pattern: {padroes['chartpatterns']['padrao']}\n"
    
    return texto.rstrip() if texto else "   Nenhum padrão especial"


def formatar_cenarios(cenarios):
    """Formata cenários"""
    return f"""
   📊 BASE ({cenarios['cenario_base']['probabilidade']:.0f}%):
      {cenarios['cenario_base']['movimento']}
      Target: ${cenarios['cenario_base']['target']:,.2f}
      Timeframe: {cenarios['cenario_base']['timeframe']}
   
   📈 OTIMISTA ({cenarios['cenario_otimista']['probabilidade']:.0f}%):
      {cenarios['cenario_otimista']['movimento']}
      Target: ${cenarios['cenario_otimista']['target']:,.2f}
   
   📉 PESSIMISTA ({cenarios['cenario_pessimista']['probabilidade']:.0f}%):
      {cenarios['cenario_pessimista']['movimento']}
      Target: ${cenarios['cenario_pessimista']['target']:,.2f}"""


def formatar_validacoes(validacoes):
    """Formata validações"""
    texto = "   Validações:\n"
    for v in validacoes:
        texto += f"   {v['status']} {v['camada']}: +{v['contribuicao']}\n"
    return texto.rstrip()


def formatar_wedges(wedges):
    """Formata análise de wedges"""
    if not wedges or not wedges.get('wedge_detectado', False):
        return "   Nenhum padrão wedge detectado"
    
    wedge = wedges
    texto = f"""   🔺 {wedge['nome']} DETECTADO!
   
   📊 Características:
      Tipo: {wedge['tipo']}
      Confiança: {wedge['confianca']}%
      Prob. Reversão: {wedge['probabilidade_reversao']}%
      Altura: ${wedge['altura_wedge']:,.2f}
      Volume Médio: {wedge['volume_medio']:,.0f}
   
   📈 Análise:
      Inclinação Resistência: {wedge['inclinacao_resistencia']:.4f}
      Inclinação Suporte: {wedge['inclinacao_suporte']:.4f}
      Convergência: {wedge['convergencia']:.4f}
   
   🎯 Níveis Operacionais:"""
    
    if wedge.get('alvo_teorico'):
        alvo = wedge['alvo_teorico']
        texto += f"""
      Alvo Teórico: ${alvo['preco']:,.2f} ({alvo['direcao']})
      Distância: ${alvo['distancia']:,.2f} ({alvo['percentual']:.1f}%)"""
    
    if wedge.get('stop_loss'):
        stop = wedge['stop_loss']
        texto += f"""
      Stop Loss: ${stop['preco']:,.2f} ({stop['tipo']})
      Distância SL: ${stop['distancia']:,.2f} ({stop['percentual']:.1f}%)"""
    
    if wedge.get('ponto_convergencia'):
        conv = wedge['ponto_convergencia']
        texto += f"""
      Ponto Convergência: ${conv['y']:,.2f}
      Períodos Futuros: {conv['periodos_futuros']:.0f}"""
    
    # Interpretação do sinal
    if wedge['tipo'] == 'RISING_WEDGE':
        texto += f"""
   
   ⚠️ INTERPRETAÇÃO:
      Rising Wedge = Sinal BEARISH
      Expectativa: Queda após rompimento do suporte
      Recomendação: Considerar posições SHORT"""
    elif wedge['tipo'] == 'FALLING_WEDGE':
        texto += f"""
   
   ⚠️ INTERPRETAÇÃO:
      Falling Wedge = Sinal BULLISH  
      Expectativa: Alta após rompimento da resistência
      Recomendação: Considerar posições LONG"""
    
    return texto


def formatar_candles_detalhados(analise_candles):
    """Formata análise detalhada de candles para relatório"""
    if 'erro' in analise_candles:
        return f"   ❌ Erro: {analise_candles['erro']}"
    
    try:
        candle_info = analise_candles['candle_atual']
        precos = analise_candles['precos']
        sombras = analise_candles['sombras']
        classificacao = analise_candles['classificacao']
        tendencia = analise_candles['tendencia']
        volume = analise_candles['volume']
        analise_tecnica = analise_candles['analise_tecnica']
        padroes = analise_candles['padroes']
        
        texto = f"""   🕐 CANDLE ATUAL:
      Início:     {candle_info['timestamp_inicio']}
      Fechamento: {candle_info['timestamp_fechamento']}
      Restante:   {candle_info['tempo_restante']}
      Timeframe:  {candle_info['timeframe']}
      
   💰 PREÇOS:
      Open:       ${precos['open']:,.2f}
      High:       ${precos['high']:,.2f}
      Low:        ${precos['low']:,.2f}
      Close:      ${precos['close']:,.2f}
      Range:      ${precos['range']:,.2f} ({precos['range_percentual']}%)
      Corpo:      ${precos['corpo']:,.2f} ({precos['corpo_percentual']}%)
      
   📊 SOMBRAS:
      Superior:   ${sombras['superior']:,.2f} ({sombras['superior_pct']}%)
      Inferior:   ${sombras['inferior']:,.2f} ({sombras['inferior_pct']}%)
      
   🎯 CLASSIFICAÇÃO:
      Tipo:       {classificacao['tipo']}
      Descrição:  {classificacao['descricao']}
      Significado: {classificacao['significado']}
      Força:      {classificacao['forca']}
      
   📈 TENDÊNCIA:
      Direção:    {tendencia['direcao']} {tendencia['intensidade']}
      Variação:   {tendencia['variacao_vs_anterior']}% vs anterior
      Fechamento: {tendencia['fechamento_vs_abertura']}% vs abertura
      Rejeição:   {'Superior' if tendencia['rejeicao_superior'] else 'Inferior' if tendencia['rejeicao_inferior'] else 'Nenhuma'}
      
   📊 VOLUME:
      Atual:      {volume['atual']:,.0f}
      Anterior:   {volume['anterior']:,.0f}
      Ratio:      {volume['ratio_vs_anterior']}x vs anterior
      Médio 20:   {volume['medio_20']:,.0f}
      Status:     {volume['status']}
      
   ⚡ ANÁLISE TÉCNICA:
      Força:      {analise_tecnica['forca_candle']['classificacao']} ({analise_tecnica['forca_candle']['score']}/100)
      Momentum:   {analise_tecnica['momentum']['classificacao']} ({analise_tecnica['momentum']['valor']}%)
      Volatilidade: {analise_tecnica['volatilidade']['classificacao']} ({analise_tecnica['volatilidade']['valor']}%)
      Posição:    {analise_tecnica['posicao_relativa']['posicao']} ({analise_tecnica['posicao_relativa']['percentual']}%)
      
   🔍 PADRÕES:
      {padroes['descricao']}"""
        
        # Adicionar padrões detectados
        if padroes['padroes']:
            for padrao in padroes['padroes']:
                texto += f"""
      • {padrao['nome']} ({padrao['tipo']}) - {padrao['confianca']}"""
        
        texto += f"""
      
   📋 RESUMO: {analise_candles['resumo']}"""
        
        return texto
        
    except Exception as e:
        return f"   ❌ Erro ao formatar análise de candles: {str(e)}"


def formatar_gestao_risco(gestao_risco):
    """Formata gestão de risco profissional para relatório"""
    if not gestao_risco:
        return "   Gestão de risco não disponível"
    
    if 'erro' in gestao_risco:
        return f"   ❌ Erro: {gestao_risco['erro']}"
    
    try:
        texto = ""
        
        # Status do setup
        if gestao_risco.get('valido'):
            texto += "   ✅ Status: APROVADO\n"
        else:
            texto += "   ❌ Status: REJEITADO\n"
        
        # Score de qualidade
        score_qualidade = gestao_risco.get('score_qualidade', 0)
        if score_qualidade >= 80:
            qualidade_text = "EXCELENTE"
        elif score_qualidade >= 60:
            qualidade_text = "BOA"
        elif score_qualidade >= 40:
            qualidade_text = "REGULAR"
        else:
            qualidade_text = "BAIXA"
        
        texto += f"   ⭐ Qualidade: {score_qualidade}/100 ({qualidade_text})\n"
        
        # Informações da posição
        posicao = gestao_risco.get('posicao', {})
        if posicao:
            texto += f"""
   💰 POSIÇÃO:
      Quantidade: {posicao.get('quantidade', 0):.6f} moedas
      Alavancagem: {posicao.get('alavancagem', 0):.1f}x
      Margem Necessária: ${posicao.get('margem_necessaria', 0):,.2f}
      Valor Posição: ${posicao.get('valor_posicao', 0):,.2f}
      Exposição Total: ${posicao.get('exposicao_total', 0):,.2f}
"""
        
        # Informações de risco
        texto += f"""
   ⚠️ RISCO:
      Risco USD: ${posicao.get('risco_usd', 0):,.2f}
      Risco % Capital: {posicao.get('risco_pct_capital', 0):.2f}%
      R/R Atual: 1:{gestao_risco.get('rr_atual', 0):.1f}
      R/R Mínimo: 1:{gestao_risco.get('rr_minimo', 0):.1f}
"""
        
        # Validações e warnings
        validacoes = gestao_risco.get('validacoes', [])
        if validacoes:
            texto += f"\n   ❌ MOTIVOS DE REJEIÇÃO:\n"
            for validacao in validacoes:
                texto += f"      • {validacao}\n"
        
        warnings = gestao_risco.get('warnings', [])
        if warnings:
            texto += f"\n   ⚠️ AVISOS:\n"
            for warning in warnings:
                texto += f"      • {warning}\n"
        
        return texto
        
    except Exception as e:
        return f"   ❌ Erro ao formatar gestão de risco: {str(e)}"



