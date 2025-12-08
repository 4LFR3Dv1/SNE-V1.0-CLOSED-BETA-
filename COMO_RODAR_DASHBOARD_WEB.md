# 🚀 COMO RODAR O DASHBOARD WEB SNE RADAR

---

## 📋 VERSÕES DISPONÍVEIS

Você tem **DUAS** opções de executar o SNE Radar via web:

### **OPÇÃO 1: Dashboard Web Completo Existente**
📍 **Arquivo:** `sne_radar_web.py`  
🌐 **Porta:** 9999  
✨ **Funcionalidades:** Dashboard profissional completo, autenticação, multi-pair, ML

### **OPÇÃO 2: Terminal Web Simples (A IMPLEMENTAR)**
📍 **Arquivo:** `websimple/app.py` (será criado)  
🌐 **Porta:** 5000  
✨ **Funcionalidades:** Interface terminal simples, comandos do main.py

---

## 🎯 OPÇÃO 1: Dashboard Existente (FUNCIONAL AGORA)

### **1. Executar o Dashboard Atual:**

```bash
# No diretório raiz do projeto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Ativar ambiente virtual (se não estiver ativado)
source venv/bin/activate

# Executar dashboard existente
python3 sne_radar_web.py
```

### **2. Acessar:**
- **Desktop:** `http://localhost:9999`
- **Mobile (mesma rede):** `http://[IP_COMPUTADOR]:9999`

### **3. Login:**
- **Usuário:** admin (ou qualquer um)
- **Senha:** admin (ou qualquer uma)
- Criar novo usuário em `/register`

### **4. Funcionalidades Disponíveis:**
- ✅ Dashboard em tempo real
- ✅ Gráficos TradingView
- ✅ Análise de mercado
- ✅ Multi-pair
- ✅ Alertas
- ✅ Backtesting
- ✅ Autenticação

---

## 🎯 OPÇÃO 2: Terminal Web Simples (A CRIAR)

### **1. Pré-requisitos:**

Verificar se já existe:
```bash
ls -la websimple/
```

Se **NÃO existir**, criar estrutura:
```bash
mkdir -p websimple/{routes,static/{css,js,img},templates,utils}
```

### **2. Criar arquivos básicos:**

**websimple/app.py:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request
import sys, os

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('terminal_web.html')

@app.route('/api/execute/<command>', methods=['POST'])
def execute_command(command):
    """Executa comando do terminal"""
    try:
        # Importar funções do main.py
        if command == 'R':
            from motor_renan import analise_completa
            symbol = request.json.get('symbol', 'BTCUSDT')
            timeframe = request.json.get('timeframe', '1h')
            
            resultado = analise_completa(symbol, timeframe)
            
            return jsonify({
                'type': 'analysis',
                'success': True,
                'data': {
                    'symbol': resultado['symbol'],
                    'price': resultado['indicadores']['preco'],
                    'confluence': resultado['confluencia']['score'],
                    'recommendation': resultado['sintese']['acao']
                }
            })
        
        elif command == 'CTX':
            from contexto_mercado import analisar_contexto_mercado
            contexto = analisar_contexto_mercado()
            
            return jsonify({
                'type': 'context',
                'success': True,
                'data': contexto
            })
        
        else:
            return jsonify({
                'type': 'error',
                'success': False,
                'message': f'Comando "{command}" não implementado ainda'
            })
    
    except Exception as e:
        return jsonify({
            'type': 'error',
            'success': False,
            'message': f'Erro: {str(e)}'
        })

if __name__ == '__main__':
    print("🚀 Iniciando SNE Terminal Web...")
    print("📡 Acesse: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**websimple/templates/terminal_web.html:**
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SNE Radar Terminal</title>
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
            padding: 20px;
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
            border: 1px solid #0f0;
            color: #0f0;
            font-size: 16px;
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
            border: 1px solid #0f0;
            padding: 20px;
            min-height: 400px;
            overflow-y: auto;
            font-size: 14px;
        }
        
        .quick-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn {
            padding: 15px;
            background: #222;
            border: 1px solid #0f0;
            color: #0f0;
            cursor: pointer;
            text-align: center;
        }
        
        .btn:hover {
            background: #0f0;
            color: #000;
        }
        
        .output-line {
            margin: 5px 0;
        }
        
        .success { color: #0f0; }
        .error { color: #f00; }
        .info { color: #0ff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 SNE RADAR</h1>
        <span class="status">● ONLINE</span>
    </div>
    
    <div class="command-box">
        <input type="text" id="cmd" placeholder="Digite comando: R, CTX, MULT, etc.">
        <button onclick="execute()">EXECUTAR</button>
    </div>
    
    <div class="output" id="output">
        <div class="output-line success">
            🚀 SNE RADAR - Terminal Web<br>
            Comandos disponíveis: R (Scanner), CTX (Contexto), MULT (Multi-Pair), etc.
        </div>
    </div>
    
    <div class="quick-buttons">
        <button class="btn" onclick="runCmd('R')">🔍 Scanner</button>
        <button class="btn" onclick="runCmd('CTX')">🌍 Contexto</button>
        <button class="btn" onclick="runCmd('MULT')">📊 Multi-Pair</button>
        <button class="btn" onclick="runCmd('INFO')">ℹ️ Info</button>
    </div>
    
    <script>
        function execute() {
            const cmd = document.getElementById('cmd').value.trim().toUpperCase();
            if (!cmd) return;
            
            showOutput(`<div class="loading">🔄 Executando: ${cmd}...</div>`, 'info');
            
            fetch(`/api/execute/${cmd}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showOutput(formatOutput(data), 'success');
                } else {
                    showOutput(data.message, 'error');
                }
            })
            .catch(e => showOutput(`Erro: ${e}`, 'error'));
            
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
        
        function formatOutput(data) {
            if (data.type === 'analysis') {
                return `
                    <h3>🔍 ANÁLISE: ${data.data.symbol}</h3>
                    <p>💰 Preço: $${data.data.price.toFixed(2)}</p>
                    <p>📊 Confluência: ${data.data.confluence}/10</p>
                    <p>💡 Recomendação: ${data.data.recommendation}</p>
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

### **3. Executar:**

```bash
cd websimple
python3 app.py
```

### **4. Acessar:**
- **URL:** `http://localhost:5000`
- **Mobile:** `http://[IP_SEU_COMPUTADOR]:5000`

---

## 🔄 COMPARAÇÃO DAS DUAS OPÇÕES

| Recurso | sne_radar_web.py | websimple/app.py |
|---------|------------------|------------------|
| **Porta** | 9999 | 5000 |
| **Complexidade** | Alta (3334 linhas) | Baixa (100 linhas) |
| **Autenticação** | ✅ Sim | ❌ Não |
| **Templates** | 8 arquivos | 1 arquivo |
| **Dashboard** | ✅ Completo | ✅ Terminal simples |
| **Mobile** | ✅ Responsivo | ✅ Responsivo |
| **Comandos Terminal** | ❌ Não | ✅ Todos |
| **Gráficos** | ✅ TradingView | 📝 Futuro |
| **Status** | ✅ Funcional | 🚧 A implementar |

---

## 🎯 RECOMENDAÇÃO

### **Para uso IMEDIATO:**
```bash
# Usar dashboard existente
python3 sne_radar_web.py
# Acessar: http://localhost:9999
```

### **Para replicar terminal em web:**
```bash
# Implementar websimple (plano criado)
cd websimple
python3 app.py  # Após criar arquivos
# Acessar: http://localhost:5000
```

---

## 📱 ACESSO VIA MOBILE

### **Na mesma rede Wi-Fi:**

1. **Descobrir IP do computador:**
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Exemplo output:
inet 192.168.1.100
```

2. **Acessar do celular:**
```
http://192.168.1.100:9999  (dashboard completo)
ou
http://192.168.1.100:5000  (terminal simples)
```

3. **Adicionar ao favoritos no mobile:**
- Safari: Compartilhar → Adicionar à Tela Inicial
- Chrome: Menu → Adicionar à tela inicial

---

## 🚀 RODAR AMBOS SIMULTANEAMENTE

```bash
# Terminal 1 - Dashboard completo
python3 sne_radar_web.py

# Terminal 2 - Terminal web (futuro)
cd websimple
python3 app.py
```

**Acessos:**
- `http://localhost:9999` → Dashboard completo
- `http://localhost:5000` → Terminal web

---

## ⚡ INÍCIO RÁPIDO (COMANDO ÚNICO)

### **Dashboard existente:**
```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN && \
source venv/bin/activate && \
python3 sne_radar_web.py
```

**Resultado:**
```
🚀 Iniciando SNE Radar Web...
🌐 Acesse: http://localhost:9999
✅ SNE Radar Web iniciado!
```

---

## 🐛 TROUBLESHOOTING

### **Erro: Port 9999 already in use**
```bash
# Verificar quem está usando
lsof -i :9999

# Matar processo
kill -9 [PID]
```

### **Erro: Module not found**
```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### **Mobile não acessa**
```bash
# Verificar firewall
# macOS: System Preferences → Security → Firewall
# Permitir Python

# Verificar se está na mesma rede Wi-Fi
# Testar ping do celular para o computador
```

---

## ✅ CONCLUSÃO

**Para rodar AGORA:**
```bash
python3 sne_radar_web.py
# Acessar: http://localhost:9999
```

**Para criar terminal web simples:**
- Seguir plano em `PLANO_DASHBOARD_WEB_SIMPLES.md`
- Implementar arquivos da seção "ETAPA 2"
- Rodar: `python3 websimple/app.py`



