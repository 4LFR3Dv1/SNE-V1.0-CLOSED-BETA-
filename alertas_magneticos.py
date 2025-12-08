#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE ALERTAS MAGNÉTICOS SNE RADAR
Detecta setups magnéticos: LED Reversão, LMH Rebote, ZV Impulso
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os


class AlertasMagneticos:
    """Sistema de alertas para estratégia magnética"""
    
    def __init__(self):
        self.alertas_dir = 'reports/alertas_magneticos/'
        os.makedirs(self.alertas_dir, exist_ok=True)
        
        # Configurações de alertas
        self.config = {
            'volume_threshold': 0.7,  # Volume baixo = 70% da média
            'atr_multiplier': 1.5,    # Variação > 1.5x ATR
            'wick_rejection': 0.3,     # Wick de rejeição > 30% do corpo
            'campo_cross_threshold': 0.001  # Threshold para cruzamento de campo
        }
    
    def analisar_setups_magneticos(self, df, campos, niveis_dict=None):
        """
        Analisa e detecta os 3 setups magnéticos principais
        
        Args:
            df: DataFrame com dados OHLCV
            campos: Dados dos campos magnéticos
            niveis_dict: Níveis operacionais
        
        Returns:
            dict com alertas detectados
        """
        try:
            alertas = {
                'led_reversao': self._detectar_led_reversao(df, campos),
                'lmh_rebote': self._detectar_lmh_rebote(df, campos),
                'zv_impulso': self._detectar_zv_impulso(df, campos),
                'timestamp': datetime.now().isoformat(),
                'symbol': 'BTCUSDT',  # Será passado como parâmetro
                'total_alertas': 0
            }
            
            # Contar total de alertas ativos
            alertas['total_alertas'] = sum([
                1 for alerta in [alertas['led_reversao'], alertas['lmh_rebote'], alertas['zv_impulso']]
                if alerta['ativo']
            ])
            
            return alertas
            
        except Exception as e:
            print(f"Erro ao analisar setups magnéticos: {e}")
            return {'erro': str(e)}
    
    def _detectar_led_reversao(self, df, campos):
        """
        Detecta LED Reversão: EMA8 cruza EMA21 com volume confirmando
        
        Setup: Campo dinâmico inverte sinal + volume acima da média
        """
        try:
            # Calcular EMAs
            ema8 = df['close'].ewm(span=8, adjust=False).mean()
            ema21 = df['close'].ewm(span=21, adjust=False).mean()
            
            # Detectar cruzamento
            cruzamento_atual = ema8.iloc[-1] - ema21.iloc[-1]
            cruzamento_anterior = ema8.iloc[-2] - ema21.iloc[-2]
            
            # Volume médio
            volume_medio = df['volume'].rolling(window=20).mean().iloc[-1]
            volume_atual = df['volume'].iloc[-1]
            
            # Condições para LED Reversão
            cruzamento_detectado = (
                (cruzamento_atual > 0 and cruzamento_anterior <= 0) or  # Cruzamento para cima
                (cruzamento_atual < 0 and cruzamento_anterior >= 0)      # Cruzamento para baixo
            )
            
            volume_confirmando = volume_atual > volume_medio * 1.2
            
            # Força do sinal
            forca_sinal = abs(cruzamento_atual) / df['close'].iloc[-1] * 100
            
            return {
                'ativo': cruzamento_detectado and volume_confirmando,
                'tipo': 'LED_REVERSAO',
                'direcao': 'ALTA' if cruzamento_atual > 0 else 'BAIXA',
                'forca': min(forca_sinal * 10, 10),  # Normalizar para 0-10
                'volume_ratio': volume_atual / volume_medio,
                'cruzamento_atual': cruzamento_atual,
                'descricao': f"EMA8 cruza EMA21 ({'ALTA' if cruzamento_atual > 0 else 'BAIXA'}) com volume {volume_atual/volume_medio:.1f}x",
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            return {'ativo': False, 'erro': str(e)}
    
    def _detectar_lmh_rebote(self, df, campos):
        """
        Detecta LMH Rebote: Preço toca LMH + rejeita com wick + volume baixo
        
        Setup: Preço toca VAL/VAH/POC + wick de rejeição + volume baixo
        """
        try:
            preco_atual = df['close'].iloc[-1]
            high_atual = df['high'].iloc[-1]
            low_atual = df['low'].iloc[-1]
            
            # Campos magnéticos horizontais
            val = campos['val']
            vah = campos['vah']
            poc = campos['poc']
            
            # Volume médio
            volume_medio = df['volume'].rolling(window=20).mean().iloc[-1]
            volume_atual = df['volume'].iloc[-1]
            
            # Detectar toque em LMH
            toque_val = abs(low_atual - val) / val < 0.005  # 0.5% de tolerância
            toque_vah = abs(high_atual - vah) / vah < 0.005
            toque_poc = abs(preco_atual - poc) / poc < 0.005
            
            toque_lmh = toque_val or toque_vah or toque_poc
            
            # Detectar rejeição (wick)
            corpo_candle = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
            wick_superior = df['high'].iloc[-1] - max(df['close'].iloc[-1], df['open'].iloc[-1])
            wick_inferior = min(df['close'].iloc[-1], df['open'].iloc[-1]) - df['low'].iloc[-1]
            
            rejeicao_detectada = (
                (wick_superior > corpo_candle * self.config['wick_rejection']) or
                (wick_inferior > corpo_candle * self.config['wick_rejection'])
            )
            
            # Volume baixo (redução de volume)
            volume_baixo = volume_atual < volume_medio * self.config['volume_threshold']
            
            # Determinar direção do rebote
            if toque_val and rejeicao_detectada:
                direcao = 'ALTA'  # Rebote de VAL para cima
            elif toque_vah and rejeicao_detectada:
                direcao = 'BAIXA'  # Rebote de VAH para baixo
            elif toque_poc and rejeicao_detectada:
                direcao = 'NEUTRO'  # Rebote de POC
            else:
                direcao = 'NENHUMA'
            
            # Força do sinal
            forca_sinal = 0
            if toque_lmh and rejeicao_detectada and volume_baixo:
                forca_sinal = 8  # Alto
            elif toque_lmh and (rejeicao_detectada or volume_baixo):
                forca_sinal = 5  # Médio
            
            return {
                'ativo': toque_lmh and rejeicao_detectada and volume_baixo,
                'tipo': 'LMH_REBOTE',
                'direcao': direcao,
                'forca': forca_sinal,
                'volume_ratio': volume_atual / volume_medio,
                'wick_ratio': max(wick_superior, wick_inferior) / corpo_candle if corpo_candle > 0 else 0,
                'lmh_tocado': 'VAL' if toque_val else ('VAH' if toque_vah else ('POC' if toque_poc else 'NENHUM')),
                'descricao': f"Rebote em {direcao} de LMH com volume {volume_atual/volume_medio:.1f}x e wick {max(wick_superior, wick_inferior)/corpo_candle:.1f}x",
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            return {'ativo': False, 'erro': str(e)}
    
    def _detectar_zv_impulso(self, df, campos):
        """
        Detecta ZV Impulso: Preço entra em zona de vácuo + variação > ATR
        
        Setup: Preço sai de campo magnético + movimento rápido + volume crescente
        """
        try:
            # Calcular ATR
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[-1]
            
            # Movimento atual
            movimento_atual = abs(df['close'].iloc[-1] - df['close'].iloc[-2])
            
            # Volume
            volume_medio = df['volume'].rolling(window=20).mean().iloc[-1]
            volume_atual = df['volume'].iloc[-1]
            
            # Detectar zona de vácuo (EMA8 e EMA21 distantes)
            ema8 = df['close'].ewm(span=8, adjust=False).mean()
            ema21 = df['close'].ewm(span=21, adjust=False).mean()
            distancia_emas = abs(ema8.iloc[-1] - ema21.iloc[-1])
            distancia_media = abs(ema8.rolling(window=20).mean().iloc[-1] - 
                                ema21.rolling(window=20).mean().iloc[-1])
            
            em_zona_vacuo = distancia_emas > distancia_media * 1.5
            
            # Movimento rápido (variação > ATR)
            movimento_rapido = movimento_atual > atr * self.config['atr_multiplier']
            
            # Volume crescente
            volume_crescente = volume_atual > volume_medio * 1.1
            
            # Determinar direção do impulso
            if df['close'].iloc[-1] > df['close'].iloc[-2]:
                direcao = 'ALTA'
            else:
                direcao = 'BAIXA'
            
            # Força do sinal
            forca_sinal = 0
            if em_zona_vacuo and movimento_rapido and volume_crescente:
                forca_sinal = 9  # Muito alto
            elif em_zona_vacuo and (movimento_rapido or volume_crescente):
                forca_sinal = 6  # Alto
            
            return {
                'ativo': em_zona_vacuo and movimento_rapido and volume_crescente,
                'tipo': 'ZV_IMPULSO',
                'direcao': direcao,
                'forca': forca_sinal,
                'volume_ratio': volume_atual / volume_medio,
                'movimento_atr_ratio': movimento_atual / atr,
                'distancia_emas_ratio': distancia_emas / distancia_media,
                'descricao': f"Impulso {direcao} em ZV com movimento {movimento_atual/atr:.1f}x ATR e volume {volume_atual/volume_medio:.1f}x",
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            return {'ativo': False, 'erro': str(e)}
    
    def salvar_alertas(self, alertas, symbol):
        """Salva alertas em arquivo JSON"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.alertas_dir}{symbol}_alertas_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(alertas, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Alertas salvos: {filename}")
            return filename
            
        except Exception as e:
            print(f"Erro ao salvar alertas: {e}")
            return None
    
    def gerar_relatorio_alertas(self, alertas, symbol):
        """Gera relatório textual dos alertas"""
        try:
            if alertas.get('total_alertas', 0) == 0:
                return f"🔇 {symbol} - Nenhum alerta magnético ativo"
            
            relatorio = f"🧲 ALERTAS MAGNÉTICOS - {symbol}\n"
            relatorio += f"📊 Total de alertas: {alertas['total_alertas']}\n"
            relatorio += f"⏰ {alertas['timestamp']}\n\n"
            
            # LED Reversão
            if alertas['led_reversao']['ativo']:
                led = alertas['led_reversao']
                relatorio += f"🔄 LED REVERSÃO ({led['forca']}/10)\n"
                relatorio += f"   Direção: {led['direcao']}\n"
                relatorio += f"   Volume: {led['volume_ratio']:.1f}x\n"
                relatorio += f"   {led['descricao']}\n\n"
            
            # LMH Rebote
            if alertas['lmh_rebote']['ativo']:
                lmh = alertas['lmh_rebote']
                relatorio += f"⚡ LMH REBOTE ({lmh['forca']}/10)\n"
                relatorio += f"   Direção: {lmh['direcao']}\n"
                relatorio += f"   LMH: {lmh['lmh_tocado']}\n"
                relatorio += f"   Volume: {lmh['volume_ratio']:.1f}x\n"
                relatorio += f"   {lmh['descricao']}\n\n"
            
            # ZV Impulso
            if alertas['zv_impulso']['ativo']:
                zv = alertas['zv_impulso']
                relatorio += f"🚀 ZV IMPULSO ({zv['forca']}/10)\n"
                relatorio += f"   Direção: {zv['direcao']}\n"
                relatorio += f"   Movimento: {zv['movimento_atr_ratio']:.1f}x ATR\n"
                relatorio += f"   Volume: {zv['volume_ratio']:.1f}x\n"
                relatorio += f"   {zv['descricao']}\n\n"
            
            return relatorio
            
        except Exception as e:
            return f"Erro ao gerar relatório: {e}"


def analisar_alertas_magneticos(df, campos, symbol="BTCUSDT", niveis_dict=None):
    """
    Função principal para analisar alertas magnéticos
    
    Args:
        df: DataFrame com dados OHLCV
        campos: Dados dos campos magnéticos
        symbol: Par analisado
        niveis_dict: Níveis operacionais
    
    Returns:
        dict com alertas e relatório
    """
    alertas_system = AlertasMagneticos()
    
    # Analisar setups
    alertas = alertas_system.analisar_setups_magneticos(df, campos, niveis_dict)
    
    # Gerar relatório
    relatorio = alertas_system.gerar_relatorio_alertas(alertas, symbol)
    
    # Salvar alertas
    arquivo_alertas = alertas_system.salvar_alertas(alertas, symbol)
    
    return {
        'alertas': alertas,
        'relatorio': relatorio,
        'arquivo': arquivo_alertas
    }


if __name__ == "__main__":
    # Teste do sistema de alertas
    print("🧲 Testando Sistema de Alertas Magnéticos...")
    
    # Criar dados de teste
    dates = pd.date_range(start='2024-01-01', periods=100, freq='5min')
    np.random.seed(42)
    
    df_teste = pd.DataFrame({
        'open': 50000 + np.random.randn(100) * 100,
        'high': 50000 + np.random.randn(100) * 100 + 50,
        'low': 50000 + np.random.randn(100) * 100 - 50,
        'close': 50000 + np.random.randn(100) * 100,
        'volume': 1000 + np.random.randn(100) * 200
    }, index=dates)
    
    # Campos de teste
    campos_teste = {
        'val': 49500,
        'vah': 50500,
        'poc': 50000,
        'campo_dinamico': 0.001,
        'campo_dinamico_tendencia': 'expansao',
        'zonas_vacuo': [0] * 20
    }
    
    # Testar alertas
    resultado = analisar_alertas_magneticos(df_teste, campos_teste, "BTCUSDT")
    
    print("📊 Relatório de Teste:")
    print(resultado['relatorio'])
    
    if resultado['arquivo']:
        print(f"✅ Teste concluído: {resultado['arquivo']}")
    else:
        print("❌ Erro no teste")






