# 🔄 INTEGRAÇÃO EM ANDAMENTO - SNE RADAR → SNE 1.0 CLOUD

## ✅ O QUE FOI FEITO

### 1. Estrutura Compartilhada Criada
- ✅ `services/shared/__init__.py`
- ✅ `services/shared/binance_client.py` - Cliente Binance com Secret Manager
- ✅ `services/shared/database.py` - Conexão PostgreSQL

### 2. Motor Integrado em sne-web
- ✅ `services/sne-web/app/motor.py` - Wrapper para motor_renan.py
- ✅ `services/sne-web/app/api.py` - Atualizado para usar motor real
- ✅ `requirements.txt` - Atualizado com dependências necessárias

---

## 📋 PRÓXIMOS PASSOS

### 1. Copiar Módulos Necessários

Os módulos do SNE RADAR precisam estar acessíveis. Opções:

**Opção A: Copiar módulos para o serviço** (Recomendado para começar)
```bash
# Copiar módulos principais para sne-web
cp motor_renan.py services/sne-web/app/
cp contexto_global.py services/sne-web/app/
cp estrutura_mercado.py services/sne-web/app/
cp multi_timeframe.py services/sne-web/app/
cp confluencia.py services/sne-web/app/
cp indicadores.py services/sne-web/app/
# ... outros módulos necessários
```

**Opção B: Usar sys.path** (Já implementado)
- O `motor.py` já adiciona o diretório raiz ao sys.path
- Mas precisa garantir que os módulos estejam no contexto do build

### 2. Atualizar Dockerfile

O Dockerfile precisa copiar os módulos do SNE para o container:

```dockerfile
# Copiar módulos do SNE
COPY motor_renan.py ./
COPY contexto_global.py ./
COPY estrutura_mercado.py ./
COPY multi_timeframe.py ./
COPY confluencia.py ./
COPY indicadores.py ./
# ... outros módulos
```

### 3. Testar Localmente

```bash
# Rodar com docker-compose
docker-compose -f docker-compose.dev.yml up sne-web

# Testar
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'
```

### 4. Build e Deploy

```bash
./deploy_cloud_build.sh sne-v1 us-central1
```

---

## 🔍 MÓDULOS NECESSÁRIOS

Baseado nos imports do `motor_renan.py`:

### Essenciais
- `motor_renan.py` ✅ (já referenciado)
- `contexto_global.py`
- `estrutura_mercado.py`
- `multi_timeframe.py`
- `confluencia.py`
- `fluxo_ativo.py`
- `catalogo_magnetico.py`
- `padroes_graficos.py`
- `indicadores.py`
- `indicadores_avancados.py`
- `analise_candles_detalhada.py`
- `gestao_risco_profissional.py`
- `relatorio_profissional.py`

### Dependências Python
- `pandas`
- `numpy`
- `requests`
- `google-cloud-secret-manager`

---

## ⚠️ CONSIDERAÇÕES

### 1. Tamanho do Container
- Muitos módulos podem aumentar o tamanho
- Considerar otimização futura

### 2. Imports Relativos
- Alguns módulos podem ter imports relativos
- Pode precisar ajustar paths

### 3. Dependências Externas
- Verificar se todos os módulos têm suas dependências
- Adicionar ao `requirements.txt` conforme necessário

---

## 🎯 ESTRATÉGIA RECOMENDADA

### Fase 1: Mínimo Viável (AGORA)
1. Copiar apenas módulos essenciais
2. Testar se funciona
3. Deploy e testar na nuvem

### Fase 2: Expansão
1. Adicionar módulos restantes gradualmente
2. Testar cada adição
3. Otimizar imports

### Fase 3: Otimização
1. Refatorar imports
2. Criar versões otimizadas dos módulos
3. Reduzir tamanho do container

---

## 📝 CHECKLIST

- [x] Estrutura compartilhada criada
- [x] Motor wrapper criado
- [x] API atualizada
- [x] Requirements atualizado
- [ ] Módulos copiados para serviço
- [ ] Dockerfile atualizado
- [ ] Teste local
- [ ] Deploy e teste na nuvem

---

**💡 Próximo passo**: Copiar os módulos essenciais e atualizar o Dockerfile!



