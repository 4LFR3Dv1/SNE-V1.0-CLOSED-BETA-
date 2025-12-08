#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÕES NOS CÁLCULOS DE INDICADORES - SNE RADAR
Corrige inconsistências específicas nos cálculos de indicadores técnicos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple


class CorrecoesIndicadoresSNE:
    """Sistema de correção específica para cálculos de indicadores"""
    
    def __init__(self):
        self.thresholds_corrigidos = {
            # Volatilidade
            'volatilidade_muito_baixa': 0.5,
            'volatilidade_baixa': 1.0,
            'volatilidade_media': 2.0,
            'volatilidade_alta': 4.0,
            'volatilidade_muito_alta': 6.0,
            
            # RSI
            'rsi_sobrevenda': 30,
            'rsi_neutro_baixo': 40,
            'rsi_neutro_alto': 60,
            'rsi_sobrecompra': 70,
            
            # Gap EMAs
            'gap_emas_muito_pequeno': 0.1,
            'gap_emas_pequeno': 0.3,
            'gap_emas_moderado': 0.8,
            'gap_emas_grande': 1.5,
            
            # Força da tendência
            'forca_muito_fraca': 2.0,
            'forca_fraca': 4.0,
            'forca_moderada': 6.0,
            'forca_forte': 8.0,
            'forca_muito_forte': 9.0
        }
    
    def corrigir_calculo_forca_tendencia(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Corrige cálculo da força da tendência baseado em múltiplos fatores
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            Dict com força corrigida e fatores de correção
        """
        try:
            # Calcular indicadores básicos
            ema8 = df['close'].ewm(span=8, adjust=False).mean().iloc[-1]
            ema21 = df['close'].ewm(span=21, adjust=False).mean().iloc[-1]
            preco_atual = df['close'].iloc[-1]
            
            # Calcular RSI
            rsi = self._calcular_rsi_corrigido(df)
            
            # Calcular volatilidade
            volatilidade = df['close'].pct_change().std() * 100
            
            # Calcular gap entre EMAs
            gap_emas = abs(ema8 - ema21) / ema21 * 100
            
            # Calcular força baseada em múltiplos fatores
            forca_calculada = self._calcular_forca_multi_fator(
                ema8, ema21, preco_atual, rsi, volatilidade, gap_emas
            )
            
            # Determinar tendência
            if ema8 > ema21:
                tendencia = 'ALTA'
            elif ema8 < ema21:
                tendencia = 'BAIXA'
            else:
                tendencia = 'LATERAL'
            
            # Aplicar correções de consistência
            forca_corrigida, correcoes = self._aplicar_correcoes_forca(
                forca_calculada, rsi, volatilidade, gap_emas, tendencia
            )
            
            return {
                'forca_original': forca_calculada,
                'forca_corrigida': forca_corrigida,
                'tendencia': tendencia,
                'rsi': rsi,
                'volatilidade': volatilidade,
                'gap_emas': gap_emas,
                'correcoes_aplicadas': correcoes,
                'indicadores': {
                    'EMA8': ema8,
                    'EMA21': ema21,
                    'preco_atual': preco_atual
                }
            }
            
        except Exception as e:
            return {
                'erro': f"Erro no cálculo: {e}",
                'forca_corrigida': 5.0,  # Valor neutro
                'tendencia': 'INDEFINIDA'
            }
    
    def _calcular_rsi_corrigido(self, df: pd.DataFrame, periodo: int = 14) -> float:
        """Calcula RSI com correções para evitar valores extremos"""
        try:
            if len(df) < periodo + 1:
                return 50.0  # Valor neutro
            
            # Calcular mudanças de preço
            delta = df['close'].diff()
            
            # Separar ganhos e perdas
            ganhos = delta.where(delta > 0, 0)
            perdas = -delta.where(delta < 0, 0)
            
            # Calcular médias móveis exponenciais
            avg_ganhos = ganhos.ewm(span=periodo, adjust=False).mean()
            avg_perdas = perdas.ewm(span=periodo, adjust=False).mean()
            
            # Evitar divisão por zero
            avg_perdas = avg_perdas.replace(0, 0.001)
            
            # Calcular RS e RSI
            rs = avg_ganhos / avg_perdas
            rsi = 100 - (100 / (1 + rs))
            
            # Limitar valores extremos
            rsi_atual = rsi.iloc[-1]
            if pd.isna(rsi_atual):
                return 50.0
            
            # Suavizar valores extremos
            if rsi_atual > 95:
                return 90.0
            elif rsi_atual < 5:
                return 10.0
            
            return round(rsi_atual, 1)
            
        except Exception:
            return 50.0
    
    def _calcular_forca_multi_fator(self, ema8: float, ema21: float, preco: float, 
                                   rsi: float, volatilidade: float, gap_emas: float) -> float:
        """Calcula força da tendência baseada em múltiplos fatores"""
        
        score = 0.0
        
        # 1. Fator EMA (peso 3.0)
        if ema8 > ema21:
            # Tendência de alta
            fator_ema = min(3.0, gap_emas * 2.0)
        elif ema8 < ema21:
            # Tendência de baixa
            fator_ema = min(3.0, gap_emas * 2.0)
        else:
            # Lateral
            fator_ema = 0.0
        
        score += fator_ema
        
        # 2. Fator Preço vs EMAs (peso 2.0)
        if preco > ema8 > ema21:
            fator_preco = 2.0  # Alinhamento perfeito bullish
        elif preco < ema8 < ema21:
            fator_preco = 2.0  # Alinhamento perfeito bearish
        elif preco > ema8:
            fator_preco = 1.0  # Parcialmente bullish
        elif preco < ema8:
            fator_preco = 1.0  # Parcialmente bearish
        else:
            fator_preco = 0.0  # Neutro
        
        score += fator_preco
        
        # 3. Fator RSI (peso 2.0)
        if rsi > 70:
            fator_rsi = 1.5  # Sobrecompra mas momentum forte
        elif rsi < 30:
            fator_rsi = 1.5  # Sobrevenda mas momentum forte
        elif 50 <= rsi <= 70:
            fator_rsi = 2.0  # Momentum positivo
        elif 30 <= rsi <= 50:
            fator_rsi = 1.0  # Momentum negativo
        else:
            fator_rsi = 0.5  # Neutro
        
        score += fator_rsi
        
        # 4. Fator Volatilidade (peso 1.0)
        if volatilidade < 1.0:
            fator_vol = 0.5  # Muito baixa - tendência fraca
        elif volatilidade < 2.0:
            fator_vol = 1.0  # Baixa - tendência moderada
        elif volatilidade < 4.0:
            fator_vol = 1.5  # Média - tendência forte
        else:
            fator_vol = 1.0  # Alta - volatilidade reduz força
        
        score += fator_vol
        
        # Normalizar para escala 0-10
        score_maximo = 8.0  # Máximo teórico
        forca_normalizada = min(10.0, (score / score_maximo) * 10.0)
        
        return round(forca_normalizada, 1)
    
    def _aplicar_correcoes_forca(self, forca: float, rsi: float, volatilidade: float, 
                                gap_emas: float, tendencia: str) -> Tuple[float, List[str]]:
        """Aplica correções de consistência na força calculada"""
        
        correcoes = []
        forca_corrigida = forca
        
        # Correção 1: Força muito alta com volatilidade muito baixa
        if forca >= 8.0 and volatilidade < 0.5:
            forca_corrigida = min(6.0, forca)
            correcoes.append("Força reduzida devido à volatilidade muito baixa")
        
        # Correção 2: Força muito baixa com RSI extremo
        if forca <= 2.0 and (rsi > 80 or rsi < 20):
            forca_corrigida = max(4.0, forca)
            correcoes.append("Força aumentada devido ao RSI extremo")
        
        # Correção 3: Força alta com gap muito pequeno
        if forca >= 7.0 and gap_emas < 0.2:
            forca_corrigida = min(5.0, forca)
            correcoes.append("Força reduzida devido ao gap pequeno entre EMAs")
        
        # Correção 4: Força baixa com gap grande
        if forca <= 3.0 and gap_emas > 1.0:
            forca_corrigida = max(5.0, forca)
            correcoes.append("Força aumentada devido ao gap grande entre EMAs")
        
        # Correção 5: Força inconsistente com volatilidade
        if volatilidade > 5.0 and forca > 8.0:
            forca_corrigida = min(6.0, forca)
            correcoes.append("Força reduzida devido à alta volatilidade")
        
        return forca_corrigida, correcoes
    
    def corrigir_niveis_suporte_resistencia(self, df: pd.DataFrame, 
                                          tendencia: str) -> Dict[str, Any]:
        """
        Corrige níveis de suporte e resistência baseado na tendência
        
        Args:
            df: DataFrame com dados OHLCV
            tendencia: Tendência atual (ALTA, BAIXA, LATERAL)
            
        Returns:
            Dict com níveis corrigidos
        """
        try:
            # Calcular EMAs
            ema8 = df['close'].ewm(span=8, adjust=False).mean().iloc[-1]
            ema21 = df['close'].ewm(span=21, adjust=False).mean().iloc[-1]
            ema50 = df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
            
            # Calcular níveis estáticos (máximas/mínimas recentes)
            dados_recentes = df.tail(50)
            maximas = dados_recentes['high'].rolling(window=5, center=True).max()
            minimas = dados_recentes['low'].rolling(window=5, center=True).min()
            
            # Identificar pontos de reversão
            resistencias_estaticas = []
            suportes_estaticos = []
            
            for i in range(2, len(maximas) - 2):
                if maximas.iloc[i] == dados_recentes['high'].iloc[i]:
                    resistencias_estaticas.append(maximas.iloc[i])
                if minimas.iloc[i] == dados_recentes['low'].iloc[i]:
                    suportes_estaticos.append(minimas.iloc[i])
            
            # Remover duplicatas e ordenar
            resistencias_estaticas = sorted(list(set(resistencias_estaticas)), reverse=True)[:5]
            suportes_estaticos = sorted(list(set(suportes_estaticos)))[:5]
            
            # Aplicar correções baseadas na tendência
            suportes_corrigidos = suportes_estaticos.copy()
            resistencias_corrigidas = resistencias_estaticas.copy()
            
            correcoes = []
            
            if tendencia == 'ALTA':
                # Em tendência de alta, EMAs são suportes dinâmicos
                if ema8 not in suportes_corrigidos:
                    suportes_corrigidos.insert(0, ema8)
                    correcoes.append("EMA8 adicionada como suporte dinâmico")
                
                if ema21 not in suportes_corrigidos:
                    suportes_corrigidos.insert(1, ema21)
                    correcoes.append("EMA21 adicionada como suporte dinâmico")
                
                # Remover EMAs das resistências se estiverem lá
                if ema8 in resistencias_corrigidas:
                    resistencias_corrigidas.remove(ema8)
                    correcoes.append("EMA8 removida das resistências")
                
                if ema21 in resistencias_corrigidas:
                    resistencias_corrigidas.remove(ema21)
                    correcoes.append("EMA21 removida das resistências")
            
            elif tendencia == 'BAIXA':
                # Em tendência de baixa, EMAs são resistências dinâmicas
                if ema8 not in resistencias_corrigidas:
                    resistencias_corrigidas.insert(0, ema8)
                    correcoes.append("EMA8 adicionada como resistência dinâmica")
                
                if ema21 not in resistencias_corrigidas:
                    resistencias_corrigidas.insert(1, ema21)
                    correcoes.append("EMA21 adicionada como resistência dinâmica")
                
                # Remover EMAs dos suportes se estiverem lá
                if ema8 in suportes_corrigidos:
                    suportes_corrigidos.remove(ema8)
                    correcoes.append("EMA8 removida dos suportes")
                
                if ema21 in suportes_corrigidos:
                    suportes_corrigidos.remove(ema21)
                    correcoes.append("EMA21 removida dos suportes")
            
            return {
                'suportes_originais': suportes_estaticos,
                'suportes_corrigidos': suportes_corrigidos[:5],
                'resistencias_originais': resistencias_estaticas,
                'resistencias_corrigidas': resistencias_corrigidas[:5],
                'correcoes_aplicadas': correcoes,
                'emas': {
                    'EMA8': ema8,
                    'EMA21': ema21,
                    'EMA50': ema50
                }
            }
            
        except Exception as e:
            return {
                'erro': f"Erro no cálculo: {e}",
                'suportes_corrigidos': [],
                'resistencias_corrigidas': []
            }
    
    def corrigir_targets_projecao(self, preco_atual: float, volatilidade: float, 
                                tendencia: str, forca_tendencia: float) -> Dict[str, Any]:
        """
        Corrige targets de projeção baseado na volatilidade e força da tendência
        
        Args:
            preco_atual: Preço atual
            volatilidade: Volatilidade em %
            tendencia: Tendência atual
            forca_tendencia: Força da tendência (0-10)
            
        Returns:
            Dict com targets corrigidos
        """
        try:
            # Calcular multiplicador baseado na volatilidade
            if volatilidade < 0.5:
                multiplicador_vol = 0.5  # Targets muito conservadores
            elif volatilidade < 1.0:
                multiplicador_vol = 0.8  # Targets conservadores
            elif volatilidade < 2.0:
                multiplicador_vol = 1.2  # Targets moderados
            elif volatilidade < 4.0:
                multiplicador_vol = 1.5  # Targets agressivos
            else:
                multiplicador_vol = 2.0  # Targets muito agressivos
            
            # Calcular multiplicador baseado na força da tendência
            multiplicador_forca = forca_tendencia / 10.0
            
            # Calcular movimento base
            movimento_base = volatilidade * multiplicador_vol * multiplicador_forca
            
            # Aplicar limite máximo baseado na volatilidade
            if volatilidade < 1.0:
                movimento_maximo = 2.0  # Máximo 2% para baixa volatilidade
            elif volatilidade < 3.0:
                movimento_maximo = 4.0  # Máximo 4% para média volatilidade
            else:
                movimento_maximo = 6.0  # Máximo 6% para alta volatilidade
            
            movimento_final = min(movimento_base, movimento_maximo)
            
            # Calcular targets baseados na tendência
            if tendencia == 'ALTA':
                target_base = preco_atual * (1 + movimento_final * 0.01)
                target_otimista = preco_atual * (1 + movimento_final * 1.5 * 0.01)
                target_pessimista = preco_atual * (1 - movimento_final * 0.5 * 0.01)
            elif tendencia == 'BAIXA':
                target_base = preco_atual * (1 - movimento_final * 0.01)
                target_otimista = preco_atual * (1 - movimento_final * 1.5 * 0.01)
                target_pessimista = preco_atual * (1 + movimento_final * 0.5 * 0.01)
            else:
                # Lateral - targets menores
                target_base = preco_atual * (1 + movimento_final * 0.5 * 0.01)
                target_otimista = preco_atual * (1 + movimento_final * 0.01)
                target_pessimista = preco_atual * (1 - movimento_final * 0.5 * 0.01)
            
            # Calcular probabilidades baseadas na força
            if forca_tendencia >= 8:
                prob_base = 60
                prob_otimista = 30
                prob_pessimista = 10
            elif forca_tendencia >= 6:
                prob_base = 50
                prob_otimista = 25
                prob_pessimista = 25
            else:
                prob_base = 40
                prob_otimista = 20
                prob_pessimista = 40
            
            return {
                'targets_originais': {
                    'base': preco_atual * 1.02,  # Exemplo original
                    'otimista': preco_atual * 1.03,
                    'pessimista': preco_atual * 0.99
                },
                'targets_corrigidos': {
                    'base': round(target_base, 2),
                    'otimista': round(target_otimista, 2),
                    'pessimista': round(target_pessimista, 2)
                },
                'probabilidades': {
                    'base': prob_base,
                    'otimista': prob_otimista,
                    'pessimista': prob_pessimista
                },
                'parametros_calculo': {
                    'volatilidade': volatilidade,
                    'multiplicador_vol': multiplicador_vol,
                    'multiplicador_forca': multiplicador_forca,
                    'movimento_final': movimento_final
                },
                'correcoes_aplicadas': [
                    f"Targets ajustados para volatilidade {volatilidade:.2f}%",
                    f"Multiplicador aplicado: {multiplicador_vol:.1f}x",
                    f"Probabilidades ajustadas para força {forca_tendencia:.1f}/10"
                ]
            }
            
        except Exception as e:
            return {
                'erro': f"Erro no cálculo: {e}",
                'targets_corrigidos': {
                    'base': preco_atual,
                    'otimista': preco_atual,
                    'pessimista': preco_atual
                }
            }


# Instância global do corretor
corretor_indicadores = CorrecoesIndicadoresSNE()


def corrigir_indicadores_sne(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Função principal para corrigir todos os indicadores
    
    Args:
        df: DataFrame com dados OHLCV
        
    Returns:
        Dict com todos os indicadores corrigidos
    """
    # Corrigir força da tendência
    forca_corrigida = corretor_indicadores.corrigir_calculo_forca_tendencia(df)
    
    # Corrigir níveis de S/R
    niveis_corrigidos = corretor_indicadores.corrigir_niveis_suporte_resistencia(
        df, forca_corrigida.get('tendencia', 'LATERAL')
    )
    
    # Corrigir targets
    targets_corrigidos = corretor_indicadores.corrigir_targets_projecao(
        forca_corrigida.get('indicadores', {}).get('preco_atual', 0),
        forca_corrigida.get('volatilidade', 1.0),
        forca_corrigida.get('tendencia', 'LATERAL'),
        forca_corrigida.get('forca_corrigida', 5.0)
    )
    
    return {
        'forca_tendencia': forca_corrigida,
        'niveis_sr': niveis_corrigidos,
        'targets': targets_corrigidos,
        'timestamp': pd.Timestamp.now().isoformat(),
        'versao_correcao': '1.0'
    }


if __name__ == "__main__":
    # Teste do sistema de correção
    print("🧪 TESTANDO CORREÇÕES DE INDICADORES")
    print("=" * 60)
    
    # Criar dados de teste
    np.random.seed(42)
    dates = pd.date_range('2025-01-01', periods=100, freq='1H')
    
    # Simular dados de preço com tendência
    base_price = 100000
    returns = np.random.normal(0.001, 0.01, 100)  # 0.1% média, 1% desvio
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    df_teste = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.002 for p in prices],
        'low': [p * 0.998 for p in prices],
        'close': prices,
        'volume': np.random.uniform(1000, 5000, 100)
    })
    
    df_teste.set_index('timestamp', inplace=True)
    
    # Aplicar correções
    resultado = corrigir_indicadores_sne(df_teste)
    
    print("✅ Correções aplicadas com sucesso!")
    print(f"📊 Força da tendência: {resultado['forca_tendencia']['forca_corrigida']}/10")
    print(f"📈 Tendência: {resultado['forca_tendencia']['tendencia']}")
    print(f"📉 RSI: {resultado['forca_tendencia']['rsi']}")
    print(f"📊 Volatilidade: {resultado['forca_tendencia']['volatilidade']:.2f}%")
    
    if resultado['forca_tendencia']['correcoes_aplicadas']:
        print("\n🔧 Correções aplicadas:")
        for correcao in resultado['forca_tendencia']['correcoes_aplicadas']:
            print(f"  • {correcao}")
    
    print(f"\n💾 Resultado salvo com {len(resultado)} seções corrigidas")




