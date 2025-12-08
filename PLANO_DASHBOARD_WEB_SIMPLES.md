# 📱 PLANO DASHBOARD WEB SIMPLES - REPLICAÇÃO DO TERMINAL

**Data:** 18 de abril de 2025  
**Objetivo:** Criar versão web/mobile do terminal SNE (main.py)  
**Filosofia:** Simples, funcional, responsivo - sem complexidade desnecessária

---

## 🎯 OBJETIVO

Criar uma interface web que replique TODOS os comandos do terminal `main.py` em formato web responsivo (desktop + mobile).

---

## 📋 COMANDOS DO TERMINAL (main.py)

### **🔍 ANÁLISE TÉCNICA:**
- **R** - Scanner Técnico (Análise Completa)
- **CM** - Campo Magnético SNE
- **MAG** - Análise Magnética SNE
- **CTX** - Contexto de Mercado Macro
- **MULT** - Multi-Pair Análise Técnica
- **DOM** - Análise Profunda de Liquidez

### **📊 RELATÓRIOS:**
- **RT** - Relatório Técnico Completo
- **RH** - Relatório Horário
- **RD** - Relatório Diário
- **RS** - Relatório Semanal

### **📈 VISUALIZAÇÃO:**
- **1** - Radar Visual (Gráfico)
- **DASH** - Dashboard Técnico Tempo Real
- **HEAT** - Heatmap Correlações

### **🤖 AUTOMAÇÃO:**
- **AUTO** - Análise Automática 24/7
- **ALERT** - Sistema de Alertas Técnicos

### **📱 TELEGRAM:**
- **TG** - Configurar Telegram
- **SEND** - Enviar Relatório Manual

### **⚙️ SISTEMA:**
- **CFG** - Configurações
- **INFO** - Informações do Sistema

---

## 🏗️ ARQUITETURA PROPOSTA (SIMPLES)

### **Opção A: Flask + HTML/CSS/JS Vanilla (RECOMENDADO)**

**Por quê esta opção:**
- ✅ Usa Flask que JÁ EXISTE
- ✅ Não precisa de frameworks complexos
- ✅ Pode reutilizar templates existentes
- ✅ Fácil manutenção
- ✅ Rápido de implementar

### **Estrutura de Arquivos:**

```
SNE_BACKUP_CLEAN/
├── websimple/
│   ├── app.py                      # Flask app simples
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analysis.py            # Rotas para análises
│   │   ├── reports.py              # Rotas para relatórios
│   │   ├── visualization.py        # Rotas para visualizações
│   │   ├── automation.py           # Rotas para automação
│   │   └── system.py               # Rotas para sistema
│   ├── static/
│   │   ├── css/
│   │   │   └── terminal.css        # Estilo terminal
│   │   ├── js/
│   │   │   ├── terminal.js         # Lógica JS
│   │   │   └── charts.js           # Charts simples
│   │   └── img/
│   ├── templates/
│   │   └── terminal_web.html      # Template único
│   └── utils/
│       └── command_executor.py     # Executa comandos do terminal
│
└── main.py (mantém existente)
```

---

## 📱 INTERFACE WEB - DESIGN

### **Layout: Card-Based + Terminal Style**

```html
<!-- TerminalWeb.html -->
<!DOCTYPE html>
<html>
<head>
    <title>SNE RADAR - Terminal Web</title>
    <link rel="stylesheet" href="/static/css/terminal.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <!-- HEADER -->
    <div class="header">
        <h1>🚀 SNE RADAR</h1>
        <span class="status-online">● ONLINE</span>
    </div>

    <!-- COMMAND INPUT -->
    <div class="command-input">
        <input type="text" id="cmd-input" placeholder="Digite um comando (R, CTX, MULT, etc.)">
        <button onclick="executeCommand()">EXECUTAR</button>
    </div>

    <!-- OUTPUT AREA (Terminal Style) -->
    <div class="output-area" id="output">
        <div class="welcome-msg">
            🚀 SNE RADAR - Terminal Web<br>
            Digite um comando acima...
        </div>
    </div>

    <!-- QUICK COMMANDS (Mobile Friendly) -->
    <div class="quick-commands">
        <button class="cmd-btn" onclick="runCommand('R')">🔍 Scanner</button>
        <button class="cmd-btn" onclick="runCommand('CTX')">🌍 Contexto</button>
        <button class="cmd-btn" onclick="runCommand('MULT')">📊 Multi-Pair</button>
        <button class="cmd-btn" onclick="runCommand('DASH')">🎛️ Dashboard</button>
        <button class="cmd-btn" onclick="runCommand('AUTO')">🔄 Auto</button>
        <button class="cmd-btn" onclick="runCommand('INFO')">ℹ️ Info</button>
    </div>

    <script src="/static/js/terminal.js"></script>
</body>
</html>
```

### **CSS - Terminal Style + Responsive**

```css
/* terminal.css */

/* Mobile First */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Courier New', monospace;
    background: #000;
    color: #0f0;
    padding: 10px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background: #111;
    border-bottom: 2px solid #0f0;
    margin-bottom: 20px;
}

.command-input {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.command-input input {
    flex: 1;
    padding: 15px;
    background: #222;
    border: 1px solid #0f0;
    color: #0f0;
    font-size: 16px;
}

.command-input button {
    padding: 15px 30px;
    background: #0f0;
    border: none;
    color: #000;
    font-weight: bold;
    cursor: pointer;
}

.output-area {
    background: #111;
    border: 1px solid #0f0;
    padding: 20px;
    min-height: 400px;
    overflow-y: auto;
    margin-bottom: 20px;
}

/* Quick Commands */
.quick-commands {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 10px;
}

.cmd-btn {
    padding: 15px;
    background: #222;
    border: 1px solid #0f0;
    color: #0f0;
    cursor: pointer;
    transition: all 0.3s;
}

.cmd-btn:hover {
    background: #0f0;
    color: #000;
}

/* Output Styling */
.output-line {
    margin: 5px 0;
    font-family: 'Courier New', monospace;
}

.output-line.success { color: #0f0; }
.output-line.error { color: #f00; }
.output-line.info { color: #0ff; }
.output-line.warning { color: #ff0; }

/* Chart Container */
.chart-container {
    width: 100%;
    max-width: 100%;
    margin: 20px 0;
}

/* Mobile Optimization */
@media (max-width: 768px) {
    .quick-commands {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .command-input {
        flex-direction: column;
    }
    
    .command-input input {
        font-size: 16px; /* Previne zoom no iOS */
    }
}

/* Loading Animation */
.loading {
    display: inline-block;
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
```

---

## 🔧 BACKEND - Flask App

### **app.py (Novo arquivo simples)**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNE Radar Terminal Web - Versão Simplificada
"""

from flask import Flask, render_template, jsonify, request
import json
from routes.analysis import bp_analysis
from routes.reports import bp_reports
from routes.visualization import bp_visualization
from routes.automation import bp_automation
from routes.system import bp_system

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(bp_analysis)
app.register_blueprint(bp_reports)
app.register_blueprint(bp_visualization)
app.register_blueprint(bp_automation)
app.register_blueprint(bp_system)

@app.route('/')
def index():
    return render_template('terminal_web.html')

@app.route('/api/execute/<command>', methods=['POST'])
def execute_command(command):
    """Executa comando do terminal via AJAX"""
    data = request.json
    
    # Importar executor de comandos
    from utils.command_executor import execute_terminal_command
    
    # Executar comando
    resultado = execute_terminal_command(command, data)
    
    return jsonify(resultado)

if __name__ == '__main__':
    # Rodar na porta 5000 (não conflita com sne_radar_web.py na porta 9999)
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## 🎯 IMPLEMENTAÇÃO EM 5 ETAPAS

### **ETAPA 1: Criar Estrutura Base (1 dia)**

```bash
mkdir -p websimple/{routes,static/{css,js,img},templates,utils}
touch websimple/app.py
touch websimple/routes/{analysis.py,reports.py,visualization.py,automation.py,system.py}
touch websimple/static/css/terminal.css
touch websimple/static/js/terminal.js
touch websimple/templates/terminal_web.html
touch websimple/utils/command_executor.py
```

### **ETAPA 2: Template HTML + CSS (1 dia)**

**Fazer:**
- ✅ Criar `terminal_web.html` (layout terminal)
- ✅ Criar `terminal.css` (estilo terminal + mobile)
- ✅ Testar responsividade no mobile

### **ETAPA 3: JavaScript Terminal (1 dia)**

```javascript
// terminal.js

// Estados
let commandHistory = [];
let currentCommand = '';

// Executar comando
async function executeCommand() {
    const input = document.getElementById('cmd-input');
    const command = input.value.trim().toUpperCase();
    
    if (!command) return;
    
    // Adicionar ao histórico
    commandHistory.push(command);
    
    // Mostrar loading
    showOutput(`<div class="loading">🔄 Executando comando: ${command}</div>`);
    
    // Chamar API
    try {
        const response = await fetch(`/api/execute/${command}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        const result = await response.json();
        
        // Mostrar resultado
        showOutput(formatOutput(result));
    } catch (error) {
        showOutput(`<div class="error">❌ Erro: ${error.message}</div>`);
    }
    
    // Limpar input
    input.value = '';
}

function showOutput(html) {
    const output = document.getElementById('output');
    output.innerHTML += html;
    output.scrollTop = output.scrollHeight; // Auto-scroll
}

function formatOutput(result) {
    let html = '<div class="output-line success">';
    
    if (result.type === 'analysis') {
        html += formatAnalysis(result.data);
    } else if (result.type === 'report') {
        html += formatReport(result.data);
    } else {
        html += result.message;
    }
    
    html += '</div>';
    return html;
}

function formatAnalysis(data) {
    return `
        <h3>🔍 ANÁLISE: ${data.symbol}</h3>
        <p>💰 Preço: $${data.price}</p>
        <p>📊 Confluência: ${data.confluence}/10</p>
        <p>💡 Recomendação: ${data.recommendation}</p>
    `;
}

// Atalhos de teclado
document.getElementById('cmd-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        executeCommand();
    }
});

// Quick commands
function runCommand(cmd) {
    document.getElementById('cmd-input').value = cmd;
    executeCommand();
}
```

### **ETAPA 4: Backend - Command Executor (2 dias)**

```python
# utils/command_executor.py

def execute_terminal_command(command, params):
    """
    Executa comandos do terminal main.py
    Retorna JSON com resultado
    """
    
    # Importar funções do main.py
    from motor_renan import analise_completa
    from contexto_mercado import analisar_contexto_mercado
    from multi_pair_context import analisar_mercado_completo
    from comando_campo_magnetico import gerar_campo_magnetico_simples
    
    command = command.upper()
    
    try:
        if command == 'R':
            # Scanner Técnico
            symbol = params.get('symbol', 'BTCUSDT')
            timeframe = params.get('timeframe', '1h')
            
            resultado = analise_completa(symbol, timeframe)
            
            return {
                'type': 'analysis',
                'success': True,
                'data': {
                    'symbol': resultado['symbol'],
                    'price': resultado['indicadores']['preco'],
                    'confluence': resultado['confluencia']['score'],
                    'recommendation': resultado['sintese']['acao'],
                    'full_data': resultado
                }
            }
            
        elif command == 'CTX':
            # Contexto de Mercado
            contexto = analisar_contexto_mercado()
            
            return {
                'type': 'context',
                'success': True,
                'data': contexto,
                'message': f"🌍 Contexto de Mercado: {contexto['regime']}"
            }
            
        elif command == 'MULT':
            # Multi-Pair
            analise = analisar_mercado_completo()
            
            return {
                'type': 'multi',
                'success': True,
                'data': analise,
                'message': f"📊 Multi-Pair: {len(analise['pares'])} pares analisados"
            }
            
        elif command == 'CM':
            # Campo Magnético
            symbol = params.get('symbol', 'BTCUSDT')
            timeframe = params.get('timeframe', '1h')
            
            resultado = gerar_campo_magnetico_simples(symbol, timeframe)
            
            return {
                'type': 'magnetic',
                'success': True,
                'data': resultado,
                'image_path': resultado['caminho']
            }
            
        else:
            return {
                'type': 'error',
                'success': False,
                'message': f'❌ Comando "{command}" não reconhecido'
            }
            
    except Exception as e:
        return {
            'type': 'error',
            'success': False,
            'message': f'❌ Erro: {str(e)}'
        }
```

### **ETAPA 5: Rotas Específicas (1 dia)**

```python
# routes/analysis.py

from flask import Blueprint, jsonify, request
from utils.command_executor import execute_terminal_command

bp_analysis = Blueprint('analysis', __name__)

@bp_analysis.route('/api/scanner', methods=['POST'])
def scanner():
    data = request.json
    result = execute_terminal_command('R', data)
    return jsonify(result)

@bp_analysis.route('/api/context', methods=['POST'])
def context():
    result = execute_terminal_command('CTX', {})
    return jsonify(result)

@bp_analysis.route('/api/multi', methods=['POST'])
def multi_pair():
    result = execute_terminal_command('MULT', {})
    return jsonify(result)
```

---

## 📱 RESPONSIVIDADE MOBILE

### **Features Mobile:**

1. **Touch-Friendly Buttons**
```css
.cmd-btn {
    min-height: 44px; /* Tamanho mínimo para touch */
    padding: 15px;
}
```

2. **Input com Fonte Grande**
```css
input[type="text"] {
    font-size: 16px; /* Previne zoom no iOS */
}
```

3. **Grid Adaptativo**
```css
.quick-commands {
    grid-template-columns: repeat(2, 1fr); /* 2 colunas no mobile */
}

@media (min-width: 768px) {
    .quick-commands {
        grid-template-columns: repeat(3, 1fr); /* 3 colunas no tablet */
    }
}
```

4. **Scroll Suave**
```css
.output-area {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch; /* iOS smooth scroll */
}
```

---

## 🚀 EXECUTAÇÃO

### **Modo Desenvolvimento:**

```bash
cd websimple
python3 app.py
```

**Acessar:** `http://localhost:5000`

### **Modo Produção (com sne_radar_web.py existente):**

```python
# Integrar no sne_radar_web.py existente

# Adicionar rota no sne_radar_web.py:
@app.route('/terminal')
def terminal_web():
    return render_template('terminal_web.html')
```

Ou rodar em porta separada:
- `sne_radar_web.py` → porta 9999 (dashboard completo)
- `websimple/app.py` → porta 5000 (terminal web)

---

## 📊 RESULTADO FINAL

### **Interface Web:**

```
┌─────────────────────────────────────────┐
│  🚀 SNE RADAR              ● ONLINE     │
├─────────────────────────────────────────┤
│  [Digite comando: R, CTX, MULT...]     │
│                        [EXECUTAR]      │
├─────────────────────────────────────────┤
│  OUTPUT AREA:                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                         │
│  🔍 ANÁLISE COMPLETA                    │
│  📊 BTCUSDT | 1h                       │
│  💰 Preço: $42,500                     │
│  📈 Confluência: 7.5/10                │
│  💡 Recomendação: COMPRAR              │
│                                         │
├─────────────────────────────────────────┤
│  [🔍 Scanner] [🌍 Ctx] [📊 Mult]      │
│  [🎛️ Dash] [🔄 Auto] [ℹ️ Info]       │
└─────────────────────────────────────────┘
```

---

## ✅ VANTAGENS DESTA ABORDAGEM

1. ✅ **Simples** - Não precisa Vue.js/React/Angular
2. ✅ **Rápido** - 5 dias de desenvolvimento
3. ✅ **Reutiliza** - Usa funções existentes do terminal
4. ✅ **Mobile-First** - Responsivo por padrão
5. ✅ **Mantém Compatibilidade** - Terminal original continua funcionando
6. ✅ **Sem Dependências Complexas** - HTML/CSS/JS vanilla + Flask

---

## 🎯 CONCLUSÃO

**Este plano é:**
- ✅ Simples (HTML/CSS/JS básico)
- ✅ Funcional (replica todos comandos)
- ✅ Rápido (5 dias)
- ✅ Responsivo (mobile + desktop)
- ✅ Mantém funcionalidades existentes

**NÃO inclui:**
- ❌ Three.js (demais para agora)
- ❌ ML complexo
- ❌ Backtesting visual
- ❌ Multi-exchange

**Próximo Passo:** Aprovar e começar implementação?

---

**Desenvolvido:** 18 de abril de 2025  
**Status:** 📋 Plano Simples e Executável



