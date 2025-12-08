@echo off
REM Script de build para Windows com Nuitka (Proteção de IP)
REM Execute: build_windows_nuitka.bat

echo ========================================
echo 🔨 Building SNE RADAR com Nuitka (Windows)
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo 💡 Instale Python de: https://www.python.org/
    pause
    exit /b 1
)

REM Verificar Nuitka
echo 📦 Verificando Nuitka...
python -m nuitka --version >nul 2>&1
if errorlevel 1 (
    echo 📥 Instalando Nuitka...
    pip install nuitka
    if errorlevel 1 (
        echo ❌ Erro ao instalar Nuitka
        pause
        exit /b 1
    )
) else (
    echo ✅ Nuitka encontrado
)

REM Build do frontend
echo.
echo 📦 Buildando frontend Vue.js...
if not exist "frontend" (
    echo ❌ Diretório frontend não encontrado
    pause
    exit /b 1
)

cd frontend

if not exist "node_modules" (
    echo 📥 Instalando dependências do frontend...
    call npm install
    if errorlevel 1 (
        echo ❌ Erro ao instalar dependências
        cd ..
        pause
        exit /b 1
    )
)

echo 🔨 Compilando frontend para produção...
call npm run build
if errorlevel 1 (
    echo ❌ Erro ao buildar frontend
    cd ..
    pause
    exit /b 1
)

if not exist "dist\index.html" (
    echo ❌ Frontend não foi buildado corretamente
    cd ..
    pause
    exit /b 1
)

echo ✅ Frontend buildado com sucesso
cd ..

REM Verificar se ícone existe
set ICON_OPTION=
if exist "assets\logo_sne.ico" (
    echo ✅ Ícone encontrado: assets\logo_sne.ico
    set ICON_OPTION=--windows-icon-from-ico=assets\logo_sne.ico
) else (
    echo ⚠️  Ícone não encontrado (assets\logo_sne.ico) - usando padrão
)

REM Build com Nuitka
echo.
echo 🔨 Compilando com Nuitka...
echo    (Isso pode levar 15-30 minutos...)
echo.

python -m nuitka ^
    --standalone ^
    --enable-plugin=anti-bloat ^
    --enable-plugin=pywebview ^
    --include-data-dir=frontend/dist=frontend/dist ^
    --include-module=flask ^
    --include-module=flask_socketio ^
    --include-module=flask_sqlalchemy ^
    --include-module=flask_login ^
    --include-module=flask_limiter ^
    --include-module=motor_renan ^
    --include-module=contexto_global ^
    --include-module=estrutura_mercado ^
    --include-module=multi_timeframe ^
    --include-module=confluencia ^
    --include-module=fluxo_ativo ^
    --include-module=catalogo_magnetico ^
    --include-module=padroes_graficos ^
    --include-module=indicadores ^
    --include-module=indicadores_avancados ^
    --include-module=analise_candles_detalhada ^
    --include-module=gestao_risco_profissional ^
    --include-module=relatorio_profissional ^
    --include-module=calcular_suportes_resistencias ^
    --include-module=niveis_operacionais ^
    --include-module=database_config ^
    --include-module=config ^
    --include-package-data=pandas ^
    --include-package-data=numpy ^
    --include-package-data=matplotlib ^
    --output-dir=dist ^
    --output-filename=SNE_RADAR.exe ^
    --windows-console-mode=disable ^
    %ICON_OPTION% ^
    --remove-output ^
    sne_desktop.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao compilar com Nuitka
    echo 💡 Verifique se você tem Visual Studio Build Tools instalado
    pause
    exit /b 1
)

REM Verificar resultado
if exist "dist\SNE_RADAR.dist\SNE_RADAR.exe" (
    echo.
    echo ✅ Build completo!
    echo.
    echo 📦 Executável criado em: dist\SNE_RADAR.dist\SNE_RADAR.exe
    echo.
    echo 🔐 Proteção de IP:
    echo    ✅ Código compilado para C++
    echo    ✅ Muito mais difícil de engenharia reversa
    echo    ✅ Binário nativo (não Python bytecode)
    echo.
    echo 🚀 Para testar:
    echo    dist\SNE_RADAR.dist\SNE_RADAR.exe
    echo.
) else (
    echo.
    echo ❌ Executável não foi criado
    echo 💡 Verifique os erros acima
    pause
    exit /b 1
)

echo ✅ Build com Nuitka concluído!
pause

