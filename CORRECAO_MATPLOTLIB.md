# 🔧 CORREÇÃO: Módulo matplotlib não encontrado

## 🐛 PROBLEMA

```
Error: No module named 'matplotlib'
```

O módulo `matplotlib` não está instalado no ambiente Python onde o Flask está rodando.

---

## ✅ SOLUÇÃO

### **Opção 1: Instalar Dependências (Recomendado)**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Se tiver venv, ativar primeiro
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install matplotlib mplfinance
# ou instalar tudo do requirements.txt
pip install -r requirements.txt
```

### **Opção 2: Verificar Ambiente Virtual**

```bash
# Verificar se venv existe
ls -la venv/

# Se não existir, criar
python3 -m venv venv

# Ativar
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

---

## 🧪 VERIFICAR INSTALAÇÃO

```bash
# Testar se matplotlib está instalado
python3 -c "import matplotlib; print('✅ matplotlib OK')"
python3 -c "import mplfinance; print('✅ mplfinance OK')"
```

---

## 📋 DEPENDÊNCIAS NECESSÁRIAS

Para o gráfico funcionar, você precisa de:

```
matplotlib>=3.8.0
mplfinance>=0.12.10b0
numpy>=1.26.0
pandas>=2.2.0
```

---

## 🚀 INSTALAÇÃO RÁPIDA

```bash
# No diretório do projeto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Instalar matplotlib e mplfinance (mínimo necessário)
pip install matplotlib mplfinance

# Ou instalar todas as dependências
pip install -r requirements.txt
```

---

**Depois de instalar, reiniciar o Flask!**

