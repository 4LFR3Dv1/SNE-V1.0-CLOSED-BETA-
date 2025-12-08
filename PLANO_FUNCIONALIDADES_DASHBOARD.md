# 📊 PLANO DE FUNCIONALIDADES DO DASHBOARD

**Data:** Janeiro 2025  
**Objetivo:** Adicionar funcionalidades avançadas ao dashboard web do SNE Radar

---

## 📋 ÍNDICE

1. [Análise do Estado Atual](#análise-do-estado-atual)
2. [Funcionalidades Existentes](#funcionalidades-existentes)
3. [Funcionalidades Planejadas](#funcionalidades-planejadas)
4. [Priorização](#priorização)
5. [Roadmap de Implementação](#roadmap-de-implementação)

---

## 🔍 ANÁLISE DO ESTADO ATUAL

### **Frontend Vue.js (Estrutura)**

#### **Páginas Existentes:**
- ✅ **Dashboard.vue** - Visão geral básica com oportunidades
- ✅ **Analysis.vue** - Análise técnica completa (funcional)
- ⚠️ **Backtesting.vue** - Placeholder (em desenvolvimento)
- ⚠️ **MagneticField.vue** - Placeholder (em desenvolvimento)
- ⚠️ **Settings.vue** - Placeholder (em desenvolvimento)

#### **Componentes Existentes:**
- ✅ **SimpleChart.vue** - Gráfico PNG estático (funcionando)
- ✅ **TradingChart.vue** - Gráfico interativo com Lightweight Charts
- ✅ **Header.vue** - Cabeçalho
- ✅ **Footer.vue** - Rodapé
- ✅ **LoadingSpinner.vue** - Indicador de carregamento

#### **Stores (Pinia):**
- ✅ **market.js** - Gerenciamento de dados de mercado
- ✅ **user.js** - Gerenciamento de usuário

#### **Serviços:**
- ✅ **api.js** - Cliente Axios configurado
- ✅ **websocket.js** - Cliente Socket.IO

---

### **Backend Flask (Endpoints Disponíveis)**

#### **APIs de Dados:**
- ✅ `GET /api/v1/ta-summary` - Resumo de análise técnica
- ✅ `GET /api/v1/global-metrics` - Métricas globais
- ✅ `GET /api/v1/derivatives` - Dados de derivativos (CoinGlass)
- ✅ `GET /api/v1/listings` - Listagens (CMC)
- ✅ `GET /api/v1/candles` - Dados de velas
- ✅ `GET /api/v1/chart-image` - Imagem PNG do gráfico

#### **Indicadores:**
- ✅ `GET /api/v1/advanced-indicators` - Indicadores avançados
- ✅ `GET /api/v1/professional-indicators` - Indicadores profissionais

#### **Machine Learning:**
- ✅ `POST /api/v1/ml/train` - Treinar modelos
- ✅ `GET /api/v1/ml/predict` - Predições
- ✅ `GET /api/v1/ml/performance` - Performance dos modelos

#### **Backtesting:**
- ✅ `POST /api/v1/backtest/run` - Executar backtest
- ✅ `POST /api/v1/backtest/optimize` - Otimizar parâmetros

#### **Alertas:**
- ✅ `GET /api/v1/alerts` - Listar alertas
- ✅ `POST /api/v1/alerts` - Criar alerta
- ✅ `DELETE /api/v1/alerts/<id>` - Deletar alerta
- ✅ `GET /api/v1/alerts/triggered` - Alertas disparados

#### **Exportação:**
- ✅ `POST /api/v1/export/market-data` - Exportar dados
- ✅ `POST /api/v1/export/candles` - Exportar velas
- ✅ `POST /api/v1/export/report` - Exportar relatório PDF

#### **Sistema:**
- ✅ `GET /api/v1/system/status` - Status do sistema
- ✅ `POST /api/v1/system/reset-circuit-breaker` - Reset circuit breaker

---

### **Funcionalidades Backend (Não Expostas na API)**

O backend tem muito código que não está integrado ao frontend:

#### **Análise Avançada:**
- ✅ Sistema de Zonas Magnéticas
- ✅ Análise Multi-Timeframe
- ✅ Análise de Contexto Global
- ✅ Detecção de Padrões Gráficos
- ✅ Análise de Estrutura de Mercado
- ✅ Sistema de Confluência (score 0-10)

#### **Trading:**
- ✅ Cálculo de Níveis Operacionais (Entry, SL, TP)
- ✅ Gestão de Risco
- ✅ Cálculo de R:R
- ✅ Múltiplas estratégias

#### **Integrações:**
- ✅ CoinGlass (Funding, OI, Liquidations)
- ✅ CoinMarketCap (Market Cap, Dominance)
- ✅ Binance (dados principais)

---

## 🎯 FUNCIONALIDADES PLANEJADAS

### **FASE 1: MELHORIAS BÁSICAS (Alta Prioridade)**

#### **1.1 Dashboard Principal Enriquecido**

**Objetivo:** Transformar o Dashboard.vue em um centro de controle rico

**Funcionalidades:**
- [ ] **Widgets Personalizáveis**
  - Grid de widgets arrastáveis (drag & drop)
  - Widgets disponíveis:
    - Preço BTC/ETH com gráfico mini
    - Top 5 Oportunidades (atual)
    - Alertas Ativos
    - Status do Sistema
    - Métricas Globais (Market Cap, Fear & Greed)
    - Últimos Sinais
  - Salvar layout personalizado no localStorage

- [ ] **Métricas em Tempo Real**
  - Cards com atualização automática a cada X segundos
  - Indicadores visuais (setas, cores)
  - Comparação com período anterior (24h, 7d)

- [ ] **Filtros e Busca**
  - Filtrar oportunidades por:
    - Score mínimo
    - Sinal (BUY/SELL)
    - Timeframe
    - Volume
  - Busca por símbolo

- [ ] **Links Rápidos**
  - Atalhos para análises frequentes
  - Histórico de análises recentes
  - Watchlists rápidas

**Tecnologias:**
- `vue-draggable` ou `@vueuse/core` para drag & drop
- WebSocket para atualizações em tempo real

---

#### **1.2 Sistema de Alertas Completo**

**Objetivo:** Interface completa para criar e gerenciar alertas

**Funcionalidades:**
- [ ] **Criar Alertas**
  - Tipos:
    - Preço (Above/Below)
    - RSI (Overbought/Oversold)
    - Volume (Spike)
    - Indicadores Técnicos
    - Padrões Gráficos
  - Formulário intuitivo
  - Preview da condição

- [ ] **Lista de Alertas**
  - Tabela com todos os alertas ativos
  - Status (Ativo/Disparado/Pausado)
  - Ações: Editar, Pausar, Deletar

- [ ] **Notificações**
  - Toast notifications quando alerta dispara
  - Badge com contador de alertas ativos
  - Som opcional (configurável)

- [ ] **Histórico de Alertas**
  - Alertas disparados recentemente
  - Log de eventos

**Interface:**
- Modal para criar/editar alerta
- Componente `AlertsList.vue`
- Componente `AlertForm.vue`

---

#### **1.3 Página de Settings Completa**

**Objetivo:** Configurar preferências do usuário e do sistema

**Funcionalidades:**
- [ ] **Perfil do Usuário**
  - Editar informações pessoais
  - Alterar senha
  - Foto de perfil

- [ ] **Preferências de Trading**
  - Par padrão (BTCUSDT, ETHUSDT, etc.)
  - Timeframe padrão
  - Risk per trade
  - R:R mínimo

- [ ] **Notificações**
  - Email notifications (ligar/desligar)
  - Som (ligar/desligar)
  - Frequência de atualização

- [ ] **Tema e Visual**
  - Tema escuro/claro (já tem terminal theme)
  - Tamanho da fonte
  - Densidade de informações

- [ ] **API Keys** (futuro)
  - Gerenciar chaves de API
  - Conectar exchanges

**Interface:**
- Tabs organizadas por categoria
- Salvar preferências no backend

---

### **FASE 2: ANÁLISES AVANÇADAS (Média Prioridade)**

#### **2.1 Comparação de Múltiplos Pares**

**Objetivo:** Comparar performance de múltiplos pares simultaneamente

**Funcionalidades:**
- [ ] **Tabela Comparativa**
  - Selecionar até 10 pares
  - Colunas:
    - Preço atual
    - Variação 24h
    - Volume 24h
    - Score de Confluência
    - Sinal
    - RSI
    - Multi-Timeframe
  - Ordenar por qualquer coluna
  - Filtrar por critérios

- [ ] **Gráficos Comparativos**
  - Overlay de múltiplos pares
  - Comparação de performance relativa
  - Heatmap de correlação

- [ ] **Análise Correlação**
  - Matriz de correlação
  - Gráfico de dispersão

**Componente:** `ComparisonTable.vue`

---

#### **2.2 Análise Multi-Timeframe Visual**

**Objetivo:** Visualizar todos os timeframes de um par simultaneamente

**Funcionalidades:**
- [ ] **Grid de Timeframes**
  - 5-6 timeframes simultâneos (1m, 5m, 15m, 1h, 4h, 1d)
  - Cada um com gráfico mini
  - Indicador visual de tendência (setas, cores)
  - Confluência MTF destacada

- [ ] **Sincronização**
  - Ao selecionar símbolo, atualiza todos os timeframes
  - Scroll sincronizado (opcional)

- [ ] **Resumo MTF**
  - Card com resumo da confluência
  - Direção dominante
  - Score combinado

**Componente:** `MultiTimeframeView.vue`

---

#### **2.3 Backtesting Completo**

**Objetivo:** Interface completa para backtesting de estratégias

**Funcionalidades:**
- [ ] **Configuração de Backtest**
  - Selecionar estratégia:
    - MA Crossover
    - RSI Strategy
    - Bollinger Bands
    - Personalizada
  - Parâmetros da estratégia (períodos, etc.)
  - Período histórico
  - Capital inicial
  - Risk per trade

- [ ] **Resultados Visuais**
  - Gráfico de equity curve
  - Gráfico de drawdown
  - Tabela de trades
  - Estatísticas:
    - Total de trades
    - Win rate
    - Profit factor
    - Sharpe ratio
    - Max drawdown

- [ ] **Otimização**
  - Grid search de parâmetros
  - Gráfico de heatmap (parâmetros vs performance)
  - Melhores configurações

**Componentes:**
- `BacktestConfig.vue`
- `BacktestResults.vue`
- `BacktestOptimizer.vue`

---

### **FASE 3: VISUALIZAÇÕES AVANÇADAS (Média-Baixa Prioridade)**

#### **3.1 Campo Magnético 3D**

**Objetivo:** Visualização 3D das zonas magnéticas

**Funcionalidades:**
- [ ] **Visualização 3D**
  - Gráfico 3D usando Three.js (já tem no package.json)
  - Zonas magnéticas como "forças gravitacionais"
  - Intensidade visual (cores, tamanhos)
  - Rotação e zoom

- [ ] **Interatividade**
  - Hover mostra informações da zona
  - Click para análise detalhada
  - Animações suaves

- [ ] **Controles**
  - Play/pause para animação temporal
  - Filtrar por força mínima
  - Mostrar/esconder zonas

**Componente:** `MagneticField3D.vue`  
**Biblioteca:** Three.js (já instalada)

---

#### **3.2 Análise de Volume Profile**

**Objetivo:** Visualizar perfil de volume e áreas de valor

**Funcionalidades:**
- [ ] **Volume Profile Chart**
  - Histograma lateral mostrando volume por preço
  - POC (Point of Control)
  - Value Area High/Low
  - Zonas de alta liquidez

- [ ] **Integração com Gráfico**
  - Overlay no gráfico principal
  - Destacar níveis importantes

**Componente:** `VolumeProfile.vue`

---

#### **3.3 Heatmaps**

**Objetivo:** Visualização de dados em formato heatmap

**Funcionalidades:**
- [ ] **Heatmap de Performance**
  - Múltiplos pares vs múltiplos timeframes
  - Cor indica score/sinal
  - Click para análise detalhada

- [ ] **Heatmap de Correlação**
  - Matriz de correlação entre pares
  - Cores indicam força da correlação

- [ ] **Heatmap de Volume**
  - Volume por par e timeframe
  - Identificar oportunidades líquidas

**Componente:** `Heatmap.vue`

---

### **FASE 4: GESTÃO E HISTÓRICO (Baixa Prioridade)**

#### **4.1 Histórico de Sinais**

**Objetivo:** Registrar e acompanhar performance dos sinais

**Funcionalidades:**
- [ ] **Registro de Sinais**
  - Salvar cada sinal gerado
  - Timestamp, símbolo, timeframe, score
  - Link para análise completa

- [ ] **Performance Tracking**
  - Estatísticas de acerto dos sinais
  - Win rate por tipo de sinal
  - ROI estimado

- [ ] **Filtros e Busca**
  - Filtrar por período
  - Filtrar por símbolo/timeframe
  - Busca textual

**Componente:** `SignalsHistory.vue`

---

#### **4.2 Watchlists**

**Objetivo:** Criar listas de pares para monitoramento

**Funcionalidades:**
- [ ] **Criar Watchlists**
  - Múltiplas watchlists (ex: "DeFi", "Layer 1", "Meme Coins")
  - Adicionar/remover pares
  - Ordenar por qualquer critério

- [ ] **Monitoramento**
  - Dashboard dedicado por watchlist
  - Alertas específicos por watchlist
  - Notificações de mudanças

- [ ] **Compartilhamento** (futuro)
  - Compartilhar watchlists com outros usuários
  - Watchlists públicas

**Componentes:**
- `WatchlistManager.vue`
- `WatchlistDashboard.vue`

---

#### **4.3 Relatórios e Exportação**

**Objetivo:** Gerar e exportar relatórios personalizados

**Funcionalidades:**
- [ ] **Relatórios Personalizados**
  - Selecionar dados a incluir
  - Período
  - Formato (PDF, CSV, JSON)
  - Agendar relatórios automáticos

- [ ] **Templates de Relatórios**
  - Relatório diário
  - Relatório semanal
  - Relatório de performance

- [ ] **Exportação de Gráficos**
  - Exportar gráfico como PNG/SVG
  - Exportar dados de análise como CSV
  - Exportar backtest completo

**Componente:** `Reports.vue`

---

#### **4.4 Histórico de Trades Simulado**

**Objetivo:** Simular e acompanhar trades baseados nos sinais

**Funcionalidades:**
- [ ] **Registrar Trade Simulado**
  - Ao clicar em "Abrir Trade" em um sinal
  - Capturar: Entry, SL, TP, quantidade
  - Timestamp automático

- [ ] **Gerenciar Trades**
  - Lista de trades abertos
  - Atualizar preço atual
  - Fechar trade (manual ou automático)
  - P&L em tempo real

- [ ] **Estatísticas**
  - Performance geral
  - Best/worst trades
  - Gráfico de equity
  - Win rate

**Componentes:**
- `TradeSimulator.vue`
- `TradesList.vue`
- `TradeStats.vue`

---

### **FASE 5: RECURSOS AVANÇADOS (Futuro)**

#### **5.1 Machine Learning Predictions**

**Objetivo:** Exibir predições de ML no dashboard

**Funcionalidades:**
- [ ] **Predições de Preço**
  - Gráfico com previsão (linha futura)
  - Intervalo de confiança
  - Múltiplos modelos (Random Forest, GB, Ensemble)

- [ ] **Score de Confiança**
  - Indicador visual de confiança do modelo
  - Avisos quando confiança é baixa

**Integração:** Já existe endpoint `/api/v1/ml/predict`

---

#### **5.2 Social Trading**

**Objetivo:** Compartilhar e acompanhar trades de outros usuários

**Funcionalidades:**
- [ ] **Feed de Trades**
  - Ver trades públicos de outros usuários
  - Follow de traders
  - Copiar trades

- [ ] **Ranking**
  - Leaderboard por performance
  - Melhores traders do mês

**Complexidade:** Alta - requer sistema de usuários completo

---

#### **5.3 Alertas Avançados (Telegram/Email)**

**Objetivo:** Notificações externas

**Funcionalidades:**
- [ ] **Integração Telegram**
  - Bot do Telegram (já existe backend)
  - Receber alertas no Telegram
  - Comandos via bot

- [ ] **Notificações Email**
  - Alertas por email
  - Relatórios diários/semanais

**Integração:** Backend já tem estrutura de Telegram

---

## 🎯 PRIORIZAÇÃO

### **Alta Prioridade (Fase 1)**
1. ✅ **Sistema de Alertas Completo** - Funcionalidade core faltando
2. ✅ **Dashboard Enriquecido** - Melhora experiência principal
3. ✅ **Settings Completa** - Necessário para personalização

**Estimativa:** 2-3 semanas

---

### **Média Prioridade (Fase 2)**
4. ✅ **Comparação Múltiplos Pares** - Muito útil para traders
5. ✅ **Multi-Timeframe Visual** - Visualização importante
6. ✅ **Backtesting Completo** - Backend já tem, só falta frontend

**Estimativa:** 3-4 semanas

---

### **Média-Baixa Prioridade (Fase 3)**
7. ✅ **Campo Magnético 3D** - Visual impressionante, mas menos essencial
8. ✅ **Volume Profile** - Útil para análise avançada
9. ✅ **Heatmaps** - Visualização alternativa interessante

**Estimativa:** 2-3 semanas

---

### **Baixa Prioridade (Fase 4)**
10. ✅ **Histórico de Sinais** - Útil para aprendizado
11. ✅ **Watchlists** - Organização pessoal
12. ✅ **Relatórios** - Exportação já existe, só melhorar UI
13. ✅ **Trade Simulator** - Interessante para prática

**Estimativa:** 3-4 semanas

---

### **Futuro (Fase 5)**
14. ✅ **ML Predictions** - Backend já tem
15. ✅ **Social Trading** - Complexo, requer muita infraestrutura
16. ✅ **Alertas Externos** - Backend já tem Telegram

**Estimativa:** Depende de outras prioridades

---

## 📅 ROADMAP DE IMPLEMENTAÇÃO

### **Sprint 1 (Semana 1-2): Dashboard Enriquecido**
- Widgets personalizáveis
- Métricas em tempo real
- Filtros e busca

### **Sprint 2 (Semana 2-3): Sistema de Alertas**
- Criar/editar/deletar alertas
- Notificações em tempo real
- Histórico de alertas

### **Sprint 3 (Semana 3-4): Settings Completa**
- Perfil do usuário
- Preferências de trading
- Configurações de notificações

### **Sprint 4 (Semana 4-5): Comparação Multi-Par**
- Tabela comparativa
- Gráficos overlay
- Análise de correlação

### **Sprint 5 (Semana 5-6): Multi-Timeframe Visual**
- Grid de timeframes
- Sincronização
- Resumo MTF

### **Sprint 6 (Semana 6-8): Backtesting Completo**
- Configuração de backtest
- Visualização de resultados
- Otimização de parâmetros

---

## 🛠️ TECNOLOGIAS NECESSÁRIAS

### **Bibliotecas Novas (a adicionar):**
- `vue-draggable` ou `@vueuse/core` - Drag & drop
- `vue-toastification` - Notificações toast
- `date-fns` - Manipulação de datas
- `recharts` ou `chart.js` - Gráficos adicionais (se necessário)
- `vue-pdf` - Visualizar PDFs (relatórios)

### **Bibliotecas Já Instaladas:**
- ✅ `three.js` - Para visualização 3D
- ✅ `lightweight-charts` - Para gráficos de trading
- ✅ `axios` - Para requisições HTTP
- ✅ `socket.io-client` - Para WebSocket

---

## 📝 NOTAS DE IMPLEMENTAÇÃO

### **Padrões a Seguir:**
1. **Componentes Reutilizáveis**
   - Criar componentes pequenos e focados
   - Props bem definidas
   - Emits claros

2. **Store (Pinia)**
   - Centralizar estado compartilhado
   - Ações assíncronas nos stores
   - Getters para computed values

3. **API Service**
   - Manter `api.js` organizado
   - Tipos de retorno claros
   - Tratamento de erros consistente

4. **Responsividade**
   - Mobile-first onde possível
   - Grid system flexível
   - Breakpoints bem definidos

5. **Performance**
   - Lazy loading de componentes pesados
   - Debounce em filtros/buscas
   - Cache de dados quando apropriado

---

## ✅ CHECKLIST DE QUALIDADE

Antes de considerar uma funcionalidade "completa":

- [ ] Componente funcional
- [ ] Responsivo (mobile + desktop)
- [ ] Loading states
- [ ] Error handling
- [ ] Testes básicos (manuais)
- [ ] Documentação inline
- [ ] Integração com API backend
- [ ] Persistência de dados (quando necessário)
- [ ] Validação de inputs

---

**Documento criado:** Janeiro 2025  
**Status:** ✅ Planejamento completo - Pronto para implementação

---

## 🚀 PRÓXIMOS PASSOS

1. **Revisar e aprovar plano** com o usuário
2. **Priorizar funcionalidades** específicas
3. **Começar implementação** pela Fase 1
4. **Criar issues/tasks** para cada funcionalidade
5. **Testar incrementalmente** após cada sprint

