# 🚀 DEPLOY SIMPLES - SEM DOCKER LOCAL

## ✅ SOLUÇÃO: Usar Cloud Build

Você **NÃO precisa** instalar Docker Desktop! O Cloud Build faz tudo na nuvem.

---

## 🎯 COMANDO ÚNICO

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
./deploy_cloud_build.sh sne-v1 us-central1
```

Isso vai:
1. ✅ Buildar todas as imagens na nuvem
2. ✅ Pushar para Artifact Registry
3. ✅ Executar migrações do banco
4. ✅ Fazer deploy dos 4 serviços
5. ✅ Atualizar Cloud Run com as imagens corretas

---

## ⏱️ TEMPO ESTIMADO

- **Build**: ~5-10 minutos
- **Deploy**: ~2-3 minutos
- **Total**: ~10-15 minutos

---

## 📋 O QUE ACONTECE

1. **Cloud Build recebe o código**
2. **Builda as 4 imagens Docker** (na nuvem)
3. **Pusha para Artifact Registry**
4. **Executa migrações Alembic** no Cloud SQL
5. **Faz deploy dos serviços** no Cloud Run
6. **Atualiza as URLs** dos serviços

---

## ✅ DEPOIS DO DEPLOY

Teste os serviços:

```bash
# Health checks
curl https://sne-web-pqhownilea-uc.a.run.app/health
curl https://sne-worker-pqhownilea-uc.a.run.app/health
curl https://sne-auto-pqhownilea-uc.a.run.app/health
curl https://sne-telegram-pqhownilea-uc.a.run.app/health
```

---

## 🎉 VANTAGENS

- ✅ Não precisa instalar Docker
- ✅ Build mais rápido (na nuvem)
- ✅ Tudo automático
- ✅ Executa migrações
- ✅ Deploy completo

---

**💡 Execute agora:**

```bash
./deploy_cloud_build.sh sne-v1 us-central1
```



