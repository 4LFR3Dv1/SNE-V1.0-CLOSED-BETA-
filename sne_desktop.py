#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNE RADAR Desktop - Launcher Nativo
Cria uma janela nativa do sistema operacional que renderiza o dashboard Vue.js
"""
import os
import sys
import threading
import time
from pathlib import Path

# Importar pywebview (a mágica acontece aqui)
try:
    import webview
except ImportError:
    print("❌ pywebview não instalado. Execute: pip install pywebview")
    sys.exit(1)

# Configurações de Ambiente (Stand-alone)
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável compilado (PyInstaller)
    # No macOS, sys.executable aponta para o executável dentro do .app bundle
    # Precisamos ir para o diretório do .app (Contents/MacOS -> Contents -> .app)
    executable_path = Path(sys.executable)
    if 'Contents/MacOS' in str(executable_path):
        # Estamos dentro de um .app bundle
        ROOT_DIR = executable_path.parent.parent.parent  # Volta para o .app
    else:
        ROOT_DIR = executable_path.parent
else:
    # Se estiver rodando como script python
    ROOT_DIR = Path(__file__).parent

# Configurar variáveis de ambiente para modo standalone
os.environ['FLASK_ENV'] = 'production'
os.environ['STANDALONE_MODE'] = 'true'

# Configurar banco de dados SQLite
# No modo bundle, criar dados em diretório do usuário (OS-agnóstico)
if getattr(sys, 'frozen', False):
    # Modo bundle - usar diretório do usuário
    import os
    import platform
    home = Path.home()
    
    # Detectar sistema operacional
    system = platform.system()
    if system == 'Darwin':  # macOS
        app_data_dir = home / 'Library' / 'Application Support' / 'SNE_RADAR'
    elif system == 'Windows':  # Windows
        app_data_dir = Path(os.getenv('APPDATA', str(home))) / 'SNE_RADAR'
    else:  # Linux e outros
        app_data_dir = home / '.local' / 'share' / 'SNE_RADAR'
    
    app_data_dir.mkdir(parents=True, exist_ok=True)
    data_dir = app_data_dir
    logs_dir = app_data_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
else:
    # Modo desenvolvimento - usar diretório do projeto
    data_dir = ROOT_DIR / 'data'
    logs_dir = ROOT_DIR / 'logs'

data_dir.mkdir(exist_ok=True)
db_path = data_dir / 'sne_radar.db'
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

# Adicionar diretório raiz ao path para imports
sys.path.insert(0, str(ROOT_DIR))

# No modo bundle, garantir que os módulos estão acessíveis
if getattr(sys, 'frozen', False):
    # PyInstaller: adicionar diretório Resources ao path
    if hasattr(sys, '_MEIPASS'):
        # Durante execução do bundle, módulos estão em _MEIPASS
        sys.path.insert(0, str(Path(sys._MEIPASS)))
        print(f"✅ Modo bundle detectado: {sys._MEIPASS}")
    else:
        # Fallback: tentar encontrar Resources
        resources_path = ROOT_DIR / 'Contents' / 'Resources'
        if resources_path.exists():
            sys.path.insert(0, str(resources_path))
            print(f"✅ Adicionado Resources ao path: {resources_path}")
    
    # Garantir que o diretório raiz está no path
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
        print(f"✅ Adicionado ROOT_DIR ao path: {ROOT_DIR}")
    
    # Adicionar também Contents/Resources ao path (onde PyInstaller coloca os dados)
    resources_path = ROOT_DIR / 'Contents' / 'Resources'
    if resources_path.exists() and str(resources_path) not in sys.path:
        sys.path.insert(0, str(resources_path))
        print(f"✅ Adicionado Contents/Resources ao path: {resources_path}")

# Importar app Flask (aguardar um pouco para garantir que os módulos estão carregados)
try:
    from sne_radar_web import app, socketio
    print("✅ Flask app importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Flask app: {e}")
    print("💡 Certifique-se de que sne_radar_web.py existe na raiz do projeto")
    sys.exit(1)

def start_server():
    """Inicia o Flask em background sem bloquear a janela"""
    print("🚀 Iniciando servidor Flask em background...")
    try:
        # use_reloader=False é vital para não bugar a thread
        socketio.run(
            app, 
            host='127.0.0.1', 
            port=9999, 
            debug=False, 
            use_reloader=False,
            allow_unsafe_werkzeug=True  # Necessário para pywebview
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()

def verify_server_ready(max_attempts=30):
    """Espera o servidor subir antes de carregar a janela"""
    import requests
    url = 'http://127.0.0.1:9999'
    
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print("✅ Servidor Flask está pronto!")
                return True
        except:
            time.sleep(0.5)
    
    print("⚠️ Servidor não respondeu, mas continuando...")
    return False

def start_background_services():
    """Inicia serviços em background (scanners, monitors)"""
    try:
        print("🔄 Tentando importar OpportunityMonitor...")
        print(f"   ROOT_DIR: {ROOT_DIR}")
        print(f"   sys.path[0]: {sys.path[0] if sys.path else 'N/A'}")
        
        # Adicionar diretório ao path explicitamente
        # No modo bundle, os módulos estão em Contents/Resources
        if getattr(sys, 'frozen', False):
            # Modo bundle: procurar em Contents/Resources
            monitors_path = ROOT_DIR / 'Contents' / 'Resources' / 'monitors'
            if monitors_path.exists():
                sys.path.insert(0, str(monitors_path.parent))
                print(f"   ✅ Adicionado ao path (bundle): {monitors_path.parent}")
            else:
                print(f"   ⚠️ Diretório monitors não encontrado (bundle): {monitors_path}")
                # Tentar também _MEIPASS
                if hasattr(sys, '_MEIPASS'):
                    meipass_monitors = Path(sys._MEIPASS) / 'monitors'
                    if meipass_monitors.exists():
                        sys.path.insert(0, str(Path(sys._MEIPASS)))
                        print(f"   ✅ Adicionado _MEIPASS ao path: {sys._MEIPASS}")
        else:
            # Modo desenvolvimento: procurar em ROOT_DIR
            monitors_path = ROOT_DIR / 'monitors'
            if monitors_path.exists():
                sys.path.insert(0, str(monitors_path.parent))
                print(f"   ✅ Adicionado ao path (dev): {monitors_path.parent}")
            else:
                print(f"   ⚠️ Diretório monitors não encontrado (dev): {monitors_path}")
        
        from monitors.opportunity_monitor import OpportunityMonitor
        print("   ✅ OpportunityMonitor importado com sucesso")
        
        import sne_radar_web
        print("   ✅ sne_radar_web importado com sucesso")
        
        # Configuração do monitor
        print("🔄 Criando instância do monitor...")
        monitor = OpportunityMonitor(
            symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT'],
            scan_interval=60,  # 1 minuto
            enable_volume_scanner=True,  # Fase 1: RVOL > 2.0
            enable_pavio_scanner=True    # Fase 2: Volume M30 + RSI M5 + Wick ✅ ATIVADO POR PADRÃO
        )
        print("   ✅ Monitor criado com sucesso")
        
        # Compartilhar monitor com sne_radar_web.py para API
        sne_radar_web.opportunity_monitor = monitor
        print("   ✅ Monitor compartilhado com sne_radar_web")
        
        # Iniciar monitor em thread separada
        print("🔄 Iniciando monitor...")
        monitor.start()
        
        print("✅ Monitor de oportunidades iniciado em background")
        print(f"   Status: {'Rodando' if monitor.running else 'Parado'}")
        
        # Enviar mensagem de inicialização
        try:
            if monitor.notifier:
                print("📤 Enviando mensagem de inicialização...")
                mode = "Bundle (.app)" if getattr(sys, 'frozen', False) else "Desenvolvimento"
                monitor.notifier.send_startup_message(mode=mode)
        except Exception as e:
            print(f"⚠️ Erro ao enviar mensagem de inicialização: {e}")
            # Não bloquear se falhar
        
        return monitor
        
    except ImportError as e:
        print(f"❌ Erro de importação ao iniciar monitor: {e}")
        import traceback
        traceback.print_exc()
        print(f"   sys.path: {sys.path[:5]}")
        return None
    except Exception as e:
        print(f"❌ Erro ao iniciar monitor: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_window():
    """Cria a janela nativa do sistema operacional"""
    
    # No modo bundle, os arquivos estão em Contents/Resources
    if getattr(sys, 'frozen', False):
        # PyInstaller coloca os dados em _MEIPASS durante execução
        # Mas os arquivos estáticos estão em Contents/Resources
        if hasattr(sys, '_MEIPASS'):
            # Durante execução do bundle
            frontend_dist = Path(sys._MEIPASS) / 'frontend' / 'dist' / 'index.html'
        else:
            # Fallback
            frontend_dist = ROOT_DIR / 'Contents' / 'Resources' / 'frontend' / 'dist' / 'index.html'
    else:
        # Modo desenvolvimento
        frontend_dist = ROOT_DIR / 'frontend' / 'dist' / 'index.html'
    
    frontend_src = ROOT_DIR / 'frontend' / 'src' if not getattr(sys, 'frozen', False) else None
    
    # URL do dashboard
    if frontend_dist.exists():
        # Frontend buildado - usar Flask
        url = 'http://127.0.0.1:9999'
        print("✅ Frontend buildado encontrado - usando Flask")
    elif frontend_src.exists():
        # Frontend não buildado mas src existe - tentar Vite dev server
        print("⚠️ Frontend não buildado")
        print("💡 Tentando usar Vite dev server (se estiver rodando)...")
        print("💡 Para buildar: cd frontend && npm run build")
        print("💡 Ou inicie Vite: cd frontend && npm run dev")
        
        # Verificar se Vite está rodando
        import requests
        vite_url = 'http://127.0.0.1:5173'
        try:
            response = requests.get(vite_url, timeout=1)
            if response.status_code == 200:
                print(f"✅ Vite dev server encontrado em {vite_url}")
                url = vite_url
            else:
                url = 'http://127.0.0.1:9999'
        except:
            print("⚠️ Vite não está rodando - usando Flask (pode não funcionar)")
            url = 'http://127.0.0.1:9999'
    else:
        # Nenhum frontend encontrado
        print("❌ Frontend não encontrado!")
        print("💡 Execute: cd frontend && npm install && npm run build")
        url = 'http://127.0.0.1:9999'
    
    # Configurações da Janela Nativa
    # Isso remove a cara de "site" e deixa com cara de "app"
    print(f"🔗 URL que será carregada: {url}")
    
    try:
        # No macOS, pode precisar de configurações específicas
        window_kwargs = {
            'title': 'SNE RADAR - Sistema Neural Estratégico',
            'url': url,
            'width': 1400,
            'height': 900,
            'min_size': (1024, 768),
            'resizable': True,
            'background_color': '#0a0a0a',
            'text_select': True,
            'fullscreen': False,
        }
        
        # Adicionar configurações específicas do macOS se necessário
        import platform
        if platform.system() == 'Darwin':  # macOS
            # No macOS, algumas opções podem não funcionar
            pass
        
        window = webview.create_window(**window_kwargs)
        print(f"✅ Janela criada com sucesso")
        print(f"   Título: {window_kwargs['title']}")
        print(f"   URL: {url}")
        print(f"   Tamanho: {window_kwargs['width']}x{window_kwargs['height']}")
        return window
    except Exception as e:
        print(f"❌ Erro ao criar janela: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    import sys
    
    # No macOS, quando executado como .app, pode não ter stdout/stderr
    # Redirecionar para arquivo de log se necessário
    if getattr(sys, 'frozen', False):
        # Usar diretório de dados do usuário para logs
        log_file = logs_dir / 'sne_desktop.log'
        log_file.parent.mkdir(exist_ok=True)
        
        # Redirecionar stdout e stderr para arquivo de log
        class TeeOutput:
            def __init__(self, *files):
                self.files = files
            def write(self, obj):
                for f in self.files:
                    f.write(obj)
                    f.flush()
            def flush(self):
                for f in self.files:
                    f.flush()
        
        # Abrir arquivo de log em modo append
        log_file_handle = open(log_file, 'a', encoding='utf-8')
        
        # Criar wrapper que escreve tanto no stdout original quanto no arquivo
        # Mas manter stdout original para não quebrar webview
        import sys
        if hasattr(sys, '__stdout__'):
            sys.stdout = TeeOutput(sys.__stdout__, log_file_handle)
        if hasattr(sys, '__stderr__'):
            sys.stderr = TeeOutput(sys.__stderr__, log_file_handle)
        
        print("=" * 60)
        print(f"📝 Logs sendo salvos em: {log_file}")
        print("=" * 60)
    
    try:
        print("=" * 60)
        print("🚀 SNE RADAR - Sistema Neural Estratégico")
        print("📦 Modo Desktop Nativo")
        print(f"🔧 Modo: {'Bundle (.app)' if getattr(sys, 'frozen', False) else 'Desenvolvimento'}")
        print("=" * 60)
    except Exception as e:
        # Se não conseguir printar, pelo menos tentar logar erro
        try:
            with open(logs_dir / 'sne_desktop_error.log', 'a') as f:
                f.write(f"Erro ao inicializar: {e}\n")
        except:
            pass
    
    # 1. Criar pasta de dados se não existir (já criado acima)
    print(f"📁 Diretório de dados: {data_dir}")
    print(f"💾 Banco de dados: {db_path}")
    print(f"📝 Logs: {logs_dir}")
    
    # 2. Iniciar o servidor em uma Thread separada (Daemon)
    # IMPORTANTE: Thread daemon para não bloquear a thread principal
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    print("✅ Thread do servidor iniciada (daemon)")
    
    # ✅ NOVO: Iniciar monitor de oportunidades em background
    print("🔄 Iniciando serviços em background...")
    monitor = start_background_services()
    
    if monitor is None:
        print("⚠️ Monitor não foi iniciado, mas continuando...")
        print("💡 O monitor pode ser iniciado manualmente via API: /api/v1/notifications/monitor/start")
    else:
        print(f"✅ Monitor iniciado: {monitor.running}")
        
        # Enviar mensagem de inicialização
        try:
            if monitor.notifier:
                print("📤 Enviando mensagem de inicialização...")
                mode = "Bundle (.app)" if getattr(sys, 'frozen', False) else "Desenvolvimento"
                monitor.notifier.send_startup_message(mode=mode)
        except Exception as e:
            print(f"⚠️ Erro ao enviar mensagem de inicialização: {e}")
            # Não bloquear se falhar
    
    # 3. Aguardar servidor estar pronto (opcional, mas recomendado)
    print("⏳ Aguardando servidor Flask iniciar...")
    server_ready = verify_server_ready()
    
    # Verificar se frontend está buildado
    frontend_dist = ROOT_DIR / 'frontend' / 'dist' / 'index.html'
    if not frontend_dist.exists():
        print("")
        print("=" * 60)
        print("⚠️  ATENÇÃO: Frontend não está buildado!")
        print("=" * 60)
        print("")
        print("Para usar o modo desktop, você precisa buildar o frontend:")
        print("")
        print("  1. cd frontend")
        print("  2. npm install  (se ainda não instalou)")
        print("  3. npm run build")
        print("  4. cd ..")
        print("  5. python3 sne_desktop.py")
        print("")
        print("OU use o modo desenvolvimento:")
        print("")
        print("  Terminal 1: cd frontend && npm run dev")
        print("  Terminal 2: python3 sne_desktop.py")
        print("")
        print("=" * 60)
        print("")
        print("💡 Continuando mesmo assim... (pode não funcionar)")
        print("")
    
    # 4. Inicializar NSApplication ANTES de criar janela (CRÍTICO no macOS)
    import platform
    import threading
    
    if platform.system() == 'Darwin':
        print("🔧 Inicializando NSApplication no macOS...")
        try:
            import AppKit
            # Obter ou criar NSApplication
            app = AppKit.NSApplication.sharedApplication()
            
            # Configurar política de ativação (deve ser feito ANTES de criar janelas)
            app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
            
            # CRÍTICO: Finalizar inicialização do app
            if not app.isRunning():
                app.finishLaunching()
                print("✅ NSApplication finishLaunching() chamado")
            
            print("✅ NSApplication inicializado e pronto")
            
        except Exception as e:
            print(f"⚠️ Erro ao inicializar NSApplication: {e}")
            import traceback
            traceback.print_exc()
            # Continuar mesmo com erro - pode funcionar sem NSApplication explícito
    
    # Verificar se estamos na thread principal (CRÍTICO para webview)
    if threading.current_thread() != threading.main_thread():
        print("❌ ERRO CRÍTICO: Não estamos na thread principal!")
        print("❌ Webview não funcionará fora da thread principal")
        raise RuntimeError("webview.start() deve ser chamado na thread principal")
    
    print("✅ Thread principal confirmada")
    
    # 5. Criar e iniciar a janela
    print("🪟 Criando janela nativa...")
    
    try:
        window = create_window()
        print(f"✅ Janela criada: {window}")
        
        # Ativar app DEPOIS de criar janela
        if platform.system() == 'Darwin':
            try:
                import AppKit
                app = AppKit.NSApplication.sharedApplication()
                
                # Garantir que o app está rodando
                if not app.isRunning():
                    app.finishLaunching()
                    print("✅ NSApplication finishLaunching() chamado após criar janela")
                
                # Ativar app e trazer para frente
                app.activateIgnoringOtherApps_(True)
                print("✅ App ativado no macOS (activateIgnoringOtherApps)")
                
                # Delay aumentado para dar tempo do macOS processar a ativação
                # Este delay é crítico para que a janela apareça
                time.sleep(0.8)  # Aumentado de 0.3 para 0.8 segundos
                
            except Exception as e:
                print(f"⚠️ Erro ao ativar app: {e}")
                import traceback
                traceback.print_exc()
                # Continuar mesmo com erro - webview pode funcionar sem isso
        
        # 6. Inicia o Loop da Interface Gráfica
        # CRÍTICO: webview.start() DEVE ser chamado na thread principal
        # e DEVE ser a última coisa antes do fim do script
        print("✅ Iniciando interface gráfica...")
        print("💡 URL: http://127.0.0.1:9999")
        print("🚀 Iniciando webview...")
        print("💡 Aguarde alguns segundos para a janela aparecer...")
        
        # Verificação final antes de iniciar webview
        if platform.system() == 'Darwin':
            try:
                import AppKit
                app = AppKit.NSApplication.sharedApplication()
                if not app.isRunning():
                    print("⚠️ NSApplication não está rodando, tentando iniciar...")
                    app.finishLaunching()
            except:
                pass
        
        # webview.start() bloqueia aqui até a janela fechar
        # CRÍTICO: No macOS bundle, webview.start() pode não funcionar se:
        # 1. NSApplication não estiver completamente inicializado
        # 2. A thread principal não estiver correta
        # 3. O app não estiver ativado
        
        print("⏳ Preparando para iniciar webview...")
        
        # Verificação final e ativação no macOS
        if platform.system() == 'Darwin':
            try:
                import AppKit
                app = AppKit.NSApplication.sharedApplication()
                
                # Garantir que está rodando
                if not app.isRunning():
                    print("⚠️ NSApplication não está rodando, iniciando...")
                    app.finishLaunching()
                
                # Ativar novamente antes de webview.start()
                app.activateIgnoringOtherApps_(True)
                
                # Processar eventos pendentes do macOS
                try:
                    run_loop = AppKit.NSRunLoop.currentRunLoop()
                    run_loop.runMode_beforeDate_(AppKit.NSDefaultRunLoopMode, AppKit.NSDate.dateWithTimeIntervalSinceNow_(0.1))
                except:
                    # Se não conseguir processar eventos, continuar mesmo assim
                    pass
                
                print("✅ NSApplication verificado e ativado antes de webview.start()")
                
            except Exception as e:
                print(f"⚠️ Erro ao preparar NSApplication: {e}")
                import traceback
                traceback.print_exc()
        
        # Delay final antes de iniciar webview
        print("⏳ Aguardando 1.5 segundos para garantir que tudo está pronto...")
        time.sleep(1.5)
        
        print("🚀 Chamando webview.start()...")
        print("💡 Se a janela não aparecer, verifique os logs acima para erros")
        
        try:
            # No modo bundle, usar debug=False para evitar problemas com stdout/stderr
            # Mas podemos tentar debug=True se necessário para diagnóstico
            webview.start(debug=False)
        except Exception as e:
            print(f"❌ Erro crítico ao iniciar webview: {e}")
            import traceback
            traceback.print_exc()
            
            # Salvar erro detalhado
            try:
                error_log = logs_dir / 'webview_start_error.log'
                with open(error_log, 'w') as f:
                    f.write(f"Erro ao iniciar webview: {e}\n")
                    f.write(traceback.format_exc())
                print(f"📝 Erro detalhado salvo em: {error_log}")
            except:
                pass
            
            raise  # Re-raise para que o usuário veja o erro
        
        print("✅ webview.start() retornou (janela fechada)")
        
    except KeyboardInterrupt:
        print("\n👋 Interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao criar/iniciar janela: {e}")
        import traceback
        traceback.print_exc()
        
        # Salvar erro em arquivo
        try:
            error_log = logs_dir / 'window_error.log'
            with open(error_log, 'w') as f:
                f.write(f"Erro ao criar/iniciar janela: {e}\n")
                f.write(traceback.format_exc())
            print(f"📝 Erro salvo em: {error_log}")
        except:
            pass
        
        # NÃO abrir navegador - apenas informar erro
        print("")
        print("=" * 60)
        print("❌ ERRO: Não foi possível abrir a janela nativa")
        print("=" * 60)
        print("")
        print("💡 Verifique os logs em:")
        print(f"   {logs_dir}/window_error.log")
        print("")
        print("💡 Servidor Flask está rodando em http://127.0.0.1:9999")
        print("💡 Você pode acessar manualmente no navegador")
        print("")
        
        # Manter servidor rodando para debug
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Encerrando servidor...")
        
    except KeyboardInterrupt:
        print("\n👋 Interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao criar/iniciar janela: {e}")
        import traceback
        traceback.print_exc()
        
        # Salvar erro em arquivo
        try:
            error_log = logs_dir / 'error.log'
            with open(error_log, 'w') as f:
                f.write(f"Erro: {e}\n")
                f.write(traceback.format_exc())
            print(f"📝 Erro salvo em: {error_log}")
        except:
            pass
        
        # Se houver erro ao criar janela, apenas informar
        # NÃO abrir navegador automaticamente - a janela deve abrir normalmente
        print("💡 Erro ao criar janela")
        print("💡 Servidor Flask está rodando em http://127.0.0.1:9999")
        print("💡 Você pode abrir manualmente no navegador se desejar")
        print("💡 Pressione Ctrl+C para parar o servidor")
        
        # Manter o processo vivo para o servidor continuar rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Encerrando...")
    
    print("👋 SNE RADAR encerrado. Até logo!")

