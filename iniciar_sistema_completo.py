#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicialização do Sistema SNE Completo
Inicia todos os módulos integrados
"""

import sys
import argparse
from sistema_integrado import iniciar_sistema_integrado, sistema_integrado

def menu_principal():
    """Menu principal do sistema"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🚀 SISTEMA SNE RADAR - COMPLETO 🚀            ║
║                                                          ║
║              Sistema Neural Estratégico                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

Escolha o modo de operação:

1) 🖥️  Sistema Completo (Visual + Alertas + Telegram)
2) 📊 Apenas Análise Multi-Pair (sem interface visual)
3) 🚨 Alertas + Telegram (sem interface visual)
4) 🎯 Análise Única (executar uma vez e sair)
5) ⚙️  Configuração Personalizada
6) ❌ Sair

""")
    
    escolha = input("Digite sua escolha (1-6): ").strip()
    
    if escolha == "1":
        print("\n🚀 Iniciando Sistema Completo...")
        print("📊 Interface Visual: ✅")
        print("🚨 Alertas: ✅")
        print("📱 Telegram: ✅")
        input("\nPressione ENTER para continuar...")
        iniciar_sistema_integrado(intervalo=30, telegram=True, visual=True)
    
    elif escolha == "2":
        print("\n📊 Iniciando Análise Multi-Pair...")
        print("📊 Interface Visual: ❌")
        print("🚨 Alertas: ✅")
        print("📱 Telegram: ❌")
        input("\nPressione ENTER para continuar...")
        iniciar_sistema_integrado(intervalo=30, telegram=False, visual=False)
    
    elif escolha == "3":
        print("\n🚨 Iniciando Alertas + Telegram...")
        print("📊 Interface Visual: ❌")
        print("🚨 Alertas: ✅")
        print("📱 Telegram: ✅")
        input("\nPressione ENTER para continuar...")
        iniciar_sistema_integrado(intervalo=30, telegram=True, visual=False)
    
    elif escolha == "4":
        print("\n🎯 Executando Análise Única...")
        resultado = sistema_integrado.executar_ciclo_unico()
        
        print(f"\n{'='*60}")
        print("📊 RESULTADO DA ANÁLISE")
        print(f"{'='*60}")
        print(f"🕰️ Timestamp: {resultado['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Pares Analisados: {len(resultado['resultados'])}")
        print(f"🎯 Pares Priorizados: {len(resultado['pares_priorizados'])}")
        print(f"🚨 Alertas Gerados: {len(resultado['alertas'])}")
        
        print(f"\n🏆 TOP 5 PRIORIDADES:")
        for i, par in enumerate(resultado['pares_priorizados'][:5], 1):
            print(f"{i}. {par['symbol']:10s} - Prioridade: {par['priority_score']:5.1f} | Score: {par['opportunity_score']:5.1f}")
        
        if resultado['alertas']:
            print(f"\n🚨 ALERTAS:")
            for alerta in resultado['alertas'][:5]:
                print(f"  {alerta}")
        
        print(f"\n{'='*60}")
        input("\nPressione ENTER para voltar ao menu...")
        menu_principal()
    
    elif escolha == "5":
        print("\n⚙️  CONFIGURAÇÃO PERSONALIZADA")
        print(f"{'─'*60}")
        
        try:
            intervalo = int(input("Intervalo de atualização (segundos) [30]: ") or "30")
            telegram = input("Enviar alertas para Telegram? (s/n) [s]: ").lower() != 'n'
            visual = input("Ativar interface visual? (s/n) [s]: ").lower() != 'n'
            
            print(f"\n📋 Configuração:")
            print(f"  Intervalo: {intervalo}s")
            print(f"  Telegram: {'✅' if telegram else '❌'}")
            print(f"  Visual: {'✅' if visual else '❌'}")
            
            confirmar = input("\nConfirmar e iniciar? (s/n): ").lower()
            if confirmar == 's':
                iniciar_sistema_integrado(intervalo=intervalo, telegram=telegram, visual=visual)
            else:
                menu_principal()
        
        except ValueError:
            print("❌ Valor inválido! Voltando ao menu...")
            time.sleep(2)
            menu_principal()
    
    elif escolha == "6":
        print("\n👋 Até logo!")
        sys.exit(0)
    
    else:
        print("\n❌ Opção inválida! Tente novamente...")
        import time
        time.sleep(2)
        menu_principal()

def main():
    """Função principal"""
    
    # Parser de argumentos para modo CLI
    parser = argparse.ArgumentParser(description='Sistema SNE Radar Completo')
    parser.add_argument('--intervalo', type=int, default=30, help='Intervalo de atualização em segundos')
    parser.add_argument('--no-telegram', action='store_true', help='Desativar envio para Telegram')
    parser.add_argument('--no-visual', action='store_true', help='Desativar interface visual')
    parser.add_argument('--unico', action='store_true', help='Executar análise única e sair')
    
    args = parser.parse_args()
    
    # Se argumentos CLI foram fornecidos, usar modo CLI
    if len(sys.argv) > 1:
        if args.unico:
            print("🎯 Executando análise única...")
            resultado = sistema_integrado.executar_ciclo_unico()
            print(f"✅ Análise concluída: {len(resultado['pares_priorizados'])} pares priorizados")
            sys.exit(0)
        else:
            telegram = not args.no_telegram
            visual = not args.no_visual
            print(f"🚀 Iniciando sistema com configurações CLI...")
            iniciar_sistema_integrado(intervalo=args.intervalo, telegram=telegram, visual=visual)
    else:
        # Modo interativo com menu
        menu_principal()

if __name__ == "__main__":
    main()




