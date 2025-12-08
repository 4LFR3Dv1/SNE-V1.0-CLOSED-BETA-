#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALERTAS TÉCNICOS - Sistema de notificações inteligentes
"""

from motor_renan import analise_completa
from xenos_bot import enviar_oraculo


def configurar_alertas():
    """Configura alertas técnicos"""
    
    print("\n🔔 CONFIGURAR ALERTAS TÉCNICOS")
    print("="*60)
    
    # Par
    par = input("\n📊 Par para monitorar (ex: BTCUSDT): ").upper().strip()
    if not par:
        par = "BTCUSDT"
    
    # Tipo de alerta
    print("\n📋 Tipos de alerta:")
    print("1) Score de confluência >= X")
    print("2) Regime específico (Bull/Bear)")
    print("3) Ruptura de zona magnética")
    print("4) Pressão DOM extrema")
    
    tipo = input("\nEscolha o tipo (1-4): ").strip()
    
    config = {'par': par, 'tipo': tipo}
    
    if tipo == '1':
        score_min = input("Score mínimo (1-10): ").strip()
        config['score_min'] = float(score_min) if score_min else 7.0
    elif tipo == '2':
        regime = input("Regime (BULL_TREND/BEAR_TREND): ").upper().strip()
        config['regime'] = regime if regime else 'BULL_TREND'
    
    print(f"\n✅ Alerta configurado para {par}")
    print(f"   Tipo: {tipo}")
    
    return config


def verificar_alertas(config):
    """Verifica condições e dispara alertas"""
    
    par = config['par']
    tipo = config['tipo']
    
    print(f"\n🔍 Verificando alertas para {par}...")
    
    analise = analise_completa(par, "1h")
    
    if 'erro' in analise:
        print("❌ Erro na análise")
        return
    
    disparar = False
    mensagem = ""
    
    # Tipo 1: Score
    if tipo == '1':
        score = analise['confluencia']['score']
        score_min = config.get('score_min', 7.0)
        
        if score >= score_min:
            disparar = True
            mensagem = f"""
🔔 <b>ALERTA DE CONFLUÊNCIA</b>

📊 {par}
💡 Score: {score}/10 (>= {score_min})

📈 Viés: {analise['sintese']['vies']}
✨ Recomendação: {analise['sintese']['recomendacao']}

Entry: {analise['sintese']['entry_type']}
Risco: {analise['sintese']['risco']}
"""
    
    # Tipo 2: Regime
    elif tipo == '2':
        regime_alvo = config.get('regime', 'BULL_TREND')
        regime_atual = analise['contexto']['regime']
        
        if regime_atual == regime_alvo:
            disparar = True
            mensagem = f"""
🔔 <b>ALERTA DE REGIME</b>

📊 {par}
📈 Regime: {regime_atual}
💪 Força: {analise['contexto']['forca_regime']}/10

✨ Recomendação: {analise['sintese']['recomendacao']}
"""
    
    # Tipo 3: Zona magnética
    elif tipo == '3':
        zona = analise['zonas']
        if zona['distancia_pct'] and zona['distancia_pct'] < 0.5:
            disparar = True
            mensagem = f"""
🔔 <b>ALERTA DE ZONA MAGNÉTICA</b>

📊 {par}
🧲 Zona Próxima: ${zona['zona_proxima']:,.2f}
📏 Distância: {zona['distancia_pct']:.2f}%

⚠️ Possível reação no preço!
"""
    
    # Tipo 4: DOM
    elif tipo == '4':
        fluxo = analise['fluxo']
        if 'fluxo_ratio' in fluxo:
            ratio = fluxo['fluxo_ratio']
            if ratio > 1.5 or ratio < 0.5:
                disparar = True
                pressao = "COMPRA" if ratio > 1 else "VENDA"
                mensagem = f"""
🔔 <b>ALERTA DE PRESSÃO DOM</b>

📊 {par}
🌊 Pressão: {pressao}
📊 Ratio: {ratio:.3f}

⚡ Desequilíbrio extremo detectado!
"""
    
    # Disparar alerta
    if disparar:
        print(f"🔔 ALERTA DISPARADO!")
        print(mensagem)
        enviar_oraculo(mensagem)
        print("✅ Enviado para Telegram!")
    else:
        print("✅ Nenhum alerta disparado")


def monitorar_alertas(config, intervalo=300):
    """Monitora alertas continuamente"""
    import time
    
    print(f"\n🔔 MONITORANDO ALERTAS...")
    print(f"⏰ Verificação a cada {intervalo}s")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        while True:
            verificar_alertas(config)
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("\n\n✅ Monitoramento finalizado.")




