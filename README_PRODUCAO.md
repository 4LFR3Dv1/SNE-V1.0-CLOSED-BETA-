# 🚀 SNE Radar - Script de Produção

Este script permite consultar estatísticas de usuários tanto no banco local quanto no banco de produção do Render.

## 📁 Arquivos Criados:

1. **`database_config.py`** - Configurações de conexão com bancos
2. **`user_stats_production.py`** - Script principal com suporte a produção
3. **`config_producao.txt`** - Exemplo de configuração das credenciais

## 🔧 Configuração para Banco de Produção:

### **Passo 1: Obter Credenciais do Render**

Para conectar ao banco de produção, você precisa das credenciais do PostgreSQL no Render:

1. Acesse o dashboard do Render
2. Vá para seu serviço de banco de dados
3. Copie as informações de conexão:
   - **Host**
   - **Porta** (geralmente 5432)
   - **Nome do banco**
   - **Usuário**
   - **Senha**

### **Passo 2: Configurar Variáveis de Ambiente**

Configure as credenciais no terminal:

```bash
export DB_HOST=seu_host_render.onrender.com
export DB_PORT=5432
export DB_NAME=seu_nome_database
export DB_USER=seu_usuario_database
export DB_PASSWORD=sua_senha_database
```

### **Passo 3: Verificar Configuração**

```bash
env | grep DB_
```

Deve mostrar algo como:
```
DB_HOST=db-abc123.onrender.com
DB_PORT=5432
DB_NAME=sne_radar_prod
DB_USER=admin_user
DB_PASSWORD=minha_senha
```

## 🚀 Como Usar:

### **Executar o Script:**

```bash
python3 user_stats_production.py
```

### **Opções Disponíveis:**

1. **Local (desenvolvimento)** - Conecta ao banco SQLite local
2. **Produção (Render)** - Conecta ao banco PostgreSQL remoto
3. **Sair** - Encerra o script

## 📊 Funcionalidades:

### **✅ Banco Local:**
- Conecta ao SQLite local
- Mostra usuários de desenvolvimento
- Funcionalidades completas de monetização

### **✅ Banco de Produção:**
- Conecta ao PostgreSQL do Render
- Mostra usuários reais de produção
- Dados em tempo real
- Exportação para CSV

## 🔍 Exemplo de Uso:

```bash
# Configurar credenciais
export DB_HOST=db-abc123.onrender.com
export DB_PORT=5432
export DB_NAME=sne_radar_prod
export DB_USER=admin_user
export DB_PASSWORD=minha_senha

# Executar script
python3 user_stats_production.py

# Escolher opção 2 (Produção)
# O script mostrará:
# - Estrutura do banco de produção
# - Total de usuários reais
# - Estatísticas por tier
# - Detalhes dos usuários
# - Opção de exportar para CSV
```

## 🛠️ Dependências:

```bash
# Instalar dependências necessárias
source venv/bin/activate
python3 -m pip install psycopg2-binary
```

## 📋 Estrutura do Banco de Produção:

O script detecta automaticamente a estrutura do banco e mostra:

- **Colunas disponíveis**
- **Colunas faltando** para monetização
- **Estatísticas** baseadas no que está disponível

## 🔒 Segurança:

- **Credenciais não são salvas** em arquivos
- **Variáveis de ambiente** são usadas temporariamente
- **Conexões são fechadas** automaticamente
- **Senhas não são exibidas** nos logs

## 🚨 Troubleshooting:

### **Erro: "Credenciais de produção não configuradas"**
```bash
# Verificar se as variáveis estão configuradas
env | grep DB_

# Configurar novamente se necessário
export DB_HOST=seu_host
export DB_PORT=5432
export DB_NAME=seu_database
export DB_USER=seu_usuario
export DB_PASSWORD=sua_senha
```

### **Erro: "Connection refused"**
- Verificar se o host e porta estão corretos
- Verificar se o banco está acessível externamente
- Verificar firewall/regras de acesso

### **Erro: "Authentication failed"**
- Verificar usuário e senha
- Verificar se o usuário tem permissões de leitura

## 📈 Vantagens:

1. **Dados Reais:** Acesso aos usuários reais de produção
2. **Flexibilidade:** Escolha entre local e produção
3. **Segurança:** Credenciais via variáveis de ambiente
4. **Exportação:** Dados exportados para CSV
5. **Detecção Automática:** Estrutura do banco detectada automaticamente

## 🎯 Próximos Passos:

1. **Obter credenciais** do banco no Render
2. **Configurar variáveis** de ambiente
3. **Testar conexão** com o script
4. **Consultar dados** reais de produção
5. **Exportar estatísticas** para análise

---

**⚠️ IMPORTANTE:** Nunca compartilhe ou commite suas credenciais de produção!

