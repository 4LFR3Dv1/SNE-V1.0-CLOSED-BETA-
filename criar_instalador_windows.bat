@echo off
REM Script para criar instalador Windows (.exe) usando Inno Setup
REM Execute: criar_instalador_windows.bat

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

echo ✅ Executável encontrado: dist\SNE_RADAR.exe
echo.

REM Verificar se Inno Setup está instalado
where iscc >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Inno Setup não encontrado no PATH
    echo.
    echo 💡 SOLUÇÃO:
    echo    1. Baixe Inno Setup (gratuito): https://jrsoftware.org/isinfo.php
    echo    2. Instale normalmente
    echo.
    echo 💡 ALTERNATIVA: Adicione o caminho do Inno Setup ao PATH
    echo    Normalmente em: C:\Program Files (x86)\Inno Setup 6\
    echo.
    echo 💡 Ou execute manualmente:
    echo    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_sne_radar.iss
    echo.
    pause
    exit /b 1
)

echo ✅ Inno Setup encontrado
echo.

REM Criar diretório para o instalador
if not exist "installer" mkdir installer

REM Compilar o instalador
echo 🔨 Compilando instalador...
echo.

iscc setup_sne_radar.iss

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
    echo 📋 O instalador inclui:
    echo    ✅ Executável SNE_RADAR.exe
    echo    ✅ Frontend Vue.js
    echo    ✅ Todas as dependências
    echo    ✅ Atalhos no menu Iniciar
    echo    ✅ Opção de atalho na área de trabalho
    echo    ✅ Desinstalador automático
    echo.
    echo 🚀 Você pode distribuir este arquivo para outros usuários!
    echo    Eles só precisam executar o instalador.
    echo.
) else (
    echo.
    echo ❌ Instalador não foi criado
    echo.
    pause
    exit /b 1
)

pause


