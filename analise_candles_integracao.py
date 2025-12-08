#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRAÇÃO DE ANÁLISE DETALHADA DE CANDLES
Módulo para integrar análise detalhada de candles aos relatórios
"""

from analise_candles_detalhada import analisar_candle_atual
from formatter_relatorio import formatar_candles_detalhados


def incluir_analise_candles_relatorio(resultado_analise, df, timeframe="1h"):
    """
    Inclui análise detalhada de candles no resultado da análise
    
    Args:
        resultado_analise: Resultado da análise completa
        df: DataFrame com dados OHLCV
        timeframe: Timeframe analisado
    
    Returns:
        resultado_analise com análise de candles incluída
    """
    try:
        # Executar análise detalhada de candles
        analise_candles = analisar_candle_atual(df, timeframe)
        
        # Adicionar ao resultado
        resultado_analise['candles_detalhados'] = analise_candles
        
        return resultado_analise
        
    except Exception as e:
        resultado_analise['candles_detalhados'] = {'erro': f'Erro na análise de candles: {str(e)}'}
        return resultado_analise


def formatar_candles_para_relatorio(analise_candles):
    """
    Formata análise de candles para inclusão no relatório
    
    Args:
        analise_candles: Resultado da análise detalhada de candles
    
    Returns:
        str com texto formatado para relatório
    """
    if 'erro' in analise_candles:
        return f"❌ Erro na análise de candles: {analise_candles['erro']}"
    
    try:
        candle_info = analise_candles['candle_atual']
        precos = analise_candles['precos']
        sombras = analise_candles['sombras']
        classificacao = analise_candles['classificacao']
        tendencia = analise_candles['tendencia']
        volume = analise_candles['volume']
        analise_tecnica = analise_candles['analise_tecnica']
        padroes = analise_candles['padroes']
        
        texto = f"""
🕐 CANDLE ATUAL:
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
        return f"❌ Erro ao formatar análise de candles: {str(e)}"


def atualizar_formatter_relatorio():
    """
    Atualiza o formatter de relatório para incluir análise de candles
    """
    # Adicionar função ao formatter_relatorio.py
    formatter_code = '''
def formatar_candles_detalhados(analise_candles):
    """Formata análise detalhada de candles para relatório"""
    if 'erro' in analise_candles:
        return f"   ❌ Erro: {analise_candles['erro']}"
    
    try:
        candle_info = analise_candles['candle_atual']
        precos = analise_candles['precos']
        classificacao = analise_candles['classificacao']
        tendencia = analise_candles['tendencia']
        volume = analise_candles['volume']
        analise_tecnica = analise_candles['analise_tecnica']
        
        texto = f"""   🕐 CANDLE ATUAL:
      Início:     {candle_info['timestamp_inicio']}
      Fechamento: {candle_info['timestamp_fechamento']}
      Restante:   {candle_info['tempo_restante']}
      
   💰 PREÇOS:
      Open:       ${precos['open']:,.2f}
      High:       ${precos['high']:,.2f}
      Low:        ${precos['low']:,.2f}
      Close:      ${precos['close']:,.2f}
      Range:      ${precos['range']:,.2f} ({precos['range_percentual']}%)
      
   🎯 CLASSIFICAÇÃO:
      Tipo:       {classificacao['tipo']}
      Significado: {classificacao['significado']}
      Força:      {classificacao['forca']}
      
   📈 TENDÊNCIA:
      Direção:    {tendencia['direcao']} {tendencia['intensidade']}
      Variação:   {tendencia['variacao_vs_anterior']}% vs anterior
      
   📊 VOLUME:
      Status:     {volume['status']} ({volume['ratio_vs_anterior']}x)
      
   ⚡ ANÁLISE:
      Força:      {analise_tecnica['forca_candle']['classificacao']} ({analise_tecnica['forca_candle']['score']}/100)
      Momentum:   {analise_tecnica['momentum']['classificacao']} ({analise_tecnica['momentum']['valor']}%)
      Posição:    {analise_tecnica['posicao_relativa']['posicao']} ({analise_tecnica['posicao_relativa']['percentual']}%)"""
        
        return texto
        
    except Exception as e:
        return f"   ❌ Erro ao formatar: {str(e)}"
'''
    
    return formatter_code


if __name__ == "__main__":
    # Teste da integração
    print("✅ Módulo de integração de análise de candles criado!")
    print("📋 Para usar:")
    print("   1. Importe: from analise_candles_integracao import incluir_analise_candles_relatorio")
    print("   2. Chame: resultado = incluir_analise_candles_relatorio(resultado, df, timeframe)")
    print("   3. Use: formatar_candles_para_relatorio(resultado['candles_detalhados'])")


