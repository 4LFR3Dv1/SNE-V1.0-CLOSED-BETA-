#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNE MODO RENAN
Une Teoria dos Campos Magnéticos com Lógica Operacional
"""

import pandas as pd
import numpy as np
from catalogo_magnetico import obter_zonas_magneticas


class ModoRenan:
    """
    Decisão baseada em campos magnéticos + contexto de mercado
    A teoria magnética encontra a lógica algorítmica
    """
    
    def __init__(self):
        self.distancia_minima_zona = 0.003  # 0.3%
    
    def campo_magnetico_decision(self, preco: float, zonas: list):
        """
        Decisão baseada em proximidade de zonas magnéticas
        
        Args:
            preco: preço atual
            zonas: lista de zonas magnéticas
        
        Returns:
            tuple (acao, forca, motivo)
        """
        if not zonas:
            return "NEUTRO", 0, "Sem zonas catalogadas"
        
        # Ordenar zonas
        zonas_ordenadas = sorted(zonas)
        
        # Encontrar zona mais próxima
        distancias = [abs(preco - z) / preco for z in zonas_ordenadas]
        zona_mais_proxima = zonas_ordenadas[np.argmin(distancias)]
        distancia_minima = min(distancias)
        
        # Decisão por proximidade
        if distancia_minima < self.distancia_minima_zona:
            # Muito próximo de zona = AGUARDAR (pode ser resistência/suporte)
            return "AGUARDAR", 0, f"Zona magnética {zona_mais_proxima:.2f} a {distancia_minima*100:.2f}%"
        
        # Preço acima da zona mais alta
        if preco > zonas_ordenadas[-1]:
            # Rompeu topo = COMPRAR
            forca = min(100, (preco - zonas_ordenadas[-1]) / zonas_ordenadas[-1] * 1000)
            return "COMPRAR", forca, f"Rompeu zona topo {zonas_ordenadas[-1]:.2f}"
        
        # Preço abaixo da zona mais baixa
        elif preco < zonas_ordenadas[0]:
            # Rompeu fundo = VENDER
            forca = min(100, (zonas_ordenadas[0] - preco) / zonas_ordenadas[0] * 1000)
            return "VENDER", forca, f"Rompeu zona fundo {zonas_ordenadas[0]:.2f}"
        
        # Preço entre zonas
        else:
            # Encontrar zona superior e inferior
            zona_inferior = max([z for z in zonas_ordenadas if z < preco])
            zona_superior = min([z for z in zonas_ordenadas if z > preco])
            
            # Calcular posição relativa (0 = inferior, 1 = superior)
            posicao = (preco - zona_inferior) / (zona_superior - zona_inferior)
            
            if posicao > 0.7:
                # Próximo da zona superior = pode romper
                return "COMPRAR", 60, f"Próximo de romper {zona_superior:.2f}"
            elif posicao < 0.3:
                # Próximo da zona inferior = pode cair
                return "VENDER", 60, f"Próximo de romper {zona_inferior:.2f}"
            else:
                # Centro do range
                return "NEUTRO", 30, f"Centro do range ({zona_inferior:.2f}-{zona_superior:.2f})"
    
    def integrar_com_contexto(self, preco: float, zonas: list, contexto: str):
        """
        Une campo magnético + contexto de mercado
        
        Args:
            preco: preço atual
            zonas: zonas magnéticas
            contexto: bull_trend, bear_trend, etc.
        
        Returns:
            dict com decisão integrada
        """
        # Decisão magnética
        acao_mag, forca_mag, motivo_mag = self.campo_magnetico_decision(preco, zonas)
        
        # Ajustar por contexto
        forca_final = forca_mag
        bonus_contexto = 0
        
        if contexto == 'BULL_TREND' and acao_mag == 'COMPRAR':
            bonus_contexto = 20
            motivo_contexto = "Bull trend confirma COMPRA"
        elif contexto == 'BEAR_TREND' and acao_mag == 'VENDER':
            bonus_contexto = 20
            motivo_contexto = "Bear trend confirma VENDA"
        elif contexto == 'CONSOLIDATION' and acao_mag == 'AGUARDAR':
            bonus_contexto = 10
            motivo_contexto = "Consolidation reforça AGUARDAR"
        elif contexto == 'BULL_TREND' and acao_mag == 'VENDER':
            bonus_contexto = -30
            motivo_contexto = "Bull trend CONTRA venda"
        elif contexto == 'BEAR_TREND' and acao_mag == 'COMPRAR':
            bonus_contexto = -30
            motivo_contexto = "Bear trend CONTRA compra"
        else:
            motivo_contexto = "Contexto neutro"
        
        forca_final = max(0, min(100, forca_mag + bonus_contexto))
        
        # Determinar ação final
        if forca_final < 40:
            acao_final = "AGUARDAR"
        else:
            acao_final = acao_mag
        
        return {
            'acao': acao_final,
            'forca': forca_final,
            'motivo_magnetico': motivo_mag,
            'motivo_contexto': motivo_contexto,
            'bonus_contexto': bonus_contexto,
            'zona_mais_proxima': min(zonas, key=lambda z: abs(preco - z)) if zonas else None,
            'distancia_zona': min([abs(preco - z) / preco for z in zonas]) * 100 if zonas else None
        }
    
    def gerar_setup_renan(self, symbol: str, preco: float, zonas: list, 
                          contexto: str, ema8: float, ema21: float):
        """
        Gera setup completo no estilo Renan
        
        Returns:
            dict com setup operacional
        """
        # Integração magnética + contexto
        decisao = self.integrar_com_contexto(preco, zonas, contexto)
        
        # Validação adicional com EMAs
        if ema8 > ema21 and decisao['acao'] == 'VENDER':
            decisao['acao'] = 'AGUARDAR'
            decisao['motivo_adicional'] = "EMAs não confirmam VENDA"
        elif ema8 < ema21 and decisao['acao'] == 'COMPRAR':
            decisao['acao'] = 'AGUARDAR'
            decisao['motivo_adicional'] = "EMAs não confirmam COMPRA"
        
        # Calcular níveis operacionais
        if decisao['acao'] == 'COMPRAR':
            entry = preco
            # TP baseado em próxima zona ou +1%
            proxima_zona = min([z for z in zonas if z > preco]) if any(z > preco for z in zonas) else preco * 1.01
            tp = proxima_zona
            sl = preco * 0.997
        elif decisao['acao'] == 'VENDER':
            entry = preco
            # TP baseado em zona inferior ou -1%
            zona_inferior = max([z for z in zonas if z < preco]) if any(z < preco for z in zonas) else preco * 0.99
            tp = zona_inferior
            sl = preco * 1.003
        else:
            entry = tp = sl = None
        
        return {
            'symbol': symbol,
            'acao': decisao['acao'],
            'forca': decisao['forca'],
            'entry': entry,
            'tp': tp,
            'sl': sl,
            'rr': abs(tp - entry) / abs(entry - sl) if entry and tp and sl and sl != entry else 0,
            'motivo_principal': decisao['motivo_magnetico'],
            'motivo_contexto': decisao['motivo_contexto'],
            'bonus_contexto': decisao['bonus_contexto'],
            'zona_referencia': decisao['zona_mais_proxima'],
            'distancia_zona_pct': decisao['distancia_zona']
        }


# ========================================
# EXEMPLO DE USO
# ========================================

if __name__ == "__main__":
    modo_renan = ModoRenan()
    
    # Cenário: BTC em bull trend próximo de zona magnética
    preco_btc = 100500
    zonas_btc = [99000, 100000, 101000, 102000]
    
    print("=" * 60)
    print("SNE MODO RENAN - DECISÃO MAGNÉTICA + CONTEXTO")
    print("=" * 60)
    
    setup = modo_renan.gerar_setup_renan(
        symbol='BTCUSDT',
        preco=preco_btc,
        zonas=zonas_btc,
        contexto='BULL_TREND',
        ema8=100400,
        ema21=100100
    )
    
    print(f"\n🧲 ANÁLISE MAGNÉTICA:")
    print(f"   Preço: ${setup['entry']:,.2f}")
    print(f"   Zona Referência: ${setup['zona_referencia']:,.2f}")
    print(f"   Distância: {setup['distancia_zona_pct']:.2f}%")
    
    print(f"\n🎯 DECISÃO:")
    print(f"   Ação: {setup['acao']}")
    print(f"   Força: {setup['forca']:.0f}%")
    
    print(f"\n💡 MOTIVOS:")
    print(f"   Magnético: {setup['motivo_principal']}")
    print(f"   Contexto: {setup['motivo_contexto']} ({setup['bonus_contexto']:+d})")
    
    if setup['entry']:
        print(f"\n📊 NÍVEIS OPERACIONAIS:")
        print(f"   Entry: ${setup['entry']:,.2f}")
        print(f"   TP: ${setup['tp']:,.2f}")
        print(f"   SL: ${setup['sl']:,.2f}")
        print(f"   R/R: 1:{setup['rr']:.1f}")





