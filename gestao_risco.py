#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE RISCO PROFISSIONAL INTEGRADO
Transforma sinais em setups operacionais completos
"""


class GestaoRisco:
    """
    Gerenciamento de risco profissional
    Calcula posição, expectativa, e valida R/R
    """
    
    def __init__(self, capital_total=10000, risk_per_trade=0.5, rr_minimo=1.8, 
                 stop_trailing=True):
        self.capital_total = capital_total
        self.risk_per_trade = risk_per_trade  # %
        self.rr_minimo = rr_minimo
        self.stop_trailing = stop_trailing
    
    def calcular_posicao(self, entry: float, sl: float):
        """
        Calcula tamanho da posição baseado no risco
        
        Args:
            entry: preço de entrada
            sl: stop loss
        
        Returns:
            dict com tamanho, risco_usd, e detalhes
        """
        # Distância do stop em %
        stop_distance = abs(entry - sl) / entry
        
        # Risco em USD
        risco_usd = self.capital_total * (self.risk_per_trade / 100)
        
        # Quantidade de moedas
        quantidade = risco_usd / abs(entry - sl)
        
        # Valor da posição
        valor_posicao = quantidade * entry
        
        # % da carteira
        pct_carteira = (valor_posicao / self.capital_total) * 100
        
        return {
            'quantidade': round(quantidade, 6),
            'valor_posicao': round(valor_posicao, 2),
            'pct_carteira': round(pct_carteira, 2),
            'risco_usd': round(risco_usd, 2),
            'stop_distance_pct': round(stop_distance * 100, 2)
        }
    
    def calcular_expectativa(self, entry: float, tp: float, sl: float, 
                            probabilidade_acerto: float = 0.6):
        """
        Calcula expectativa matemática do trade
        
        Args:
            entry: preço de entrada
            tp: take profit
            sl: stop loss
            probabilidade_acerto: % de acerto (0.0 a 1.0)
        
        Returns:
            dict com expectativa e análise
        """
        # Ganho e perda
        ganho = abs(tp - entry)
        perda = abs(entry - sl)
        
        # R/R
        rr = ganho / perda if perda > 0 else 0
        
        # Expectativa = (Prob Win * Ganho) - (Prob Loss * Perda)
        prob_loss = 1 - probabilidade_acerto
        expectativa = (probabilidade_acerto * ganho) - (prob_loss * perda)
        expectativa_pct = (expectativa / entry) * 100
        
        # Análise
        if expectativa_pct > 0.5:
            qualidade = "EXCELENTE"
        elif expectativa_pct > 0.2:
            qualidade = "BOA"
        elif expectativa_pct > 0:
            qualidade = "POSITIVA"
        else:
            qualidade = "NEGATIVA"
        
        return {
            'expectativa_usd': round(expectativa, 2),
            'expectativa_pct': round(expectativa_pct, 2),
            'rr': round(rr, 2),
            'qualidade': qualidade,
            'prob_acerto': probabilidade_acerto
        }
    
    def validar_setup(self, entry: float, tp: float, sl: float):
        """
        Valida se o setup atende os critérios de risco
        
        Returns:
            tuple (valido: bool, motivo: str)
        """
        # Calcular R/R
        ganho = abs(tp - entry)
        perda = abs(entry - sl)
        rr = ganho / perda if perda > 0 else 0
        
        # Validar R/R mínimo
        if rr < self.rr_minimo:
            return False, f"R/R {rr:.2f} < mínimo {self.rr_minimo}"
        
        # Validar stop não muito largo
        stop_pct = (perda / entry) * 100
        if stop_pct > 5:  # 5% máximo
            return False, f"Stop muito largo ({stop_pct:.1f}%)"
        
        return True, f"Setup válido (R/R {rr:.2f})"
    
    def criar_setup_completo(self, par: str, acao: str, entry: float, 
                            tp_list: list, sl: float, probabilidade: float = 0.6):
        """
        Cria setup operacional completo
        
        Returns:
            dict com todas informações necessárias para operar
        """
        # Validar
        valido, motivo_validacao = self.validar_setup(entry, tp_list[0], sl)
        
        if not valido:
            return {'valido': False, 'motivo': motivo_validacao}
        
        # Calcular posição
        posicao = self.calcular_posicao(entry, sl)
        
        # Calcular expectativa
        expectativa = self.calcular_expectativa(entry, tp_list[0], sl, probabilidade)
        
        # Calcular retorno esperado em USD
        retorno_tp1 = posicao['quantidade'] * abs(tp_list[0] - entry)
        retorno_tp2 = posicao['quantidade'] * abs(tp_list[1] - entry) if len(tp_list) > 1 else 0
        retorno_tp3 = posicao['quantidade'] * abs(tp_list[2] - entry) if len(tp_list) > 2 else 0
        
        return {
            'valido': True,
            'par': par,
            'acao': acao,
            'entry': entry,
            'tp': tp_list,
            'sl': sl,
            
            # Posição
            'quantidade': posicao['quantidade'],
            'valor_posicao': posicao['valor_posicao'],
            'pct_carteira': posicao['pct_carteira'],
            
            # Risco
            'risco_usd': posicao['risco_usd'],
            'risco_pct': self.risk_per_trade,
            
            # Retorno
            'retorno_tp1_usd': round(retorno_tp1, 2),
            'retorno_tp2_usd': round(retorno_tp2, 2),
            'retorno_tp3_usd': round(retorno_tp3, 2),
            
            # Expectativa
            'expectativa_usd': expectativa['expectativa_usd'],
            'expectativa_pct': expectativa['expectativa_pct'],
            'rr': expectativa['rr'],
            'qualidade': expectativa['qualidade'],
            
            # Stop trailing
            'stop_trailing': self.stop_trailing
        }


# ========================================
# EXEMPLO DE USO
# ========================================

if __name__ == "__main__":
    # Criar sistema de risco
    risco = GestaoRisco(
        capital_total=10000,  # $10k
        risk_per_trade=1.0,   # 1% por trade
        rr_minimo=2.0,
        stop_trailing=True
    )
    
    # Setup: COMPRAR BTCUSDT
    setup = risco.criar_setup_completo(
        par='BTCUSDT',
        acao='COMPRAR',
        entry=100000,
        tp_list=[101000, 102000, 103000],
        sl=99500,
        probabilidade=0.65
    )
    
    if setup['valido']:
        print("=" * 60)
        print(f"🎯 SETUP OPERACIONAL - {setup['acao']} {setup['par']}")
        print("=" * 60)
        
        print(f"\n💰 POSIÇÃO:")
        print(f"   Quantidade: {setup['quantidade']:.6f}")
        print(f"   Valor: ${setup['valor_posicao']:,.2f}")
        print(f"   % Carteira: {setup['pct_carteira']:.1f}%")
        
        print(f"\n📍 NÍVEIS:")
        print(f"   Entry: ${setup['entry']:,.2f}")
        print(f"   TP1: ${setup['tp'][0]:,.2f} (+${setup['retorno_tp1_usd']:,.2f})")
        print(f"   TP2: ${setup['tp'][1]:,.2f} (+${setup['retorno_tp2_usd']:,.2f})")
        print(f"   TP3: ${setup['tp'][2]:,.2f} (+${setup['retorno_tp3_usd']:,.2f})")
        print(f"   SL: ${setup['sl']:,.2f} (-${setup['risco_usd']:,.2f})")
        
        print(f"\n📊 ANÁLISE:")
        print(f"   R/R: 1:{setup['rr']:.1f}")
        print(f"   Risco: ${setup['risco_usd']:,.2f} ({setup['risco_pct']}%)")
        print(f"   Expectativa: ${setup['expectativa_usd']:,.2f} ({setup['expectativa_pct']:+.2f}%)")
        print(f"   Qualidade: {setup['qualidade']}")
        print(f"   Stop Trailing: {'SIM' if setup['stop_trailing'] else 'NÃO'}")
        
        print("\n" + "=" * 60)
    else:
        print(f"❌ Setup inválido: {setup['motivo']}")





