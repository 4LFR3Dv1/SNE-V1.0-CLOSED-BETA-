#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Alertas Inteligentes
Alertas contextuais com análise e recomendações
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from enum import Enum
import pytz

class TipoAlerta(Enum):
    """Tipos de alertas"""
    OPORTUNIDADE_ALTA = "oportunidade_alta"
    OPORTUNIDADE_MEDIA = "oportunidade_media"
    RISCO_ALTO = "risco_alto"
    RUPTURA = "ruptura"
    REVERSAO = "reversao"
    BREAKOUT = "breakout"
    VOLUME_ANOMALO = "volume_anomalo"
    VOLATILIDADE_EXTREMA = "volatilidade_extrema"
    ZONA_CRITICA = "zona_critica"
    DIVERGENCIA = "divergencia"

class PrioridadeAlerta(Enum):
    """Prioridades de alertas"""
    CRITICA = 1
    ALTA = 2
    MEDIA = 3
    BAIXA = 4
    INFO = 5

class AlertaInteligente:
    """Classe para representar um alerta inteligente"""
    
    def __init__(self, tipo: TipoAlerta, prioridade: PrioridadeAlerta,
                 symbol: str, mensagem: str, contexto: Dict[str, Any],
                 recomendacoes: List[str], timestamp: datetime = None):
        self.tipo = tipo
        self.prioridade = prioridade
        self.symbol = symbol
        self.mensagem = mensagem
        self.contexto = contexto
        self.recomendacoes = recomendacoes
        self.timestamp = timestamp or datetime.now()
        self.id = f"{symbol}_{tipo.value}_{int(self.timestamp.timestamp())}"
        self.lido = False
        self.acionado = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte alerta para dicionário"""
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'prioridade': self.prioridade.value,
            'symbol': self.symbol,
            'mensagem': self.mensagem,
            'contexto': self.contexto,
            'recomendacoes': self.recomendacoes,
            'timestamp': self.timestamp.isoformat(),
            'lido': self.lido,
            'acionado': self.acionado
        }
    
    def __str__(self) -> str:
        """Representação em string"""
        emoji = self._get_emoji()
        return f"{emoji} [{self.prioridade.name}] {self.symbol}: {self.mensagem}"
    
    def _get_emoji(self) -> str:
        """Retorna emoji baseado no tipo"""
        emojis = {
            TipoAlerta.OPORTUNIDADE_ALTA: "🔥",
            TipoAlerta.OPORTUNIDADE_MEDIA: "⭐",
            TipoAlerta.RISCO_ALTO: "⚠️",
            TipoAlerta.RUPTURA: "💥",
            TipoAlerta.REVERSAO: "🔄",
            TipoAlerta.BREAKOUT: "🚀",
            TipoAlerta.VOLUME_ANOMALO: "📊",
            TipoAlerta.VOLATILIDADE_EXTREMA: "🌪️",
            TipoAlerta.ZONA_CRITICA: "🎯",
            TipoAlerta.DIVERGENCIA: "📉"
        }
        return emojis.get(self.tipo, "ℹ️")

class SistemaAlertasInteligentes:
    """Sistema de gerenciamento de alertas inteligentes"""
    
    def __init__(self):
        self.br_tz = pytz.timezone("America/Sao_Paulo")
        self.alertas_ativos = []
        self.historico_alertas = []
        self.configuracoes = {
            'min_score_oportunidade': 70,
            'max_risk_level': 'ALTO',
            'min_volume_ratio': 1.5,
            'max_volatility': 'EXTREMA',
            'cooldown_minutos': 15  # Tempo mínimo entre alertas do mesmo tipo
        }
        self.ultimos_alertas = {}  # Para controle de cooldown
    
    def analisar_e_gerar_alertas(self, dados: Dict[str, Any]) -> List[AlertaInteligente]:
        """Analisa dados e gera alertas inteligentes"""
        
        alertas = []
        symbol = dados.get('symbol', 'UNKNOWN')
        
        # 1. Alertas de Oportunidade
        alertas.extend(self._verificar_oportunidades(dados))
        
        # 2. Alertas de Risco
        alertas.extend(self._verificar_riscos(dados))
        
        # 3. Alertas de Padrões
        alertas.extend(self._verificar_padroes(dados))
        
        # 4. Alertas de Volume
        alertas.extend(self._verificar_volume(dados))
        
        # 5. Alertas de Volatilidade
        alertas.extend(self._verificar_volatilidade(dados))
        
        # 6. Alertas de Zonas Críticas
        alertas.extend(self._verificar_zonas_criticas(dados))
        
        # Filtrar alertas por cooldown
        alertas_filtrados = []
        for alerta in alertas:
            if self._pode_enviar_alerta(alerta):
                alertas_filtrados.append(alerta)
                self._registrar_alerta_enviado(alerta)
        
        # Adicionar aos alertas ativos
        self.alertas_ativos.extend(alertas_filtrados)
        
        # Limpar alertas antigos
        self._limpar_alertas_antigos()
        
        return alertas_filtrados
    
    def _verificar_oportunidades(self, dados: Dict[str, Any]) -> List[AlertaInteligente]:
        """Verifica e gera alertas de oportunidades"""
        alertas = []
        
        symbol = dados.get('symbol', 'UNKNOWN')
        score = dados.get('opportunity_score', 0)
        regime = dados.get('market_regime', 'unknown')
        price = dados.get('price', 0)
        
        # Oportunidade Alta
        if score >= 80:
            contexto = {
                'score': score,
                'regime': regime,
                'price': price,
                'trend': dados.get('trend_direction', 'N/A'),
                'risk': dados.get('risk_level', 'N/A')
            }
            
            recomendacoes = [
                f"Considerar entrada em {symbol} com stop loss rigoroso",
                f"Preço atual: ${price:.2f}",
                f"Regime: {regime} - Tendência: {dados.get('trend_direction', 'N/A')}",
                "Monitorar volume e volatilidade antes da entrada",
                "Definir take profit em níveis de resistência"
            ]
            
            alerta = AlertaInteligente(
                tipo=TipoAlerta.OPORTUNIDADE_ALTA,
                prioridade=PrioridadeAlerta.CRITICA,
                symbol=symbol,
                mensagem=f"Oportunidade excepcional detectada! Score {score:.0f}/100",
                contexto=contexto,
                recomendacoes=recomendacoes
            )
            alertas.append(alerta)
        
        # Oportunidade Média
        elif score >= 70:
            contexto = {
                'score': score,
                'regime': regime,
                'price': price
            }
            
            recomendacoes = [
                f"Boa oportunidade em {symbol}",
                f"Aguardar confirmação adicional antes da entrada",
                "Gestão de risco adequada é essencial"
            ]
            
            alerta = AlertaInteligente(
                tipo=TipoAlerta.OPORTUNIDADE_MEDIA,
                prioridade=PrioridadeAlerta.ALTA,
                symbol=symbol,
                mensagem=f"Boa oportunidade detectada. Score {score:.0f}/100",
                contexto=contexto,
                recomendacoes=recomendacoes
            )
            alertas.append(alerta)
        
        return alertas
    
    def _verificar_riscos(self, dados: Dict[str, Any]) -> List[AlertaInteligente]:
        """Verifica e gera alertas de risco"""
        alertas = []
        
        symbol = dados.get('symbol', 'UNKNOWN')
        risk = dados.get('risk_level', 'MÉDIO')
        score = dados.get('opportunity_score', 0)
        
        # Risco Alto com Score Alto (situação perigosa)
        if risk in ['MUITO ALTO', 'ALTO'] and score >= 70:
            contexto = {
                'risk': risk,
                'score': score,
                'volatility': dados.get('volatility_level', 'N/A'),
                'volume': dados.get('volume_profile', 'N/A')
            }
            
            recomendacoes = [
                f"⚠️ ATENÇÃO: {symbol} com risco {risk}",
                "Reduzir tamanho da posição em 50%",
                "Stop loss mais apertado que o normal",
                "Considerar take profit parcial mais cedo",
                "Monitorar constantemente a posição"
            ]
            
            alerta = AlertaInteligente(
                tipo=TipoAlerta.RISCO_ALTO,
                prioridade=PrioridadeAlerta.ALTA,
                symbol=symbol,
                mensagem=f"Alto risco detectado! Risco {risk} com score {score:.0f}",
                contexto=contexto,
                recomendacoes=recomendacoes
            )
            alertas.append(alerta)
        
        return alertas
    
    def _verificar_padroes(self, dados: Dict[str, Any]) -> List[AlertaInteligente]:
        """Verifica padrões de mercado"""
        alertas = []
        
        symbol = dados.get('symbol', 'UNKNOWN')
        regime = dados.get('market_regime', 'unknown')
        trend = dados.get('trend_direction', 'NEUTRO')
        
        # Reversão potencial
        if 'MISTA' in trend and dados.get('opportunity_score', 0) >= 60:
            contexto = {
                'regime': regime,
                'trend': trend,
                'sentiment': dados.get('market_sentiment', 'N/A')
            }
            
            recomendacoes = [
                f"Possível reversão em {symbol}",
                "Aguardar confirmação de direção",
                "Não entrar em posições grandes",
                "Monitorar volume para confirmação"
            ]
            
            alerta = AlertaInteligente(
                tipo=TipoAlerta.REVERSAO,
                prioridade=PrioridadeAlerta.MEDIA,
                symbol=symbol,
                mensagem="Possível reversão de tendência detectada",
                contexto=contexto,
                recomendacoes=recomendacoes
            )
            alertas.append(alerta)
        
        # Breakout potencial
        if regime == 'consolidation' and dados.get('volatility_level') == 'BAIXA':
            contexto = {
                'regime': regime,
                'volatility': dados.get('volatility_level', 'N/A'),
                'price': dados.get('price', 0)
            }
            
            recomendacoes = [
                f"Consolidação em {symbol} - Breakout iminente",
                "Preparar para movimento direcional",
                "Definir ordens de entrada em ambos os lados",
                "Aguardar confirmação de volume"
            ]
            
            alerta = AlertaInteligente(
                tipo=TipoAlerta.BREAKOUT,
                prioridade=PrioridadeAlerta.MEDIA,
                symbol=symbol,
                mensagem="Consolidação detectada - Breakout potencial",
                contexto=contexto,
                recomendacoes=recomendacoes
            )
            alertas.append(alerta)
        
        return alertas
    
    def _verificar_volume(self, dados: Dict[str, Any]) -> List[AlertaInteligente]:
        """Verifica anomalias de volume"""
        alertas = []
        
        symbol = dados.get('symbol', 'UNKNOWN')
        volume_profile = dados.get('volume_profile', 'NORMAL')
        
        if volume_profile == 'EXTREMO':
            contexto = {
                'volume': volume_profile,
                'price': dados.get('price', 0),
                'regime': dados.get('market_regime', 'N/A')
            }
            
            recomendacoes = [
                f"Volume extremo em {symbol}",
                "Possível movimento significativo em curso",
                "Verificar notícias e eventos",
                "Cautela com entrada/saída"
            ]
            
            alerta = AlertaInteligente(
                tipo=TipoAlerta.VOLUME_ANOMALO,
                prioridade=PrioridadeAlerta.ALTA,
                symbol=symbol,
                mensagem="Volume anômalo detectado!",
                contexto=contexto,
                recomendacoes=recomendacoes
            )
            alertas.append(alerta)
        
        return alertas
    
    def _verificar_volatilidade(self, dados: Dict[str, Any]) -> List[AlertaInteligente]:
        """Verifica volatilidade extrema"""
        alertas = []
        
        symbol = dados.get('symbol', 'UNKNOWN')
        volatility = dados.get('volatility_level', 'MÉDIA')
        
        if volatility == 'EXTREMA':
            contexto = {
                'volatility': volatility,
                'risk': dados.get('risk_level', 'N/A'),
                'regime': dados.get('market_regime', 'N/A')
            }
            
            recomendacoes = [
                f"⚠️ Volatilidade extrema em {symbol}",
                "Reduzir tamanho de posição",
                "Stop loss mais amplo para evitar stop hunt",
                "Evitar trading se inexperiente",
                "Oportunidade para traders experientes"
            ]
            
            alerta = AlertaInteligente(
                tipo=TipoAlerta.VOLATILIDADE_EXTREMA,
                prioridade=PrioridadeAlerta.ALTA,
                symbol=symbol,
                mensagem="Volatilidade extrema detectada!",
                contexto=contexto,
                recomendacoes=recomendacoes
            )
            alertas.append(alerta)
        
        return alertas
    
    def _verificar_zonas_criticas(self, dados: Dict[str, Any]) -> List[AlertaInteligente]:
        """Verifica proximidade de zonas críticas"""
        alertas = []
        
        symbol = dados.get('symbol', 'UNKNOWN')
        price = dados.get('price', 0)
        support_resistance = dados.get('support_resistance', {})
        
        if support_resistance:
            support = support_resistance.get('support', 0)
            resistance = support_resistance.get('resistance', 0)
            
            # Próximo ao suporte
            if support and abs(price - support) / price < 0.01:  # Menos de 1% de distância
                contexto = {
                    'price': price,
                    'support': support,
                    'distance_pct': abs(price - support) / price * 100
                }
                
                recomendacoes = [
                    f"Preço próximo ao suporte em ${support:.2f}",
                    "Possível reversão ou quebra",
                    "Aguardar confirmação",
                    "Oportunidade de compra se suporte segurar"
                ]
                
                alerta = AlertaInteligente(
                    tipo=TipoAlerta.ZONA_CRITICA,
                    prioridade=PrioridadeAlerta.MEDIA,
                    symbol=symbol,
                    mensagem=f"Preço próximo ao suporte (${support:.2f})",
                    contexto=contexto,
                    recomendacoes=recomendacoes
                )
                alertas.append(alerta)
            
            # Próximo à resistência
            elif resistance and abs(price - resistance) / price < 0.01:
                contexto = {
                    'price': price,
                    'resistance': resistance,
                    'distance_pct': abs(price - resistance) / price * 100
                }
                
                recomendacoes = [
                    f"Preço próximo à resistência em ${resistance:.2f}",
                    "Possível reversão ou breakout",
                    "Aguardar confirmação",
                    "Considerar take profit se em posição long"
                ]
                
                alerta = AlertaInteligente(
                    tipo=TipoAlerta.ZONA_CRITICA,
                    prioridade=PrioridadeAlerta.MEDIA,
                    symbol=symbol,
                    mensagem=f"Preço próximo à resistência (${resistance:.2f})",
                    contexto=contexto,
                    recomendacoes=recomendacoes
                )
                alertas.append(alerta)
        
        return alertas
    
    def _pode_enviar_alerta(self, alerta: AlertaInteligente) -> bool:
        """Verifica se pode enviar o alerta (cooldown)"""
        chave = f"{alerta.symbol}_{alerta.tipo.value}"
        
        if chave not in self.ultimos_alertas:
            return True
        
        ultimo_envio = self.ultimos_alertas[chave]
        tempo_decorrido = (datetime.now() - ultimo_envio).total_seconds() / 60
        
        return tempo_decorrido >= self.configuracoes['cooldown_minutos']
    
    def _registrar_alerta_enviado(self, alerta: AlertaInteligente):
        """Registra que um alerta foi enviado"""
        chave = f"{alerta.symbol}_{alerta.tipo.value}"
        self.ultimos_alertas[chave] = datetime.now()
    
    def _limpar_alertas_antigos(self, horas: int = 24):
        """Remove alertas antigos"""
        tempo_limite = datetime.now() - timedelta(hours=horas)
        
        # Mover alertas antigos para histórico
        alertas_antigos = [a for a in self.alertas_ativos if a.timestamp < tempo_limite]
        self.historico_alertas.extend(alertas_antigos)
        
        # Manter apenas alertas recentes
        self.alertas_ativos = [a for a in self.alertas_ativos if a.timestamp >= tempo_limite]
        
        # Limitar tamanho do histórico
        if len(self.historico_alertas) > 1000:
            self.historico_alertas = self.historico_alertas[-1000:]
    
    def obter_alertas_ativos(self, apenas_nao_lidos: bool = False) -> List[AlertaInteligente]:
        """Retorna alertas ativos"""
        if apenas_nao_lidos:
            return [a for a in self.alertas_ativos if not a.lido]
        return self.alertas_ativos
    
    def marcar_como_lido(self, alerta_id: str):
        """Marca alerta como lido"""
        for alerta in self.alertas_ativos:
            if alerta.id == alerta_id:
                alerta.lido = True
                break
    
    def marcar_como_acionado(self, alerta_id: str):
        """Marca alerta como acionado (usuário agiu)"""
        for alerta in self.alertas_ativos:
            if alerta.id == alerta_id:
                alerta.acionado = True
                break
    
    def gerar_relatorio_alertas(self) -> str:
        """Gera relatório de alertas"""
        timestamp = datetime.now(self.br_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        alertas_por_prioridade = {}
        for alerta in self.alertas_ativos:
            prioridade = alerta.prioridade.name
            if prioridade not in alertas_por_prioridade:
                alertas_por_prioridade[prioridade] = []
            alertas_por_prioridade[prioridade].append(alerta)
        
        relatorio = f"""
🚨 RELATÓRIO DE ALERTAS INTELIGENTES
{'='*60}
🕰️ Timestamp: {timestamp}
📊 Total de Alertas Ativos: {len(self.alertas_ativos)}
📖 Alertas Não Lidos: {len([a for a in self.alertas_ativos if not a.lido])}

"""
        
        # Alertas por prioridade
        for prioridade in ['CRITICA', 'ALTA', 'MEDIA', 'BAIXA', 'INFO']:
            alertas = alertas_por_prioridade.get(prioridade, [])
            if alertas:
                relatorio += f"\n🔔 {prioridade} ({len(alertas)} alertas):\n"
                for alerta in alertas[:5]:  # Mostrar apenas os 5 primeiros
                    relatorio += f"  {alerta}\n"
                    for rec in alerta.recomendacoes[:2]:
                        relatorio += f"    • {rec}\n"
        
        relatorio += f"\n{'='*60}\n🤖 Relatório gerado automaticamente"
        
        return relatorio

# Função principal para integração
def gerar_alertas_inteligentes(dados: Dict[str, Any]) -> List[AlertaInteligente]:
    """Função principal para gerar alertas"""
    sistema = SistemaAlertasInteligentes()
    return sistema.analisar_e_gerar_alertas(dados)

# Instância global
sistema_alertas_global = SistemaAlertasInteligentes()




