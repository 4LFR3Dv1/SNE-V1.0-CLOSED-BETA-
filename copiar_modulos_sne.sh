#!/bin/bash
# Script para copiar módulos do SNE para os serviços

set -e

SERVICES_DIR="services"
SNE_MODULES=(
    "motor_renan.py"
    "contexto_global.py"
    "estrutura_mercado.py"
    "multi_timeframe.py"
    "confluencia.py"
    "fluxo_ativo.py"
    "catalogo_magnetico.py"
    "padroes_graficos.py"
    "indicadores.py"
    "indicadores_avancados.py"
    "analise_candles_detalhada.py"
    "gestao_risco_profissional.py"
    "relatorio_profissional.py"
    "calcular_suportes_resistencias.py"
    "niveis_operacionais.py"
)

echo "📦 Copiando módulos do SNE para serviços..."
echo ""

# Copiar para sne-web
echo "📁 Copiando para sne-web..."
for module in "${SNE_MODULES[@]}"; do
    if [ -f "$module" ]; then
        cp "$module" "$SERVICES_DIR/sne-web/" 2>/dev/null || true
        echo "  ✅ $module"
    else
        echo "  ⚠️  $module não encontrado"
    fi
done

echo ""
echo "✅ Módulos copiados!"
echo ""
echo "📋 Próximos passos:"
echo "1. Verificar se todos os módulos foram copiados"
echo "2. Testar localmente: docker-compose up sne-web"
echo "3. Deploy: ./deploy_cloud_build.sh sne-v1 us-central1"

