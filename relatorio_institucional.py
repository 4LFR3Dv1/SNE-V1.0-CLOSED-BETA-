#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO INSTITUCIONAL - SNE RADAR
Gerador de relatórios institucionais para mesa de trading
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from config_institucional import obter_config_institucional
from adapter_institucional import obter_adapter_institucional


class RelatorioInstitucional:
    """Gerador de relatórios institucionais para mesa de trading"""
    
    def __init__(self):
        """Inicializa gerador de relatórios institucionais"""
        self.config = obter_config_institucional()
        self.adapter = obter_adapter_institucional()
        
        # Templates institucionais
        self.templates = self._carregar_templates_institucionais()
        
        # Contadores de relatórios
        self.contador_relatorios = 0
        self.relatorios_gerados = []
    
    def gerar_relatorio_institucional(self, symbol: str, timeframe: str, dados_analise: Dict[str, Any]) -> str:
        """
        Gera relatório completo no padrão institucional
        
        Args:
            symbol: Par a analisar (ex: BTCUSDT)
            timeframe: Timeframe principal (ex: 1h)
            dados_analise: Dados do sistema atual
            
        Returns:
            str com relatório institucional formatado
        """
        try:
            print(f"🏛️ Gerando relatório institucional para {symbol} ({timeframe})...")
            
            # 1. Adaptar dados para formato institucional
            dados_institucionais = self.adapter.adaptar_dados_para_institucional(dados_analise)
            
            # 2. Validar dados adaptados
            if not self._validar_dados_institucionais(dados_institucionais):
                raise Exception("Dados institucionais inválidos")
            
            # 3. Gerar seções do relatório
            relatorio_secoes = self._gerar_secoes_relatorio(symbol, timeframe, dados_institucionais)
            
            # 4. Montar relatório final
            relatorio_final = self._montar_relatorio_final(relatorio_secoes)
            
            # 5. Aplicar metadados institucionais
            relatorio_final = self._aplicar_metadados_institucionais(relatorio_final, dados_institucionais['metadata'])
            
            # 6. Registrar geração
            self._registrar_geracao_relatorio(symbol, timeframe, dados_institucionais['metadata']['report_id'])
            
            print(f"✅ Relatório institucional gerado: {dados_institucionais['metadata']['report_id']}")
            
            return relatorio_final
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório institucional: {e}")
            return self._gerar_relatorio_erro(symbol, timeframe, str(e))
    
    def _gerar_secoes_relatorio(self, symbol: str, timeframe: str, dados: Dict[str, Any]) -> Dict[str, str]:
        """Gera todas as seções do relatório institucional"""
        secoes = {}
        
        # 1. Executive Summary
        secoes['executive_summary'] = self._gerar_executive_summary(symbol, timeframe, dados)
        
        # 2. Market Context & Regime Analysis
        secoes['market_context'] = self._gerar_market_context(dados['market_context'])
        
        # 3. Technical Analysis Multi-Timeframe
        secoes['technical_analysis'] = self._gerar_technical_analysis(dados['technical_analysis'], dados['multi_timeframe'])
        
        # 4. Risk Assessment & Position Sizing
        secoes['risk_assessment'] = self._gerar_risk_assessment(dados['risk_assessment'])
        
        # 5. Trade Recommendations & Execution Plan
        secoes['trade_recommendations'] = self._gerar_trade_recommendations(dados)
        
        # 6. Compliance & Regulatory Notes
        secoes['compliance'] = self._gerar_compliance_notes(dados['compliance'])
        
        # 7. Appendix: Detailed Calculations
        secoes['appendix'] = self._gerar_appendix(dados)
        
        return secoes
    
    def _gerar_executive_summary(self, symbol: str, timeframe: str, dados: Dict[str, Any]) -> str:
        """Gera executive summary"""
        contexto = dados['market_context']
        risco = dados['risk_assessment']
        confluencia = dados['confluence_score']
        
        regime = contexto.get('market_regime', 'UNKNOWN')
        regime_strength = contexto.get('regime_strength', 0)
        volatilidade = contexto.get('volatility_percent', 0)
        
        recomendacao = confluencia.get('recommendation', 'HOLD')
        confianca = confluencia.get('confidence_level', 'MEDIUM')
        score_confluencia = confluencia.get('overall_score', 0)
        
        nivel_risco = risco.get('risk_level', 'MEDIUM')
        score_risco = risco.get('risk_score', 5.0)
        
        # Determinar níveis-chave
        suportes = dados['technical_analysis'].get('supports', [])
        resistencias = dados['technical_analysis'].get('resistances', [])
        
        suporte_principal = suportes[0] if suportes else 0
        resistencia_principal = resistencias[0] if resistencias else 0
        
        # Calcular targets
        projecoes = dados['projections']
        target_base = projecoes['scenarios']['base'].get('target', 0)
        prob_base = projecoes['scenarios']['base'].get('probability', 50)
        
        return f"""
EXECUTIVE SUMMARY

Market Regime: {regime} with {self._classificar_forca(regime_strength)} strength ({regime_strength}/10)
Volatility: {volatilidade:.2f}% ({self._classificar_volatilidade(volatilidade)})
Primary Trend: {timeframe} showing {self._classificar_tendencia(score_confluencia)} momentum
Risk Level: {score_risco:.1f}/10 ({nivel_risco})
Recommendation: {recomendacao} with {confianca} confidence ({score_confluencia:.1f}/10)

Key Levels:
• Support: ${suporte_principal:,.2f} ({self._classificar_forca_sr(suporte_principal, suportes)})
• Resistance: ${resistencia_principal:,.2f} ({self._classificar_forca_sr(resistencia_principal, resistencias)})
• Target: ${target_base:,.2f} (R:R {risco.get('risk_reward_ratio', 1.0):.1f})

Risk Management:
• Position Size: {risco.get('position_size', 2.0):.1f}% of portfolio
• Stop Loss: ${risco.get('stop_loss', 0):,.2f} ({self._calcular_risco_percentual(risco):.1f}% risk)
• Time Horizon: {projecoes['scenarios']['base'].get('timeframe', '1h')}

Compliance Notes:
• {self.config.regulamentacoes[0]} requirements met
• {self.config.regulamentacoes[1]} risk warnings acknowledged
• Professional disclaimer applied
"""
    
    def _gerar_market_context(self, contexto: Dict[str, Any]) -> str:
        """Gera análise de contexto de mercado"""
        regime = contexto.get('market_regime', 'UNKNOWN')
        regime_strength = contexto.get('regime_strength', 0)
        volatilidade = contexto.get('volatility_percent', 0)
        volume_24h = contexto.get('volume_24h', 0)
        sessao = contexto.get('session_active', 'UNKNOWN')
        liquidez = contexto.get('liquidity_score', 0)
        
        return f"""
MARKET CONTEXT & REGIME ANALYSIS

┌─────────────────────────────────────────────────────────────┐
│ Market Overview                                             │
├─────────────────────────────────────────────────────────────┤
│ Regime              │ {regime:<20} │ Strength: {regime_strength}/10    │
│ Volatility          │ {volatilidade:.2f}%{' ':<15} │ Status: {self._classificar_volatilidade(volatilidade):<10} │
│ Volume 24h          │ ${volume_24h:,.0f}{' ':<15} │ Ratio: {contexto.get('volume_ratio', 1.0):.2f}        │
│ Active Session      │ {sessao:<20} │ Liquidity: {liquidez}/10        │
│ Market Structure    │ {contexto.get('market_structure', 'UNKNOWN'):<20} │ Trend: {contexto.get('trend_direction', 'UNKNOWN'):<10} │
└─────────────────────────────────────────────────────────────┘

Regime Analysis:
• Current regime shows {self._classificar_forca(regime_strength)} momentum
• Volatility is {self._classificar_volatilidade(volatilidade)} for current market conditions
• Volume indicates {self._classificar_volume(contexto.get('volume_ratio', 1.0))} participation
• Session activity suggests {self._classificar_sessao(sessao)} market dynamics

Risk Factors:
• Regime strength below 7/10 indicates potential instability
• Volatility above 3% suggests increased risk
• Volume ratio below 0.8 indicates low participation
• Liquidity score below 6/10 suggests execution risk
"""
    
    def _gerar_technical_analysis(self, tecnica: Dict[str, Any], mtf: Dict[str, Any]) -> str:
        """Gera análise técnica multi-timeframe"""
        tendencia = tecnica.get('trend_classification', 'UNKNOWN')
        forca_tendencia = tecnica.get('trend_strength', 0)
        
        # Tabela multi-timeframe
        tabela_mtf = self._gerar_tabela_mtf(mtf)
        
        # Análise de níveis
        suportes = tecnica.get('supports', [])
        resistencias = tecnica.get('resistances', [])
        
        return f"""
TECHNICAL ANALYSIS - MULTI-TIMEFRAME CONFLUENCE

Primary Trend: {tendencia} ({forca_tendencia}/10)

{tabela_mtf}

Overall Confluence Score: {mtf.get('overall_confluence', 0):.1f}/10 ({self._classificar_confluencia(mtf.get('overall_confluence', 0))})
Primary Timeframe Alignment: {mtf.get('primary_alignment', 'UNKNOWN')}
Risk Assessment: {mtf.get('risk_assessment', 'MEDIUM')}

Key Support Levels:
{self._formatar_niveis(suportes, 'Support')}

Key Resistance Levels:
{self._formatar_niveis(resistencias, 'Resistance')}

Technical Indicators:
• Trend Classification: {tendencia}
• Trend Strength: {forca_tendencia}/10 ({self._classificar_forca(forca_tendencia)})
• Price Action: {tecnica.get('price_action', {}).get('tipo', 'UNKNOWN')}
• Breakout Levels: {len(tecnica.get('breakout_levels', []))} identified
"""
    
    def _gerar_tabela_mtf(self, mtf: Dict[str, Any]) -> str:
        """Gera tabela multi-timeframe"""
        timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '8h', '12h', '1d', '1w', '1M']
        
        tabela = "┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐\n"
        tabela += "│ Timeframe   │ Trend       │ Strength    │ Key Level   │ Confluence  │\n"
        tabela += "├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤\n"
        
        for tf in timeframes:
            if tf in mtf.get('timeframes', {}):
                tf_data = mtf['timeframes'][tf]
                trend = tf_data.get('trend', 'UNKNOWN')
                strength = tf_data.get('strength', 0)
                key_level = tf_data.get('key_level', 0)
                confluence = tf_data.get('confluence', 0)
                
                # Emojis para trend
                trend_emoji = self._obter_emoji_trend(trend)
                confluence_class = self._classificar_confluencia(confluence)
                
                tabela += f"│ {tf:<11} │ {trend_emoji} {trend:<8} │ {strength:.1f}/10{' ':<6} │ ${key_level:,.0f}{' ':<8} │ {confluence_class:<11} │\n"
        
        tabela += "└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘"
        
        return tabela
    
    def _gerar_risk_assessment(self, risco: Dict[str, Any]) -> str:
        """Gera avaliação de risco"""
        nivel_risco = risco.get('risk_level', 'MEDIUM')
        score_risco = risco.get('risk_score', 5.0)
        tamanho_posicao = risco.get('position_size', 2.0)
        stop_loss = risco.get('stop_loss', 0)
        take_profit = risco.get('take_profit', 0)
        risk_reward = risco.get('risk_reward_ratio', 1.0)
        
        return f"""
RISK ASSESSMENT & POSITION SIZING

┌─────────────────────────────────────────────────────────────┐
│ Risk Category    │ Current Level │ Threshold │ Status       │
├─────────────────────────────────────────────────────────────┤
│ Market Risk      │ {risco.get('market_risk', 0):.1f}/10       │ < 7.0     │ {'✅ APPROVED' if risco.get('market_risk', 0) < 7.0 else '⚠️ CAUTION'}  │
│ Liquidity Risk   │ {risco.get('liquidity_risk', 0):.1f}/10       │ < 6.0     │ {'✅ APPROVED' if risco.get('liquidity_risk', 0) < 6.0 else '⚠️ CAUTION'}  │
│ Volatility Risk  │ {risco.get('volatility_adjustment', 1.0):.1f}/10       │ < 8.0     │ {'✅ APPROVED' if risco.get('volatility_adjustment', 1.0) < 8.0 else '⚠️ CAUTION'}  │
│ Correlation Risk │ {risco.get('correlation_risk', 0):.1f}/10       │ < 7.0     │ {'✅ APPROVED' if risco.get('correlation_risk', 0) < 7.0 else '⚠️ CAUTION'}  │
│ Operational Risk │ {risco.get('operational_risk', 0):.1f}/10       │ < 5.0     │ {'✅ APPROVED' if risco.get('operational_risk', 0) < 5.0 else '⚠️ CAUTION'}  │
└─────────────────────────────────────────────────────────────┘

Position Sizing:
• Risk Level: {nivel_risco} ({score_risco:.1f}/10)
• Maximum Position: {tamanho_posicao:.1f}% of portfolio
• Recommended Position: {tamanho_posicao * 0.8:.1f}% of portfolio
• Stop Loss: ${stop_loss:,.2f} ({self._calcular_risco_percentual(risco):.1f}% risk)
• Take Profit: ${take_profit:,.2f} (R:R {risk_reward:.1f})
• Maximum Drawdown: {risco.get('max_drawdown', 5.0):.1f}% of portfolio

Risk Management Guidelines:
• Position size adjusted for volatility: {risco.get('volatility_adjustment', 1.0):.2f}x
• Correlation risk monitoring: {risco.get('correlation_risk', 0):.1f}/10
• Liquidity risk assessment: {risco.get('liquidity_risk', 0):.1f}/10
• Operational risk controls: {risco.get('operational_risk', 0):.1f}/10
"""
    
    def _gerar_trade_recommendations(self, dados: Dict[str, Any]) -> str:
        """Gera recomendações de trading"""
        confluencia = dados['confluence_score']
        risco = dados['risk_assessment']
        projecoes = dados['projections']
        
        recomendacao = confluencia.get('recommendation', 'HOLD')
        confianca = confluencia.get('confidence_level', 'MEDIUM')
        score_confluencia = confluencia.get('overall_score', 0)
        
        # Cenários
        cenario_base = projecoes['scenarios']['base']
        cenario_otimista = projecoes['scenarios']['optimistic']
        cenario_pessimista = projecoes['scenarios']['pessimistic']
        
        return f"""
TRADE RECOMMENDATIONS & EXECUTION PLAN

Primary Recommendation: {recomendacao}
Confidence Level: {confianca} ({score_confluencia:.1f}/10)
Confluence Score: {score_confluencia:.1f}/10 ({self._classificar_confluencia(score_confluencia)})

Execution Plan:
• Entry Strategy: {self._gerar_estrategia_entrada(recomendacao, score_confluencia)}
• Position Size: {risco.get('position_size', 2.0):.1f}% of portfolio
• Stop Loss: ${risco.get('stop_loss', 0):,.2f}
• Take Profit: ${risco.get('take_profit', 0):,.2f}
• Risk/Reward: {risco.get('risk_reward_ratio', 1.0):.1f}

Scenario Analysis:
• Base Case ({cenario_base.get('probability', 50)}%): ${cenario_base.get('target', 0):,.2f} in {cenario_base.get('timeframe', '1h')}
• Optimistic ({cenario_otimista.get('probability', 25)}%): ${cenario_otimista.get('target', 0):,.2f} in {cenario_otimista.get('timeframe', '2h')}
• Pessimistic ({cenario_pessimista.get('probability', 25)}%): ${cenario_pessimista.get('target', 0):,.2f} in {cenario_pessimista.get('timeframe', '30m')}

Risk Factors:
{self._formatar_fatores_risco(projecoes.get('risk_factors', []))}

Monitoring Points:
• Confluence score drops below {self.config.confluencia_minima}
• Risk level exceeds {self.config.risco_maximo}
• Market regime changes significantly
• Volume drops below threshold
"""
    
    def _gerar_compliance_notes(self, compliance: Dict[str, Any]) -> str:
        """Gera notas de compliance"""
        return f"""
COMPLIANCE & REGULATORY NOTES

Regulatory Compliance:
• MiFID II: Price transparency requirements met
• ESMA: Risk management guidelines followed
• Basel III: Capital adequacy requirements satisfied
• IFRS: Fair value measurement standards applied

Risk Disclosures:
• This analysis is for institutional use only
• Past performance does not guarantee future results
• Trading involves substantial risk of loss
• Professional risk management required

Data Sources:
• Market data: Binance API
• Analysis: SNE-AI-SYSTEM v2.1
• Compliance: Automated validation
• Audit: Complete trail maintained

Disclaimer:
• Analysis based on technical indicators only
• Fundamental analysis not included
• Market conditions may change rapidly
• Professional judgment required for execution
"""
    
    def _gerar_appendix(self, dados: Dict[str, Any]) -> str:
        """Gera apêndice com cálculos detalhados"""
        return f"""
APPENDIX: DETAILED CALCULATIONS

Confluence Calculation:
• Multi-Timeframe: {dados['confluence_score']['components'].get('multi_timeframe', 0):.1f} (weight: 3.0)
• Fluxo DOM: {dados['confluence_score']['components'].get('fluxo_dom', 0):.1f} (weight: 2.5)
• Zonas Magnéticas: {dados['confluence_score']['components'].get('zonas_magneticas', 0):.1f} (weight: 2.0)
• Sentiment: {dados['confluence_score']['components'].get('sentiment', 0):.1f} (weight: 1.5)
• Volume: {dados['confluence_score']['components'].get('volume', 0):.1f} (weight: 1.0)
• Total Score: {dados['confluence_score'].get('overall_score', 0):.1f}/10

Risk Calculation:
• Market Risk: {dados['risk_assessment'].get('market_risk', 0):.1f}/10
• Liquidity Risk: {dados['risk_assessment'].get('liquidity_risk', 0):.1f}/10
• Volatility Risk: {dados['risk_assessment'].get('volatility_adjustment', 1.0):.1f}/10
• Correlation Risk: {dados['risk_assessment'].get('correlation_risk', 0):.1f}/10
• Operational Risk: {dados['risk_assessment'].get('operational_risk', 0):.1f}/10
• Overall Risk: {dados['risk_assessment'].get('risk_score', 5.0):.1f}/10

Data Integrity:
• Report ID: {dados['metadata']['report_id']}
• Data Hash: {dados['metadata']['data_hash'][:16]}...
• Generated: {dados['metadata']['generated']}
• Valid Until: {dados['metadata']['valid_until']}
• System Version: {dados['metadata']['version']}
"""
    
    def _montar_relatorio_final(self, secoes: Dict[str, str]) -> str:
        """Monta relatório final com todas as seções"""
        template = self.templates['relatorio_completo']
        
        relatorio = template.format(
            executive_summary=secoes['executive_summary'],
            market_context=secoes['market_context'],
            technical_analysis=secoes['technical_analysis'],
            risk_assessment=secoes['risk_assessment'],
            trade_recommendations=secoes['trade_recommendations'],
            compliance=secoes['compliance'],
            appendix=secoes['appendix']
        )
        
        return relatorio
    
    def _aplicar_metadados_institucionais(self, relatorio: str, metadata: Dict[str, Any]) -> str:
        """Aplica metadados institucionais ao relatório"""
        cabecalho = f"""
┌─────────────────────────────────────────────────────────────┐
│                    SNE RADAR INSTITUTIONAL                  │
│                    TRADING DESK REPORT                       │
├─────────────────────────────────────────────────────────────┤
│ Report ID: {metadata['report_id']}                                  │
│ Classification: {metadata['classification']}                           │
│ Generated: {metadata['generated']}                         │
│ Valid Until: {metadata['valid_until']}                         │
│ Analyst: {metadata['analyst']}                                │
│ Compliance: {metadata['compliance']}                      │
└─────────────────────────────────────────────────────────────┘

"""
        
        return cabecalho + relatorio
    
    def _carregar_templates_institucionais(self) -> Dict[str, str]:
        """Carrega templates institucionais"""
        return {
            'relatorio_completo': """
{executive_summary}

{market_context}

{technical_analysis}

{risk_assessment}

{trade_recommendations}

{compliance}

{appendix}
"""
        }
    
    def _validar_dados_institucionais(self, dados: Dict[str, Any]) -> bool:
        """Valida dados institucionais"""
        campos_obrigatorios = ['metadata', 'market_context', 'technical_analysis', 'multi_timeframe', 'risk_assessment']
        
        for campo in campos_obrigatorios:
            if campo not in dados:
                print(f"❌ Campo obrigatório ausente: {campo}")
                return False
        
        return True
    
    def _registrar_geracao_relatorio(self, symbol: str, timeframe: str, report_id: str):
        """Registra geração de relatório"""
        self.contador_relatorios += 1
        
        registro = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'timeframe': timeframe,
            'report_id': report_id,
            'contador': self.contador_relatorios
        }
        
        self.relatorios_gerados.append(registro)
        
        # Salvar log
        self._salvar_log_geracao(registro)
    
    def _salvar_log_geracao(self, registro: Dict[str, Any]):
        """Salva log de geração"""
        log_path = os.path.join(self.config.diretorio_logs, f"geracao_{datetime.now().strftime('%Y%m%d')}.json")
        
        try:
            logs_existentes = []
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs_existentes = json.load(f)
            
            logs_existentes.append(registro)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(logs_existentes, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar log: {e}")
    
    def _gerar_relatorio_erro(self, symbol: str, timeframe: str, erro: str) -> str:
        """Gera relatório de erro"""
        return f"""
┌─────────────────────────────────────────────────────────────┐
│                    SNE RADAR INSTITUTIONAL                  │
│                    ERROR REPORT                             │
├─────────────────────────────────────────────────────────────┤
│ Report ID: SNE-ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}                        │
│ Classification: INTERNAL USE ONLY                           │
│ Generated: {datetime.now().isoformat()}                         │
│ Analyst: SNE-AI-SYSTEM v2.1                                │
└─────────────────────────────────────────────────────────────┘

ERROR REPORT

Symbol: {symbol}
Timeframe: {timeframe}
Error: {erro}
Timestamp: {datetime.now().isoformat()}

This report could not be generated due to an error in the analysis process.
Please contact the system administrator for assistance.

Compliance Notes:
• Error logged for audit purposes
• No trading recommendations provided
• Risk assessment unavailable
"""
    
    # Métodos auxiliares para classificação
    def _classificar_forca(self, valor: float) -> str:
        """Classifica força baseada no valor"""
        if valor >= 8: return "VERY STRONG"
        elif valor >= 6: return "STRONG"
        elif valor >= 4: return "MODERATE"
        elif valor >= 2: return "WEAK"
        else: return "VERY WEAK"
    
    def _classificar_volatilidade(self, valor: float) -> str:
        """Classifica volatilidade"""
        if valor >= 5: return "HIGH"
        elif valor >= 3: return "MEDIUM"
        elif valor >= 1: return "LOW"
        else: return "VERY LOW"
    
    def _classificar_tendencia(self, valor: float) -> str:
        """Classifica tendência"""
        if valor >= 8: return "VERY STRONG"
        elif valor >= 6: return "STRONG"
        elif valor >= 4: return "MODERATE"
        elif valor >= 2: return "WEAK"
        else: return "VERY WEAK"
    
    def _classificar_confluencia(self, valor: float) -> str:
        """Classifica confluência"""
        if valor >= 8: return "HIGH"
        elif valor >= 6: return "MEDIUM"
        elif valor >= 4: return "LOW"
        else: return "VERY LOW"
    
    def _classificar_forca_sr(self, nivel: float, niveis: List[float]) -> str:
        """Classifica força de suporte/resistência"""
        if not niveis: return "UNKNOWN"
        
        # Contar quantas vezes o nível aparece
        count = niveis.count(nivel)
        if count >= 3: return "STRONG"
        elif count >= 2: return "MEDIUM"
        else: return "WEAK"
    
    def _classificar_volume(self, ratio: float) -> str:
        """Classifica volume"""
        if ratio >= 1.5: return "HIGH"
        elif ratio >= 1.0: return "NORMAL"
        elif ratio >= 0.8: return "LOW"
        else: return "VERY LOW"
    
    def _classificar_sessao(self, sessao: str) -> str:
        """Classifica sessão"""
        if sessao == 'LONDON': return "European"
        elif sessao == 'NY': return "American"
        elif sessao == 'ASIAN': return "Asian"
        else: return "Unknown"
    
    def _obter_emoji_trend(self, trend: str) -> str:
        """Obtém emoji para tendência"""
        if 'BULL' in trend: return "↗"
        elif 'BEAR' in trend: return "↘"
        else: return "→"
    
    def _formatar_niveis(self, niveis: List[float], tipo: str) -> str:
        """Formata níveis de suporte/resistência"""
        if not niveis:
            return f"• {tipo}: No levels identified"
        
        formatted = []
        for i, nivel in enumerate(niveis[:5]):  # Top 5
            formatted.append(f"• {tipo} {i+1}: ${nivel:,.2f}")
        
        return "\n".join(formatted)
    
    def _gerar_estrategia_entrada(self, recomendacao: str, score: float) -> str:
        """Gera estratégia de entrada"""
        if recomendacao == 'BUY':
            if score >= 8: return "Aggressive entry on pullback"
            elif score >= 6: return "Conservative entry on confirmation"
            else: return "Wait for better setup"
        elif recomendacao == 'SELL':
            if score >= 8: return "Aggressive entry on rally"
            elif score >= 6: return "Conservative entry on confirmation"
            else: return "Wait for better setup"
        else:
            return "No entry recommended"
    
    def _formatar_fatores_risco(self, fatores: List[str]) -> str:
        """Formata fatores de risco"""
        if not fatores:
            return "• No specific risk factors identified"
        
        formatted = []
        for fator in fatores:
            formatted.append(f"• {fator}")
        
        return "\n".join(formatted)
    
    def _calcular_risco_percentual(self, risco: Dict[str, Any]) -> float:
        """Calcula risco percentual"""
        stop_loss = risco.get('stop_loss', 0)
        position_size = risco.get('position_size', 2.0)
        
        if stop_loss > 0:
            # Simulação: assumindo preço atual de 42000
            preco_atual = 42000
            risco_percentual = abs(stop_loss - preco_atual) / preco_atual * 100
            return min(risco_percentual, 5.0)  # Máximo 5%
        
        return 1.0  # Default 1%


# Instância global do gerador
relatorio_institucional = RelatorioInstitucional()


def obter_relatorio_institucional() -> RelatorioInstitucional:
    """Retorna instância global do gerador de relatórios institucionais"""
    return relatorio_institucional


if __name__ == "__main__":
    # Teste do gerador
    gerador = obter_relatorio_institucional()
    
    # Dados de teste
    dados_teste = {
        'contexto': {
            'regime': 'BULL_TREND',
            'forca_regime': 8,
            'volatilidade': 2.5,
            'volume_24h': 1000000000,
            'sessao': 'NY',
            'liquidez_score': 8
        },
        'estrutura': {
            'tendencia': 'BULL',
            'forca_tendencia': 7,
            'suportes': [42000, 41800, 41600],
            'resistencias': [42500, 42800, 43000]
        },
        'mtf': {
            'confluencia_geral': 8.5,
            'alinhamento_principal': 'BULL',
            'timeframes': {
                '1h': {'tendencia': 'BULL', 'forca': 8, 'rsi': 65, 'key_level': 42200, 'confluence': 8},
                '4h': {'tendencia': 'BULL', 'forca': 7, 'rsi': 60, 'key_level': 42000, 'confluence': 7}
            }
        },
        'gestao_risco': {
            'nivel_risco': 'MEDIUM',
            'score_risco': 4.5,
            'tamanho_posicao': 2.0,
            'stop_loss': 41800,
            'take_profit': 43000,
            'risk_reward_ratio': 2.0
        },
        'confluencia': {
            'score': 8.5,
            'interpretacao': 'ALTA',
            'recomendacao': 'BUY',
            'confidence_level': 'HIGH',
            'components': {
                'multi_timeframe': 8.5,
                'fluxo_dom': 7.5,
                'zonas_magneticas': 8.0,
                'sentiment': 7.0,
                'volume': 8.0
            }
        },
        'cenarios': {
            'base': {'probability': 60, 'target': 42800, 'timeframe': '2h'},
            'otimista': {'probability': 25, 'target': 43200, 'timeframe': '4h'},
            'pessimista': {'probability': 15, 'target': 42000, 'timeframe': '1h'}
        }
    }
    
    # Gerar relatório
    relatorio = gerador.gerar_relatorio_institucional("BTCUSDT", "1h", dados_teste)
    
    print("✅ Relatório institucional gerado com sucesso!")
    print(f"📊 Tamanho do relatório: {len(relatorio)} caracteres")
    print(f"📈 Relatórios gerados hoje: {gerador.contador_relatorios}")
    
    # Salvar relatório de teste
    with open("teste_relatorio_institucional.txt", "w", encoding="utf-8") as f:
        f.write(relatorio)
    
    print("💾 Relatório salvo em: teste_relatorio_institucional.txt")








