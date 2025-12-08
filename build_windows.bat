@echo off
REM Script de build para Windows - SNE RADAR Desktop
REM Execute: build_windows.bat

echo ========================================
echo 🔨 Construindo SNE RADAR para Windows
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

REM Verificar Node.js (para buildar frontend)
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js não encontrado!
    echo 💡 Node.js é necessário APENAS para buildar o frontend
    echo 💡 O executável FINAL não precisará do Node.js!
    echo.
    echo Instale Node.js de: https://nodejs.org/
    pause
    exit /b 1
)

REM 1. Verificar pywebview
echo 📦 Verificando pywebview...
python -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo 📥 Instalando pywebview...
    python -m pip install pywebview
    if errorlevel 1 (
        echo ❌ Erro ao instalar pywebview
        echo 💡 Tentando com py launcher...
        py -m pip install pywebview
        if errorlevel 1 (
            echo ❌ Erro ao instalar pywebview
            echo 💡 Verifique se pip está instalado: python -m ensurepip --upgrade
            pause
            exit /b 1
        )
    )
) else (
    echo ✅ pywebview já instalado
)

REM 2. Build do frontend
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

REM 3. Verificar PyInstaller
echo.
echo 📦 Verificando PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo 📥 Instalando PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo 💡 Tentando com py launcher...
        py -m pip install pyinstaller
        if errorlevel 1 (
            echo ❌ Erro ao instalar PyInstaller
            echo 💡 Verifique se pip está instalado: python -m ensurepip --upgrade
            pause
            exit /b 1
        )
    )
) else (
    echo ✅ PyInstaller já instalado
)

REM 4. Criar diretórios
echo.
echo 📁 Criando diretórios...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM 5. Build executável
echo.
echo 🔨 Criando executável Windows...
python -m PyInstaller build_windows.spec --clean --noconfirm
if errorlevel 1 (
    echo ❌ Erro ao criar executável
    pause
    exit /b 1
)

REM 6. Verificar resultado
if exist "dist\SNE_RADAR.exe" (
    echo.
    echo ✅ Build completo!
    echo.
    echo 📦 Executável criado em: dist\SNE_RADAR.exe
    echo.
    echo ✅ O executável inclui:
    echo    - Backend Python completo
    echo    - Frontend Vue.js buildado
    echo    - Todas as dependências
    echo    - Banco SQLite (será criado na primeira execução)
    echo.
    echo 💡 O executável é STANDALONE - não precisa de:
    echo    ❌ Python instalado
    echo    ❌ Node.js instalado
    echo    ❌ Dependências instaladas
    echo    ✅ Tudo está incluído!
    echo.
    echo 🚀 Para testar:
    echo    dist\SNE_RADAR.exe
    echo.
) else (
    echo ❌ Executável não foi criado
    pause
    exit /b 1
)

pause

