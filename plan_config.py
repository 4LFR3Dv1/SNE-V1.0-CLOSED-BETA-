#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURAÇÕES DE PLANOS E PREÇOS - SNE RADAR 3.0
Definição de planos, preços e funcionalidades
"""

from typing import Dict, List, Any
from datetime import timedelta

# ===========================================
# CONFIGURAÇÕES DE PLANOS
# ===========================================
PLANOS = {
    'free': {
        'nome': 'Free',
        'preco': 0,
        'preco_anual': 0,
        'desconto_anual': 0,
        'analises_dia': 3,
        'timeframes': ['1h'],
        'funcionalidades': [
            'demo',
            'start', 
            'ajuda',
            'termos',
            'contato'
        ],
        'recursos': [
            'Análise básica (1 par, 1 timeframe)',
            'Suporte por Telegram',
            'Acesso limitado'
        ],
        'limites': {
            'alertas': 0,
            'relatorios': 0,
            'backtest': 0,
            'api_calls': 0
        },
        'descricao': 'Plano gratuito para testar o sistema'
    },
    
    'premium': {
        'nome': 'Premium',
        'preco': 199,
        'preco_anual': 1592,  # 20% desconto
        'desconto_anual': 20,
        'analises_dia': 50,
        'timeframes': ['1m', '5m', '15m', '30m', '1h', '4h'],
        'funcionalidades': [
            'analise',
            'relatorio',
            'alertas',
            'backtest',
            'dom',
            'magnetico',
            'risco',
            'minha_assinatura',
            'config'
        ],
        'recursos': [
            'Análise multi-timeframe completa',
            'Relatórios técnicos automáticos',
            'Sistema de alertas personalizados',
            'Backtest de estratégias',
            'DOM Analysis exclusivo',
            'Zonas magnéticas',
            'Gestão de risco profissional',
            'Suporte prioritário'
        ],
        'limites': {
            'alertas': 20,
            'relatorios': 10,
            'backtest': 5,
            'api_calls': 1000
        },
        'descricao': 'Plano profissional para traders ativos'
    },
    
    'institutional': {
        'nome': 'Institutional',
        'preco': 799,
        'preco_anual': 6392,  # 20% desconto
        'desconto_anual': 20,
        'analises_dia': 1000,
        'timeframes': ['all'],
        'funcionalidades': [
            'all',  # Todas as funcionalidades
            'api',
            'whitelabel',
            'automacao',
            'multi_pair',
            'exportar',
            'estatisticas',
            'admin'
        ],
        'recursos': [
            'Todas as funcionalidades Premium',
            'Análise multi-pair simultânea',
            'Automação 24/7',
            'Acesso à API completa',
            'Whitelabel personalizado',
            'Exportação de dados',
            'Estatísticas avançadas',
            'Suporte dedicado',
            'Treinamento personalizado'
        ],
        'limites': {
            'alertas': 100,
            'relatorios': 100,
            'backtest': 50,
            'api_calls': 10000
        },
        'descricao': 'Plano institucional para empresas e traders profissionais'
    }
}

# ===========================================
# CONFIGURAÇÕES DE PAGAMENTO
# ===========================================
PAGAMENTO_CONFIG = {
    'moeda': 'BRL',
    'metodos': {
        'pix': {
            'nome': 'PIX',
            'taxa': 0,
            'prazo': 'Imediato',
            'disponivel': True,
            'chave': 'sne.radar@email.com'  # Substituir pela chave real
        },
        'mercadopago': {
            'nome': 'Mercado Pago',
            'taxa': 2.99,
            'prazo': 'Imediato',
            'disponivel': True,
            'access_token': 'SEU_ACCESS_TOKEN'  # Substituir pelo token real
        },
        'stripe': {
            'nome': 'Stripe (Cartão)',
            'taxa': 3.49,
            'prazo': 'Imediato',
            'disponivel': True,
            'publishable_key': 'pk_test_...',  # Substituir pela chave real
            'secret_key': 'sk_test_...'  # Substituir pela chave real
        }
    },
    'descontos': {
        'anual': 20,  # 20% desconto para pagamento anual
        'semestral': 10,  # 10% desconto para pagamento semestral
        'trimestral': 5   # 5% desconto para pagamento trimestral
    }
}

# ===========================================
# CONFIGURAÇÕES DE FUNCIONALIDADES
# ===========================================
FUNCIONALIDADES = {
    'analise': {
        'nome': 'Análise Técnica',
        'descricao': 'Análise multi-timeframe completa com confluência',
        'requer_premium': True,
        'timeout': 30,  # segundos
        'cache_ttl': 300  # 5 minutos
    },
    'relatorio': {
        'nome': 'Relatórios Técnicos',
        'descricao': 'Relatórios automáticos (horário, diário, semanal)',
        'requer_premium': True,
        'timeout': 60,
        'cache_ttl': 600  # 10 minutos
    },
    'alertas': {
        'nome': 'Sistema de Alertas',
        'descricao': 'Alertas personalizados por preço e condições',
        'requer_premium': True,
        'timeout': 5,
        'cache_ttl': 60
    },
    'backtest': {
        'nome': 'Backtest de Estratégias',
        'descricao': 'Teste histórico de estratégias de trading',
        'requer_premium': True,
        'timeout': 120,
        'cache_ttl': 1800  # 30 minutos
    },
    'dom': {
        'nome': 'DOM Analysis',
        'descricao': 'Análise profunda de liquidez e ordem book',
        'requer_premium': True,
        'timeout': 15,
        'cache_ttl': 180
    },
    'magnetico': {
        'nome': 'Zonas Magnéticas',
        'descricao': 'Detecção de zonas de atração de preços',
        'requer_premium': True,
        'timeout': 20,
        'cache_ttl': 300
    },
    'risco': {
        'nome': 'Gestão de Risco',
        'descricao': 'Cálculo profissional de posição e risco',
        'requer_premium': True,
        'timeout': 10,
        'cache_ttl': 300
    },
    'api': {
        'nome': 'API Access',
        'descricao': 'Acesso programático à API do SNE Radar',
        'requer_institutional': True,
        'timeout': 5,
        'cache_ttl': 60
    },
    'whitelabel': {
        'nome': 'Whitelabel',
        'descricao': 'Personalização completa da marca',
        'requer_institutional': True,
        'timeout': 0,
        'cache_ttl': 0
    },
    'automacao': {
        'nome': 'Automação 24/7',
        'descricao': 'Monitoramento e análise automática contínua',
        'requer_institutional': True,
        'timeout': 0,
        'cache_ttl': 0
    }
}

# ===========================================
# CONFIGURAÇÕES DE LIMITES E RATE LIMITING
# ===========================================
RATE_LIMITS = {
    'free': {
        'comandos_minuto': 5,
        'analises_dia': 3,
        'alertas_max': 0,
        'relatorios_dia': 0,
        'backtest_dia': 0
    },
    'premium': {
        'comandos_minuto': 20,
        'analises_dia': 50,
        'alertas_max': 20,
        'relatorios_dia': 10,
        'backtest_dia': 5
    },
    'institutional': {
        'comandos_minuto': 100,
        'analises_dia': 1000,
        'alertas_max': 100,
        'relatorios_dia': 100,
        'backtest_dia': 50
    }
}

# ===========================================
# CONFIGURAÇÕES DE NOTIFICAÇÕES
# ===========================================
NOTIFICACOES = {
    'pagamento_aprovado': {
        'template': '✅ Pagamento aprovado! Acesso premium liberado.',
        'enviar_telegram': True,
        'enviar_email': False
    },
    'pagamento_rejeitado': {
        'template': '❌ Pagamento rejeitado. Tente novamente.',
        'enviar_telegram': True,
        'enviar_email': False
    },
    'assinatura_expirando': {
        'template': '⚠️ Sua assinatura expira em {dias} dias. Renove com /assinar',
        'enviar_telegram': True,
        'enviar_email': True,
        'dias_antecedencia': 7
    },
    'assinatura_expirada': {
        'template': '❌ Sua assinatura expirou. Renove com /assinar',
        'enviar_telegram': True,
        'enviar_email': True
    },
    'limite_atingido': {
        'template': '⚠️ Limite diário atingido. Upgrade para mais análises.',
        'enviar_telegram': True,
        'enviar_email': False
    }
}

# ===========================================
# CONFIGURAÇÕES DE MARKETING
# ===========================================
MARKETING = {
    'promocoes': {
        'primeiro_mes': {
            'desconto': 50,
            'plano': 'premium',
            'valido_ate': '2025-12-31',
            'codigo': 'PRIMEIROMES50'
        },
        'black_friday': {
            'desconto': 30,
            'plano': 'all',
            'valido_ate': '2025-11-30',
            'codigo': 'BLACKFRIDAY30'
        }
    },
    'afiliados': {
        'comissao_percentual': 20,
        'comissao_fixa': 0,
        'minimo_pagamento': 100,
        'periodo_cookie': 30  # dias
    },
    'referencias': {
        'desconto_referidor': 10,  # % desconto para quem indica
        'desconto_referido': 20,   # % desconto para quem é indicado
        'max_referencias': 5       # máximo de referências por usuário
    }
}

# ===========================================
# FUNÇÕES UTILITÁRIAS
# ===========================================
def get_plano_info(plano: str) -> Dict[str, Any]:
    """
    Obtém informações de um plano
    
    Args:
        plano: Nome do plano
        
    Returns:
        Dict: Informações do plano
    """
    return PLANOS.get(plano, {})

def get_preco_plano(plano: str, periodo: str = 'mensal') -> float:
    """
    Obtém preço de um plano
    
    Args:
        plano: Nome do plano
        periodo: 'mensal', 'trimestral', 'semestral', 'anual'
        
    Returns:
        float: Preço do plano
    """
    plano_info = get_plano_info(plano)
    if not plano_info:
        return 0
    
    preco_base = plano_info['preco']
    
    if periodo == 'anual':
        return plano_info['preco_anual']
    elif periodo == 'semestral':
        desconto = PAGAMENTO_CONFIG['descontos']['semestral']
        return preco_base * 6 * (1 - desconto / 100)
    elif periodo == 'trimestral':
        desconto = PAGAMENTO_CONFIG['descontos']['trimestral']
        return preco_base * 3 * (1 - desconto / 100)
    else:  # mensal
        return preco_base

def verificar_funcionalidade_disponivel(plano: str, funcionalidade: str) -> bool:
    """
    Verifica se uma funcionalidade está disponível para um plano
    
    Args:
        plano: Nome do plano
        funcionalidade: Nome da funcionalidade
        
    Returns:
        bool: True se disponível
    """
    plano_info = get_plano_info(plano)
    if not plano_info:
        return False
    
    funcionalidades_plano = plano_info.get('funcionalidades', [])
    
    # Verificar se tem acesso a todas as funcionalidades
    if 'all' in funcionalidades_plano:
        return True
    
    # Verificar funcionalidade específica
    return funcionalidade in funcionalidades_plano

def get_limites_plano(plano: str) -> Dict[str, int]:
    """
    Obtém limites de um plano
    
    Args:
        plano: Nome do plano
        
    Returns:
        Dict: Limites do plano
    """
    return RATE_LIMITS.get(plano, RATE_LIMITS['free'])

def calcular_desconto(plano: str, periodo: str) -> float:
    """
    Calcula desconto para um plano e período
    
    Args:
        plano: Nome do plano
        periodo: Período de pagamento
        
    Returns:
        float: Percentual de desconto
    """
    if periodo == 'anual':
        return PAGAMENTO_CONFIG['descontos']['anual']
    elif periodo == 'semestral':
        return PAGAMENTO_CONFIG['descontos']['semestral']
    elif periodo == 'trimestral':
        return PAGAMENTO_CONFIG['descontos']['trimestral']
    else:
        return 0

def formatar_preco(preco: float, moeda: str = 'BRL') -> str:
    """
    Formata preço para exibição
    
    Args:
        preco: Preço a ser formatado
        moeda: Moeda
        
    Returns:
        str: Preço formatado
    """
    if moeda == 'BRL':
        return f"R$ {preco:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    else:
        return f"${preco:,.2f}"

def get_plano_recomendado(uso_estimado: str) -> str:
    """
    Recomenda plano baseado no uso estimado
    
    Args:
        uso_estimado: 'baixo', 'medio', 'alto', 'institucional'
        
    Returns:
        str: Plano recomendado
    """
    recomendacoes = {
        'baixo': 'free',
        'medio': 'premium',
        'alto': 'premium',
        'institucional': 'institutional'
    }
    
    return recomendacoes.get(uso_estimado, 'free')

# ===========================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# ===========================================
DEV_CONFIG = {
    'test_mode': True,
    'test_users': ['123456789', '987654321'],
    'test_plans': ['free', 'premium'],
    'mock_payments': True,
    'debug_logs': True
}

if __name__ == "__main__":
    # Teste das configurações de planos
    print("🧪 Testando configurações de planos do SNE Radar 3.0...")
    
    try:
        # Testar informações de planos
        print("\n📋 Informações dos planos:")
        for plano, info in PLANOS.items():
            print(f"\n🔹 {info['nome']} ({plano}):")
            print(f"   Preço mensal: {formatar_preco(info['preco'])}")
            print(f"   Preço anual: {formatar_preco(info['preco_anual'])}")
            print(f"   Análises/dia: {info['analises_dia']}")
            print(f"   Timeframes: {', '.join(info['timeframes'])}")
            print(f"   Funcionalidades: {len(info['funcionalidades'])}")
        
        # Testar verificações de funcionalidades
        print(f"\n🔍 Testando verificações de funcionalidades:")
        funcionalidades_teste = ['analise', 'relatorio', 'api', 'whitelabel']
        
        for plano in ['free', 'premium', 'institutional']:
            print(f"\n   Plano {plano}:")
            for func in funcionalidades_teste:
                disponivel = verificar_funcionalidade_disponivel(plano, func)
                status = "✅" if disponivel else "❌"
                print(f"     {status} {func}")
        
        # Testar cálculos de preço
        print(f"\n💰 Testando cálculos de preço:")
        for plano in ['premium', 'institutional']:
            for periodo in ['mensal', 'trimestral', 'semestral', 'anual']:
                preco = get_preco_plano(plano, periodo)
                desconto = calcular_desconto(plano, periodo)
                print(f"   {plano} {periodo}: {formatar_preco(preco)} (desconto: {desconto}%)")
        
        # Testar limites
        print(f"\n📊 Testando limites:")
        for plano in ['free', 'premium', 'institutional']:
            limites = get_limites_plano(plano)
            print(f"   {plano}: {limites}")
        
        print("\n✅ Configurações de planos testadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao testar configurações: {e}")
