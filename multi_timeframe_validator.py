#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Timeframe Validator - SNE Radar
Sistema de validação de sinais, detecção de divergências e critérios de qualidade
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class MultiTimeframeValidator:
    """Sistema de validação multi-timeframe para SNE Radar"""
    
    def __init__(self):
        # Configuração dos timeframes com pesos
        self.timeframes_config = {
            "1m": {"interval": "1m", "limit": 100, "weight": 0.15, "name": "Tempo Real"},
            "5m": {"interval": "5m", "limit": 100, "weight": 0.20, "name": "Curto Prazo"},
            "15m": {"interval": "15m", "limit": 100, "weight": 0.25, "name": "Médio Prazo"},
            "1h": {"interval": "1h", "limit": 100, "weight": 0.20, "name": "Médio-Longo Prazo"},
            "4h": {"interval": "4h", "limit": 100, "weight": 0.15, "name": "Longo Prazo"},
            "1d": {"interval": "1d", "limit": 100, "weight": 0.05, "name": "Tendência Principal"}
        }
        
        # Critérios de qualidade por tipo de sinal
        self.quality_criteria = {
            "compra": {
                "min_score_bullish": 65,
                "min_timeframes_bullish": 3,
                "max_divergencia": 25,
                "min_volume_confirmation": 1.2,
                "max_rsi_overbought": 75,
                "min_trend_alignment": 2
            },
            "venda": {
                "min_score_bearish": 65,
                "min_timeframes_bearish": 3,
                "max_divergencia": 25,
                "min_volume_confirmation": 1.2,
                "min_rsi_oversold": 25,
                "min_trend_alignment": 2
            },
            "aguardar": {
                "max_score_any": 45,
                "max_timeframes_any": 2,
                "min_divergencia": 40
            }
        }
        
        # Histórico de validações para análise
        self.validation_history = {}
    
    def calcular_score_timeframe(self, df, timeframe):
        """Calcula score de 0-100 para um timeframe específico"""
        try:
            if df is None or df.empty:
                return {"score": 0, "tendencia": "neutral", "confianca": 0}
            
            score = 0
            confianca = 0
            
            # Análise de tendência (40% do score)
            ema8 = float(df["EMA8"].iloc[-1])
            ema21 = float(df["EMA21"].iloc[-1])
            sma200 = float(df["SMA200"].iloc[-1])
            
            if ema8 > ema21 > sma200:
                score += 40
                confianca += 20
            elif ema8 < ema21 < sma200:
                score += 0
                confianca += 20
            elif ema8 > ema21 and ema21 < sma200:
                score += 20
                confianca += 10
            elif ema8 < ema21 and ema21 > sma200:
                score += 10
                confianca += 10
            
            # Análise de momentum (30% do score)
            rsi = float(df["rsi"].iloc[-1]) if "rsi" in df.columns else 50
            if rsi > 50 and rsi < 70:
                score += 30
                confianca += 15
            elif rsi > 30 and rsi < 50:
                score += 15
                confianca += 10
            elif rsi > 70:
                score += 10
                confianca += 5
            elif rsi < 30:
                score += 5
                confianca += 5
            
            # Análise de volume (20% do score)
            volume_ratio = float(df["volume_ratio"].iloc[-1]) if "volume_ratio" in df.columns else 1
            if volume_ratio > 1.5:
                score += 20
                confianca += 15
            elif volume_ratio > 1.2:
                score += 15
                confianca += 10
            elif volume_ratio > 0.8:
                score += 10
                confianca += 5
            else:
                score += 5
                confianca += 2
            
            # Análise de volatilidade (10% do score)
            volatilidade = float(df["volatilidade"].iloc[-1]) if "volatilidade" in df.columns else 0
            if volatilidade < 3:
                score += 10
                confianca += 5
            elif volatilidade < 5:
                score += 8
                confianca += 4
            elif volatilidade < 10:
                score += 5
                confianca += 3
            else:
                score += 2
                confianca += 1
            
            # Determinar tendência
            if score >= 70:
                tendencia = "bullish"
            elif score >= 40:
                tendencia = "neutral"
            else:
                tendencia = "bearish"
            
            return {
                "score": score,
                "tendencia": tendencia,
                "confianca": confianca,
                "timeframe": timeframe,
                "ema8": ema8,
                "ema21": ema21,
                "sma200": sma200,
                "rsi": rsi,
                "volume_ratio": volume_ratio,
                "volatilidade": volatilidade
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular score para {timeframe}: {e}")
            return {"score": 0, "tendencia": "neutral", "confianca": 0, "timeframe": timeframe}
    
    def calcular_concordancia_multitimeframe(self, symbol, dados_timeframes):
        """Calcula concordância entre múltiplos timeframes"""
        try:
            scores = {
                "bullish": 0,
                "bearish": 0,
                "neutral": 0
            }
            
            timeframes_analysis = {}
            total_weight = 0
            
            for timeframe, config in self.timeframes_config.items():
                if timeframe in dados_timeframes and dados_timeframes[timeframe] is not None:
                    df = dados_timeframes[timeframe]
                    analysis = self.calcular_score_timeframe(df, timeframe)
                    
                    timeframes_analysis[timeframe] = analysis
                    scores[analysis["tendencia"]] += config["weight"] * 100
                    total_weight += config["weight"]
            
            if total_weight == 0:
                return {
                    "score_bullish": 0,
                    "score_bearish": 0,
                    "tendencia_dominante": "neutral",
                    "forca_sinal": 0,
                    "concordancia": "BAIXA",
                    "timeframes_analysis": timeframes_analysis,
                    "total_timeframes": len(timeframes_analysis)
                }
            
            # Normalizar scores
            for tendencia in scores:
                scores[tendencia] = scores[tendencia] / total_weight
            
            tendencia_dominante = max(scores, key=scores.get)
            forca_sinal = max(scores.values())
            
            # Determinar nível de concordância
            if forca_sinal >= 70:
                concordancia = "ALTA"
            elif forca_sinal >= 50:
                concordancia = "MÉDIA"
            else:
                concordancia = "BAIXA"
            
            return {
                "score_bullish": scores["bullish"],
                "score_bearish": scores["bearish"],
                "tendencia_dominante": tendencia_dominante,
                "forca_sinal": forca_sinal,
                "concordancia": concordancia,
                "timeframes_analysis": timeframes_analysis,
                "total_timeframes": len(timeframes_analysis),
                "scores_detalhados": scores
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular concordância para {symbol}: {e}")
            return {
                "score_bullish": 0,
                "score_bearish": 0,
                "tendencia_dominante": "neutral",
                "forca_sinal": 0,
                "concordancia": "BAIXA",
                "timeframes_analysis": {},
                "total_timeframes": 0
            }
    
    def detectar_divergencias(self, timeframes_analysis):
        """Detecta divergências entre timeframes"""
        try:
            divergencias = []
            tendencias = {}
            
            # Coletar tendências por timeframe
            for timeframe, analysis in timeframes_analysis.items():
                if analysis and "tendencia" in analysis:
                    tendencias[timeframe] = analysis["tendencia"]
            
            # Detectar divergências
            bullish_timeframes = [tf for tf, tendencia in tendencias.items() if tendencia == "bullish"]
            bearish_timeframes = [tf for tf, tendencia in tendencias.items() if tendencia == "bearish"]
            neutral_timeframes = [tf for tf, tendencia in tendencias.items() if tendencia == "neutral"]
            
            # Divergência: timeframes curtos vs longos
            timeframes_curtos = ["1m", "5m", "15m"]
            timeframes_longos = ["1h", "4h", "1d"]
            
            tendencia_curtos = [tendencias.get(tf, "neutral") for tf in timeframes_curtos if tf in tendencias]
            tendencia_longos = [tendencias.get(tf, "neutral") for tf in timeframes_longos if tf in tendencias]
            
            if tendencia_curtos and tendencia_longos:
                # Verificar divergência curto vs longo prazo
                if len(set(tendencia_curtos)) > 1 or len(set(tendencia_longos)) > 1:
                    divergencias.append({
                        "tipo": "DIVERGÊNCIA TEMPORAL",
                        "descricao": "Timeframes de diferentes períodos mostram tendências conflitantes",
                        "severidade": "ALTA",
                        "timeframes_curtos": tendencia_curtos,
                        "timeframes_longos": tendencia_longos
                    })
                
                # Verificar divergência entre curto e longo prazo
                if len(set(tendencia_curtos)) == 1 and len(set(tendencia_longos)) == 1:
                    if tendencia_curtos[0] != tendencia_longos[0]:
                        divergencias.append({
                            "tipo": "DIVERGÊNCIA CURTO-LONGO PRAZO",
                            "descricao": f"Curto prazo: {tendencia_curtos[0]}, Longo prazo: {tendencia_longos[0]}",
                            "severidade": "MÉDIA",
                            "recomendacao": "Aguardar alinhamento ou usar timeframes intermediários"
                        })
            
            # Divergência de força
            scores = [analysis.get("score", 0) for analysis in timeframes_analysis.values() if analysis]
            if scores:
                score_max = max(scores)
                score_min = min(scores)
                if score_max - score_min > 40:
                    divergencias.append({
                        "tipo": "DIVERGÊNCIA DE FORÇA",
                        "descricao": f"Diferença significativa de força entre timeframes ({score_min}-{score_max})",
                        "severidade": "MÉDIA",
                        "score_max": score_max,
                        "score_min": score_min
                    })
            
            return divergencias
            
        except Exception as e:
            print(f"❌ Erro ao detectar divergências: {e}")
            return []
    
    def validar_sinal_multitimeframe(self, symbol, sinal_tipo, dados_timeframes):
        """Valida se um sinal é confiável baseado em múltiplos timeframes"""
        try:
            # Calcular concordância
            concordancia = self.calcular_concordancia_multitimeframe(symbol, dados_timeframes)
            
            # Detectar divergências
            divergencias = self.detectar_divergencias(concordancia["timeframes_analysis"])
            
            # Aplicar critérios de qualidade
            criterios = self.quality_criteria.get(sinal_tipo, {})
            
            # Validação básica
            validacao = {
                "sinal_tipo": sinal_tipo,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "concordancia": concordancia,
                "divergencias": divergencias,
                "criterios_atendidos": [],
                "criterios_falhados": [],
                "valido": False,
                "confianca": 0,
                "recomendacao": "",
                "score_final": 0
            }
            
            # Verificar critérios específicos
            if sinal_tipo == "compra":
                # Score bullish mínimo
                if concordancia["score_bullish"] >= criterios["min_score_bullish"]:
                    validacao["criterios_atendidos"].append("score_bullish")
                    validacao["score_final"] += 30
                else:
                    validacao["criterios_falhados"].append(f"score_bullish (atual: {concordancia['score_bullish']:.1f}, mínimo: {criterios['min_score_bullish']})")
                
                # Número mínimo de timeframes bullish
                bullish_count = sum(1 for analysis in concordancia["timeframes_analysis"].values() 
                                  if analysis and analysis.get("tendencia") == "bullish")
                if bullish_count >= criterios["min_timeframes_bullish"]:
                    validacao["criterios_atendidos"].append("timeframes_bullish")
                    validacao["score_final"] += 25
                else:
                    validacao["criterios_falhados"].append(f"timeframes_bullish (atual: {bullish_count}, mínimo: {criterios['min_timeframes_bullish']})")
                
                # Concordância
                if concordancia["concordancia"] in ["ALTA", "MÉDIA"]:
                    validacao["criterios_atendidos"].append("concordancia")
                    validacao["score_final"] += 20
                else:
                    validacao["criterios_falhados"].append("concordancia")
                
                # Volume confirmation
                volume_ok = False
                for analysis in concordancia["timeframes_analysis"].values():
                    if analysis and analysis.get("volume_ratio", 0) >= criterios["min_volume_confirmation"]:
                        volume_ok = True
                        break
                
                if volume_ok:
                    validacao["criterios_atendidos"].append("volume_confirmation")
                    validacao["score_final"] += 15
                else:
                    validacao["criterios_falhados"].append("volume_confirmation")
                
                # RSI não sobrecomprado
                rsi_ok = True
                for analysis in concordancia["timeframes_analysis"].values():
                    if analysis and analysis.get("rsi", 50) > criterios["max_rsi_overbought"]:
                        rsi_ok = False
                        break
                
                if rsi_ok:
                    validacao["criterios_atendidos"].append("rsi_ok")
                    validacao["score_final"] += 10
                else:
                    validacao["criterios_falhados"].append("rsi_overbought")
            
            elif sinal_tipo == "venda":
                # Score bearish mínimo
                if concordancia["score_bearish"] >= criterios["min_score_bearish"]:
                    validacao["criterios_atendidos"].append("score_bearish")
                    validacao["score_final"] += 30
                else:
                    validacao["criterios_falhados"].append(f"score_bearish (atual: {concordancia['score_bearish']:.1f}, mínimo: {criterios['min_score_bearish']})")
                
                # Número mínimo de timeframes bearish
                bearish_count = sum(1 for analysis in concordancia["timeframes_analysis"].values() 
                                  if analysis and analysis.get("tendencia") == "bearish")
                if bearish_count >= criterios["min_timeframes_bearish"]:
                    validacao["criterios_atendidos"].append("timeframes_bearish")
                    validacao["score_final"] += 25
                else:
                    validacao["criterios_falhados"].append(f"timeframes_bearish (atual: {bearish_count}, mínimo: {criterios['min_timeframes_bearish']})")
                
                # Concordância
                if concordancia["concordancia"] in ["ALTA", "MÉDIA"]:
                    validacao["criterios_atendidos"].append("concordancia")
                    validacao["score_final"] += 20
                else:
                    validacao["criterios_falhados"].append("concordancia")
                
                # Volume confirmation
                volume_ok = False
                for analysis in concordancia["timeframes_analysis"].values():
                    if analysis and analysis.get("volume_ratio", 0) >= criterios["min_volume_confirmation"]:
                        volume_ok = True
                        break
                
                if volume_ok:
                    validacao["criterios_atendidos"].append("volume_confirmation")
                    validacao["score_final"] += 15
                else:
                    validacao["criterios_falhados"].append("volume_confirmation")
                
                # RSI não sobrevendido
                rsi_ok = True
                for analysis in concordancia["timeframes_analysis"].values():
                    if analysis and analysis.get("rsi", 50) < criterios["min_rsi_oversold"]:
                        rsi_ok = False
                        break
                
                if rsi_ok:
                    validacao["criterios_atendidos"].append("rsi_ok")
                    validacao["score_final"] += 10
                else:
                    validacao["criterios_falhados"].append("rsi_oversold")
            
            # Determinar se o sinal é válido
            validacao["valido"] = validacao["score_final"] >= 70 and len(validacao["criterios_falhados"]) <= 2
            
            # Calcular confiança
            validacao["confianca"] = min(100, validacao["score_final"])
            
            # Gerar recomendação
            if validacao["valido"]:
                if validacao["confianca"] >= 90:
                    validacao["recomendacao"] = "SINAL FORTE - Ação recomendada com posição normal"
                elif validacao["confianca"] >= 80:
                    validacao["recomendacao"] = "SINAL BOM - Ação recomendada com posição reduzida"
                else:
                    validacao["recomendacao"] = "SINAL MODERADO - Ação com cautela e stop loss apertado"
            else:
                if divergencias:
                    validacao["recomendacao"] = "DIVERGÊNCIAS DETECTADAS - Aguardar confirmação"
                else:
                    validacao["recomendacao"] = "CRITÉRIOS NÃO ATENDIDOS - Aguardar melhor setup"
            
            # Salvar no histórico
            self.validation_history[symbol] = validacao
            
            return validacao
            
        except Exception as e:
            print(f"❌ Erro ao validar sinal para {symbol}: {e}")
            return {
                "sinal_tipo": sinal_tipo,
                "symbol": symbol,
                "valido": False,
                "confianca": 0,
                "recomendacao": f"Erro na validação: {e}",
                "score_final": 0
            }
    
    def gerar_relatorio_validacao(self, symbol):
        """Gera relatório detalhado de validação"""
        try:
            if symbol not in self.validation_history:
                return "Nenhuma validação encontrada para este símbolo"
            
            validacao = self.validation_history[symbol]
            
            relatorio = f"""
=== RELATÓRIO DE VALIDAÇÃO MULTI-TIMEFRAME ===
Símbolo: {symbol}
Tipo de Sinal: {validacao['sinal_tipo'].upper()}
Timestamp: {validacao['timestamp']}

📊 CONCORDÂNCIA MULTI-TIMEFRAME:
• Score Bullish: {validacao['concordancia']['score_bullish']:.1f}
• Score Bearish: {validacao['concordancia']['score_bearish']:.1f}
• Tendência Dominante: {validacao['concordancia']['tendencia_dominante'].upper()}
• Força do Sinal: {validacao['concordancia']['forca_sinal']:.1f}
• Concordância: {validacao['concordancia']['concordancia']}
• Timeframes Analisados: {validacao['concordancia']['total_timeframes']}

✅ CRITÉRIOS ATENDIDOS ({len(validacao['criterios_atendidos'])}):
{chr(10).join([f"• {criterio}" for criterio in validacao['criterios_atendidos']])}

❌ CRITÉRIOS FALHADOS ({len(validacao['criterios_falhados'])}):
{chr(10).join([f"• {criterio}" for criterio in validacao['criterios_falhados']])}

🚨 DIVERGÊNCIAS DETECTADAS ({len(validacao['divergencias'])}):
"""
            
            for i, divergencia in enumerate(validacao['divergencias'], 1):
                relatorio += f"""
{i}. {divergencia['tipo']} - {divergencia['severidade']}
   Descrição: {divergencia['descricao']}
   Recomendação: {divergencia.get('recomendacao', 'N/A')}
"""
            
            relatorio += f"""
📈 RESULTADO FINAL:
• Score Final: {validacao['score_final']:.1f}/100
• Confiança: {validacao['confianca']:.1f}%
• Válido: {'SIM' if validacao['valido'] else 'NÃO'}
• Recomendação: {validacao['recomendacao']}

=== ANÁLISE POR TIMEFRAME ===
"""
            
            for timeframe, analysis in validacao['concordancia']['timeframes_analysis'].items():
                if analysis:
                    relatorio += f"""
{timeframe.upper()}:
• Score: {analysis.get('score', 0):.1f}
• Tendência: {analysis.get('tendencia', 'N/A').upper()}
• Confiança: {analysis.get('confianca', 0):.1f}
• RSI: {analysis.get('rsi', 0):.1f}
• Volume Ratio: {analysis.get('volume_ratio', 0):.2f}
• Volatilidade: {analysis.get('volatilidade', 0):.2f}%
"""
            
            return relatorio
            
        except Exception as e:
            return f"Erro ao gerar relatório: {e}"
    
    def get_estatisticas_validacao(self):
        """Retorna estatísticas das validações realizadas"""
        try:
            total_validacoes = len(self.validation_history)
            validacoes_validas = sum(1 for v in self.validation_history.values() if v.get('valido', False))
            validacoes_invalidas = total_validacoes - validacoes_validas
            
            confianca_media = 0
            if total_validacoes > 0:
                confianca_media = sum(v.get('confianca', 0) for v in self.validation_history.values()) / total_validacoes
            
            return {
                "total_validacoes": total_validacoes,
                "validacoes_validas": validacoes_validas,
                "validacoes_invalidas": validacoes_invalidas,
                "taxa_sucesso": (validacoes_validas / total_validacoes * 100) if total_validacoes > 0 else 0,
                "confianca_media": confianca_media,
                "ultima_atualizacao": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas: {e}")
            return {}

# Instância global do validador
validator = MultiTimeframeValidator()

def validar_sinal_completo(symbol, sinal_tipo, dados_timeframes):
    """Função wrapper para validação completa"""
    return validator.validar_sinal_multitimeframe(symbol, sinal_tipo, dados_timeframes)

def detectar_divergencias_completo(dados_timeframes):
    """Função wrapper para detecção de divergências"""
    concordancia = validator.calcular_concordancia_multitimeframe("", dados_timeframes)
    return validator.detectar_divergencias(concordancia["timeframes_analysis"])

def gerar_relatorio_completo(symbol):
    """Função wrapper para geração de relatório"""
    return validator.gerar_relatorio_validacao(symbol)

if __name__ == "__main__":
    print("✅ Multi-Timeframe Validator carregado com sucesso!")
    print("📊 Critérios de qualidade configurados:")
    for sinal, criterios in validator.quality_criteria.items():
        print(f"   {sinal.upper()}: {len(criterios)} critérios")
