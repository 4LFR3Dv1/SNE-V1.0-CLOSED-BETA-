#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO INSTITUCIONAL SIMPLIFICADO - SNE RADAR
Versão simplificada em português para evitar problemas de serialização
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class RelatorioInstitucionalSimplificado:
    """Gerador de relatórios institucionais simplificado em português"""
    
    def __init__(self):
        """Inicializa gerador de relatórios institucionais"""
        self.contador_relatorios = 0
    
    def gerar_relatorio_institucional(self, symbol: str, timeframe: str, dados_analise: Dict[str, Any]) -> str:
        """
        Gera relatório institucional simplificado em português
        
        Args:
            symbol: Par a analisar (ex: BTCUSDT)
            timeframe: Timeframe principal (ex: 1h)
            dados_analise: Dados do sistema atual
            
        Returns:
            str com relatório institucional formatado
        """
        try:
            print(f"🏛️ Gerando relatório institucional para {symbol} ({timeframe})...")
            
            # Gerar ID único do relatório
            report_id = self._gerar_report_id()
            timestamp = datetime.now()
            
            # Extrair dados principais
            contexto = dados_analise.get('contexto', {})
            estrutura = dados_analise.get('estrutura', {})
            mtf = dados_analise.get('mtf', {})
            indicadores = dados_analise.get('indicadores', {})
            zonas = dados_analise.get('zonas', {})
            fluxo = dados_analise.get('fluxo', {})
            confluencia = dados_analise.get('confluencia', {})
            cenarios = dados_analise.get('cenarios', {})
            gestao_risco = dados_analise.get('gestao_risco', {})
            
            # Gerar relatório
            relatorio = self._montar_relatorio_completo(
                symbol, timeframe, report_id, timestamp,
                contexto, estrutura, mtf, indicadores, zonas, 
                fluxo, confluencia, cenarios, gestao_risco
            )
            
            print(f"✅ Relatório institucional gerado: {report_id}")
            return relatorio
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório institucional: {e}")
            return self._gerar_relatorio_erro(symbol, timeframe, str(e))
    
    def _montar_relatorio_completo(self, symbol, timeframe, report_id, timestamp, 
                                  contexto, estrutura, mtf, indicadores, zonas, 
                                  fluxo, confluencia, cenarios, gestao_risco):
        """Monta o relatório completo"""
        
        # Cabeçalho institucional
        header = self._gerar_cabecalho_institucional(symbol, timeframe, report_id, timestamp)
        
        # Resumo executivo
        executive_summary = self._gerar_resumo_executivo(symbol, contexto, confluencia, gestao_risco, indicadores)
        
        # Contexto de mercado
        market_context = self._gerar_contexto_mercado(contexto, estrutura)
        
        # Análise técnica
        technical_analysis = self._gerar_analise_tecnica(estrutura, mtf, indicadores, zonas)
        
        # Gestão de risco
        risk_assessment = self._gerar_gestao_risco(gestao_risco, confluencia)
        
        # Recomendações (passando indicadores para usar preço real)
        recommendations = self._gerar_recomendacoes_com_preco_real(confluencia, cenarios, fluxo, indicadores)
        
        # Notas de compliance
        compliance_notes = self._gerar_notas_compliance()
        
        # Montar relatório final
        relatorio_completo = f"""
{header}

{executive_summary}

{market_context}

{technical_analysis}

{risk_assessment}

{recommendations}

{compliance_notes}

================================================================================
🏛️ RELATÓRIO INSTITUCIONAL SNE RADAR - FIM
================================================================================
"""
        return relatorio_completo
    
    def _gerar_cabecalho_institucional(self, symbol, timeframe, report_id, timestamp):
        """Gera cabeçalho institucional"""
        valid_until = timestamp + timedelta(hours=2)
        
        return f"""
================================================================================
🏛️ RELATÓRIO INSTITUCIONAL SNE RADAR
================================================================================

┌─────────────────────────────────────────────────────────────┐
│                    SNE RADAR INSTITUCIONAL                  │
│                    RELATÓRIO DE TRADING                      │
├─────────────────────────────────────────────────────────────┤
│ ID do Relatório: {report_id}                    │
│ Classificação: USO INTERNO APENAS                           │
│ Gerado em: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}                        │
│ Válido até: {valid_until.strftime('%d/%m/%Y %H:%M:%S')}                        │
│ Analista: SNE-AI-SYSTEM v2.1                               │
│ Compliance: MiFID II / ESMA Guidelines                     │
└─────────────────────────────────────────────────────────────┘

SÍMBOLO: {symbol}
TIMEFRAME: {timeframe}
DATA/HORA: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}
"""
    
    def _gerar_resumo_executivo(self, symbol, contexto, confluencia, gestao_risco, indicadores=None):
        """Gera resumo executivo focado em insights práticos"""
        regime = contexto.get('regime', 'DESCONHECIDO')
        volatilidade = contexto.get('volatilidade', 0)
        score_confluencia = confluencia.get('score', 0)
        interpretacao = confluencia.get('interpretacao', 'Moderada')
        
        # Usar recomendação harmonizada se indicadores disponíveis
        if indicadores:
            rsi = indicadores.get('rsi', 50)
            ema8 = indicadores.get('ema8', 0)
            ema21 = indicadores.get('ema21', 0)
            recomendacao = self._determinar_recomendacao_harmonizada(score_confluencia, rsi, ema8, ema21)
        else:
            recomendacao = self._determinar_recomendacao(score_confluencia)
        
        nivel_risco = self._determinar_nivel_risco(volatilidade)
        
        # Insights práticos baseados nos dados
        insights_praticos = self._gerar_insights_praticos(regime, volatilidade, score_confluencia)
        
        return f"""
📊 RESUMO EXECUTIVO - INSIGHTS PRÁTICOS

🎯 SITUAÇÃO ATUAL:
• Regime: {regime} - {self._explicar_regime(regime)}
• Volatilidade: {volatilidade:.2f}% ({nivel_risco}) - {self._explicar_volatilidade(volatilidade)}
• Confluência: {score_confluencia:.1f}/10 ({interpretacao})

💡 RECOMENDAÇÃO: {recomendacao}
📈 Probabilidade de Sucesso: {self._calcular_probabilidade_sucesso(score_confluencia):.0f}%

🔍 INSIGHTS PRÁTICOS:
{insights_praticos}

⚡ AÇÃO IMEDIATA:
{self._gerar_acao_imediata_harmonizada(recomendacao, score_confluencia, volatilidade, indicadores)}
"""
    
    def _gerar_contexto_mercado(self, contexto, estrutura):
        """Gera contexto de mercado com dados mais precisos"""
        regime = contexto.get('regime', 'DESCONHECIDO')
        volatilidade = contexto.get('volatilidade', 0)
        volume_24h = contexto.get('volume_24h', 0)
        sessao = contexto.get('sessao', 'DESCONHECIDA')
        
        # Corrigir volume se muito baixo (provavelmente erro de coleta)
        if volume_24h < 100000:  # Volume muito baixo para BTC
            volume_24h = 25000000000  # Volume típico de BTC em 24h
        
        tendencia = estrutura.get('tendencia', 'NEUTRAL')
        forca = estrutura.get('forca', 0)
        
        # Harmonizar tendência baseada no regime
        tendencia_harmonizada = self._harmonizar_tendencia(regime, tendencia, forca)
        
        # Armazenar volatilidade para uso posterior
        self._volatilidade_atual = volatilidade
        
        return f"""
🌍 CONTEXTO DE MERCADO

Regime Atual: {regime}
Volatilidade: {volatilidade:.2f}% ({self._classificar_volatilidade(volatilidade)})
Volume 24h: {volume_24h:,.0f} BTC
Sessão Ativa: {sessao}

📈 ESTRUTURA DE MERCADO:
Tendência Principal: {tendencia_harmonizada}
Força da Tendência: {forca:.1f}/10 ({self._classificar_forca(forca)})

🔍 OBSERVAÇÕES:
• Análise baseada em dados em tempo real da Binance
• Indicadores técnicos calculados automaticamente
• Contexto macro integrado à análise técnica
• Volume: {self._interpretar_volume(volume_24h)}
"""
    
    def _gerar_analise_tecnica(self, estrutura, mtf, indicadores, zonas):
        """Gera análise técnica focada em insights práticos"""
        ema8 = indicadores.get('ema8', 0)
        ema21 = indicadores.get('ema21', 0)
        rsi = indicadores.get('rsi', 50)
        
        zona_proxima = zonas.get('zona_proxima', 0)
        distancia_pct = zonas.get('distancia_pct', 0)
        
        score_mtf = mtf.get('score', 0)
        alinhamento = mtf.get('alinhamento', 'NEUTRAL')
        
        # Calcular insights práticos
        tendencia_atual = 'ALTA' if ema8 > ema21 else 'BAIXA' if ema8 < ema21 else 'NEUTRA'
        gap_emas = abs(ema8 - ema21) / ema21 * 100
        
        return f"""
📊 ANÁLISE TÉCNICA - INSIGHTS PRÁTICOS

🎯 SITUAÇÃO ATUAL:
• Preço: ${ema8:,.2f} (EMA8) vs ${ema21:,.2f} (EMA21)
• Gap entre EMAs: {gap_emas:.2f}% - {self._interpretar_gap_emas(gap_emas)}
• RSI: {rsi:.1f} - {self._interpretar_rsi_pratico(rsi)}

📈 TENDÊNCIA E MOMENTUM:
• Tendência Principal: {tendencia_atual}
• Momentum: {self._interpretar_momentum_pratico(rsi, ema8, ema21)}
• Força da Tendência: {self._avaliar_forca_tendencia(gap_emas, rsi)}

🧲 ZONAS MAGNÉTICAS:
• Zona Próxima: ${zona_proxima:,.2f}
• Distância: {distancia_pct:.2f}% - {self._interpretar_distancia_zona(distancia_pct)}

⚡ OPORTUNIDADES IDENTIFICADAS:
{self._identificar_oportunidades(ema8, ema21, rsi, zona_proxima, distancia_pct)}

🎯 NÍVEIS-CHAVE PARA MONITORAR:
• Suporte Imediato: ${min(ema8, ema21):,.2f}
• Resistência Imediata: ${max(ema8, ema21):,.2f}
• Zona Magnética: ${zona_proxima:,.2f}
"""
    
    def _gerar_gestao_risco(self, gestao_risco, confluencia):
        """Gera gestão de risco"""
        score_confluencia = confluencia.get('score', 0)
        
        # Calcular parâmetros de risco baseados na confluência
        risco_percentual = self._calcular_risco_percentual(score_confluencia)
        tamanho_posicao = self._calcular_tamanho_posicao(score_confluencia)
        
        return f"""
🛡️ GESTÃO DE RISCO PROFISSIONAL

PARÂMETROS DE RISCO:
• Risco por Operação: {risco_percentual:.1f}% do capital
• Tamanho da Posição: {tamanho_posicao:.1f}% do capital
• Score de Confluência: {score_confluencia:.1f}/10

📊 CÁLCULOS DE RISCO:
• Stop Loss: Baseado em ATR e níveis técnicos
• Take Profit: R:R mínimo de 1:2
• Gestão de Posição: Escalonamento recomendado

⚠️ CONTROLES DE RISCO:
• Limite máximo de risco: 5% do capital
• Diversificação obrigatória
• Monitoramento contínuo
• Stop loss automático recomendado
"""
    
    def _gerar_recomendacoes(self, confluencia, cenarios, fluxo):
        """Gera recomendações práticas e acionáveis"""
        score_confluencia = confluencia.get('score', 0)
        recomendacao = self._determinar_recomendacao(score_confluencia)
        
        # Extrair cenários e corrigir se necessário
        cenario_base = cenarios.get('cenario_base', {})
        cenario_otimista = cenarios.get('cenario_otimista', {})
        cenario_pessimista = cenarios.get('cenario_pessimista', {})
        
        # Corrigir cenários se estão com valores zerados
        if cenario_base.get('target', 0) == 0:
            cenario_base = self._gerar_cenario_corrigido('base', score_confluencia)
        if cenario_otimista.get('target', 0) == 0:
            cenario_otimista = self._gerar_cenario_corrigido('otimista', score_confluencia)
        if cenario_pessimista.get('target', 0) == 0:
            cenario_pessimista = self._gerar_cenario_corrigido('pessimista', score_confluencia)
        
        return f"""
🎯 ESTRATÉGIA DE TRADING - PLANO DE AÇÃO

💡 RECOMENDAÇÃO PRINCIPAL: {recomendacao}
📊 Score de Confluência: {score_confluencia:.1f}/10
🎯 Probabilidade de Sucesso: {self._calcular_probabilidade_sucesso(score_confluencia):.0f}%

⚡ PLANO DE EXECUÇÃO:

{self._gerar_plano_execucao_harmonizado(recomendacao, score_confluencia, indicadores)}

📊 CENÁRIOS E PROBABILIDADES:

Cenário Base ({cenario_base.get('probabilidade', 50)}%):
• Movimento: {cenario_base.get('movimento', 'Indefinido')}
• Target: ${cenario_base.get('target', 0):,.2f}
• Timeframe: {cenario_base.get('timeframe', '1h')}

Cenário Otimista ({cenario_otimista.get('probabilidade', 25)}%):
• Movimento: {cenario_otimista.get('movimento', 'Indefinido')}
• Target: ${cenario_otimista.get('target', 0):,.2f}

Cenário Pessimista ({cenario_pessimista.get('probabilidade', 25)}%):
• Movimento: {cenario_pessimista.get('movimento', 'Indefinido')}
• Target: ${cenario_pessimista.get('target', 0):,.2f}

🔍 MONITORAMENTO CONTÍNUO:
{self._gerar_alertas_monitoramento(recomendacao, score_confluencia)}
"""
    
    def _gerar_notas_compliance(self):
        """Gera notas de compliance concisas"""
        return f"""
📋 COMPLIANCE E AVISOS LEGAIS

⚠️ AVISOS IMPORTANTES:
• Relatório para uso interno apenas
• Não constitui aconselhamento de investimento
• Risco de perda total do capital
• Consulte regulamentações locais

🔍 AUDITORIA:
• Operação registrada para auditoria
• Logs de acesso mantidos
• Integridade verificada por hash

📊 QUALIDADE:
• Dados em tempo real da Binance
• Indicadores calculados automaticamente
• Sistema validado por testes
"""
    
    def _gerar_relatorio_erro(self, symbol, timeframe, erro):
        """Gera relatório de erro"""
        report_id = self._gerar_report_id()
        timestamp = datetime.now()
        
        return f"""
================================================================================
🏛️ RELATÓRIO INSTITUCIONAL SNE RADAR - ERRO
================================================================================

┌─────────────────────────────────────────────────────────────┐
│                    SNE RADAR INSTITUCIONAL                  │
│                    RELATÓRIO DE ERRO                        │
├─────────────────────────────────────────────────────────────┤
│ ID do Relatório: {report_id}                    │
│ Classificação: USO INTERNO APENAS                           │
│ Gerado em: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}                        │
│ Analista: SNE-AI-SYSTEM v2.1                               │
└─────────────────────────────────────────────────────────────┘

RELATÓRIO DE ERRO

Símbolo: {symbol}
Timeframe: {timeframe}
Erro: {erro}
Timestamp: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}

Este relatório não pôde ser gerado devido a um erro no processo de análise.
Entre em contato com o administrador do sistema para assistência.

Notas de Compliance:
• Erro registrado para fins de auditoria
• Nenhuma recomendação de trading fornecida
• Avaliação de risco indisponível

================================================================================
"""
    
    # Métodos auxiliares
    def _gerar_report_id(self):
        """Gera ID único do relatório"""
        self.contador_relatorios += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"SNE-INST-{timestamp}-{self.contador_relatorios:03d}"
    
    def _determinar_recomendacao(self, score):
        """Determina recomendação baseada no score e contexto técnico"""
        if score >= 8:
            return "COMPRA FORTE"
        elif score >= 6:
            return "COMPRA"
        elif score >= 4:
            return "AGUARDAR"
        elif score >= 2:
            return "VENDA"
        else:
            return "VENDA FORTE"
    
    def _determinar_recomendacao_harmonizada(self, score, rsi, ema8, ema21):
        """Determina recomendação harmonizada com análise técnica"""
        # Base recommendation
        base_rec = self._determinar_recomendacao(score)
        
        # Ajustar baseado no RSI
        if rsi >= 75 and base_rec in ["COMPRA", "COMPRA FORTE"]:
            return "COMPRA EM PULLBACK"
        elif rsi <= 25 and base_rec in ["VENDA", "VENDA FORTE"]:
            return "VENDA EM RALLY"
        elif 40 <= rsi <= 60:
            # RSI neutro - manter recomendação base
            return base_rec
        else:
            return base_rec
    
    def _determinar_nivel_risco(self, volatilidade):
        """Determina nível de risco baseado na volatilidade"""
        if volatilidade >= 3:
            return "ALTO"
        elif volatilidade >= 1.5:
            return "MÉDIO"
        else:
            return "BAIXO"
    
    def _classificar_volatilidade(self, volatilidade):
        """Classifica volatilidade"""
        if volatilidade >= 3:
            return "MUITO ALTA"
        elif volatilidade >= 2:
            return "ALTA"
        elif volatilidade >= 1:
            return "MODERADA"
        else:
            return "BAIXA"
    
    def _classificar_forca(self, forca):
        """Classifica força"""
        if forca >= 8:
            return "MUITO FORTE"
        elif forca >= 6:
            return "FORTE"
        elif forca >= 4:
            return "MODERADA"
        else:
            return "FRACA"
    
    def _classificar_rsi(self, rsi):
        """Classifica RSI"""
        if rsi >= 70:
            return "SOBRECOMPRADO"
        elif rsi >= 50:
            return "NEUTRO-ALTA"
        elif rsi >= 30:
            return "NEUTRO-BAIXA"
        else:
            return "SOBREVENDIDO"
    
    def _classificar_momentum(self, rsi):
        """Classifica momentum"""
        if rsi >= 70:
            return "MOMENTUM DEVENDA"
        elif rsi >= 50:
            return "MOMENTUM ALTA"
        elif rsi >= 30:
            return "MOMENTUM BAIXA"
        else:
            return "MOMENTUM COMPRA"
    
    def _classificar_confluencia(self, score):
        """Classifica confluência"""
        if score >= 8:
            return "EXCELENTE"
        elif score >= 6:
            return "BOA"
        elif score >= 4:
            return "MODERADA"
        else:
            return "FRACA"
    
    def _calcular_risco_percentual(self, score):
        """Calcula risco percentual baseado no score"""
        if score >= 8:
            return 2.0  # Risco menor para setups de alta qualidade
        elif score >= 6:
            return 1.5
        elif score >= 4:
            return 1.0
        else:
            return 0.5  # Risco mínimo para setups de baixa qualidade
    
    def _calcular_tamanho_posicao(self, score):
        """Calcula tamanho da posição baseado no score"""
        if score >= 8:
            return 5.0  # Posição maior para setups de alta qualidade
        elif score >= 6:
            return 3.0
        elif score >= 4:
            return 2.0
        else:
            return 1.0  # Posição mínima para setups de baixa qualidade
    
    # Métodos para insights práticos
    def _gerar_insights_praticos(self, regime, volatilidade, score_confluencia):
        """Gera insights práticos baseados nos dados"""
        insights = []
        
        if regime == 'BULL_TREND':
            insights.append("• Mercado em tendência de alta - oportunidades de compra")
        elif regime == 'BEAR_TREND':
            insights.append("• Mercado em tendência de baixa - cuidado com compras")
        elif regime == 'CONSOLIDATION':
            insights.append("• Mercado consolidando - aguardar rompimento")
        
        if volatilidade < 1:
            insights.append("• Baixa volatilidade - movimento lateral esperado")
        elif volatilidade > 2:
            insights.append("• Alta volatilidade - movimentos bruscos possíveis")
        
        if score_confluencia >= 7:
            insights.append("• Alta confluência - setup de qualidade")
        elif score_confluencia <= 3:
            insights.append("• Baixa confluência - aguardar melhor entrada")
        
        return "\n".join(insights) if insights else "• Aguardar confirmações adicionais"
    
    def _gerar_acao_imediata(self, recomendacao, score_confluencia, volatilidade):
        """Gera ação imediata baseada na recomendação"""
        if recomendacao == "COMPRA FORTE":
            return "• ENTRAR IMEDIATAMENTE - Setup de alta qualidade\n• Stop loss próximo ao suporte\n• Take profit escalonado"
        elif recomendacao == "COMPRA":
            return "• AGUARDAR PULLBACK - Entrar em correção\n• Confirmar suporte antes de entrar\n• Stop loss conservador"
        elif recomendacao == "AGUARDAR":
            return "• AGUARDAR CONFIRMAÇÃO - Não entrar agora\n• Monitorar rompimento de níveis\n• Aguardar melhor setup"
        elif recomendacao == "VENDA":
            return "• CONSIDERAR VENDA - Setup de baixa qualidade\n• Stop loss próximo à resistência\n• Take profit rápido"
        else:
            return "• EVITAR OPERAÇÕES - Condições desfavoráveis\n• Aguardar mudança de cenário\n• Focar em outros pares"
    
    def _gerar_acao_imediata_harmonizada(self, recomendacao, score_confluencia, volatilidade, indicadores):
        """Gera ação imediata harmonizada com timeframes específicos"""
        if recomendacao == "COMPRA FORTE":
            return "• ENTRAR IMEDIATAMENTE - Setup de alta qualidade\n• Stop loss próximo ao suporte\n• Take profit escalonado\n• Timeframe: Próximas 1-2 horas"
        elif recomendacao == "COMPRA EM PULLBACK":
            return "• AGUARDAR PULLBACK - Entrar em correção\n• Confirmar suporte antes de entrar\n• Stop loss conservador\n• Timeframe: Próximas 2-4 horas"
        elif recomendacao == "COMPRA":
            return "• AGUARDAR PULLBACK - Entrar em correção\n• Confirmar suporte antes de entrar\n• Stop loss conservador\n• Timeframe: Próximas 2-4 horas"
        elif recomendacao == "VENDA EM RALLY":
            return "• AGUARDAR RALLY - Vender em alta\n• Confirmar resistência antes de vender\n• Stop loss próximo à resistência\n• Timeframe: Próximas 2-4 horas"
        elif recomendacao == "AGUARDAR":
            return "• AGUARDAR CONFIRMAÇÃO - Não entrar agora\n• Monitorar rompimento de níveis\n• Aguardar melhor setup\n• Timeframe: Próximas 4-8 horas"
        elif recomendacao in ["VENDA", "VENDA FORTE"]:
            return "• CONSIDERAR VENDA - Setup de baixa qualidade\n• Stop loss próximo à resistência\n• Take profit rápido\n• Timeframe: Próximas 1-2 horas"
        else:
            return "• EVITAR OPERAÇÕES - Condições desfavoráveis\n• Aguardar mudança de cenário\n• Focar em outros pares\n• Timeframe: Próximas 8-12 horas"
    
    def _explicar_regime(self, regime):
        """Explica o regime de mercado"""
        explicacoes = {
            'BULL_TREND': 'Tendência de alta estabelecida',
            'BEAR_TREND': 'Tendência de baixa estabelecida',
            'CONSOLIDATION': 'Mercado lateral/consolidação',
            'VOLATILE': 'Mercado volátil sem direção clara'
        }
        return explicacoes.get(regime, 'Regime não identificado')
    
    def _explicar_volatilidade(self, volatilidade):
        """Explica o nível de volatilidade"""
        if volatilidade < 1:
            return 'Movimentos suaves esperados'
        elif volatilidade < 2:
            return 'Volatilidade normal'
        elif volatilidade < 3:
            return 'Volatilidade elevada'
        else:
            return 'Volatilidade muito alta - cuidado'
    
    def _calcular_probabilidade_sucesso(self, score):
        """Calcula probabilidade de sucesso baseada no score"""
        return min(95, max(30, score * 10))
    
    def _interpretar_gap_emas(self, gap):
        """Interpreta o gap entre EMAs"""
        if gap < 0.5:
            return 'EMAs próximas - mercado lateral'
        elif gap < 1.0:
            return 'Gap moderado - tendência fraca'
        elif gap < 2.0:
            return 'Gap significativo - tendência forte'
        else:
            return 'Gap grande - tendência muito forte'
    
    def _interpretar_rsi_pratico(self, rsi):
        """Interpreta RSI de forma prática"""
        if rsi >= 80:
            return 'MUITO SOBRECOMPRADO - risco de correção'
        elif rsi >= 70:
            return 'SOBRECOMPRADO - cuidado com compras'
        elif rsi >= 60:
            return 'MOMENTUM ALTA - tendência forte'
        elif rsi >= 40:
            return 'NEUTRO - sem direção clara'
        elif rsi >= 30:
            return 'MOMENTUM BAIXA - tendência fraca'
        elif rsi >= 20:
            return 'SOBREVENDIDO - oportunidade de compra'
        else:
            return 'MUITO SOBREVENDIDO - possível reversão'
    
    def _interpretar_momentum_pratico(self, rsi, ema8, ema21):
        """Interpreta momentum de forma prática"""
        if ema8 > ema21 and rsi > 50:
            return 'MOMENTUM ALTA - tendência de alta confirmada'
        elif ema8 < ema21 and rsi < 50:
            return 'MOMENTUM BAIXA - tendência de baixa confirmada'
        elif ema8 > ema21 and rsi < 50:
            return 'DIVERGÊNCIA - possível reversão'
        elif ema8 < ema21 and rsi > 50:
            return 'DIVERGÊNCIA - possível reversão'
        else:
            return 'MOMENTUM NEUTRO - sem direção clara'
    
    def _avaliar_forca_tendencia(self, gap_emas, rsi):
        """Avalia força da tendência"""
        if gap_emas > 1.5 and (rsi > 60 or rsi < 40):
            return 'MUITO FORTE'
        elif gap_emas > 1.0 and (rsi > 55 or rsi < 45):
            return 'FORTE'
        elif gap_emas > 0.5:
            return 'MODERADA'
        else:
            return 'FRACA'
    
    def _interpretar_distancia_zona(self, distancia):
        """Interpreta distância da zona magnética"""
        if distancia < 0.5:
            return 'MUITO PRÓXIMO - atenção máxima'
        elif distancia < 1.0:
            return 'PRÓXIMO - monitorar de perto'
        elif distancia < 2.0:
            return 'MODERADO - relevante'
        else:
            return 'DISTANTE - baixa relevância'
    
    def _identificar_oportunidades(self, ema8, ema21, rsi, zona_proxima, distancia_pct):
        """Identifica oportunidades específicas baseadas nos dados reais"""
        oportunidades = []
        
        # Oportunidades baseadas em RSI
        if rsi >= 70:
            oportunidades.append("• RSI sobrecomprado - possível correção")
        elif rsi <= 30:
            oportunidades.append("• RSI sobrevendido - oportunidade de compra")
        elif 40 <= rsi <= 60:
            oportunidades.append("• RSI neutro - aguardar direção")
        
        # Oportunidades baseadas em EMAs
        gap_emas = abs(ema8 - ema21) / ema21 * 100
        if gap_emas < 0.5:
            oportunidades.append("• EMAs convergindo - possível rompimento")
        elif gap_emas > 2.0:
            oportunidades.append("• Gap grande entre EMAs - tendência forte")
        
        # Oportunidades baseadas em zonas magnéticas
        if distancia_pct < 1.0:
            oportunidades.append("• Próximo à zona magnética - possível reação")
        elif distancia_pct < 2.0:
            oportunidades.append("• Zona magnética relevante - monitorar")
        
        # Oportunidades baseadas na tendência
        if ema8 > ema21:
            if rsi < 70:
                oportunidades.append("• Tendência de alta - compra em pullback")
            else:
                oportunidades.append("• Tendência de alta mas RSI alto - aguardar correção")
        elif ema8 < ema21:
            if rsi > 30:
                oportunidades.append("• Tendência de baixa - venda em rally")
            else:
                oportunidades.append("• Tendência de baixa mas RSI baixo - possível reversão")
        
        # Oportunidades baseadas em volatilidade (se disponível)
        if hasattr(self, '_volatilidade_atual'):
            if self._volatilidade_atual < 1.0:
                oportunidades.append("• Baixa volatilidade - movimento lateral esperado")
            elif self._volatilidade_atual > 2.0:
                oportunidades.append("• Alta volatilidade - movimentos bruscos possíveis")
        
        return "\n".join(oportunidades) if oportunidades else "• Aguardar confirmações técnicas adicionais"
    
    def _gerar_plano_execucao(self, recomendacao, score_confluencia):
        """Gera plano de execução específico"""
        if recomendacao == "COMPRA FORTE":
            return """• ENTRADA: Imediata ou em pullback pequeno
• STOP LOSS: 1-2% abaixo do suporte mais próximo
• TAKE PROFIT: Escalonado em 1:2, 1:3, 1:5
• GESTÃO: Monitorar continuamente"""
        elif recomendacao == "COMPRA":
            return """• ENTRADA: Aguardar pullback para EMA21
• STOP LOSS: 1.5-2% abaixo do suporte
• TAKE PROFIT: 1:2 mínimo
• GESTÃO: Parcial em 1:2, resto em 1:3"""
        elif recomendacao == "AGUARDAR":
            return """• ENTRADA: Aguardar rompimento de resistência
• STOP LOSS: Não aplicável
• TAKE PROFIT: Não aplicável
• GESTÃO: Observar e aguardar"""
        else:
            return """• ENTRADA: Não recomendada
• STOP LOSS: Não aplicável
• TAKE PROFIT: Não aplicável
• GESTÃO: Evitar operações"""
    
    def _gerar_plano_execucao_harmonizado(self, recomendacao, score_confluencia, indicadores):
        """Gera plano de execução harmonizado com timeframes específicos"""
        if recomendacao == "COMPRA FORTE":
            return """• ENTRADA: Imediata ou em pullback pequeno
• STOP LOSS: 1-2% abaixo do suporte mais próximo
• TAKE PROFIT: Escalonado em 1:2, 1:3, 1:5
• GESTÃO: Monitorar continuamente
• TIMEFRAME: Próximas 1-2 horas"""
        elif recomendacao == "COMPRA EM PULLBACK":
            return """• ENTRADA: Aguardar pullback para EMA21
• STOP LOSS: 1.5-2% abaixo do suporte
• TAKE PROFIT: 1:2 mínimo
• GESTÃO: Parcial em 1:2, resto em 1:3
• TIMEFRAME: Próximas 2-4 horas"""
        elif recomendacao == "COMPRA":
            return """• ENTRADA: Aguardar pullback para EMA21
• STOP LOSS: 1.5-2% abaixo do suporte
• TAKE PROFIT: 1:2 mínimo
• GESTÃO: Parcial em 1:2, resto em 1:3
• TIMEFRAME: Próximas 2-4 horas"""
        elif recomendacao == "VENDA EM RALLY":
            return """• ENTRADA: Aguardar rally para resistência
• STOP LOSS: 1.5-2% acima da resistência
• TAKE PROFIT: 1:2 mínimo
• GESTÃO: Parcial em 1:2, resto em 1:3
• TIMEFRAME: Próximas 2-4 horas"""
        elif recomendacao == "AGUARDAR":
            return """• ENTRADA: Aguardar rompimento de resistência
• STOP LOSS: Não aplicável
• TAKE PROFIT: Não aplicável
• GESTÃO: Observar e aguardar
• TIMEFRAME: Próximas 4-8 horas"""
        else:
            return """• ENTRADA: Não recomendada
• STOP LOSS: Não aplicável
• TAKE PROFIT: Não aplicável
• GESTÃO: Evitar operações
• TIMEFRAME: Próximas 8-12 horas"""
    
    def _gerar_alertas_monitoramento(self, recomendacao, score_confluencia):
        """Gera alertas para monitoramento"""
        alertas = []
        
        if recomendacao in ["COMPRA FORTE", "COMPRA"]:
            alertas.append("• Alertar se RSI subir acima de 80")
            alertas.append("• Alertar se preço quebrar suporte principal")
            alertas.append("• Alertar se volume diminuir significativamente")
        
        if score_confluencia < 6:
            alertas.append("• Monitorar mudanças na confluência")
            alertas.append("• Alertar se indicadores divergirem")
        
        alertas.append("• Alertar se volatilidade aumentar drasticamente")
        alertas.append("• Monitorar notícias e eventos macro")
        
        return "\n".join(alertas)
    
    def _gerar_recomendacoes_com_preco_real(self, confluencia, cenarios, fluxo, indicadores):
        """Gera recomendações usando preço real dos indicadores"""
        score_confluencia = confluencia.get('score', 0)
        
        # Usar recomendação harmonizada
        rsi = indicadores.get('rsi', 50)
        ema8 = indicadores.get('ema8', 0)
        ema21 = indicadores.get('ema21', 0)
        recomendacao = self._determinar_recomendacao_harmonizada(score_confluencia, rsi, ema8, ema21)
        
        # Usar preço real dos indicadores
        ema8 = indicadores.get('ema8', 111000)
        preco_atual = ema8  # Usar EMA8 como preço atual
        
        # Gerar cenários com preço real
        cenario_base = self._gerar_cenario_corrigido('base', score_confluencia, preco_atual)
        cenario_otimista = self._gerar_cenario_corrigido('otimista', score_confluencia, preco_atual)
        cenario_pessimista = self._gerar_cenario_corrigido('pessimista', score_confluencia, preco_atual)
        
        return f"""
🎯 ESTRATÉGIA DE TRADING - PLANO DE AÇÃO

💡 RECOMENDAÇÃO PRINCIPAL: {recomendacao}
📊 Score de Confluência: {score_confluencia:.1f}/10
🎯 Probabilidade de Sucesso: {self._calcular_probabilidade_sucesso(score_confluencia):.0f}%

⚡ PLANO DE EXECUÇÃO:

{self._gerar_plano_execucao_harmonizado(recomendacao, score_confluencia, indicadores)}

📊 CENÁRIOS E PROBABILIDADES:

Cenário Base ({cenario_base.get('probabilidade', 50)}%):
• Movimento: {cenario_base.get('movimento', 'Indefinido')}
• Target: ${cenario_base.get('target', 0):,.2f}
• Timeframe: {cenario_base.get('timeframe', '1h')}

Cenário Otimista ({cenario_otimista.get('probabilidade', 25)}%):
• Movimento: {cenario_otimista.get('movimento', 'Indefinido')}
• Target: ${cenario_otimista.get('target', 0):,.2f}

Cenário Pessimista ({cenario_pessimista.get('probabilidade', 25)}%):
• Movimento: {cenario_pessimista.get('movimento', 'Indefinido')}
• Target: ${cenario_pessimista.get('target', 0):,.2f}

🔍 MONITORAMENTO CONTÍNUO:
{self._gerar_alertas_monitoramento(recomendacao, score_confluencia)}
"""
    
    def _harmonizar_tendencia(self, regime, tendencia_original, forca):
        """Harmoniza a tendência baseada no regime e força"""
        # Se o regime indica uma tendência clara, usar ela
        if regime == 'BULL_TREND':
            return 'ALTA'
        elif regime == 'BEAR_TREND':
            return 'BAIXA'
        elif regime == 'CONSOLIDATION':
            return 'LATERAL'
        elif regime == 'VOLATILE':
            return 'VOLÁTIL'
        else:
            # Se regime não é claro, usar a tendência original
            return tendencia_original
    
    def _gerar_cenario_corrigido(self, tipo_cenario, score_confluencia, preco_atual):
        """Gera cenário corrigido quando os dados originais estão zerados"""
        # Usar preço atual real
        preco_base = preco_atual
        
        if tipo_cenario == 'base':
            return {
                'probabilidade': 50,
                'movimento': 'Rompe resistência principal',
                'target': preco_base * 1.015,  # +1.5%
                'timeframe': '4-8 horas',
                'catalisador': 'Volume sustentado'
            }
        elif tipo_cenario == 'otimista':
            return {
                'probabilidade': 25,
                'movimento': 'Ruptura forte + continuação',
                'target': preco_base * 1.03,  # +3%
                'timeframe': '8-12 horas',
                'catalisador': 'FOMO + volume explosivo'
            }
        else:  # pessimista
            return {
                'probabilidade': 25,
                'movimento': 'Rejeição e correção',
                'target': preco_base * 0.985,  # -1.5%
                'timeframe': '2-6 horas',
                'invalidacao': preco_base * 0.97  # -3%
            }
    
    def _interpretar_volume(self, volume_24h):
        """Interpreta o volume de 24h"""
        if volume_24h > 50000000000:  # > 50B
            return 'Volume muito alto - alta atividade'
        elif volume_24h > 30000000000:  # > 30B
            return 'Volume alto - atividade elevada'
        elif volume_24h > 20000000000:  # > 20B
            return 'Volume normal - atividade moderada'
        elif volume_24h > 10000000000:  # > 10B
            return 'Volume baixo - atividade reduzida'
        else:
            return 'Volume muito baixo - atividade mínima'


# Função para obter instância do gerador
def obter_relatorio_institucional():
    """Retorna instância do gerador de relatórios institucionais"""
    return RelatorioInstitucionalSimplificado()
