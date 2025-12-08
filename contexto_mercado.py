#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Análise de Contexto de Mercado
Gera interpretações textuais baseadas em padrões algorítmicos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import pytz
from dataclasses import dataclass
from enum import Enum

# Importar módulos do SNE
from services.advanced_indicators import calculate_all_indicators
from services.professional_indicators import calculate_all_professional_indicators
from services.ta_summary import summarize

class MarketRegime(Enum):
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    CONSOLIDATION = "consolidation"

class SignalStrength(Enum):
    VERY_WEAK = 1
    WEAK = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5

@dataclass
class MarketContext:
    """Contexto completo do mercado"""
    symbol: str
    timestamp: datetime
    price: float
    market_regime: MarketRegime
    signal_strength: SignalStrength
    trend_direction: str
    volatility_level: str
    volume_profile: str
    support_resistance: Dict[str, float]
    key_levels: List[float]
    market_sentiment: str
    risk_level: str
    opportunity_score: float
    interpretation: str
    recommendations: List[str]
    warnings: List[str]

class MarketContextAnalyzer:
    """Analisador de contexto de mercado com interpretação algorítmica"""
    
    def __init__(self):
        self.br_tz = pytz.timezone("America/Sao_Paulo")
        self.volatility_thresholds = {
            'low': 0.01,      # < 1%
            'medium': 0.03,    # 1-3%
            'high': 0.05,      # 3-5%
            'extreme': 0.10    # > 5%
        }
        
        self.volume_thresholds = {
            'low': 0.5,       # < 50% da média
            'normal': 1.5,    # 50-150% da média
            'high': 2.0,      # 150-200% da média
            'extreme': 3.0     # > 200% da média
        }
    
    def analyze_market_context(self, symbol: str, df: pd.DataFrame) -> MarketContext:
        """Análise completa do contexto de mercado"""
        
        # Dados básicos
        current_price = df['close'].iloc[-1]
        timestamp = datetime.now(self.br_tz)
        
        # Análise de regime de mercado
        market_regime = self._determine_market_regime(df)
        
        # Análise de força do sinal
        signal_strength = self._calculate_signal_strength(df)
        
        # Análise de tendência
        trend_direction = self._analyze_trend_direction(df)
        
        # Análise de volatilidade
        volatility_level = self._analyze_volatility(df)
        
        # Análise de volume
        volume_profile = self._analyze_volume_profile(df)
        
        # Suporte e resistência
        support_resistance = self._identify_support_resistance(df)
        
        # Níveis-chave
        key_levels = self._identify_key_levels(df)
        
        # Sentimento do mercado
        market_sentiment = self._analyze_market_sentiment(df)
        
        # Nível de risco
        risk_level = self._assess_risk_level(df, market_regime, volatility_level)
        
        # Score de oportunidade
        opportunity_score = self._calculate_opportunity_score(df, market_regime, signal_strength)
        
        # Interpretação algorítmica
        interpretation = self._generate_interpretation(
            market_regime, signal_strength, trend_direction, 
            volatility_level, volume_profile, market_sentiment
        )
        
        # Recomendações
        recommendations = self._generate_recommendations(
            market_regime, signal_strength, trend_direction, 
            support_resistance, key_levels, risk_level
        )
        
        # Avisos
        warnings = self._generate_warnings(
            market_regime, volatility_level, volume_profile, risk_level
        )
        
        return MarketContext(
            symbol=symbol,
            timestamp=timestamp,
            price=current_price,
            market_regime=market_regime,
            signal_strength=signal_strength,
            trend_direction=trend_direction,
            volatility_level=volatility_level,
            volume_profile=volume_profile,
            support_resistance=support_resistance,
            key_levels=key_levels,
            market_sentiment=market_sentiment,
            risk_level=risk_level,
            opportunity_score=opportunity_score,
            interpretation=interpretation,
            recommendations=recommendations,
            warnings=warnings
        )
    
    def _determine_market_regime(self, df: pd.DataFrame) -> MarketRegime:
        """Determina o regime de mercado baseado em padrões algorítmicos"""
        
        # Análise de tendência
        ema8 = df['EMA8'].iloc[-1]
        ema21 = df['EMA21'].iloc[-1]
        sma200 = df['SMA200'].iloc[-1]
        
        # Análise de volatilidade
        volatility = df['close'].pct_change().std() * 100
        
        # Análise de range
        high_20 = df['high'].rolling(20).max().iloc[-1]
        low_20 = df['low'].rolling(20).min().iloc[-1]
        range_20 = (high_20 - low_20) / df['close'].iloc[-1] * 100
        
        # Classificação do regime
        if ema8 > ema21 > sma200 and volatility < 2:
            return MarketRegime.BULL_TREND
        elif ema8 < ema21 < sma200 and volatility < 2:
            return MarketRegime.BEAR_TREND
        elif volatility > 5:
            return MarketRegime.VOLATILE
        elif range_20 < 3:
            return MarketRegime.CONSOLIDATION
        else:
            return MarketRegime.SIDEWAYS
    
    def _calculate_signal_strength(self, df: pd.DataFrame) -> SignalStrength:
        """Calcula força do sinal baseada em múltiplos indicadores"""
        
        # Indicadores técnicos
        indicators = calculate_all_indicators(df)
        
        score = 0
        
        # RSI
        if 'rsi' in indicators and 'rsi' in indicators['rsi']:
            rsi = indicators['rsi']['rsi']
            if rsi < 30 or rsi > 70:
                score += 2
            elif 40 <= rsi <= 60:
                score += 1
        
        # MACD
        if 'macd' in indicators and 'histogram' in indicators['macd']:
            macd_hist = indicators['macd']['histogram']
            if abs(macd_hist) > 0.001:
                score += 2
            elif abs(macd_hist) > 0.0005:
                score += 1
        
        # Bollinger Bands
        if 'bollinger' in indicators and 'width' in indicators['bollinger']:
            bb_width = indicators['bollinger']['width']
            if bb_width > 5:
                score += 2
            elif bb_width > 3:
                score += 1
        
        # Volume
        volume_ratio = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
        if volume_ratio > 2:
            score += 2
        elif volume_ratio > 1.5:
            score += 1
        
        # Classificação da força
        if score >= 8:
            return SignalStrength.VERY_STRONG
        elif score >= 6:
            return SignalStrength.STRONG
        elif score >= 4:
            return SignalStrength.MODERATE
        elif score >= 2:
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK
    
    def _analyze_trend_direction(self, df: pd.DataFrame) -> str:
        """Analisa direção da tendência"""
        
        ema8 = df['EMA8'].iloc[-1]
        ema21 = df['EMA21'].iloc[-1]
        sma200 = df['SMA200'].iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Análise multi-timeframe
        short_trend = "BULLISH" if ema8 > ema21 else "BEARISH"
        long_trend = "BULLISH" if ema21 > sma200 else "BEARISH"
        
        # Força da tendência
        if short_trend == long_trend:
            if short_trend == "BULLISH":
                return "FORTE ALTA"
            else:
                return "FORTE BAIXA"
        else:
            return "TENDÊNCIA MISTA"
    
    def _analyze_volatility(self, df: pd.DataFrame) -> str:
        """Analisa nível de volatilidade"""
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(14).mean().iloc[-1]
        
        # Volatilidade percentual
        volatility_pct = (atr / df['close'].iloc[-1]) * 100
        
        if volatility_pct < 1:
            return "BAIXA"
        elif volatility_pct < 3:
            return "MÉDIA"
        elif volatility_pct < 5:
            return "ALTA"
        else:
            return "EXTREMA"
    
    def _analyze_volume_profile(self, df: pd.DataFrame) -> str:
        """Analisa perfil de volume"""
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio < 0.5:
            return "BAIXO"
        elif volume_ratio < 1.5:
            return "NORMAL"
        elif volume_ratio < 2.0:
            return "ALTO"
        else:
            return "EXTREMO"
    
    def _identify_support_resistance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Identifica suporte e resistência"""
        
        # Suporte (mínimos locais)
        support = df['low'].rolling(20).min().iloc[-1]
        
        # Resistência (máximos locais)
        resistance = df['high'].rolling(20).max().iloc[-1]
        
        # Níveis psicológicos
        current_price = df['close'].iloc[-1]
        psychological_levels = [
            round(current_price, -1),  # Nível redondo
            round(current_price, -2),  # Nível centena
            round(current_price, -3)   # Nível milhar
        ]
        
        return {
            'support': support,
            'resistance': resistance,
            'psychological_levels': psychological_levels
        }
    
    def _identify_key_levels(self, df: pd.DataFrame) -> List[float]:
        """Identifica níveis-chave importantes"""
        
        current_price = df['close'].iloc[-1]
        key_levels = []
        
        # EMAs como níveis-chave
        key_levels.extend([
            df['EMA8'].iloc[-1],
            df['EMA21'].iloc[-1],
            df['SMA200'].iloc[-1]
        ])
        
        # Bollinger Bands
        try:
            indicators = calculate_all_indicators(df)
            if 'bollinger' in indicators:
                bb = indicators['bollinger']
                key_levels.extend([
                    bb['upper'],
                    bb['middle'],
                    bb['lower']
                ])
        except:
            pass
        
        # Níveis de Fibonacci (simplificado)
        high_20 = df['high'].rolling(20).max().iloc[-1]
        low_20 = df['low'].rolling(20).min().iloc[-1]
        fib_range = high_20 - low_20
        
        key_levels.extend([
            low_20 + fib_range * 0.236,  # 23.6%
            low_20 + fib_range * 0.382,  # 38.2%
            low_20 + fib_range * 0.5,    # 50%
            low_20 + fib_range * 0.618,   # 61.8%
            low_20 + fib_range * 0.786    # 78.6%
        ])
        
        return sorted(set([round(level, 2) for level in key_levels]))
    
    def _analyze_market_sentiment(self, df: pd.DataFrame) -> str:
        """Analisa sentimento do mercado"""
        
        # Análise de momentum
        price_change = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100
        
        # Análise de volume
        volume_ratio = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
        
        # Análise de RSI
        try:
            indicators = calculate_all_indicators(df)
            rsi = indicators.get('rsi', {}).get('rsi', 50)
        except:
            rsi = 50
        
        # Classificação do sentimento
        if price_change > 2 and volume_ratio > 1.5 and rsi < 70:
            return "MUITO OTIMISTA"
        elif price_change > 0 and volume_ratio > 1.2:
            return "OTIMISTA"
        elif price_change < -2 and volume_ratio > 1.5 and rsi > 30:
            return "MUITO PESSIMISTA"
        elif price_change < 0 and volume_ratio > 1.2:
            return "PESSIMISTA"
        else:
            return "NEUTRO"
    
    def _assess_risk_level(self, df: pd.DataFrame, market_regime: MarketRegime, volatility_level: str) -> str:
        """Avalia nível de risco"""
        
        risk_score = 0
        
        # Risco por regime
        if market_regime == MarketRegime.VOLATILE:
            risk_score += 3
        elif market_regime == MarketRegime.CONSOLIDATION:
            risk_score += 1
        
        # Risco por volatilidade
        if volatility_level == "EXTREMA":
            risk_score += 3
        elif volatility_level == "ALTA":
            risk_score += 2
        elif volatility_level == "MÉDIA":
            risk_score += 1
        
        # Risco por volume
        volume_ratio = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
        if volume_ratio < 0.5:  # Baixa liquidez
            risk_score += 2
        
        # Classificação do risco
        if risk_score >= 5:
            return "MUITO ALTO"
        elif risk_score >= 3:
            return "ALTO"
        elif risk_score >= 2:
            return "MÉDIO"
        else:
            return "BAIXO"
    
    def _calculate_opportunity_score(self, df: pd.DataFrame, market_regime: MarketRegime, signal_strength: SignalStrength) -> float:
        """Calcula score de oportunidade (0-100) - Versão OTIMIZADA"""
        
        score = 0
        
        # Score por regime (MUITO mais generoso)
        regime_scores = {
            MarketRegime.BULL_TREND: 45,      # Aumentado de 35
            MarketRegime.BEAR_TREND: 45,      # Aumentado de 35
            MarketRegime.VOLATILE: 50,        # Aumentado de 40
            MarketRegime.CONSOLIDATION: 30,   # Aumentado de 20
            MarketRegime.SIDEWAYS: 35         # Aumentado de 25
        }
        score += regime_scores.get(market_regime, 30)  # Base 30 se não encontrar
        
        # Score por força do sinal (MUITO mais generoso)
        strength_scores = {
            SignalStrength.VERY_STRONG: 40,   # Aumentado de 35
            SignalStrength.STRONG: 35,        # Aumentado de 30
            SignalStrength.MODERATE: 30,      # Aumentado de 25
            SignalStrength.WEAK: 25,          # Aumentado de 15
            SignalStrength.VERY_WEAK: 20      # Aumentado de 10
        }
        score += strength_scores.get(signal_strength, 20)  # Base 20 se não encontrar
        
        # Score por volume (mais generoso)
        try:
            volume_ratio = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
            if volume_ratio > 2:
                score += 15
            elif volume_ratio > 1.5:
                score += 12
            elif volume_ratio > 1:
                score += 10
            elif volume_ratio > 0.5:
                score += 8   # Volume razoável
            else:
                score += 5   # Volume baixo mas presente
        except:
            score += 8  # Score padrão se houver erro
        
        # Score por volatilidade (mais generoso)
        try:
            volatility = df['close'].pct_change().std() * 100
            if 1.5 <= volatility <= 6:  # Faixa ideal
                score += 15
            elif volatility > 6:  # Alta volatilidade
                score += 12
            elif volatility > 0.5:  # Volatilidade baixa mas presente
                score += 10
            else:
                score += 5  # Volatilidade muito baixa
        except:
            score += 8  # Score padrão se houver erro
        
        # Bonus por momentum
        try:
            if 'close' in df.columns and len(df) >= 5:
                recent_change = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1) * 100
                if abs(recent_change) > 2:  # Movimento significativo
                    score += 10
                elif abs(recent_change) > 1:
                    score += 8
                elif abs(recent_change) > 0.5:
                    score += 5
        except:
            pass
        
        # Garantir que score está entre 40 e 100 (mais realista)
        score = max(40, min(score, 100))
        
        return score
    
    def _generate_interpretation(self, market_regime: MarketRegime, signal_strength: SignalStrength, 
                               trend_direction: str, volatility_level: str, volume_profile: str, 
                               market_sentiment: str) -> str:
        """Gera interpretação textual do contexto de mercado"""
        
        interpretations = {
            MarketRegime.BULL_TREND: {
                SignalStrength.VERY_STRONG: "🔥 MERCADO EM FORTE TENDÊNCIA DE ALTA - Oportunidade excepcional para posições longas. Momentum positivo com alta confiança técnica.",
                SignalStrength.STRONG: "📈 TENDÊNCIA DE ALTA CONFIRMADA - Boa oportunidade para entrada em posições longas com gestão de risco adequada.",
                SignalStrength.MODERATE: "🟢 MERCADO BULLISH COM SINAIS MISTOS - Tendência de alta presente, mas aguardar confirmação adicional.",
                SignalStrength.WEAK: "⚠️ TENDÊNCIA DE ALTA FRACA - Mercado bullish mas com sinais técnicos fracos. Cautela recomendada.",
                SignalStrength.VERY_WEAK: "🔍 TENDÊNCIA DE ALTA QUESTIONÁVEL - Sinais muito fracos, possível reversão. Evitar posições."
            },
            MarketRegime.BEAR_TREND: {
                SignalStrength.VERY_STRONG: "❄️ MERCADO EM FORTE TENDÊNCIA DE BAIXA - Oportunidade excepcional para posições short. Momentum negativo com alta confiança técnica.",
                SignalStrength.STRONG: "📉 TENDÊNCIA DE BAIXA CONFIRMADA - Boa oportunidade para entrada em posições short com gestão de risco adequada.",
                SignalStrength.MODERATE: "🔴 MERCADO BEARISH COM SINAIS MISTOS - Tendência de baixa presente, mas aguardar confirmação adicional.",
                SignalStrength.WEAK: "⚠️ TENDÊNCIA DE BAIXA FRACA - Mercado bearish mas com sinais técnicos fracos. Cautela recomendada.",
                SignalStrength.VERY_WEAK: "🔍 TENDÊNCIA DE BAIXA QUESTIONÁVEL - Sinais muito fracos, possível reversão. Evitar posições."
            },
            MarketRegime.VOLATILE: {
                SignalStrength.VERY_STRONG: "⚡ MERCADO ALTAMENTE VOLÁTIL COM SINAIS FORTES - Oportunidade de trading de curto prazo com alto potencial, mas alto risco.",
                SignalStrength.STRONG: "🌪️ ALTA VOLATILIDADE COM SINAIS BONS - Boas oportunidades de scalping, mas gestão de risco rigorosa necessária.",
                SignalStrength.MODERATE: "🌀 MERCADO VOLÁTIL COM SINAIS MISTOS - Oportunidades de trading presentes, mas ambiente instável.",
                SignalStrength.WEAK: "⚠️ ALTA VOLATILIDADE COM SINAIS FRACOS - Ambiente perigoso, evitar trading até clareza maior.",
                SignalStrength.VERY_WEAK: "🚨 MERCADO EXTREMAMENTE VOLÁTIL E IMPREVISÍVEL - Evitar trading, risco muito alto."
            },
            MarketRegime.CONSOLIDATION: {
                SignalStrength.VERY_STRONG: "🎯 CONSOLIDAÇÃO COM SINAIS FORTES - Possível breakout iminente, preparar para movimento direcional.",
                SignalStrength.STRONG: "📊 MERCADO CONSOLIDANDO COM SINAIS BONS - Aguardar confirmação de direção para entrada.",
                SignalStrength.MODERATE: "⏳ CONSOLIDAÇÃO COM SINAIS MISTOS - Mercado lateral, aguardar definição de direção.",
                SignalStrength.WEAK: "😴 CONSOLIDAÇÃO COM SINAIS FRACOS - Mercado sem direção clara, evitar trading.",
                SignalStrength.VERY_WEAK: "💤 MERCADO ADORMECIDO - Baixa atividade, aguardar catalisador para movimento."
            },
            MarketRegime.SIDEWAYS: {
                SignalStrength.VERY_STRONG: "🔄 MERCADO LATERAL COM SINAIS FORTES - Oportunidades de range trading com alta probabilidade.",
                SignalStrength.STRONG: "↔️ TENDÊNCIA LATERAL COM SINAIS BONS - Boas oportunidades de trading de range.",
                SignalStrength.MODERATE: "📐 MERCADO LATERAL COM SINAIS MISTOS - Trading de range possível, mas com cautela.",
                SignalStrength.WEAK: "⚠️ MERCADO LATERAL COM SINAIS FRACOS - Range trading arriscado, aguardar clareza.",
                SignalStrength.VERY_WEAK: "❓ MERCADO SEM DIREÇÃO CLARA - Evitar trading até definição de tendência."
            }
        }
        
        base_interpretation = interpretations.get(market_regime, {}).get(signal_strength, "Contexto de mercado não identificado.")
        
        # Adicionar contexto de volatilidade e volume
        context_additions = []
        
        if volatility_level == "EXTREMA":
            context_additions.append("⚠️ VOLATILIDADE EXTREMA - Gestão de risco rigorosa necessária.")
        elif volatility_level == "ALTA":
            context_additions.append("📊 Alta volatilidade presente - Oportunidades de trading de curto prazo.")
        
        if volume_profile == "EXTREMO":
            context_additions.append("📈 VOLUME EXTREMO - Alta participação do mercado, sinais mais confiáveis.")
        elif volume_profile == "BAIXO":
            context_additions.append("📉 Volume baixo - Sinais menos confiáveis, cautela recomendada.")
        
        if market_sentiment == "MUITO OTIMISTA":
            context_additions.append("🚀 Sentimento muito otimista - Possível correção próxima.")
        elif market_sentiment == "MUITO PESSIMISTA":
            context_additions.append("😱 Sentimento muito pessimista - Possível reversão próxima.")
        
        # Combinar interpretação base com contexto
        full_interpretation = base_interpretation
        if context_additions:
            full_interpretation += "\n\n" + "\n".join(context_additions)
        
        return full_interpretation
    
    def _generate_recommendations(self, market_regime: MarketRegime, signal_strength: SignalStrength,
                                trend_direction: str, support_resistance: Dict[str, float],
                                key_levels: List[float], risk_level: str) -> List[str]:
        """Gera recomendações baseadas no contexto"""
        
        recommendations = []
        
        # Recomendações por regime
        if market_regime == MarketRegime.BULL_TREND:
            if signal_strength in [SignalStrength.VERY_STRONG, SignalStrength.STRONG]:
                recommendations.append("🟢 CONSIDERAR ENTRADA LONG - Tendência de alta confirmada com sinais fortes")
                recommendations.append(f"🎯 STOP LOSS: {support_resistance['support']:.2f} - Nível de suporte próximo")
            else:
                recommendations.append("⏳ AGUARDAR CONFIRMAÇÃO - Sinais ainda fracos para entrada")
        
        elif market_regime == MarketRegime.BEAR_TREND:
            if signal_strength in [SignalStrength.VERY_STRONG, SignalStrength.STRONG]:
                recommendations.append("🔴 CONSIDERAR ENTRADA SHORT - Tendência de baixa confirmada com sinais fortes")
                recommendations.append(f"🎯 STOP LOSS: {support_resistance['resistance']:.2f} - Nível de resistência próximo")
            else:
                recommendations.append("⏳ AGUARDAR CONFIRMAÇÃO - Sinais ainda fracos para entrada")
        
        elif market_regime == MarketRegime.VOLATILE:
            recommendations.append("⚡ TRADING DE CURTO PRAZO - Ambiente volátil, posições rápidas recomendadas")
            recommendations.append("🛡️ GESTÃO DE RISCO RIGOROSA - Stop loss apertado obrigatório")
        
        elif market_regime == MarketRegime.CONSOLIDATION:
            recommendations.append("📊 RANGE TRADING - Mercado consolidando, trading entre suporte e resistência")
            recommendations.append("🎯 AGUARDAR BREAKOUT - Preparar para movimento direcional")
        
        # Recomendações por nível de risco
        if risk_level == "MUITO ALTO":
            recommendations.append("🚨 RISCO MUITO ALTO - Reduzir tamanho da posição ou evitar trading")
        elif risk_level == "ALTO":
            recommendations.append("⚠️ RISCO ALTO - Gestão de risco rigorosa necessária")
        
        # Recomendações por níveis-chave
        if key_levels:
            recommendations.append(f"📊 NÍVEIS-CHAVE: {', '.join([f'{level:.2f}' for level in key_levels[:3]])}")
        
        return recommendations
    
    def _generate_warnings(self, market_regime: MarketRegime, volatility_level: str,
                         volume_profile: str, risk_level: str) -> List[str]:
        """Gera avisos baseados no contexto"""
        
        warnings = []
        
        # Avisos por volatilidade
        if volatility_level == "EXTREMA":
            warnings.append("🚨 VOLATILIDADE EXTREMA - Mercado muito instável, alto risco de perdas")
        elif volatility_level == "ALTA":
            warnings.append("⚠️ ALTA VOLATILIDADE - Gestão de risco rigorosa necessária")
        
        # Avisos por volume
        if volume_profile == "BAIXO":
            warnings.append("📉 VOLUME BAIXO - Sinais menos confiáveis, possível baixa liquidez")
        elif volume_profile == "EXTREMO":
            warnings.append("📈 VOLUME EXTREMO - Possível manipulação ou evento importante")
        
        # Avisos por regime
        if market_regime == MarketRegime.VOLATILE:
            warnings.append("🌪️ MERCADO VOLÁTIL - Ambiente instável, posições de curto prazo apenas")
        
        # Avisos por risco
        if risk_level == "MUITO ALTO":
            warnings.append("🚨 RISCO MUITO ALTO - Considerar evitar trading neste momento")
        elif risk_level == "ALTO":
            warnings.append("⚠️ RISCO ALTO - Reduzir exposição e aumentar cautela")
        
        return warnings

class MarketContextReporter:
    """Gerador de relatórios de contexto de mercado"""
    
    def __init__(self):
        self.analyzer = MarketContextAnalyzer()
    
    def generate_market_report(self, symbol: str, df: pd.DataFrame) -> str:
        """Gera relatório completo de contexto de mercado"""
        
        context = self.analyzer.analyze_market_context(symbol, df)
        
        # Cabeçalho
        report = f"""
🧠 ANÁLISE DE CONTEXTO DE MERCADO - {symbol}
{'='*60}
🕰️ Timestamp: {context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
💰 Preço Atual: ${context.price:.2f}
📊 Score de Oportunidade: {context.opportunity_score:.1f}/100

"""
        
        # Interpretação principal
        report += f"🎯 INTERPRETAÇÃO PRINCIPAL:\n{context.interpretation}\n\n"
        
        # Análise técnica
        report += f"""📈 ANÁLISE TÉCNICA:
• Regime de Mercado: {context.market_regime.value.upper()}
• Força do Sinal: {context.signal_strength.name}
• Direção da Tendência: {context.trend_direction}
• Nível de Volatilidade: {context.volatility_level}
• Perfil de Volume: {context.volume_profile}
• Sentimento do Mercado: {context.market_sentiment}
• Nível de Risco: {context.risk_level}

"""
        
        # Suporte e resistência
        report += f"""🎯 SUPORTE E RESISTÊNCIA:
• Suporte: ${context.support_resistance['support']:.2f}
• Resistência: ${context.support_resistance['resistance']:.2f}
• Níveis Psicológicos: {', '.join([f'${level:.2f}' for level in context.support_resistance['psychological_levels']])}

"""
        
        # Níveis-chave
        if context.key_levels:
            report += f"""📊 NÍVEIS-CHAVE:
{', '.join([f'${level:.2f}' for level in context.key_levels[:5]])}

"""
        
        # Recomendações
        if context.recommendations:
            report += f"""💡 RECOMENDAÇÕES:
"""
            for i, rec in enumerate(context.recommendations, 1):
                report += f"{i}. {rec}\n"
            report += "\n"
        
        # Avisos
        if context.warnings:
            report += f"""⚠️ AVISOS IMPORTANTES:
"""
            for i, warning in enumerate(context.warnings, 1):
                report += f"{i}. {warning}\n"
            report += "\n"
        
        # Rodapé
        report += f"""📋 RESUMO EXECUTIVO:
O mercado {symbol} está em regime {context.market_regime.value} com força de sinal {context.signal_strength.name.lower()}.
A volatilidade está {context.volatility_level.lower()} e o volume está {context.volume_profile.lower()}.
O nível de risco é {context.risk_level.lower()} com score de oportunidade de {context.opportunity_score:.1f}/100.

{'='*60}
🤖 Análise gerada automaticamente pelo SNE Radar
"""
        
        return report

# Função principal para integração
def analisar_contexto_mercado(symbol: str, df: pd.DataFrame) -> str:
    """Função principal para análise de contexto de mercado"""
    reporter = MarketContextReporter()
    return reporter.generate_market_report(symbol, df)

# Função para análise rápida
def analise_rapida_contexto(symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
    """Análise rápida de contexto retornando dicionário"""
    analyzer = MarketContextAnalyzer()
    context = analyzer.analyze_market_context(symbol, df)
    
    return {
        'symbol': context.symbol,
        'price': context.price,
        'market_regime': context.market_regime.value,
        'signal_strength': context.signal_strength.name,
        'trend_direction': context.trend_direction,
        'volatility_level': context.volatility_level,
        'volume_profile': context.volume_profile,
        'market_sentiment': context.market_sentiment,
        'risk_level': context.risk_level,
        'opportunity_score': context.opportunity_score,
        'interpretation': context.interpretation,
        'recommendations': context.recommendations,
        'warnings': context.warnings
    }
