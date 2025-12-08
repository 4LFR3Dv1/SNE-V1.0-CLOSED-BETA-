#!/bin/bash
# Prepara arquivos para build em Windows
# Use este script se você vai buildar em uma máquina Windows depois

echo "========================================"
echo "📦 Preparando Build para Windows"
echo "========================================"
echo ""

# Criar arquivo com instruções
cat > INSTRUCOES_BUILD_WINDOWS.txt << 'EOF'
========================================
INSTRUÇÕES PARA BUILD NO WINDOWS
========================================

1. Copie TODA a pasta do projeto para o Windows
   (ou use Git para clonar no Windows)

2. No Windows, abra o Prompt de Comando

3. Navegue até a pasta do projeto:
   cd C:\caminho\para\SNE_BACKUP_CLEAN

4. Execute o build:
   build_windows.bat

5. Depois de buildar o executável, crie o instalador:
   criar_instalador_windows.bat

6. O instalador estará em: installer\SNE_RADAR_Setup.exe

========================================
REQUISITOS NO WINDOWS:
========================================

- Python 3.10+ (com "Add to PATH" marcado)
- Node.js 18+
- Inno Setup (para criar instalador)

========================================
EOF

echo "✅ Arquivo de instruções criado: INSTRUCOES_BUILD_WINDOWS.txt"
echo ""

# Verificar se frontend precisa ser buildado
if [ ! -d "frontend/dist" ]; then
    echo "⚠️  Frontend não está buildado"
    echo ""
    echo "💡 Você pode buildar o frontend no Mac:"
    echo "   cd frontend && npm install && npm run build"
    echo ""
    echo "   Ou buildar no Windows (o script build_windows.bat faz isso)"
    echo ""
fi

# Criar checklist
cat > CHECKLIST_WINDOWS.txt << 'EOF'
CHECKLIST - Build no Windows
=============================

Antes de buildar no Windows, verifique:

[ ] Python 3.10+ instalado
[ ] Node.js 18+ instalado
[ ] Inno Setup instalado (para instalador)
[ ] Projeto copiado para Windows
[ ] Prompt de Comando aberto na pasta do projeto

Comandos:
1. build_windows.bat          (cria o executável)
2. criar_instalador_windows.bat  (cria o instalador)

Resultado:
- dist\SNE_RADAR.exe (executável)
- installer\SNE_RADAR_Setup.exe (instalador)
EOF

echo "✅ Checklist criado: CHECKLIST_WINDOWS.txt"
echo ""
echo "📋 ARQUIVOS CRIADOS:"
echo "   - INSTRUCOES_BUILD_WINDOWS.txt"
echo "   - CHECKLIST_WINDOWS.txt"
echo ""
echo "💡 Copie estes arquivos junto com o projeto para Windows"
echo ""


