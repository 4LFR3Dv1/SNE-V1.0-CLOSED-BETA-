#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Priorização Automática de Pares
Seleção inteligente baseada em múltiplos critérios
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import pytz

class PriorizadorInteligente:
    """Sistema de priorização automática de pares"""
    
    def __init__(self):
        self.br_tz = pytz.timezone("America/Sao_Paulo")
        
        # Pesos para cada critério (total = 100%)
        self.pesos = {
            'opportunity_score': 0.30,    # 30% - Score de oportunidade
            'volatility': 0.20,           # 20% - Volatilidade
            'volume': 0.15,               # 15% - Volume
            'trend_strength': 0.15,       # 15% - Força da tendência
            'risk_reward': 0.10,          # 10% - Relação risco/retorno
            'momentum': 0.10              # 10% - Momentum
        }
        
        # Histórico de performance
        self.historico_performance = {}
        
        # Blacklist temporária (pares com problemas)
        self.blacklist = {}
    
    def priorizar_pares(self, resultados: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioriza pares baseado em múltiplos critérios
        Retorna lista ordenada por prioridade
        """
        
        pares_priorizados = []
        
        for symbol, dados in resultados.items():
            # Verificar blacklist
            if self._esta_na_blacklist(symbol):
                continue
            
            # Calcular score de priorização
            score_priorizacao = self._calcular_score_priorizacao(symbol, dados)
            
            # Adicionar informações extras
            dados_priorizados = {
                **dados,
                'priority_score': score_priorizacao,
                'priority_rank': 0,  # Será atualizado depois
                'recommendation': self._gerar_recomendacao(dados, score_priorizacao),
                'entry_points': self._identificar_pontos_entrada(dados),
                'exit_points': self._identificar_pontos_saida(dados)
            }
            
            pares_priorizados.append(dados_priorizados)
        
        # Ordenar por score de priorização
        pares_priorizados.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Atualizar rank
        for i, par in enumerate(pares_priorizados, 1):
            par['priority_rank'] = i
        
        return pares_priorizados
    
    def _calcular_score_priorizacao(self, symbol: str, dados: Dict[str, Any]) -> float:
        """Calcula score de priorização baseado em múltiplos critérios"""
        
        score_total = 0.0
        
        # 1. Opportunity Score (30%)
        opportunity_score = dados.get('opportunity_score', 0)
        score_total += (opportunity_score / 100) * self.pesos['opportunity_score'] * 100
        
        # 2. Volatilidade (20%)
        volatility_score = self._avaliar_volatilidade(dados)
        score_total += volatility_score * self.pesos['volatility'] * 100
        
        # 3. Volume (15%)
        volume_score = self._avaliar_volume(dados)
        score_total += volume_score * self.pesos['volume'] * 100
        
        # 4. Força da Tendência (15%)
        trend_score = self._avaliar_tendencia(dados)
        score_total += trend_score * self.pesos['trend_strength'] * 100
        
        # 5. Relação Risco/Retorno (10%)
        risk_reward_score = self._avaliar_risco_retorno(dados)
        score_total += risk_reward_score * self.pesos['risk_reward'] * 100
        
        # 6. Momentum (10%)
        momentum_score = self._avaliar_momentum(dados)
        score_total += momentum_score * self.pesos['momentum'] * 100
        
        # Ajustar baseado em performance histórica
        if symbol in self.historico_performance:
            performance_multiplier = self.historico_performance[symbol].get('multiplier', 1.0)
            score_total *= performance_multiplier
        
        return min(score_total, 100.0)
    
    def _avaliar_volatilidade(self, dados: Dict[str, Any]) -> float:
        """Avalia volatilidade (ideal: média-alta)"""
        volatility = dados.get('volatility_level', 'BAIXA')
        
        scores = {
            'BAIXA': 0.3,      # Pouco movimento
            'MÉDIA': 0.8,      # Ideal
            'ALTA': 1.0,       # Muito bom
            'EXTREMA': 0.5     # Arriscado demais
        }
        
        return scores.get(volatility, 0.5)
    
    def _avaliar_volume(self, dados: Dict[str, Any]) -> float:
        """Avalia volume (quanto maior, melhor)"""
        volume_profile = dados.get('volume_profile', 'NORMAL')
        
        scores = {
            'BAIXO': 0.3,
            'NORMAL': 0.6,
            'ALTO': 0.9,
            'EXTREMO': 1.0
        }
        
        return scores.get(volume_profile, 0.5)
    
    def _avaliar_tendencia(self, dados: Dict[str, Any]) -> float:
        """Avalia força da tendência"""
        trend = dados.get('trend_direction', 'NEUTRO')
        regime = dados.get('market_regime', 'sideways')
        
        # Tendências fortes são melhores
        if 'FORTE' in trend:
            return 1.0
        elif 'ALTA' in trend or 'BAIXA' in trend:
            return 0.8
        elif 'MISTA' in trend:
            return 0.4
        else:
            return 0.3
    
    def _avaliar_risco_retorno(self, dados: Dict[str, Any]) -> float:
        """Avalia relação risco/retorno"""
        risk = dados.get('risk_level', 'MÉDIO')
        score = dados.get('opportunity_score', 0)
        
        # Baixo risco + alto score = excelente
        if risk == 'BAIXO' and score >= 70:
            return 1.0
        elif risk == 'MÉDIO' and score >= 60:
            return 0.8
        elif risk == 'ALTO' and score >= 80:
            return 0.6
        elif risk == 'MUITO ALTO':
            return 0.3
        else:
            return 0.5
    
    def _avaliar_momentum(self, dados: Dict[str, Any]) -> float:
        """Avalia momentum do mercado"""
        sentiment = dados.get('market_sentiment', 'NEUTRO')
        
        scores = {
            'MUITO OTIMISTA': 1.0,
            'OTIMISTA': 0.9,
            'NEUTRO': 0.5,
            'PESSIMISTA': 0.7,  # Pode ser oportunidade de reversão
            'MUITO PESSIMISTA': 0.8  # Idem
        }
        
        return scores.get(sentiment, 0.5)
    
    def _gerar_recomendacao(self, dados: Dict[str, Any], priority_score: float) -> str:
        """Gera recomendação baseada nos dados"""
        
        symbol = dados.get('symbol', 'UNKNOWN')
        score = dados.get('opportunity_score', 0)
        regime = dados.get('market_regime', 'unknown')
        risk = dados.get('risk_level', 'MÉDIO')
        
        if priority_score >= 80:
            return f"🔥 PRIORIDADE MÁXIMA - {symbol} com score {score:.0f}, {regime}, risco {risk}"
        elif priority_score >= 70:
            return f"⭐ ALTA PRIORIDADE - {symbol} com score {score:.0f}, {regime}, risco {risk}"
        elif priority_score >= 60:
            return f"📊 PRIORIDADE MÉDIA - {symbol} com score {score:.0f}, {regime}, risco {risk}"
        elif priority_score >= 40:
            return f"⚠️ BAIXA PRIORIDADE - {symbol} com score {score:.0f}, {regime}, risco {risk}"
        else:
            return f"❌ SEM PRIORIDADE - {symbol} com score {score:.0f}, {regime}, risco {risk}"
    
    def _identificar_pontos_entrada(self, dados: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica pontos de entrada potenciais"""
        pontos = []
        
        price = dados.get('price', 0)
        support = dados.get('support_resistance', {}).get('support', price * 0.98)
        
        # Ponto 1: Próximo ao suporte
        pontos.append({
            'type': 'support',
            'price': support,
            'confidence': 0.8,
            'description': f"Entrada próxima ao suporte em ${support:.2f}"
        })
        
        # Ponto 2: Breakout
        resistance = dados.get('support_resistance', {}).get('resistance', price * 1.02)
        pontos.append({
            'type': 'breakout',
            'price': resistance * 1.01,
            'confidence': 0.7,
            'description': f"Entrada em breakout acima de ${resistance:.2f}"
        })
        
        # Ponto 3: Pullback
        if 'bull' in dados.get('market_regime', ''):
            pontos.append({
                'type': 'pullback',
                'price': price * 0.99,
                'confidence': 0.75,
                'description': f"Entrada em pullback próximo a ${price * 0.99:.2f}"
            })
        
        return pontos
    
    def _identificar_pontos_saida(self, dados: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica pontos de saída potenciais"""
        pontos = []
        
        price = dados.get('price', 0)
        resistance = dados.get('support_resistance', {}).get('resistance', price * 1.02)
        
        # Ponto 1: Take Profit na resistência
        pontos.append({
            'type': 'take_profit',
            'price': resistance,
            'confidence': 0.8,
            'description': f"Take profit na resistência ${resistance:.2f}"
        })
        
        # Ponto 2: Take Profit parcial
        pontos.append({
            'type': 'partial_profit',
            'price': price * 1.015,
            'confidence': 0.9,
            'description': f"Take profit parcial (50%) em ${price * 1.015:.2f}"
        })
        
        # Ponto 3: Stop Loss
        support = dados.get('support_resistance', {}).get('support', price * 0.98)
        pontos.append({
            'type': 'stop_loss',
            'price': support * 0.99,
            'confidence': 1.0,
            'description': f"Stop loss abaixo do suporte ${support * 0.99:.2f}"
        })
        
        return pontos
    
    def _esta_na_blacklist(self, symbol: str) -> bool:
        """Verifica se o par está na blacklist"""
        if symbol not in self.blacklist:
            return False
        
        # Verificar se o tempo de blacklist expirou
        expiracao = self.blacklist[symbol]
        if datetime.now() > expiracao:
            del self.blacklist[symbol]
            return False
        
        return True
    
    def adicionar_blacklist(self, symbol: str, duracao_horas: int = 24):
        """Adiciona par à blacklist temporária"""
        expiracao = datetime.now() + timedelta(hours=duracao_horas)
        self.blacklist[symbol] = expiracao
        print(f"⚠️ {symbol} adicionado à blacklist até {expiracao.strftime('%Y-%m-%d %H:%M')}")
    
    def atualizar_performance(self, symbol: str, resultado: str, profit_pct: float = 0):
        """Atualiza histórico de performance de um par"""
        if symbol not in self.historico_performance:
            self.historico_performance[symbol] = {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'total_profit': 0.0,
                'multiplier': 1.0
            }
        
        hist = self.historico_performance[symbol]
        hist['trades'] += 1
        
        if resultado == 'win':
            hist['wins'] += 1
            hist['total_profit'] += profit_pct
        elif resultado == 'loss':
            hist['losses'] += 1
            hist['total_profit'] += profit_pct  # profit_pct será negativo
        
        # Calcular win rate
        win_rate = hist['wins'] / hist['trades'] if hist['trades'] > 0 else 0.5
        
        # Ajustar multiplicador baseado em performance
        if win_rate >= 0.7:
            hist['multiplier'] = 1.2  # Aumentar prioridade
        elif win_rate >= 0.6:
            hist['multiplier'] = 1.1
        elif win_rate <= 0.3:
            hist['multiplier'] = 0.7  # Reduzir prioridade
        elif win_rate <= 0.4:
            hist['multiplier'] = 0.85
        else:
            hist['multiplier'] = 1.0
        
        print(f"📊 {symbol} - Win Rate: {win_rate:.1%}, Multiplier: {hist['multiplier']:.2f}")
    
    def gerar_relatorio_priorizacao(self, pares_priorizados: List[Dict[str, Any]]) -> str:
        """Gera relatório de priorização"""
        
        timestamp = datetime.now(self.br_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        relatorio = f"""
🎯 RELATÓRIO DE PRIORIZAÇÃO AUTOMÁTICA
{'='*60}
🕰️ Timestamp: {timestamp}
📊 Total de Pares Analisados: {len(pares_priorizados)}

🏆 TOP 5 PRIORIDADES:
"""
        
        for par in pares_priorizados[:5]:
            symbol = par['symbol']
            priority = par['priority_score']
            opp_score = par['opportunity_score']
            regime = par['market_regime']
            risk = par['risk_level']
            
            relatorio += f"""
{par['priority_rank']}. {symbol} - Prioridade: {priority:.1f}/100
   Score de Oportunidade: {opp_score:.1f}
   Regime: {regime} | Risco: {risk}
   Recomendação: {par['recommendation']}
"""
        
        # Estatísticas
        priorities = [p['priority_score'] for p in pares_priorizados]
        relatorio += f"""
📊 ESTATÍSTICAS:
• Prioridade Média: {np.mean(priorities):.1f}/100
• Maior Prioridade: {max(priorities):.1f}/100
• Pares com Alta Prioridade (≥70): {len([p for p in priorities if p >= 70])}
• Pares com Média Prioridade (50-70): {len([p for p in priorities if 50 <= p < 70])}
• Pares com Baixa Prioridade (<50): {len([p for p in priorities if p < 50])}

{'='*60}
🤖 Relatório gerado automaticamente pelo Sistema de Priorização
"""
        
        return relatorio

# Função principal para integração
def priorizar_pares_automaticamente(resultados: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
    """Função principal para priorização automática"""
    priorizador = PriorizadorInteligente()
    pares_priorizados = priorizador.priorizar_pares(resultados)
    relatorio = priorizador.gerar_relatorio_priorizacao(pares_priorizados)
    return pares_priorizados, relatorio

# Instância global
priorizador_global = PriorizadorInteligente()




