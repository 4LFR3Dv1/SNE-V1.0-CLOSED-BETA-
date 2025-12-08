@echo off
REM Script de verificação de instalação para Windows
REM Execute: verificar_instalacao_windows.bat

echo ========================================
echo 🔍 Verificando Instalação - SNE RADAR
echo ========================================
echo.

REM Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python NÃO encontrado!
    echo.
    echo 💡 SOLUÇÃO:
    echo    1. Instale Python de: https://www.python.org/downloads/
    echo    2. Durante a instalação, MARQUE "Add Python to PATH"
    echo    3. Reinicie o computador após instalar
    echo.
) else (
    python --version
    echo ✅ Python encontrado!
)

REM Verificar pip
echo.
echo [2/4] Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip NÃO encontrado via python -m pip
    echo 💡 Tentando py launcher...
    py -m pip --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ pip NÃO encontrado!
        echo.
        echo 💡 SOLUÇÃO:
        echo    Execute: python -m ensurepip --upgrade
        echo    Ou: py -m ensurepip --upgrade
        echo.
    ) else (
        py -m pip --version
        echo ✅ pip encontrado via py launcher!
        echo 💡 Use: py -m pip install [pacote]
    )
) else (
    python -m pip --version
    echo ✅ pip encontrado!
)

REM Verificar Node.js
echo.
echo [3/4] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js NÃO encontrado!
    echo.
    echo 💡 SOLUÇÃO:
    echo    Instale Node.js de: https://nodejs.org/
    echo    Reinicie o Prompt de Comando após instalar
    echo.
) else (
    node --version
    echo ✅ Node.js encontrado!
)

REM Verificar npm
echo.
echo [4/4] Verificando npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm NÃO encontrado!
    echo 💡 npm geralmente vem com Node.js
    echo 💡 Reinstale o Node.js: https://nodejs.org/
) else (
    npm --version
    echo ✅ npm encontrado!
)

echo.
echo ========================================
echo 📋 Resumo
echo ========================================
echo.

REM Verificar tudo
python --version >nul 2>&1
set PYTHON_OK=%errorlevel%

python -m pip --version >nul 2>&1
if errorlevel 1 (
    py -m pip --version >nul 2>&1
    set PIP_OK=%errorlevel%
) else (
    set PIP_OK=0
)

node --version >nul 2>&1
set NODE_OK=%errorlevel%

npm --version >nul 2>&1
set NPM_OK=%errorlevel%

if %PYTHON_OK%==0 if %PIP_OK%==0 if %NODE_OK%==0 if %NPM_OK%==0 (
    echo ✅ TUDO PRONTO! Você pode executar: build_windows.bat
    echo.
) else (
    echo ⚠️  Alguns componentes estão faltando. Corrija os erros acima.
    echo.
    echo 💡 Comandos úteis:
    echo    - Instalar pip: python -m ensurepip --upgrade
    echo    - Usar pip: python -m pip install [pacote]
    echo    - Alternativa: py -m pip install [pacote]
    echo.
)

pause


