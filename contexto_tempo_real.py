#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Análise de Contexto em Tempo Real
Integração com o radar principal para análise contínua
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import pytz
from contexto_mercado import analise_rapida_contexto, analisar_contexto_mercado
from multi_pair_context import analisar_mercado_completo
import threading
import time

class ContextoTempoReal:
    """Sistema de análise de contexto em tempo real"""
    
    def __init__(self):
        self.br_tz = pytz.timezone("America/Sao_Paulo")
        self.contexto_atual = {}
        self.ranking_atual = []
        self.ultima_analise = None
        self.analise_thread = None
        self.ativo = False
        
        # Configurações
        self.intervalo_analise = 30  # segundos
        self.pares_principais = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.threshold_oportunidade = 70
        
    def iniciar_analise_tempo_real(self):
        """Inicia análise em tempo real"""
        if self.ativo:
            print("⚠️ Análise em tempo real já está ativa")
            return
        
        self.ativo = True
        self.analise_thread = threading.Thread(target=self._loop_analise, daemon=True)
        self.analise_thread.start()
        print("🚀 Análise de contexto em tempo real iniciada")
    
    def parar_analise_tempo_real(self):
        """Para análise em tempo real"""
        self.ativo = False
        if self.analise_thread:
            self.analise_thread.join(timeout=5)
        print("⏹️ Análise de contexto em tempo real parada")
    
    def _loop_analise(self):
        """Loop principal de análise"""
        while self.ativo:
            try:
                print(f"🔄 Executando análise de contexto... {datetime.now().strftime('%H:%M:%S')}")
                
                # Análise completa do mercado
                resultados, ranking, relatorio = analisar_mercado_completo()
                
                # Atualizar estado
                self.contexto_atual = resultados
                self.ranking_atual = ranking
                self.ultima_analise = datetime.now()
                
                # Verificar oportunidades críticas
                self._verificar_oportunidades_criticas(ranking)
                
                print(f"✅ Análise concluída - {len(ranking)} pares analisados")
                
            except Exception as e:
                print(f"❌ Erro na análise: {e}")
            
            # Aguardar próximo ciclo
            time.sleep(self.intervalo_analise)
    
    def _verificar_oportunidades_criticas(self, ranking: List[Dict[str, Any]]):
        """Verifica oportunidades críticas e envia alertas"""
        
        # Top 3 oportunidades com score alto
        oportunidades_alta = [par for par in ranking[:3] if par['score'] >= self.threshold_oportunidade]
        
        if oportunidades_alta:
            print(f"🎯 {len(oportunidades_alta)} oportunidades críticas detectadas!")
            
            for par in oportunidades_alta:
                print(f"🔥 {par['symbol']} - Score: {par['score']:.1f} - {par['regime']}")
                
                # Aqui você pode integrar com o sistema de alertas
                # enviar_alerta_oportunidade(par)
    
    def obter_contexto_atual(self, symbol: str = None) -> Dict[str, Any]:
        """Obtém contexto atual do mercado"""
        
        if not self.contexto_atual:
            return {"erro": "Nenhuma análise disponível"}
        
        if symbol:
            return self.contexto_atual.get(symbol, {"erro": f"Par {symbol} não encontrado"})
        
        return {
            "timestamp": self.ultima_analise,
            "total_pares": len(self.contexto_atual),
            "ranking": self.ranking_atual[:5],  # Top 5
            "melhor_oportunidade": self.ranking_atual[0] if self.ranking_atual else None
        }
    
    def obter_ranking_atual(self) -> List[Dict[str, Any]]:
        """Obtém ranking atual de oportunidades"""
        return self.ranking_atual
    
    def obter_analise_par(self, symbol: str) -> Dict[str, Any]:
        """Obtém análise específica de um par"""
        return self.contexto_atual.get(symbol, {})
    
    def gerar_resumo_executivo(self) -> str:
        """Gera resumo executivo do mercado atual"""
        
        if not self.ranking_atual:
            return "❌ Nenhuma análise disponível"
        
        timestamp = datetime.now(self.br_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        # Estatísticas gerais
        scores = [par['score'] for par in self.ranking_atual]
        avg_score = np.mean(scores)
        max_score = max(scores)
        
        # Top 3 oportunidades
        top3 = self.ranking_atual[:3]
        
        resumo = f"""
🧠 RESUMO EXECUTIVO DO MERCADO
{'='*50}
🕰️ Timestamp: {timestamp}
📊 Total de Pares: {len(self.ranking_atual)}
📈 Score Médio: {avg_score:.1f}/100
🏆 Melhor Oportunidade: {max_score:.1f}/100

🏆 TOP 3 OPORTUNIDADES:
"""
        
        for i, par in enumerate(top3, 1):
            resumo += f"""
{i}. {par['symbol']} - Score: {par['score']:.1f}
   💰 Preço: ${par['price']:.2f} ({par['price_change']:+.2f}%)
   📊 Regime: {par['regime']} | Risco: {par['risk']}
   🎯 {par['interpretation'][:80]}...
"""
        
        # Análise de mercado
        if avg_score >= 70:
            resumo += "\n🔥 MERCADO MUITO ATIVO - Múltiplas oportunidades detectadas"
        elif avg_score >= 50:
            resumo += "\n📈 MERCADO MODERADO - Algumas oportunidades presentes"
        else:
            resumo += "\n😴 MERCADO ADORMECIDO - Poucas oportunidades significativas"
        
        return resumo

# Instância global para uso no radar
contexto_global = ContextoTempoReal()

def iniciar_contexto_tempo_real():
    """Inicia análise de contexto em tempo real"""
    contexto_global.iniciar_analise_tempo_real()

def parar_contexto_tempo_real():
    """Para análise de contexto em tempo real"""
    contexto_global.parar_analise_tempo_real()

def obter_contexto_atual(symbol: str = None) -> Dict[str, Any]:
    """Obtém contexto atual"""
    return contexto_global.obter_contexto_atual(symbol)

def obter_ranking_atual() -> List[Dict[str, Any]]:
    """Obtém ranking atual"""
    return contexto_global.obter_ranking_atual()

def obter_resumo_executivo() -> str:
    """Obtém resumo executivo"""
    return contexto_global.gerar_resumo_executivo()

# Função para integração com o radar principal
def analisar_contexto_radar(symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
    """Análise de contexto para integração com o radar"""
    
    try:
        # Análise rápida do par atual
        contexto_par = analise_rapida_contexto(symbol, df)
        
        # Obter contexto global se disponível
        contexto_global_data = obter_contexto_atual()
        
        # Combinar análises
        resultado = {
            'par_atual': contexto_par,
            'contexto_global': contexto_global_data,
            'timestamp': datetime.now().isoformat(),
            'recomendacao': _gerar_recomendacao_integrada(contexto_par, contexto_global_data)
        }
        
        return resultado
        
    except Exception as e:
        return {
            'erro': f"Falha na análise de contexto: {e}",
            'timestamp': datetime.now().isoformat()
        }

def _gerar_recomendacao_integrada(contexto_par: Dict[str, Any], contexto_global: Dict[str, Any]) -> str:
    """Gera recomendação integrada baseada no contexto local e global"""
    
    score_par = contexto_par.get('opportunity_score', 0)
    regime_par = contexto_par.get('market_regime', 'unknown')
    risco_par = contexto_par.get('risk_level', 'unknown')
    
    # Análise do contexto global
    melhor_global = contexto_global.get('melhor_oportunidade', {})
    score_global = melhor_global.get('score', 0) if melhor_global else 0
    
    # Gerar recomendação
    if score_par >= 80:
        return f"🔥 OPORTUNIDADE EXCEPCIONAL - {regime_par.upper()} com score {score_par:.1f}"
    elif score_par >= 70:
        return f"📈 BOA OPORTUNIDADE - {regime_par.upper()} com score {score_par:.1f}"
    elif score_par >= 50:
        return f"⚠️ OPORTUNIDADE MODERADA - {regime_par.upper()} com score {score_par:.1f}"
    else:
        return f"😴 OPORTUNIDADE BAIXA - {regime_par.upper()} com score {score_par:.1f}"




