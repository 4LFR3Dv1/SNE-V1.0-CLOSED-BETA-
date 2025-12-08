# ⚡ BUILD WINDOWS - GUIA RÁPIDO

## 🚀 OPÇÃO 1: PyInstaller (Rápido)

```powershell
.\build_windows.ps1
```

**Resultado:** `dist\SNE_RADAR.exe`  
**Tempo:** 5-10 minutos  
**Proteção IP:** 🟡 Média

---

## 🛡️ OPÇÃO 2: Nuitka (Melhor Proteção)

```powershell
.\build_windows_nuitka.ps1
```

**Resultado:** `dist\SNE_RADAR.dist\SNE_RADAR.exe`  
**Tempo:** 15-30 minutos  
**Proteção IP:** 🟢 Alta

---

## 📋 PRÉ-REQUISITOS

- ✅ Python 3.10+ (https://www.python.org/)
- ✅ Node.js (https://nodejs.org/)
- ✅ Para Nuitka: Visual Studio Build Tools

---

## 🎨 ADICIONAR ÍCONE

1. Converter PNG → ICO: https://convertio.co/png-ico/
2. Salvar em: `assets\logo_sne.ico`
3. Rebuildar

---

**Para mais detalhes:** `BUILD_WINDOWS_COMPLETO.md`

