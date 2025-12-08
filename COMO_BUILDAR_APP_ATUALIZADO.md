# 🔨 COMO BUILDAR O .APP ATUALIZADO

**Data:** 25 de Outubro de 2025  
**Versão:** Com Scanner de Oportunidades e Wick Radar

---

## 📋 PRÉ-REQUISITOS

### **1. Dependências Python:**
```bash
pip install pyinstaller pywebview flask flask-socketio pandas numpy
```

### **2. Dependências Node.js (para frontend):**
```bash
cd frontend
npm install
```

---

## 🚀 PROCESSO DE BUILD

### **Passo 1: Buildar Frontend**

```bash
cd frontend
npm run build
cd ..
```

**Verificar:**
- Deve existir `frontend/dist/index.html`
- Deve existir `frontend/dist/assets/` com arquivos JS/CSS

---

### **Passo 2: Verificar Módulos Novos**

Certifique-se de que os novos diretórios existem:
```bash
ls -la scanners/ notifications/ monitors/
```

**Deve mostrar:**
- `scanners/__init__.py`
- `scanners/volume_scanner.py`
- `scanners/pavio_scanner.py`
- `notifications/__init__.py`
- `notifications/telegram_notifier.py`
- `notifications/alert_formatter.py`
- `monitors/__init__.py`
- `monitors/opportunity_monitor.py`

---

### **Passo 3: Buildar o .app**

#### **Opção A: Usando o Script (Recomendado)**

```bash
chmod +x build_with_launcher.sh
./build_with_launcher.sh
```

#### **Opção B: Manual com PyInstaller**

```bash
pyinstaller build_mac_with_launcher.spec --clean
```

**Onde o .app será criado:**
- `dist/SNE_RADAR.app`

---

### **Passo 4: Testar o .app**

```bash
# Abrir o .app
open dist/SNE_RADAR.app

# OU copiar para Applications
cp -r dist/SNE_RADAR.app /Applications/
```

---

## 🔍 VERIFICAÇÕES PÓS-BUILD

### **1. Verificar Estrutura do .app**

```bash
# Verificar se módulos foram incluídos
ls -la dist/SNE_RADAR.app/Contents/Resources/scanners/
ls -la dist/SNE_RADAR.app/Contents/Resources/notifications/
ls -la dist/SNE_RADAR.app/Contents/Resources/monitors/
```

### **2. Verificar Frontend**

```bash
# Verificar se frontend foi incluído
ls -la dist/SNE_RADAR.app/Contents/Resources/frontend/dist/
```

### **3. Testar Funcionalidades**

1. **Abrir o app:**
   ```bash
   open dist/SNE_RADAR.app
   ```

2. **Verificar logs:**
   ```bash
   tail -f ~/Library/Application\ Support/SNE_RADAR/logs/scanner.log
   ```

3. **Verificar se monitor inicia:**
   - Deve aparecer: `✅ Monitor de oportunidades iniciado em background`
   - Deve aparecer: `Volume Scanner: ✅`
   - Deve aparecer: `Pavio Scanner: ✅`

4. **Acessar Wick Radar:**
   - Navegar para: `http://127.0.0.1:9999/wick-radar`
   - Ou clicar no link "🎯 Wick Radar" no Header

---

## ⚠️ TROUBLESHOOTING

### **Erro: "ModuleNotFoundError: No module named 'scanners'"**

**Solução:**
1. Verificar se `scanners/__init__.py` existe
2. Verificar se está no `datas` do spec file
3. Rebuildar com `--clean`:
   ```bash
   pyinstaller build_mac_with_launcher.spec --clean
   ```

### **Erro: "Frontend não encontrado"**

**Solução:**
1. Buildar frontend primeiro:
   ```bash
   cd frontend && npm run build && cd ..
   ```
2. Verificar se `frontend/dist/index.html` existe

### **Erro: "Monitor não disponível"**

**Solução:**
1. Verificar se todos os módulos foram incluídos no build
2. Verificar logs do app:
   ```bash
   cat ~/Library/Application\ Support/SNE_RADAR/logs/scanner.log
   ```

### **App não abre**

**Solução:**
1. Verificar permissões:
   ```bash
   chmod +x dist/SNE_RADAR.app/Contents/MacOS/launcher.sh
   ```
2. Verificar logs do sistema:
   ```bash
   log show --predicate 'process == "SNE_RADAR"' --last 5m
   ```

---

## 📝 CHECKLIST DE BUILD

### **Antes do Build:**
- [ ] Frontend buildado (`frontend/dist` existe)
- [ ] Módulos novos existem (`scanners/`, `notifications/`, `monitors/`)
- [ ] Dependências Python instaladas
- [ ] PyInstaller instalado

### **Durante o Build:**
- [ ] Spec file atualizado com novos módulos
- [ ] Build sem erros
- [ ] `.app` criado em `dist/`

### **Após o Build:**
- [ ] Estrutura do .app verificada
- [ ] Módulos incluídos corretamente
- [ ] Frontend incluído corretamente
- [ ] App abre sem erros
- [ ] Monitor inicia automaticamente
- [ ] Wick Radar acessível

---

## 🎯 COMANDOS RÁPIDOS

### **Build Completo (Tudo de uma vez):**

```bash
# 1. Buildar frontend
cd frontend && npm run build && cd ..

# 2. Limpar builds anteriores
rm -rf build dist

# 3. Buildar .app
pyinstaller build_mac_with_launcher.spec --clean

# 4. Testar
open dist/SNE_RADAR.app
```

### **Script Automatizado:**

Criar `build_completo.sh`:
```bash
#!/bin/bash
set -e

echo "🔨 Iniciando build completo do SNE_RADAR.app..."

# 1. Buildar frontend
echo "📦 Buildando frontend..."
cd frontend
npm run build
cd ..

# 2. Limpar builds anteriores
echo "🧹 Limpando builds anteriores..."
rm -rf build dist

# 3. Buildar .app
echo "🔨 Buildando .app..."
pyinstaller build_mac_with_launcher.spec --clean

# 4. Verificar estrutura
echo "✅ Verificando estrutura..."
if [ -d "dist/SNE_RADAR.app" ]; then
    echo "✅ .app criado com sucesso!"
    echo "📁 Localização: $(pwd)/dist/SNE_RADAR.app"
    echo ""
    echo "🧪 Para testar:"
    echo "   open dist/SNE_RADAR.app"
else
    echo "❌ Erro: .app não foi criado"
    exit 1
fi
```

Tornar executável:
```bash
chmod +x build_completo.sh
./build_completo.sh
```

---

## 📊 ESTRUTURA DO .APP FINAL

```
SNE_RADAR.app/
├── Contents/
│   ├── MacOS/
│   │   ├── launcher.sh
│   │   └── SNE_RADAR (executável Python)
│   ├── Resources/
│   │   ├── frontend/dist/ (✅ Frontend buildado)
│   │   ├── scanners/ (✅ NOVO)
│   │   │   ├── __init__.py
│   │   │   ├── volume_scanner.py
│   │   │   └── pavio_scanner.py
│   │   ├── notifications/ (✅ NOVO)
│   │   │   ├── __init__.py
│   │   │   ├── telegram_notifier.py
│   │   │   └── alert_formatter.py
│   │   └── monitors/ (✅ NOVO)
│   │       ├── __init__.py
│   │       └── opportunity_monitor.py
│   └── Info.plist
└── ...
```

---

## 🎯 RESULTADO ESPERADO

Após o build bem-sucedido:

1. **App abre normalmente**
2. **Monitor inicia automaticamente** (logs mostram "✅ Monitor iniciado")
3. **Wick Radar acessível** em `http://127.0.0.1:9999/wick-radar`
4. **Notificações funcionam** (quando alertas são detectados)
5. **Gráficos mostram wicks** na página Wick Radar

---

**Status:** ✅ Guia Completo de Build  
**Próximo Passo:** Executar build e testar



