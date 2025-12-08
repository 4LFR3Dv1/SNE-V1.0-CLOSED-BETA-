#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE CONTEXTO DINÂMICO
Ajusta pesos dos indicadores conforme regime de mercado
O mesmo sinal tem valores diferentes em contextos diferentes
"""

import numpy as np
from enum import Enum


class RegimeMercado(Enum):
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    CONSOLIDATION = "consolidation"
    VOLATILE = "volatile"
    SIDEWAYS = "sideways"


class ContextoAdaptativo:
    """
    Núcleo Inteligente: Adapta pesos dos indicadores ao contexto
    """
    
    def __init__(self):
        # Pesos base (neutros)
        self.pesos_base = {
            'EMA': 0.25,
            'RSI': 0.25,
            'Volume': 0.25,
            'BB': 0.25
        }
    
    def ajustar_pesos_por_contexto(self, regime: str, volatilidade: float, volume_ratio: float):
        """
        Ajusta pesos dinamicamente com base no contexto
        
        Args:
            regime: bull_trend, bear_trend, consolidation, etc.
            volatilidade: ATR ou % de variação
            volume_ratio: Volume atual / Volume médio
        
        Returns:
            dict com pesos ajustados
        """
        pesos = self.pesos_base.copy()
        
        # ========================================
        # AJUSTE POR REGIME DE MERCADO
        # ========================================
        
        if regime == 'BULL_TREND':
            # Em tendência de alta:
            # - EMA é mais importante (seguir tendência)
            # - RSI menos (pode ficar sobrecomprado muito tempo)
            pesos['EMA'] = 0.40
            pesos['RSI'] = 0.15
            pesos['Volume'] = 0.25
            pesos['BB'] = 0.20
            
        elif regime == 'BEAR_TREND':
            # Em tendência de baixa:
            # - EMA importante (seguir tendência)
            # - Volume crítico (confirmar movimento)
            pesos['EMA'] = 0.40
            pesos['RSI'] = 0.15
            pesos['Volume'] = 0.30
            pesos['BB'] = 0.15
            
        elif regime == 'CONSOLIDATION':
            # Em consolidação:
            # - Bollinger Bands fundamental (range trading)
            # - RSI importante (sobrecompra/sobrevenda)
            # - EMA menos relevante (lateral)
            pesos['EMA'] = 0.15
            pesos['RSI'] = 0.35
            pesos['Volume'] = 0.10
            pesos['BB'] = 0.40
            
        elif regime == 'VOLATILE':
            # Em volatilidade alta:
            # - Volume crítico (validar movimento)
            # - Bollinger importante (extremos)
            # - RSI relevante (reversal)
            pesos['EMA'] = 0.20
            pesos['RSI'] = 0.25
            pesos['Volume'] = 0.35
            pesos['BB'] = 0.20
            
        elif regime == 'SIDEWAYS':
            # Mercado lateral:
            # - RSI e BB dominam (range)
            # - EMA e Volume secundários
            pesos['EMA'] = 0.10
            pesos['RSI'] = 0.40
            pesos['Volume'] = 0.10
            pesos['BB'] = 0.40
        
        # ========================================
        # AJUSTE POR VOLATILIDADE
        # ========================================
        
        if volatilidade > 3.0:
            # Volatilidade extrema: volume é crítico
            pesos['Volume'] += 0.15
            # Redistribuir dos outros
            pesos['EMA'] -= 0.05
            pesos['RSI'] -= 0.05
            pesos['BB'] -= 0.05
            
        elif volatilidade < 1.0:
            # Volatilidade muito baixa: confiar menos em tudo
            # Aumentar peso do Bollinger (range)
            pesos['BB'] += 0.10
            pesos['Volume'] -= 0.10
        
        # ========================================
        # AJUSTE POR VOLUME
        # ========================================
        
        if volume_ratio > 2.0:
            # Volume explosivo: aumentar peso do volume
            pesos['Volume'] += 0.20
            # Redistribuir
            pesos['EMA'] -= 0.07
            pesos['RSI'] -= 0.07
            pesos['BB'] -= 0.06
            
        elif volume_ratio < 0.5:
            # Volume muito baixo: reduzir confiança geral
            # Aumentar peso do RSI (mais confiável em baixo volume)
            pesos['RSI'] += 0.15
            pesos['Volume'] -= 0.15
        
        # Normalizar para somar 1.0
        total = sum(pesos.values())
        pesos = {k: v/total for k, v in pesos.items()}
        
        return pesos
    
    def calcular_forca_sinal_adaptativa(self, indicadores: dict, regime: str, 
                                        volatilidade: float, volume_ratio: float):
        """
        Calcula força do sinal com pesos adaptativos
        
        Args:
            indicadores: {'EMA': bool, 'RSI': bool, 'Volume': bool, 'BB': bool}
            regime: regime de mercado
            volatilidade: nível de volatilidade
            volume_ratio: razão de volume
        
        Returns:
            tuple (força 0-100, pesos usados, explicação)
        """
        # Obter pesos ajustados
        pesos = self.ajustar_pesos_por_contexto(regime, volatilidade, volume_ratio)
        
        # Calcular força ponderada
        forca = 0
        detalhes = []
        
        for indicador, ativo in indicadores.items():
            if indicador in pesos:
                contribuicao = pesos[indicador] * 100 if ativo else 0
                forca += contribuicao
                
                if ativo:
                    detalhes.append(f"{indicador}: {pesos[indicador]*100:.0f}%")
        
        # Gerar explicação
        regime_nome = regime.replace('_', ' ').title()
        explicacao = f"Regime {regime_nome} | Vol: {volatilidade:.1f} | Vol Ratio: {volume_ratio:.1f}x"
        
        return round(forca, 1), pesos, explicacao, detalhes
    
    def recomendar_acao_por_contexto(self, sinal_basico: str, regime: str, 
                                     forca_adaptativa: float):
        """
        Recomenda ação final baseada em contexto
        
        Args:
            sinal_basico: 'COMPRAR', 'VENDER' ou 'AGUARDAR'
            regime: regime de mercado
            forca_adaptativa: força calculada com pesos adaptativos
        
        Returns:
            tuple (acao_final, confianca, motivo)
        """
        # Thresholds por regime
        thresholds = {
            'BULL_TREND': {'min_compra': 50, 'min_venda': 70},
            'BEAR_TREND': {'min_compra': 70, 'min_venda': 50},
            'CONSOLIDATION': {'min_compra': 60, 'min_venda': 60},
            'VOLATILE': {'min_compra': 65, 'min_venda': 65},
            'SIDEWAYS': {'min_compra': 55, 'min_venda': 55}
        }
        
        threshold = thresholds.get(regime, {'min_compra': 60, 'min_venda': 60})
        
        if sinal_basico == 'COMPRAR':
            if forca_adaptativa >= threshold['min_compra']:
                confianca = min(95, forca_adaptativa + 10)
                motivo = f"Força {forca_adaptativa:.0f}% em {regime} (threshold {threshold['min_compra']})"
                return 'COMPRAR', confianca, motivo
            else:
                return 'AGUARDAR', forca_adaptativa, f"Força insuficiente ({forca_adaptativa:.0f}% < {threshold['min_compra']})"
        
        elif sinal_basico == 'VENDER':
            if forca_adaptativa >= threshold['min_venda']:
                confianca = min(95, forca_adaptativa + 10)
                motivo = f"Força {forca_adaptativa:.0f}% em {regime} (threshold {threshold['min_venda']})"
                return 'VENDER', confianca, motivo
            else:
                return 'AGUARDAR', forca_adaptativa, f"Força insuficiente ({forca_adaptativa:.0f}% < {threshold['min_venda']})"
        
        else:
            return 'AGUARDAR', forca_adaptativa, "Sem sinal claro"


# ========================================
# EXEMPLO DE USO
# ========================================

if __name__ == "__main__":
    contexto = ContextoAdaptativo()
    
    # Cenário 1: Bull Trend com volume alto
    print("=" * 60)
    print("CENÁRIO 1: BULL TREND + VOLUME ALTO")
    print("=" * 60)
    
    indicadores = {
        'EMA': True,   # EMA8 > EMA21
        'RSI': False,  # RSI 75 (sobrecomprado)
        'Volume': True,  # Volume 2.5x
        'BB': False   # Preço próximo BB superior
    }
    
    forca, pesos, explicacao, detalhes = contexto.calcular_forca_sinal_adaptativa(
        indicadores, 'BULL_TREND', volatilidade=2.0, volume_ratio=2.5
    )
    
    print(f"\n📊 {explicacao}")
    print(f"⚡ Força: {forca}%")
    print(f"⚖️  Pesos usados:")
    for k, v in pesos.items():
        print(f"   {k}: {v*100:.0f}%")
    print(f"✅ Contribuições:")
    for d in detalhes:
        print(f"   {d}")
    
    acao, conf, motivo = contexto.recomendar_acao_por_contexto('COMPRAR', 'BULL_TREND', forca)
    print(f"\n🎯 Ação: {acao}")
    print(f"💯 Confiança: {conf:.0f}%")
    print(f"💡 Motivo: {motivo}")
    
    # Cenário 2: Consolidation
    print("\n" + "=" * 60)
    print("CENÁRIO 2: CONSOLIDATION + VOLUME BAIXO")
    print("=" * 60)
    
    indicadores2 = {
        'EMA': False,  # EMA8 ≈ EMA21
        'RSI': True,   # RSI 35 (oversold)
        'Volume': False,  # Volume 0.6x
        'BB': True     # Preço no BB inferior
    }
    
    forca2, pesos2, explicacao2, detalhes2 = contexto.calcular_forca_sinal_adaptativa(
        indicadores2, 'CONSOLIDATION', volatilidade=0.8, volume_ratio=0.6
    )
    
    print(f"\n📊 {explicacao2}")
    print(f"⚡ Força: {forca2}%")
    print(f"⚖️  Pesos usados:")
    for k, v in pesos2.items():
        print(f"   {k}: {v*100:.0f}%")
    print(f"✅ Contribuições:")
    for d in detalhes2:
        print(f"   {d}")
    
    acao2, conf2, motivo2 = contexto.recomendar_acao_por_contexto('COMPRAR', 'CONSOLIDATION', forca2)
    print(f"\n🎯 Ação: {acao2}")
    print(f"💯 Confiança: {conf2:.0f}%")
    print(f"💡 Motivo: {motivo2}")





