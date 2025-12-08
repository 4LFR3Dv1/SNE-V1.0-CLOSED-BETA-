# ✅ INSTALAR DEPENDÊNCIAS CORRETAMENTE

## ⚠️ Erro Comum

**NÃO use:** `pip install sklearn`  
**USE:** `pip install scikit-learn`

O pacote `sklearn` está **depreciado**. Use sempre `scikit-learn`.

---

## ✅ Instalação Correta

### Opção 1: Instalar Tudo (Recomendado)

```bash
pip3 install -r requirements.txt
```

Isso instala todas as dependências de uma vez, incluindo `scikit-learn`.

### Opção 2: Instalar Manualmente

```bash
# Dependências principais
pip3 install flask flask-socketio flask-sqlalchemy flask-login flask-limiter flask-wtf
pip3 install requests pandas numpy scikit-learn
pip3 install matplotlib mplfinance pytz
pip3 install bcrypt websocket-client python-telegram-bot
pip3 install psycopg2-binary alembic fpdf2 mnemonic
```

---

## 🔍 Verificar Instalação

```bash
python3 -c "import sklearn; print('✅ scikit-learn instalado')"
python3 -c "import flask; print('✅ Flask instalado')"
python3 -c "import pandas; print('✅ Pandas instalado')"
```

---

## 🚀 Depois de Instalar

```bash
python3 sne_radar_web.py
```

---

## 📋 Dependências Principais

- `scikit-learn` (não `sklearn`) - Machine Learning
- `flask` - Framework web
- `pandas` - Análise de dados
- `numpy` - Cálculos numéricos
- `requests` - Chamadas HTTP

---

**Lembrete:** Sempre use `scikit-learn`, nunca `sklearn`!

