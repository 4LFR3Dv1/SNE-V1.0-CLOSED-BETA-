# 🤖 BOT TELEGRAM SNE RADAR - GUIA COMPLETO

## 📋 **VISÃO GERAL**

O bot do Telegram SNE Radar agora suporta **duas modalidades**:
1. **Modo Polling** - Para desenvolvimento e testes
2. **Modo Webhook** - Para produção

## 🚀 **MODALIDADES DISPONÍVEIS**

### **1. MODO POLLING (Desenvolvimento)**
- ✅ **Funciona localmente** sem servidor
- ✅ **Ideal para testes** e desenvolvimento
- ✅ **Fácil de configurar** e usar
- ⚠️ **Limitação:** Precisa estar sempre rodando

### **2. MODO WEBHOOK (Produção)**
- ✅ **Funciona em servidor** remoto
- ✅ **Mais eficiente** para produção
- ✅ **Escalável** e profissional
- ⚠️ **Requer:** Servidor com URL pública

## 🔧 **COMO USAR**

### **OPÇÃO 1: MODO POLLING (Recomendado para testes)**

```bash
# Executar bot em modo polling
python3 teste_bot_polling.py
```

**O que acontece:**
- Bot inicia e fica aguardando mensagens
- Recebe comandos do Telegram automaticamente
- Processa e responde em tempo real
- **Pressione Ctrl+C para parar**

### **OPÇÃO 2: MODO WEBHOOK (Para produção)**

```bash
# 1. Iniciar servidor webhook
python3 servidor_webhook.py

# 2. Em outro terminal, configurar webhook
python3 configurar_webhook.py
```

**O que acontece:**
- Servidor Flask fica rodando na porta 5000
- Webhook configurado no Telegram
- Mensagens chegam via HTTP POST
- **Mais eficiente para produção**

## 📱 **COMANDOS DISPONÍVEIS**

### **COMANDOS BÁSICOS:**
- `/start` - Iniciar bot e ver boas-vindas
- `/ajuda` - Lista completa de comandos
- `/demo` - Análise demo gratuita (limitada)
- `/planos` - Ver planos premium disponíveis

### **COMANDOS PREMIUM:**
- `/analise` - Análise técnica completa
- `/relatorio` - Relatórios técnicos automáticos
- `/status` - Status da conta do usuário
- `/upgrade` - Upgrade de plano

## 🎯 **EXEMPLOS DE USO**

### **Teste Básico:**
```
Usuário: /start
Bot: 🚀 Bem-vindo ao SNE Radar!...

Usuário: /demo
Bot: 📊 ANÁLISE DEMO - BTCUSDT...

Usuário: /ajuda
Bot: 📋 COMANDOS DISPONÍVEIS...
```

### **Teste Premium:**
```
Usuário: /analise
Bot: 📊 ANÁLISE COMPLETA - BTCUSDT (1h)...

Usuário: /relatorio
Bot: 📊 RELATÓRIO TÉCNICO - MERCADO ATUAL...
```

## ⚙️ **CONFIGURAÇÃO**

### **Variáveis de Ambiente:**
```bash
# .env
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

### **Configuração Automática:**
- ✅ **Token detectado** automaticamente
- ✅ **Chat ID configurado** automaticamente
- ✅ **Fallback** para valores padrão

## 🔄 **INTEGRAÇÃO COM SISTEMA EXISTENTE**

### **No Terminal (main.py):**
```bash
# Comandos do bot funcionam no terminal também
Comando >> /start
Comando >> /demo
Comando >> /ajuda
```

### **No Telegram:**
- Bot responde automaticamente
- Comandos processados em tempo real
- Respostas formatadas para Telegram

## 📊 **MONITORAMENTO**

### **Logs do Bot:**
```
🤖 Iniciando SNE Bot (Modo Polling)...
✅ SNE Bot iniciado com sucesso! (Modo Polling)
🔄 Aguardando mensagens...
🔧 Processando comando: /start de 123456789
✅ Mensagem enviada para 123456789
```

### **Status do Webhook:**
```
📊 INFORMAÇÕES DO WEBHOOK:
🔹 URL: https://seu-dominio.com/webhook
🔹 Certificado: False
🔹 Updates pendentes: 0
🔹 IP permitidos: []
```

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Erro: "No module named 'requests'"**
```bash
python3 -m pip install --break-system-packages requests
```

### **Erro: "No module named 'flask'"**
```bash
python3 -m pip install --break-system-packages flask
```

### **Bot não responde:**
1. Verificar se está rodando
2. Verificar token do Telegram
3. Verificar conexão com internet

### **Webhook não funciona:**
1. Verificar se servidor está rodando
2. Verificar URL do webhook
3. Verificar se URL é acessível publicamente

## 🎯 **PRÓXIMOS PASSOS**

### **Para Desenvolvimento:**
1. ✅ **Bot funcionando** em modo polling
2. ✅ **Comandos implementados** e testados
3. ✅ **Integração** com sistema existente

### **Para Produção:**
1. 🔄 **Configurar servidor** com URL pública
2. 🔄 **Configurar webhook** no Telegram
3. 🔄 **Implementar sistema** de pagamento
4. 🔄 **Adicionar mais funcionalidades**

## 💡 **DICAS IMPORTANTES**

- **Modo Polling:** Ideal para testes e desenvolvimento
- **Modo Webhook:** Ideal para produção e escalabilidade
- **Comandos:** Funcionam tanto no terminal quanto no Telegram
- **Integração:** Sistema totalmente integrado com SNE Radar
- **Segurança:** Token e configurações protegidas

## 🎉 **RESULTADO FINAL**

✅ **Bot funcionando** em modo polling
✅ **Comandos implementados** e testados
✅ **Integração completa** com sistema existente
✅ **Pronto para produção** com webhook
✅ **Documentação completa** criada

**O bot agora responde aos comandos `/start`, `/demo`, `/ajuda`, etc. tanto no terminal quanto no Telegram!** 🚀
