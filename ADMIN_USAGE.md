# 📊 Funcionalidades Administrativas - SNE Radar

Este documento explica como usar as funcionalidades para consultar estatísticas de usuários no sistema SNE Radar.

## 🚀 Opções Disponíveis

### **Opção 1: Script Python (Recomendado para Consultas Rápidas)**

Execute o script `user_stats.py` para obter estatísticas detalhadas:

```bash
python user_stats.py
```

**Funcionalidades:**
- ✅ Contagem total de usuários
- ✅ Usuários ativos vs. inativos
- ✅ Distribuição por tier (free/pro/institutional)
- ✅ Análise de uso da API
- ✅ Exportação para CSV
- ✅ Detalhes individuais dos usuários

### **Opção 2: Dashboard Web Administrativo**

Acesse `/admin` no sistema web (apenas usuário admin):

```
http://localhost:9999/admin
```

**Credenciais padrão:**
- Username: `admin`
- Senha: `Admin123!`

**Funcionalidades:**
- ✅ Dashboard visual com estatísticas
- ✅ Lista de usuários com busca
- ✅ Gerenciamento de tiers
- ✅ Reset de contadores de API
- ✅ Estatísticas em tempo real

### **Opção 3: Consulta Direta no Banco SQLite**

Conecte diretamente ao banco para consultas personalizadas:

```bash
sqlite3 instance/sne_radar.db
```

**Consultas úteis:**

```sql
-- Total de usuários
SELECT COUNT(*) as total_usuarios FROM user;

-- Usuários por tier
SELECT tier, COUNT(*) as quantidade FROM user GROUP BY tier;

-- Usuários ativos (últimos 30 dias)
SELECT COUNT(*) as usuarios_ativos FROM user 
WHERE last_api_reset >= date('now', '-30 days');

-- Top usuários por uso de API
SELECT username, tier, api_calls_today, last_api_reset 
FROM user 
WHERE api_calls_today > 0 
ORDER BY api_calls_today DESC 
LIMIT 10;

-- Usuários com assinatura expirada
SELECT username, tier, subscription_expires 
FROM user 
WHERE subscription_expires < datetime('now') 
AND subscription_expires IS NOT NULL;
```

## 🔧 Configuração das Rotas Administrativas

Para ativar o dashboard web administrativo, adicione as rotas do arquivo `admin_routes.py` ao seu `sne_radar_web.py`:

```python
# Adicionar no início do arquivo, após os imports
from admin_routes import *

# Ou copiar as rotas diretamente para o arquivo principal
```

## 📈 Métricas Disponíveis

### **Estatísticas de Usuários:**
- **Total de usuários** cadastrados
- **Usuários ativos** (últimos 30 dias)
- **Usuários inativos** (mais de 30 dias)
- **Taxa de atividade** (percentual)
- **Distribuição por tier** (free/pro/institutional)

### **Análise de Uso:**
- **API calls por usuário** (diário)
- **Top usuários** por uso da API
- **Média de uso** por tier
- **Último acesso** de cada usuário

### **Estatísticas do Sistema:**
- **Total de alertas** gerados
- **Dados de mercado** coletados
- **Alertas por tipo**
- **Dados por símbolo**

## 🛡️ Segurança

- **Acesso restrito** apenas para usuário `admin`
- **Autenticação obrigatória** para todas as rotas admin
- **Validação de permissões** em todas as operações
- **Rate limiting** para prevenir abuso

## 📋 Exemplos de Uso

### **Verificar Crescimento de Usuários:**
```bash
# Executar script diariamente para acompanhar crescimento
python user_stats.py > user_growth_$(date +%Y%m%d).log
```

### **Identificar Usuários Inativos:**
```sql
SELECT username, last_api_reset, tier 
FROM user 
WHERE last_api_reset < date('now', '-60 days')
ORDER BY last_api_reset;
```

### **Analisar Conversão de Tiers:**
```sql
SELECT 
    tier,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM user), 2) as percentual
FROM user 
GROUP BY tier 
ORDER BY total DESC;
```

### **Monitorar Uso da API:**
```sql
SELECT 
    tier,
    AVG(api_calls_today) as media_calls,
    MAX(api_calls_today) as max_calls,
    COUNT(*) as usuarios
FROM user 
GROUP BY tier;
```

## 🔄 Atualizações Automáticas

O dashboard web atualiza automaticamente:
- **Estatísticas:** a cada carregamento da página
- **Lista de usuários:** em tempo real
- **Contadores:** via WebSocket (se implementado)

## 📊 Exportação de Dados

### **CSV via Script Python:**
```bash
python user_stats.py
# Responder 's' quando perguntado sobre exportação
```

### **JSON via API:**
```bash
# Estatísticas gerais
curl -H "Authorization: Bearer TOKEN" /api/admin/users/stats

# Lista de usuários
curl -H "Authorization: Bearer TOKEN" /api/admin/users/list
```

## 🚨 Troubleshooting

### **Erro de Conexão com Banco:**
```bash
# Verificar se o banco existe
ls -la instance/sne_radar.db

# Verificar permissões
chmod 644 instance/sne_radar.db
```

### **Erro de Acesso Negado:**
- Verificar se está logado como usuário `admin`
- Verificar se as rotas admin estão ativas
- Verificar se o template `admin_dashboard.html` existe

### **Dados Não Carregam:**
- Verificar logs do Flask
- Verificar se o banco tem dados
- Verificar se as tabelas existem

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs do sistema
2. Executar script Python para diagnóstico
3. Verificar conectividade com banco
4. Validar permissões de usuário

---

**⚠️ IMPORTANTE:** Sempre altere a senha padrão do admin após o primeiro login!

