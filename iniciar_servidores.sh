#!/bin/bash

# Script para iniciar Flask e Vite simultaneamente

echo "🚀 Iniciando SNE Radar - Frontend + Backend"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se estamos no diretório correto
if [ ! -f "sne_radar_web.py" ]; then
    echo -e "${RED}❌ Arquivo sne_radar_web.py não encontrado!${NC}"
    echo "   Execute este script do diretório raiz do projeto"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 não encontrado!${NC}"
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️ Node.js não encontrado. Tentando carregar NVM...${NC}"
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js não encontrado!${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Python: $(python3 --version)${NC}"
echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"
echo ""

# Verificar se as portas estão livres
if lsof -Pi :9999 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️ Porta 9999 já está em uso!${NC}"
    echo "   Parando processo anterior..."
    lsof -ti:9999 | xargs kill -9 2>/dev/null
    sleep 1
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️ Porta 5173 já está em uso!${NC}"
    echo "   Parando processo anterior..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    sleep 1
fi

echo -e "${GREEN}📋 Iniciando servidores...${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🔧 Flask (Backend)${NC}  → http://localhost:9999"
echo -e "${GREEN}⚡ Vite (Frontend)${NC}  → http://localhost:5173"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}💡 Dica:${NC} Pressione Ctrl+C para parar ambos os servidores"
echo ""

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo -e "${YELLOW}⏹️ Parando servidores...${NC}"
    kill $FLASK_PID 2>/dev/null
    kill $VITE_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar Flask em background
echo -e "${GREEN}🔧 Iniciando Flask...${NC}"
python3 sne_radar_web.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!

# Aguardar Flask iniciar
sleep 3

# Verificar se Flask iniciou
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo -e "${RED}❌ Erro ao iniciar Flask!${NC}"
    echo "   Verifique o log: cat /tmp/flask.log"
    exit 1
fi

echo -e "${GREEN}✅ Flask rodando (PID: $FLASK_PID)${NC}"

# Iniciar Vite em background
echo -e "${GREEN}⚡ Iniciando Vite...${NC}"
cd frontend
npm run dev > /tmp/vite.log 2>&1 &
VITE_PID=$!
cd ..

# Aguardar Vite iniciar
sleep 3

# Verificar se Vite iniciou
if ! kill -0 $VITE_PID 2>/dev/null; then
    echo -e "${RED}❌ Erro ao iniciar Vite!${NC}"
    echo "   Verifique o log: cat /tmp/vite.log"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Vite rodando (PID: $VITE_PID)${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎉 Servidores iniciados com sucesso!${NC}"
echo ""
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:9999"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Mostrar logs
echo -e "${YELLOW}📋 Logs (últimas 10 linhas):${NC}"
echo ""
echo "━━━━ Flask ━━━━"
tail -n 5 /tmp/flask.log 2>/dev/null || echo "Nenhum log ainda"
echo ""
echo "━━━━ Vite ━━━━"
tail -n 5 /tmp/vite.log 2>/dev/null || echo "Nenhum log ainda"
echo ""

# Aguardar processos
wait

