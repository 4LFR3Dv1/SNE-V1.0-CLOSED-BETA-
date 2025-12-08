# 🧪 TESTE LOCAL - SNE 1.0 CLOUD

Guia passo a passo para testar localmente.

---

## ⚠️ PRÉ-REQUISITO: Docker Desktop

**O Docker Desktop precisa estar rodando!**

### Como iniciar:
1. Abra o **Docker Desktop** no seu Mac
2. Aguarde até aparecer "Docker Desktop is running" na barra de menu
3. Verifique com: `docker ps`

---

## 🚀 PASSO A PASSO

### 1. Iniciar Docker Desktop

```bash
# Tentar abrir automaticamente
open -a Docker

# OU abra manualmente: Applications > Docker
```

### 2. Verificar se Docker está rodando

```bash
docker ps
```

Se retornar uma lista (mesmo que vazia), está funcionando! ✅

### 3. Iniciar todos os serviços

```bash
# Parar containers anteriores (se houver)
docker-compose -f docker-compose.dev.yml down

# Iniciar todos os serviços
docker-compose -f docker-compose.dev.yml up -d
```

**Isso vai iniciar:**
- ✅ PostgreSQL (porta 5432)
- ✅ Redis (porta 6379)
- ✅ sne-web (porta 8080)
- ✅ sne-worker (porta 8081)
- ✅ sne-auto (porta 8082)
- ✅ sne-telegram (porta 8083)

### 4. Aguardar serviços iniciarem

```bash
# Aguardar 15-20 segundos
sleep 20

# Verificar status
docker-compose -f docker-compose.dev.yml ps
```

Todos devem estar com status "Up" ✅

### 5. Testar Health Checks

```bash
# sne-web
curl http://localhost:8080/health

# sne-worker
curl http://localhost:8081/health

# sne-auto
curl http://localhost:8082/health

# sne-telegram
curl http://localhost:8083/health
```

**Resposta esperada:**
```json
{"status":"healthy","service":"sne-web","version":"1.0.0"}
```

### 6. Testar API

```bash
# Testar endpoint de análise
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","timeframe":"15m"}'
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "analysis": {
    "confluence_score": 7.5,
    "bias": "BULLISH",
    "recommendation": "LONG"
  }
}
```

### 7. Ver Logs

```bash
# Ver todos os logs
docker-compose -f docker-compose.dev.yml logs -f

# Ver logs de um serviço específico
docker-compose -f docker-compose.dev.yml logs -f sne-web
```

### 8. Parar Serviços

```bash
# Parar todos os serviços
docker-compose -f docker-compose.dev.yml down

# Parar e remover volumes (limpar dados)
docker-compose -f docker-compose.dev.yml down -v
```

---

## 🔍 TROUBLESHOOTING

### Erro: "Cannot connect to Docker daemon"

**Solução:** Inicie o Docker Desktop
```bash
open -a Docker
# Aguarde 30 segundos
docker ps  # Deve funcionar agora
```

### Erro: "Port already in use"

**Solução:** Parar serviços que estão usando as portas
```bash
# Ver o que está usando a porta 8080
lsof -i :8080

# Parar containers anteriores
docker-compose -f docker-compose.dev.yml down
```

### Serviço não inicia

**Solução:** Ver logs do serviço
```bash
# Ver logs detalhados
docker-compose -f docker-compose.dev.yml logs sne-web

# Verificar se há erros
docker-compose -f docker-compose.dev.yml logs | grep -i error
```

### PostgreSQL não conecta

**Solução:** Verificar se o container está saudável
```bash
# Verificar health do postgres
docker-compose -f docker-compose.dev.yml ps postgres

# Testar conexão manual
docker exec -it sne-postgres-dev psql -U sne_admin -d sne -c "SELECT 1;"
```

---

## ✅ CHECKLIST DE TESTE

- [ ] Docker Desktop está rodando
- [ ] Todos os containers estão "Up"
- [ ] Health checks retornam 200 OK
- [ ] API `/api/analyze` funciona
- [ ] Logs não mostram erros
- [ ] PostgreSQL está acessível
- [ ] Redis está acessível

---

## 🎯 PRÓXIMOS PASSOS

Se todos os testes passaram:

1. ✅ **Integrar código do SNE RADAR** nos serviços
2. ✅ **Fazer deploy na GCP** seguindo o CHECKLIST.md
3. ✅ **Configurar CI/CD** com Cloud Build

---

**🚀 Pronto para testar! Inicie o Docker Desktop e execute os comandos acima.**



