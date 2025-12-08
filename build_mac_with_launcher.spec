# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para criar SNE_RADAR.app no macOS COM LAUNCHER
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
    ['sne_desktop.py'],  # Seu novo arquivo launcher
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),  # Sua pasta Vue buildada
        ('launcher.sh', 'MacOS'),  # Launcher script no diretório MacOS
        ('scanners', 'scanners'),  # ✅ NOVO: Módulos de scanner
        ('notifications', 'notifications'),  # ✅ NOVO: Módulos de notificação
        ('monitors', 'monitors'),  # ✅ NOVO: Módulos de monitor
        ('app', 'app'),  # ✅ NOVO: Incluir módulo app completo (trading, models, etc)
        ('alembic', 'alembic'),  # ✅ NOVO: Migrations do Alembic
        # Não incluir 'data' - será criado em ~/Library/Application Support
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
        
        # macOS específico
        'objc',
        'AppKit',
        'Foundation',
        
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
        
        # ✅ NOVO: Módulos de Scanner e Notificações
        'scanners',
        'scanners.volume_scanner',
        'scanners.pavio_scanner',
        'notifications',
        'notifications.telegram_notifier',
        'notifications.alert_formatter',
        'monitors',
        'monitors.opportunity_monitor',
        'xenos_bot',
        
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
        
        # ✅ NOVO: Trading Automatizado
        'app',
        'app.api',
        'app.api.trading',
        'app.api.trading.routes',
        'app.api.trading.strategies',
        'app.api.trading.execution',
        'app.api.trading.positions',
        'app.api.trading.portfolio',
        'app.api.trading.compliance',
        'app.api.trading.emergency',
        'app.services',
        'app.services.executors',
        'app.services.executors.exchange_adapter',
        'app.services.executors.bybit_executor',
        'app.services.order_manager',
        'app.services.risk_manager',
        'app.services.portfolio_manager',
        'app.services.reconciliation_engine',
        'app.services.strategy_engine',
        'app.services.compliance_engine',
        'app.models.trading_models',
        'app.tasks.order_tasks',
        'app.tasks.reconciliation_tasks',
        
        # ✅ NOVO: Dependências de Trading
        'pybit',
        'pybit.unified_trading',
        'celery',
        'redis',
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
    [],
    exclude_binaries=True,
    name='SNE_RADAR',  # Nome do Processo
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # FALSE = Não abre terminal preto atrás
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ISSO CRIA O .APP (BUNDLE DE MAC) COM LAUNCHER
app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='SNE_RADAR.app',  # O arquivo final que vai pra pasta Applications
    icon='assets/logo_sne.icns',
    bundle_identifier='com.sne.radar',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleName': 'SNE RADAR',
        'CFBundleDisplayName': 'SNE RADAR - Sistema Neural Estratégico',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2025 SNE Radar',
        'LSMinimumSystemVersion': '10.13',  # macOS High Sierra
        'LSUIElement': '0',  # 0 = Mostra na Dock, 1 = Não mostra (background app)
        'NSRequiresAquaSystemAppearance': 'False',
        'NSHighResolutionCapable': 'True',
        'LSApplicationCategoryType': 'public.app-category.finance',  # Categoria Finance
        'NSHumanReadableCopyright': '© 2025 SNE Radar',
        # IMPORTANTE: Usar o binário Python como executável principal
        'CFBundleExecutable': 'SNE_RADAR',  # <-- Binário Python (não script shell)
        'LSEnvironment': {
            'PYTHONUNBUFFERED': '1',
        },
    },
)


