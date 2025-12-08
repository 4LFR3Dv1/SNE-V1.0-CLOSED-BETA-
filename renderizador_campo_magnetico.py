#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RENDERIZADOR VISUAL DE CAMPOS MAGNÉTICOS SNE
Sistema de visualização estética para campos magnéticos
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.animation import FuncAnimation
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')


class RenderizadorCampoMagnetico:
    """
    Renderizador visual para campos magnéticos
    
    Cria visualizações estéticas dos campos magnéticos com:
    - Gradientes de densidade
    - Linhas de campo dinâmicas
    - Vetores de força
    - Núcleo pulsante
    """
    
    def __init__(self):
        """Inicializa o renderizador"""
        self.config_visual = {
            'figsize': (16, 12),
            'dpi': 100,
            'estilo': 'dark_background',
            'animacao': True,
            'pulsacao_nucleo': True,
            'gradiente_suave': True
        }
        
        # Paleta de cores magnéticas
        self.paleta_campo = {
            'fundo': '#0a0a0a',
            'polo_atrativo': '#0066ff',
            'polo_repulsivo': '#ff3300',
            'linha_campo': '#ffffff',
            'vetor_forca': '#ffff00',
            'equalizacao': '#ffffff',
            'nucleo': '#ff00ff',
            'grade': '#333333'
        }
        
        # Configurar estilo
        plt.style.use('dark_background')
        
    def renderizar_campo_completo(self, dados_campo: Dict[str, Any], 
                                 salvar: bool = True, mostrar: bool = False) -> str:
        """
        Renderiza campo magnético completo
        
        Args:
            dados_campo: Dados do campo magnético
            salvar: Se deve salvar o arquivo
            mostrar: Se deve mostrar na tela
            
        Returns:
            Caminho do arquivo salvo
        """
        try:
            print("🎨 Renderizando campo magnético...")
            
            if not dados_campo or 'campo_magnetico' not in dados_campo:
                print("❌ Dados de campo inválidos")
                return None
            
            campo = dados_campo['campo_magnetico']
            interpretacao = dados_campo.get('interpretacao', {})
            metadata = dados_campo.get('metadata', {})
            
            # Criar figura com layout especializado
            fig = plt.figure(figsize=self.config_visual['figsize'], 
                           facecolor=self.paleta_campo['fundo'])
            
            # Layout em 5 camadas
            gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], 
                                 width_ratios=[3, 1], hspace=0.3, wspace=0.2)
            
            # Camada 1: Campo magnético principal
            ax_campo = fig.add_subplot(gs[0, :])
            self._renderizar_campo_principal(ax_campo, campo)
            
            # Camada 2: Densidade de campo
            ax_densidade = fig.add_subplot(gs[1, 0])
            self._renderizar_densidade_campo(ax_densidade, campo)
            
            # Camada 3: Interpretação simbólica
            ax_interpretacao = fig.add_subplot(gs[1, 1])
            self._renderizar_interpretacao(ax_interpretacao, interpretacao)
            
            # Camada 4: Polos magnéticos
            ax_polos = fig.add_subplot(gs[2, 0])
            self._renderizar_polos_magneticos(ax_polos, campo)
            
            # Camada 5: Resumo energético
            ax_resumo = fig.add_subplot(gs[2, 1])
            self._renderizar_resumo_energetico(ax_resumo, dados_campo)
            
            # Título principal
            symbol = metadata.get('symbol', 'UNKNOWN')
            timeframe = metadata.get('timeframe', '1h')
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            fig.suptitle(f'🧲 CAMPO MAGNÉTICO SNE - {symbol} ({timeframe})\n{timestamp}', 
                        fontsize=16, color='white', y=0.95)
            
            # Salvar arquivo
            if salvar:
                caminho = self._salvar_campo_magnetico(fig, symbol, timeframe)
                print(f"✅ Campo magnético salvo: {caminho}")
            
            # Mostrar se solicitado
            if mostrar:
                plt.show()
            else:
                plt.close(fig)
            
            return caminho if salvar else None
            
        except Exception as e:
            print(f"❌ Erro ao renderizar campo: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _renderizar_campo_principal(self, ax, campo: Dict[str, Any]):
        """Renderiza o campo magnético principal"""
        try:
            grade_precos = campo['grade_precos']
            densidade = campo['densidade_campo']
            polos = campo['polos']
            nucleo = campo['nucleo']
            
            # Configurar eixo
            ax.set_facecolor(self.paleta_campo['fundo'])
            ax.set_xlim(grade_precos[0], grade_precos[-1])
            ax.set_ylim(-1.2, 1.2)
            
            # Renderizar gradiente de densidade
            if self.config_visual['gradiente_suave']:
                self._renderizar_gradiente_densidade(ax, grade_precos, densidade)
            
            # Renderizar polos magnéticos
            self._renderizar_polos_visuais(ax, polos)
            
            # Renderizar núcleo pulsante
            if self.config_visual['pulsacao_nucleo']:
                self._renderizar_nucleo_pulsante(ax, nucleo)
            
            # Renderizar linhas de campo
            linhas_campo = campo.get('linhas_campo', [])
            self._renderizar_linhas_campo(ax, linhas_campo)
            
            # Configurar visual
            ax.set_title('🧲 Campo Magnético Principal', color='white', fontsize=12)
            ax.set_xlabel('Preço', color='white')
            ax.set_ylabel('Densidade de Campo', color='white')
            ax.grid(True, alpha=0.3, color=self.paleta_campo['grade'])
            ax.tick_params(colors='white')
            
        except Exception as e:
            print(f"❌ Erro ao renderizar campo principal: {e}")
    
    def _renderizar_gradiente_densidade(self, ax, grade_precos: np.ndarray, densidade: np.ndarray):
        """Renderiza gradiente de densidade do campo"""
        try:
            # Criar grade 2D para gradiente
            X = np.linspace(grade_precos[0], grade_precos[-1], len(grade_precos))
            Y = np.linspace(-1, 1, 50)
            X_grid, Y_grid = np.meshgrid(X, Y)
            
            # Interpolar densidade para grade 2D
            Z = np.tile(densidade, (len(Y), 1))
            
            # Criar colormap personalizado
            cores = ['#ff3300', '#ff6600', '#ff9900', '#ffcc00', '#ffff00', 
                    '#ccff00', '#99ff00', '#66ff00', '#33ff00', '#00ff00',
                    '#00ff33', '#00ff66', '#00ff99', '#00ffcc', '#00ffff',
                    '#00ccff', '#0099ff', '#0066ff', '#0033ff', '#0000ff']
            
            cmap = LinearSegmentedColormap.from_list('campo_magnetico', cores)
            
            # Renderizar gradiente
            im = ax.imshow(Z, extent=[grade_precos[0], grade_precos[-1], -1, 1], 
                          cmap=cmap, alpha=0.6, aspect='auto', origin='lower')
            
        except Exception as e:
            print(f"❌ Erro ao renderizar gradiente: {e}")
    
    def _renderizar_polos_visuais(self, ax, polos: List[Dict[str, Any]]):
        """Renderiza polos magnéticos como elementos visuais"""
        try:
            for polo in polos:
                preco = polo['preco']
                tipo = polo['tipo']
                forca = polo['forca']
                
                # Determinar cor e símbolo baseado no tipo
                if 'ATRATIVO' in tipo or polo['direcao'] > 0:
                    cor = self.paleta_campo['polo_atrativo']
                    simbolo = '🔵'
                    tamanho = 100 + (forca * 50)
                else:
                    cor = self.paleta_campo['polo_repulsivo']
                    simbolo = '🔴'
                    tamanho = 100 + (forca * 50)
                
                # Renderizar polo
                ax.scatter(preco, 0, s=tamanho, c=cor, alpha=0.8, 
                          edgecolors='white', linewidth=2, zorder=5)
                
                # Adicionar label
                ax.annotate(f'{simbolo}\n{forca:.2f}', 
                           xy=(preco, 0), xytext=(preco, 0.5),
                           ha='center', va='bottom', color='white', fontsize=8,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor=cor, alpha=0.7))
                
        except Exception as e:
            print(f"❌ Erro ao renderizar polos: {e}")
    
    def _renderizar_nucleo_pulsante(self, ax, nucleo: Dict[str, Any]):
        """Renderiza núcleo de equilíbrio pulsante"""
        try:
            preco = nucleo['preco']
            forca = nucleo['forca']
            
            # Criar círculo pulsante
            circulo = patches.Circle((preco, 0), radius=0.1, 
                                    facecolor=self.paleta_campo['nucleo'], 
                                    alpha=0.7, edgecolor='white', linewidth=2)
            ax.add_patch(circulo)
            
            # Adicionar label do núcleo
            ax.annotate('⚡ NÚCLEO', xy=(preco, 0), xytext=(preco, -0.8),
                       ha='center', va='top', color='white', fontsize=10,
                       bbox=dict(boxstyle='round,pad=0.5', 
                                facecolor=self.paleta_campo['nucleo'], alpha=0.8))
            
        except Exception as e:
            print(f"❌ Erro ao renderizar núcleo: {e}")
    
    def _renderizar_linhas_campo(self, ax, linhas_campo: List[Dict[str, Any]]):
        """Renderiza linhas de campo entre polos"""
        try:
            for linha in linhas_campo:
                polo_inicio = linha['polo_inicio']
                polo_fim = linha['polo_fim']
                intensidade = linha['intensidade']
                
                # Calcular pontos da linha de campo
                x_inicio = polo_inicio['preco']
                x_fim = polo_fim['preco']
                
                # Criar linha curva usando spline
                x_linha = np.linspace(x_inicio, x_fim, 50)
                y_linha = np.sin(np.linspace(0, np.pi, 50)) * 0.3
                
                # Renderizar linha
                ax.plot(x_linha, y_linha, color=self.paleta_campo['linha_campo'], 
                       alpha=0.6, linewidth=intensidade * 2, zorder=3)
                
                # Adicionar setas indicando direção
                ax.annotate('', xy=(x_linha[-1], y_linha[-1]), 
                           xytext=(x_linha[-2], y_linha[-2]),
                           arrowprops=dict(arrowstyle='->', 
                                         color=self.paleta_campo['linha_campo'],
                                         alpha=0.8))
                
        except Exception as e:
            print(f"❌ Erro ao renderizar linhas de campo: {e}")
    
    def _renderizar_densidade_campo(self, ax, campo: Dict[str, Any]):
        """Renderiza gráfico de densidade de campo"""
        try:
            grade_precos = campo['grade_precos']
            densidade = campo['densidade_campo']
            
            ax.set_facecolor(self.paleta_campo['fundo'])
            
            # Plotar densidade
            ax.plot(grade_precos, densidade, color=self.paleta_campo['linha_campo'], 
                   linewidth=2, alpha=0.8)
            
            # Preenchimento colorido
            ax.fill_between(grade_precos, densidade, alpha=0.3, 
                           color=self.paleta_campo['polo_atrativo'] if np.mean(densidade) > 0 
                           else self.paleta_campo['polo_repulsivo'])
            
            ax.set_title('📊 Densidade de Campo', color='white', fontsize=10)
            ax.set_xlabel('Preço', color='white')
            ax.set_ylabel('Densidade', color='white')
            ax.grid(True, alpha=0.3)
            ax.tick_params(colors='white')
            
        except Exception as e:
            print(f"❌ Erro ao renderizar densidade: {e}")
    
    def _renderizar_interpretacao(self, ax, interpretacao: Dict[str, Any]):
        """Renderiza interpretação simbólica"""
        try:
            ax.set_facecolor(self.paleta_campo['fundo'])
            ax.axis('off')
            
            # Título
            ax.text(0.5, 0.95, '🧠 Interpretação Simbólica', 
                   ha='center', va='top', color='white', fontsize=10, weight='bold')
            
            # Eventos detectados
            eventos = interpretacao.get('eventos_detectados', [])
            y_pos = 0.85
            
            for evento in eventos[:5]:  # Máximo 5 eventos
                ax.text(0.05, y_pos, f"• {evento}", ha='left', va='top', 
                       color='yellow', fontsize=8)
                y_pos -= 0.12
            
            # Score de confluência
            score = interpretacao.get('score_confluencia', 0)
            ax.text(0.5, 0.2, f'Score: {score:.1f}/10', ha='center', va='center',
                   color='white', fontsize=12, weight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='blue', alpha=0.7))
            
        except Exception as e:
            print(f"❌ Erro ao renderizar interpretação: {e}")
    
    def _renderizar_polos_magneticos(self, ax, campo: Dict[str, Any]):
        """Renderiza lista detalhada de polos magnéticos"""
        try:
            ax.set_facecolor(self.paleta_campo['fundo'])
            ax.axis('off')
            
            polos = campo.get('polos', [])
            
            # Título
            ax.text(0.5, 0.95, f'🧲 Polos Magnéticos ({len(polos)})', 
                   ha='center', va='top', color='white', fontsize=10, weight='bold')
            
            # Listar polos
            y_pos = 0.85
            for i, polo in enumerate(polos[:8]):  # Máximo 8 polos
                tipo = polo['tipo']
                preco = polo['preco']
                forca = polo['forca']
                
                # Cor baseada no tipo
                cor = self.paleta_campo['polo_atrativo'] if polo['direcao'] > 0 else self.paleta_campo['polo_repulsivo']
                
                ax.text(0.05, y_pos, f"{i+1}. {tipo}", ha='left', va='top', 
                       color=cor, fontsize=8)
                ax.text(0.6, y_pos, f"${preco:.2f}", ha='left', va='top', 
                       color='white', fontsize=8)
                ax.text(0.85, y_pos, f"{forca:.2f}", ha='left', va='top', 
                       color='yellow', fontsize=8)
                
                y_pos -= 0.1
            
        except Exception as e:
            print(f"❌ Erro ao renderizar polos: {e}")
    
    def _renderizar_resumo_energetico(self, ax, dados_campo: Dict[str, Any]):
        """Renderiza resumo energético do campo"""
        try:
            ax.set_facecolor(self.paleta_campo['fundo'])
            ax.axis('off')
            
            resumo = dados_campo.get('resumo', {})
            campo = dados_campo.get('campo_magnetico', {})
            
            # Título
            ax.text(0.5, 0.95, '⚡ Resumo Energético', 
                   ha='center', va='top', color='white', fontsize=10, weight='bold')
            
            # Métricas
            y_pos = 0.8
            
            metricas = [
                ('Polos', resumo.get('polos_detectados', 0)),
                ('Intensidade', f"{resumo.get('intensidade_total', 0):.2f}"),
                ('Polaridade', resumo.get('polaridade_dominante', 'NEUTRA')),
                ('Score', f"{resumo.get('score_confluencia', 0):.1f}"),
                ('Recomendação', resumo.get('recomendacao', 'NEUTRO'))
            ]
            
            for metrica, valor in metricas:
                ax.text(0.05, y_pos, f"{metrica}:", ha='left', va='top', 
                       color='white', fontsize=8, weight='bold')
                ax.text(0.5, y_pos, f"{valor}", ha='left', va='top', 
                       color='yellow', fontsize=8)
                y_pos -= 0.12
            
        except Exception as e:
            print(f"❌ Erro ao renderizar resumo: {e}")
    
    def _salvar_campo_magnetico(self, fig, symbol: str, timeframe: str) -> str:
        """Salva o campo magnético renderizado"""
        try:
            import os
            
            # Criar diretório se não existir
            diretorio = "reports/campo_magnetico/"
            os.makedirs(diretorio, exist_ok=True)
            
            # Nome do arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol}_{timeframe}_{timestamp}_campo_magnetico.png"
            caminho = os.path.join(diretorio, filename)
            
            # Salvar com alta qualidade
            fig.savefig(caminho, dpi=self.config_visual['dpi'], 
                       facecolor=self.paleta_campo['fundo'], 
                       edgecolor='none', bbox_inches='tight')
            
            return caminho
            
        except Exception as e:
            print(f"❌ Erro ao salvar campo magnético: {e}")
            return None


def renderizar_campo_magnetico_sne(dados_campo: Dict[str, Any], 
                                 salvar: bool = True, mostrar: bool = False) -> str:
    """
    Função principal para renderizar campo magnético
    
    Args:
        dados_campo: Dados do campo magnético
        salvar: Se deve salvar o arquivo
        mostrar: Se deve mostrar na tela
        
    Returns:
        Caminho do arquivo salvo
    """
    try:
        renderizador = RenderizadorCampoMagnetico()
        return renderizador.renderizar_campo_completo(dados_campo, salvar, mostrar)
        
    except Exception as e:
        print(f"❌ Erro ao renderizar campo magnético: {e}")
        return None


if __name__ == "__main__":
    # Teste do renderizador
    print("🎨 TESTANDO RENDERIZADOR DE CAMPOS MAGNÉTICOS")
    print("=" * 50)
    
    # Dados de teste
    dados_teste = {
        'metadata': {'symbol': 'BTCUSDT', 'timeframe': '1h'},
        'campo_magnetico': {
            'grade_precos': np.linspace(100000, 110000, 100),
            'densidade_campo': np.sin(np.linspace(0, 4*np.pi, 100)) * 0.5,
            'polos': [
                {'preco': 105000, 'tipo': 'EQUAL_HIGH', 'direcao': -1, 'forca': 0.8},
                {'preco': 102000, 'tipo': 'EQUAL_LOW', 'direcao': 1, 'forca': 0.6}
            ],
            'nucleo': {'preco': 103500, 'forca': 0.1}
        },
        'interpretacao': {
            'eventos_detectados': ['COMPRESSAO_INTENSA', 'EQUALIZACAO'],
            'score_confluencia': 7.5
        },
        'resumo': {
            'polos_detectados': 2,
            'intensidade_total': 1.4,
            'polaridade_dominante': 'ATRATIVA',
            'score_confluencia': 7.5,
            'recomendacao': 'ALTA_CONFLUENCIA'
        }
    }
    
    caminho = renderizar_campo_magnetico_sne(dados_teste, salvar=True, mostrar=False)
    
    if caminho:
        print(f"✅ Campo magnético renderizado: {caminho}")
    else:
        print("❌ Erro ao renderizar campo magnético")
