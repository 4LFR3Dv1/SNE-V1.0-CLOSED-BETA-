# 📊 GUIA DE VISUALIZAÇÃO GRÁFICA - SNE RADAR

## 🎨 SISTEMA DE RELATÓRIOS VISUAIS

O sistema agora gera **relatórios gráficos profissionais** a partir das análises técnicas!

---

## 🚀 FUNCIONALIDADES

### **1. Relatório Visual Completo (Motor Renan)**

Transforma a análise do Motor Renan em um dashboard visual com 8 gráficos:

#### **Componentes:**
1. **📊 Confluência por Camada** - Barras horizontais mostrando contribuição de cada camada
2. **🎯 Gauge de Score** - Velocímetro semicircular (0-10) com zonas coloridas
3. **⏰ Multi-Timeframe** - Barras coloridas por tendência (verde/vermelho/cinza)
4. **📈 Estrutura de Mercado** - Círculo com emoji e tendência
5. **🌊 Fluxo DOM** - Barra de pressão com ratio
6. **📊 Indicadores** - Barras com EMA8, EMA21, RSI
7. **🌍 Contexto** - Pizza chart com regime e força
8. **✨ Síntese** - Box de texto com recomendações

---

### **2. Comparação de Pares**

Gráfico duplo comparando múltiplos pares:

- **Ranking por Score** - Barras horizontais coloridas por nível
- **Distribuição de Viés** - Pizza chart mostrando proporção Bull/Bear

---

### **3. Heatmap de Correlações**

Matriz visual de correlações entre pares:

- Cores: Verde (positivo) → Amarelo (neutro) → Vermelho (negativo)
- Valores numéricos em cada célula
- Fácil identificação de pares correlacionados

---

## 💻 COMO USAR

### **Opção 1: Via Código Python**

```python
from visualizacao_graficos import VisualizadorGrafico
from motor_renan import analise_completa

# Gerar análise
resultado = analise_completa("BTCUSDT", "1h")

# Gerar gráfico
viz = VisualizadorGrafico()
arquivo = viz.gerar_relatorio_completo(resultado, "BTCUSDT", "1h")

print(f"Gráfico salvo em: {arquivo}")
```

---

### **Opção 2: Integração no Terminal (PRÓXIMO PASSO)**

Adicionar ao `main.py`:

```python
# No comando R (Motor Renan)
if comando == "R":
    # ... análise existente ...
    
    # Perguntar se quer gráfico
    grafico = input("\n📊 Gerar relatório gráfico? (s/n): ").lower().strip()
    if grafico == 's':
        from visualizacao_graficos import VisualizadorGrafico
        viz = VisualizadorGrafico()
        arquivo = viz.gerar_relatorio_completo(resultado, symbol_r, tf_r)
        print(f"✅ Gráfico salvo: {arquivo}")
        
        # Enviar para Telegram (opcional)
        enviar_img = input("📤 Enviar gráfico para Telegram? (s/n): ").lower()
        if enviar_img == 's':
            # Código para enviar imagem
            pass
```

---

### **Opção 3: Multi-Pair e Heatmap**

```python
from visualizacao_graficos import gerar_grafico_comparacao_pares, gerar_heatmap_visual
from multi_pair_analise import analise_multi_pair
from heatmap_correlacoes import gerar_heatmap_correlacoes

# Comparação de pares
resultado_mult = analise_multi_pair()
arquivo1 = gerar_grafico_comparacao_pares(resultado_mult)

# Heatmap
resultado_heat = gerar_heatmap_correlacoes()
arquivo2 = gerar_heatmap_visual(resultado_heat)
```

---

## 📁 ESTRUTURA DE SAÍDA

```
reports/graficos/
├── BTCUSDT_1h_20241014_1430.png          # Relatório completo
├── comparacao_pares_20241014_1430.png    # Comparação
└── heatmap_20241014_1430.png             # Heatmap
```

---

## 🎨 PERSONALIZAÇÃO

### **Cores do Tema (Dark Mode):**
- Background: `#0a0a0a`
- Primário: `#00D9FF` (azul cyan)
- Sucesso: `#00FF00` (verde)
- Alerta: `#FFA500` (laranja)
- Erro: `#FF0000` (vermelho)
- Texto: `#FFFFFF` (branco)

### **Modificar Estilo:**

```python
viz = VisualizadorGrafico()
viz.style = 'seaborn'  # ou 'ggplot', 'bmh', etc.
viz.figsize = (20, 12)  # Tamanho maior
```

---

## 📊 TIPOS DE GRÁFICOS DISPONÍVEIS

### **1. Barras Horizontais**
- Confluência por camada
- Ranking de pares
- Usado para: Comparações, rankings

### **2. Gauge (Velocímetro)**
- Score de confiança
- Zonas coloridas (0-3.3 vermelho, 3.3-6.6 laranja, 6.6-10 verde)
- Usado para: Indicadores únicos

### **3. Barras Verticais**
- Indicadores técnicos
- Multi-timeframe
- Usado para: Múltiplos valores

### **4. Pizza Chart**
- Contexto (regime + força)
- Distribuição de viés
- Usado para: Proporções

### **5. Heatmap**
- Matriz de correlações
- Escala de cores -1 a +1
- Usado para: Relações entre variáveis

### **6. Texto Formatado**
- Síntese e recomendações
- Box com background
- Usado para: Informações textuais

---

## 🔧 INTEGRAÇÃO COM TELEGRAM

### **Enviar Imagem para Telegram:**

```python
def enviar_imagem_telegram(arquivo_imagem, caption=""):
    import requests
    
    TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    with open(arquivo_imagem, 'rb') as photo:
        files = {'photo': photo}
        params = {
            'chat_id': CHAT_ID,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(TELEGRAM_URL, params=params, files=files)
        
        if response.status_code == 200:
            print("✅ Imagem enviada para Telegram!")
            return True
        else:
            print(f"❌ Erro: {response.text}")
            return False
```

---

## 🎯 CASOS DE USO

### **1. Análise Completa com Gráfico**
```bash
Comando >> R
Par: BTC
Timeframe: 4h
→ Análise textual exibida
→ Gerar gráfico? s
→ ✅ Gráfico salvo!
→ Enviar para Telegram? s
→ ✅ Enviado!
```

### **2. Comparação Visual de Pares**
```bash
Comando >> MULT
Timeframe: 1h
→ Ranking textual
→ Gerar gráfico? s
→ ✅ Comparação visual salva!
```

### **3. Heatmap de Correlações**
```bash
Comando >> HEAT
→ Matriz textual
→ Gerar heatmap visual? s
→ ✅ Heatmap salvo!
```

---

## 📈 EXEMPLOS DE APLICAÇÃO

### **Trading:**
- **Relatório completo** antes de entrar em operação
- **Comparação de pares** para escolher melhor setup
- **Heatmap** para evitar pares correlacionados

### **Análise:**
- **Gauge de score** para decisão rápida
- **Multi-timeframe visual** para confluência
- **Estrutura gráfica** para identificar tendência

### **Compartilhamento:**
- **Gráficos para Telegram** - Relatórios visuais para grupo
- **PDFs profissionais** - Converter PNG para PDF
- **Relatórios automáticos** - Gerar a cada X horas

---

## 🚀 PRÓXIMOS PASSOS - IMPLEMENTAÇÃO

### **1. Adicionar ao main.py**

```python
# Adicionar no início do arquivo
from visualizacao_graficos import (
    VisualizadorGrafico, 
    gerar_grafico_comparacao_pares,
    gerar_heatmap_visual
)

# Modificar comando R
elif comando == "R":
    # ... código existente ...
    
    # Nova opção de gráfico
    if 'erro' not in resultado:
        grafico = input("\n📊 Gerar relatório gráfico? (s/n): ").lower()
        if grafico == 's':
            viz = VisualizadorGrafico()
            arquivo = viz.gerar_relatorio_completo(resultado, symbol_r, tf_r)
            print(f"\n✅ Gráfico salvo: {arquivo}")

# Modificar comando MULT
elif comando == "MULT":
    # ... código existente ...
    
    grafico = input("\n📊 Gerar gráfico comparativo? (s/n): ").lower()
    if grafico == 's':
        arquivo = gerar_grafico_comparacao_pares(resultado)
        print(f"\n✅ Gráfico salvo: {arquivo}")

# Modificar comando HEAT
elif comando == "HEAT":
    # ... código existente ...
    
    visual = input("\n📊 Gerar heatmap visual? (s/n): ").lower()
    if visual == 's':
        arquivo = gerar_heatmap_visual(resultado)
        print(f"\n✅ Heatmap salvo: {arquivo}")
```

---

### **2. Criar Novo Comando GRAF**

```python
elif comando == "GRAF":
    print("\n📊 GERADOR DE GRÁFICOS")
    print("="*60)
    print("\n1) Relatório Completo (Motor Renan)")
    print("2) Comparação de Pares")
    print("3) Heatmap de Correlações")
    print("4) Todos")
    
    opcao = input("\nEscolha: ")
    
    if opcao == "1":
        # Motor Renan + Gráfico
        pass
    elif opcao == "2":
        # Multi-pair + Gráfico
        pass
    # etc...
```

---

## 📚 DEPENDÊNCIAS

```bash
pip install matplotlib numpy pandas
```

Já incluídas no `requirements.txt`

---

## ✅ VANTAGENS DO SISTEMA VISUAL

### **1. Comunicação:**
- ✅ Gráficos são mais fáceis de entender
- ✅ Compartilháveis (Telegram, email)
- ✅ Profissionais para relatórios

### **2. Análise:**
- ✅ Identificação rápida de padrões
- ✅ Comparação visual eficiente
- ✅ Decisões mais rápidas

### **3. Documentação:**
- ✅ Histórico visual de análises
- ✅ Revisão de setups anteriores
- ✅ Aprendizado com histórico

---

## 🎯 RESUMO

**O sistema agora pode gerar:**

1. ✅ Relatórios visuais completos (8 gráficos)
2. ✅ Comparação de pares (ranking + distribuição)
3. ✅ Heatmap de correlações (matriz visual)
4. ✅ Exportação PNG (alta qualidade)
5. ✅ Integração Telegram (envio de imagens)

**Pronto para integrar ao terminal e começar a usar! 📊🚀**




