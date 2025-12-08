# 🔧 RESOLVER ERRO DO HOMEBREW

O Homebrew teve um erro ao instalar Node.js. Vamos resolver.

## 🔍 Diagnóstico

O erro foi:
```
FormulaUnavailableError: No available formula with the name "formula.jws.json".
```

Isso geralmente acontece quando:
- Homebrew está desatualizado
- Cache corrompido
- Problema de rede

## ✅ Solução 1: Tentar Corrigir Homebrew

```bash
# Atualizar Homebrew
brew update

# Limpar cache
brew cleanup

# Tentar instalar novamente
brew install node
```

## ✅ Solução 2: Usar Instalador Oficial (RECOMENDADO - Mais Rápido)

Se o Homebrew continuar dando erro, use o instalador oficial:

### 1. Baixar Node.js

Acesse: **https://nodejs.org/**

Baixe a versão **LTS** (v20.x ou v22.x) - arquivo `.pkg`

### 2. Instalar

- Abra o arquivo `.pkg`
- Siga o assistente (Next → Next → Install)
- Aguarde ~2 minutos

### 3. Verificar

**IMPORTANTE:** Feche o terminal atual e abra um NOVO terminal:

```bash
node --version
npm --version
```

### 4. Instalar Dependências

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm install
```

## 🎯 Por que Instalador Oficial é Melhor?

- ✅ **Mais rápido:** 2-3 minutos vs 30+ minutos
- ✅ **Mais confiável:** Não compila do código fonte
- ✅ **Menos problemas:** Não depende de dependências do Homebrew
- ✅ **Funciona sempre:** Mesmo em macOS antigo

---

**Recomendação:** Use o instalador oficial. É muito mais rápido e confiável.

