# 🚀 DEPLOY COM MÓDULOS INTEGRADOS

## ✅ MÓDULOS COPIADOS

15 módulos essenciais foram copiados para `services/sne-web/`:

1. ✅ motor_renan.py
2. ✅ contexto_global.py
3. ✅ estrutura_mercado.py
4. ✅ multi_timeframe.py
5. ✅ confluencia.py
6. ✅ fluxo_ativo.py
7. ✅ catalogo_magnetico.py
8. ✅ padroes_graficos.py
9. ✅ indicadores.py
10. ✅ indicadores_avancados.py
11. ✅ analise_candles_detalhada.py
12. ✅ gestao_risco_profissional.py
13. ✅ relatorio_profissional.py
14. ✅ calcular_suportes_resistencias.py
15. ✅ niveis_operacionais.py

---

## 📋 DEPENDÊNCIAS ATUALIZADAS

- ✅ scipy>=1.11.0 (adicionado)
- ✅ pandas, numpy (já estavam)
- ✅ pytz (adicionado)

---

## 🚀 DEPLOY AGORA

Execute o deploy:

```bash
./deploy_cloud_build.sh sne-v1 us-central1
```

---

## 🧪 DEPOIS DO DEPLOY

Teste os endpoints:

```bash
# Análise completa
curl -X POST https://sne-web-pqhownilea-uc.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'

# Sinal
curl "https://sne-web-pqhownilea-uc.a.run.app/api/signal?symbol=BTCUSDT&timeframe=1h"
```

---

## ⚠️ SE HOUVER MAIS ERROS

Verifique os logs:

```bash
gcloud run services logs read sne-web --region=us-central1 --limit=50 | grep -i "module\|import\|error"
```

E adicione os módulos faltando ao:
1. `copiar_modulos_sne.sh`
2. `services/sne-web/Dockerfile`

---

**💡 Execute o deploy agora para testar com todos os módulos!**



