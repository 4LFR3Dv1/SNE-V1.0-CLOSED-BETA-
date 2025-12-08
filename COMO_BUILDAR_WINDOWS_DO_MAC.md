# 🍎 Como Criar Instalador Windows a partir do Mac

Este guia explica como criar o instalador Windows (`.exe`) mesmo estando no Mac.

## ⚠️ Limitação

**PyInstaller no Mac NÃO cria executáveis `.exe` para Windows.** Ele só cria `.app` para macOS.

## 🎯 Soluções Disponíveis

Você tem **4 opções** para criar o instalador Windows:

---

## ✅ OPÇÃO 1: GitHub Actions (RECOMENDADO - Mais Fácil)

**Vantagens:**
- ✅ Não precisa instalar nada no Mac
- ✅ Build automático em Windows real (na nuvem)
- ✅ Mais confiável
- ✅ Pode automatizar releases
- ✅ Gratuito para repositórios públicos

### Como usar:

1. **Configurar GitHub Actions:**
   ```bash
   ./setup_github_actions_windows.sh
   ```

2. **Fazer commit e push:**
   ```bash
   git add .github/workflows/build-windows.yml
   git commit -m "Add Windows build workflow"
   git push
   ```

3. **Executar no GitHub:**
   - Vá em: `https://github.com/seu-usuario/seu-repo/actions`
   - Clique em "Build Windows Installer"
   - Clique em "Run workflow"
   - Aguarde 5-10 minutos

4. **Baixar o instalador:**
   - Na aba "Artifacts" do workflow
   - Baixe `SNE_RADAR_Setup.exe`

**Pronto!** Você tem o instalador Windows sem precisar de Windows! 🎉

---

## ✅ OPÇÃO 2: Usar Wine (Emulação Windows)

**Vantagens:**
- ✅ Funciona no Mac
- ✅ Não precisa de máquina Windows

**Desvantagens:**
- ⚠️ Pode ter problemas de compatibilidade
- ⚠️ Requer instalar Wine

### Como usar:

1. **Instalar Wine:**
   ```bash
   brew install --cask wine-stable
   ```

2. **Baixar e instalar Inno Setup no Wine:**
   - Baixe: https://jrsoftware.org/isinfo.php
   - Execute: `wine innosetup-6.x.x.exe`
   - Instale normalmente

3. **Buildar o executável primeiro:**
   - Use GitHub Actions ou Docker para criar `dist/SNE_RADAR.exe`

4. **Criar o instalador:**
   ```bash
   ./build_windows_wine.sh
   ```

---

## ✅ OPÇÃO 3: Docker com Windows (Avançado)

**Vantagens:**
- ✅ Build em Windows real (container)
- ✅ Mais confiável que Wine

**Desvantagens:**
- ⚠️ Requer Docker Desktop
- ⚠️ Mais complexo

### Como usar:

1. **Instalar Docker Desktop:**
   ```bash
   brew install --cask docker
   ```

2. **Criar Dockerfile Windows:**
   (Precisa criar um Dockerfile específico)

3. **Build no container:**
   ```bash
   docker build -t sne-windows-build .
   ```

**Nota:** Esta opção requer mais configuração. GitHub Actions é mais fácil!

---

## ✅ OPÇÃO 4: Preparar e Buildar em Windows Depois

**Vantagens:**
- ✅ Mais simples (se você tem acesso a Windows)
- ✅ Build nativo

**Desvantagens:**
- ⚠️ Precisa de uma máquina Windows

### Como usar:

1. **Preparar arquivos:**
   ```bash
   ./preparar_build_windows.sh
   ```

2. **Copiar projeto para Windows:**
   - Via USB, Git, ou nuvem

3. **No Windows:**
   ```cmd
   build_windows.bat
   criar_instalador_windows.bat
   ```

---

## 🎯 Recomendação

**Use GitHub Actions (Opção 1)!**

É a forma mais fácil, confiável e não precisa instalar nada no seu Mac.

### Passo a Passo Rápido:

```bash
# 1. Configurar
./setup_github_actions_windows.sh

# 2. Commit e push
git add .github/workflows/build-windows.yml
git commit -m "Add Windows build"
git push

# 3. Ir no GitHub e executar o workflow
# 4. Baixar o instalador na aba Artifacts
```

**Pronto!** 🚀

---

## 🔍 Verificar Opções Disponíveis

Execute este comando para ver quais opções você tem disponíveis:

```bash
./criar_instalador_windows_mac.sh
```

Ele verifica:
- ✅ Se Wine está instalado
- ✅ Se Docker está disponível
- ✅ E mostra as opções recomendadas

---

## 📋 Resumo das Opções

| Opção | Dificuldade | Confiabilidade | Requer Instalação |
|-------|-------------|----------------|-------------------|
| GitHub Actions | ⭐ Fácil | ⭐⭐⭐⭐⭐ Excelente | ❌ Não |
| Wine | ⭐⭐ Média | ⭐⭐⭐ Boa | ✅ Sim (Wine) |
| Docker | ⭐⭐⭐ Difícil | ⭐⭐⭐⭐ Muito Boa | ✅ Sim (Docker) |
| Windows Real | ⭐ Fácil | ⭐⭐⭐⭐⭐ Excelente | ✅ Sim (Windows) |

---

**💡 Dica:** Se você não tem acesso a Windows e quer a solução mais fácil, use **GitHub Actions**!


