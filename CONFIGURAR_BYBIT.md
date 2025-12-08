# 🔧 CONFIGURAR BYBIT - GUIA RÁPIDO

## 1. Adicionar Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```bash
# Exchange principal (bybit ou binance)
EXCHANGE_NAME=bybit

# Credenciais Bybit
BYBIT_API_KEY=HGycbYV1tmVIzJW0ZC
BYBIT_SECRET_KEY=F7CEtn1DU3KCE6BvoYIFh6zqHy0zT8AyAMsL

# Testnet (opcional - false para produção)
BYBIT_TESTNET=false
```

## 2. Instalar Dependência

```bash
pip install pybit>=5.7.0
```

## 3. Aplicar Migration

```bash
python3 -m alembic upgrade head
```

## 4. Reiniciar App

```bash
python sne_radar_web.py
```

## ✅ Pronto!

O sistema agora usará Bybit como exchange padrão.


