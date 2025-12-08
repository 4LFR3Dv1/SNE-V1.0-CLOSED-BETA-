#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRAÇÃO DO FORMATADOR MELHORADO
Integra o formatador melhorado no sistema de relatórios
"""

from datetime import datetime
from formatador_telegram_melhorado import FormatadorTelegram


def gerar_relatorio_telegram_melhorado(resultado):
    """Gera relatório do Telegram com formatação melhorada em blocos"""
    try:
        formatador = FormatadorTelegram()
        blocos = formatador.formatar_mensagem_completa(resultado)
        
        # Retornar blocos formatados
        return blocos
        
    except Exception as e:
        return [f"❌ Erro ao gerar relatório melhorado: {str(e)}"]


def enviar_relatorio_telegram_blocos(bot, chat_id, resultado, foto_path=None):
    """Envia relatório do Telegram em blocos organizados"""
    try:
        # Gerar blocos formatados
        blocos = gerar_relatorio_telegram_melhorado(resultado)
        
        # Enviar foto primeiro se disponível
        if foto_path:
            try:
                with open(foto_path, 'rb') as foto:
                    bot.send_photo(chat_id, foto, caption="📈 **Gráfico Técnico Atualizado**")
            except Exception as e:
                print(f"⚠️ Erro ao enviar foto: {e}")
        
        # Enviar blocos de texto
        for i, bloco in enumerate(blocos, 1):
            try:
                # Adicionar indicador de bloco
                bloco_completo = f"📱 **BLOCO {i}/{len(blocos)}**\n\n{bloco}"
                
                # Enviar bloco
                bot.send_message(chat_id, bloco_completo, parse_mode='Markdown')
                
                # Pequena pausa entre blocos para evitar spam
                import time
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ Erro ao enviar bloco {i}: {e}")
                # Tentar enviar sem formatação Markdown
                try:
                    bot.send_message(chat_id, f"📱 BLOCO {i}/{len(blocos)}\n\n{bloco}")
                except Exception as e2:
                    print(f"❌ Erro crítico ao enviar bloco {i}: {e2}")
        
        print(f"✅ Relatório enviado em {len(blocos)} blocos organizados!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar relatório em blocos: {e}")
        return False


def testar_formatador_melhorado():
    """Testa o formatador melhorado"""
    print("🚀 TESTANDO FORMATADOR MELHORADO")
    print("="*50)
    
    # Dados de teste simulados
    resultado_teste = {
        'symbol': 'BTCUSDT',
        'timeframe': '1m',
        'indicadores': {'preco': 111209.54},
        'contexto': {
            'regime': 'CONSOLIDATION',
            'forca_regime': 8.3,
            'volatilidade': 0.03,
            'liquidez': 3,
            'rsi': 52,
            'confluencia_score': 5.5
        },
        'estrutura': {'tendencia': 'BAIXA'},
        'mtf': {'alta': 2, 'baixa': 1, 'lateral': 0},
        'fluxo': {'ratio': 0.948, 'pressao': 'NEUTRO'},
        'sintese': {
            'acao': '🔴 SHORT (SCALP)',
            'vies': 'MODERADO CONSOLIDATION',
            'score_confianca': 5.5,
            'recomendacao': '📊 SHORT ESPECULATIVO (1m) - Vender em $111,401.44 (risco maior)'
        },
        'candles_detalhados': {
            'candle_atual': {
                'tempo_restante': '06:59',
                'timestamp_inicio': '24/10/2025 01:52:49',
                'timestamp_fechamento': '24/10/2025 01:53:49'
            },
            'precos': {
                'open': 111197.40,
                'high': 111230.93,
                'low': 111180.27,
                'close': 111209.54,
                'range': 50.66,
                'range_percentual': 0.05
            },
            'classificacao': {
                'tipo': 'Candle Fraco',
                'significado': 'Movimento fraco'
            }
        },
        'niveis_operacionais': {
            'entry_price': 111401.44,
            'stop_loss': 111957.33,
            'tp1': 110623.18,
            'tp2': 110474.76,
            'rr_ratio': '1:1.7'
        },
        'gestao_risco': {
            'status': '❌ REJEITADO',
            'risco_percentual': 0.5
        }
    }
    
    try:
        # Testar formatador
        blocos = gerar_relatorio_telegram_melhorado(resultado_teste)
        
        print(f"✅ Formatador funcionando! Gerados {len(blocos)} blocos:")
        print("-" * 50)
        
        for i, bloco in enumerate(blocos, 1):
            print(f"📱 BLOCO {i}:")
            print(bloco)
            print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    testar_formatador_melhorado()









