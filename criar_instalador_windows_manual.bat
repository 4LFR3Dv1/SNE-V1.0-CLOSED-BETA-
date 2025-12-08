@echo off
REM Script alternativo - usa caminho completo do Inno Setup
REM Use este se o Inno Setup não estiver no PATH

echo ========================================
echo 📦 Criando Instalador SNE RADAR
echo ========================================
echo.

REM Verificar se o executável foi buildado
if not exist "dist\SNE_RADAR.exe" (
    echo ❌ Executável não encontrado!
    echo 💡 Primeiro você precisa buildar o executável:
    echo    build_windows.bat
    echo.
    pause
    exit /b 1
)

REM Caminhos comuns do Inno Setup
set INNO_PATH1="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set INNO_PATH2="C:\Program Files\Inno Setup 6\ISCC.exe"
set INNO_PATH3="%LOCALAPPDATA%\Programs\Inno Setup\ISCC.exe"

REM Tentar encontrar Inno Setup
set INNO_FOUND=0

if exist %INNO_PATH1% (
    set INNO_CMD=%INNO_PATH1%
    set INNO_FOUND=1
    goto :found
)

if exist %INNO_PATH2% (
    set INNO_CMD=%INNO_PATH2%
    set INNO_FOUND=1
    goto :found
)

if exist %INNO_PATH3% (
    set INNO_CMD=%INNO_PATH3%
    set INNO_FOUND=1
    goto :found
)

:found
if %INNO_FOUND%==0 (
    echo ❌ Inno Setup não encontrado!
    echo.
    echo 💡 Por favor, instale Inno Setup:
    echo    https://jrsoftware.org/isinfo.php
    echo.
    echo 💡 Ou informe o caminho manualmente editando este arquivo .bat
    echo.
    pause
    exit /b 1
)

echo ✅ Inno Setup encontrado: %INNO_CMD%
echo.

REM Criar diretório para o instalador
if not exist "installer" mkdir installer

REM Compilar o instalador
echo 🔨 Compilando instalador...
echo.

%INNO_CMD% setup_sne_radar.iss

if errorlevel 1 (
    echo.
    echo ❌ Erro ao criar instalador
    echo.
    pause
    exit /b 1
)

REM Verificar se o instalador foi criado
if exist "installer\SNE_RADAR_Setup.exe" (
    echo.
    echo ✅ Instalador criado com sucesso!
    echo.
    echo 📦 Arquivo: installer\SNE_RADAR_Setup.exe
    echo.
) else (
    echo.
    echo ❌ Instalador não foi criado
    echo.
    pause
    exit /b 1
)

pause


