# 🚀 Guia de Deploy SNE Radar no Render

## 📋 Pré-requisitos

1. **Conta no Render** - [render.com](https://render.com)
2. **Repositório no GitHub** - Código deve estar no GitHub
3. **Banco PostgreSQL** - Será criado automaticamente

## 🔧 Configuração Automática (Recomendado)

### 1. Usar o arquivo `render.yaml`

O arquivo `render.yaml` já está configurado para deploy automático:

```yaml
services:
  - type: web
    name: sne-radar-web
    env: python
    plan: free
    buildCommand: |
      pip install -r requirements_render.txt
      pip install psycopg2-binary
    startCommand: gunicorn --bind 0.0.0.0:$PORT sne_radar_web:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      # ... outras variáveis
```

### 2. Deploy via GitHub

1. **Push do código para GitHub**
2. **No Render Dashboard:**
   - Clique em "New +"
   - Selecione "Blueprint"
   - Conecte seu repositório
   - O Render detectará automaticamente o `render.yaml`

## 🔧 Configuração Manual

### 1. Criar Web Service

1. **Acesse** [dashboard.render.com](https://dashboard.render.com)
2. **Clique** em "New +" → "Web Service"
3. **Conecte** seu repositório GitHub
4. **Configure:**
   - **Name:** `sne-radar-web`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements_render.txt && pip install psycopg2-binary`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT sne_radar_web:app`

### 2. Criar Banco PostgreSQL

1. **No Dashboard Render:**
   - Clique em "New +" → "PostgreSQL"
   - **Name:** `sne-radar-db`
   - **Plan:** Free
   - **Database Name:** `sne_radar`
   - **User:** `sne_radar_user`

### 3. Configurar Variáveis de Ambiente

No seu Web Service, adicione as seguintes variáveis:

```bash
# Ambiente
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Banco de Dados (será preenchido automaticamente pelo Render)
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=sne_radar
DB_USER=sne_radar_user
DB_PASSWORD=your-db-password

# Feature Flags
ENABLE_COINGLASS=false
ENABLE_CMC=false
ENABLE_TA_SUMMARY=false

# Configurações
UPDATE_INTERVAL=30
REQUEST_TIMEOUT=12
BINANCE_CALLS_PER_WINDOW=10
BINANCE_WINDOW_SECONDS=60
```

## 🔍 Verificação do Deploy

### 1. Logs de Build

Verifique se o build foi bem-sucedido:
- Acesse o Web Service
- Vá em "Logs"
- Procure por "✅ Dependências instaladas"

### 2. Logs de Runtime

Verifique se a aplicação está rodando:
- Procure por "🚀 Iniciando SNE Radar..."
- Verifique se não há erros de conexão com banco

### 3. Teste da Aplicação

1. **Acesse** a URL fornecida pelo Render
2. **Verifique** se a página carrega
3. **Teste** os endpoints principais:
   - `/` - Página principal
   - `/api/v1/ta-summary` - Resumo de análise técnica
   - `/api/v1/global-metrics` - Métricas globais

## 🚨 Solução de Problemas

### Erro: "psycopg2 not found"

**Solução:**
```bash
# No build command, adicione:
pip install psycopg2-binary
```

### Erro: "Database connection failed"

**Solução:**
1. Verifique se o banco PostgreSQL foi criado
2. Verifique se as variáveis de ambiente estão corretas
3. Verifique se o banco está no mesmo projeto

### Erro: "Module not found"

**Solução:**
1. Verifique se todas as dependências estão no `requirements_render.txt`
2. Verifique se o build command está correto

### Erro: "Port binding failed"

**Solução:**
1. Use `gunicorn --bind 0.0.0.0:$PORT sne_radar_web:app`
2. Certifique-se de usar a variável `$PORT` do Render

## 📊 Monitoramento

### 1. Logs em Tempo Real

- Acesse o Web Service
- Vá em "Logs"
- Monitore erros e performance

### 2. Métricas

- **CPU Usage** - Deve estar abaixo de 80%
- **Memory Usage** - Deve estar abaixo de 512MB (plano free)
- **Response Time** - Deve estar abaixo de 2s

### 3. Health Check

Crie um endpoint de health check:

```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })
```

## 🔄 Atualizações

### 1. Deploy Automático

- Push para a branch `main` no GitHub
- O Render fará deploy automático

### 2. Deploy Manual

- No Dashboard Render
- Clique em "Manual Deploy"
- Selecione a branch/commit desejado

## 💡 Dicas de Otimização

### 1. Performance

- Use `gunicorn` com múltiplos workers
- Configure cache para APIs externas
- Use CDN para assets estáticos

### 2. Segurança

- Use HTTPS (automático no Render)
- Configure CORS adequadamente
- Use rate limiting

### 3. Monitoramento

- Configure alertas para erros
- Monitore uso de recursos
- Configure logs estruturados

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** no Render Dashboard
2. **Consulte a documentação** do Render
3. **Verifique** se todas as dependências estão corretas
4. **Teste localmente** se possível

---

**🎉 Com este guia, seu SNE Radar deve estar funcionando no Render!**




