# 🔧 CORRIGIR DEPENDÊNCIAS

## ⚠️ PROBLEMA

Erro: `No module named 'scipy'`

O módulo `scipy` é necessário mas não está no `requirements.txt`.

---

## ✅ CORREÇÃO APLICADA

Adicionado `scipy>=1.11.0` ao `requirements.txt` do `sne-web`.

---

## 📋 DEPENDÊNCIAS ADICIONADAS

- ✅ `scipy>=1.11.0` - Usado em `indicadores_avancados.py`, `padroes_graficos.py`, `estrutura_mercado.py`

---

## 🔄 PRÓXIMO PASSO: DEPLOY NOVAMENTE

Execute o deploy novamente para incluir a dependência:

```bash
./deploy_cloud_build.sh sne-v1 us-central1
```

---

## 🔍 VERIFICAR OUTRAS DEPENDÊNCIAS

Se houver mais erros de módulos faltando, adicione ao `requirements.txt`:

```bash
# Verificar logs para erros de import
gcloud run services logs read sne-web --region=us-central1 --limit=100 | grep -i "module\|import"
```

---

**💡 Execute o deploy novamente para aplicar a correção!**



