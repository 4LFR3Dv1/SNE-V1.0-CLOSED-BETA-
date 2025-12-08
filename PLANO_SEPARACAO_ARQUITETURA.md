# 🔧 PLANO PRÁTICO: SEPARAÇÃO GRADUAL DA ARQUITETURA

**Objetivo:** Separar backend e frontend do `sne_radar_web.py` de forma gradual, sem quebrar nada.

---

## 🎯 ESTRATÉGIA: REFATORAÇÃO EM FASES

### **Filosofia:**
- ✅ **Sem breaking changes** - Tudo continua funcionando
- ✅ **Passo a passo** - Uma mudança por vez
- ✅ **Testável** - Verificar após cada fase
- ✅ **Reversível** - Pode voltar se necessário

---

## 📋 FASE 0: PREPARAÇÃO (Hoje - 30 min)

### **Objetivo:** Criar estrutura de diretórios, sem mudar código

### **1. Criar Estrutura de Diretórios**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Criar estrutura modular
mkdir -p app/{api,models,services,routes,utils,websocket}
mkdir -p app/api/{market,analysis,alerts,admin,export}
mkdir -p app/routes/{pages,auth}
mkdir -p app/services/{exchange,analysis,market}
mkdir -p app/utils/{security,validators,serializers}
```

**Estrutura resultante:**
```
SNE_BACKUP_CLEAN/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── market.py
│   │   ├── analysis.py
│   │   ├── alerts.py
│   │   ├── admin.py
│   │   └── export.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── exchange_client.py
│   │   ├── analysis_service.py
│   │   └── market_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── pages.py
│   │   └── auth.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── validators.py
│   │   └── serializers.py
│   └── websocket/
│       ├── __init__.py
│       └── events.py
├── sne_radar_web.py (mantido por enquanto)
└── ...
```

**Resultado:** Estrutura criada, código não muda

---

## 📋 FASE 1: ORGANIZAR CÓDIGO (Semana 1)

### **Objetivo:** Mover código para módulos, mantendo imports no arquivo principal

### **1.1. Extrair Modelos**

**Criar:** `app/models/models.py`

```python
# app/models/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()  # Será inicializado depois

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tier = db.Column(db.String(20), default='free')
    api_calls_today = db.Column(db.Integer, default=0)
    last_api_reset = db.Column(db.Date, default=datetime.date.today)
    subscription_expires = db.Column(db.DateTime, nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=True)

class MarketData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    ema8 = db.Column(db.Float, nullable=False)
    ema21 = db.Column(db.Float, nullable=False)
    sma200 = db.Column(db.Float, nullable=False)
    rsi = db.Column(db.Float, nullable=False)
    volatilidade = db.Column(db.Float, nullable=False)
    tendencia = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    message = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tier = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')
```

**No `sne_radar_web.py`, substituir modelos por:**
```python
from app.models.models import db, User, MarketData, Alert, Subscription
```

**✅ Resultado:** Modelos organizados, código funciona igual

---

### **1.2. Extrair Funções de Segurança**

**Criar:** `app/utils/security.py`

```python
# app/utils/security.py
import re
import bcrypt

def sanitize_input(text):
    """Sanitiza entrada de texto para prevenir XSS e injeção"""
    if not text:
        return ""
    
    text = re.sub(r'[<>"\']', '', str(text))
    text = text.strip()
    
    if len(text) > 100:
        text = text[:100]
    
    return text

def validate_username(username):
    """Valida formato do username"""
    if not username:
        return False, "Username é obrigatório"
    
    username = sanitize_input(username)
    
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return False, "Username deve ter 3-20 caracteres (apenas letras, números e _)"
    
    return True, username

def validate_password(password):
    """Valida força da senha"""
    if not password:
        return False, "Senha é obrigatória"
    
    if len(password) < 3:
        return False, "Senha deve ter pelo menos 3 caracteres"
    
    return True, password

def hash_password(password):
    """Cria hash seguro da senha"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    """Verifica senha contra hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

**No `sne_radar_web.py`:**
```python
from app.utils.security import (
    sanitize_input, validate_username, 
    validate_password, hash_password, verify_password
)
```

**✅ Resultado:** Segurança organizada

---

### **1.3. Extrair Cliente de Exchange**

**Criar:** `app/services/exchange_client.py`

```python
# app/services/exchange_client.py
"""
Cliente unificado para múltiplas exchanges
Substitui as 7 funções de busca duplicadas
"""
import requests
import pandas as pd
import time
from typing import Optional, Dict
import pytz

class ExchangeClient:
    """Cliente unificado para buscar dados de exchanges"""
    
    EXCHANGES = {
        'binance': {
            'base_url': 'https://api.binance.com/api/v3',
            'klines_endpoint': '/klines'
        },
        'coingecko': {
            'base_url': 'https://api.coingecko.com/api/v3',
            'klines_endpoint': '/ohlc'
        },
        # Adicionar outras exchanges...
    }
    
    def __init__(self, exchange: str = 'binance'):
        self.exchange = exchange.lower()
        if self.exchange not in self.EXCHANGES:
            raise ValueError(f"Exchange {exchange} não suportada")
        
        self.config = self.EXCHANGES[self.exchange]
        self.br_tz = pytz.timezone("America/Sao_Paulo")
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100, 
                   skip_rate_limit: bool = False) -> Optional[pd.DataFrame]:
        """
        Busca dados de candles/kline de uma exchange
        
        Args:
            symbol: Símbolo da moeda (ex: BTCUSDT)
            interval: Intervalo (1m, 5m, 1h, etc)
            limit: Número de candles
            skip_rate_limit: Se True, ignora rate limit
        
        Returns:
            DataFrame com dados OHLCV ou None se erro
        """
        if self.exchange == 'binance':
            return self._get_binance_klines(symbol, interval, limit, skip_rate_limit)
        elif self.exchange == 'coingecko':
            return self._get_coingecko_klines(symbol, interval, limit)
        # Adicionar outros...
        
        return None
    
    def _get_binance_klines(self, symbol: str, interval: str, 
                           limit: int, skip_rate_limit: bool) -> Optional[pd.DataFrame]:
        """Busca dados da Binance"""
        try:
            # Rate limit check (pode ser movido para outro lugar)
            if not skip_rate_limit:
                # Verificar rate limit aqui
                pass
            
            # Mapear intervalos
            interval_mapping = {
                "1m": "1m", "5m": "5m", "15m": "15m",
                "1h": "1h", "4h": "4h", "1d": "1d"
            }
            binance_interval = interval_mapping.get(interval, "1m")
            
            # Requisição
            url = f"{self.config['base_url']}{self.config['klines_endpoint']}"
            params = {
                "symbol": symbol,
                "interval": binance_interval,
                "limit": limit
            }
            
            time.sleep(0.1)  # Delay para rate limit
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Erro na API Binance: {response.status_code}")
                return None
            
            data = response.json()
            if not data or len(data) == 0:
                return None
            
            # Converter para DataFrame
            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "qav", "trades", "tbb", "tbq", "ignore"
            ])
            
            # Processar dados
            df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(self.br_tz)
            df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
                "open": float, "high": float, "low": float, "close": float,
                "volume": float, "trades": int
            })
            df.set_index("time", inplace=True)
            
            # Calcular indicadores básicos
            df["EMA8"] = df["close"].ewm(span=8).mean()
            df["EMA21"] = df["close"].ewm(span=21).mean()
            df["SMA200"] = df["close"].rolling(window=20).mean()
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados Binance: {e}")
            return None
    
    def _get_coingecko_klines(self, symbol: str, interval: str, limit: int):
        """Busca dados do CoinGecko (implementar depois)"""
        # TODO: Implementar
        return None

# Função de conveniência para manter compatibilidade
def buscar_dados_binance(symbol, interval, limit, skip_rate_limit=False):
    """Função wrapper para manter compatibilidade com código existente"""
    client = ExchangeClient('binance')
    return client.get_klines(symbol, interval, limit, skip_rate_limit)
```

**No `sne_radar_web.py`:**
```python
from app.services.exchange_client import buscar_dados_binance, ExchangeClient
```

**✅ Resultado:** Funções de busca unificadas, menos duplicação

---

### **1.4. Criar Blueprints de API**

**Criar:** `app/api/market.py`

```python
# app/api/market.py
from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.services.exchange_client import ExchangeClient

market_bp = Blueprint('market', __name__, url_prefix='/api')

@market_bp.route('/market-data')
@login_required
def get_market_data():
    """Endpoint para buscar dados de mercado"""
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        interval = request.args.get('interval', '1m')
        
        client = ExchangeClient('binance')
        df = client.get_klines(symbol, interval, 100, skip_rate_limit=True)
        
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados não disponíveis"}), 404
        
        # Processar e retornar dados
        # ... (lógica de análise)
        
        return jsonify({
            "success": True,
            "data": {
                "symbol": symbol,
                "price": float(df["close"].iloc[-1]),
                # ... mais dados
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

**Registrar no `sne_radar_web.py`:**
```python
from app.api.market import market_bp
app.register_blueprint(market_bp)
```

**✅ Resultado:** APIs organizadas em blueprints

---

## 📋 FASE 2: SEPARAR ROTAS (Semana 2)

### **Objetivo:** Separar rotas de API das rotas de templates

### **2.1. Blueprint de Páginas**

**Criar:** `app/routes/pages.py`

```python
# app/routes/pages.py
from flask import Blueprint, render_template, redirect, url_for, make_response
from flask_login import login_required, current_user

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    return redirect(url_for('pages.terminal_dashboard'))

@pages_bp.route('/terminal')
@login_required
def terminal_dashboard():
    """Dashboard terminal com comandos interativos"""
    response = make_response(render_template('dashboard_terminal.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@pages_bp.route('/professional')
@login_required
def professional_dashboard():
    """Dashboard profissional"""
    response = make_response(render_template('professional_dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@pages_bp.route('/pricing')
def pricing():
    """Página de planos"""
    return render_template('pricing.html')
```

**Registrar:**
```python
from app.routes.pages import pages_bp
app.register_blueprint(pages_bp)
```

---

### **2.2. Blueprint de Autenticação**

**Criar:** `app/routes/auth.py`

```python
# app/routes/auth.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from flask_login import login_user, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models.models import db, User
from app.utils.security import validate_username, validate_password, hash_password, verify_password

auth_bp = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        username_valid, username_msg = validate_username(username)
        password_valid, password_msg = validate_password(password)
        
        if not username_valid:
            flash(f'❌ {username_msg}')
            return render_template('login.html')
        
        # Buscar usuário
        user = User.query.filter_by(username=username).first()
        
        if user and verify_password(password, user.password.encode('utf-8')):
            login_user(user)
            return redirect(url_for('pages.dashboard'))
        else:
            flash('❌ Usuário ou senha incorretos')
    
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-cache'
    return response

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    # Implementar registro...
    pass

@auth_bp.route('/logout')
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('pages.pricing'))
```

**Registrar:**
```python
from app.routes.auth import auth_bp
app.register_blueprint(auth_bp)
```

---

## 📋 FASE 3: SEPARAR FRONTEND (Semana 3-4)

### **Objetivo:** Frontend Vue.js completamente independente

### **3.1. Criar API Backend Pura**

**Criar:** `app/api/__init__.py`

```python
# app/api/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Importar todos os blueprints de API
from app.api import market, analysis, alerts, admin, export

def register_blueprints(app):
    """Registra todos os blueprints de API"""
    app.register_blueprint(api_bp)
    app.register_blueprint(market.market_bp)
    app.register_blueprint(analysis.analysis_bp)
    app.register_blueprint(alerts.alerts_bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(export.export_bp)
```

---

### **3.2. Criar App Factory (Backend Puro)**

**Criar:** `app/__init__.py`

```python
# app/__init__.py
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO()

def create_app(config_name='default'):
    """Factory function para criar Flask app"""
    
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sne_radar.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Importar modelos
    from app.models import models
    
    # Registrar blueprints
    from app.api import register_blueprints as register_api
    from app.routes.pages import pages_bp
    from app.routes.auth import auth_bp
    
    register_api(app)
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    
    # Configurar login manager
    from app.models.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app
```

---

### **3.3. Novo Arquivo Principal (Backend Puro)**

**Criar:** `app/main.py`

```python
# app/main.py
"""
Backend API puro do SNE Radar
Apenas APIs REST, sem servir templates HTML
"""
import os
from app import create_app, socketio

app = create_app()

@app.route('/health')
def health():
    """Health check"""
    return {"status": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9999))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

---

### **3.4. Frontend Independe do Backend**

**Configurar:** `frontend/vite.config.js` (já existe)

```javascript
// Já configurado! Frontend já faz proxy para backend
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:9999',
      changeOrigin: true
    },
    '/socket.io': {
      target: 'http://localhost:9999',
      ws: true
    }
  }
}
```

**✅ Resultado:** Frontend e backend separados, comunicando via API

---

## 📋 FASE 4: LIMPEZA FINAL (Semana 5)

### **Objetivo:** Remover código antigo, manter apenas o necessário

### **4.1. Migrar Templates Antigos para Vue.js**

- Converter `/dashboard` para componente Vue
- Converter `/professional` para componente Vue
- Converter `/login` para componente Vue

### **4.2. Remover Templates HTML Antigos**

- Manter apenas se necessário para fallback
- Ou migrar tudo para Vue.js

### **4.3. Limpar `sne_radar_web.py`**

- Remover rotas duplicadas
- Remover funções movidas para módulos
- Manter apenas como wrapper temporário ou remover completamente

---

## 🚀 COMO EXECUTAR

### **Passo a Passo Imediato (Fase 0 - 30 min):**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Criar estrutura
mkdir -p app/{api/{market,analysis,alerts,admin,export},models,services,routes/{pages,auth},utils,websocket}

# Criar __init__.py em todos os diretórios
find app -type d -exec touch {}/__init__.py \;

# Verificar estrutura
tree app -L 3
```

**✅ Pronto! Estrutura criada, nada quebrou**

---

### **Próximos Passos:**

1. **Hoje:** Criar estrutura (Fase 0)
2. **Esta Semana:** Mover modelos e segurança (Fase 1.1-1.2)
3. **Próxima Semana:** Mover ExchangeClient (Fase 1.3)
4. **Seguinte:** Criar blueprints de API (Fase 1.4)
5. **Depois:** Separar rotas (Fase 2)

---

## ✅ CHECKLIST DE PROGRESSO

### **Fase 0: Preparação**
- [ ] Criar estrutura de diretórios
- [ ] Criar `__init__.py` em todos os diretórios
- [ ] Documentar estrutura

### **Fase 1: Organizar Código**
- [ ] Extrair modelos (`app/models/models.py`)
- [ ] Extrair segurança (`app/utils/security.py`)
- [ ] Criar ExchangeClient (`app/services/exchange_client.py`)
- [ ] Criar blueprints de API (`app/api/*`)

### **Fase 2: Separar Rotas**
- [ ] Blueprint de páginas (`app/routes/pages.py`)
- [ ] Blueprint de autenticação (`app/routes/auth.py`)
- [ ] Registrar blueprints

### **Fase 3: Separar Frontend**
- [ ] Criar app factory (`app/__init__.py`)
- [ ] Criar backend puro (`app/main.py`)
- [ ] Frontend independe do backend

### **Fase 4: Limpeza**
- [ ] Migrar templates para Vue.js
- [ ] Remover código antigo
- [ ] Limpar `sne_radar_web.py`

---

## 🎯 RESULTADO FINAL

### **Antes (Híbrido):**
```
sne_radar_web.py (3,829 linhas)
├── Modelos
├── Segurança
├── Lógica de negócio
├── APIs
├── Templates
└── Tudo misturado
```

### **Depois (Separado):**
```
app/
├── api/           # Apenas APIs REST
├── models/        # Modelos de dados
├── services/      # Lógica de negócio
├── routes/        # Rotas de templates (temporário)
└── utils/         # Utilidades

frontend/          # Frontend Vue.js independente
├── src/
└── dist/

sne_radar_web.py   # Wrapper ou removido
```

---

**Pronto para começar? Vou criar os arquivos iniciais agora!** 🚀

