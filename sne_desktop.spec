# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec para SNE Radar Desktop (pywebview)
# Executar de: C:\...\SNE-V1.0-CLOSED-BETA--production-functional\

from pathlib import Path
import os

# ROOT = diretório onde o spec está (raiz do projeto)
ROOT = Path(".").resolve()

# Entry point
ENTRY = str(ROOT / "sne_desktop.py")

block_cipher = None

# Coletar arquivos de dados
datas = [
    # Frontend Vue.js buildado (em frontend/dist)
    (str(ROOT / "frontend" / "dist"), "frontend/dist"),
    
    # Templates Flask
    (str(ROOT / "templates"), "templates"),
    
    # Diretórios de módulos Python (necessários como dados também)
    (str(ROOT / "monitors"), "monitors"),
    (str(ROOT / "services"), "services"),
    (str(ROOT / "app"), "app"),
    (str(ROOT / "integrations"), "integrations"),
    
    # CRITICO: Arquivos Python da raiz que são importados
    (str(ROOT / "sne_radar_web.py"), "."),
    (str(ROOT / "config.py"), "."),
    (str(ROOT / "database_config.py"), "."),
]

# Arquivos opcionais (adicionar apenas se existirem)
optional_files = [
    "extensions.py",
    "telemetry_helpers.py", 
    "models_telemetry.py",
    "multi_timeframe_validator.py",
]
for f in optional_files:
    if (ROOT / f).exists():
        datas.append((str(ROOT / f), "."))

# Filtrar apenas arquivos/diretórios que existem
datas = [(src, dst) for src, dst in datas if Path(src).exists()]

a = Analysis(
    [ENTRY],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # WebView
        "webview",
        "webview.platforms.winforms",  # Windows WebView
        "clr",  # pythonnet para webview no Windows
        
        # Flask & SocketIO
        "flask",
        "flask_socketio",
        "flask_cors",
        "socketio",
        "engineio",
        "engineio.async_drivers.threading",
        
        # Database
        "sqlalchemy",
        "sqlalchemy.ext.declarative",
        
        # Backend principal
        "sne_radar_web",
        "config",
        "database_config",
        "extensions",
        "telemetry_helpers",
        "models_telemetry",
        
        # Monitors
        "monitors",
        "monitors.opportunity_monitor",
        "monitors.pavio_detector",
        
        # Services
        "services",
        "services.ta_summary",
        "services.telegram_notifier",
        "services.advanced_indicators",
        "services.professional_indicators",
        "services.ml_predictions",
        "services.advanced_backtesting",
        "services.alert_system",
        "services.export_system",
        
        # Integrations
        "integrations",
        "integrations.cmc",
        "integrations.coinglass",
        
        # Validators
        "multi_timeframe_validator",
        
        # API Blueprints
        "app.api",
        "app.api.telemetry",
        "app.api.telemetry.routes",
        "app.api.diagnostics",
        "app.api.diagnostics.routes",
        "app.api.health",
        "app.api.health.routes",
        "app.api.lifecycle",
        "app.api.lifecycle.routes",
        "app.api.trading",
        "app.api.trading.routes",
        
        # Dependências comuns que PyInstaller pode não detectar
        "requests",
        "pandas",
        "numpy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos pesados desnecessários
        "matplotlib",
        "tkinter",
        "IPython",
        "jupyter",
        "pytest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SNE_Radar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Produção: sem console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "frontend" / "build" / "icon.ico") if (ROOT / "frontend" / "build" / "icon.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SNE_Radar',
)

