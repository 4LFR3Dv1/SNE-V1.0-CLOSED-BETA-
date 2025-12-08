# 🔧 CORRIGIR INSTALAÇÃO DO GCLOUD

O gcloud está tentando usar Python 3.13 de um caminho que não existe. Vamos corrigir isso.

---

## 🎯 SOLUÇÃO RÁPIDA

### Opção 1: Configurar gcloud para usar Python disponível

```bash
# Configurar variável de ambiente
export CLOUDSDK_PYTHON=$(which python3)

# Tentar instalar novamente
brew install --cask google-cloud-sdk
```

### Opção 2: Usar Python do sistema (3.9.6)

```bash
# Configurar para usar Python do sistema
export CLOUDSDK_PYTHON=/usr/bin/python3

# Tentar instalar novamente
brew install --cask google-cloud-sdk
```

### Opção 3: Instalar Python 3.12 (mais compatível)

```bash
# Instalar Python 3.12
brew install python@3.12

# Configurar gcloud para usar Python 3.12
export CLOUDSDK_PYTHON=/usr/local/opt/python@3.12/bin/python3

# Tentar instalar novamente
brew install --cask google-cloud-sdk
```

---

## 🚀 SOLUÇÃO RECOMENDADA (Passo a Passo)

### 1. Limpar instalação anterior

```bash
# Remover instalação parcial
brew uninstall --cask google-cloud-sdk 2>/dev/null || true
rm -rf /usr/local/share/google-cloud-sdk 2>/dev/null || true
```

### 2. Configurar Python antes de instalar

```bash
# Usar Python do sistema (mais estável)
export CLOUDSDK_PYTHON=/usr/bin/python3

# Verificar
echo $CLOUDSDK_PYTHON
/usr/bin/python3 --version
```

### 3. Instalar gcloud novamente

```bash
# Instalar com Python configurado
brew install --cask google-cloud-sdk
```

### 4. Se ainda der erro, instalar manualmente

```bash
# Baixar e instalar manualmente
curl https://sdk.cloud.google.com | bash

# Adicionar ao PATH
echo 'export PATH="$HOME/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Inicializar
gcloud init
```

---

## ✅ VERIFICAR INSTALAÇÃO

```bash
# Verificar se gcloud funciona
gcloud --version

# Se funcionar, inicializar
gcloud init
```

---

## 🔄 ALTERNATIVA: Pular gcloud por enquanto

Se estiver com dificuldades, você pode:

1. **Usar Terraform direto** (sem gcloud CLI)
2. **Usar Console Web** da Google Cloud
3. **Instalar gcloud depois** quando precisar

O Terraform pode criar a infraestrutura sem precisar do gcloud CLI inicialmente.

---

**💡 Dica:** Se nenhuma solução funcionar, podemos continuar com Terraform e configurar o gcloud depois.



