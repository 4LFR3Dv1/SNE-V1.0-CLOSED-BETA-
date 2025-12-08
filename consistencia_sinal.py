#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMADA DE ANÁLISE DE CONSISTÊNCIA DE SINAL
Valida sinais com múltiplos critérios para reduzir falsos positivos
"""

import requests
import pandas as pd
from indicadores import calcular_indicadores_simples


class ConsistenciaSinal:
    """
    Valida sinais com confirmações cruzadas
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
    
    def buscar_dados_tf(self, symbol: str, interval: str, limit: int = 50):
        """Busca dados de um timeframe"""
        try:
            url = f"{self.base_url}/klines"
            params = {"symbol": symbol, "interval": interval, "limit": limit}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                closes = [float(candle[4]) for candle in data]
                volumes = [float(candle[5]) for candle in data]
                return closes, volumes
            return None, None
        except:
            return None, None
    
    def confirmar_em_outro_tf(self, symbol: str, acao: str, tf_principal: str = '15m'):
        """
        Confirma sinal em outro timeframe
        
        Args:
            symbol: par
            acao: COMPRAR ou VENDER
            tf_principal: timeframe principal
        
        Returns:
            tuple (confirmado: bool, motivo: str)
        """
        # Definir timeframe de confirmação
        tfs_confirmacao = {
            '1m': '5m',
            '5m': '15m',
            '15m': '1h',
            '1h': '4h'
        }
        
        tf_conf = tfs_confirmacao.get(tf_principal, '1h')
        
        # Buscar dados
        closes, _ = self.buscar_dados_tf(symbol, tf_conf, 50)
        
        if not closes:
            return False, f"Falha ao buscar {tf_conf}"
        
        # Calcular indicadores
        ema8, ema21, rsi, bb_upper, bb_lower = calcular_indicadores_simples(closes)
        
        # Verificar alinhamento
        if acao == 'COMPRAR':
            if ema8 > ema21:
                return True, f"{tf_conf}: EMA8 > EMA21 ✓"
            else:
                return False, f"{tf_conf}: EMAs não alinhadas"
        
        elif acao == 'VENDER':
            if ema8 < ema21:
                return True, f"{tf_conf}: EMA8 < EMA21 ✓"
            else:
                return False, f"{tf_conf}: EMAs não alinhadas"
        
        return False, "Sem confirmação"
    
    def verificar_direcao_volume(self, symbol: str, acao: str, tf: str = '15m'):
        """
        Verifica se volume confirma a direção
        
        Returns:
            tuple (confirmado: bool, motivo: str)
        """
        closes, volumes = self.buscar_dados_tf(symbol, tf, 20)
        
        if not closes or not volumes:
            return False, "Falha ao buscar volume"
        
        # Últimos 5 candles
        closes_recentes = closes[-5:]
        volumes_recentes = volumes[-5:]
        
        # Preço subindo ou caindo?
        preco_subindo = closes_recentes[-1] > closes_recentes[0]
        
        # Volume aumentando?
        volume_medio_antes = sum(volumes[-10:-5]) / 5
        volume_medio_recente = sum(volumes_recentes) / 5
        volume_aumentando = volume_medio_recente > volume_medio_antes * 1.1
        
        # Verificar alinhamento
        if acao == 'COMPRAR':
            if preco_subindo and volume_aumentando:
                return True, f"Preço↑ + Volume↑ ({volume_medio_recente/volume_medio_antes:.1f}x)"
            elif preco_subindo and not volume_aumentando:
                return False, "Preço↑ mas Volume↓ (divergência)"
            else:
                return False, "Preço não confirma COMPRA"
        
        elif acao == 'VENDER':
            if not preco_subindo and volume_aumentando:
                return True, f"Preço↓ + Volume↑ ({volume_medio_recente/volume_medio_antes:.1f}x)"
            elif not preco_subindo and not volume_aumentando:
                return False, "Preço↓ mas Volume↓ (sem convicção)"
            else:
                return False, "Preço não confirma VENDA"
        
        return False, "Sem confirmação"
    
    def detectar_divergencia_rsi(self, symbol: str, tf: str = '15m'):
        """
        Detecta divergência RSI (sinal de reversão)
        
        Returns:
            tuple (divergencia: bool, tipo: str, motivo: str)
        """
        closes, _ = self.buscar_dados_tf(symbol, tf, 50)
        
        if not closes:
            return False, None, "Falha ao buscar dados"
        
        # Calcular RSI
        closes_series = pd.Series(closes)
        delta = closes_series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Últimos 20 períodos
        rsi_recente = rsi.tail(20).values
        preco_recente = closes[-20:]
        
        # Buscar topos e fundos
        # Simplificado: comparar últimos 2 picos
        if len(preco_recente) < 10:
            return False, None, "Dados insuficientes"
        
        # Divergência de alta: preço faz fundo mais baixo, RSI fundo mais alto
        if preco_recente[-1] < preco_recente[-10] and rsi_recente[-1] > rsi_recente[-10]:
            return True, "ALTA", "RSI divergente positivo (reversão alta)"
        
        # Divergência de baixa: preço faz topo mais alto, RSI topo mais baixo
        if preco_recente[-1] > preco_recente[-10] and rsi_recente[-1] < rsi_recente[-10]:
            return True, "BAIXA", "RSI divergente negativo (reversão baixa)"
        
        return False, None, "Sem divergência detectada"
    
    def validar_sinal_completo(self, symbol: str, acao: str, tf_principal: str = '15m'):
        """
        Validação completa com múltiplos critérios
        
        Returns:
            dict com resultado da validação
        """
        validacoes = []
        score = 0
        
        # 1. Confirmação em outro TF
        conf_tf, motivo_tf = self.confirmar_em_outro_tf(symbol, acao, tf_principal)
        validacoes.append({
            'criterio': 'Multi-Timeframe',
            'resultado': conf_tf,
            'motivo': motivo_tf
        })
        if conf_tf:
            score += 40
        
        # 2. Direção do volume
        conf_vol, motivo_vol = self.verificar_direcao_volume(symbol, acao, tf_principal)
        validacoes.append({
            'criterio': 'Volume',
            'resultado': conf_vol,
            'motivo': motivo_vol
        })
        if conf_vol:
            score += 30
        
        # 3. Divergência RSI
        div_rsi, tipo_div, motivo_div = self.detectar_divergencia_rsi(symbol, tf_principal)
        validacoes.append({
            'criterio': 'Divergência RSI',
            'resultado': not div_rsi,  # Divergência é CONTRA o sinal
            'motivo': motivo_div if div_rsi else "Sem divergência ✓"
        })
        if not div_rsi:
            score += 30
        elif div_rsi and tipo_div != acao:
            score -= 50  # Penalizar se divergência contra
        
        # Resultado final
        valido = score >= 60
        
        return {
            'valido': valido,
            'score': score,
            'validacoes': validacoes,
            'motivo_final': f"Score de consistência: {score}/100"
        }


if __name__ == "__main__":
    consistencia = ConsistenciaSinal()
    
    print("=" * 60)
    print("ANÁLISE DE CONSISTÊNCIA DE SINAL")
    print("=" * 60)
    
    resultado = consistencia.validar_sinal_completo('BTCUSDT', 'COMPRAR', '15m')
    
    print(f"\n🎯 Sinal: COMPRAR BTCUSDT (15m)")
    print(f"{'✅ VÁLIDO' if resultado['valido'] else '❌ INVÁLIDO'}")
    print(f"📊 Score: {resultado['score']}/100")
    
    print(f"\n📋 VALIDAÇÕES:")
    for v in resultado['validacoes']:
        emoji = "✅" if v['resultado'] else "❌"
        print(f"   {emoji} {v['criterio']}: {v['motivo']}")
    
    print(f"\n💡 {resultado['motivo_final']}")





