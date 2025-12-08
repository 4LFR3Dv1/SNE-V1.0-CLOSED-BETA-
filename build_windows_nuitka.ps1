# Script de build para Windows com Nuitka (Proteção de IP)
# Execute: .\build_windows_nuitka.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔨 Building SNE RADAR com Nuitka (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "💡 Instale Python de: https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Verificar Nuitka
Write-Host "📦 Verificando Nuitka..." -ForegroundColor Yellow
$nuitkaCheck = python -m nuitka --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "📥 Instalando Nuitka..." -ForegroundColor Yellow
    pip install nuitka
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar Nuitka" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Nuitka encontrado" -ForegroundColor Green
    Write-Host "   Versão: $($nuitkaCheck -split "`n" | Select-Object -First 1)" -ForegroundColor Gray
}

# Build do frontend
Write-Host ""
Write-Host "📦 Buildando frontend Vue.js..." -ForegroundColor Yellow
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Diretório frontend não encontrado" -ForegroundColor Red
    exit 1
}

Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "📥 Instalando dependências do frontend..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
}

Write-Host "🔨 Compilando frontend para produção..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao buildar frontend" -ForegroundColor Red
    Set-Location ..
    exit 1
}

if (-not (Test-Path "dist\index.html")) {
    Write-Host "❌ Frontend não foi buildado corretamente" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Frontend buildado com sucesso" -ForegroundColor Green
Set-Location ..

# Verificar se ícone existe
$iconOption = ""
if (Test-Path "assets\logo_sne.ico") {
    Write-Host "✅ Ícone encontrado: assets\logo_sne.ico" -ForegroundColor Green
    $iconOption = "--windows-icon-from-ico=assets\logo_sne.ico"
} else {
    Write-Host "⚠️  Ícone não encontrado (assets\logo_sne.ico) - usando padrão" -ForegroundColor Yellow
}

# Build com Nuitka
Write-Host ""
Write-Host "🔨 Compilando com Nuitka..." -ForegroundColor Yellow
Write-Host "   (Isso pode levar 15-30 minutos...)" -ForegroundColor Gray
Write-Host ""

$nuitkaArgs = @(
    "--standalone",
    "--enable-plugin=anti-bloat",
    "--enable-plugin=pywebview",
    "--include-data-dir=frontend/dist=frontend/dist",
    "--include-module=flask",
    "--include-module=flask_socketio",
    "--include-module=flask_sqlalchemy",
    "--include-module=flask_login",
    "--include-module=flask_limiter",
    "--include-module=motor_renan",
    "--include-module=contexto_global",
    "--include-module=estrutura_mercado",
    "--include-module=multi_timeframe",
    "--include-module=confluencia",
    "--include-module=fluxo_ativo",
    "--include-module=catalogo_magnetico",
    "--include-module=padroes_graficos",
    "--include-module=indicadores",
    "--include-module=indicadores_avancados",
    "--include-module=analise_candles_detalhada",
    "--include-module=gestao_risco_profissional",
    "--include-module=relatorio_profissional",
    "--include-module=calcular_suportes_resistencias",
    "--include-module=niveis_operacionais",
    "--include-module=database_config",
    "--include-module=config",
    "--include-package-data=pandas",
    "--include-package-data=numpy",
    "--include-package-data=matplotlib",
    "--output-dir=dist",
    "--output-filename=SNE_RADAR.exe",
    "--windows-console-mode=disable",
    "--remove-output"
)

if ($iconOption) {
    $nuitkaArgs += $iconOption
}

$nuitkaArgs += "sne_desktop.py"

python -m nuitka @nuitkaArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao compilar com Nuitka" -ForegroundColor Red
    Write-Host "💡 Verifique se você tem Visual Studio Build Tools instalado" -ForegroundColor Yellow
    exit 1
}

# Verificar resultado
$exePath = "dist\SNE_RADAR.dist\SNE_RADAR.exe"
if (Test-Path $exePath) {
    Write-Host ""
    Write-Host "✅ Build completo!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Executável criado em: $exePath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔐 Proteção de IP:" -ForegroundColor Yellow
    Write-Host "   ✅ Código compilado para C++" -ForegroundColor Green
    Write-Host "   ✅ Muito mais difícil de engenharia reversa" -ForegroundColor Green
    Write-Host "   ✅ Binário nativo (não Python bytecode)" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Para testar:" -ForegroundColor Yellow
    Write-Host "   .\$exePath" -ForegroundColor White
    Write-Host ""
    
    # Calcular tamanho
    $exeSize = (Get-Item $exePath).Length / 1MB
    Write-Host "📊 Tamanho: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Executável não foi criado" -ForegroundColor Red
    Write-Host "💡 Verifique os erros acima" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Build com Nuitka concluído!" -ForegroundColor Green

