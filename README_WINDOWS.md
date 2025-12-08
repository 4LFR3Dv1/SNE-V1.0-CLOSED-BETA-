# 🪟 Build para Windows - SNE RADAR

Guia completo para buildar o SNE RADAR como aplicação desktop no Windows.

---

## 📋 Pré-requisitos

### 1. Python 3.10 ou superior

- Download: https://www.python.org/downloads/
- ⚠️ **IMPORTANTE:** Marque "Add Python to PATH" durante a instalação

### 2. Node.js (apenas para buildar frontend)

- Download: https://nodejs.org/
- Versão LTS recomendada

### 3. Git (opcional, para clonar repositório)

- Download: https://git-scm.com/download/win

---

## 🚀 Build Rápido

### Opção 1: Script Batch (Mais Simples)

```cmd
build_windows.bat
```

### Opção 2: PowerShell (Recomendado)

```powershell
.\build_windows.ps1
```

### Opção 3: Manual

```cmd
REM 1. Instalar dependências
pip install pywebview pyinstaller

REM 2. Buildar frontend
cd frontend
npm install
npm run build
cd ..

REM 3. Buildar executável
python -m PyInstaller build_windows.spec --clean --noconfirm
```

---

## 📦 O que é Criado

Após o build, você terá:

```
dist/
└── SNE_RADAR.exe  (Executável standalone)
```

**Tamanho estimado:** ~150-200 MB

---

## ✅ O Executável Inclui

- ✅ Backend Python completo (Flask + todos os módulos)
- ✅ Frontend Vue.js buildado
- ✅ Todas as dependências Python
- ✅ Runtime Python (não precisa Python instalado)
- ✅ Banco SQLite (criado automaticamente na primeira execução)

**O usuário final NÃO precisa:**
- ❌ Instalar Python
- ❌ Instalar Node.js
- ❌ Instalar dependências
- ❌ Buildar nada
- ✅ **Apenas executar o .exe!**

---

## 🎯 Como Usar o Executável

### Executar

1. **Duplo clique** em `SNE_RADAR.exe`
2. Ou execute via terminal: `.\dist\SNE_RADAR.exe`

### Dados do Usuário

Os dados são salvos em:

```
%APPDATA%\SNE_RADAR\
├── sne_radar.db      (Banco de dados)
└── logs\             (Logs da aplicação)
```

---

## 🔧 Troubleshooting

### Erro: "Python não encontrado"

```cmd
REM Verificar se Python está no PATH
python --version

REM Se não funcionar, adicione Python ao PATH:
REM 1. Painel de Controle > Sistema > Variáveis de Ambiente
REM 2. Adicione Python ao PATH
```

### Erro: "Node.js não encontrado"

- Instale Node.js de: https://nodejs.org/
- Reinicie o terminal após instalar

### Erro: "pywebview não instalado"

```cmd
pip install pywebview
```

### Erro: "PyInstaller não encontrado"

```cmd
pip install pyinstaller
```

### Windows Defender bloqueia o .exe

1. Clique com botão direito no `.exe`
2. Selecione "Propriedades"
3. Clique em "Desbloquear" (se disponível)
4. Ou adicione exceção no Windows Defender

### Janela não abre

1. Execute via terminal para ver erros: `.\dist\SNE_RADAR.exe`
2. Verifique logs em: `%APPDATA%\SNE_RADAR\logs\`

---

## 🎨 Personalização

### Adicionar Ícone

1. Crie um arquivo `assets/logo_sne.ico`
2. Edite `build_windows.spec`:
   ```python
   icon='assets/logo_sne.ico',
   ```

### Mudar Nome do Executável

Edite `build_windows.spec`:
```python
name='MeuApp',  # Mude aqui
```

### Mostrar Console (Debug)

Edite `build_windows.spec`:
```python
console=True,  # Mostra console preto
```

---

## 📊 Comparação: macOS vs Windows

| Característica | macOS | Windows |
|----------------|-------|---------|
| **Formato** | `.app` bundle | `.exe` |
| **Tamanho** | ~200 MB | ~150-200 MB |
| **Dados** | `~/Library/Application Support/SNE_RADAR` | `%APPDATA%\SNE_RADAR` |
| **Execução** | Duplo clique | Duplo clique |
| **Launcher** | `launcher.sh` | Não necessário (executa direto) |

---

## 🚀 Distribuição

### Criar ZIP para Distribuição

```cmd
cd dist
powershell Compress-Archive -Path SNE_RADAR.exe -DestinationPath SNE_RADAR_Windows_v1.0.0.zip
```

### Criar Instalador (Opcional)

Para criar um instalador profissional, use:
- **NSIS** (Nullsoft Scriptable Install System)
- **Inno Setup**
- **WiX Toolset**

---

## 💡 Dicas

1. **Teste em máquina limpa** antes de distribuir
2. **Assine o executável** (requer certificado) para evitar avisos do Windows Defender
3. **Use console=True** durante desenvolvimento para ver erros
4. **Mude para console=False** na versão final

---

**Status:** ✅ Pronto para Windows!


