@echo off
REM Script para criar pacote de distribuição segura do SNE_RADAR.exe para Windows
REM Execute: criar_pacote_distribuicao_windows.bat

echo ========================================
echo 📦 Criando pacote de distribuição segura
echo ========================================
echo.

REM Verificar se o executável existe
if exist "dist\SNE_RADAR.exe" (
    set EXE_TO_USE=dist\SNE_RADAR.exe
    echo ✅ Executável encontrado: dist\SNE_RADAR.exe
    goto :copy_exe
)

if exist "dist\SNE_RADAR.dist\SNE_RADAR.exe" (
    set EXE_TO_USE=dist\SNE_RADAR.dist\SNE_RADAR.exe
    echo ✅ Executável encontrado: dist\SNE_RADAR.dist\SNE_RADAR.exe
    goto :copy_dist
)

echo ❌ Erro: Executável não encontrado!
echo.
echo Por favor, build o executável primeiro:
echo   build_windows.bat
echo.
echo Ou com Nuitka (recomendado para proteção):
echo   build_windows_nuitka.bat
echo.
pause
exit /b 1

:copy_exe
REM Criar diretório temporário
set DIST_DIR=dist\SNE_RADAR_DISTRIBUICAO
if exist "%DIST_DIR%" (
    echo 🗑️  Removendo pacote anterior...
    rmdir /s /q "%DIST_DIR%"
)
mkdir "%DIST_DIR%"

echo 📁 Copiando executável...
copy "%EXE_TO_USE%" "%DIST_DIR%\"
goto :create_files

:copy_dist
REM Criar diretório temporário
set DIST_DIR=dist\SNE_RADAR_DISTRIBUICAO
if exist "%DIST_DIR%" (
    echo 🗑️  Removendo pacote anterior...
    rmdir /s /q "%DIST_DIR%"
)
mkdir "%DIST_DIR%"

echo 📁 Copiando pasta dist...
xcopy /E /I /Y "dist\SNE_RADAR.dist" "%DIST_DIR%\SNE_RADAR.dist"
goto :create_files

:create_files
echo 📝 Criando arquivos de documentação...

REM Criar EULA
(
echo ═══════════════════════════════════════════════════════════════
echo     END USER LICENSE AGREEMENT (EULA^)
echo     SNE RADAR - Sistema Neural Estratégico
echo ═══════════════════════════════════════════════════════════════
echo.
echo IMPORTANTE: LEIA ATENTAMENTE ESTE ACORDO ANTES DE USAR O SOFTWARE.
echo.
echo Ao usar este software, você concorda com os termos abaixo. Se você
echo não concordar, NÃO use o software.
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo 1. PROPRIEDADE INTELECTUAL
echo.
echo Este software e todo seu conteúdo são propriedade exclusiva do
echo desenvolvedor. Todos os direitos reservados.
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo 2. LICENÇA DE USO
echo.
echo Esta licença permite o uso do software APENAS para fins de TESTE
echo e AVALIAÇÃO.
echo.
echo ✅ PERMITIDO:
echo    - Usar o software para teste pessoal
echo    - Avaliar funcionalidades
echo    - Reportar bugs e feedback
echo.
echo ❌ PROIBIDO:
echo    - Uso comercial sem autorização expressa
echo    - Redistribuir o software
echo    - Compartilhar com terceiros
echo    - Fazer engenharia reversa
echo    - Descompilar ou desmontar o código
echo    - Copiar funcionalidades ou algoritmos
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo 3. GARANTIA
echo.
echo O SOFTWARE É FORNECIDO "COMO ESTÁ", SEM GARANTIAS DE QUALQUER TIPO.
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo ═══════════════════════════════════════════════════════════════
echo                     © 2025 SNE RADAR
echo ═══════════════════════════════════════════════════════════════
) > "%DIST_DIR%\EULA.txt"

REM Criar README
(
echo ═══════════════════════════════════════════════════════════════
echo         SNE RADAR - Guia de Instalação e Uso
echo ═══════════════════════════════════════════════════════════════
echo.
echo ⚠️  AVISO IMPORTANTE DE PROPRIEDADE INTELECTUAL
echo.
echo Este software é fornecido para TESTE e AVALIAÇÃO APENAS.
echo Leia o EULA.txt antes de usar.
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo 📦 INSTALAÇÃO (Windows^)
echo.
echo 1. Extraia este arquivo ZIP
echo.
echo 2. Leia o EULA.txt e aceite os termos
echo.
echo 3. Execute o SNE_RADAR.exe:
echo    - Duplo clique no arquivo SNE_RADAR.exe
echo    - OU clique com botão direito ^> Executar como administrador
echo.
echo 4. Na primeira execução, o Windows Defender pode bloquear:
echo    - Clique em "Mais informações"
echo    - Clique em "Executar mesmo assim"
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo ⚠️  RESTRIÇÕES DE USO
echo.
echo Este é um build de TESTE. Você NÃO pode:
echo.
echo ❌ Compartilhar com outras pessoas
echo ❌ Fazer engenharia reversa
echo ❌ Usar comercialmente sem autorização
echo ❌ Redistribuir o software
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo Obrigado por testar o SNE RADAR!
echo.
echo ═══════════════════════════════════════════════════════════════
echo                     © 2025 SNE RADAR
echo ═══════════════════════════════════════════════════════════════
) > "%DIST_DIR%\README_INSTALACAO.txt"

REM Criar aviso
(
echo ═══════════════════════════════════════════════════════════════
echo         ⚠️  AVISO DE PROPRIEDADE INTELECTUAL ⚠️
echo ═══════════════════════════════════════════════════════════════
echo.
echo Este software é PROPRIEDADE INTELECTUAL PROTEGIDA.
echo.
echo PROIBIÇÕES ABSOLUTAS:
echo.
echo ❌ ENGENHARIA REVERSA
echo ❌ REDISTRIBUIÇÃO
echo ❌ USO COMERCIAL
echo ❌ CÓPIA DE FUNCIONALIDADES
echo.
echo CONSEQUÊNCIAS DE VIOLAÇÃO:
echo    • Rescisão imediata da licença
echo    • Ação legal por violação de propriedade intelectual
echo.
echo ═══════════════════════════════════════════════════════════════
echo                     © 2025 SNE RADAR
echo ═══════════════════════════════════════════════════════════════
) > "%DIST_DIR%\AVISO_PROPRIEDADE_INTELECTUAL.txt"

REM Criar ZIP usando PowerShell (mais confiável)
echo.
echo 📦 Criando arquivo ZIP...
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set ZIP_NAME=dist\SNE_RADAR_DISTRIBUICAO_%TIMESTAMP%.zip

powershell -Command "Compress-Archive -Path '%DIST_DIR%\*' -DestinationPath '%ZIP_NAME%' -Force"

if exist "%ZIP_NAME%" (
    echo.
    echo ✅ Pacote criado com sucesso!
    echo.
    echo 📦 Arquivo: %ZIP_NAME%
    echo.
    echo 📋 Conteúdo do pacote:
    echo    ✅ SNE_RADAR.exe (ou pasta SNE_RADAR.dist^)
    echo    ✅ EULA.txt
    echo    ✅ README_INSTALACAO.txt
    echo    ✅ AVISO_PROPRIEDADE_INTELECTUAL.txt
    echo.
    echo 🚀 Próximos passos:
    echo    1. Verifique o conteúdo: explorer %DIST_DIR%
    echo    2. Envie o arquivo ZIP para o colega
    echo    3. Lembre o colega de ler o EULA antes de usar
    echo.
) else (
    echo ❌ Erro ao criar ZIP
    echo 💡 Certifique-se de que o PowerShell está disponível
)

pause

