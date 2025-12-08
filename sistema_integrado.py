#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Integrado SNE
Integração de todos os módulos: Multi-Pair, Priorização e Alertas
"""

import time
from datetime import datetime
import pytz
from typing import Dict, List, Any
import matplotlib.pyplot as plt

# Importar todos os sistemas
from multi_pair_context import analisar_mercado_completo
from priorizacao_automatica import priorizador_global
from alertas_inteligentes import sistema_alertas_global
from multi_pair_radar_interface import MultiPairRadarInterface
from xenos_bot import enviar_oraculo

class SistemaIntegradoSNE:
    """Sistema integrado com todos os módulos"""
    
    def __init__(self):
        self.br_tz = pytz.timezone("America/Sao_Paulo")
        self.interface = MultiPairRadarInterface()
        self.priorizador = priorizador_global
        self.sistema_alertas = sistema_alertas_global
        
        # Configurações
        self.intervalo_atualizacao = 30  # segundos
        self.enviar_telegram = True
        self.modo_visual = True
        
        # Estado
        self.ultima_atualizacao = None
        self.ciclos_executados = 0
    
    def iniciar_sistema_completo(self):
        """Inicia o sistema completo integrado"""
        
        print("="*60)
        print("🚀 INICIANDO SISTEMA INTEGRADO SNE")
        print("="*60)
        print(f"📊 Multi-Pair Radar Interface: {'✅' if self.modo_visual else '❌'}")
        print(f"🎯 Sistema de Priorização: ✅")
        print(f"🚨 Sistema de Alertas: ✅")
        print(f"📱 Integração Telegram: {'✅' if self.enviar_telegram else '❌'}")
        print(f"⏱️  Intervalo de Atualização: {self.intervalo_atualizacao}s")
        print("="*60)
        
        # Criar interface se modo visual ativo
        if self.modo_visual:
            self.interface.criar_interface()
            plt.ion()
            plt.show()
        
        # Loop principal
        try:
            while True:
                self._executar_ciclo_completo()
                time.sleep(self.intervalo_atualizacao)
        
        except KeyboardInterrupt:
            print("\n⏹️ Sistema encerrado pelo usuário")
            if self.modo_visual:
                plt.close('all')
    
    def _executar_ciclo_completo(self):
        """Executa um ciclo completo de análise"""
        
        self.ciclos_executados += 1
        timestamp = datetime.now(self.br_tz)
        
        print(f"\n{'='*60}")
        print(f"🔄 CICLO #{self.ciclos_executados} - {timestamp.strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # 1. ANÁLISE MULTI-PAIR
        print("📊 Fase 1: Análise Multi-Pair...")
        resultados, ranking, relatorio_contexto = analisar_mercado_completo()
        print(f"✅ {len(resultados)} pares analisados")
        
        # 2. PRIORIZAÇÃO AUTOMÁTICA
        print("🎯 Fase 2: Priorização Automática...")
        pares_priorizados = self.priorizador.priorizar_pares(resultados)
        print(f"✅ {len(pares_priorizados)} pares priorizados")
        
        # 3. GERAÇÃO DE ALERTAS
        print("🚨 Fase 3: Geração de Alertas Inteligentes...")
        todos_alertas = []
        for par in pares_priorizados[:5]:  # Top 5 pares
            alertas = self.sistema_alertas.analisar_e_gerar_alertas(par)
            todos_alertas.extend(alertas)
        print(f"✅ {len(todos_alertas)} alertas gerados")
        
        # 4. ATUALIZAÇÃO VISUAL
        if self.modo_visual:
            print("🖥️  Fase 4: Atualização Interface Visual...")
            self.interface.atualizar_interface(resultados, pares_priorizados)
            print("✅ Interface atualizada")
        
        # 5. ENVIO TELEGRAM
        if self.enviar_telegram and todos_alertas:
            print("📱 Fase 5: Envio de Alertas Telegram...")
            self._enviar_alertas_telegram(pares_priorizados, todos_alertas)
            print("✅ Alertas enviados")
        
        # 6. RELATÓRIO RESUMIDO
        self._exibir_resumo(pares_priorizados, todos_alertas)
        
        self.ultima_atualizacao = timestamp
    
    def _enviar_alertas_telegram(self, pares_priorizados: List[Dict[str, Any]], 
                                 alertas: List[Any]):
        """Envia alertas importantes para o Telegram"""
        
        # Enviar apenas alertas críticos e de alta prioridade
        alertas_importantes = [a for a in alertas if a.prioridade.value <= 2]
        
        if not alertas_importantes:
            return
        
        # Montar mensagem
        mensagem = f"🚨 <b>ALERTAS IMPORTANTES</b>\n"
        mensagem += f"🕰️ {datetime.now(self.br_tz).strftime('%H:%M:%S')}\n\n"
        
        for alerta in alertas_importantes[:3]:  # Máximo 3 alertas
            mensagem += f"{alerta}\n"
            mensagem += f"📊 Contexto: Score {alerta.contexto.get('score', 0):.0f}\n"
            mensagem += f"💡 {alerta.recomendacoes[0]}\n\n"
        
        # Top 3 prioridades
        mensagem += f"\n🏆 <b>TOP 3 PRIORIDADES:</b>\n"
        for i, par in enumerate(pares_priorizados[:3], 1):
            mensagem += f"{i}. {par['symbol']} - Prioridade {par['priority_score']:.0f}\n"
        
        try:
            enviar_oraculo(mensagem)
        except Exception as e:
            print(f"⚠️ Erro ao enviar Telegram: {e}")
    
    def _exibir_resumo(self, pares_priorizados: List[Dict[str, Any]], alertas: List[Any]):
        """Exibe resumo do ciclo"""
        
        print(f"\n📋 RESUMO DO CICLO:")
        print(f"{'─'*60}")
        
        # Top 3 Prioridades
        print("🏆 TOP 3 PRIORIDADES:")
        for i, par in enumerate(pares_priorizados[:3], 1):
            print(f"  {i}. {par['symbol']:10s} - Prioridade: {par['priority_score']:5.1f} | Score: {par['opportunity_score']:5.1f}")
        
        # Alertas por prioridade
        if alertas:
            print(f"\n🚨 ALERTAS:")
            alertas_por_prioridade = {}
            for alerta in alertas:
                p = alerta.prioridade.name
                alertas_por_prioridade[p] = alertas_por_prioridade.get(p, 0) + 1
            
            for prioridade, count in alertas_por_prioridade.items():
                print(f"  {prioridade}: {count}")
        
        # Estatísticas
        scores = [p['priority_score'] for p in pares_priorizados]
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"  Prioridade Média: {sum(scores)/len(scores):.1f}")
        print(f"  Maior Prioridade: {max(scores):.1f}")
        print(f"  Pares com Alta Prioridade (≥70): {len([s for s in scores if s >= 70])}")
        
        print(f"{'─'*60}")
    
    def configurar(self, intervalo: int = None, telegram: bool = None, visual: bool = None):
        """Configura parâmetros do sistema"""
        if intervalo is not None:
            self.intervalo_atualizacao = intervalo
        if telegram is not None:
            self.enviar_telegram = telegram
        if visual is not None:
            self.modo_visual = visual
    
    def executar_ciclo_unico(self) -> Dict[str, Any]:
        """Executa um único ciclo e retorna resultados"""
        
        # Análise
        resultados, ranking, _ = analisar_mercado_completo()
        
        # Priorização
        pares_priorizados = self.priorizador.priorizar_pares(resultados)
        
        # Alertas
        todos_alertas = []
        for par in pares_priorizados[:5]:
            alertas = self.sistema_alertas.analisar_e_gerar_alertas(par)
            todos_alertas.extend(alertas)
        
        return {
            'resultados': resultados,
            'ranking': ranking,
            'pares_priorizados': pares_priorizados,
            'alertas': todos_alertas,
            'timestamp': datetime.now(self.br_tz)
        }

# Função principal
def iniciar_sistema_integrado(intervalo: int = 30, telegram: bool = True, visual: bool = True):
    """Inicia o sistema integrado completo"""
    sistema = SistemaIntegradoSNE()
    sistema.configurar(intervalo=intervalo, telegram=telegram, visual=visual)
    sistema.iniciar_sistema_completo()

# Instância global
sistema_integrado = SistemaIntegradoSNE()

if __name__ == "__main__":
    # Iniciar sistema com configurações padrão
    iniciar_sistema_integrado(intervalo=30, telegram=True, visual=True)




