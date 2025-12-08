#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURAÇÕES SEGURAS DO SNE RADAR 3.0
Sistema centralizado de configuração com suporte a variáveis de ambiente
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# ===========================================
# CONFIGURAÇÃO DE LOGGING
# ===========================================
# Criar diretório de logs se não existir
import os
from pathlib import Path

# Determinar diretório de logs baseado no modo de execução
if getattr(sys, 'frozen', False):
    # Modo bundle: usar diretório do usuário
    import platform
    home = Path.home()
    if platform.system() == 'Darwin':  # macOS
        log_dir = home / 'Library' / 'Application Support' / 'SNE_RADAR' / 'logs'
    elif platform.system() == 'Windows':
        log_dir = Path(os.getenv('APPDATA', str(home))) / 'SNE_RADAR' / 'logs'
    else:  # Linux
        log_dir = home / '.local' / 'share' / 'SNE_RADAR' / 'logs'
else:
    # Modo desenvolvimento: usar diretório do projeto
    log_dir = Path(__file__).parent / 'logs'

log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'sne_radar.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Config:
    """
    Classe de configuração centralizada para o SNE Radar 3.0
    Carrega variáveis de ambiente e fornece configurações seguras
    """
    
    def __init__(self):
        """Inicializa as configurações carregando variáveis de ambiente"""
        self._load_env_variables()
        self._validate_required_configs()
        self._setup_cache()
        self._setup_rate_limiting()
        
    def _load_env_variables(self):
        """Carrega variáveis de ambiente do arquivo .env"""
        try:
            # Tentar carregar python-dotenv se disponível
            try:
                from dotenv import load_dotenv
                load_dotenv()
                logger.info("✅ Variáveis de ambiente carregadas do .env")
            except ImportError:
                logger.warning("⚠️ python-dotenv não instalado. Usando variáveis do sistema.")
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar variáveis de ambiente: {e}")
            
    def _validate_required_configs(self):
        """Valida se as configurações obrigatórias estão presentes"""
        required_configs = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID'
        ]
        
        missing_configs = []
        for config in required_configs:
            if not os.getenv(config):
                missing_configs.append(config)
                
        if missing_configs:
            logger.warning(f"⚠️ Configurações obrigatórias ausentes: {missing_configs}")
            logger.info("🔄 Usando configurações padrão do sistema")
            # Não levantar erro, usar configurações padrão
            # raise ValueError(f"Configurações obrigatórias ausentes: {missing_configs}")
            
        logger.info("✅ Configurações carregadas (padrão ou ambiente)")
        
    def _setup_cache(self):
        """Configura sistema de cache"""
        self.cache_config = {
            'maxsize': int(os.getenv('MAX_CACHE_SIZE', '100')),
            'ttl': int(os.getenv('CACHE_TTL', '300'))
        }
        
    def _setup_rate_limiting(self):
        """Configura sistema de rate limiting"""
        self.rate_limit_config = {
            'limit': int(os.getenv('API_RATE_LIMIT', '5')),
            'window': int(os.getenv('API_RATE_WINDOW', '60'))
        }

    # ===========================================
    # CONFIGURAÇÕES DO TELEGRAM
    # ===========================================
    @property
    def TELEGRAM_TOKEN(self) -> str:
        """Token do bot Telegram"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            # Usar token padrão do sistema atual
            token = "7970664442:AAHTBoX69oRH-r_FxMXWDw8EZjnxxeBd69Y"
            logger.info("🔄 Usando token Telegram padrão do sistema")
        return token
    
    @property
    def TELEGRAM_CHAT_ID(self) -> str:
        """ID do chat Telegram"""
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            # Usar chat ID padrão do sistema atual
            chat_id = "6457067653"
            logger.info("🔄 Usando chat ID padrão do sistema")
        return chat_id
    
    @property
    def TELEGRAM_WEBHOOK_URL(self) -> Optional[str]:
        """URL do webhook Telegram (opcional)"""
        return os.getenv('TELEGRAM_WEBHOOK_URL')
    
    @property
    def TELEGRAM_URL(self) -> str:
        """URL base da API do Telegram"""
        return f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage"
    
    @property
    def TELEGRAM_PHOTO_URL(self) -> str:
        """URL para envio de fotos via Telegram"""
        return f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendPhoto"

    # ===========================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ===========================================
    @property
    def AUTH_TOKEN(self) -> str:
        """Token de autenticação para comandos sensíveis"""
        return os.getenv('AUTH_TOKEN', 'sne_radar_default_token')
    
    @property
    def ADMIN_USER_ID(self) -> str:
        """ID do usuário administrador"""
        admin_id = os.getenv('ADMIN_USER_ID')
        if not admin_id:
            # Usar chat ID padrão como admin
            admin_id = "6457067653"
        return admin_id
    
    @property
    def IS_ADMIN(self, user_id: str) -> bool:
        """Verifica se o usuário é administrador"""
        return str(user_id) == self.ADMIN_USER_ID

    # ===========================================
    # CONFIGURAÇÕES DE PERFORMANCE
    # ===========================================
    @property
    def MAX_RETRIES(self) -> int:
        """Número máximo de tentativas para requisições"""
        return int(os.getenv('MAX_RETRIES', '3'))
    
    @property
    def REQUEST_TIMEOUT(self) -> int:
        """Timeout para requisições em segundos"""
        return int(os.getenv('REQUEST_TIMEOUT', '10'))
    
    @property
    def MESSAGE_LIMIT(self) -> int:
        """Limite de caracteres por mensagem"""
        return int(os.getenv('MESSAGE_LIMIT', '3500'))
    
    @property
    def CACHE_TTL(self) -> int:
        """TTL do cache em segundos"""
        return self.cache_config['ttl']
    
    @property
    def MAX_CACHE_SIZE(self) -> int:
        """Tamanho máximo do cache"""
        return self.cache_config['maxsize']

    # ===========================================
    # CONFIGURAÇÕES DE RATE LIMITING
    # ===========================================
    @property
    def RATE_LIMIT(self) -> int:
        """Limite de comandos por janela de tempo"""
        return self.rate_limit_config['limit']
    
    @property
    def RATE_WINDOW(self) -> int:
        """Janela de tempo para rate limiting em segundos"""
        return self.rate_limit_config['window']

    # ===========================================
    # CONFIGURAÇÕES DE AMBIENTE
    # ===========================================
    @property
    def ENVIRONMENT(self) -> str:
        """Ambiente atual (development/production)"""
        return os.getenv('ENVIRONMENT', 'development')
    
    @property
    def DEBUG(self) -> bool:
        """Modo debug ativado"""
        return os.getenv('DEBUG', 'True').lower() == 'true'
    
    @property
    def LOG_LEVEL(self) -> str:
        """Nível de log"""
        return os.getenv('LOG_LEVEL', 'INFO')

    # ===========================================
    # CONFIGURAÇÕES DE NOTIFICAÇÃO
    # ===========================================
    @property
    def ENABLE_NOTIFICATIONS(self) -> bool:
        """Notificações habilitadas"""
        return os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'
    
    @property
    def NOTIFICATION_INTERVAL(self) -> int:
        """Intervalo entre notificações em segundos"""
        return int(os.getenv('NOTIFICATION_INTERVAL', '300'))
    
    @property
    def MAX_NOTIFICATIONS_PER_HOUR(self) -> int:
        """Máximo de notificações por hora"""
        return int(os.getenv('MAX_NOTIFICATIONS_PER_HOUR', '10'))

    # ===========================================
    # CONFIGURAÇÕES DE ANÁLISE
    # ===========================================
    @property
    def DEFAULT_TIMEFRAME(self) -> str:
        """Timeframe padrão para análises"""
        return os.getenv('DEFAULT_TIMEFRAME', '1h')
    
    @property
    def ANALYSIS_TIMEOUT(self) -> int:
        """Timeout para análises em segundos"""
        return int(os.getenv('ANALYSIS_TIMEOUT', '30'))
    
    @property
    def MAX_CONCURRENT_ANALYSES(self) -> int:
        """Máximo de análises simultâneas"""
        return int(os.getenv('MAX_CONCURRENT_ANALYSES', '3'))

    # ===========================================
    # CONFIGURAÇÕES DE BANCO DE DADOS
    # ===========================================
    @property
    def DATABASE_URL(self) -> str:
        """URL do banco de dados"""
        return os.getenv('DATABASE_URL', 'sqlite:///sne_radar.db')
    
    @property
    def POSTGRES_URL(self) -> Optional[str]:
        """URL do PostgreSQL (opcional)"""
        return os.getenv('POSTGRES_URL')

    # ===========================================
    # CONFIGURAÇÕES DE BINANCE
    # ===========================================
    @property
    def BINANCE_API_KEY(self) -> Optional[str]:
        """Chave da API Binance"""
        return os.getenv('BINANCE_API_KEY')
    
    @property
    def BINANCE_SECRET_KEY(self) -> Optional[str]:
        """Chave secreta da API Binance"""
        return os.getenv('BINANCE_SECRET_KEY')

    # ===========================================
    # CONFIGURAÇÕES DE BACKUP
    # ===========================================
    @property
    def BACKUP_ENABLED(self) -> bool:
        """Backup habilitado"""
        return os.getenv('BACKUP_ENABLED', 'True').lower() == 'true'
    
    @property
    def BACKUP_INTERVAL(self) -> int:
        """Intervalo entre backups em segundos"""
        return int(os.getenv('BACKUP_INTERVAL', '3600'))
    
    @property
    def BACKUP_RETENTION_DAYS(self) -> int:
        """Dias de retenção dos backups"""
        return int(os.getenv('BACKUP_RETENTION_DAYS', '7'))

    # ===========================================
    # MÉTODOS UTILITÁRIOS
    # ===========================================
    def get_config_summary(self) -> Dict[str, Any]:
        """Retorna um resumo das configurações (sem credenciais sensíveis)"""
        return {
            'environment': self.ENVIRONMENT,
            'debug': self.DEBUG,
            'log_level': self.LOG_LEVEL,
            'max_retries': self.MAX_RETRIES,
            'request_timeout': self.REQUEST_TIMEOUT,
            'message_limit': self.MESSAGE_LIMIT,
            'cache_ttl': self.CACHE_TTL,
            'max_cache_size': self.MAX_CACHE_SIZE,
            'rate_limit': self.RATE_LIMIT,
            'rate_window': self.RATE_WINDOW,
            'enable_notifications': self.ENABLE_NOTIFICATIONS,
            'notification_interval': self.NOTIFICATION_INTERVAL,
            'default_timeframe': self.DEFAULT_TIMEFRAME,
            'analysis_timeout': self.ANALYSIS_TIMEOUT,
            'max_concurrent_analyses': self.MAX_CONCURRENT_ANALYSES,
            'backup_enabled': self.BACKUP_ENABLED,
            'backup_interval': self.BACKUP_INTERVAL,
            'backup_retention_days': self.BACKUP_RETENTION_DAYS,
            'telegram_configured': bool(self.TELEGRAM_TOKEN and self.TELEGRAM_CHAT_ID),
            'binance_configured': bool(self.BINANCE_API_KEY and self.BINANCE_SECRET_KEY),
            'webhook_configured': bool(self.TELEGRAM_WEBHOOK_URL)
        }
    
    def validate_telegram_token(self) -> bool:
        """Valida se o token do Telegram é válido"""
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/getMe"
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Erro ao validar token Telegram: {e}")
            return False
    
    def log_configuration(self):
        """Registra as configurações no log (sem credenciais)"""
        summary = self.get_config_summary()
        logger.info("🔧 Configurações carregadas:")
        for key, value in summary.items():
            logger.info(f"   {key}: {value}")

# ===========================================
# INSTÂNCIA GLOBAL DE CONFIGURAÇÃO
# ===========================================
config = Config()

# ===========================================
# COMANDOS DISPONÍVEIS
# ===========================================
COMANDOS = {
    "start": {
        "descricao": "Inicia o bot e mostra menu principal",
        "funcao": "start_command",
        "admin_only": False
    },
    "status": {
        "descricao": "Verifica status do sistema",
        "funcao": "status_command", 
        "admin_only": False
    },
    "analise": {
        "descricao": "Gera análise técnica de um par",
        "funcao": "analise_command",
        "admin_only": False,
        "args": ["par"]
    },
    "relatorio": {
        "descricao": "Gera relatório completo",
        "funcao": "relatorio_command",
        "admin_only": False
    },
    "config": {
        "descricao": "Mostra configurações do sistema",
        "funcao": "config_command",
        "admin_only": True
    },
    "logs": {
        "descricao": "Mostra logs recentes",
        "funcao": "logs_command",
        "admin_only": True
    },
    "backup": {
        "descricao": "Executa backup do sistema",
        "funcao": "backup_command",
        "admin_only": True
    },
    "restart": {
        "descricao": "Reinicia o sistema",
        "funcao": "restart_command",
        "admin_only": True
    }
}

# ===========================================
# CONFIGURAÇÕES DE CACHE
# ===========================================
CACHE_CONFIG = {
    'analises': {
        'maxsize': config.MAX_CACHE_SIZE,
        'ttl': config.CACHE_TTL
    },
    'relatorios': {
        'maxsize': 50,
        'ttl': 600  # 10 minutos
    },
    'sinais': {
        'maxsize': 200,
        'ttl': 180  # 3 minutos
    }
}

# ===========================================
# CONFIGURAÇÕES DE RATE LIMITING
# ===========================================
RATE_LIMIT_CONFIG = {
    'comandos': {
        'limit': config.RATE_LIMIT,
        'window': config.RATE_WINDOW
    },
    'analises': {
        'limit': 3,
        'window': 60
    },
    'relatorios': {
        'limit': 2,
        'window': 300
    }
}

if __name__ == "__main__":
    # Teste das configurações
    print("🧪 Testando configurações do SNE Radar 3.0...")
    
    try:
        # Carregar configuração
        cfg = Config()
        
        # Mostrar resumo
        print("\n📊 Resumo das configurações:")
        summary = cfg.get_config_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # Validar token Telegram
        print(f"\n🔍 Validando token Telegram...")
        if cfg.validate_telegram_token():
            print("✅ Token Telegram válido!")
        else:
            print("❌ Token Telegram inválido!")
        
        # Mostrar comandos disponíveis
        print(f"\n📋 Comandos disponíveis ({len(COMANDOS)}):")
        for cmd, info in COMANDOS.items():
            admin_flag = " [ADMIN]" if info.get('admin_only') else ""
            print(f"   /{cmd}: {info['descricao']}{admin_flag}")
        
        print("\n✅ Configurações carregadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        sys.exit(1)
