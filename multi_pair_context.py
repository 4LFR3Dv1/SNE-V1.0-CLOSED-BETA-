#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Análise de Contexto Multi-Pares
Análise comparativa e ranking de oportunidades
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
from contexto_mercado import MarketContextAnalyzer, analise_rapida_contexto
import requests
import pytz

class MultiPairContextAnalyzer:
    """Analisador de contexto para múltiplos pares"""
    
    def __init__(self):
        self.analyzer = MarketContextAnalyzer()
        self.br_tz = pytz.timezone("America/Sao_Paulo")
        
        # Pares para análise
        self.pairs = [
            "BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", 
            "DOTUSDT", "AVAXUSDT", "MATICUSDT", "LINKUSDT",
            "UNIUSDT", "ATOMUSDT", "NEARUSDT", "FTMUSDT"
        ]
        
        # Configurações
        self.interval = "1m"
        self.limit = 100
        self.update_interval = 5  # segundos
        
    def buscar_dados_binance(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """Busca dados da Binance"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": symbol, "interval": interval, "limit": limit}
            data = requests.get(url, params=params, timeout=10).json()
            
            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "qav", "trades", "tbb", "tbq", "ignore"
            ])
            
            df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(self.br_tz)
            df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
                "open": float, "high": float, "low": float, "close": float,
                "volume": float, "trades": int
            })
            df.set_index("time", inplace=True)
            
            # Calcular indicadores básicos
            df["EMA8"] = df["close"].ewm(span=8).mean()
            df["EMA21"] = df["close"].ewm(span=21).mean()
            df["SMA200"] = df["close"].rolling(window=20).mean()  # Usando 20 para dados limitados
            df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
            df["timestamp"] = pd.to_datetime(df.index).astype(int) / 10**9
            
            return df
            
        except Exception as e:
            print(f"[ERRO] Falha ao buscar dados para {symbol}: {e}")
            return pd.DataFrame()
    
    def analisar_todos_pares(self) -> Dict[str, Dict[str, Any]]:
        """Analisa todos os pares e retorna ranking"""
        
        resultados = {}
        
        print(f"🔍 Analisando {len(self.pairs)} pares...")
        
        for symbol in self.pairs:
            try:
                print(f"📊 Processando {symbol}...")
                df = self.buscar_dados_binance(symbol, self.interval, self.limit)
                
                if df.empty:
                    print(f"❌ Dados vazios para {symbol}")
                    continue
                
                # Análise de contexto
                contexto = analise_rapida_contexto(symbol, df)
                
                # Adicionar dados técnicos básicos
                contexto.update({
                    'price': df['close'].iloc[-1],
                    'volume_24h': df['volume'].sum(),
                    'volatility': df['close'].pct_change().std() * 100,
                    'price_change_1h': ((df['close'].iloc[-1] - df['close'].iloc[-60]) / df['close'].iloc[-60] * 100) if len(df) >= 60 else 0,
                    'ema8': df['EMA8'].iloc[-1],
                    'ema21': df['EMA21'].iloc[-1],
                    'sma200': df['SMA200'].iloc[-1]
                })
                
                resultados[symbol] = contexto
                print(f"✅ {symbol} - Score: {contexto['opportunity_score']:.1f}")
                
            except Exception as e:
                print(f"❌ Erro ao analisar {symbol}: {e}")
                continue
        
        return resultados
    
    def gerar_ranking_oportunidades(self, resultados: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gera ranking de oportunidades"""
        
        # Filtrar apenas pares com dados válidos
        pares_validos = {k: v for k, v in resultados.items() if 'opportunity_score' in v}
        
        # Ordenar por score de oportunidade
        ranking = sorted(
            pares_validos.items(), 
            key=lambda x: x[1]['opportunity_score'], 
            reverse=True
        )
        
        return [
            {
                'rank': i + 1,
                'symbol': symbol,
                'score': data['opportunity_score'],
                'regime': data['market_regime'],
                'signal_strength': data['signal_strength'],
                'trend': data['trend_direction'],
                'volatility': data['volatility_level'],
                'risk': data['risk_level'],
                'price': data['price'],
                'price_change': data.get('price_change_1h', 0),
                'volume_ratio': data.get('volume_24h', 0) / 1000000,  # Normalizar volume
                'interpretation': data['interpretation'],
                'recommendations': data['recommendations'],
                'warnings': data['warnings']
            }
            for i, (symbol, data) in enumerate(ranking)
        ]
    
    def gerar_relatorio_comparativo(self, ranking: List[Dict[str, Any]]) -> str:
        """Gera relatório comparativo de todos os pares"""
        
        timestamp = datetime.now(self.br_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        relatorio = f"""
🧠 RELATÓRIO COMPARATIVO DE MERCADO
{'='*60}
🕰️ Timestamp: {timestamp}
📊 Total de Pares Analisados: {len(ranking)}

"""
        
        # Top 5 oportunidades
        relatorio += "🏆 TOP 5 OPORTUNIDADES:\n"
        for i, par in enumerate(ranking[:5], 1):
            relatorio += f"""
{i}. {par['symbol']} - Score: {par['score']:.1f}/100
   💰 Preço: ${par['price']:.2f} ({par['price_change']:+.2f}%)
   📊 Regime: {par['regime']} | Força: {par['signal_strength']}
   📈 Tendência: {par['trend']} | Volatilidade: {par['volatility']}
   ⚠️ Risco: {par['risk']}
   🎯 Interpretação: {par['interpretation'][:100]}...
"""
        
        # Análise de mercado geral
        if ranking:
            scores = [par['score'] for par in ranking]
            avg_score = np.mean(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            relatorio += f"""
📊 ANÁLISE GERAL DO MERCADO:
• Score Médio: {avg_score:.1f}/100
• Melhor Oportunidade: {max_score:.1f}/100
• Pior Oportunidade: {min_score:.1f}/100
• Distribuição: {len([s for s in scores if s >= 70])} pares com score alto (≥70)
"""
        
        # Regimes de mercado
        regimes = {}
        for par in ranking:
            regime = par['regime']
            regimes[regime] = regimes.get(regime, 0) + 1
        
        relatorio += f"\n📈 DISTRIBUIÇÃO POR REGIME:\n"
        for regime, count in regimes.items():
            relatorio += f"• {regime}: {count} pares\n"
        
        # Níveis de risco
        riscos = {}
        for par in ranking:
            risco = par['risk']
            riscos[risco] = riscos.get(risco, 0) + 1
        
        relatorio += f"\n⚠️ DISTRIBUIÇÃO POR RISCO:\n"
        for risco, count in riscos.items():
            relatorio += f"• {risco}: {count} pares\n"
        
        # Recomendações gerais
        relatorio += f"\n💡 RECOMENDAÇÕES GERAIS:\n"
        
        if ranking and ranking[0]['score'] >= 80:
            relatorio += f"🔥 OPORTUNIDADE EXCEPCIONAL: {ranking[0]['symbol']} com score {ranking[0]['score']:.1f}\n"
        elif ranking and ranking[0]['score'] >= 70:
            relatorio += f"📈 BOA OPORTUNIDADE: {ranking[0]['symbol']} com score {ranking[0]['score']:.1f}\n"
        elif ranking and ranking[0]['score'] >= 50:
            relatorio += f"⚠️ OPORTUNIDADE MODERADA: {ranking[0]['symbol']} com score {ranking[0]['score']:.1f}\n"
        else:
            relatorio += f"😴 MERCADO ADORMECIDO: Nenhuma oportunidade significativa detectada\n"
        
        # Avisos importantes
        high_risk_pairs = [par for par in ranking if par['risk'] in ['ALTO', 'MUITO ALTO']]
        if high_risk_pairs:
            relatorio += f"\n🚨 AVISOS IMPORTANTES:\n"
            for par in high_risk_pairs[:3]:  # Top 3 mais arriscados
                relatorio += f"• {par['symbol']}: Risco {par['risk']} - {par['warnings'][0] if par['warnings'] else 'Cautela recomendada'}\n"
        
        relatorio += f"\n{'='*60}\n🤖 Análise gerada automaticamente pelo SNE Radar Multi-Pair"
        
        return relatorio
    
    def executar_analise_completa(self) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]], str]:
        """Executa análise completa de todos os pares"""
        
        print("🚀 Iniciando análise multi-pair...")
        
        # Analisar todos os pares
        resultados = self.analisar_todos_pares()
        
        # Gerar ranking
        ranking = self.gerar_ranking_oportunidades(resultados)
        
        # Gerar relatório
        relatorio = self.gerar_relatorio_comparativo(ranking)
        
        return resultados, ranking, relatorio

# Função principal para integração
def analisar_mercado_completo() -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]], str]:
    """Função principal para análise completa do mercado"""
    analyzer = MultiPairContextAnalyzer()
    return analyzer.executar_analise_completa()

# Função para análise rápida de top pares
def analisar_top_pares(num_pares: int = 5) -> List[Dict[str, Any]]:
    """Analisa apenas os top N pares por volume"""
    analyzer = MultiPairContextAnalyzer()
    resultados, ranking, _ = analyzer.executar_analise_completa()
    return ranking[:num_pares]




