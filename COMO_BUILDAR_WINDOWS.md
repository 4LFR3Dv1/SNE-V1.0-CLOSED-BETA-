# 🪟 COMO BUILDAR NO WINDOWS

## ⚡ OPÇÃO RÁPIDA (PyInstaller)

```powershell
.\build_windows.ps1
```

**OU**

```cmd
build_windows.bat
```

**Resultado:** `dist\SNE_RADAR.exe`  
**Tempo:** 5-10 minutos

---

## 🛡️ OPÇÃO COM PROTEÇÃO (Nuitka)

```powershell
.\build_windows_nuitka.ps1
```

**OU**

```cmd
build_windows_nuitka.bat
```

**Resultado:** `dist\SNE_RADAR.dist\SNE_RADAR.exe`  
**Tempo:** 15-30 minutos  
**Proteção IP:** Código compilado para C++

---

## 📋 PRÉ-REQUISITOS

1. **Python 3.10+**
   - Download: https://www.python.org/
   - ⚠️ Marque "Add Python to PATH"

2. **Node.js**
   - Download: https://nodejs.org/
   - Versão LTS

3. **Visual Studio Build Tools** (apenas para Nuitka)
   - Download: https://visualstudio.microsoft.com/downloads/
   - Selecione "Desktop development with C++"

---

## 🎨 ADICIONAR ÍCONE

1. Converter PNG → ICO: https://convertio.co/png-ico/
2. Salvar em: `assets\logo_sne.ico`
3. Rebuildar

---

## 📊 COMPARAÇÃO

| | PyInstaller | Nuitka |
|---|---|---|
| **Tempo** | 5-10 min | 15-30 min |
| **Proteção IP** | 🟡 Média | 🟢 Alta |
| **Tamanho** | ~150-200 MB | ~100-150 MB |

---

**Para mais detalhes:** `BUILD_WINDOWS_COMPLETO.md`
