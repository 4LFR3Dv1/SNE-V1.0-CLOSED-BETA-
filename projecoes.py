#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJEÇÕES
Gera cenários probabilísticos
"""


def projetar_cenarios(dados, confluencia_score, estrutura, fluxo):
    """Projeta 3 cenários com probabilidades"""
    
    # Verificar se dados é DataFrame ou dict
    if isinstance(dados, dict):
        # Se for dict, extrair DataFrame se disponível
        if 'dados' in dados and hasattr(dados['dados'], 'columns'):
            df = dados['dados']
        elif 'close' in dados:
            # Se tem preço direto no dict
            preco_atual = dados['close']
        else:
            # Fallback
            preco_atual = 50000
    else:
        df = dados
    
    # Verificar se a coluna 'close' existe no DataFrame
    if isinstance(dados, dict) and 'close' in dados:
        preco_atual = dados['close']
    elif hasattr(dados, 'columns') and 'close' in dados.columns:
        preco_atual = dados['close'].iloc[-1]
    elif isinstance(dados, dict) and 'preco_atual' in dados:
        preco_atual = dados['preco_atual']
    else:
        print("⚠️ Coluna 'close' não encontrada em projecoes")
        # Usar dados de fallback se disponíveis
        preco_atual = 50000  # Fallback para BTC
    
    # Resistências e suportes com fallback
    resistencias = estrutura.get('resistencias', [])
    suportes = estrutura.get('suportes', [])
    
    # Se não há resistências/suportes, criar níveis baseados no preço atual
    if not resistencias:
        resistencias = [
            {'preco': preco_atual * 1.01},
            {'preco': preco_atual * 1.02},
            {'preco': preco_atual * 1.03}
        ]
    
    if not suportes:
        suportes = [
            {'preco': preco_atual * 0.99},
            {'preco': preco_atual * 0.98}
        ]
    
    # Targets com fallback
    target1 = resistencias[0]['preco'] if resistencias else preco_atual * 1.01
    target2 = resistencias[1]['preco'] if len(resistencias) > 1 else preco_atual * 1.02
    target3 = resistencias[2]['preco'] if len(resistencias) > 2 else preco_atual * 1.03
    
    suporte1 = suportes[0]['preco'] if suportes else preco_atual * 0.99
    suporte2 = suportes[1]['preco'] if len(suportes) > 1 else preco_atual * 0.98
    
    # Probabilidades baseadas em confluência
    prob_base = (confluencia_score / 10) * 0.6
    prob_otimista = (fluxo.get('fluxo_ratio', 1) - 1) * 0.4 if fluxo else 0.2
    prob_pessimista = 1 - prob_base - prob_otimista
    
    # Ajustar para somar 100%
    total = prob_base + prob_otimista + prob_pessimista
    prob_base /= total
    prob_otimista /= total
    prob_pessimista /= total
    
    return {
        'cenario_base': {
            'probabilidade': round(prob_base * 100, 0),
            'movimento': 'Rompe resistência principal',
            'target': target1,
            'timeframe': '4-8 horas',
            'catalisador': 'Volume sustentado'
        },
        'cenario_otimista': {
            'probabilidade': round(prob_otimista * 100, 0),
            'movimento': 'Ruptura forte + continuação',
            'target': target2,
            'timeframe': '8-12 horas',
            'catalisador': 'FOMO + volume explosivo'
        },
        'cenario_pessimista': {
            'probabilidade': round(prob_pessimista * 100, 0),
            'movimento': 'Rejeição e correção',
            'target': suporte1,
            'timeframe': '2-6 horas',
            'invalidacao': suporte2
        }
    }





