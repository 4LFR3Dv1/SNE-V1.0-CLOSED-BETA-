#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTIMIZADOR SNE RADAR
Sistema para otimizar parâmetros do backtest
"""

import json
import pandas as pd
import numpy as np
from itertools import product
from backtest_sne import EngineBacktestSNE, ColetorDadosHistoricos
import os
from datetime import datetime

class OtimizadorSNE:
    """Classe para otimizar parâmetros do SNE Radar"""
    
    def __init__(self, dados_historicos: dict):
        self.dados = dados_historicos
        self.resultados_otimizacao = []
        
    def otimizar_parametros(self, symbol: str, parametros_teste: dict):
        """
        Otimiza parâmetros do backtest
        
        Args:
            symbol: Par para otimização
            parametros_teste: Dict com ranges de parâmetros
        """
        print(f"\n🔧 OTIMIZANDO PARÂMETROS - {symbol}")
        print("="*60)
        
        # Gerar combinações de parâmetros
        combinacoes = self._gerar_combinacoes(parametros_teste)
        total_combinacoes = len(combinacoes)
        
        print(f"📊 Testando {total_combinacoes} combinações de parâmetros...")
        
        melhor_resultado = None
        melhor_retorno = -float('inf')
        
        for i, params in enumerate(combinacoes):
            try:
                # Executar backtest com parâmetros específicos
                resultado = self._executar_backtest_otimizado(symbol, params)
                
                if resultado and resultado.get('retorno_total', 0) > melhor_retorno:
                    melhor_retorno = resultado['retorno_total']
                    melhor_resultado = resultado
                
                # Progresso
                if (i + 1) % 10 == 0:
                    progresso = ((i + 1) / total_combinacoes) * 100
                    print(f"⏳ Progresso: {progresso:.1f}% - Melhor: {melhor_retorno:+.2f}%")
                
            except Exception as e:
                print(f"❌ Erro na combinação {i+1}: {e}")
                continue
        
        # Resultados da otimização
        print(f"\n✅ OTIMIZAÇÃO CONCLUÍDA!")
        print(f"🏆 Melhor resultado: {melhor_retorno:+.2f}%")
        
        if melhor_resultado:
            self._exibir_resultado_otimizado(melhor_resultado)
            self._salvar_resultado_otimizacao(melhor_resultado, symbol)
        
        return melhor_resultado
    
    def _gerar_combinacoes(self, parametros: dict):
        """Gera todas as combinações de parâmetros"""
        keys = list(parametros.keys())
        values = list(parametros.values())
        
        combinacoes = []
        for combo in product(*values):
            combinacoes.append(dict(zip(keys, combo)))
        
        return combinacoes
    
    def _executar_backtest_otimizado(self, symbol: str, params: dict):
        """Executa backtest com parâmetros específicos"""
        try:
            # Criar engine com parâmetros customizados
            engine = EngineBacktestSNEOtimizado(self.dados, params)
            
            # Executar backtest
            df = self.dados.get(symbol)
            if df.empty:
                return None
            
            # Período de teste (últimos 3 meses para validação)
            end_date = df.index[-1]
            start_date = df.index[-int(len(df) * 0.5)]  # Últimos 50% dos dados
            
            engine.executar_backtest(symbol, start_date.strftime('%Y-%m-%d'), 
                                   end_date.strftime('%Y-%m-%d'))
            
            # Adicionar parâmetros ao resultado
            metricas = engine.metricas.copy()
            metricas['parametros'] = params
            
            return metricas
            
        except Exception as e:
            print(f"❌ Erro no backtest otimizado: {e}")
            return None
    
    def _exibir_resultado_otimizado(self, resultado: dict):
        """Exibe resultado da otimização"""
        print(f"\n🏆 MELHOR CONFIGURAÇÃO ENCONTRADA:")
        print("-" * 50)
        
        # Parâmetros
        params = resultado.get('parametros', {})
        print("⚙️ PARÂMETROS OTIMIZADOS:")
        for param, valor in params.items():
            print(f"   {param}: {valor}")
        
        # Métricas
        print(f"\n📊 PERFORMANCE:")
        print(f"   Retorno Total: {resultado.get('retorno_total', 0):+.2f}%")
        print(f"   Win Rate: {resultado.get('win_rate', 0):.1f}%")
        print(f"   Sharpe Ratio: {resultado.get('sharpe_ratio', 0):.2f}")
        print(f"   Max Drawdown: {resultado.get('max_drawdown', 0):.2f}%")
        print(f"   Total Trades: {resultado.get('total_trades', 0)}")
    
    def _salvar_resultado_otimizacao(self, resultado: dict, symbol: str):
        """Salva resultado da otimização"""
        try:
            filename = f"otimizacao_resultado_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(resultado, f, indent=2, default=str)
            print(f"💾 Resultado salvo em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")


class EngineBacktestSNEOtimizado(EngineBacktestSNE):
    """Engine de backtest com parâmetros otimizáveis"""
    
    def __init__(self, dados_historicos: dict, parametros: dict):
        super().__init__(dados_historicos)
        
        # Aplicar parâmetros customizados
        self.stop_loss_pct = parametros.get('stop_loss_pct', 0.02)
        self.take_profit_pct = parametros.get('take_profit_pct', 0.04)
        self.confianca_minima = parametros.get('confianca_minima', 70)
        self.score_minimo_long = parametros.get('score_minimo_long', 7)
        self.score_maximo_short = parametros.get('score_maximo_short', 3)
        self.filtro_volume = parametros.get('filtro_volume', 1.0)
        self.filtro_volatilidade = parametros.get('filtro_volatilidade', True)
    
    def _processar_sinal(self, analise: dict, candle_atual: pd.Series, index: int):
        """Processa sinal com parâmetros otimizados"""
        try:
            sintese = analise.get('sintese', {})
            acao = sintese.get('acao', 'AGUARDAR')
            score = sintese.get('score', 5.0)
            confianca = sintese.get('confianca', 50)
            
            contexto = analise.get('contexto', {})
            volume_ratio = contexto.get('volume_ratio', 1.0)
            volatilidade = contexto.get('volatilidade', 30)
            
            preco_atual = candle_atual['close']
            
            # Filtros adicionais
            if volume_ratio < self.filtro_volume:
                return  # Volume muito baixo
            
            if self.filtro_volatilidade and volatilidade > 80:
                return  # Volatilidade muito alta
            
            # Só entrar se não estiver em posição e confiança alta
            if self.posicao_atual == 0 and confianca >= self.confianca_minima:
                if acao == 'LONG' and score >= self.score_minimo_long:
                    self._abrir_posicao('LONG', preco_atual, index, confianca)
                elif acao == 'SHORT' and score <= self.score_maximo_short:
                    self._abrir_posicao('SHORT', preco_atual, index, confianca)
            
        except Exception as e:
            print(f"❌ Erro ao processar sinal: {e}")


def executar_otimizacao_completa(symbol: str = "BTCUSDT"):
    """Executa otimização completa dos parâmetros"""
    
    print("🔧 INICIANDO OTIMIZAÇÃO SNE RADAR")
    print("="*60)
    
    try:
        # Carregar dados históricos
        coletor = ColetorDadosHistoricos()
        df = coletor.carregar_dados(symbol, "1h")
        
        if df.empty:
            print("❌ Dados não encontrados. Execute o backtest primeiro.")
            return
        
        print(f"📊 Dados carregados: {len(df)} candles")
        
        # Definir parâmetros para otimização
        parametros_teste = {
            'stop_loss_pct': [0.015, 0.02, 0.025, 0.03],  # 1.5% a 3%
            'take_profit_pct': [0.03, 0.04, 0.05, 0.06],  # 3% a 6%
            'confianca_minima': [65, 70, 75, 80],          # 65% a 80%
            'score_minimo_long': [6, 7, 8],               # 6 a 8
            'score_maximo_short': [2, 3, 4],              # 2 a 4
            'filtro_volume': [0.8, 1.0, 1.2],             # Volume filter
            'filtro_volatilidade': [True, False]          # Volatilidade filter
        }
        
        # Executar otimização
        otimizador = OtimizadorSNE({symbol: df})
        melhor_resultado = otimizador.otimizar_parametros(symbol, parametros_teste)
        
        if melhor_resultado:
            print(f"\n🎯 OTIMIZAÇÃO CONCLUÍDA!")
            print(f"📈 Melhoria esperada: {melhor_resultado.get('retorno_total', 0):+.2f}%")
            
            # Sugerir próximos passos
            print(f"\n💡 PRÓXIMOS PASSOS:")
            print("1. Testar configuração otimizada em período diferente")
            print("2. Validar em outros pares")
            print("3. Implementar filtros adicionais")
            print("4. Considerar position sizing dinâmico")
        
    except Exception as e:
        print(f"❌ Erro na otimização: {e}")


def analisar_resultado_atual():
    """Analisa o resultado atual e sugere melhorias"""
    
    print("📊 ANÁLISE DO RESULTADO ATUAL")
    print("="*50)
    
    # Resultados do backtest atual
    resultado_atual = {
        'retorno_total': 2.73,
        'win_rate': 38.1,
        'sharpe_ratio': 0.04,
        'max_drawdown': -16.51,
        'total_trades': 42,
        'profit_factor': 1.05
    }
    
    print("📈 RESULTADOS ATUAIS:")
    print(f"   Retorno: {resultado_atual['retorno_total']:+.2f}%")
    print(f"   Win Rate: {resultado_atual['win_rate']:.1f}%")
    print(f"   Sharpe: {resultado_atual['sharpe_ratio']:.2f}")
    print(f"   Drawdown: {resultado_atual['max_drawdown']:.2f}%")
    
    print(f"\n🔧 SUGESTÕES DE MELHORIA:")
    
    # Análise e sugestões
    if resultado_atual['win_rate'] < 45:
        print("❌ WIN RATE BAIXO (38.1%)")
        print("   💡 Aumentar threshold de confiança (70% → 75%)")
        print("   💡 Melhorar filtros de entrada")
        print("   💡 Considerar filtro de volume")
    
    if resultado_atual['sharpe_ratio'] < 0.5:
        print("❌ SHARPE RATIO BAIXO (0.04)")
        print("   💡 Otimizar relação risco/retorno")
        print("   💡 Reduzir drawdown máximo")
        print("   💡 Melhorar timing de entrada")
    
    if resultado_atual['max_drawdown'] < -15:
        print("❌ DRAWDOWN ALTO (-16.51%)")
        print("   💡 Reduzir stop loss (2% → 1.5%)")
        print("   💡 Implementar trailing stop")
        print("   💡 Adicionar filtro de volatilidade")
    
    print(f"\n🎯 CONFIGURAÇÕES SUGERIDAS:")
    print("   Stop Loss: 1.5% (atual: 2%)")
    print("   Take Profit: 4.5% (atual: 4%)")
    print("   Confiança Mínima: 75% (atual: 70%)")
    print("   Score Mínimo LONG: 7.5 (atual: 7)")
    print("   Filtro Volume: 1.2x (atual: 1.0x)")
    print("   Filtro Volatilidade: Ativo")
    
    print(f"\n📊 EXPECTATIVA DE MELHORIA:")
    print("   Win Rate: 38% → 45%+")
    print("   Sharpe Ratio: 0.04 → 0.5+")
    print("   Max Drawdown: -16% → -10%")
    print("   Retorno: 2.7% → 5%+")


if __name__ == "__main__":
    print("🔧 OTIMIZADOR SNE RADAR")
    print("="*40)
    print("1. Analisar resultado atual")
    print("2. Executar otimização completa")
    print("3. Sugerir melhorias")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == "1":
        analisar_resultado_atual()
    elif opcao == "2":
        executar_otimizacao_completa()
    elif opcao == "3":
        analisar_resultado_atual()
    else:
        print("❌ Opção inválida")

