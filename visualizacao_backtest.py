#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VISUALIZAÇÃO DE BACKTEST SNE RADAR
Gráficos e análises dos resultados de backtest
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json
import os
from typing import Dict, List, Optional

class VisualizadorBacktest:
    """Classe para visualizar resultados de backtest"""
    
    def __init__(self, resultados_backtest: Dict):
        self.resultados = resultados_backtest
        self.metricas = resultados_backtest.get('metricas', {})
        self.trades = resultados_backtest.get('trades', [])
        self.config = resultados_backtest.get('configuracao', {})
        
    def gerar_grafico_equity_curve(self, salvar: bool = True) -> str:
        """Gera gráfico da curva de equity"""
        try:
            if not self.trades:
                print("❌ Nenhum trade para visualizar")
                return ""
            
            # Preparar dados
            trades_completos = [t for t in self.trades if 'capital_final' in t]
            if not trades_completos:
                print("❌ Nenhum trade completo")
                return ""
            
            # Criar série de capital
            capital_series = [t['capital_final'] for t in trades_completos]
            timestamps = [t['timestamp'] for t in trades_completos]
            
            # Criar gráfico
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
            
            # Gráfico 1: Curva de Equity
            ax1.plot(timestamps, capital_series, linewidth=2, color='#00ff88', label='Capital')
            ax1.axhline(y=self.config.get('capital_inicial', 10000), color='red', 
                       linestyle='--', alpha=0.7, label='Capital Inicial')
            ax1.set_title('📈 Curva de Equity - SNE Radar Backtest', 
                         fontsize=16, fontweight='bold', color='white')
            ax1.set_ylabel('Capital ($)', fontsize=12, color='white')
            ax1.legend(fontsize=10)
            ax1.grid(True, alpha=0.3, color='gray')
            ax1.tick_params(colors='white')
            
            # Adicionar anotações de trades
            for i, trade in enumerate(trades_completos):
                resultado_pct = trade.get('resultado_pct', 0)
                cor = 'green' if resultado_pct > 0 else 'red'
                ax1.annotate(f'{resultado_pct:+.1f}%', 
                           xy=(trade['timestamp'], trade['capital_final']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, color=cor, fontweight='bold')
            
            # Gráfico 2: Drawdown
            peak = np.maximum.accumulate(capital_series)
            drawdown = (np.array(capital_series) - peak) / peak * 100
            
            ax2.fill_between(timestamps, drawdown, 0, alpha=0.3, color='red', label='Drawdown')
            ax2.plot(timestamps, drawdown, linewidth=1, color='red')
            ax2.set_title('📉 Drawdown', fontsize=14, fontweight='bold', color='white')
            ax2.set_xlabel('Trade #', fontsize=12, color='white')
            ax2.set_ylabel('Drawdown (%)', fontsize=12, color='white')
            ax2.grid(True, alpha=0.3, color='gray')
            ax2.tick_params(colors='white')
            
            # Configurar estilo
            plt.style.use('dark_background')
            plt.tight_layout()
            
            if salvar:
                filename = f"backtest_equity_curve_{self.config.get('symbol', 'BTC')}.png"
                plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
                plt.close()
                print(f"📊 Gráfico salvo: {filename}")
                return filename
            else:
                plt.show()
                return ""
                
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de equity: {e}")
            return ""
    
    def gerar_grafico_distribuicao_retornos(self, salvar: bool = True) -> str:
        """Gera gráfico da distribuição de retornos"""
        try:
            if not self.trades:
                print("❌ Nenhum trade para visualizar")
                return ""
            
            trades_completos = [t for t in self.trades if 'resultado_pct' in t]
            if not trades_completos:
                print("❌ Nenhum trade completo")
                return ""
            
            retornos = [t['resultado_pct'] for t in trades_completos]
            
            # Criar gráfico
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Histograma
            ax1.hist(retornos, bins=20, alpha=0.7, color='#00ff88', edgecolor='white')
            ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Break Even')
            ax1.axvline(x=np.mean(retornos), color='yellow', linestyle='-', linewidth=2, 
                       label=f'Média: {np.mean(retornos):.2f}%')
            ax1.set_title('📊 Distribuição de Retornos', fontsize=14, fontweight='bold', color='white')
            ax1.set_xlabel('Retorno por Trade (%)', fontsize=12, color='white')
            ax1.set_ylabel('Frequência', fontsize=12, color='white')
            ax1.legend(fontsize=10)
            ax1.grid(True, alpha=0.3, color='gray')
            ax1.tick_params(colors='white')
            
            # Box plot
            ax2.boxplot(retornos, patch_artist=True, 
                       boxprops=dict(facecolor='#00ff88', alpha=0.7),
                       medianprops=dict(color='red', linewidth=2))
            ax2.set_title('📦 Box Plot de Retornos', fontsize=14, fontweight='bold', color='white')
            ax2.set_ylabel('Retorno por Trade (%)', fontsize=12, color='white')
            ax2.grid(True, alpha=0.3, color='gray')
            ax2.tick_params(colors='white')
            
            # Adicionar estatísticas
            stats_text = f"""
Estatísticas:
Média: {np.mean(retornos):.2f}%
Mediana: {np.median(retornos):.2f}%
Std: {np.std(retornos):.2f}%
Min: {np.min(retornos):.2f}%
Max: {np.max(retornos):.2f}%
"""
            ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.8),
                    color='white')
            
            plt.style.use('dark_background')
            plt.tight_layout()
            
            if salvar:
                filename = f"backtest_distribuicao_{self.config.get('symbol', 'BTC')}.png"
                plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
                plt.close()
                print(f"📊 Gráfico salvo: {filename}")
                return filename
            else:
                plt.show()
                return ""
                
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de distribuição: {e}")
            return ""
    
    def gerar_grafico_metricas_performance(self, salvar: bool = True) -> str:
        """Gera gráfico com métricas de performance"""
        try:
            if not self.metricas or 'erro' in self.metricas:
                print("❌ Métricas não disponíveis")
                return ""
            
            # Criar gráfico de radar
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # Métricas para radar
            categorias = ['Win Rate', 'Retorno Total', 'Sharpe Ratio', 'Profit Factor', 'Consistência']
            
            # Normalizar métricas para 0-100
            win_rate = min(self.metricas.get('win_rate', 0), 100)
            retorno_total = max(min(self.metricas.get('retorno_total', 0) + 50, 100), 0)  # -50% a +50%
            sharpe_ratio = max(min(self.metricas.get('sharpe_ratio', 0) * 20 + 50, 100), 0)  # -2.5 a +2.5
            profit_factor = max(min(self.metricas.get('profit_factor', 0) * 25, 100), 0)  # 0 a 4
            consistencia = max(min(100 - abs(self.metricas.get('max_drawdown', 0)), 100), 0)
            
            valores = [win_rate, retorno_total, sharpe_ratio, profit_factor, consistencia]
            valores += valores[:1]  # Fechar o polígono
            
            # Ângulos
            angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
            angles += angles[:1]
            
            # Plotar
            ax.plot(angles, valores, 'o-', linewidth=2, color='#00ff88', label='Performance')
            ax.fill(angles, valores, alpha=0.25, color='#00ff88')
            
            # Configurar eixos
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categorias, fontsize=12, color='white')
            ax.set_ylim(0, 100)
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10, color='white')
            ax.grid(True, alpha=0.3, color='gray')
            
            # Título
            ax.set_title('🎯 Métricas de Performance - SNE Radar', 
                        fontsize=16, fontweight='bold', color='white', pad=20)
            
            # Adicionar valores nas categorias
            for angle, valor, categoria in zip(angles[:-1], valores[:-1], categorias):
                ax.text(angle, valor + 5, f'{valor:.0f}', ha='center', va='center', 
                       fontsize=10, fontweight='bold', color='white')
            
            plt.style.use('dark_background')
            plt.tight_layout()
            
            if salvar:
                filename = f"backtest_metricas_{self.config.get('symbol', 'BTC')}.png"
                plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
                plt.close()
                print(f"📊 Gráfico salvo: {filename}")
                return filename
            else:
                plt.show()
                return ""
                
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de métricas: {e}")
            return ""
    
    def gerar_grafico_trades_timeline(self, salvar: bool = True) -> str:
        """Gera gráfico da timeline de trades"""
        try:
            if not self.trades:
                print("❌ Nenhum trade para visualizar")
                return ""
            
            trades_completos = [t for t in self.trades if 'preco_saida' in t]
            if not trades_completos:
                print("❌ Nenhum trade completo")
                return ""
            
            # Criar gráfico
            fig, ax = plt.subplots(figsize=(15, 8))
            
            # Plotar trades
            for i, trade in enumerate(trades_completos):
                resultado_pct = trade.get('resultado_pct', 0)
                cor = '#00ff88' if resultado_pct > 0 else '#ff4444'
                
                # Linha do trade
                ax.plot([i, i+1], [trade['preco_entrada'], trade['preco_saida']], 
                       color=cor, linewidth=2, alpha=0.7)
                
                # Marcadores
                ax.scatter(i, trade['preco_entrada'], color=cor, s=100, marker='o', 
                          edgecolors='white', linewidth=2, zorder=5)
                ax.scatter(i+1, trade['preco_saida'], color=cor, s=100, marker='s', 
                          edgecolors='white', linewidth=2, zorder=5)
                
                # Anotação do resultado
                ax.annotate(f'{resultado_pct:+.1f}%', 
                           xy=(i+0.5, max(trade['preco_entrada'], trade['preco_saida'])),
                           ha='center', va='bottom', fontsize=8, fontweight='bold', color=cor)
            
            # Configurar gráfico
            ax.set_title('📈 Timeline de Trades - SNE Radar', 
                        fontsize=16, fontweight='bold', color='white')
            ax.set_xlabel('Trade #', fontsize=12, color='white')
            ax.set_ylabel('Preço ($)', fontsize=12, color='white')
            ax.grid(True, alpha=0.3, color='gray')
            ax.tick_params(colors='white')
            
            # Legenda
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#00ff88', label='Trades Lucrativos'),
                Patch(facecolor='#ff4444', label='Trades com Prejuízo')
            ]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
            
            plt.style.use('dark_background')
            plt.tight_layout()
            
            if salvar:
                filename = f"backtest_timeline_{self.config.get('symbol', 'BTC')}.png"
                plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
                plt.close()
                print(f"📊 Gráfico salvo: {filename}")
                return filename
            else:
                plt.show()
                return ""
                
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de timeline: {e}")
            return ""
    
    def gerar_painel_completo(self, salvar: bool = True) -> str:
        """Gera painel completo com todos os gráficos"""
        try:
            print("📊 Gerando painel completo de backtest...")
            
            # Criar figura com subplots
            fig = plt.figure(figsize=(20, 16))
            gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
            
            # 1. Curva de Equity (superior esquerdo)
            ax1 = fig.add_subplot(gs[0, 0])
            self._plot_equity_curve(ax1)
            
            # 2. Distribuição de Retornos (superior direito)
            ax2 = fig.add_subplot(gs[0, 1])
            self._plot_distribuicao_retornos(ax2)
            
            # 3. Timeline de Trades (meio esquerdo)
            ax3 = fig.add_subplot(gs[1, 0])
            self._plot_timeline_trades(ax3)
            
            # 4. Métricas de Performance (meio direito)
            ax4 = fig.add_subplot(gs[1, 1], projection='polar')
            self._plot_metricas_radar(ax4)
            
            # 5. Estatísticas Resumidas (inferior)
            ax5 = fig.add_subplot(gs[2, :])
            self._plot_estatisticas_resumidas(ax5)
            
            # Título geral
            symbol = self.config.get('symbol', 'BTC')
            periodo = f"{self.config.get('start_date', '')} - {self.config.get('end_date', '')}"
            fig.suptitle(f'📊 PAINEL COMPLETO DE BACKTEST - {symbol} | {periodo}', 
                        fontsize=18, fontweight='bold', color='white', y=0.98)
            
            plt.style.use('dark_background')
            
            if salvar:
                filename = f"backtest_painel_completo_{symbol}.png"
                plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
                plt.close()
                print(f"📊 Painel completo salvo: {filename}")
                return filename
            else:
                plt.show()
                return ""
                
        except Exception as e:
            print(f"❌ Erro ao gerar painel completo: {e}")
            return ""
    
    def _plot_equity_curve(self, ax):
        """Subplot da curva de equity"""
        try:
            trades_completos = [t for t in self.trades if 'capital_final' in t]
            if not trades_completos:
                ax.text(0.5, 0.5, 'Sem dados', ha='center', va='center', transform=ax.transAxes)
                return
            
            capital_series = [t['capital_final'] for t in trades_completos]
            timestamps = [t['timestamp'] for t in trades_completos]
            
            ax.plot(timestamps, capital_series, linewidth=2, color='#00ff88')
            ax.axhline(y=self.config.get('capital_inicial', 10000), color='red', 
                      linestyle='--', alpha=0.7)
            ax.set_title('Curva de Equity', fontsize=12, fontweight='bold', color='white')
            ax.set_ylabel('Capital ($)', fontsize=10, color='white')
            ax.grid(True, alpha=0.3)
            ax.tick_params(colors='white')
        except:
            pass
    
    def _plot_distribuicao_retornos(self, ax):
        """Subplot da distribuição de retornos"""
        try:
            trades_completos = [t for t in self.trades if 'resultado_pct' in t]
            if not trades_completos:
                ax.text(0.5, 0.5, 'Sem dados', ha='center', va='center', transform=ax.transAxes)
                return
            
            retornos = [t['resultado_pct'] for t in trades_completos]
            ax.hist(retornos, bins=15, alpha=0.7, color='#00ff88', edgecolor='white')
            ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
            ax.set_title('Distribuição de Retornos', fontsize=12, fontweight='bold', color='white')
            ax.set_xlabel('Retorno (%)', fontsize=10, color='white')
            ax.set_ylabel('Frequência', fontsize=10, color='white')
            ax.grid(True, alpha=0.3)
            ax.tick_params(colors='white')
        except:
            pass
    
    def _plot_timeline_trades(self, ax):
        """Subplot da timeline de trades"""
        try:
            trades_completos = [t for t in self.trades if 'preco_saida' in t]
            if not trades_completos:
                ax.text(0.5, 0.5, 'Sem dados', ha='center', va='center', transform=ax.transAxes)
                return
            
            for i, trade in enumerate(trades_completos):
                resultado_pct = trade.get('resultado_pct', 0)
                cor = '#00ff88' if resultado_pct > 0 else '#ff4444'
                ax.plot([i, i+1], [trade['preco_entrada'], trade['preco_saida']], 
                       color=cor, linewidth=1.5, alpha=0.7)
                ax.scatter(i, trade['preco_entrada'], color=cor, s=50, marker='o')
                ax.scatter(i+1, trade['preco_saida'], color=cor, s=50, marker='s')
            
            ax.set_title('Timeline de Trades', fontsize=12, fontweight='bold', color='white')
            ax.set_xlabel('Trade #', fontsize=10, color='white')
            ax.set_ylabel('Preço ($)', fontsize=10, color='white')
            ax.grid(True, alpha=0.3)
            ax.tick_params(colors='white')
        except:
            pass
    
    def _plot_metricas_radar(self, ax):
        """Subplot das métricas em radar"""
        try:
            if not self.metricas or 'erro' in self.metricas:
                ax.text(0.5, 0.5, 'Sem métricas', ha='center', va='center', transform=ax.transAxes)
                return
            
            categorias = ['Win Rate', 'Retorno', 'Sharpe', 'Profit Factor']
            valores = [
                min(self.metricas.get('win_rate', 0), 100),
                max(min(self.metricas.get('retorno_total', 0) + 50, 100), 0),
                max(min(self.metricas.get('sharpe_ratio', 0) * 20 + 50, 100), 0),
                max(min(self.metricas.get('profit_factor', 0) * 25, 100), 0)
            ]
            valores += valores[:1]
            
            angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
            angles += angles[:1]
            
            ax.plot(angles, valores, 'o-', linewidth=2, color='#00ff88')
            ax.fill(angles, valores, alpha=0.25, color='#00ff88')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categorias, fontsize=10, color='white')
            ax.set_ylim(0, 100)
            ax.set_title('Métricas de Performance', fontsize=12, fontweight='bold', color='white')
            ax.grid(True, alpha=0.3)
        except:
            pass
    
    def _plot_estatisticas_resumidas(self, ax):
        """Subplot das estatísticas resumidas"""
        try:
            if not self.metricas or 'erro' in self.metricas:
                ax.text(0.5, 0.5, 'Sem métricas', ha='center', va='center', transform=ax.transAxes)
                return
            
            stats_text = f"""
📊 RESUMO DE PERFORMANCE

💰 FINANCEIRO:
   Capital Inicial: ${self.metricas.get('capital_inicial', 0):,.2f}
   Capital Final: ${self.metricas.get('capital_final', 0):,.2f}
   Retorno Total: {self.metricas.get('retorno_total', 0):+.2f}%

📈 TRADING:
   Total de Trades: {self.metricas.get('total_trades', 0)}
   Win Rate: {self.metricas.get('win_rate', 0):.1f}%
   Profit Factor: {self.metricas.get('profit_factor', 0):.2f}

⚠️ RISCO:
   Sharpe Ratio: {self.metricas.get('sharpe_ratio', 0):.2f}
   Max Drawdown: {self.metricas.get('max_drawdown', 0):.2f}%
   Volatilidade: {self.metricas.get('retorno_std', 0):.2f}%
"""
            
            ax.text(0.5, 0.5, stats_text, ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='white', fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8, edgecolor='white'))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        except:
            pass


def carregar_resultados_backtest(arquivo: str) -> Optional[Dict]:
    """Carrega resultados de backtest de arquivo JSON"""
    try:
        with open(arquivo, 'r') as f:
            resultados = json.load(f)
        print(f"📂 Resultados carregados: {arquivo}")
        return resultados
    except Exception as e:
        print(f"❌ Erro ao carregar resultados: {e}")
        return None


def visualizar_backtest_completo(arquivo_resultados: str):
    """
    Visualiza resultados completos de backtest
    
    Args:
        arquivo_resultados: Caminho para arquivo JSON com resultados
    """
    try:
        print("📊 INICIANDO VISUALIZAÇÃO DE BACKTEST")
        print("="*50)
        
        # Carregar resultados
        resultados = carregar_resultados_backtest(arquivo_resultados)
        if not resultados:
            return
        
        # Criar visualizador
        visualizador = VisualizadorBacktest(resultados)
        
        # Gerar gráficos individuais
        print("\n📈 Gerando gráficos individuais...")
        visualizador.gerar_grafico_equity_curve()
        visualizador.gerar_grafico_distribuicao_retornos()
        visualizador.gerar_grafico_metricas_performance()
        visualizador.gerar_grafico_trades_timeline()
        
        # Gerar painel completo
        print("\n📊 Gerando painel completo...")
        visualizador.gerar_painel_completo()
        
        print("\n✅ Visualização completa gerada!")
        
    except Exception as e:
        print(f"❌ Erro na visualização: {e}")


if __name__ == "__main__":
    # Exemplo de uso
    visualizar_backtest_completo("backtest_results_BTCUSDT_1h_2024-01-01.json")

