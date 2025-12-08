# 🪟 BUILD PARA WINDOWS - GUIA COMPLETO

Guia completo para buildar o SNE RADAR no Windows com PyInstaller ou Nuitka.

---

## 📋 PRÉ-REQUISITOS

### **1. Python 3.10 ou superior**
- Download: https://www.python.org/downloads/
- ⚠️ **IMPORTANTE:** Marque "Add Python to PATH" durante a instalação
- Verificar: `python --version`

### **2. Node.js (para buildar frontend)**
- Download: https://nodejs.org/
- Versão LTS recomendada
- Verificar: `node --version`

### **3. Visual Studio Build Tools (para Nuitka)**
- Se usar Nuitka, instale: https://visualstudio.microsoft.com/downloads/
- Selecione "Desktop development with C++"
- Ou use: `winget install Microsoft.VisualStudio.2022.BuildTools`

---

## 🚀 OPÇÃO 1: BUILD COM PYINSTALLER (Rápido)

### **Método A: Script PowerShell (Recomendado)**

```powershell
.\build_windows.ps1
```

### **Método B: Script Batch**

```cmd
build_windows.bat
```

### **Método C: Manual**

```cmd
REM 1. Buildar frontend
cd frontend
npm install
npm run build
cd ..

REM 2. Buildar executável
python -m PyInstaller build_windows.spec --clean --noconfirm
```

**Resultado:** `dist\SNE_RADAR.exe`

**Proteção IP:** 🟡 Média (código pode ser extraído)

---

## 🛡️ OPÇÃO 2: BUILD COM NUITKA (Melhor Proteção)

### **Passo 1: Instalar Nuitka**

```cmd
pip install nuitka
```

### **Passo 2: Executar Script**

```powershell
.\build_windows_nuitka.ps1
```

**OU manualmente:**

```cmd
REM 1. Buildar frontend
cd frontend
npm install
npm run build
cd ..

REM 2. Buildar com Nuitka
python -m nuitka --standalone --enable-plugin=anti-bloat --enable-plugin=pywebview --include-data-dir=frontend/dist=frontend/dist --include-module=flask --include-module=flask_socketio --include-module=motor_renan --output-dir=dist --output-filename=SNE_RADAR.exe --windows-console-mode=disable sne_desktop.py
```

**Resultado:** `dist\SNE_RADAR.dist\SNE_RADAR.exe`

**Proteção IP:** 🟢 Alta (código compilado para C++)

---

## 📦 O QUE É CRIADO

### **Com PyInstaller:**
```
dist/
└── SNE_RADAR.exe  (Standalone, ~150-200 MB)
```

### **Com Nuitka:**
```
dist/
└── SNE_RADAR.dist/
    ├── SNE_RADAR.exe
    └── [dependências]
```

---

## ✅ O EXECUTÁVEL INCLUI

- ✅ Backend Python completo (Flask + todos os módulos)
- ✅ Frontend Vue.js buildado
- ✅ Todas as dependências Python
- ✅ Runtime Python (não precisa Python instalado)
- ✅ Banco SQLite (criado automaticamente)

**O usuário final NÃO precisa:**
- ❌ Instalar Python
- ❌ Instalar Node.js
- ❌ Instalar dependências
- ✅ **Apenas executar o .exe!**

---

## 🎨 ADICIONAR ÍCONE

### **1. Converter PNG para ICO**

No Windows, você pode usar:
- **Online:** https://convertio.co/png-ico/
- **Ou criar:** `assets/logo_sne.ico` (256x256)

### **2. Atualizar build_windows.spec**

```python
icon='assets/logo_sne.ico',  # Linha 116
```

### **3. Rebuildar**

```cmd
python -m PyInstaller build_windows.spec --clean --noconfirm
```

---

## 🔧 TROUBLESHOOTING

### **Erro: "Python não encontrado"**
```cmd
REM Verificar se Python está no PATH
python --version

REM Se não funcionar, reinstale Python marcando "Add to PATH"
```

### **Erro: "PyInstaller não encontrado"**
```cmd
pip install pyinstaller
```

### **Erro: "Node.js não encontrado"**
- Instale Node.js de: https://nodejs.org/
- Reinicie o terminal após instalar

### **Erro: "Nuitka precisa compilador C++"**
- Instale Visual Studio Build Tools
- Ou use PyInstaller (mais simples)

### **Executável muito grande**
- Normal: PyInstaller inclui tudo (~150-200 MB)
- Nuitka pode ser menor, mas requer mais configuração

### **Windows Defender bloqueia o .exe**
- Isso é normal para executáveis não assinados
- Clique em "Mais informações" > "Executar mesmo assim"
- Ou adicione exceção no Windows Defender

---

## 📊 COMPARAÇÃO

| Aspecto | PyInstaller | Nuitka |
|---------|-------------|--------|
| **Facilidade** | 🟢 Fácil | 🟡 Média |
| **Velocidade Build** | 🟢 Rápido (5-10 min) | 🟡 Lento (15-30 min) |
| **Tamanho Executável** | 🟡 ~150-200 MB | 🟢 ~100-150 MB |
| **Proteção IP** | 🟡 Média | 🟢 Alta |
| **Performance** | 🟡 Boa | 🟢 Melhor |
| **Requisitos** | Python + PyInstaller | Python + Nuitka + Compilador C++ |

---

## 🎯 RECOMENDAÇÃO

### **Para Teste Rápido:**
→ Use **PyInstaller** (`build_windows.ps1`)

### **Para Distribuição com Proteção:**
→ Use **Nuitka** (`build_windows_nuitka.ps1`)

---

## 📝 PRÓXIMOS PASSOS

1. ✅ Escolher método (PyInstaller ou Nuitka)
2. ✅ Executar script de build
3. ✅ Testar o executável
4. ✅ Criar pacote de distribuição (se necessário)

---

**Para mais detalhes, veja:** `README_WINDOWS.md`

