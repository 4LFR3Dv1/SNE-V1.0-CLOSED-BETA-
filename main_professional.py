#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNE Radar Professional - Terminal Principal
Sistema profissional de day-trading com sinais multi-timeframe
"""

from auto_signal_system import AutoSignalSystem
from coin_scanner import ProfessionalCoinScanner
from telegram_professional import TelegramProfessional

def exibir_sinal_detalhado(sinal):
    """
    Exibe sinal de forma detalhada no terminal
    """
    print("\n" + "="*60)
    print("🎯 SINAL ENCONTRADO")
    print("="*60)
    
    tipo_emoji = "🟢" if sinal['tipo'] == 'LONG' else "🔴"
    
    print(f"\n{tipo_emoji} <b>TIPO:</b> {sinal['tipo']}")
    print(f"📊 PAR: {sinal['symbol']}")
    print(f"⚡ CONFIANÇA: {sinal['score_confianca']:.0f}%")
    print(f"📈 TIMEFRAMES: {sinal['timeframe_principal']} → {sinal['timeframe_target']}")
    
    print(f"\n💰 ENTRY: ${sinal['entry']:.4f}")
    
    print(f"\n🎯 TAKE PROFIT:")
    tp1_pct = abs((sinal['tp'][0] - sinal['entry']) / sinal['entry'] * 100)
    tp2_pct = abs((sinal['tp'][1] - sinal['entry']) / sinal['entry'] * 100)
    tp3_pct = abs((sinal['tp'][2] - sinal['entry']) / sinal['entry'] * 100)
    
    print(f"   TP1: ${sinal['tp'][0]:.4f} (+{tp1_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][0]:.1f}]")
    print(f"   TP2: ${sinal['tp'][1]:.4f} (+{tp2_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][1]:.1f}]")
    print(f"   TP3: ${sinal['tp'][2]:.4f} (+{tp3_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][2]:.1f}]")
    
    risco_pct = abs((sinal['entry'] - sinal['sl']) / sinal['entry'] * 100)
    print(f"\n🛡️ STOP LOSS: ${sinal['sl']:.4f} (-{risco_pct:.2f}%)")
    
    print(f"\n✅ CONFIRMAÇÕES:")
    for conf in sinal['confirmacoes'][:5]:
        print(f"   • {conf}")
    
    if len(sinal['confirmacoes']) > 5:
        print(f"   • +{len(sinal['confirmacoes'])-5} confirmações adicionais")
    
    print(f"\n⏰ Válido por: {sinal['validade']}")
    print("="*60)

def terminal_profissional():
    """
    Terminal simplificado e profissional
    """
    
    print("\n" + "="*60)
    print("🚀 SNE RADAR PRO - DAY TRADING ASSISTANT")
    print("="*60)
    print("Sistema profissional de sinais multi-timeframe")
    print("Desenvolvido para traders profissionais")
    print("="*60)
    
    # Inicializar sistemas
    signal_system = AutoSignalSystem()
    scanner = signal_system.scanner
    telegram = signal_system.telegram
    
    while True:
        print("\n" + "="*60)
        print("🎯 SNE RADAR PRO - MENU PRINCIPAL")
        print("="*60)
        print("\n⚡ MODO RÁPIDO")
        print("1) 🔍 Escanear Mercado (Top 30 moedas por liquidez)")
        print("2) 🎯 Melhor Sinal Multi-Timeframe AGORA")
        print("3) 🏆 Top 3 Melhores Sinais")
        print("4) 🤖 Modo Automático 24/7 (Sinais via Telegram)")
        print("\n📊 ANÁLISE AVANÇADA")
        print("5) 📈 Análise Específica (Par + Timeframe)")
        print("6) 💹 Top 10 por Volume")
        print("7) 🔥 Top 10 por Volatilidade")
        print("\n⚙️ SISTEMA")
        print("8) 📱 Testar Telegram")
        print("9) ⚙️ Configurações")
        print("0) ❌ Sair")
        print("="*60)
        
        comando = input("\nComando >> ")
        
        if comando == "1":
            # Escanear mercado
            print("\n🔍 Escaneando mercado Binance...")
            pares = scanner.escanear_mercado(force_refresh=True)
            
            if pares:
                print(f"\n✅ {len(pares)} pares com boa liquidez encontrados")
                print("\n🏆 TOP 10 POR SCORE DE LIQUIDEZ:")
                print("-"*60)
                print(f"{'#':<3} {'Par':<12} {'Volume 24h':<15} {'Spread':<10} {'Volatil':<10}")
                print("-"*60)
                
                for i, par in enumerate(pares[:10], 1):
                    print(f"{i:<3} {par['symbol']:<12} "
                          f"${par['volume_24h']/1e6:>6.1f}M      "
                          f"{par['spread']*100:>5.3f}%    "
                          f"{par['volatilidade']:>+6.2f}%")
            else:
                print("❌ Erro ao escanear mercado")
        
        elif comando == "2":
            # Melhor sinal
            melhor_sinal = signal_system.buscar_melhor_sinal_agora()
            
            if melhor_sinal:
                exibir_sinal_detalhado(melhor_sinal)
                
                # Perguntar se quer enviar
                enviar = input("\n📱 Enviar para Telegram? (s/n): ")
                if enviar.lower() == 's':
                    telegram.enviar_alerta_oportunidade(melhor_sinal)
                    mensagem = telegram.gerar_sinal_telegram_pro(melhor_sinal)
                    if telegram.enviar(mensagem):
                        print("✅ Sinal enviado para Telegram!")
                    else:
                        print("❌ Erro ao enviar para Telegram")
            else:
                print("\n⏸️  Nenhuma oportunidade de alta qualidade no momento")
                print("💡 Tente novamente em alguns minutos ou use o Modo Automático")
        
        elif comando == "3":
            # Top 3 sinais
            sinais = signal_system.buscar_top_sinais(n=3)
            
            if sinais:
                print(f"\n✅ {len(sinais)} oportunidades encontradas")
                print("\n🏆 TOP 3 SINAIS:")
                print("-"*60)
                
                for i, sinal in enumerate(sinais, 1):
                    tipo_emoji = "🟢" if sinal['tipo'] == 'LONG' else "🔴"
                    print(f"\n{i}. {tipo_emoji} {sinal['symbol']} - {sinal['tipo']}")
                    print(f"   Score: {sinal['score_confianca']:.0f}% | Entry: ${sinal['entry']:.4f}")
                    print(f"   TP1: ${sinal['tp'][0]:.4f} (R/R: 1:{sinal['risco_retorno'][0]:.1f})")
                
                print("\n" + "-"*60)
                
                # Ver detalhes
                ver_detalhes = input("\n📊 Ver detalhes de algum? (1-3 ou n): ")
                if ver_detalhes in ['1', '2', '3']:
                    idx = int(ver_detalhes) - 1
                    if idx < len(sinais):
                        exibir_sinal_detalhado(sinais[idx])
                        
                        # Enviar para Telegram
                        enviar = input("\n📱 Enviar para Telegram? (s/n): ")
                        if enviar.lower() == 's':
                            telegram.enviar_alerta_oportunidade(sinais[idx])
                            mensagem = telegram.gerar_sinal_telegram_pro(sinais[idx])
                            if telegram.enviar(mensagem):
                                print("✅ Sinal enviado para Telegram!")
                            else:
                                print("❌ Erro ao enviar para Telegram")
            else:
                print("\n⏸️  Nenhuma oportunidade no momento")
        
        elif comando == "4":
            # Modo automático
            print("\n🤖 MODO AUTOMÁTICO")
            print("="*60)
            print("Este modo irá:")
            print("• Escanear mercado a cada 60 segundos")
            print("• Analisar múltiplos timeframes")
            print("• Enviar sinais automaticamente para Telegram")
            print("• Apenas sinais com score ≥75%")
            print("\n⚠️  Pressione Ctrl+C para parar")
            print("="*60)
            
            confirmar = input("\nIniciar Modo Automático? (s/n): ")
            if confirmar.lower() == 's':
                signal_system.iniciar_modo_automatico()
        
        elif comando == "5":
            # Análise específica
            print("\n📈 ANÁLISE ESPECÍFICA")
            print("-"*60)
            symbol = input("Par (ex: BTCUSDT): ").upper()
            
            print(f"\n📊 Analisando {symbol} em múltiplos timeframes...")
            sinal = signal_system.signal_generator.analisar_multi_timeframe(symbol)
            
            if sinal:
                exibir_sinal_detalhado(sinal)
                
                enviar = input("\n📱 Enviar para Telegram? (s/n): ")
                if enviar.lower() == 's':
                    telegram.enviar_alerta_oportunidade(sinal)
                    mensagem = telegram.gerar_sinal_telegram_pro(sinal)
                    if telegram.enviar(mensagem):
                        print("✅ Sinal enviado para Telegram!")
            else:
                print(f"\n⏸️  Nenhum sinal de qualidade para {symbol} no momento")
        
        elif comando == "6":
            # Top por volume
            print("\n💹 TOP 10 POR VOLUME 24H")
            print("-"*60)
            pares = scanner.obter_top_por_volume(n=10)
            
            if pares:
                print(f"{'#':<3} {'Par':<12} {'Volume 24h':<15} {'Variação':<12}")
                print("-"*60)
                
                for i, par in enumerate(pares, 1):
                    print(f"{i:<3} {par['symbol']:<12} "
                          f"${par['volume_24h']/1e6:>6.1f}M      "
                          f"{par['price_change_pct']:>+6.2f}%")
        
        elif comando == "7":
            # Top por volatilidade
            print("\n🔥 TOP 10 POR VOLATILIDADE")
            print("-"*60)
            pares = scanner.obter_top_por_volatilidade(n=10)
            
            if pares:
                print(f"{'#':<3} {'Par':<12} {'Volatilidade':<15} {'Volume 24h':<12}")
                print("-"*60)
                
                for i, par in enumerate(pares, 1):
                    print(f"{i:<3} {par['symbol']:<12} "
                          f"{par['volatilidade']:>+6.2f}%       "
                          f"${par['volume_24h']/1e6:>6.1f}M")
        
        elif comando == "8":
            # Testar Telegram
            print("\n📱 TESTE DE TELEGRAM")
            print("-"*60)
            
            if not telegram.token or not telegram.chat_id:
                print("❌ Telegram não configurado")
                print("\n💡 Configure em xenos_bot.py:")
                print("   TELEGRAM_TOKEN = 'seu_token'")
                print("   CHAT_ID = 'seu_chat_id'")
            else:
                mensagem = "🤖 <b>Teste SNE Radar Pro</b>\n\nSistema funcionando corretamente! ✅"
                if telegram.enviar(mensagem):
                    print("✅ Mensagem de teste enviada com sucesso!")
                else:
                    print("❌ Erro ao enviar mensagem")
        
        elif comando == "9":
            # Configurações
            print("\n⚙️ CONFIGURAÇÕES")
            print("-"*60)
            print(f"1. Score mínimo para envio: {signal_system.min_score_envio}%")
            print(f"2. Intervalo de scan: {signal_system.intervalo_scan}s")
            print(f"3. Confirmações mínimas: {signal_system.signal_generator.min_confirmations}")
            print("\n0. Voltar")
            
            config = input("\nAlterar configuração (1-3 ou 0): ")
            
            if config == "1":
                novo_score = input("Novo score mínimo (60-90): ")
                try:
                    signal_system.min_score_envio = int(novo_score)
                    print(f"✅ Score mínimo alterado para {novo_score}%")
                except:
                    print("❌ Valor inválido")
            
            elif config == "2":
                novo_intervalo = input("Novo intervalo em segundos (30-300): ")
                try:
                    signal_system.intervalo_scan = int(novo_intervalo)
                    print(f"✅ Intervalo alterado para {novo_intervalo}s")
                except:
                    print("❌ Valor inválido")
            
            elif config == "3":
                novas_conf = input("Novas confirmações mínimas (2-4): ")
                try:
                    signal_system.signal_generator.min_confirmations = int(novas_conf)
                    print(f"✅ Confirmações mínimas alteradas para {novas_conf}")
                except:
                    print("❌ Valor inválido")
        
        elif comando == "0":
            print("\n👋 Até logo!")
            print("🚀 SNE Radar Pro - Sistema Profissional de Day-Trading")
            break
        
        else:
            print("❌ Comando inválido")

if __name__ == "__main__":
    try:
        terminal_profissional()
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")





