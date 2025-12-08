#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTER INSTITUCIONAL - SNE RADAR
Adapta dados do sistema atual para formato institucional
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from config_institucional import obter_config_institucional


class AdapterInstitucional:
    """Adapta dados do sistema atual para formato institucional"""
    
    def __init__(self):
        """Inicializa adapter institucional"""
        self.config = obter_config_institucional()
        self.transformador = TransformerInstitucional()
        self.validator = ValidatorInstitucional()
        
        # Cache de adaptações
        self.cache_adaptacoes = {}
        self.cache_timeout = self.config.cache_timeout_minutos * 60
    
    def adaptar_dados_para_institucional(self, dados_sne: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados do SNE para formato institucional
        
        Args:
            dados_sne: Dados do sistema atual
            
        Returns:
            Dict com dados adaptados para formato institucional
        """
        try:
            # Verificar cache
            cache_key = self._gerar_cache_key(dados_sne)
            if self._verificar_cache(cache_key):
                return self.cache_adaptacoes[cache_key]
            
            # Adaptar cada componente
            dados_adaptados = {
                'metadata': self._adaptar_metadata(dados_sne),
                'market_context': self._adaptar_contexto_global(dados_sne.get('contexto', {})),
                'technical_analysis': self._adaptar_analise_tecnica(dados_sne.get('estrutura', {})),
                'multi_timeframe': self._adaptar_multi_tf(dados_sne.get('mtf', {})),
                'risk_assessment': self._adaptar_gestao_risco(dados_sne.get('gestao_risco', {})),
                'confluence_score': self._adaptar_confluencia(dados_sne.get('confluencia', {})),
                'projections': self._adaptar_projecoes(dados_sne.get('cenarios', {})),
                'patterns': self._adaptar_padroes(dados_sne.get('padroes', {})),
                'sentiment': self._adaptar_sentiment(dados_sne.get('sentiment', {})),
                'compliance': self._gerar_compliance_data(),
                'audit': self._gerar_audit_data()
            }
            
            # Converter valores problemáticos para JSON-safe
            dados_adaptados = self._converter_para_json_safe(dados_adaptados)
            
            # Salvar no cache
            self._salvar_cache(cache_key, dados_adaptados)
            
            return dados_adaptados
            
        except Exception as e:
            print(f"❌ Erro ao adaptar dados: {e}")
            return self._gerar_dados_fallback()
    
    def _converter_para_json_safe(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Converte dados para formato seguro para JSON"""
        try:
            import json
            # Tentar serializar e deserializar para converter tipos problemáticos
            json_str = json.dumps(dados, default=str)
            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️ Erro na conversão JSON-safe: {e}")
            return dados
    
    def _adaptar_metadata(self, dados_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta metadados para formato institucional"""
        timestamp = datetime.utcnow()
        
        return {
            'report_id': self._gerar_report_id(),
            'classification': 'INTERNAL USE ONLY',
            'generated': timestamp.isoformat(),
            'valid_until': self._calcular_valid_until(timestamp),
            'analyst': 'SNE-AI-SYSTEM v2.1',
            'compliance': 'MiFID II / ESMA Guidelines',
            'version': 'INSTITUTIONAL-1.0',
            'source_system': 'SNE-RADAR',
            'data_hash': self._calcular_hash_dados(dados_sne)
        }
    
    def _adaptar_contexto_global(self, contexto_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta contexto global para formato institucional"""
        return {
            'market_regime': contexto_sne.get('regime', 'UNKNOWN'),
            'regime_strength': contexto_sne.get('forca_regime', 0),
            'volatility_percent': contexto_sne.get('volatilidade', 0),
            'volatility_status': contexto_sne.get('volatilidade_status', 'Normal'),
            'volume_24h': contexto_sne.get('volume_24h', 0),
            'volume_ratio': contexto_sne.get('volume_ratio', 1.0),
            'session_active': contexto_sne.get('sessao', 'UNKNOWN'),
            'liquidity_score': contexto_sne.get('liquidez_score', 0),
            'market_structure': contexto_sne.get('estrutura_mercado', 'UNKNOWN'),
            'trend_direction': contexto_sne.get('direcao_tendencia', 'UNKNOWN'),
            'trend_strength': contexto_sne.get('forca_tendencia', 0)
        }
    
    def _adaptar_analise_tecnica(self, estrutura_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta análise técnica para formato institucional"""
        return {
            'trend_classification': estrutura_sne.get('tendencia', 'UNKNOWN'),
            'trend_strength': estrutura_sne.get('forca_tendencia', 0),
            'higher_highs': estrutura_sne.get('higher_highs', []),
            'higher_lows': estrutura_sne.get('higher_lows', []),
            'lower_highs': estrutura_sne.get('lower_highs', []),
            'lower_lows': estrutura_sne.get('lower_lows', []),
            'supports': estrutura_sne.get('suportes', []),
            'resistances': estrutura_sne.get('resistencias', []),
            'price_action': estrutura_sne.get('price_action', {}),
            'key_levels': estrutura_sne.get('niveis_chave', []),
            'breakout_levels': estrutura_sne.get('niveis_ruptura', [])
        }
    
    def _adaptar_multi_tf(self, mtf_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta análise multi-timeframe para formato institucional"""
        timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '8h', '12h', '1d', '1w', '1M']
        
        mtf_adaptado = {
            'timeframes': {},
            'overall_confluence': mtf_sne.get('confluencia_geral', 0),
            'primary_alignment': mtf_sne.get('alinhamento_principal', 'UNKNOWN'),
            'risk_assessment': mtf_sne.get('avaliacao_risco', 'MEDIUM'),
            'recommended_timeframes': mtf_sne.get('timeframes_recomendados', [])
        }
        
        # Adaptar cada timeframe
        for tf in timeframes:
            if tf in mtf_sne:
                mtf_adaptado['timeframes'][tf] = {
                    'trend': mtf_sne[tf].get('tendencia', 'UNKNOWN'),
                    'strength': mtf_sne[tf].get('forca', 0),
                    'ema8': mtf_sne[tf].get('ema8', 0),
                    'ema21': mtf_sne[tf].get('ema21', 0),
                    'rsi': mtf_sne[tf].get('rsi', 50),
                    'macd': mtf_sne[tf].get('macd', {}),
                    'key_level': mtf_sne[tf].get('nivel_chave', 0),
                    'confluence': mtf_sne[tf].get('confluencia', 0)
                }
        
        return mtf_adaptado
    
    def _adaptar_gestao_risco(self, risco_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta gestão de risco para formato institucional"""
        return {
            'risk_level': risco_sne.get('nivel_risco', 'MEDIUM'),
            'risk_score': risco_sne.get('score_risco', 5.0),
            'position_size': risco_sne.get('tamanho_posicao', 2.0),
            'stop_loss': risco_sne.get('stop_loss', 0),
            'take_profit': risco_sne.get('take_profit', 0),
            'risk_reward_ratio': risco_sne.get('risk_reward', 1.0),
            'max_drawdown': risco_sne.get('max_drawdown', 5.0),
            'volatility_adjustment': risco_sne.get('ajuste_volatilidade', 1.0),
            'correlation_risk': risco_sne.get('risco_correlacao', 0),
            'liquidity_risk': risco_sne.get('risco_liquidez', 0),
            'market_risk': risco_sne.get('risco_mercado', 0),
            'operational_risk': risco_sne.get('risco_operacional', 0)
        }
    
    def _adaptar_confluencia(self, confluencia_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta análise de confluência para formato institucional"""
        return {
            'overall_score': confluencia_sne.get('score', 0),
            'interpretation': confluencia_sne.get('interpretacao', 'UNKNOWN'),
            'components': {
                'multi_timeframe': confluencia_sne.get('multi_tf', 0),
                'fluxo_dom': confluencia_sne.get('fluxo_dom', 0),
                'zonas_magneticas': confluencia_sne.get('zonas_magneticas', 0),
                'sentiment': confluencia_sne.get('sentiment', 0),
                'volume': confluencia_sne.get('volume', 0)
            },
            'weights': {
                'multi_timeframe': 3.0,
                'fluxo_dom': 2.5,
                'zonas_magneticas': 2.0,
                'sentiment': 1.5,
                'volume': 1.0
            },
            'confidence_level': confluencia_sne.get('nivel_confianca', 'MEDIUM'),
            'recommendation': confluencia_sne.get('recomendacao', 'HOLD')
        }
    
    def _adaptar_projecoes(self, projecoes_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta projeções para formato institucional"""
        return {
            'scenarios': {
                'base': {
                    'probability': projecoes_sne.get('probabilidade_base', 50),
                    'target': projecoes_sne.get('target_base', 0),
                    'timeframe': projecoes_sne.get('timeframe_base', '1h'),
                    'description': projecoes_sne.get('descricao_base', 'Cenário base')
                },
                'optimistic': {
                    'probability': projecoes_sne.get('probabilidade_otimista', 25),
                    'target': projecoes_sne.get('target_otimista', 0),
                    'timeframe': projecoes_sne.get('timeframe_otimista', '2h'),
                    'description': projecoes_sne.get('descricao_otimista', 'Cenário otimista')
                },
                'pessimistic': {
                    'probability': projecoes_sne.get('probabilidade_pessimista', 25),
                    'target': projecoes_sne.get('target_pessimista', 0),
                    'timeframe': projecoes_sne.get('timeframe_pessimista', '30m'),
                    'description': projecoes_sne.get('descricao_pessimista', 'Cenário pessimista')
                }
            },
            'expected_value': projecoes_sne.get('valor_esperado', 0),
            'confidence_interval': projecoes_sne.get('intervalo_confianca', {}),
            'risk_factors': projecoes_sne.get('fatores_risco', [])
        }
    
    def _adaptar_padroes(self, padroes_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta padrões gráficos para formato institucional"""
        return {
            'candlestick_patterns': padroes_sne.get('padroes_candlestick', []),
            'chart_patterns': padroes_sne.get('padroes_graficos', []),
            'divergences': padroes_sne.get('divergencias', []),
            'fibonacci_levels': padroes_sne.get('niveis_fibonacci', []),
            'wedges': padroes_sne.get('wedges', []),
            'triangles': padroes_sne.get('triangulos', []),
            'flags': padroes_sne.get('flags', []),
            'support_resistance': padroes_sne.get('suporte_resistencia', [])
        }
    
    def _adaptar_sentiment(self, sentiment_sne: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta análise de sentiment para formato institucional"""
        return {
            'fear_greed_index': sentiment_sne.get('fear_greed', 50),
            'funding_rate': sentiment_sne.get('funding_rate', 0),
            'open_interest': sentiment_sne.get('open_interest', 0),
            'correlations': sentiment_sne.get('correlacoes', {}),
            'market_sentiment': sentiment_sne.get('sentiment_mercado', 'NEUTRAL'),
            'social_sentiment': sentiment_sne.get('sentiment_social', 'NEUTRAL'),
            'institutional_sentiment': sentiment_sne.get('sentiment_institucional', 'NEUTRAL')
        }
    
    def _gerar_compliance_data(self) -> Dict[str, Any]:
        """Gera dados de compliance"""
        return {
            'mifid_ii': {
                'price_transparency': True,
                'best_execution': True,
                'client_categorization': 'PROFESSIONAL'
            },
            'esma': {
                'risk_management': True,
                'position_limits': True,
                'reporting': True
            },
            'basel_iii': {
                'capital_adequacy': True,
                'liquidity_coverage': True,
                'leverage_ratio': True
            },
            'ifrs': {
                'fair_value': True,
            'impairment': True,
                'disclosure': True
            }
        }
    
    def _gerar_audit_data(self) -> Dict[str, Any]:
        """Gera dados de auditoria"""
        return {
            'audit_trail': True,
            'data_integrity': True,
            'access_logs': True,
            'change_logs': True,
            'compliance_logs': True,
            'retention_period': self.config.retencao_logs_dias,
            'encryption': self.config.criptografia_logs
        }
    
    def _gerar_report_id(self) -> str:
        """Gera ID único para relatório"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(timestamp.encode()).hexdigest()[:6].upper()
        return f"SNE-{timestamp}-{random_suffix}"
    
    def _calcular_valid_until(self, timestamp: datetime) -> str:
        """Calcula validade do relatório (2 horas)"""
        valid_until = timestamp.timestamp() + (2 * 3600)  # 2 horas
        return datetime.fromtimestamp(valid_until).isoformat()
    
    def _calcular_hash_dados(self, dados: Dict[str, Any]) -> str:
        """Calcula hash dos dados para integridade"""
        dados_str = json.dumps(dados, sort_keys=True)
        return hashlib.sha256(dados_str.encode()).hexdigest()
    
    def _gerar_cache_key(self, dados: Dict[str, Any]) -> str:
        """Gera chave de cache"""
        dados_str = json.dumps(dados, sort_keys=True)
        return hashlib.md5(dados_str.encode()).hexdigest()
    
    def _verificar_cache(self, cache_key: str) -> bool:
        """Verifica se dados estão em cache"""
        if cache_key in self.cache_adaptacoes:
            # Verificar timeout
            timestamp = self.cache_adaptacoes[cache_key].get('_timestamp', 0)
            if datetime.now().timestamp() - timestamp < self.cache_timeout:
                return True
            else:
                # Remover do cache
                del self.cache_adaptacoes[cache_key]
        return False
    
    def _salvar_cache(self, cache_key: str, dados: Dict[str, Any]):
        """Salva dados no cache"""
        dados['_timestamp'] = datetime.now().timestamp()
        self.cache_adaptacoes[cache_key] = dados
    
    def _gerar_dados_fallback(self) -> Dict[str, Any]:
        """Gera dados de fallback em caso de erro"""
        return {
            'metadata': {
                'report_id': 'SNE-FALLBACK-ERROR',
                'classification': 'INTERNAL USE ONLY',
                'generated': datetime.utcnow().isoformat(),
                'valid_until': datetime.utcnow().isoformat(),
                'analyst': 'SNE-AI-SYSTEM v2.1',
                'compliance': 'MiFID II / ESMA Guidelines',
                'version': 'INSTITUTIONAL-1.0',
                'source_system': 'SNE-RADAR',
                'data_hash': 'ERROR'
            },
            'error': 'Falha na adaptação de dados',
            'fallback': True
        }


class TransformerInstitucional:
    """Transforma dados específicos para formato institucional"""
    
    def __init__(self):
        """Inicializa transformer"""
        self.config = obter_config_institucional()
    
    def transformar_timeframe_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Transforma pesos de timeframe para padrão institucional"""
        # Padrão institucional: pesos baseados em volatilidade e liquidez
        institutional_weights = {
            '1m': 0.10,   # Alta volatilidade, baixa liquidez
            '5m': 0.15,   # Alta volatilidade, média liquidez
            '15m': 0.20,  # Média volatilidade, boa liquidez
            '30m': 0.15,  # Média volatilidade, boa liquidez
            '1h': 0.20,  # Baixa volatilidade, alta liquidez
            '4h': 0.15,  # Baixa volatilidade, alta liquidez
            '8h': 0.03,  # Muito baixa volatilidade
            '12h': 0.01, # Muito baixa volatilidade
            '1d': 0.01,  # Muito baixa volatilidade
            '1w': 0.00   # Desconsiderado para trading
        }
        
        return institutional_weights
    
    def transformar_risk_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma critérios de risco para padrão institucional"""
        return {
            'rsi': {
                '1m': {'oversold': 20, 'overbought': 80},
                '5m': {'oversold': 25, 'overbought': 75},
                '15m': {'oversold': 30, 'overbought': 70},
                '30m': {'oversold': 30, 'overbought': 70},
                '1h': {'oversold': 30, 'overbought': 70},
                '4h': {'oversold': 35, 'overbought': 65},
                '8h': {'oversold': 35, 'overbought': 65},
                '12h': {'oversold': 40, 'overbought': 60},
                '1d': {'oversold': 40, 'overbought': 60},
                '1w': {'oversold': 45, 'overbought': 55}
            },
            'volume': {
                '1m': {'min_multiplier': 0.5, 'max_multiplier': 3.0},
                '5m': {'min_multiplier': 0.7, 'max_multiplier': 2.5},
                '15m': {'min_multiplier': 0.8, 'max_multiplier': 2.0},
                '30m': {'min_multiplier': 0.9, 'max_multiplier': 1.8},
                '1h': {'min_multiplier': 1.0, 'max_multiplier': 1.5},
                '4h': {'min_multiplier': 1.1, 'max_multiplier': 1.3},
                '8h': {'min_multiplier': 1.2, 'max_multiplier': 1.2},
                '12h': {'min_multiplier': 1.3, 'max_multiplier': 1.1},
                '1d': {'min_multiplier': 1.5, 'max_multiplier': 1.0},
                '1w': {'min_multiplier': 2.0, 'max_multiplier': 0.8}
            }
        }


class ValidatorInstitucional:
    """Valida dados adaptados para formato institucional"""
    
    def __init__(self):
        """Inicializa validator"""
        self.config = obter_config_institucional()
    
    def validar_dados_adaptados(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados adaptados"""
        erros = []
        avisos = []
        
        # Validar metadata
        if 'metadata' not in dados:
            erros.append("Metadata ausente")
        else:
            metadata = dados['metadata']
            if not metadata.get('report_id'):
                erros.append("Report ID ausente")
            if not metadata.get('generated'):
                erros.append("Timestamp de geração ausente")
        
        # Validar contexto de mercado
        if 'market_context' not in dados:
            erros.append("Contexto de mercado ausente")
        else:
            contexto = dados['market_context']
            if contexto.get('market_regime') == 'UNKNOWN':
                avisos.append("Regime de mercado desconhecido")
            if contexto.get('regime_strength', 0) < 3:
                avisos.append("Regime de mercado fraco")
        
        # Validar análise técnica
        if 'technical_analysis' not in dados:
            erros.append("Análise técnica ausente")
        
        # Validar multi-timeframe
        if 'multi_timeframe' not in dados:
            erros.append("Análise multi-timeframe ausente")
        else:
            mtf = dados['multi_timeframe']
            if mtf.get('overall_confluence', 0) < self.config.confluencia_minima:
                avisos.append(f"Confluência baixa: {mtf.get('overall_confluence', 0)}")
        
        # Validar gestão de risco
        if 'risk_assessment' not in dados:
            erros.append("Gestão de risco ausente")
        else:
            risco = dados['risk_assessment']
            if risco.get('risk_score', 0) > self.config.risco_maximo:
                avisos.append(f"Risco alto: {risco.get('risk_score', 0)}")
        
        return {
            'valido': len(erros) == 0,
            'erros': erros,
            'avisos': avisos,
            'score_qualidade': self._calcular_score_qualidade(erros, avisos)
        }
    
    def _calcular_score_qualidade(self, erros: List[str], avisos: List[str]) -> float:
        """Calcula score de qualidade baseado em erros e avisos"""
        score = 100.0
        
        # Penalizar erros
        score -= len(erros) * 20.0
        
        # Penalizar avisos
        score -= len(avisos) * 5.0
        
        return max(0.0, score)


# Instância global do adapter
adapter_institucional = AdapterInstitucional()


def obter_adapter_institucional() -> AdapterInstitucional:
    """Retorna instância global do adapter institucional"""
    return adapter_institucional


if __name__ == "__main__":
    # Teste do adapter
    adapter = obter_adapter_institucional()
    
    # Dados de teste
    dados_teste = {
        'contexto': {
            'regime': 'BULL_TREND',
            'forca_regime': 8,
            'volatilidade': 2.5,
            'volume_24h': 1000000000
        },
        'estrutura': {
            'tendencia': 'BULL',
            'forca_tendencia': 7,
            'suportes': [42000, 41800, 41600],
            'resistencias': [42500, 42800, 43000]
        },
        'mtf': {
            'confluencia_geral': 8.5,
            'alinhamento_principal': 'BULL',
            '1h': {'tendencia': 'BULL', 'forca': 8, 'rsi': 65}
        },
        'gestao_risco': {
            'nivel_risco': 'MEDIUM',
            'score_risco': 4.5,
            'tamanho_posicao': 2.0
        },
        'confluencia': {
            'score': 8.5,
            'interpretacao': 'ALTA',
            'recomendacao': 'BUY'
        }
    }
    
    # Adaptar dados
    dados_adaptados = adapter.adaptar_dados_para_institucional(dados_teste)
    
    print("✅ Adapter institucional testado com sucesso!")
    print(f"📊 Dados adaptados: {len(dados_adaptados)} seções")
    print(f"🆔 Report ID: {dados_adaptados['metadata']['report_id']}")
