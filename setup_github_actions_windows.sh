#!/bin/bash
# Configura GitHub Actions para buildar Windows automaticamente
# Esta é a opção MAIS FÁCIL e mais confiável!

echo "========================================"
echo "🚀 Configurar GitHub Actions para Windows"
echo "========================================"
echo ""

# Criar diretório .github/workflows se não existir
mkdir -p .github/workflows

# Criar workflow para build Windows
cat > .github/workflows/build-windows.yml << 'EOF'
name: Build Windows Installer

on:
  workflow_dispatch:  # Permite executar manualmente
  push:
    branches: [ main, master ]
    paths:
      - 'frontend/**'
      - '*.py'
      - 'build_windows.spec'
      - 'setup_sne_radar.iss'
      - '.github/workflows/build-windows.yml'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pywebview pyinstaller flask flask-socketio flask-sqlalchemy
        
    - name: Build frontend
      working-directory: ./frontend
      run: |
        npm install
        npm run build
        
    - name: Build executable
      run: |
        python -m PyInstaller build_windows.spec --clean --noconfirm
        
    - name: Download Inno Setup
      run: |
        Invoke-WebRequest -Uri "https://jrsoftware.org/download.php/is.exe" -OutFile "innosetup.exe"
        
    - name: Install Inno Setup
      run: |
        Start-Process -FilePath "innosetup.exe" -ArgumentList "/SILENT" -Wait
        
    - name: Create installer
      run: |
        & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_sne_radar.iss
        
    - name: Upload installer
      uses: actions/upload-artifact@v3
      with:
        name: SNE_RADAR_Setup
        path: installer/SNE_RADAR_Setup.exe
        
    - name: Create Release (optional)
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: installer/SNE_RADAR_Setup.exe
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
EOF

echo "✅ Workflow criado: .github/workflows/build-windows.yml"
echo ""

# Verificar se é um repositório git
if [ ! -d ".git" ]; then
    echo "⚠️  Não é um repositório Git"
    echo ""
    echo "💡 Para usar GitHub Actions, você precisa:"
    echo ""
    echo "1. Inicializar Git:"
    echo "   git init"
    echo ""
    echo "2. Criar repositório no GitHub"
    echo ""
    echo "3. Fazer commit e push:"
    echo "   git add ."
    echo "   git commit -m 'Add Windows build workflow'"
    echo "   git remote add origin https://github.com/seu-usuario/seu-repo.git"
    echo "   git push -u origin main"
    echo ""
    echo "4. Ir em Actions no GitHub e executar o workflow"
    echo ""
else
    echo "✅ Repositório Git encontrado"
    echo ""
    echo "📋 PRÓXIMOS PASSOS:"
    echo ""
    echo "1. Adicione os arquivos ao Git:"
    echo "   git add .github/workflows/build-windows.yml"
    echo ""
    echo "2. Faça commit:"
    echo "   git commit -m 'Add Windows build workflow'"
    echo ""
    echo "3. Faça push para GitHub:"
    echo "   git push"
    echo ""
    echo "4. Vá em: https://github.com/seu-usuario/seu-repo/actions"
    echo "   E execute o workflow 'Build Windows Installer'"
    echo ""
    echo "5. Aguarde o build (5-10 minutos)"
    echo ""
    echo "6. Baixe o instalador na aba 'Artifacts'"
    echo ""
fi

echo ""
echo "💡 VANTAGENS do GitHub Actions:"
echo "   ✅ Não precisa instalar nada no seu Mac"
echo "   ✅ Build automático em Windows real"
echo "   ✅ Mais confiável que Wine"
echo "   ✅ Pode automatizar releases"
echo ""


