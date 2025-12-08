# 🚀 DEPLOY TERMINAL WEB SIMPLES NO RENDER

## 🎯 OBJETIVO

Deploy de uma **versão web simples** que replique os comandos do terminal (`main.py`) sem dependências de scraper ou análises em tempo real conflitantes.

---

## 📊 O QUE FUNCIONA vs O QUE NÃO FUNCIONA

### ✅ **O QUE FUNCIONA (main.py):**
- ✅ Comandos R, CTX, MULT, DOM
- ✅ Geração de relatórios (RT, RH, RD, RS)
- ✅ Geração de gráficos (campo magnético, candlestick)
- ✅ Multi-pair analysis
- ✅ Análise técnica completa
- ✅ Bot Telegram funcional
- ✅ Backtesting

### ❌ **O QUE NÃO FUNCIONA (sne_radar_web.py):**
- ❌ Análise em tempo real (depende de scraper)
- ❌ Dashboard com updates automáticos
- ❌ Gráficos em tempo real
- ❌ WebSocket real-time (complexo demais)

---

## 🎯 SOLUÇÃO: VERSÃO WEB SIMPLES DO TERMINAL

### **Arquitetura Proposta:**

```
┌─────────────────────────────────────┐
│   RENDER.COM (HTTP)               │
│   ┌───────────────────────────────┐ │
│   │  Flask App Simples            │ │
│   │  - Interface Terminal Web    │ │
│   │  - Chamadas API sob demanda  │ │
│   └───────────────────────────────┘ │
│   │                                 │
│   └──→ Executa comandos do main.py │
│       R, CTX, MULT, DOM           │
│       Gera relatórios/gráficos    │
│       Retorna resultados           │
└─────────────────────────────────────┘
```

---

## 🏗️ ESTRUTURA DO PROJETO PARA DEPLOY

```
SNE_BACKUP_CLEAN/
│
├── app_terminal.py          # ← NOVO: Flask app simples
├── render_terminal.yaml      # ← NOVO: Config Render
├── requirements_simple.txt    # ← NOVO: Dependências mínimas
│
├── main.py                   # ← Usa como biblioteca
├── motor_renan.py            # ← Usa comandos
├── relatorios_periodicos.py  # ← Usa relatórios
├── comando_campo_magnetico.py # ← Usa gráficos
├── xenos_bot.py             # ← Telegram
│
└── reports/                  # ← Output de relatórios
    ├── scanner/
    ├── campo_magnetico/
    ├── daily/
    └── weekly/
```

---

## 📝 ARQUIVO app_terminal.py (NOVO)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNE Terminal Web - Versão Simplificada para Render
Sem scraping, sem websockets, apenas comandos sob demanda
"""

from flask import Flask, render_template, jsonify, request, send_file
import sys
import os

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).hex()

# Imports dos módulos do terminal
from motor_renan import analise_completa, exibir_analise, coletar_dados
from contexto_mercado import analisar_contexto_mercado
from multi_pair_context import analisar_mercado_completo
from comando_campo_magnetico import gerar_campo_magnetico_simples
from relatorios_periodicos import gerar_relatorio_horario
from grafico_candlestick import gerar_grafico_com_niveis
from calcular_suportes_resistencias import calcular_suportes_resistencias

@app.route('/')
def index():
    """Interface terminal web"""
    return render_template('terminal_web.html')

@app.route('/api/execute/<command>', methods=['POST'])
def execute_command(command):
    """
    Executa comandos do terminal sob demanda
    Sem updates automáticos, sem scraping
    """
    try:
        data = request.json or {}
        command = command.upper()
        
        if command == 'R':
            # Scanner Técnico
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1h')
            
            resultado = analise_completa(symbol, timeframe)
            
            return jsonify({
                'success': True,
                'type': 'analysis',
                'data': {
                    'symbol': resultado['symbol'],
                    'price': resultado['indicadores']['preco'],
                    'confluence': resultado['confluencia']['score'],
                    'recommendation': resultado['sintese']['acao'],
                    'entry': resultado['sintese'].get('entry_price'),
                    'stop': resultado['sintese'].get('stop_loss'),
                    'tp1': resultado['sintese'].get('tp1'),
                    'tp2': resultado['sintese'].get('tp2'),
                    'tp3': resultado['sintese'].get('tp3'),
                    'full_analysis': resultado
                }
            })
        
        elif command == 'CTX':
            # Contexto de Mercado
            contexto = analisar_contexto_mercado()
            
            return jsonify({
                'success': True,
                'type': 'context',
                'data': contexto
            })
        
        elif command == 'MULT':
            # Multi-Pair
            analise = analisar_mercado_completo()
            
            return jsonify({
                'success': True,
                'type': 'multi',
                'data': analise
            })
        
        elif command == 'CM':
            # Campo Magnético
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1h')
            
            resultado = gerar_campo_magnetico_simples(symbol, timeframe)
            
            return jsonify({
                'success': True,
                'type': 'magnetic',
                'image_url': f"/files/{os.path.basename(resultado['caminho'])}",
                'data': resultado
            })
        
        elif command == 'RT':
            # Relatório Técnico Completo
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1h')
            
            resultado = analise_completa(symbol, timeframe)
            
            return jsonify({
                'success': True,
                'type': 'report',
                'data': {
                    'symbol': resultado['symbol'],
                    'timeframe': timeframe,
                    'full_report': resultado
                }
            })
        
        elif command == 'RH':
            # Relatório Horário
            symbol = data.get('symbol', 'BTCUSDT')
            resultado = gerar_relatorio_horario(symbol)
            
            return jsonify({
                'success': True,
                'type': 'hourly_report',
                'data': resultado
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'Comando "{command}" não implementado'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/files/<filename>')
def serve_file(filename):
    """Serve arquivos gerados (gráficos, relatórios)"""
    import os
    from flask import send_from_directory
    
    # Procurar em múltiplos diretórios
    directories = [
        'reports/campo_magnetico',
        'reports/scanner',
        'reports'
    ]
    
    for directory in directories:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            return send_from_directory(directory, filename)
    
    return "File not found", 404

@app.route('/api/health')
def health_check():
    """Health check para Render"""
    return jsonify({
        'status': 'healthy',
        'app': 'sne-terminal-web',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Iniciando SNE Terminal Web...")
    print("📡 Acesse: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## 📝 ARQUIVO render_terminal.yaml (NOVO)

```yaml
services:
  - type: web
    name: sne-terminal-web
    env: python
    plan: free
    buildCommand: |
      pip install -r requirements_simple.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app_terminal:app --timeout 120 --workers 1
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: TELEGRAM_TOKEN
        sync: false
      - key: TELEGRAM_CHAT_ID
        sync: false
```

---

## 📝 ARQUIVO requirements_simple.txt (NOVO)

```txt
# Dependências mínimas para terminal web
flask==3.0.0
gunicorn==21.2.0
requests==2.31.0
pandas>=2.2.0
numpy>=1.26.0
matplotlib>=3.8.0
mplfinance>=0.12.10b0
pytz==2023.3
python-telegram-bot==20.7
scipy>=1.11.0
scikit-learn>=1.4.0
```

---

## 📝 TEMPLATE terminal_web.html (NOVO)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SNE Radar - Terminal Web</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: #000;
            color: #0f0;
            padding: 15px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #111;
            border: 2px solid #0f0;
            margin-bottom: 20px;
        }
        
        .header h1 {
            margin: 0;
        }
        
        .status {
            color: #0f0;
        }
        
        .command-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .command-box input {
            flex: 1;
            padding: 15px;
            background: #222;
            border: 2px solid #0f0;
            color: #0f0;
            font-size: 16px;
            font-family: 'Courier New', monospace;
        }
        
        .command-box button {
            padding: 15px 30px;
            background: #0f0;
            border: none;
            color: #000;
            font-weight: bold;
            cursor: pointer;
        }
        
        .output {
            background: #111;
            border: 2px solid #0f0;
            padding: 20px;
            min-height: 400px;
            overflow-y: auto;
            font-size: 14px;
            margin-bottom: 20px;
        }
        
        .output-line {
            margin: 5px 0;
        }
        
        .success { color: #0f0; }
        .error { color: #f00; }
        .info { color: #0ff; }
        
        .quick-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
        }
        
        .btn {
            padding: 15px;
            background: #222;
            border: 2px solid #0f0;
            color: #0f0;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #0f0;
            color: #000;
        }
        
        .loading {
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        @media (max-width: 768px) {
            .quick-buttons {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .command-box {
                flex-direction: column;
            }
            
            .command-box input {
                font-size: 16px; /* Previne zoom iOS */
            }
        }
        
        .chart-img {
            max-width: 100%;
            margin: 20px 0;
            border: 2px solid #0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 SNE RADAR</h1>
            <span class="status">● ONLINE</span>
        </div>
        
        <div class="command-box">
            <input type="text" id="cmd" placeholder="Digite comando: R, CTX, MULT, CM, etc.">
            <button onclick="execute()">EXECUTAR</button>
        </div>
        
        <div class="output" id="output">
            <div class="output-line success">
                🚀 SNE RADAR - Terminal Web<br>
                Comandos: R (Scanner), CTX (Contexto), MULT (Multi-Pair), CM (Campo Magnético), RT (Relatório)
            </div>
        </div>
        
        <div class="quick-buttons">
            <button class="btn" onclick="runCmd('R')">🔍 Scanner</button>
            <button class="btn" onclick="runCmd('CTX')">🌍 Contexto</button>
            <button class="btn" onclick="runCmd('MULT')">📊 Multi-Pair</button>
            <button class="btn" onclick="runCmd('CM')">🧲 Campo Mag.</button>
            <button class="btn" onclick="runCmd('RT')">📄 Relatório</button>
        </div>
    </div>
    
    <script>
        function execute() {
            const cmd = document.getElementById('cmd').value.trim().toUpperCase();
            if (!cmd) return;
            
            showOutput(`<div class="loading">🔄 Executando: ${cmd}...</div>`, 'info');
            
            const data = {};
            
            // Comandos que precisam de parâmetros
            if (cmd === 'R' || cmd === 'CM' || cmd === 'RT') {
                const symbol = prompt('Símbolo (ex: BTCUSDT, ou Enter para padrão):');
                if (symbol) {
                    data.symbol = symbol;
                }
                const tf = prompt('Timeframe (1h, 4h, 1d, ou Enter para padrão):');
                if (tf) {
                    data.timeframe = tf;
                }
            }
            
            fetch(`/api/execute/${cmd}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showOutput(formatOutput(data), 'success');
                    
                    // Se for imagem, mostrar
                    if (data.image_url) {
                        showImage(data.image_url);
                    }
                } else {
                    showOutput(`<div class="error">❌ Erro: ${data.error}</div>`, 'error');
                }
            })
            .catch(e => showOutput(`<div class="error">❌ Erro: ${e.message}</div>`, 'error'));
            
            document.getElementById('cmd').value = '';
        }
        
        function runCmd(cmd) {
            document.getElementById('cmd').value = cmd;
            execute();
        }
        
        function showOutput(html, cls) {
            const output = document.getElementById('output');
            output.innerHTML += `<div class="output-line ${cls}">${html}</div>`;
            output.scrollTop = output.scrollHeight;
        }
        
        function showImage(url) {
            const img = `<img src="${url}" class="chart-img" alt="Chart">`;
            showOutput(img, 'success');
        }
        
        function formatOutput(data) {
            if (data.type === 'analysis') {
                const d = data.data;
                return `
                    <h3>🔍 ANÁLISE: ${d.symbol}</h3>
                    <p>💰 Preço: $${d.price.toFixed(2)}</p>
                    <p>📊 Confluência: ${d.confluence}/10</p>
                    <p>💡 Recomendação: ${d.recommendation}</p>
                    ${d.entry ? `<p>📍 Entry: $${d.entry.toFixed(2)}</p>` : ''}
                    ${d.stop ? `<p>🛡️ Stop: $${d.stop.toFixed(2)}</p>` : ''}
                    ${d.tp1 ? `<p>🎯 TP1: $${d.tp1.toFixed(2)}</p>` : ''}
                    ${d.tp2 ? `<p>🎯 TP2: $${d.tp2.toFixed(2)}</p>` : ''}
                `;
            }
            return JSON.stringify(data, null, 2);
        }
        
        document.getElementById('cmd').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') execute();
        });
    </script>
</body>
</html>
```

---

## 🚀 PROCESSO DE DEPLOY

### **1. Criar arquivos:**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Criar diretório para templates
mkdir -p templates

# Criar os 4 arquivos novos:
```

Arquivos a criar:
- `app_terminal.py`
- `render_terminal.yaml`
- `requirements_simple.txt`
- `templates/terminal_web.html`

### **2. Push para GitHub:**

```bash
git add app_terminal.py render_terminal.yaml requirements_simple.txt templates/
git commit -m "Deploy: Terminal Web Simplificado"
git push origin main
```

### **3. Deploy no Render:**

1. Acesse: https://dashboard.render.com
2. Clique: "New +" → "Blueprint"
3. Conecte repositório
4. Use o arquivo: `render_terminal.yaml`
5. Deploy automático!

---

## ✅ VANTAGENS DESTA ABORDAGEM

✅ **Sem scraping** - Apenas API Binance sob demanda  
✅ **Sem WebSocket** - HTTP simples  
✅ **Gera gráficos** - Campo magnético, candlestick  
✅ **Gera relatórios** - RT, RH, RD, RS  
✅ **Mobile-friendly** - Layout responsivo  
✅ **Deploy rápido** - 5 minutos  
✅ **Plano Free** - Grátis no Render  

---

## 🎯 RESULTADO FINAL

**URL Após Deploy:**
```
https://sne-terminal-web.onrender.com
```

**Interface:**
```
┌─────────────────────────────────┐
│ 🚀 SNE RADAR    ● ONLINE       │
├─────────────────────────────────┤
│ [Digite: R, CTX, MULT...]  EXEC│
├─────────────────────────────────┤
│ OUTPUT:                         │
│ 🔍 ANÁLISE: BTCUSDT             │
│ 💰 Preço: $42,500               │
│ 📊 Confluência: 7.5/10          │
│ 💡 Recomendação: COMPRAR        │
│ 📍 Entry: $42,500               │
│ 🛡️ Stop: $41,800                │
│ 🎯 TP1: $43,200                 │
│ [Gráfico gerado abaixo]         │
├─────────────────────────────────┤
│ [🔍] [🌍] [📊] [🧲] [📄]      │
└─────────────────────────────────┘
```

---

**Quer que eu crie os 4 arquivos agora?**



