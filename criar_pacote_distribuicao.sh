#!/bin/bash
# Script para criar pacote de distribuição segura do SNE_RADAR.app
# Inclui EULA, instruções e avisos de propriedade intelectual

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Criando pacote de distribuição segura do SNE_RADAR${NC}"
echo ""

# 1. Verificar se o app existe
APP_PATH="dist/SNE_RADAR.app"
if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}❌ Erro: $APP_PATH não encontrado!${NC}"
    echo ""
    echo "Por favor, build o app primeiro:"
    echo "  ./build_with_launcher.sh"
    echo ""
    echo "Ou com Nuitka (recomendado para proteção):"
    echo "  ./build_nuitka.sh"
    exit 1
fi

echo -e "${GREEN}✅ App encontrado: $APP_PATH${NC}"

# 2. Criar diretório temporário para o pacote
DIST_DIR="dist/SNE_RADAR_DISTRIBUICAO"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

echo -e "${YELLOW}📁 Criando estrutura do pacote...${NC}"

# 3. Copiar o app
cp -R "$APP_PATH" "$DIST_DIR/"

# 4. Criar EULA
echo -e "${YELLOW}📝 Criando EULA...${NC}"
cat > "$DIST_DIR/EULA.txt" << 'EOF'
═══════════════════════════════════════════════════════════════
    END USER LICENSE AGREEMENT (EULA)
    SNE RADAR - Sistema Neural Estratégico
═══════════════════════════════════════════════════════════════

IMPORTANTE: LEIA ATENTAMENTE ESTE ACORDO ANTES DE USAR O SOFTWARE.

Ao usar este software, você concorda com os termos abaixo. Se você
não concordar, NÃO use o software.

───────────────────────────────────────────────────────────────

1. PROPRIEDADE INTELECTUAL

Este software e todo seu conteúdo (incluindo, mas não limitado a,
código fonte, algoritmos, lógica de negócio, interface gráfica,
documentação e marcas) são propriedade exclusiva do desenvolvedor.
Todos os direitos reservados.

O software contém informações proprietárias e confidenciais que são
protegidas por leis de propriedade intelectual e outros direitos.

───────────────────────────────────────────────────────────────

2. LICENÇA DE USO

Esta licença permite o uso do software APENAS para fins de TESTE
e AVALIAÇÃO, sujeito às seguintes restrições:

✅ PERMITIDO:
   - Usar o software para teste pessoal
   - Avaliar funcionalidades
   - Reportar bugs e feedback

❌ PROIBIDO:
   - Uso comercial sem autorização expressa
   - Redistribuir o software
   - Compartilhar com terceiros
   - Fazer engenharia reversa
   - Descompilar ou desmontar o código
   - Copiar, modificar ou criar trabalhos derivados
   - Remover avisos de propriedade intelectual
   - Usar algoritmos ou lógica para criar software similar

───────────────────────────────────────────────────────────────

3. RESTRIÇÕES TÉCNICAS

Você NÃO pode:
   - Tentar extrair o código fonte
   - Usar ferramentas de engenharia reversa
   - Analisar o binário para entender algoritmos
   - Copiar funcionalidades ou lógica de negócio
   - Criar software concorrente baseado neste software

───────────────────────────────────────────────────────────────

4. CONFIDENCIALIDADE

Este software é fornecido sob confidencialidade. Você concorda em:
   - Manter o software em confiança
   - Não divulgar informações sobre o software
   - Não compartilhar o software com terceiros
   - Reportar qualquer uso não autorizado

───────────────────────────────────────────────────────────────

5. GARANTIA E LIMITAÇÃO DE RESPONSABILIDADE

O SOFTWARE É FORNECIDO "COMO ESTÁ", SEM GARANTIAS DE QUALQUER TIPO,
EXPRESSAS OU IMPLÍCITAS, INCLUINDO, MAS NÃO LIMITADO A, GARANTIAS DE
COMERCIALIZAÇÃO, ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO E NÃO VIOLAÇÃO.

Em nenhuma circunstância o desenvolvedor será responsável por danos
diretos, indiretos, incidentais, especiais ou consequenciais
resultantes do uso ou incapacidade de usar o software.

───────────────────────────────────────────────────────────────

6. VIOLAÇÃO E REMÉDIOS

Qualquer violação deste acordo resultará em:
   - Rescisão imediata da licença
   - Ação legal por violação de propriedade intelectual
   - Busca de indenização por danos

───────────────────────────────────────────────────────────────

7. CONTATO

Para questões sobre licenciamento comercial ou uso autorizado:
   Entre em contato com o desenvolvedor.

───────────────────────────────────────────────────────────────

Ao usar este software, você confirma que:
   ✅ Leu e entendeu este acordo
   ✅ Concorda em cumprir todos os termos
   ✅ Reconhece que violações resultarão em ação legal

═══════════════════════════════════════════════════════════════
                    © 2025 SNE RADAR
        Todos os direitos reservados. Propriedade intelectual.
═══════════════════════════════════════════════════════════════
EOF

# 5. Criar README de instalação
echo -e "${YELLOW}📖 Criando README de instalação...${NC}"
cat > "$DIST_DIR/README_INSTALACAO.txt" << 'EOF'
═══════════════════════════════════════════════════════════════
        SNE RADAR - Guia de Instalação e Uso
═══════════════════════════════════════════════════════════════

⚠️  AVISO IMPORTANTE DE PROPRIEDADE INTELECTUAL

Este software é fornecido para TESTE e AVALIAÇÃO APENAS.
É propriedade intelectual protegida. Leia o EULA.txt antes de usar.

───────────────────────────────────────────────────────────────

📦 INSTALAÇÃO (macOS)

1. Extraia este arquivo ZIP

2. Leia o EULA.txt e aceite os termos

3. Arraste o SNE_RADAR.app para a pasta Applications:
   - Abra a pasta Applications
   - Arraste SNE_RADAR.app para lá

4. Na primeira execução, o macOS pode bloquear o app:
   - Vá em: System Preferences > Security & Privacy
   - Clique em "Open Anyway" ao lado da mensagem de bloqueio
   - Ou: Clique com botão direito no app > Open > Open

───────────────────────────────────────────────────────────────

🚀 COMO USAR

1. Abra o SNE_RADAR.app (duplo clique)

2. O app abrirá uma janela com a interface

3. Configure suas preferências na primeira execução

───────────────────────────────────────────────────────────────

⚠️  RESTRIÇÕES DE USO

Este é um build de TESTE. Você NÃO pode:

❌ Compartilhar com outras pessoas
❌ Fazer engenharia reversa
❌ Usar comercialmente sem autorização
❌ Redistribuir o software
❌ Copiar funcionalidades ou algoritmos

───────────────────────────────────────────────────────────────

📞 SUPORTE E FEEDBACK

Para reportar bugs ou dar feedback:
   Entre em contato com o desenvolvedor.

───────────────────────────────────────────────────────────────

🔐 PROPRIEDADE INTELECTUAL

Este software contém algoritmos proprietários e informações
confidenciais. Qualquer tentativa de engenharia reversa,
descompilação ou extração de código é PROIBIDA e resultará
em ação legal.

───────────────────────────────────────────────────────────────

Obrigado por testar o SNE RADAR!

═══════════════════════════════════════════════════════════════
                    © 2025 SNE RADAR
═══════════════════════════════════════════════════════════════
EOF

# 6. Criar arquivo de aviso
echo -e "${YELLOW}⚠️  Criando aviso de propriedade intelectual...${NC}"
cat > "$DIST_DIR/AVISO_PROPRIEDADE_INTELECTUAL.txt" << 'EOF'
═══════════════════════════════════════════════════════════════
        ⚠️  AVISO DE PROPRIEDADE INTELECTUAL ⚠️
═══════════════════════════════════════════════════════════════

Este software é PROPRIEDADE INTELECTUAL PROTEGIDA.

O software contém:
   • Algoritmos proprietários
   • Lógica de negócio confidencial
   • Código fonte protegido
   • Informações técnicas exclusivas

───────────────────────────────────────────────────────────────

PROIBIÇÕES ABSOLUTAS:

❌ ENGENHARIA REVERSA
   Não tente extrair, descompilar ou analisar o código.

❌ REDISTRIBUIÇÃO
   Não compartilhe este software com terceiros.

❌ USO COMERCIAL
   Não use comercialmente sem licença expressa.

❌ CÓPIA DE FUNCIONALIDADES
   Não copie algoritmos ou lógica para outros projetos.

───────────────────────────────────────────────────────────────

CONSEQUÊNCIAS DE VIOLAÇÃO:

Qualquer violação resultará em:
   • Rescisão imediata da licença
   • Ação legal por violação de propriedade intelectual
   • Busca de indenização por danos

───────────────────────────────────────────────────────────────

Este software é fornecido para TESTE APENAS.

Leia o EULA.txt para termos completos.

═══════════════════════════════════════════════════════════════
                    © 2025 SNE RADAR
═══════════════════════════════════════════════════════════════
EOF

# 7. Criar ZIP
echo ""
echo -e "${YELLOW}📦 Criando arquivo ZIP...${NC}"
cd dist
ZIP_NAME="SNE_RADAR_DISTRIBUICAO_$(date +%Y%m%d_%H%M%S).zip"
zip -r "$ZIP_NAME" "SNE_RADAR_DISTRIBUICAO" -q
cd ..

# 8. Calcular tamanho
ZIP_SIZE=$(du -h "dist/$ZIP_NAME" | cut -f1)

echo ""
echo -e "${GREEN}✅ Pacote criado com sucesso!${NC}"
echo ""
echo -e "${BLUE}📦 Arquivo:${NC} dist/$ZIP_NAME"
echo -e "${BLUE}📊 Tamanho:${NC} $ZIP_SIZE"
echo ""
echo -e "${GREEN}📋 Conteúdo do pacote:${NC}"
echo "   ✅ SNE_RADAR.app"
echo "   ✅ EULA.txt (Termos de uso)"
echo "   ✅ README_INSTALACAO.txt"
echo "   ✅ AVISO_PROPRIEDADE_INTELECTUAL.txt"
echo ""
echo -e "${YELLOW}🚀 Próximos passos:${NC}"
echo "   1. Verifique o conteúdo: open dist/SNE_RADAR_DISTRIBUICAO"
echo "   2. Envie o arquivo ZIP para o colega:"
echo "      dist/$ZIP_NAME"
echo "   3. Lembre o colega de ler o EULA antes de usar"
echo ""
echo -e "${RED}⚠️  IMPORTANTE:${NC}"
echo "   • Este é um build de TESTE"
echo "   • PyInstaller NÃO protege código efetivamente"
echo "   • Para melhor proteção, considere rebuildar com Nuitka"
echo "   • Ver: ./build_nuitka.sh"
echo ""

