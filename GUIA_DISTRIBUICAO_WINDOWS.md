# 📦 GUIA: DISTRIBUIÇÃO SEGURA DO SNE_RADAR.exe

**Objetivo:** Enviar o SNE_RADAR.exe para teste sem comprometer a Propriedade Intelectual

---

## 🚀 CRIAR PACOTE DE DISTRIBUIÇÃO

### **Opção 1: PowerShell (Recomendado)**

```powershell
.\criar_pacote_distribuicao_windows.ps1
```

### **Opção 2: Batch**

```cmd
criar_pacote_distribuicao_windows.bat
```

---

## 📋 O QUE É CRIADO

O script cria um arquivo ZIP contendo:

- ✅ **SNE_RADAR.exe** (ou pasta SNE_RADAR.dist com executável)
- ✅ **EULA.txt** (Termos de uso)
- ✅ **README_INSTALACAO.txt** (Instruções)
- ✅ **AVISO_PROPRIEDADE_INTELECTUAL.txt** (Avisos legais)

**Arquivo:** `dist\SNE_RADAR_DISTRIBUICAO_[data_hora].zip`

---

## 🎯 PROCESSO COMPLETO

### **1. Buildar o Executável**

**Com PyInstaller (rápido):**
```powershell
.\build_windows.ps1
```

**Com Nuitka (melhor proteção):**
```powershell
.\build_windows_nuitka.ps1
```

### **2. Criar Pacote de Distribuição**

```powershell
.\criar_pacote_distribuicao_windows.ps1
```

### **3. Enviar para o Colega**

- **WeTransfer / Google Drive** (recomendado)
- **Email** (se arquivo < 25MB)
- **USB / HD externo** (presencial)

---

## ⚠️ AVISOS IMPORTANTES

### **Para o Colega:**
- Este é um build de **TESTE**
- **NÃO compartilhar** com terceiros
- **NÃO fazer engenharia reversa**
- **NÃO usar comercialmente** sem autorização

### **Para Você:**
- ⚠️ **PyInstaller não protege código** efetivamente
- ✅ **EULA cria barreira legal**
- ✅ **Nuitka oferece melhor proteção técnica**
- ✅ **Para máxima proteção, considere SaaS**

---

## 🔐 PROTEÇÃO ATUAL

### **Com PyInstaller:**
- ❌ Código Python pode ser extraído
- ✅ EULA legal protege contra uso indevido
- ✅ Avisos desencorajam engenharia reversa

### **Com Nuitka:**
- ✅ Código compilado para C++ (muito difícil de reverter)
- ✅ EULA legal protege contra uso indevido
- ✅ Múltiplas camadas de proteção

---

## 📝 CHECKLIST ANTES DE ENVIAR

- [ ] Executável buildado (PyInstaller ou Nuitka)
- [ ] Pacote ZIP criado
- [ ] EULA incluído no pacote
- [ ] Instruções de instalação incluídas
- [ ] Avisos de propriedade intelectual incluídos

---

## 🎯 RECOMENDAÇÃO

### **Para Teste Imediato:**
1. Use **PyInstaller** (`build_windows.ps1`)
2. Crie pacote (`criar_pacote_distribuicao_windows.ps1`)
3. Envie o ZIP

### **Para Melhor Proteção:**
1. Use **Nuitka** (`build_windows_nuitka.ps1`)
2. Crie pacote (`criar_pacote_distribuicao_windows.ps1`)
3. Envie o ZIP

---

**Documento criado em:** Janeiro 2025

