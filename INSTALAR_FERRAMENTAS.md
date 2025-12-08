# 🛠️ INSTALAR FERRAMENTAS PARA DEPLOY GCP

Guia para instalar todas as ferramentas necessárias antes do deploy.

---

## 📦 FERRAMENTAS NECESSÁRIAS

- [ ] **gcloud CLI** - Interface de linha de comando do Google Cloud
- [ ] **Terraform** - Infraestrutura como código
- [ ] **Docker** - Para build de imagens (já instalado ✅)

---

## 1️⃣ INSTALAR gcloud CLI (Google Cloud SDK)

### Opção A: Via Homebrew (Recomendado - Mac)

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Google Cloud SDK
brew install --cask google-cloud-sdk

# Verificar instalação
gcloud --version
```

### Opção B: Download Manual

```bash
# Baixar de: https://cloud.google.com/sdk/docs/install

# Ou via curl (Mac):
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verificar
gcloud --version
```

### Configurar gcloud

```bash
# Inicializar
gcloud init

# Ou apenas autenticar
gcloud auth login
```

---

## 2️⃣ INSTALAR Terraform

### Opção A: Via Homebrew (Recomendado - Mac)

```bash
brew install terraform

# Verificar
terraform --version
```

### Opção B: Download Manual

```bash
# Mac (Intel)
curl -O https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_darwin_amd64.zip
unzip terraform_1.6.0_darwin_amd64.zip
sudo mv terraform /usr/local/bin/

# Mac (Apple Silicon/M1/M2)
curl -O https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_darwin_arm64.zip
unzip terraform_1.6.0_darwin_arm64.zip
sudo mv terraform /usr/local/bin/

# Verificar
terraform --version
```

### Opção C: Via tfenv (Gerenciador de Versões)

```bash
# Instalar tfenv
brew install tfenv

# Instalar Terraform
tfenv install 1.6.0
tfenv use 1.6.0

# Verificar
terraform --version
```

---

## 3️⃣ VERIFICAR INSTALAÇÕES

Execute estes comandos para verificar se tudo está instalado:

```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar gcloud
gcloud --version

# Verificar Terraform
terraform --version

# Verificar Python (já tem 3.13 ✅)
python3 --version
```

**✅ Se todos retornarem versões, está pronto para deploy!**

---

## 🚀 PRÓXIMO PASSO

Após instalar as ferramentas, siga o guia:

**`DEPLOY_GCP.md`** - Guia completo de deploy

---

## 🆘 PROBLEMAS COMUNS

### Erro: "command not found: gcloud"

**Solução:**
```bash
# Adicionar ao PATH
echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.zshrc
source ~/.zshrc

# Ou reiniciar terminal
```

### Erro: "Homebrew not found"

**Solução:**
```bash
# Instalar Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Erro: "Permission denied" ao instalar

**Solução:**
```bash
# Usar sudo (se necessário)
sudo mv terraform /usr/local/bin/
```

---

**📚 Documentação Oficial:**
- gcloud: https://cloud.google.com/sdk/docs/install
- Terraform: https://developer.hashicorp.com/terraform/downloads



