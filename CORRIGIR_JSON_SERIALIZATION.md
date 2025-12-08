# 🔧 Corrigir Erro de Serialização JSON

## ❌ Problema

Erro: `"Object of type bool is not JSON serializable"`

O problema ocorre porque o resultado do `motor_renan.analise_completa()` contém valores não serializáveis em JSON:
- Valores booleanos do numpy/pandas
- Arrays numpy
- DataFrames pandas
- Outros tipos não nativos do Python

## ✅ Correção Aplicada

Foi adicionada uma função `make_json_serializable()` em `services/sne-web/app/motor.py` que:
- Converte valores numpy para tipos Python nativos
- Converte DataFrames pandas para dicionários
- Converte arrays numpy para listas
- Garante que booleanos são tipos Python nativos
- Trata valores NaN/None corretamente

## 🚀 Aplicar Correção

### Opção 1: Rebuild e Redeploy Automático

```bash
./deploy_cloud_build.sh sne-v1 europe-west1
```

### Opção 2: Rebuild Apenas do sne-web

```bash
# Build e push da imagem
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_PROJECT_ID=sne-v1,_REGION=europe-west1 \
    --project=sne-v1

# Ou apenas rebuild do sne-web manualmente
cd services/sne-web
gcloud builds submit \
    --tag=europe-west1-docker.pkg.dev/sne-v1/sne-artifacts/sne-web:latest \
    --project=sne-v1

# Deploy
gcloud run deploy sne-web \
    --image=europe-west1-docker.pkg.dev/sne-v1/sne-artifacts/sne-web:latest \
    --region=europe-west1 \
    --project=sne-v1
```

## 🧪 Testar Após Correção

```bash
# Health check
curl https://sne-web-pqhownilea-ew.a.run.app/health

# API de análise (deve funcionar agora)
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'
```

## 📋 Arquivos Modificados

- `services/sne-web/app/motor.py` - Adicionada função `make_json_serializable()`

## 🔍 Verificar Logs

Se ainda houver problemas, verifique os logs:

```bash
gcloud run services logs read sne-web \
    --region=europe-west1 \
    --project=sne-v1 \
    --limit=50
```

---

**Execute o rebuild e redeploy para aplicar a correção!** 🚀

