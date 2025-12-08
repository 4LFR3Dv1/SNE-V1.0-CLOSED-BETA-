#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notificador Telegram para Alertas de Oportunidades
Com persistência de estado
"""

import sys
import json
import platform
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Importar função de envio existente (LAZY - só quando necessário)
# Não importar no nível do módulo para evitar erros de inicialização
TELEGRAM_AVAILABLE = None  # Será verificado quando necessário

def _get_enviar_oraculo():
    """Importa enviar_oraculo apenas quando necessário (lazy import)"""
    global TELEGRAM_AVAILABLE
    if TELEGRAM_AVAILABLE is None:
        try:
            from xenos_bot import enviar_oraculo
            TELEGRAM_AVAILABLE = True
            return enviar_oraculo
        except ImportError as e:
            TELEGRAM_AVAILABLE = False
            print(f"⚠️ xenos_bot não disponível - notificações Telegram desabilitadas: {e}")
            return None
        except Exception as e:
            TELEGRAM_AVAILABLE = False
            print(f"⚠️ Erro ao importar xenos_bot - notificações Telegram desabilitadas: {e}")
            return None
    elif TELEGRAM_AVAILABLE:
        from xenos_bot import enviar_oraculo
        return enviar_oraculo
    else:
        return None

from .alert_formatter import AlertFormatter


def get_app_data_dir() -> Path:
    """Retorna diretório de dados do app (funciona em .app e dev)"""
    if getattr(sys, 'frozen', False):
        # Modo .app - usar diretório do usuário
        home = Path.home()
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            return home / 'Library' / 'Application Support' / 'SNE_RADAR'
        elif system == 'Windows':
            return Path(os.getenv('APPDATA', str(home))) / 'SNE_RADAR'
        else:  # Linux
            return home / '.local' / 'share' / 'SNE_RADAR'
    else:
        # Modo desenvolvimento
        data_dir = ROOT_DIR / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir


class TelegramNotifier:
    """Notificador Telegram para alertas com persistência de estado"""
    
    def __init__(self, state_file: Optional[str] = None, cooldown_minutes: int = 5):
        """
        Inicializa notificador
        
        Args:
            state_file: Caminho do arquivo de estado (None = automático)
            cooldown_minutes: Cooldown entre alertas do mesmo símbolo
        """
        # Verificar se Telegram está disponível (lazy)
        self.enabled = _get_enviar_oraculo() is not None
        self.cooldown_minutes = cooldown_minutes
        
        # Configurar arquivo de estado
        if state_file is None:
            app_data_dir = get_app_data_dir()
            app_data_dir.mkdir(parents=True, exist_ok=True)
            state_file = app_data_dir / 'scanner_state.json'
        
        self.state_file = Path(state_file)
        self.last_alerts = self.load_state()
        self.formatter = AlertFormatter()
        self.startup_message_sent = False  # Flag para evitar mensagem duplicada
    
    def load_state(self) -> Dict:
        """Carrega estado persistido"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    # Converter timestamps de string para datetime se necessário
                    return data
            except Exception as e:
                print(f"⚠️ Erro ao carregar estado: {e}")
                return {}
        return {}
    
    def save_state(self):
        """Salva estado em arquivo"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.last_alerts, f, default=str, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar estado: {e}")
    
    def can_send_alert(self, symbol: str) -> bool:
        """Verifica se pode enviar alerta (cooldown)"""
        if symbol not in self.last_alerts:
            return True
        
        last_alert_str = self.last_alerts[symbol]
        
        # Converter string para datetime se necessário
        if isinstance(last_alert_str, str):
            try:
                last_alert = datetime.fromisoformat(last_alert_str)
            except:
                # Tentar outros formatos
                try:
                    last_alert = datetime.strptime(last_alert_str, '%Y-%m-%d %H:%M:%S')
                except:
                    # Se não conseguir parsear, permitir envio
                    return True
        else:
            last_alert = last_alert_str
        
        elapsed = (datetime.now() - last_alert).total_seconds() / 60
        
        can_send = elapsed >= self.cooldown_minutes
        
        if can_send:
            # Salvar estado após verificação
            self.save_state()
        
        return can_send
    
    def send_volume_alert(self, data: Dict) -> bool:
        """Envia alerta de volume"""
        if not self.enabled:
            print("⚠️ Telegram não disponível")
            return False
        
        symbol = data['symbol']
        
        # Verificar cooldown
        if not self.can_send_alert(symbol):
            print(f"⏳ Alerta de {symbol} em cooldown")
            return False
        
        # Formatar e enviar
        mensagem = self.formatter.format_volume_alert(data)
        enviar_oraculo_func = _get_enviar_oraculo()
        if enviar_oraculo_func is None:
            print("⚠️ enviar_oraculo não disponível")
            return False
        sucesso = enviar_oraculo_func(mensagem)
        
        if sucesso:
            self.last_alerts[symbol] = datetime.now().isoformat()
            self.save_state()  # ✅ Persistir imediatamente
            
            # Salvar histórico detalhado
            self._save_history(symbol, {**data, 'type': 'volume'})
            
            print(f"✅ Alerta de volume enviado: {symbol}")
        else:
            print(f"❌ Falha ao enviar alerta de volume: {symbol}")
        
        return sucesso
    
    def send_pavio_alert(self, data: Dict) -> bool:
        """Envia alerta de agulhada"""
        if not self.enabled:
            print("⚠️ Telegram não disponível")
            return False
        
        symbol = data['symbol']
        
        # Verificar cooldown
        if not self.can_send_alert(symbol):
            print(f"⏳ Alerta de {symbol} em cooldown")
            return False
        
        # Formatar e enviar
        mensagem = self.formatter.format_pavio_alert(data)
        enviar_oraculo_func = _get_enviar_oraculo()
        if enviar_oraculo_func is None:
            print("⚠️ enviar_oraculo não disponível")
            return False
        sucesso = enviar_oraculo_func(mensagem)
        
        if sucesso:
            self.last_alerts[symbol] = datetime.now().isoformat()
            self.save_state()  # ✅ Persistir imediatamente
            
            # Salvar histórico detalhado
            self._save_history(symbol, {**data, 'type': 'pavio'})
            
            print(f"✅ Alerta de agulhada enviado: {symbol} ({data.get('tipo', 'UNKNOWN')})")
        else:
            print(f"❌ Falha ao enviar alerta de agulhada: {symbol}")
        
        return sucesso
    
    def _save_history(self, symbol: str, data: Dict):
        """Salva histórico detalhado de alertas"""
        try:
            history_file = get_app_data_dir() / 'scanner_history.json'
            
            # Carregar histórico existente
            history = {}
            if history_file.exists():
                try:
                    with open(history_file, 'r') as f:
                        history = json.load(f)
                except:
                    history = {}
            
            # Atualizar com novo alerta (manter apenas o mais recente por símbolo)
            history[symbol] = data
            
            # Limitar histórico (manter últimos 100 símbolos)
            if len(history) > 100:
                # Ordenar por timestamp e manter apenas os 100 mais recentes
                sorted_history = sorted(
                    history.items(),
                    key=lambda x: x[1].get('timestamp', ''),
                    reverse=True
                )[:100]
                history = dict(sorted_history)
            
            # Salvar
            with open(history_file, 'w') as f:
                json.dump(history, f, default=str, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar histórico: {e}")
    
    def send_startup_message(self, mode: str = "app") -> bool:
        """
        Envia mensagem de inicialização do sistema
        
        Args:
            mode: Modo de execução ('app', 'dev', 'web', etc.)
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        # Evitar mensagem duplicada
        if self.startup_message_sent:
            print("ℹ️ Mensagem de inicialização já foi enviada, ignorando...")
            return True
        
        if not self.enabled:
            print("⚠️ Telegram não disponível - mensagem de inicialização não enviada")
            return False
        
        try:
            from datetime import datetime
            import platform
            
            # Informações do sistema
            system_info = platform.system()
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Mensagem de inicialização
            mensagem = f"""
🚀 **SNE RADAR - Sistema Iniciado**

📅 Data/Hora: {timestamp}
💻 Sistema: {system_info}
🔧 Modo: {mode}

✅ Monitor de Oportunidades: Ativo
📊 Scanners: Volume + Pavio
🎯 Símbolos: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, ADAUSDT, XRPUSDT

🔄 Sistema pronto para monitorar oportunidades de trading!
            """.strip()
            
            # Enviar mensagem
            enviar_oraculo_func = _get_enviar_oraculo()
            if enviar_oraculo_func is None:
                print("⚠️ enviar_oraculo não disponível")
                return False
            
            sucesso = enviar_oraculo_func(mensagem)
            
            if sucesso:
                print("✅ Mensagem de inicialização enviada com sucesso")
                self.startup_message_sent = True  # Marcar como enviada
            else:
                print("❌ Falha ao enviar mensagem de inicialização")
            
            return sucesso
            
        except Exception as e:
            print(f"⚠️ Erro ao enviar mensagem de inicialização: {e}")
            import traceback
            traceback.print_exc()
            return False

