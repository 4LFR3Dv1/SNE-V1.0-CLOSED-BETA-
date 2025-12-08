# Script de build para Windows (PowerShell)
# Execute: .\build_windows.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔨 Construindo SNE RADAR para Windows" -ForegroundColor Cyan
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

# Verificar Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não encontrado!" -ForegroundColor Red
    Write-Host "💡 Instale Node.js de: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Verificar pywebview
Write-Host "📦 Verificando pywebview..." -ForegroundColor Yellow
$webviewCheck = python -c "import webview" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "📥 Instalando pywebview..." -ForegroundColor Yellow
    pip install pywebview
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar pywebview" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ pywebview já instalado" -ForegroundColor Green
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

# Verificar PyInstaller
Write-Host ""
Write-Host "📦 Verificando PyInstaller..." -ForegroundColor Yellow
$pyinstallerCheck = python -m PyInstaller --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "📥 Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar PyInstaller" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ PyInstaller já instalado" -ForegroundColor Green
}

# Criar diretórios
Write-Host ""
Write-Host "📁 Criando diretórios..." -ForegroundColor Yellow
if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" | Out-Null }
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }

# Build executável
Write-Host ""
Write-Host "🔨 Criando executável Windows..." -ForegroundColor Yellow
python -m PyInstaller build_windows.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao criar executável" -ForegroundColor Red
    exit 1
}

# Verificar resultado
if (Test-Path "dist\SNE_RADAR.exe") {
    Write-Host ""
    Write-Host "✅ Build completo!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Executável criado em: dist\SNE_RADAR.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🚀 Para testar:" -ForegroundColor Yellow
    Write-Host "   .\dist\SNE_RADAR.exe" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Executável não foi criado" -ForegroundColor Red
    exit 1
}


