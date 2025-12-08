# 🔧 MODIFICAR DASHBOARD ATUAL - SEM CRIAR NOVO

## 🎯 OBJETIVO

Modificar APENAS a rota `/dashboard` no `sne_radar_web.py` para funcionar SEM threads/WebSocket, mantendo o resto intacto.

---

## 📝 ALTERAÇÕES NECESSÁRIAS

### **1. ADICIONAR NOVOS ENDPOINTS NO sne_radar_web.py**

**Adicionar ANTES da rota /dashboard (após linha 2110):**

```python
# ========================================
# NOVOS ENDPOINTS SOB DEMANDA PARA DASHBOARD
# ========================================

@app.route('/api/dashboard/execute/<command>', methods=['POST'])
@login_required
def api_dashboard_execute(command):
    """Executa comandos do terminal sob demanda para o dashboard"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from motor_renan import analise_completa
        from contexto_mercado import analisar_contexto_mercado
        from multi_pair_context import analisar_mercado_completo
        from comando_campo_magnetico import gerar_campo_magnetico_simples
        
        data = request.json or {}
        command = command.upper()
        
        if command == 'R':
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
                    'tp3': resultado['sintese'].get('tp3')
                }
            })
        
        elif command == 'CTX':
            contexto = analisar_contexto_mercado()
            return jsonify({'success': True, 'type': 'context', 'data': contexto})
        
        elif command == 'MULT':
            analise = analisar_mercado_completo()
            return jsonify({'success': True, 'type': 'multi', 'data': analise})
        
        elif command == 'CM':
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1h')
            resultado = gerar_campo_magnetico_simples(symbol, timeframe)
            return jsonify({
                'success': True,
                'type': 'magnetic',
                'image_url': f"/static/reports/campo_magnetico/{os.path.basename(resultado['caminho'])}",
                'data': resultado
            })
        
        else:
            return jsonify({'success': False, 'error': f'Comando "{command}" não implementado'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard/commands')
@login_required
def api_dashboard_commands():
    """Lista comandos disponíveis"""
    return jsonify({
        'success': True,
        'commands': [
            {'code': 'R', 'name': 'Scanner Técnico', 'description': 'Análise completa'},
            {'code': 'CTX', 'name': 'Contexto Macro', 'description': 'Regime e sentiment'},
            {'code': 'MULT', 'name': 'Multi-Pair', 'description': 'Comparação de pares'},
            {'code': 'CM', 'name': 'Campo Magnético', 'description': 'Visualização 3D'},
        ]
    })
```

---

### **2. MODIFICAR A ROTA /dashboard**

**SUBSTITUIR a rota atual (linhas 2111-2119):**

```python
@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal sem threads - versão sob demanda"""
    response = make_response(render_template('dashboard_simple.html'))  # ← MUDANÇA
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
```

---

### **3. CRIAR TEMPLATE dashboard_simple.html**

**Copiar `templates/dashboard.html` para `templates/dashboard_simple.html`**

**Então MODIFICAR o JavaScript:**

**LINHA 377 - REMOVER:**
```javascript
const socket = io();
```

**SUBSTITUIR por:**
```javascript
// Sem WebSocket - usar AJAX sob demanda
```

**LINHA 682-688 - SUBSTITUIR:**
```javascript
socket.on('market_data', function(data) {
    updateMarketSummary(data);
    updateMarketData(data);
    updateEstrategias(data);
    updateInterpretacao(data);
    updateDicas(data);
});
```

**POR:**
```javascript
// Função para atualizar manualmente
async function refreshData() {
    try {
        const response = await fetch('/api/market-data?symbol=BTCUSDT');
        const data = await response.json();
        
        if (data && Object.keys(data).length > 0) {
            updateMarketSummary({symbol: 'BTCUSDT', data: data});
            updateMarketData({symbol: 'BTCUSDT', data: data});
            updateEstrategias({symbol: 'BTCUSDT', data: data});
            updateInterpretacao({symbol: 'BTCUSDT', data: data});
            updateDicas({symbol: 'BTCUSDT', data: data});
        }
    } catch (e) {
        console.error('Erro ao buscar dados:', e);
    }
}

// Botão de atualização manual
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar botão "Atualizar"
    const statusBar = document.querySelector('.status-bar');
    if (statusBar) {
        const refreshBtn = document.createElement('button');
        refreshBtn.innerHTML = '🔄 ATUALIZAR';
        refreshBtn.onclick = refreshData;
        refreshBtn.style.marginRight = '10px';
        statusBar.appendChild(refreshBtn);
    }
    
    // Primeira atualização
    refreshData();
    
    // Auto-refresh a cada 60s (opcional)
    setInterval(refreshData, 60000);
});
```

---

## ✅ RESUMO DAS ALTERAÇÕES

### **Arquivos a MODIFICAR:**

1. **`sne_radar_web.py`** - Adicionar 2 rotas novas
   - `/api/dashboard/execute/<command>` (linha 2110)
   - `/api/dashboard/commands` (linha 2140)
   - Modificar rota `/dashboard` (linha 2111)

2. **`templates/dashboard_simple.html`** - CRIAR novo
   - Copiar de `dashboard.html`
   - Modificar JavaScript (remover SocketIO)
   - Adicionar botão "Atualizar"

### **Arquivos a MANTER COMO ESTÁ:**

- ✅ Todo o resto de `sne_radar_web.py`
- ✅ Todas as outras rotas
- ✅ Sistema de autenticação
- ✅ Banco de dados
- ✅ Configurações Render

---

## 🚀 RESULTADO

### **Antes:**
```
/dashboard → Depende de WebSocket → Thread contínua → Falha no Render
```

### **Depois:**
```
/dashboard → Botão "Atualizar" → Busca dados sob demanda → Funciona no Render ✅
```

---

**Quer que eu implemente essas modificações agora?**



