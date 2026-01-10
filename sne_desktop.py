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
import io
from pathlib import Path

#  CRITICAL: Configurar para modo windowed no Windows (sem console)
# Quando console=False no PyInstaller, stdout/stderr so None
_log_file = None

# IMPORTANTE: Salvar print original ANTES de substituir
import builtins
_original_print = builtins.print

def safe_print(*args, **kwargs):
    """Print seguro que funciona mesmo sem console (windowed mode)"""
    global _log_file
    
    # Tentar converter para string removendo emojis se necessrio
    try:
        msg = ' '.join(str(arg) for arg in args)
    except:
        msg = "Log message"
    
    # Se stdout existe e funciona, usar o print ORIGINAL (evita recursao)
    if sys.stdout is not None:
        try:
            # Limpar caracteres problematicos antes de printar
            clean_msg = msg.encode('cp1252', 'replace').decode('cp1252')
            _original_print(clean_msg, **kwargs)
            return
        except (UnicodeEncodeError, OSError, AttributeError):
            pass  # Fallback para arquivo
    
    # Fallback: escrever em arquivo de log
    try:
        if _log_file is None:
            # Criar arquivo de log no diretrio do usurio
            if getattr(sys, 'frozen', False):
                if sys.platform == 'win32':
                    log_dir = Path(os.getenv('APPDATA', Path.home())) / 'SNE_RADAR' / 'logs'
                else:
                    log_dir = Path.home() / '.local' / 'share' / 'SNE_RADAR' / 'logs'
                log_dir.mkdir(parents=True, exist_ok=True)
                _log_file = open(log_dir / 'sne_desktop.log', 'a', encoding='utf-8')
        if _log_file:
            # Remover emojis para compatibilidade
            clean_msg = msg.encode('ascii', 'ignore').decode('ascii')
            _log_file.write(clean_msg + '\n')
            _log_file.flush()
    except:
        pass  # Silenciosamente ignorar se tudo falhar

# Substituir print global para modo seguro
builtins.print = safe_print

# Importar pywebview (a mgica acontece aqui)
try:
    import webview
except ImportError:
    safe_print("pywebview nao instalado. Execute: pip install pywebview")
    sys.exit(1)

# Configuraes de Ambiente (Stand-alone)
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executvel compilado (PyInstaller)
    # No macOS, sys.executable aponta para o executvel dentro do .app bundle
    # Precisamos ir para o diretrio do .app (Contents/MacOS -> Contents -> .app)
    executable_path = Path(sys.executable)
    if 'Contents/MacOS' in str(executable_path):
        # Estamos dentro de um .app bundle
        ROOT_DIR = executable_path.parent.parent.parent  # Volta para o .app
    else:
        ROOT_DIR = executable_path.parent
else:
    # Se estiver rodando como script python
    ROOT_DIR = Path(__file__).parent

# Configurar variveis de ambiente para modo standalone
os.environ['FLASK_ENV'] = 'production'
os.environ['STANDALONE_MODE'] = 'true'

# Configurar banco de dados SQLite
# No modo bundle, criar dados em diretrio do usurio (OS-agnstico)
if getattr(sys, 'frozen', False):
    # Modo bundle - usar diretrio do usurio
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
    # Modo desenvolvimento - usar diretrio do projeto
    data_dir = ROOT_DIR / 'data'
    logs_dir = ROOT_DIR / 'logs'

data_dir.mkdir(exist_ok=True)
db_path = data_dir / 'sne_radar.db'
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

# Adicionar diretrio raiz ao path para imports
sys.path.insert(0, str(ROOT_DIR))

# No modo bundle, garantir que os mdulos esto acessveis
if getattr(sys, 'frozen', False):
    # PyInstaller: adicionar diretrio Resources ao path
    if hasattr(sys, '_MEIPASS'):
        # Durante execuo do bundle, mdulos esto em _MEIPASS
        sys.path.insert(0, str(Path(sys._MEIPASS)))
        print(f" Modo bundle detectado: {sys._MEIPASS}")
    else:
        # Fallback: tentar encontrar Resources
        resources_path = ROOT_DIR / 'Contents' / 'Resources'
        if resources_path.exists():
            sys.path.insert(0, str(resources_path))
            print(f" Adicionado Resources ao path: {resources_path}")
    
    # Garantir que o diretrio raiz est no path
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
        print(f" Adicionado ROOT_DIR ao path: {ROOT_DIR}")
    
    # Adicionar tambm Contents/Resources ao path (onde PyInstaller coloca os dados)
    resources_path = ROOT_DIR / 'Contents' / 'Resources'
    if resources_path.exists() and str(resources_path) not in sys.path:
        sys.path.insert(0, str(resources_path))
        print(f" Adicionado Contents/Resources ao path: {resources_path}")

# Importar app Flask (aguardar um pouco para garantir que os mdulos esto carregados)
try:
    from sne_radar_web import app, socketio
    print(" Flask app importado com sucesso")
except ImportError as e:
    print(f" Erro ao importar Flask app: {e}")
    print(" Certifique-se de que sne_radar_web.py existe na raiz do projeto")
    sys.exit(1)

def start_server():
    """Inicia o Flask em background sem bloquear a janela"""
    print(" Iniciando servidor Flask em background...")
    try:
        # use_reloader=False  vital para no bugar a thread
        socketio.run(
            app, 
            host='127.0.0.1', 
            port=9999, 
            debug=False, 
            use_reloader=False,
            allow_unsafe_werkzeug=True  # Necessrio para pywebview
        )
    except Exception as e:
        print(f" Erro ao iniciar servidor: {e}")
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
                print(" Servidor Flask est pronto!")
                return True
        except:
            time.sleep(0.5)
    
    print(" Servidor no respondeu, mas continuando...")
    return False

def start_background_services():
    """Inicia servios em background (scanners, monitors)"""
    try:
        print(" Tentando importar OpportunityMonitor...")
        print(f"   ROOT_DIR: {ROOT_DIR}")
        print(f"   sys.path[0]: {sys.path[0] if sys.path else 'N/A'}")
        
        # Adicionar diretrio ao path explicitamente
        # No modo bundle, os mdulos esto em Contents/Resources
        if getattr(sys, 'frozen', False):
            # Modo bundle: procurar em Contents/Resources
            monitors_path = ROOT_DIR / 'Contents' / 'Resources' / 'monitors'
            if monitors_path.exists():
                sys.path.insert(0, str(monitors_path.parent))
                print(f"    Adicionado ao path (bundle): {monitors_path.parent}")
            else:
                print(f"    Diretrio monitors no encontrado (bundle): {monitors_path}")
                # Tentar tambm _MEIPASS
                if hasattr(sys, '_MEIPASS'):
                    meipass_monitors = Path(sys._MEIPASS) / 'monitors'
                    if meipass_monitors.exists():
                        sys.path.insert(0, str(Path(sys._MEIPASS)))
                        print(f"    Adicionado _MEIPASS ao path: {sys._MEIPASS}")
        else:
            # Modo desenvolvimento: procurar em ROOT_DIR
            monitors_path = ROOT_DIR / 'monitors'
            if monitors_path.exists():
                sys.path.insert(0, str(monitors_path.parent))
                print(f"    Adicionado ao path (dev): {monitors_path.parent}")
            else:
                print(f"    Diretrio monitors no encontrado (dev): {monitors_path}")
        
        from monitors.opportunity_monitor import OpportunityMonitor
        print("    OpportunityMonitor importado com sucesso")
        
        import sne_radar_web
        print("    sne_radar_web importado com sucesso")
        
        # Configurao do monitor
        print(" Criando instncia do monitor...")
        monitor = OpportunityMonitor(
            symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT'],
            scan_interval=60,  # 1 minuto
            enable_volume_scanner=True,  # Fase 1: RVOL > 2.0
            enable_pavio_scanner=True    # Fase 2: Volume M30 + RSI M5 + Wick  ATIVADO POR PADRO
        )
        print("    Monitor criado com sucesso")
        
        # Compartilhar monitor com sne_radar_web.py para API
        sne_radar_web.opportunity_monitor = monitor
        print("    Monitor compartilhado com sne_radar_web")
        
        # Iniciar monitor em thread separada
        print(" Iniciando monitor...")
        monitor.start()
        
        print(" Monitor de oportunidades iniciado em background")
        print(f"   Status: {'Rodando' if monitor.running else 'Parado'}")
        
        # Enviar mensagem de inicializao
        try:
            if monitor.notifier:
                print(" Enviando mensagem de inicializao...")
                mode = "Bundle (.app)" if getattr(sys, 'frozen', False) else "Desenvolvimento"
                monitor.notifier.send_startup_message(mode=mode)
        except Exception as e:
            print(f" Erro ao enviar mensagem de inicializao: {e}")
            # No bloquear se falhar
        
        return monitor
        
    except ImportError as e:
        print(f" Erro de importao ao iniciar monitor: {e}")
        import traceback
        traceback.print_exc()
        print(f"   sys.path: {sys.path[:5]}")
        return None
    except Exception as e:
        print(f" Erro ao iniciar monitor: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_window():
    """Cria a janela nativa do sistema operacional"""
    
    # No modo bundle, os arquivos esto em Contents/Resources
    if getattr(sys, 'frozen', False):
        # PyInstaller coloca os dados em _MEIPASS durante execuo
        # Mas os arquivos estticos esto em Contents/Resources
        if hasattr(sys, '_MEIPASS'):
            # Durante execuo do bundle
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
        print(" Frontend buildado encontrado - usando Flask")
    elif frontend_src.exists():
        # Frontend no buildado mas src existe - tentar Vite dev server
        print(" Frontend no buildado")
        print(" Tentando usar Vite dev server (se estiver rodando)...")
        print(" Para buildar: cd frontend && npm run build")
        print(" Ou inicie Vite: cd frontend && npm run dev")
        
        # Verificar se Vite est rodando
        import requests
        vite_url = 'http://127.0.0.1:5173'
        try:
            response = requests.get(vite_url, timeout=1)
            if response.status_code == 200:
                print(f" Vite dev server encontrado em {vite_url}")
                url = vite_url
            else:
                url = 'http://127.0.0.1:9999'
        except:
            print(" Vite no est rodando - usando Flask (pode no funcionar)")
            url = 'http://127.0.0.1:9999'
    else:
        # Nenhum frontend encontrado
        print(" Frontend no encontrado!")
        print(" Execute: cd frontend && npm install && npm run build")
        url = 'http://127.0.0.1:9999'
    
    # Configuraes da Janela Nativa
    # Isso remove a cara de "site" e deixa com cara de "app"
    print(f" URL que ser carregada: {url}")
    
    try:
        # No macOS, pode precisar de configuraes especficas
        window_kwargs = {
            'title': 'SNE RADAR - Sistema Neural Estratgico',
            'url': url,
            'width': 1400,
            'height': 900,
            'min_size': (1024, 768),
            'resizable': True,
            'background_color': '#0a0a0a',
            'text_select': True,
            'fullscreen': False,
        }
        
        # Adicionar configuraes especficas do macOS se necessrio
        import platform
        if platform.system() == 'Darwin':  # macOS
            # No macOS, algumas opes podem no funcionar
            pass
        
        window = webview.create_window(**window_kwargs)
        print(f" Janela criada com sucesso")
        print(f"   Ttulo: {window_kwargs['title']}")
        print(f"   URL: {url}")
        print(f"   Tamanho: {window_kwargs['width']}x{window_kwargs['height']}")
        return window
    except Exception as e:
        print(f" Erro ao criar janela: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    import sys
    
    # No macOS, quando executado como .app, pode no ter stdout/stderr
    # Redirecionar para arquivo de log se necessrio
    if getattr(sys, 'frozen', False):
        # Usar diretrio de dados do usurio para logs
        log_file = logs_dir / 'sne_desktop.log'
        log_file.parent.mkdir(exist_ok=True)
        
        # Redirecionar stdout e stderr para arquivo de log
        class TeeOutput:
            def __init__(self, *files):
                # Filtrar None (quando console=False, __stdout__ é None)
                self.files = [f for f in files if f is not None]
            def write(self, obj):
                for f in self.files:
                    try:
                        f.write(obj)
                        f.flush()
                    except:
                        pass  # Ignorar erros de escrita
            def flush(self):
                for f in self.files:
                    try:
                        f.flush()
                    except:
                        pass
        
        # Abrir arquivo de log em modo append
        log_file_handle = open(log_file, 'a', encoding='utf-8')
        
        # Criar wrapper que escreve tanto no stdout original quanto no arquivo
        # Filtrar None quando console=False
        import sys
        original_stdout = sys.__stdout__ if hasattr(sys, '__stdout__') and sys.__stdout__ is not None else None
        original_stderr = sys.__stderr__ if hasattr(sys, '__stderr__') and sys.__stderr__ is not None else None
        
        sys.stdout = TeeOutput(original_stdout, log_file_handle)
        sys.stderr = TeeOutput(original_stderr, log_file_handle)
        
        print("=" * 60)
        print(f" Logs sendo salvos em: {log_file}")
        print("=" * 60)
    
    try:
        print("=" * 60)
        print(" SNE RADAR - Sistema Neural Estratgico")
        print(" Modo Desktop Nativo")
        print(f" Modo: {'Bundle (.app)' if getattr(sys, 'frozen', False) else 'Desenvolvimento'}")
        print("=" * 60)
    except Exception as e:
        # Se no conseguir printar, pelo menos tentar logar erro
        try:
            with open(logs_dir / 'sne_desktop_error.log', 'a') as f:
                f.write(f"Erro ao inicializar: {e}\n")
        except:
            pass
    
    # 1. Criar pasta de dados se no existir (j criado acima)
    print(f" Diretrio de dados: {data_dir}")
    print(f" Banco de dados: {db_path}")
    print(f" Logs: {logs_dir}")
    
    # 2. Iniciar o servidor em uma Thread separada (Daemon)
    # IMPORTANTE: Thread daemon para no bloquear a thread principal
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    print(" Thread do servidor iniciada (daemon)")
    
    #  NOVO: Iniciar monitor de oportunidades em background
    print(" Iniciando servios em background...")
    monitor = start_background_services()
    
    if monitor is None:
        print(" Monitor no foi iniciado, mas continuando...")
        print(" O monitor pode ser iniciado manualmente via API: /api/v1/notifications/monitor/start")
    else:
        print(f" Monitor iniciado: {monitor.running}")
        
        # Enviar mensagem de inicializao
        try:
            if monitor.notifier:
                print(" Enviando mensagem de inicializao...")
                mode = "Bundle (.app)" if getattr(sys, 'frozen', False) else "Desenvolvimento"
                monitor.notifier.send_startup_message(mode=mode)
        except Exception as e:
            print(f" Erro ao enviar mensagem de inicializao: {e}")
            # No bloquear se falhar
    
    # 3. Aguardar servidor estar pronto (opcional, mas recomendado)
    print(" Aguardando servidor Flask iniciar...")
    server_ready = verify_server_ready()
    
    # Verificar se frontend est buildado
    frontend_dist = ROOT_DIR / 'frontend' / 'dist' / 'index.html'
    if not frontend_dist.exists():
        print("")
        print("=" * 60)
        print("  ATENO: Frontend no est buildado!")
        print("=" * 60)
        print("")
        print("Para usar o modo desktop, voc precisa buildar o frontend:")
        print("")
        print("  1. cd frontend")
        print("  2. npm install  (se ainda no instalou)")
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
        print(" Continuando mesmo assim... (pode no funcionar)")
        print("")
    
    # 4. Inicializar NSApplication ANTES de criar janela (CRTICO no macOS)
    import platform
    import threading
    
    if platform.system() == 'Darwin':
        print(" Inicializando NSApplication no macOS...")
        try:
            import AppKit
            # Obter ou criar NSApplication
            app = AppKit.NSApplication.sharedApplication()
            
            # Configurar poltica de ativao (deve ser feito ANTES de criar janelas)
            app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
            
            # CRTICO: Finalizar inicializao do app
            if not app.isRunning():
                app.finishLaunching()
                print(" NSApplication finishLaunching() chamado")
            
            print(" NSApplication inicializado e pronto")
            
        except Exception as e:
            print(f" Erro ao inicializar NSApplication: {e}")
            import traceback
            traceback.print_exc()
            # Continuar mesmo com erro - pode funcionar sem NSApplication explcito
    
    # Verificar se estamos na thread principal (CRTICO para webview)
    if threading.current_thread() != threading.main_thread():
        print(" ERRO CRTICO: No estamos na thread principal!")
        print(" Webview no funcionar fora da thread principal")
        raise RuntimeError("webview.start() deve ser chamado na thread principal")
    
    print(" Thread principal confirmada")
    
    # 5. Criar e iniciar a janela
    print(" Criando janela nativa...")
    
    try:
        window = create_window()
        print(f" Janela criada: {window}")
        
        # Ativar app DEPOIS de criar janela
        if platform.system() == 'Darwin':
            try:
                import AppKit
                app = AppKit.NSApplication.sharedApplication()
                
                # Garantir que o app est rodando
                if not app.isRunning():
                    app.finishLaunching()
                    print(" NSApplication finishLaunching() chamado aps criar janela")
                
                # Ativar app e trazer para frente
                app.activateIgnoringOtherApps_(True)
                print(" App ativado no macOS (activateIgnoringOtherApps)")
                
                # Delay aumentado para dar tempo do macOS processar a ativao
                # Este delay  crtico para que a janela aparea
                time.sleep(0.8)  # Aumentado de 0.3 para 0.8 segundos
                
            except Exception as e:
                print(f" Erro ao ativar app: {e}")
                import traceback
                traceback.print_exc()
                # Continuar mesmo com erro - webview pode funcionar sem isso
        
        # 6. Inicia o Loop da Interface Grfica
        # CRTICO: webview.start() DEVE ser chamado na thread principal
        # e DEVE ser a ltima coisa antes do fim do script
        print(" Iniciando interface grfica...")
        print(" URL: http://127.0.0.1:9999")
        print(" Iniciando webview...")
        print(" Aguarde alguns segundos para a janela aparecer...")
        
        # Verificao final antes de iniciar webview
        if platform.system() == 'Darwin':
            try:
                import AppKit
                app = AppKit.NSApplication.sharedApplication()
                if not app.isRunning():
                    print(" NSApplication no est rodando, tentando iniciar...")
                    app.finishLaunching()
            except:
                pass
        
        # webview.start() bloqueia aqui at a janela fechar
        # CRTICO: No macOS bundle, webview.start() pode no funcionar se:
        # 1. NSApplication no estiver completamente inicializado
        # 2. A thread principal no estiver correta
        # 3. O app no estiver ativado
        
        print(" Preparando para iniciar webview...")
        
        # Verificao final e ativao no macOS
        if platform.system() == 'Darwin':
            try:
                import AppKit
                app = AppKit.NSApplication.sharedApplication()
                
                # Garantir que est rodando
                if not app.isRunning():
                    print(" NSApplication no est rodando, iniciando...")
                    app.finishLaunching()
                
                # Ativar novamente antes de webview.start()
                app.activateIgnoringOtherApps_(True)
                
                # Processar eventos pendentes do macOS
                try:
                    run_loop = AppKit.NSRunLoop.currentRunLoop()
                    run_loop.runMode_beforeDate_(AppKit.NSDefaultRunLoopMode, AppKit.NSDate.dateWithTimeIntervalSinceNow_(0.1))
                except:
                    # Se no conseguir processar eventos, continuar mesmo assim
                    pass
                
                print(" NSApplication verificado e ativado antes de webview.start()")
                
            except Exception as e:
                print(f" Erro ao preparar NSApplication: {e}")
                import traceback
                traceback.print_exc()
        
        # Delay final antes de iniciar webview
        print(" Aguardando 1.5 segundos para garantir que tudo est pronto...")
        time.sleep(1.5)
        
        print(" Chamando webview.start()...")
        print(" Se a janela no aparecer, verifique os logs acima para erros")
        
        try:
            # No modo bundle, usar debug=False para evitar problemas com stdout/stderr
            # Mas podemos tentar debug=True se necessrio para diagnstico
            webview.start(debug=False)
        except Exception as e:
            print(f" Erro crtico ao iniciar webview: {e}")
            import traceback
            traceback.print_exc()
            
            # Salvar erro detalhado
            try:
                error_log = logs_dir / 'webview_start_error.log'
                with open(error_log, 'w') as f:
                    f.write(f"Erro ao iniciar webview: {e}\n")
                    f.write(traceback.format_exc())
                print(f" Erro detalhado salvo em: {error_log}")
            except:
                pass
            
            raise  # Re-raise para que o usurio veja o erro
        
        print(" webview.start() retornou (janela fechada)")
        
    except KeyboardInterrupt:
        print("\n Interrompido pelo usurio")
    except Exception as e:
        print(f" Erro ao criar/iniciar janela: {e}")
        import traceback
        traceback.print_exc()
        
        # Salvar erro em arquivo
        try:
            error_log = logs_dir / 'window_error.log'
            with open(error_log, 'w') as f:
                f.write(f"Erro ao criar/iniciar janela: {e}\n")
                f.write(traceback.format_exc())
            print(f" Erro salvo em: {error_log}")
        except:
            pass
        
        # NO abrir navegador - apenas informar erro
        print("")
        print("=" * 60)
        print(" ERRO: No foi possvel abrir a janela nativa")
        print("=" * 60)
        print("")
        print(" Verifique os logs em:")
        print(f"   {logs_dir}/window_error.log")
        print("")
        print(" Servidor Flask est rodando em http://127.0.0.1:9999")
        print(" Voc pode acessar manualmente no navegador")
        print("")
        
        # Manter servidor rodando para debug
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n Encerrando servidor...")
        
    except KeyboardInterrupt:
        print("\n Interrompido pelo usurio")
    except Exception as e:
        print(f" Erro ao criar/iniciar janela: {e}")
        import traceback
        traceback.print_exc()
        
        # Salvar erro em arquivo
        try:
            error_log = logs_dir / 'error.log'
            with open(error_log, 'w') as f:
                f.write(f"Erro: {e}\n")
                f.write(traceback.format_exc())
            print(f" Erro salvo em: {error_log}")
        except:
            pass
        
        # Se houver erro ao criar janela, apenas informar
        # NO abrir navegador automaticamente - a janela deve abrir normalmente
        print(" Erro ao criar janela")
        print(" Servidor Flask est rodando em http://127.0.0.1:9999")
        print(" Voc pode abrir manualmente no navegador se desejar")
        print(" Pressione Ctrl+C para parar o servidor")
        
        # Manter o processo vivo para o servidor continuar rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n Encerrando...")
    
    print(" SNE RADAR encerrado. At logo!")

