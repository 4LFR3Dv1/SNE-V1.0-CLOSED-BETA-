# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para criar SNE_RADAR.exe no Windows
"""
import os
from pathlib import Path

block_cipher = None

# Diretório raiz do projeto
ROOT_DIR = Path(SPECPATH)

# Verificar se frontend está buildado
FRONTEND_DIST = ROOT_DIR / 'frontend' / 'dist'
if not FRONTEND_DIST.exists():
    print("⚠️ AVISO: frontend/dist não encontrado. Execute: cd frontend && npm run build")

a = Analysis(
    ['sne_desktop.py'],  # Arquivo launcher
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),  # Frontend Vue.js buildado
        # Não incluir 'data' - será criado em %APPDATA%\SNE_RADAR
    ],
    hiddenimports=[
        # Flask e SocketIO
        'flask',
        'flask_socketio',
        'flask_sqlalchemy',
        'flask_login',
        'flask_limiter',
        'flask_wtf',
        'engineio.async_drivers.threading',
        'engineio.async_drivers.gevent',
        
        # pywebview
        'webview',
        'webview.platforms',
        
        # Windows específico
        'win32api',
        'win32con',
        'win32gui',
        'pythoncom',
        'pywintypes',
        
        # Módulos SNE
        'motor_renan',
        'contexto_global',
        'estrutura_mercado',
        'multi_timeframe',
        'confluencia',
        'fluxo_ativo',
        'catalogo_magnetico',
        'padroes_graficos',
        'indicadores',
        'indicadores_avancados',
        'analise_candles_detalhada',
        'gestao_risco_profissional',
        'relatorio_profissional',
        'calcular_suportes_resistencias',
        'niveis_operacionais',
        'database_config',
        'config',
        
        # Dependências científicas
        'pandas',
        'numpy',
        'matplotlib',
        'mplfinance',
        'scipy',
        'sklearn',
        'sqlalchemy',
        'alembic',
        
        # Outros
        'requests',
        'bcrypt',
        'cachetools',
        'pytz',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Não precisamos de Tkinter
        'matplotlib.tests',
        'numpy.tests',
        'pandas.tests',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SNE_RADAR',  # Nome do executável .exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # FALSE = Não abre console (janela preta)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=None,  # Se você tiver um ícone .ico, coloque aqui: 'assets/logo_sne.ico'
    version_file=None,  # Opcional: arquivo de versão .txt
)


