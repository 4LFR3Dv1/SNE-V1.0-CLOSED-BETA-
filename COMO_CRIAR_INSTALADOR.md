# 📦 Como Criar Instalador Windows para SNE RADAR

Este guia explica como criar um **instalador profissional** (.exe) ao invés de apenas distribuir o executável.

## 🎯 Por que criar um instalador?

✅ **Vantagens do instalador:**
- Interface profissional de instalação
- Instala em `C:\Program Files\SNE RADAR` (local padrão)
- Cria atalhos no Menu Iniciar automaticamente
- Opção de atalho na área de trabalho
- Cria desinstalador automático
- Mais fácil para usuários finais
- Pode incluir licença, documentação, etc.

## 📋 Pré-requisitos

1. **Python e Node.js** (já instalados para buildar)
2. **Inno Setup** (gratuito) - https://jrsoftware.org/isinfo.php
   - Baixe e instale normalmente
   - É gratuito e open-source

## 🚀 Passo a Passo

### Passo 1: Instalar Inno Setup

1. Acesse: https://jrsoftware.org/isinfo.php
2. Baixe a versão mais recente
3. Instale normalmente
4. (Opcional) Durante a instalação, marque **"Add Inno Setup to PATH"**

### Passo 2: Buildar o Executável

Primeiro, você precisa ter o executável buildado:

```cmd
build_windows.bat
```

Aguarde o build terminar. Você deve ter:
```
dist\SNE_RADAR.exe
```

### Passo 3: Criar o Instalador

Execute um dos scripts:

**Opção A: Se Inno Setup está no PATH**
```cmd
criar_instalador_windows.bat
```

**Opção B: Se Inno Setup NÃO está no PATH**
```cmd
criar_instalador_windows_manual.bat
```

### Passo 4: Resultado

O instalador será criado em:
```
installer\SNE_RADAR_Setup.exe
```

Este arquivo pode ser distribuído para qualquer usuário Windows!

## 🎨 Personalizar o Instalador

Edite o arquivo `setup_sne_radar.iss` para personalizar:

### Informações Básicas

```innosetup
#define MyAppName "SNE RADAR"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Sua Empresa"
#define MyAppURL "https://seu-site.com"
```

### Adicionar Ícone

1. Crie ou baixe um arquivo `.ico`
2. Coloque na pasta do projeto
3. No arquivo `.iss`, adicione:
```innosetup
SetupIconFile=logo.ico
WizardImageFile=logo.bmp
```

### Adicionar Licença

1. Crie um arquivo `LICENSE.txt`
2. No arquivo `.iss`, adicione:
```innosetup
LicenseFile=LICENSE.txt
```

### Adicionar Informações Antes/Depois

```innosetup
InfoBeforeFile=INFO_ANTES.txt
InfoAfterFile=INFO_DEPOIS.txt
```

## 📦 O que o Instalador Faz?

1. **Copia arquivos** para `C:\Program Files\SNE RADAR`
2. **Cria atalhos** no Menu Iniciar
3. **Opção de atalho** na área de trabalho
4. **Cria desinstalador** em "Adicionar ou Remover Programas"
5. **Registra no sistema** para fácil desinstalação

## 🧪 Testar o Instalador

1. Execute `installer\SNE_RADAR_Setup.exe`
2. Siga o assistente de instalação
3. Verifique se o app aparece no Menu Iniciar
4. Teste executar o app
5. Teste desinstalar pelo Painel de Controle

## 🔧 Solução de Problemas

### Erro: "Inno Setup não encontrado"

**Solução:**
1. Instale o Inno Setup: https://jrsoftware.org/isinfo.php
2. Ou use o script manual: `criar_instalador_windows_manual.bat`
3. Ou adicione o Inno Setup ao PATH:
   - Normalmente em: `C:\Program Files (x86)\Inno Setup 6\`
   - Adicione ao PATH do Windows

### Erro: "Executável não encontrado"

**Solução:**
1. Primeiro build o executável: `build_windows.bat`
2. Verifique se existe: `dist\SNE_RADAR.exe`

### Instalador não cria atalhos

**Solução:**
1. Verifique se você executou como Administrador
2. O instalador precisa de privilégios de admin para criar atalhos

### Erro ao compilar o instalador

**Solução:**
1. Verifique se o arquivo `setup_sne_radar.iss` está correto
2. Abra o arquivo `.iss` no Inno Setup Compiler
3. Veja os erros detalhados na interface

## 📚 Documentação Adicional

- **Inno Setup Docs:** https://jrsoftware.org/ishelp/
- **Exemplos:** https://jrsoftware.org/ishelp/index.php?topic=examples

## 💡 Dicas

1. **Teste sempre** o instalador antes de distribuir
2. **Assine digitalmente** o instalador para evitar avisos do Windows
3. **Inclua documentação** no instalador (README, etc.)
4. **Versione corretamente** para facilitar atualizações

---

**Pronto!** Agora você pode criar instaladores profissionais para distribuição! 🚀


