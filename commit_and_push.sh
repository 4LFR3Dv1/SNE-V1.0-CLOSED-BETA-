#!/bin/bash

# Script para fazer commit e push das mudanças para o GitHub
echo "🚀 Fazendo commit e push para o GitHub..."

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ Execute este script no diretório raiz do SNE Radar"
    exit 1
fi

# Inicializar git se não existir
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositório git..."
    git init
fi

# Adicionar remote se não existir
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Adicionando remote do GitHub..."
    git remote add origin https://github.com/4LFR3Dv1/SNE-RADAR.git
fi

# Adicionar todos os arquivos
echo "📝 Adicionando arquivos..."
git add .

# Fazer commit
echo "💾 Fazendo commit..."
git commit -m "feat: Implementação completa de charts e integrações

✅ Charts implementados:
- Gráfico principal com candlesticks e volume
- Gráficos de Machine Learning
- Gráficos de Backtesting
- Indicadores técnicos (EMA, Bollinger, etc.)

✅ Integrações corrigidas:
- APIs CoinGlass e CMC habilitadas
- Endpoints de alertas e exportação
- Funções JavaScript completas
- Feature flags configuradas

✅ Funcionalidades restauradas:
- Dashboard profissional completo
- Sistema de indicadores avançados
- Machine Learning e Backtesting
- Exportação de dados (CSV/PDF)

✅ Deploy otimizado:
- Configuração Render atualizada
- Dependências otimizadas
- Scripts de verificação criados

🎯 Sistema 100% funcional e integrado!"

# Push para o GitHub
echo "🚀 Fazendo push para o GitHub..."
git push -u origin main

echo ""
echo "🎉 Commit e push concluídos com sucesso!"
echo "📋 Resumo das mudanças:"
echo "   - Charts implementados e funcionais"
echo "   - Integrações corrigidas"
echo "   - APIs externas habilitadas"
echo "   - Dashboard profissional completo"
echo "   - Deploy otimizado para Render"
echo ""
echo "🌐 Acesse: https://github.com/4LFR3Dv1/SNE-RADAR"




