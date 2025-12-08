#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO TÉCNICO - NÚCLEO ORQUESTRADOR
Gera relatório técnico completo integrando todos os módulos
"""

import os
import requests
import pandas as pd
from datetime import datetime
from indicadores import calcular_indicadores
import contexto_global
import estrutura_mercado
import multi_timeframe
import padroes_graficos
import sentimento_global
import projecoes
import confluencia
import formatter_relatorio
from catalogo_magnetico import obter_zonas_magneticas
from fluxo_ativo import FluxoAtivo
from analise_candles_integracao import incluir_analise_candles_relatorio
from gestao_risco_profissional import GestaoRiscoProfissional


def gerar_relatorio(symbol="BTCUSDT", timeframe="1h", salvar=True, modo_institucional=False):
    """
    Gera relatório técnico completo
    
    Args:
        symbol: Par a analisar
        timeframe: Timeframe principal
        salvar: Se deve salvar em arquivo
        modo_institucional: Se deve gerar formato institucional
    
    Returns:
        str com relatório formatado
    """
    print(f"🔄 Gerando relatório técnico para {symbol}...")
    
    # 1. COLETAR DADOS
    dados = coletar_dados(symbol, timeframe)
    if dados is None:
        return "❌ Erro ao coletar dados da Binance. Verifique sua conexão e tente novamente."
    
    # 2. ANÁLISE MODULAR
    print("📊 Analisando contexto...")
    try:
        ctx = contexto_global.analisar_contexto(dados)
    except Exception as e:
        print(f"⚠️ Erro em contexto_global: {e}")
        ctx = {'regime': 'UNKNOWN', 'volatilidade': 0, 'volume_24h': 0}
    
    print("📊 Analisando estrutura...")
    try:
        est = estrutura_mercado.analisar_estrutura(dados)
    except Exception as e:
        print(f"⚠️ Erro em estrutura_mercado (scipy): {e}")
        est = {'tendencia': 'NEUTRAL', 'forca': 0, 'estrutura': 'INDEFINIDA'}
    
    print("📊 Análise multi-timeframe...")
    try:
        mtf = multi_timeframe.analise_multitf(symbol)
    except Exception as e:
        print(f"⚠️ Erro em multi_timeframe: {e}")
        mtf = {'score': 5.0, 'alinhamento': 'NEUTRAL'}
    
    print("📊 Calculando indicadores...")
    
    # Verificar se as colunas dos indicadores existem
    required_indicators = ['EMA8', 'EMA21', 'RSI']
    missing_indicators = [col for col in required_indicators if col not in dados.columns]
    if missing_indicators:
        print(f"❌ Indicadores faltando: {missing_indicators}")
        return f"❌ Erro: Indicadores não calculados - {missing_indicators}"
    
    ind = {
        'ema8': dados['EMA8'].iloc[-1],
        'ema21': dados['EMA21'].iloc[-1],
        'rsi': dados['RSI'].iloc[-1]
    }
    
    print("📊 Analisando zonas magnéticas...")
    zonas_list = obter_zonas_magneticas()
    
    # Verificar se a coluna 'close' existe antes de acessá-la
    if 'close' not in dados.columns:
        print("❌ Coluna 'close' não encontrada nos dados")
        return "❌ Erro: Dados incompletos - coluna 'close' não encontrada"
    
    preco_atual = dados['close'].iloc[-1]
    zona_proxima = min(zonas_list, key=lambda z: abs(z - preco_atual)) if zonas_list else None
    dist_pct = abs(zona_proxima - preco_atual) / preco_atual * 100 if zona_proxima else 0
    
    zonas = {
        'zonas': zonas_list,
        'zona_proxima': zona_proxima,
        'distancia_pct': dist_pct,
        'motivo': f"Próximo de romper zona ${zona_proxima:,.2f}" if zona_proxima else "Sem zonas próximas"
    }
    
    print("📊 Analisando fluxo...")
    fluxo_obj = FluxoAtivo()
    flx = fluxo_obj.calcular_pressao_liquidez(symbol)
    
    print("📊 Detectando padrões...")
    try:
        pad = padroes_graficos.detectar_padroes(dados)
    except Exception as e:
        print(f"⚠️ Erro em padroes_graficos: {e}")
        pad = {'padroes': [], 'forca': 0}
    
    print("🔺 Analisando Wedges...")
    try:
        wedges = padroes_graficos.detectar_wedges(dados)
    except Exception as e:
        print(f"⚠️ Erro em wedges: {e}")
        wedges = {'wedges': [], 'forca': 0}
    
    print("📊 Analisando sentiment...")
    try:
        sent = sentimento_global.analisar_sentiment(symbol)
    except Exception as e:
        print(f"⚠️ Erro em sentimento_global: {e}")
        sent = {'score': 0.5, 'fear_greed': {'valor': 50}}
    
    # 3. ANÁLISE DETALHADA DE CANDLES
    print("🕐 Analisando candle atual...")
    try:
        dados = incluir_analise_candles_relatorio({'dados': dados}, dados, timeframe)
        candles_analise = dados['candles_detalhados']
    except Exception as e:
        print(f"⚠️ Erro em analise_candles: {e}")
        candles_analise = {'candle_atual': 'INDEFINIDO', 'padroes': []}
    
    # 4. INTELIGÊNCIA
    print("🧠 Calculando confluência...")
    try:
        conf = confluencia.calcular_confluencia(mtf, flx, zonas, sent)
    except Exception as e:
        print(f"⚠️ Erro em confluencia: {e}")
        conf = {'score': 5.0, 'interpretacao': 'Moderada - Confirmação parcial'}
    
    print("🔮 Projetando cenários...")
    try:
        cen = projecoes.projetar_cenarios(dados, conf['score'], est, flx)
    except Exception as e:
        print(f"⚠️ Erro em projecoes: {e}")
        cen = {'cenarios': [], 'probabilidade': 0.5}
    
    # 5. GESTÃO DE RISCO PROFISSIONAL
    print("🛡️ Aplicando gestão de risco...")
    try:
        gestao_risco = GestaoRiscoProfissional(capital_base=10.0)
        
        # Criar dados básicos para gestão de risco
        dados_risco = {
            'preco_atual': preco_atual,
            'volatilidade': ctx.get('volatilidade', 1.0),
            'volume': dados['volume'].iloc[-1] if 'volume' in dados.columns else 0
        }
        
        gestao_risco_data = gestao_risco.calcular_gestao_risco_com_niveis(
            dados_risco, ctx, est, timeframe, direcao='LONG'
        )
    except Exception as e:
        print(f"⚠️ Erro em gestao_risco: {e}")
        gestao_risco_data = {
            'gestao_risco': 'Erro na gestão de risco',
            'setup_validado': False,
            'niveis': {}
        }
    
    # 6. DECISÃO DE FORMATO
    if modo_institucional:
        # NOVO: Modo institucional
        print("🏛️ Gerando relatório institucional...")
        try:
            from relatorio_institucional_simples import obter_relatorio_institucional
            from compliance_institucional import obter_compliance_institucional
            from auditoria_institucional import obter_auditoria_institucional
            
            gerador_institucional = obter_relatorio_institucional()
            compliance = obter_compliance_institucional()
            auditoria = obter_auditoria_institucional()
            
            # Preparar dados para formato institucional
            dados_institucionais = {
                'symbol': symbol,
                'timeframe': timeframe,
                'contexto': ctx,
                'estrutura': est,
                'mtf': mtf,
                'indicadores': ind,
                'zonas': zonas,
                'fluxo': flx,
                'padroes': pad,
                'wedges': wedges,
                'sentiment': sent,
                'cenarios': cen,
                'confluencia': conf,
                'candles_detalhados': candles_analise,
                'gestao_risco': gestao_risco_data
            }
            
            # Gerar relatório institucional
            relatorio = gerador_institucional.gerar_relatorio_institucional(
                symbol, timeframe, dados_institucionais
            )
            
            # Validar compliance
            resultado_compliance = compliance.validar_relatorio(relatorio, dados_institucionais)
            
            # Registrar auditoria
            auditoria.registrar_operacao(
                "gerar_relatorio_institucional",
                {'symbol': symbol, 'timeframe': timeframe},
                dados_institucionais
            )
            
            # Salvar em diretório institucional
            if salvar:
                caminho = salvar_relatorio_institucional(relatorio, symbol)
                print(f"✅ Relatório institucional salvo: {caminho}")
                print(f"📊 Compliance: {resultado_compliance['score_compliance']:.1f}%")
                print(f"🔍 Auditoria: Operação registrada")
            
        except ImportError as e:
            print(f"⚠️ Módulos institucionais não disponíveis: {e}")
            print("🔄 Gerando relatório padrão...")
            modo_institucional = False
    
    if not modo_institucional:
        # MANTIDO: Formato atual
        print("📝 Formatando relatório padrão...")
        relatorio = formatter_relatorio.montar_relatorio(
            symbol=symbol,
            contexto=ctx,
            estrutura=est,
            mtf=mtf,
            indicadores=ind,
            zonas=zonas,
            fluxo=flx,
            padroes=pad,
            wedges=wedges,
            sentiment=sent,
            cenarios=cen,
            confluencia=conf,
            candles_detalhados=candles_analise,
            gestao_risco=gestao_risco_data.get('gestao_risco')
        )
        
        if salvar:
            caminho = salvar_relatorio(relatorio, symbol)
            print(f"✅ Relatório salvo: {caminho}")
    
    print("✅ Relatório gerado com sucesso!")
    return relatorio


def coletar_dados(symbol, interval, limit=200, max_retries=3):
    """Coleta dados da Binance com retry automático"""
    import time
    
    for tentativa in range(max_retries):
        try:
            print(f"🔄 Tentativa {tentativa + 1}/{max_retries} - Coletando dados para {symbol}...")
            
            # Normalizar interval para lowercase
            interval = interval.lower()
            
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": symbol, "interval": interval, "limit": limit}
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se há dados
                if not data or len(data) == 0:
                    print(f"⚠️ Nenhum dado retornado para {symbol}")
                    if tentativa < max_retries - 1:
                        time.sleep(2)  # Aguardar antes da próxima tentativa
                        continue
                    return None
                
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                # Verificar se as colunas existem
                required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in required_columns):
                    print(f"⚠️ Colunas faltando nos dados para {symbol}")
                    if tentativa < max_retries - 1:
                        time.sleep(2)
                        continue
                    return None
                
                df = df[required_columns].astype({
                    'timestamp': 'datetime64[ms]',
                    'open': float, 'high': float, 'low': float,
                    'close': float, 'volume': float
                })
                
                # Verificar se há dados válidos
                if df.empty or df['close'].isna().all():
                    print(f"⚠️ Dados inválidos para {symbol}")
                    if tentativa < max_retries - 1:
                        time.sleep(2)
                        continue
                    return None
                
                # Calcular indicadores
                try:
                    df = calcular_indicadores(df)
                    print(f"✅ Dados coletados com sucesso para {symbol} ({len(df)} candles)")
                    return df
                except Exception as e:
                    print(f"⚠️ Erro ao calcular indicadores: {e}")
                    # Retornar dados sem indicadores se necessário
                    print(f"✅ Dados coletados sem indicadores para {symbol}")
                    return df
            else:
                print(f"❌ Erro HTTP {response.status_code} ao coletar dados para {symbol}")
                if tentativa < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout na tentativa {tentativa + 1} para {symbol}")
            if tentativa < max_retries - 1:
                time.sleep(3)
                continue
        except requests.exceptions.ConnectionError:
            print(f"🌐 Erro de conexão na tentativa {tentativa + 1} para {symbol}")
            if tentativa < max_retries - 1:
                time.sleep(3)
                continue
        except Exception as e:
            print(f"❌ Erro na tentativa {tentativa + 1} para {symbol}: {e}")
            if tentativa < max_retries - 1:
                time.sleep(2)
                continue
    
    print(f"❌ Falha ao coletar dados para {symbol} após {max_retries} tentativas")
    return None


def salvar_relatorio(relatorio, symbol):
    """Salva relatório em arquivo"""
    try:
        # Criar diretório
        os.makedirs("reports", exist_ok=True)
        
        # Nome do arquivo
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"reports/{symbol}_{timestamp}.txt"
        
        # Salvar
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        return filename
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return None


def salvar_relatorio_institucional(relatorio, symbol):
    """Salva relatório institucional em arquivo"""
    try:
        # Criar diretório institucional
        os.makedirs("reports/institutional", exist_ok=True)
        
        # Nome do arquivo institucional
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"reports/institutional/{symbol}_{timestamp}_institutional.txt"
        
        # Salvar
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        return filename
    except Exception as e:
        print(f"Erro ao salvar relatório institucional: {e}")
        return None


if __name__ == "__main__":
    # Teste do modo institucional
    print("🏛️ Testando modo institucional...")
    relatorio_institucional = gerar_relatorio("BTCUSDT", "1h", salvar=True, modo_institucional=True)
    print("\n" + "="*80)
    print("RELATÓRIO INSTITUCIONAL GERADO")
    print("="*80)
    print(relatorio_institucional[:500] + "..." if len(relatorio_institucional) > 500 else relatorio_institucional)
    
    print("\n" + "="*80)
    print("🔄 Testando modo padrão...")
    relatorio_padrao = gerar_relatorio("BTCUSDT", "1h", salvar=True, modo_institucional=False)
    print("\n" + "="*80)
    print("RELATÓRIO PADRÃO GERADO")
    print("="*80)
    print(relatorio_padrao[:500] + "..." if len(relatorio_padrao) > 500 else relatorio_padrao)


