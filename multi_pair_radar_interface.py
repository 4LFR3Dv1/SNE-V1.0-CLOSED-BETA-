#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Pair Radar Interface
Interface visual para monitoramento de múltiplos pares simultaneamente
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime
import pytz
from typing import Dict, List, Any
from multi_pair_context import analisar_mercado_completo
from contexto_mercado import analise_rapida_contexto

class MultiPairRadarInterface:
    """Interface visual para múltiplos pares"""
    
    def __init__(self):
        self.br_tz = pytz.timezone("America/Sao_Paulo")
        self.fig = None
        self.axes = {}
        self.pares_principais = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.pares_secundarios = ["ADAUSDT", "DOTUSDT", "AVAXUSDT", "MATICUSDT", "LINKUSDT"]
        
        # Cores por regime
        self.cores_regime = {
            'bull_trend': '#00ff00',      # Verde
            'bear_trend': '#ff0000',      # Vermelho
            'sideways': '#ffff00',        # Amarelo
            'volatile': '#ff8800',        # Laranja
            'consolidation': '#888888'    # Cinza
        }
        
        # Cores por score
        self.cores_score = {
            'muito_alto': '#00ff00',  # Verde
            'alto': '#88ff00',        # Verde claro
            'medio': '#ffff00',       # Amarelo
            'baixo': '#ff8800',       # Laranja
            'muito_baixo': '#ff0000'  # Vermelho
        }
    
    def criar_interface(self):
        """Cria a interface visual completa"""
        
        # Criar figura com layout em grid
        self.fig = plt.figure(figsize=(20, 12))
        self.fig.patch.set_facecolor('black')
        
        # Criar grid layout
        gs = GridSpec(4, 4, figure=self.fig, hspace=0.3, wspace=0.3)
        
        # Área principal - Par principal (maior)
        self.axes['principal'] = self.fig.add_subplot(gs[0:2, 0:2])
        
        # Áreas secundárias - Pares secundários (menores)
        self.axes['sec1'] = self.fig.add_subplot(gs[0, 2])
        self.axes['sec2'] = self.fig.add_subplot(gs[0, 3])
        self.axes['sec3'] = self.fig.add_subplot(gs[1, 2])
        self.axes['sec4'] = self.fig.add_subplot(gs[1, 3])
        
        # Área de ranking
        self.axes['ranking'] = self.fig.add_subplot(gs[2, 0:2])
        
        # Área de alertas
        self.axes['alertas'] = self.fig.add_subplot(gs[2, 2:4])
        
        # Área de estatísticas
        self.axes['stats'] = self.fig.add_subplot(gs[3, 0:2])
        
        # Área de recomendações
        self.axes['recomendacoes'] = self.fig.add_subplot(gs[3, 2:4])
        
        # Configurar todos os eixos
        for ax in self.axes.values():
            ax.set_facecolor('black')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        return self.fig
    
    def plotar_par_principal(self, dados: Dict[str, Any]):
        """Plota o par principal com detalhes"""
        ax = self.axes['principal']
        ax.clear()
        ax.set_facecolor('black')
        
        symbol = dados['symbol']
        score = dados['opportunity_score']
        regime = dados['market_regime']
        price = dados['price']
        trend = dados['trend_direction']
        volatility = dados['volatility_level']
        risk = dados['risk_level']
        
        # Cor baseada no regime
        cor = self.cores_regime.get(regime, '#ffffff')
        
        # Título
        ax.text(0.5, 0.95, f"{symbol}", 
                ha='center', va='top', fontsize=24, color=cor, weight='bold',
                transform=ax.transAxes)
        
        # Preço
        ax.text(0.5, 0.80, f"${price:.2f}", 
                ha='center', va='top', fontsize=20, color='white',
                transform=ax.transAxes)
        
        # Score circular
        circle = plt.Circle((0.5, 0.5), 0.25, 
                           color=self._get_cor_score(score), 
                           transform=ax.transAxes, alpha=0.3)
        ax.add_patch(circle)
        
        ax.text(0.5, 0.5, f"{score:.0f}", 
                ha='center', va='center', fontsize=48, color='white', weight='bold',
                transform=ax.transAxes)
        
        # Informações adicionais
        info_text = f"""
Regime: {regime.upper()}
Tendência: {trend}
Volatilidade: {volatility}
Risco: {risk}
"""
        ax.text(0.05, 0.20, info_text.strip(), 
                ha='left', va='top', fontsize=10, color='white',
                transform=ax.transAxes, family='monospace')
        
        # Interpretação
        if 'interpretation' in dados:
            interp = dados['interpretation'][:150] + "..."
            ax.text(0.5, 0.05, interp, 
                    ha='center', va='bottom', fontsize=8, color='yellow',
                    transform=ax.transAxes, wrap=True)
        
        ax.axis('off')
    
    def plotar_par_secundario(self, ax_name: str, dados: Dict[str, Any]):
        """Plota um par secundário"""
        ax = self.axes[ax_name]
        ax.clear()
        ax.set_facecolor('black')
        
        symbol = dados['symbol']
        score = dados['opportunity_score']
        regime = dados['market_regime']
        price = dados['price']
        
        # Cor baseada no score
        cor = self._get_cor_score(score)
        
        # Título
        ax.text(0.5, 0.90, symbol, 
                ha='center', va='top', fontsize=14, color='white', weight='bold',
                transform=ax.transAxes)
        
        # Score
        ax.text(0.5, 0.60, f"{score:.0f}", 
                ha='center', va='center', fontsize=32, color=cor, weight='bold',
                transform=ax.transAxes)
        
        # Preço
        ax.text(0.5, 0.30, f"${price:.2f}", 
                ha='center', va='center', fontsize=10, color='white',
                transform=ax.transAxes)
        
        # Regime
        ax.text(0.5, 0.10, regime.upper(), 
                ha='center', va='center', fontsize=8, color=self.cores_regime.get(regime, '#ffffff'),
                transform=ax.transAxes)
        
        ax.axis('off')
    
    def plotar_ranking(self, ranking: List[Dict[str, Any]]):
        """Plota o ranking de oportunidades"""
        ax = self.axes['ranking']
        ax.clear()
        ax.set_facecolor('black')
        
        # Título
        ax.text(0.5, 0.95, "🏆 RANKING DE OPORTUNIDADES", 
                ha='center', va='top', fontsize=14, color='yellow', weight='bold',
                transform=ax.transAxes)
        
        # Plotar top 8
        y_pos = 0.85
        for i, par in enumerate(ranking[:8], 1):
            symbol = par.get('symbol', 'N/A')
            # Usar priority_score se disponível, senão opportunity_score
            score = par.get('priority_score', par.get('opportunity_score', 0))
            regime = par.get('market_regime', par.get('regime', 'N/A'))
            
            # Cor baseada no score
            cor = self._get_cor_score(score)
            
            # Texto
            texto = f"{i}. {symbol:10s} {score:5.1f} {regime:15s}"
            ax.text(0.05, y_pos, texto, 
                    ha='left', va='top', fontsize=10, color=cor,
                    transform=ax.transAxes, family='monospace')
            
            y_pos -= 0.10
        
        ax.axis('off')
    
    def plotar_alertas(self, alertas: List[str]):
        """Plota alertas importantes"""
        ax = self.axes['alertas']
        ax.clear()
        ax.set_facecolor('black')
        
        # Título
        ax.text(0.5, 0.95, "⚠️ ALERTAS IMPORTANTES", 
                ha='center', va='top', fontsize=14, color='red', weight='bold',
                transform=ax.transAxes)
        
        # Plotar alertas
        y_pos = 0.85
        for alerta in alertas[:6]:
            ax.text(0.05, y_pos, f"• {alerta}", 
                    ha='left', va='top', fontsize=9, color='yellow',
                    transform=ax.transAxes, wrap=True)
            y_pos -= 0.13
        
        if not alertas:
            ax.text(0.5, 0.5, "Nenhum alerta no momento", 
                    ha='center', va='center', fontsize=10, color='gray',
                    transform=ax.transAxes)
        
        ax.axis('off')
    
    def plotar_estatisticas(self, stats: Dict[str, Any]):
        """Plota estatísticas gerais"""
        ax = self.axes['stats']
        ax.clear()
        ax.set_facecolor('black')
        
        # Título
        ax.text(0.5, 0.95, "📊 ESTATÍSTICAS DO MERCADO", 
                ha='center', va='top', fontsize=14, color='cyan', weight='bold',
                transform=ax.transAxes)
        
        # Estatísticas
        texto = f"""
Score Médio: {stats.get('avg_score', 0):.1f}/100
Melhor Oportunidade: {stats.get('max_score', 0):.1f}/100
Pares Analisados: {stats.get('total_pairs', 0)}
Pares com Score Alto (≥70): {stats.get('high_score_pairs', 0)}
Pares em Bull Trend: {stats.get('bull_pairs', 0)}
Pares em Bear Trend: {stats.get('bear_pairs', 0)}
"""
        ax.text(0.05, 0.75, texto.strip(), 
                ha='left', va='top', fontsize=10, color='white',
                transform=ax.transAxes, family='monospace')
        
        ax.axis('off')
    
    def plotar_recomendacoes(self, recomendacoes: List[str]):
        """Plota recomendações de trading"""
        ax = self.axes['recomendacoes']
        ax.clear()
        ax.set_facecolor('black')
        
        # Título
        ax.text(0.5, 0.95, "💡 RECOMENDAÇÕES", 
                ha='center', va='top', fontsize=14, color='lime', weight='bold',
                transform=ax.transAxes)
        
        # Plotar recomendações
        y_pos = 0.80
        for rec in recomendacoes[:5]:
            ax.text(0.05, y_pos, f"• {rec}", 
                    ha='left', va='top', fontsize=9, color='lightgreen',
                    transform=ax.transAxes, wrap=True)
            y_pos -= 0.15
        
        if not recomendacoes:
            ax.text(0.5, 0.5, "Aguardando oportunidades...", 
                    ha='center', va='center', fontsize=10, color='gray',
                    transform=ax.transAxes)
        
        ax.axis('off')
    
    def atualizar_interface(self, resultados: Dict[str, Dict[str, Any]], 
                           ranking: List[Dict[str, Any]]):
        """Atualiza toda a interface com novos dados"""
        
        # Par principal (melhor oportunidade)
        if ranking:
            par_principal = ranking[0]
            self.plotar_par_principal(par_principal)
            
            # Pares secundários (próximos 4)
            axes_sec = ['sec1', 'sec2', 'sec3', 'sec4']
            for i, ax_name in enumerate(axes_sec):
                if i + 1 < len(ranking):
                    self.plotar_par_secundario(ax_name, ranking[i + 1])
        
        # Ranking
        self.plotar_ranking(ranking)
        
        # Alertas
        alertas = self._gerar_alertas(ranking)
        self.plotar_alertas(alertas)
        
        # Estatísticas
        stats = self._calcular_estatisticas(ranking)
        self.plotar_estatisticas(stats)
        
        # Recomendações
        recomendacoes = self._gerar_recomendacoes(ranking)
        self.plotar_recomendacoes(recomendacoes)
        
        # Timestamp
        timestamp = datetime.now(self.br_tz).strftime('%Y-%m-%d %H:%M:%S')
        self.fig.text(0.5, 0.01, f"Última atualização: {timestamp}", 
                     ha='center', fontsize=8, color='gray')
        
        plt.draw()
        plt.pause(0.1)
    
    def _get_cor_score(self, score: float) -> str:
        """Retorna cor baseada no score"""
        if score >= 80:
            return self.cores_score['muito_alto']
        elif score >= 70:
            return self.cores_score['alto']
        elif score >= 50:
            return self.cores_score['medio']
        elif score >= 30:
            return self.cores_score['baixo']
        else:
            return self.cores_score['muito_baixo']
    
    def _gerar_alertas(self, ranking: List[Dict[str, Any]]) -> List[str]:
        """Gera alertas baseados no ranking"""
        alertas = []
        
        for par in ranking[:5]:
            score = par.get('priority_score', par.get('opportunity_score', 0))
            symbol = par.get('symbol', 'N/A')
            risk = par.get('risk_level', par.get('risk', 'MÉDIO'))
            
            if score >= 80:
                alertas.append(f"🔥 {symbol}: Oportunidade excepcional (Score {score:.0f})")
            
            if risk in ['MUITO ALTO', 'ALTO']:
                alertas.append(f"⚠️ {symbol}: Risco {risk} - Cautela recomendada")
            
            if par.get('warnings'):
                for warning in par['warnings'][:1]:
                    alertas.append(f"⚠️ {symbol}: {warning}")
        
        return alertas[:6]
    
    def _calcular_estatisticas(self, ranking: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estatísticas gerais"""
        if not ranking:
            return {}
        
        scores = [par.get('priority_score', par.get('opportunity_score', 0)) for par in ranking]
        regimes = [par.get('market_regime', par.get('regime', 'unknown')) for par in ranking]
        
        return {
            'avg_score': np.mean(scores),
            'max_score': max(scores),
            'total_pairs': len(ranking),
            'high_score_pairs': len([s for s in scores if s >= 70]),
            'bull_pairs': len([r for r in regimes if 'bull' in r]),
            'bear_pairs': len([r for r in regimes if 'bear' in r])
        }
    
    def _gerar_recomendacoes(self, ranking: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações de trading"""
        recomendacoes = []
        
        if not ranking:
            return recomendacoes
        
        # Melhor oportunidade
        melhor = ranking[0]
        melhor_score = melhor.get('priority_score', melhor.get('opportunity_score', 0))
        melhor_symbol = melhor.get('symbol', 'N/A')
        melhor_regime = melhor.get('market_regime', melhor.get('regime', 'N/A'))
        
        if melhor_score >= 70:
            recomendacoes.append(
                f"🎯 FOCO EM {melhor_symbol} - Score {melhor_score:.0f}, {melhor_regime}"
            )
        
        # Oportunidades secundárias
        secundarias = [p for p in ranking[1:5] 
                      if p.get('priority_score', p.get('opportunity_score', 0)) >= 60]
        if secundarias:
            symbols = ", ".join([p.get('symbol', 'N/A') for p in secundarias])
            recomendacoes.append(f"📊 Monitorar também: {symbols}")
        
        # Recomendações por regime
        bull_pairs = [p for p in ranking 
                     if 'bull' in p.get('market_regime', p.get('regime', ''))
                     and p.get('priority_score', p.get('opportunity_score', 0)) >= 60]
        if bull_pairs:
            recomendacoes.append(
                f"📈 {len(bull_pairs)} pares em tendência de alta com bom score"
            )
        
        # Avisos de risco
        high_risk = [p for p in ranking[:5] 
                    if p.get('risk_level', p.get('risk', 'MÉDIO')) in ['MUITO ALTO', 'ALTO']]
        if high_risk:
            recomendacoes.append(
                f"⚠️ {len(high_risk)} pares com risco elevado - Gestão rigorosa"
            )
        
        # Diversificação
        if len(ranking) >= 5:
            recomendacoes.append(
                "💼 Considerar diversificação entre top 3-5 oportunidades"
            )
        
        return recomendacoes[:5]
    
    def iniciar_modo_continuo(self, intervalo: int = 30):
        """Inicia atualização contínua da interface"""
        import time
        
        self.criar_interface()
        plt.ion()  # Modo interativo
        plt.show()
        
        print("🚀 Multi-Pair Radar Interface iniciada!")
        print(f"📊 Atualizando a cada {intervalo} segundos...")
        print("Pressione Ctrl+C para parar")
        
        try:
            while True:
                # Buscar dados
                print(f"\n🔄 Atualizando dados... {datetime.now().strftime('%H:%M:%S')}")
                resultados, ranking, _ = analisar_mercado_completo()
                
                # Atualizar interface
                self.atualizar_interface(resultados, ranking)
                
                # Aguardar próxima atualização
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print("\n⏹️ Interface encerrada pelo usuário")
            plt.close('all')

# Função principal para uso standalone
def iniciar_multi_pair_radar(intervalo: int = 30):
    """Inicia o radar multi-pair em modo standalone"""
    radar = MultiPairRadarInterface()
    radar.iniciar_modo_continuo(intervalo)

if __name__ == "__main__":
    iniciar_multi_pair_radar()
