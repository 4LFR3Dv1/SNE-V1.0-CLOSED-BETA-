# ⚡ QUICK START - MODO RENAN ULTRA

## 🚀 INÍCIO RÁPIDO (3 PASSOS)

### **1. Iniciar Sistema**
```bash
python3 main.py
```

### **2. Escolher Modo Renan Ultra**
```
Comando >> R
```

### **3. Selecionar Par**
```
Digite o símbolo (ou Enter para BTC): 
```

**Pronto! Sistema analisa em 9 camadas e gera setup completo.** ✅

---

## 📊 O QUE ACONTECE (9 CAMADAS)

1. ✅ Busca dados (500 candles 15m)
2. ✅ Detecta regime (BULL/BEAR/CONSOLIDATION)
3. ✅ Gera sinal básico (EMA)
4. ✅ **Ajusta pesos por contexto** ⭐
5. ✅ **Valida multi-critério** ⭐
6. ✅ **Analisa fluxo DOM** ⭐
7. ✅ **Consulta memória (aprende)** ⭐
8. ✅ **Aplica teoria magnética** ⭐
9. ✅ **Calcula risco/posição** ⭐

---

## 💡 EXEMPLO DE SAÍDA

```
✅ SETUP PROFISSIONAL VALIDADO - COMPRAR BTCUSDT

💰 POSIÇÃO:
   Quantidade: 0.200000
   Risco: $60 (1%)

📍 NÍVEIS:
   Entry: $100,500
   TP: $101,000
   SL: $100,200
   R/R: 1:1.7

📊 ANÁLISE:
   Confiança: 61%
   Expectativa: +$40.80
   Qualidade: POSITIVA

🧠 INTELIGÊNCIA:
   • Histórico: 68% de acerto
   • Fluxo: Pressão de COMPRA (78%)
   • Zona magnética: $101k
   • Regime: BULL_TREND confirma
```

---

## 🎓 APRENDIZAGEM AUTOMÁTICA

### **Registrar Resultado do Trade:**

```python
from memoria_operacional import MemoriaOperacional

memoria = MemoriaOperacional()

# Se atingiu TP ✅
memoria.fechar_sinal(sinal_id=1, hit_tp=True)

# Se atingiu SL ❌
memoria.fechar_sinal(sinal_id=1, hit_sl=True)
```

### **Ver Estatísticas:**

```python
print(memoria.gerar_relatorio())
```

**Sistema aprende e ajusta automaticamente!** 🧠

---

## 🔧 CONFIGURAÇÕES (OPCIONAL)

### **Ajustar Capital e Risco:**

Edite `main.py` linha 786:

```python
gestao_risco = GestaoRisco(
    capital_total=10000,    # Seu capital
    risk_per_trade=1.0,     # % de risco por trade
    rr_minimo=1.8           # R/R mínimo aceito
)
```

### **Ajustar Pesos Adaptativos:**

Edite `contexto_adaptativo.py` linha 43+:

```python
if regime == 'BULL_TREND':
    pesos['EMA'] = 0.40     # Aumentar/diminuir
    pesos['RSI'] = 0.15
    # ...
```

---

## 📁 ARQUIVOS IMPORTANTES

- `main.py` - Sistema principal (opção R)
- `memoria_sneer.json` - Banco de aprendizagem
- `catalogo_magnetico.csv` - Zonas magnéticas

---

## 🧪 TESTAR MÓDULOS

```bash
# Teste contexto adaptativo
python3 contexto_adaptativo.py

# Teste memória
python3 memoria_operacional.py

# Teste gestão de risco
python3 gestao_risco.py

# Teste fluxo
python3 fluxo_ativo.py

# Teste consistência
python3 consistencia_sinal.py

# Teste modo Renan
python3 modo_renan.py
```

---

## 🆘 TROUBLESHOOTING

### **Erro: Module not found**
```bash
pip install pandas numpy requests
```

### **Erro: No zonas magnéticas**
- Normal na primeira execução
- Sistema cria conforme detecta rupturas

### **Confiança muito baixa**
- Sistema está aprendendo
- Após 50+ sinais, melhora automaticamente

---

## 🎯 WORKFLOW RECOMENDADO

### **Dia 1-7:**
1. Usar Modo Renan Ultra (opção R)
2. Executar 10-20 sinais
3. Registrar resultados (TP/SL)

### **Dia 8-14:**
1. Continuar operando
2. Ver `memoria.gerar_relatorio()`
3. Sistema já aprendeu padrões

### **Dia 15+:**
1. Sistema totalmente calibrado
2. Confiança ajustada por experiência
3. Pesos adaptativos otimizados

---

## ✅ CHECKLIST DE USO

- [ ] Sistema instalado (`python3 main.py` funciona)
- [ ] Opção R disponível no menu
- [ ] Primeiro sinal gerado com sucesso
- [ ] Resultado registrado na memória
- [ ] `memoria_sneer.json` criado
- [ ] Relatório funcionando

---

## 🚀 COMANDO ÚNICO (COPY-PASTE)

```bash
python3 main.py
# Depois digite: R
# Depois digite: Enter (para BTC)
```

**É só isso!** Sistema faz o resto. 🎯

---

**Modo Renan Ultra v1.0**  
**Status: 🟢 OPERACIONAL**  
**Pronto para uso!** ✅





