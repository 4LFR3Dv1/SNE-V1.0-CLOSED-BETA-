#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Templates HTML Terminal/Hacker para SNE Radar
Interface com fundo preto, fontes Courier e cores contrastantes
"""

import os

def create_terminal_templates():
    """Cria templates HTML com estilo terminal"""
    
    base_template = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SNE Radar{% endblock %}</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background-color: #000000;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
            overflow-x: hidden;
        }
        
        .terminal-header {
            background: linear-gradient(90deg, #000000 0%, #1a1a1a 50%, #000000 100%);
            border-bottom: 2px solid #00ff00;
            padding: 10px 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        
        .terminal-title {
            color: #00ff00;
            font-size: 24px;
            font-weight: bold;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .terminal-subtitle {
            color: #00aa00;
            font-size: 12px;
        }
        
        .status-online {
            color: #00ff00;
            animation: blink 1s infinite;
        }
        
        .status-offline {
            color: #ff0000;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        .terminal-container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .terminal-card {
            background-color: #0a0a0a;
            border: 1px solid #00ff00;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        }
        
        .terminal-card:hover {
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.4);
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }
        
        .card-title {
            color: #00ff00;
            font-size: 16px;
            font-weight: bold;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }
        
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin: 10px 0;
        }
        
        .data-item {
            background-color: #111111;
            border: 1px solid #333333;
            padding: 8px;
            border-radius: 3px;
        }
        
        .data-label {
            color: #00aa00;
            font-size: 11px;
            text-transform: uppercase;
        }
        
        .data-value {
            color: #00ff00;
            font-size: 14px;
            font-weight: bold;
        }
        
        .data-value.positive {
            color: #00ff00;
        }
        
        .data-value.negative {
            color: #ff0000;
        }
        
        .data-value.warning {
            color: #ffff00;
        }
        
        .alert-rupture {
            background-color: #1a0000;
            border: 2px solid #ff0000;
            color: #ff0000;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            animation: pulse-red 2s infinite;
        }
        
        .alert-buy {
            background-color: #001a00;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            animation: pulse-green 2s infinite;
        }
        
        .alert-sell {
            background-color: #1a0000;
            border: 2px solid #ff0000;
            color: #ff0000;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            animation: pulse-red 2s infinite;
        }
        
        .alert-bullish {
            background-color: #001a00;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 8px;
            margin: 5px 0;
            border-radius: 3px;
        }
        
        .alert-bearish {
            background-color: #1a0000;
            border: 2px solid #ff0000;
            color: #ff0000;
            padding: 8px;
            margin: 5px 0;
            border-radius: 3px;
        }
        
        .alert-neutral {
            background-color: #1a1a00;
            border: 2px solid #ffff00;
            color: #ffff00;
            padding: 8px;
            margin: 5px 0;
            border-radius: 3px;
        }
        
        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 5px rgba(255, 0, 0, 0.5); }
            50% { box-shadow: 0 0 20px rgba(255, 0, 0, 0.8); }
        }
        
        @keyframes pulse-green {
            0%, 100% { box-shadow: 0 0 5px rgba(0, 255, 0, 0.5); }
            50% { box-shadow: 0 0 20px rgba(0, 255, 0, 0.8); }
        }
        
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: radial-gradient(circle, #000000 0%, #0a0a0a 100%);
        }
        
        .login-form {
            background-color: #0a0a0a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 30px;
            width: 400px;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.3);
        }
        
        .login-title {
            text-align: center;
            color: #00ff00;
            font-size: 28px;
            margin-bottom: 20px;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            color: #00aa00;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
            display: block;
        }
        
        .form-input {
            width: 100%;
            background-color: #000000;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            border-radius: 3px;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .btn-primary {
            width: 100%;
            background-color: #000000;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            background-color: #00ff00;
            color: #000000;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.8);
        }
        
        .btn-danger {
            background-color: #000000;
            border: 2px solid #ff0000;
            color: #ff0000;
            padding: 8px 16px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            cursor: pointer;
            border-radius: 3px;
            transition: all 0.3s ease;
        }
        
        .btn-danger:hover {
            background-color: #ff0000;
            color: #000000;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.8);
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .grid-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }
        
        .grid-4 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 15px;
        }
        
        .status-bar {
            background-color: #0a0a0a;
            border: 1px solid #00ff00;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        
        .status-item {
            display: inline-block;
            margin-right: 20px;
            color: #00aa00;
        }
        
        .status-value {
            color: #00ff00;
            font-weight: bold;
        }
        
        .scroll-container {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #333333;
            padding: 10px;
            background-color: #0a0a0a;
        }
        
        .scroll-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .scroll-container::-webkit-scrollbar-track {
            background: #000000;
        }
        
        .scroll-container::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 4px;
        }
        
        .scroll-container::-webkit-scrollbar-thumb:hover {
            background: #00aa00;
        }
        
        .compact-card {
            background-color: #0a0a0a;
            border: 1px solid #00ff00;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        }
        
        .compact-title {
            color: #00ff00;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .compact-content {
            color: #00aa00;
            font-size: 12px;
            line-height: 1.4;
        }
        
        .market-summary {
            background-color: #0a0a0a;
            border: 1px solid #00ff00;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .summary-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .summary-symbol {
            color: #00ff00;
            font-size: 18px;
            font-weight: bold;
        }
        
        .summary-price {
            color: #00ff00;
            font-size: 20px;
            font-weight: bold;
        }
        
        .summary-change {
            font-size: 14px;
            font-weight: bold;
        }
        
        .summary-change.positive {
            color: #00ff00;
        }
        
        .summary-change.negative {
            color: #ff0000;
        }
        
        .summary-metrics {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-top: 10px;
        }
        
        .metric-item {
            background-color: #111111;
            border: 1px solid #333333;
            padding: 6px;
            border-radius: 3px;
            text-align: center;
        }
        
        .metric-label {
            color: #00aa00;
            font-size: 10px;
            text-transform: uppercase;
        }
        
        .metric-value {
            color: #00ff00;
            font-size: 12px;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 {
                grid-template-columns: 1fr;
            }
            
            .data-grid {
                grid-template-columns: 1fr;
            }
            
            .summary-metrics {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>'''
    
    login_template = '''{% extends "base.html" %}
{% block title %}Login - SNE Radar{% endblock %}
{% block content %}
<div class="login-container">
    <div class="login-form">
        <div class="login-title">
            <i class="fas fa-rocket"></i> SNE RADAR
        </div>
        <div style="text-align: center; color: #00aa00; margin-bottom: 20px; font-size: 12px;">
            SISTEMA NEURAL ESTRATÉGICO
        </div>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div style="background-color: #1a0000; border: 1px solid #ff0000; color: #ff0000; padding: 10px; margin-bottom: 15px; border-radius: 3px;">
                        <i class="fas fa-exclamation-triangle"></i> {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">USUÁRIO</label>
                <input type="text" name="username" required class="form-input">
            </div>
            <div class="form-group">
                <label class="form-label">SENHA</label>
                <input type="password" name="password" required class="form-input">
            </div>
            <button type="submit" class="btn-primary">
                <i class="fas fa-sign-in-alt"></i> ENTRAR NO SISTEMA
            </button>
        </form>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="{{ url_for('register') }}" style="color: #00ff00; text-decoration: none; font-size: 12px;">
                <i class="fas fa-user-plus"></i> CRIAR CONTA
            </a>
        </div>
    </div>
</div>
{% endblock %}'''
    
    register_template = '''{% extends "base.html" %}
{% block title %}Registro - SNE Radar{% endblock %}
{% block content %}
<div class="login-container">
    <div class="login-form">
        <div class="login-title">
            <i class="fas fa-user-plus"></i> SNE RADAR
        </div>
        <div style="text-align: center; color: #00aa00; margin-bottom: 20px; font-size: 12px;">
            CRIAR NOVA CONTA
        </div>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div style="background-color: #1a0000; border: 1px solid #ff0000; color: #ff0000; padding: 10px; margin-bottom: 15px; border-radius: 3px;">
                        <i class="fas fa-exclamation-triangle"></i> {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">USUÁRIO</label>
                <input type="text" name="username" required class="form-input">
            </div>
            <div class="form-group">
                <label class="form-label">SENHA</label>
                <input type="password" name="password" required class="form-input">
            </div>
            <button type="submit" class="btn-primary">
                <i class="fas fa-user-plus"></i> CRIAR CONTA
            </button>
        </form>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="{{ url_for('login') }}" style="color: #00ff00; text-decoration: none; font-size: 12px;">
                <i class="fas fa-sign-in-alt"></i> JÁ TEM CONTA? ENTRAR
            </a>
        </div>
    </div>
</div>
{% endblock %}'''
    
    dashboard_template = '''{% extends "base.html" %}
{% block title %}Dashboard Terminal - SNE Radar{% endblock %}
{% block content %}
<div class="terminal-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="terminal-title">
                <i class="fas fa-rocket"></i> SNE RADAR
            </div>
            <div class="terminal-subtitle">
                SISTEMA NEURAL ESTRATÉGICO DE ANÁLISE DE MERCADO
            </div>
        </div>
        <div style="text-align: right;">
            <div class="status-online">
                <i class="fas fa-circle"></i> SISTEMA ONLINE
            </div>
            <div style="color: #00aa00; font-size: 12px;">
                USUÁRIO: {{ current_user.username }}
            </div>
            <div style="color: #00aa00; font-size: 12px;" id="current-time"></div>
        </div>
    </div>
</div>

<div class="terminal-container">
    <!-- Status Bar -->
    <div class="status-bar">
        <div class="status-item">
            <i class="fas fa-chart-line"></i> ANÁLISE: <span class="status-value status-online">ATIVA</span>
        </div>
        <div class="status-item">
            <i class="fas fa-database"></i> DADOS: <span class="status-value status-online">SALVOS</span>
        </div>
        <div class="status-item">
            <i class="fas fa-bell"></i> ALERTAS: <span class="status-value" id="alert-count">0</span>
        </div>
        <div class="status-item">
            <i class="fas fa-brain"></i> IA: <span class="status-value status-online">ATIVA</span>
        </div>
        <div style="float: right;">
            <a href="{{ url_for('logout') }}" class="btn-danger">
                <i class="fas fa-sign-out-alt"></i> SAIR
            </a>
        </div>
    </div>

    <!-- Market Summary -->
    <div id="market-summary">
        <!-- Resumos dos mercados serão carregados aqui -->
    </div>

    <!-- Main Content -->
    <div class="grid-3">
        <!-- Market Data -->
        <div class="terminal-card">
            <div class="card-title">
                <i class="fas fa-chart-candlestick"></i> DADOS DETALHADOS
            </div>
            <div id="market-data">
                <!-- Dados detalhados serão carregados aqui -->
            </div>
        </div>
        
        <!-- Strategies -->
        <div class="terminal-card">
            <div class="card-title">
                <i class="fas fa-chess"></i> ESTRATÉGIAS
            </div>
            <div id="estrategias" class="scroll-container">
                <div style="color: #00aa00; font-size: 12px;">
                    Aguardando dados de mercado...
                </div>
            </div>
        </div>
        
        <!-- Interpretation -->
        <div class="terminal-card">
            <div class="card-title">
                <i class="fas fa-eye"></i> INTERPRETAÇÃO
            </div>
            <div id="interpretacao" class="scroll-container">
                <div style="color: #00aa00; font-size: 12px;">
                    Aguardando análise...
                </div>
            </div>
        </div>
    </div>

    <div class="grid-2">
        <!-- Trading Tips -->
        <div class="terminal-card">
            <div class="card-title">
                <i class="fas fa-lightbulb"></i> DICAS DE TRADING
            </div>
            <div id="dicas" class="scroll-container">
                <div style="color: #00aa00; font-size: 12px;">
                    💰 Nunca arrisque mais de 2% por trade<br>
                    💰 Use sempre stop loss<br>
                    💰 Diversifique posições
                </div>
            </div>
        </div>
        
        <!-- Alerts -->
        <div class="terminal-card">
            <div class="card-title">
                <i class="fas fa-exclamation-triangle"></i> ALERTAS E NOTIFICAÇÕES
            </div>
            <div id="alerts" class="scroll-container">
                <div style="color: #00aa00; font-size: 12px;">
                    Monitorando rupturas e sinais...
                </div>
            </div>
        </div>
    </div>
</div>

<script>
const socket = io();

socket.on('connect', function() {
    console.log('Conectado ao servidor SNE Radar');
});

socket.on('market_data', function(data) {
    updateMarketSummary(data);
    updateMarketData(data);
    updateEstrategias(data);
    updateInterpretacao(data);
    updateDicas(data);
});

function updateMarketSummary(data) {
    const container = document.getElementById('market-summary');
    const symbol = data.symbol;
    const marketData = data.data;
    
    let existingElement = container.querySelector(`[data-symbol="${symbol}"]`);
    let html = `
        <div class="market-summary" data-symbol="${symbol}">
            <div class="summary-header">
                <div class="summary-symbol">${symbol}</div>
                <div>
                    <div class="summary-price">$${marketData.price.toFixed(2)}</div>
                    <div class="summary-change ${marketData.variacao_preco >= 0 ? 'positive' : 'negative'}">
                        ${marketData.variacao_preco >= 0 ? '+' : ''}${marketData.variacao_preco.toFixed(2)}%
                    </div>
                </div>
            </div>
            <div class="summary-metrics">
                <div class="metric-item">
                    <div class="metric-label">Tendência</div>
                    <div class="metric-value ${marketData.tendencia_curta === 'BULLISH' ? 'positive' : 'negative'}">${marketData.tendencia_curta}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">RSI</div>
                    <div class="metric-value ${marketData.rsi > 70 ? 'negative' : marketData.rsi < 30 ? 'positive' : 'warning'}">${marketData.rsi.toFixed(1)}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Volume</div>
                    <div class="metric-value ${marketData.volume_ratio > 1.5 ? 'positive' : marketData.volume_ratio < 0.5 ? 'negative' : 'warning'}">${marketData.volume_ratio.toFixed(1)}x</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Volatilidade</div>
                    <div class="metric-value">${marketData.volatilidade.toFixed(1)}%</div>
                </div>
            </div>
            ${marketData.rupture ? `
                <div class="alert-rupture" style="margin-top: 10px;">
                    <i class="fas fa-exclamation-triangle"></i> <strong>RUPTURA!</strong> ${marketData.percentual_ruptura.toFixed(1)}%
                </div>
            ` : ''}
            ${marketData.sinal_compra ? `
                <div class="alert-buy" style="margin-top: 10px;">
                    <i class="fas fa-arrow-up"></i> <strong>COMPRA</strong>
                </div>
            ` : ''}
            ${marketData.sinal_venda ? `
                <div class="alert-sell" style="margin-top: 10px;">
                    <i class="fas fa-arrow-down"></i> <strong>VENDA</strong>
                </div>
            ` : ''}
        </div>
    `;
    
    if (existingElement) {
        existingElement.outerHTML = html;
    } else {
        container.innerHTML += html;
    }
}

function updateMarketData(data) {
    const container = document.getElementById('market-data');
    const symbol = data.symbol;
    const marketData = data.data;
    
    let html = `
        <div class="compact-card" data-symbol="${symbol}">
            <div class="compact-title">${symbol} - Análise Detalhada</div>
            <div class="compact-content">
                <div style="margin-bottom: 8px;">
                    <strong>Preço:</strong> $${marketData.price.toFixed(2)} 
                    <span style="color: ${marketData.variacao_preco >= 0 ? '#00ff00' : '#ff0000'};">
                        (${marketData.variacao_preco >= 0 ? '+' : ''}${marketData.variacao_preco.toFixed(2)}%)
                    </span>
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>Médias Móveis:</strong> EMA8: $${marketData.ema8.toFixed(2)} | EMA21: $${marketData.ema21.toFixed(2)} | SMA200: $${marketData.sma200.toFixed(2)}
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>Tendências:</strong> Curta: <span style="color: ${marketData.tendencia_curta === 'BULLISH' ? '#00ff00' : '#ff0000'};">${marketData.tendencia_curta}</span> | 
                    Longa: <span style="color: ${marketData.tendencia_longa === 'BULLISH' ? '#00ff00' : '#ff0000'};">${marketData.tendencia_longa}</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>Indicadores:</strong> RSI: ${marketData.rsi.toFixed(1)} | Volume: ${marketData.volume_ratio.toFixed(2)}x | Volatilidade: ${marketData.volatilidade.toFixed(2)}%
                </div>
                <div>
                    <strong>Suporte/Resistência:</strong> $${marketData.suporte.toFixed(2)} / $${marketData.resistencia.toFixed(2)}
                </div>
            </div>
        </div>
    `;
    
    let existingElement = container.querySelector(`[data-symbol="${symbol}"]`);
    if (existingElement) {
        existingElement.outerHTML = html;
    } else {
        container.innerHTML += html;
    }
}

function updateEstrategias(data) {
    const container = document.getElementById('estrategias');
    const marketData = data.data;
    
    let html = `
        <div class="compact-card">
            <div class="compact-title">Estratégia Atual</div>
            <div class="compact-content">
                ${marketData.estrategia.split(' | ').map(strat => `
                    <div style="margin-bottom: 5px; padding: 3px; background-color: #111111; border-radius: 3px;">
                        ${strat}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function updateInterpretacao(data) {
    const container = document.getElementById('interpretacao');
    const marketData = data.data;
    
    let html = `
        <div class="compact-card">
            <div class="compact-title">Interpretação do Mercado</div>
            <div class="compact-content">
                ${marketData.interpretacao.split(' | ').map(interp => `
                    <div style="margin-bottom: 5px; padding: 3px; background-color: #111111; border-radius: 3px;">
                        ${interp}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function updateDicas(data) {
    const container = document.getElementById('dicas');
    const marketData = data.data;
    
    let html = '';
    marketData.dicas.forEach(dica => {
        const color = dica.includes('✅') ? '#00ff00' : dica.includes('❌') ? '#ff0000' : dica.includes('⚠️') ? '#ffff00' : dica.includes('🚨') ? '#ff0000' : '#00ff00';
        html += `<div style="color: ${color}; font-size: 12px; margin-bottom: 5px; padding: 3px; background-color: #111111; border-radius: 3px;">${dica}</div>`;
    });
    
    container.innerHTML = html;
}

function loadInitialData() {
    ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'].forEach(symbol => {
        fetch(`/api/market-data?symbol=${symbol}`)
            .then(response => response.json())
            .then(data => {
                if (data && Object.keys(data).length > 0) {
                    updateMarketSummary({symbol: symbol, data: data});
                    updateMarketData({symbol: symbol, data: data});
                    updateEstrategias({symbol: symbol, data: data});
                    updateInterpretacao({symbol: symbol, data: data});
                    updateDicas({symbol: symbol, data: data});
                }
            });
    });
    
    loadAlerts();
}

function loadAlerts() {
    fetch('/api/alerts')
        .then(response => response.json())
        .then(alerts => {
            const container = document.getElementById('alerts');
            document.getElementById('alert-count').textContent = alerts.length;
            
            if (alerts.length === 0) {
                container.innerHTML = `
                    <div style="color: #00aa00; font-size: 12px;">
                        Nenhum alerta recente
                    </div>
                `;
                return;
            }
            
            container.innerHTML = alerts.map(alert => {
                // Determina o tipo de alerta baseado na mensagem
                let alertClass = 'alert-neutral';
                let icon = 'fas fa-info-circle';
                
                if (alert.message.toLowerCase().includes('compra') || alert.message.toLowerCase().includes('bullish') || alert.message.toLowerCase().includes('alta')) {
                    alertClass = 'alert-bullish';
                    icon = 'fas fa-arrow-up';
                } else if (alert.message.toLowerCase().includes('venda') || alert.message.toLowerCase().includes('bearish') || alert.message.toLowerCase().includes('baixa')) {
                    alertClass = 'alert-bearish';
                    icon = 'fas fa-arrow-down';
                } else if (alert.message.toLowerCase().includes('ruptura') || alert.message.toLowerCase().includes('atenção')) {
                    alertClass = 'alert-rupture';
                    icon = 'fas fa-exclamation-triangle';
                }
                
                return `
                    <div class="${alertClass}" style="margin-bottom: 8px;">
                        <div style="font-weight: bold; font-size: 12px;">
                            <i class="${icon}"></i> ${alert.symbol} - $${alert.price.toFixed(2)}
                        </div>
                        <div style="font-size: 11px; margin-top: 3px;">
                            ${alert.message}
                        </div>
                        <div style="color: #00aa00; font-size: 10px; margin-top: 3px;">
                            ${new Date(alert.timestamp).toLocaleString()}
                        </div>
                    </div>
                `;
            }).join('');
        });
}

setInterval(loadInitialData, 30000);

document.addEventListener('DOMContentLoaded', function() {
    loadInitialData();
    
    // Atualiza timestamp
    setInterval(() => {
        const now = new Date();
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = now.toLocaleString('pt-BR');
        }
    }, 1000);
});
</script>
{% endblock %}'''

    os.makedirs('templates', exist_ok=True)
    
    with open('templates/base.html', 'w') as f:
        f.write(base_template)
    
    with open('templates/login.html', 'w') as f:
        f.write(login_template)
    
    with open('templates/register.html', 'w') as f:
        f.write(register_template)
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(dashboard_template)
    
    print("✅ Templates Terminal criados com sucesso!")

if __name__ == "__main__":
    create_terminal_templates()
