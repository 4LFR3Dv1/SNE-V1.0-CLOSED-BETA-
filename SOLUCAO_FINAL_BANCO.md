# ✅ SOLUÇÃO FINAL: Inicializar Banco

## 🎯 MÉTODO RECOMENDADO: Cloud Storage + gcloud sql import

Este método funciona mesmo com IP privado!

---

## 🚀 EXECUTAR AGORA

```bash
./inicializar_banco_gcs.sh sne-v1 sne-db-prod sne
```

Este script:
1. ✅ Cria um bucket temporário no Cloud Storage
2. ✅ Faz upload do arquivo SQL
3. ✅ Importa o SQL no banco via `gcloud sql import sql`
4. ✅ Limpa o arquivo temporário

---

## 📋 O QUE O SCRIPT FAZ

1. **Cria bucket** (se não existir): `sne-v1-temp-sql`
2. **Upload SQL**: Envia `criar_tabelas.sql` para o bucket
3. **Importa SQL**: Executa o SQL no banco via `gcloud sql import sql`
4. **Limpa**: Remove o arquivo temporário

---

## 🔍 VERIFICAR TABELAS

Depois de executar, você pode verificar as tabelas usando Cloud Shell:

```bash
# No Cloud Shell
gcloud sql connect sne-db-prod --user=sne_admin --database=sne
# Quando pedir senha:
gcloud secrets versions access latest --secret=sne-db-password --project=sne-v1

# No prompt do PostgreSQL:
\dt
```

---

## ⚠️ ALTERNATIVA: Habilitar IP Público Temporariamente

Se preferir usar `gcloud sql connect`:

```bash
# Habilitar IP público
gcloud sql instances patch sne-db-prod \
    --assign-ip \
    --project=sne-v1

# Conectar
gcloud sql connect sne-db-prod --user=sne_admin --database=sne

# Executar SQL (cole o conteúdo de criar_tabelas.sql)

# Desabilitar IP público (segurança)
gcloud sql instances patch sne-db-prod \
    --no-assign-ip \
    --project=sne-v1
```

**⚠️ Não recomendado para produção!**

---

## 🎯 RECOMENDAÇÃO

**Use o script `inicializar_banco_gcs.sh`** - É mais seguro e funciona com IP privado!

Execute:

```bash
./inicializar_banco_gcs.sh sne-v1 sne-db-prod sne
```

---

**💡 Dica**: O método via Cloud Storage é o mais seguro e funciona sempre, mesmo com IP privado!



