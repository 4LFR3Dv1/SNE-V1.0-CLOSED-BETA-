# Script para criar pacote de distribuição segura do SNE_RADAR.exe para Windows
# Inclui EULA, instruções e avisos de propriedade intelectual

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📦 Criando pacote de distribuição segura" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o executável existe
$EXE_PATH = "dist\SNE_RADAR.exe"
$DIST_PATH = "dist\SNE_RADAR.dist\SNE_RADAR.exe"

# Verificar qual executável existe
$EXE_TO_USE = $null
if (Test-Path $EXE_PATH) {
    $EXE_TO_USE = $EXE_PATH
    Write-Host "✅ Executável encontrado: $EXE_PATH" -ForegroundColor Green
} elseif (Test-Path $DIST_PATH) {
    $EXE_TO_USE = $DIST_PATH
    Write-Host "✅ Executável encontrado: $DIST_PATH" -ForegroundColor Green
} else {
    Write-Host "❌ Erro: Executável não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, build o executável primeiro:" -ForegroundColor Yellow
    Write-Host "  .\build_windows.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou com Nuitka (recomendado para proteção):" -ForegroundColor Yellow
    Write-Host "  .\build_windows_nuitka.ps1" -ForegroundColor White
    exit 1
}

# Criar diretório temporário para o pacote
$DIST_DIR = "dist\SNE_RADAR_DISTRIBUICAO"
if (Test-Path $DIST_DIR) {
    Write-Host "🗑️  Removendo pacote anterior..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $DIST_DIR
}
New-Item -ItemType Directory -Path $DIST_DIR | Out-Null

Write-Host "📁 Criando estrutura do pacote..." -ForegroundColor Yellow

# Copiar o executável ou pasta dist
if ($EXE_TO_USE -eq $EXE_PATH) {
    # PyInstaller - copiar apenas o .exe
    Copy-Item $EXE_PATH $DIST_DIR\
} else {
    # Nuitka - copiar toda a pasta .dist
    $DIST_FOLDER = Split-Path $DIST_PATH -Parent
    Copy-Item -Recurse $DIST_FOLDER $DIST_DIR\
}

# Criar EULA
Write-Host "📝 Criando EULA..." -ForegroundColor Yellow
$EULA_CONTENT = @"
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
"@
$EULA_CONTENT | Out-File -FilePath "$DIST_DIR\EULA.txt" -Encoding UTF8

# Criar README de instalação
Write-Host "📖 Criando README de instalação..." -ForegroundColor Yellow
$README_CONTENT = @"
═══════════════════════════════════════════════════════════════
        SNE RADAR - Guia de Instalação e Uso
═══════════════════════════════════════════════════════════════

⚠️  AVISO IMPORTANTE DE PROPRIEDADE INTELECTUAL

Este software é fornecido para TESTE e AVALIAÇÃO APENAS.
É propriedade intelectual protegida. Leia o EULA.txt antes de usar.

───────────────────────────────────────────────────────────────

📦 INSTALAÇÃO (Windows)

1. Extraia este arquivo ZIP

2. Leia o EULA.txt e aceite os termos

3. Execute o SNE_RADAR.exe:
   - Duplo clique no arquivo SNE_RADAR.exe
   - OU clique com botão direito > Executar como administrador

4. Na primeira execução, o Windows Defender pode bloquear:
   - Clique em "Mais informações"
   - Clique em "Executar mesmo assim"
   - Isso é normal para executáveis não assinados

───────────────────────────────────────────────────────────────

🚀 COMO USAR

1. Execute o SNE_RADAR.exe (duplo clique)

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
"@
$README_CONTENT | Out-File -FilePath "$DIST_DIR\README_INSTALACAO.txt" -Encoding UTF8

# Criar arquivo de aviso
Write-Host "⚠️  Criando aviso de propriedade intelectual..." -ForegroundColor Yellow
$AVISO_CONTENT = @"
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
"@
$AVISO_CONTENT | Out-File -FilePath "$DIST_DIR\AVISO_PROPRIEDADE_INTELECTUAL.txt" -Encoding UTF8

# Criar ZIP
Write-Host ""
Write-Host "📦 Criando arquivo ZIP..." -ForegroundColor Yellow
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$ZIP_NAME = "dist\SNE_RADAR_DISTRIBUICAO_$TIMESTAMP.zip"

# Remover ZIP anterior se existir
if (Test-Path $ZIP_NAME) {
    Remove-Item $ZIP_NAME
}

# Criar ZIP usando .NET
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($DIST_DIR, $ZIP_NAME)

# Calcular tamanho
$ZIP_SIZE = (Get-Item $ZIP_NAME).Length / 1MB

Write-Host ""
Write-Host "✅ Pacote criado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Arquivo: $ZIP_NAME" -ForegroundColor Cyan
Write-Host "📊 Tamanho: $([math]::Round($ZIP_SIZE, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Conteúdo do pacote:" -ForegroundColor Green
Write-Host "   ✅ SNE_RADAR.exe (ou pasta SNE_RADAR.dist)" -ForegroundColor White
Write-Host "   ✅ EULA.txt (Termos de uso)" -ForegroundColor White
Write-Host "   ✅ README_INSTALACAO.txt" -ForegroundColor White
Write-Host "   ✅ AVISO_PROPRIEDADE_INTELECTUAL.txt" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Verifique o conteúdo: explorer $DIST_DIR" -ForegroundColor White
Write-Host "   2. Envie o arquivo ZIP para o colega:" -ForegroundColor White
Write-Host "      $ZIP_NAME" -ForegroundColor Cyan
Write-Host "   3. Lembre o colega de ler o EULA antes de usar" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Red
Write-Host "   • Este é um build de TESTE" -ForegroundColor Yellow
Write-Host "   • PyInstaller NÃO protege código efetivamente" -ForegroundColor Yellow
Write-Host "   • Para melhor proteção, considere rebuildar com Nuitka" -ForegroundColor Yellow
Write-Host "   • Ver: .\build_windows_nuitka.ps1" -ForegroundColor Yellow
Write-Host ""

