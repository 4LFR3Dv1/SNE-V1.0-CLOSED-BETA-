# 🔧 CORRIGIR SECRETS APÓS TERRAFORM APPLY

## ⚠️ PROBLEMA

Os secrets foram criados, mas não têm versões. Os serviços Cloud Run precisam de versões dos secrets para funcionar.

---

## ✅ SOLUÇÃO: Criar Versões dos Secrets

Após o `terraform apply` terminar (mesmo com erros), execute:

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Gerar secret key
SECRET_KEY=$(openssl rand -base64 32)

# Criar versões dos secrets
echo -n "$SECRET_KEY" | gcloud secrets versions add sne-secret-key --data-file=-
echo -n "TEMPORARY_PLACEHOLDER" | gcloud secrets versions add sne-telegram-bot-token --data-file=-
echo -n "TEMPORARY_PLACEHOLDER" | gcloud secrets versions add sne-telegram-chat-id --data-file=-

# Verificar
gcloud secrets versions list sne-secret-key
```

---

## 🔄 DEPOIS: Aplicar Terraform Novamente

```bash
cd infra/terraform
terraform apply
```

Agora os serviços devem ser criados com sucesso!

---

## 📝 ATUALIZAR SECRETS COM VALORES REAIS

Depois que tudo estiver funcionando:

```bash
# Atualizar com valores reais
echo -n "SEU_TELEGRAM_BOT_TOKEN_REAL" | gcloud secrets versions add sne-telegram-bot-token --data-file=-
echo -n "SEU_CHAT_ID_REAL" | gcloud secrets versions add sne-telegram-chat-id --data-file=-
```

---

**💡 Dica:** Aguarde o `terraform apply` atual terminar antes de executar os comandos acima.



