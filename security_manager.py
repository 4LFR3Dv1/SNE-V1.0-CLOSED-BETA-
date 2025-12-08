#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE SEGURANÇA E AUTENTICAÇÃO DO SNE RADAR 3.0
Validação de tokens, rate limiting e logs de auditoria
"""

import os
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
from threading import Lock
import json

# ===========================================
# CONFIGURAÇÃO DE LOGGING
# ===========================================
logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Gerenciador de segurança para o SNE Radar 3.0
    Responsável por validação de tokens, rate limiting e auditoria
    """
    
    def __init__(self):
        """Inicializa o gerenciador de segurança"""
        self._rate_limit_data = {}  # {user_id: [timestamps]}
        self._auth_tokens = {}  # {token: {user_id, expires_at, permissions}}
        self._audit_logs = []  # Lista de logs de auditoria
        self._lock = Lock()  # Lock para thread safety
        
        # Carregar configurações
        try:
            from config_seguro import config
            self.config = config
        except ImportError:
            # Fallback para configurações padrão
            self.config = type('Config', (), {
                'AUTH_TOKEN': 'sne_radar_default_token',
                'ADMIN_USER_ID': '6457067653',
                'RATE_LIMIT': 5,
                'RATE_WINDOW': 60,
                'REQUEST_TIMEOUT': 10
            })()
            
        logger.info("🔒 SecurityManager inicializado")
    
    # ===========================================
    # VALIDAÇÃO DE TOKENS
    # ===========================================
    def validate_telegram_token(self, token: str) -> bool:
        """
        Valida se o token do Telegram é válido
        
        Args:
            token: Token do bot Telegram
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            import requests
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"✅ Token Telegram válido para bot: {bot_info.get('result', {}).get('username', 'Unknown')}")
                return True
            else:
                logger.warning(f"❌ Token Telegram inválido: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao validar token Telegram: {e}")
            return False
    
    def validate_auth_token(self, token: str) -> bool:
        """
        Valida token de autenticação para comandos sensíveis
        
        Args:
            token: Token de autenticação
            
        Returns:
            bool: True se válido, False caso contrário
        """
        expected_token = self.config.AUTH_TOKEN
        
        # Verificar se o token corresponde
        if token != expected_token:
            self._log_audit("AUTH_FAILED", f"Token inválido: {token[:10]}...")
            return False
        
        # Verificar se o token não expirou (se aplicável)
        if token in self._auth_tokens:
            auth_data = self._auth_tokens[token]
            if datetime.now() > auth_data['expires_at']:
                self._log_audit("AUTH_EXPIRED", f"Token expirado: {token[:10]}...")
                del self._auth_tokens[token]
                return False
        
        self._log_audit("AUTH_SUCCESS", f"Token válido: {token[:10]}...")
        return True
    
    def generate_session_token(self, user_id: str, permissions: List[str] = None) -> str:
        """
        Gera um token de sessão temporário
        
        Args:
            user_id: ID do usuário
            permissions: Lista de permissões
            
        Returns:
            str: Token de sessão gerado
        """
        timestamp = str(int(time.time()))
        data = f"{user_id}:{timestamp}:{self.config.AUTH_TOKEN}"
        token = hashlib.sha256(data.encode()).hexdigest()[:32]
        
        # Armazenar token com expiração
        expires_at = datetime.now() + timedelta(hours=24)
        self._auth_tokens[token] = {
            'user_id': user_id,
            'expires_at': expires_at,
            'permissions': permissions or ['read']
        }
        
        self._log_audit("TOKEN_GENERATED", f"Token gerado para usuário {user_id}")
        return token
    
    # ===========================================
    # RATE LIMITING
    # ===========================================
    def check_rate_limit(self, user_id: str, action: str = 'comando') -> bool:
        """
        Verifica se o usuário está dentro do limite de rate
        
        Args:
            user_id: ID do usuário
            action: Tipo de ação (comando, analise, relatorio)
            
        Returns:
            bool: True se permitido, False se limitado
        """
        with self._lock:
            now = time.time()
            
            # Configurações de rate limit por tipo de ação
            rate_configs = {
                'comando': {'limit': self.config.RATE_LIMIT, 'window': self.config.RATE_WINDOW},
                'analise': {'limit': 3, 'window': 60},
                'relatorio': {'limit': 2, 'window': 300}
            }
            
            config = rate_configs.get(action, rate_configs['comando'])
            limit = config['limit']
            window = config['window']
            
            # Obter timestamps do usuário
            user_key = f"{user_id}:{action}"
            if user_key not in self._rate_limit_data:
                self._rate_limit_data[user_key] = []
            
            timestamps = self._rate_limit_data[user_key]
            
            # Remover timestamps antigos (fora da janela)
            timestamps = [t for t in timestamps if now - t < window]
            
            # Verificar se está dentro do limite
            if len(timestamps) >= limit:
                self._log_audit("RATE_LIMIT_EXCEEDED", f"Usuário {user_id} excedeu limite para {action}")
                return False
            
            # Adicionar timestamp atual
            timestamps.append(now)
            self._rate_limit_data[user_key] = timestamps
            
            self._log_audit("RATE_LIMIT_OK", f"Usuário {user_id} dentro do limite para {action}")
            return True
    
    def get_rate_limit_info(self, user_id: str, action: str = 'comando') -> Dict[str, Any]:
        """
        Retorna informações sobre o rate limit do usuário
        
        Args:
            user_id: ID do usuário
            action: Tipo de ação
            
        Returns:
            Dict: Informações sobre rate limit
        """
        with self._lock:
            user_key = f"{user_id}:{action}"
            if user_key not in self._rate_limit_data:
                return {
                    'current': 0,
                    'limit': self.config.RATE_LIMIT,
                    'window': self.config.RATE_WINDOW,
                    'reset_in': 0
                }
            
            now = time.time()
            timestamps = self._rate_limit_data[user_key]
            
            # Remover timestamps antigos
            timestamps = [t for t in timestamps if now - t < self.config.RATE_WINDOW]
            
            # Calcular próximo reset
            if timestamps:
                oldest_timestamp = min(timestamps)
                reset_in = self.config.RATE_WINDOW - (now - oldest_timestamp)
            else:
                reset_in = 0
            
            return {
                'current': len(timestamps),
                'limit': self.config.RATE_LIMIT,
                'window': self.config.RATE_WINDOW,
                'reset_in': max(0, reset_in)
            }
    
    # ===========================================
    # LOGS DE AUDITORIA
    # ===========================================
    def _log_audit(self, action: str, details: str, user_id: str = None, severity: str = 'INFO'):
        """
        Registra um evento de auditoria
        
        Args:
            action: Ação realizada
            details: Detalhes da ação
            user_id: ID do usuário (opcional)
            severity: Severidade do evento (INFO, WARNING, ERROR)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'user_id': user_id,
            'severity': severity
        }
        
        with self._lock:
            self._audit_logs.append(log_entry)
            
            # Manter apenas os últimos 1000 logs
            if len(self._audit_logs) > 1000:
                self._audit_logs = self._audit_logs[-1000:]
        
        # Log também no sistema de logging
        log_message = f"[AUDIT] {action}: {details}"
        if user_id:
            log_message += f" (User: {user_id})"
            
        if severity == 'ERROR':
            logger.error(log_message)
        elif severity == 'WARNING':
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def get_audit_logs(self, limit: int = 100, severity: str = None) -> List[Dict[str, Any]]:
        """
        Retorna logs de auditoria
        
        Args:
            limit: Número máximo de logs
            severity: Filtrar por severidade
            
        Returns:
            List: Lista de logs de auditoria
        """
        with self._lock:
            logs = self._audit_logs.copy()
        
        # Filtrar por severidade se especificado
        if severity:
            logs = [log for log in logs if log['severity'] == severity]
        
        # Retornar os logs mais recentes
        return logs[-limit:] if limit else logs
    
    def save_audit_logs(self, filename: str = None):
        """
        Salva logs de auditoria em arquivo
        
        Args:
            filename: Nome do arquivo (opcional)
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audit_logs_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self._audit_logs, f, indent=2, ensure_ascii=False)
            
            self._log_audit("AUDIT_SAVED", f"Logs salvos em {filename}")
            logger.info(f"✅ Logs de auditoria salvos em {filename}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar logs de auditoria: {e}")
    
    # ===========================================
    # VERIFICAÇÕES DE PLANO E MONETIZAÇÃO
    # ===========================================
    def verificar_plano_usuario(self, user_id: str, plano_requerido: str) -> bool:
        """
        Verifica se o usuário tem o plano necessário
        
        Args:
            user_id: ID do usuário
            plano_requerido: Plano requerido (free, premium, institutional)
            
        Returns:
            bool: True se tem o plano necessário
        """
        try:
            from user_manager import user_manager
            
            user_data = user_manager.get_user_data(user_id)
            if not user_data:
                self._log_audit("PLAN_CHECK_FAILED", f"Usuário {user_id} não encontrado", user_id)
                return False
            
            # Verificar se é admin (acesso total)
            if self.is_admin(user_id):
                return True
            
            # Hierarquia de planos
            planos_hierarquia = {'free': 0, 'premium': 1, 'institutional': 2}
            
            plano_atual = planos_hierarquia.get(user_data['plano'], 0)
            plano_necessario = planos_hierarquia.get(plano_requerido, 0)
            
            tem_acesso = plano_atual >= plano_necessario
            
            if tem_acesso:
                self._log_audit("PLAN_CHECK_SUCCESS", f"Usuário {user_id} tem acesso {user_data['plano']} >= {plano_requerido}", user_id)
            else:
                self._log_audit("PLAN_CHECK_DENIED", f"Usuário {user_id} sem acesso {user_data['plano']} < {plano_requerido}", user_id)
            
            return tem_acesso
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar plano do usuário {user_id}: {e}")
            return False
    
    def verificar_acesso_premium(self, user_id: str) -> bool:
        """
        Verifica se o usuário tem acesso premium
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se tem acesso premium
        """
        return self.verificar_plano_usuario(user_id, 'premium')
    
    def verificar_acesso_institutional(self, user_id: str) -> bool:
        """
        Verifica se o usuário tem acesso institucional
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se tem acesso institucional
        """
        return self.verificar_plano_usuario(user_id, 'institutional')
    
    def verificar_limite_analises(self, user_id: str) -> bool:
        """
        Verifica se o usuário pode fazer mais análises hoje
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se pode fazer mais análises
        """
        try:
            from user_manager import user_manager
            
            pode_analisar = user_manager.verificar_limite_analises(user_id)
            
            if pode_analisar:
                self._log_audit("ANALYSIS_LIMIT_OK", f"Usuário {user_id} dentro do limite de análises", user_id)
            else:
                self._log_audit("ANALYSIS_LIMIT_EXCEEDED", f"Usuário {user_id} excedeu limite de análises", user_id)
            
            return pode_analisar
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar limite de análises do usuário {user_id}: {e}")
            return False
    
    def aplicar_rate_limit_por_plano(self, user_id: str, acao: str) -> bool:
        """
        Aplica rate limiting baseado no plano do usuário
        
        Args:
            user_id: ID do usuário
            acao: Tipo de ação
            
        Returns:
            bool: True se permitido
        """
        try:
            from user_manager import user_manager
            from plan_config import RATE_LIMITS
            
            user_data = user_manager.get_user_data(user_id)
            if not user_data:
                return False
            
            plano = user_data['plano']
            limites = RATE_LIMITS.get(plano, RATE_LIMITS['free'])
            
            # Aplicar rate limit específico por ação
            if acao == 'analise':
                return self.check_rate_limit(user_id, 'analise')
            elif acao == 'relatorio':
                return self.check_rate_limit(user_id, 'relatorio')
            elif acao == 'comando':
                return self.check_rate_limit(user_id, 'comando')
            else:
                return self.check_rate_limit(user_id, acao)
                
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar rate limit por plano para usuário {user_id}: {e}")
            return False
    
    def verificar_funcionalidade_disponivel(self, user_id: str, funcionalidade: str) -> bool:
        """
        Verifica se uma funcionalidade está disponível para o usuário
        
        Args:
            user_id: ID do usuário
            funcionalidade: Nome da funcionalidade
            
        Returns:
            bool: True se disponível
        """
        try:
            from user_manager import user_manager
            from plan_config import verificar_funcionalidade_disponivel
            
            user_data = user_manager.get_user_data(user_id)
            if not user_data:
                return False
            
            # Verificar se é admin (acesso total)
            if self.is_admin(user_id):
                return True
            
            # Verificar funcionalidade no plano
            disponivel = verificar_funcionalidade_disponivel(user_data['plano'], funcionalidade)
            
            if disponivel:
                self._log_audit("FEATURE_ACCESS_GRANTED", f"Usuário {user_id} acessou {funcionalidade}", user_id)
            else:
                self._log_audit("FEATURE_ACCESS_DENIED", f"Usuário {user_id} negado acesso a {funcionalidade}", user_id)
            
            return disponivel
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar funcionalidade para usuário {user_id}: {e}")
            return False
    
    def registrar_uso_funcionalidade(self, user_id: str, funcionalidade: str) -> bool:
        """
        Registra uso de uma funcionalidade pelo usuário
        
        Args:
            user_id: ID do usuário
            funcionalidade: Nome da funcionalidade
            
        Returns:
            bool: True se registrado com sucesso
        """
        try:
            from user_manager import user_manager
            
            # Incrementar contador se for análise
            if funcionalidade == 'analise':
                user_manager.incrementar_analise(user_id)
            
            # Log de auditoria
            self._log_audit("FEATURE_USED", f"Usuário {user_id} usou {funcionalidade}", user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar uso da funcionalidade {funcionalidade} para usuário {user_id}: {e}")
            return False
    def is_admin(self, user_id: str) -> bool:
        """
        Verifica se o usuário é administrador
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se for admin, False caso contrário
        """
        is_admin = str(user_id) == self.config.ADMIN_USER_ID
        if is_admin:
            self._log_audit("ADMIN_ACCESS", f"Usuário {user_id} identificado como admin")
        return is_admin
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Verifica se o usuário tem uma permissão específica
        
        Args:
            user_id: ID do usuário
            permission: Permissão requerida
            
        Returns:
            bool: True se tem permissão, False caso contrário
        """
        # Admin tem todas as permissões
        if self.is_admin(user_id):
            return True
        
        # Verificar permissões específicas (implementar conforme necessário)
        permissions = {
            'read': True,  # Todos podem ler
            'write': False,  # Apenas admin pode escrever
            'admin': False  # Apenas admin
        }
        
        has_perm = permissions.get(permission, False)
        self._log_audit("PERMISSION_CHECK", f"Usuário {user_id} verificou permissão {permission}: {has_perm}")
        return has_perm
    
    # ===========================================
    # DECORATORS DE SEGURANÇA
    # ===========================================
    def require_auth(self, func):
        """Decorator para requerer autenticação"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extrair token dos argumentos (implementar conforme necessário)
            token = kwargs.get('token') or (args[0] if args else None)
            
            if not self.validate_auth_token(token):
                return {'error': 'Token de autenticação inválido'}
            
            return func(*args, **kwargs)
        return wrapper
    
    def require_admin(self, func):
        """Decorator para requerer privilégios de admin"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            
            if not self.is_admin(user_id):
                self._log_audit("ADMIN_REQUIRED", f"Usuário {user_id} tentou acessar função admin")
                return {'error': 'Privilégios de administrador requeridos'}
            
            return func(*args, **kwargs)
        return wrapper
    
    def rate_limited(self, action: str = 'comando'):
        """Decorator para aplicar rate limiting"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_id = kwargs.get('user_id') or (args[0] if args else None)
                
                if not self.check_rate_limit(user_id, action):
                    return {
                        'error': f'Rate limit excedido para {action}',
                        'rate_info': self.get_rate_limit_info(user_id, action)
                    }
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    # ===========================================
    # MÉTODOS UTILITÁRIOS
    # ===========================================
    def get_security_status(self) -> Dict[str, Any]:
        """
        Retorna status de segurança do sistema
        
        Returns:
            Dict: Status de segurança
        """
        with self._lock:
            active_tokens = len([t for t in self._auth_tokens.values() 
                               if datetime.now() < t['expires_at']])
            
            rate_limited_users = len([k for k, v in self._rate_limit_data.items() 
                                    if len(v) > 0])
        
        return {
            'active_tokens': active_tokens,
            'rate_limited_users': rate_limited_users,
            'total_audit_logs': len(self._audit_logs),
            'telegram_token_valid': self.validate_telegram_token(self.config.TELEGRAM_TOKEN),
            'admin_user_id': self.config.ADMIN_USER_ID,
            'rate_limit_config': {
                'limit': self.config.RATE_LIMIT,
                'window': self.config.RATE_WINDOW
            }
        }
    
    def cleanup_expired_tokens(self):
        """Remove tokens expirados"""
        now = datetime.now()
        expired_tokens = [token for token, data in self._auth_tokens.items() 
                         if now > data['expires_at']]
        
        for token in expired_tokens:
            del self._auth_tokens[token]
            self._log_audit("TOKEN_EXPIRED", f"Token expirado removido: {token[:10]}...")
        
        if expired_tokens:
            logger.info(f"🧹 {len(expired_tokens)} tokens expirados removidos")

# ===========================================
# INSTÂNCIA GLOBAL DE SEGURANÇA
# ===========================================
security_manager = SecurityManager()

# ===========================================
# FUNÇÕES UTILITÁRIAS
# ===========================================
def validate_telegram_token(token: str) -> bool:
    """Valida token do Telegram"""
    return security_manager.validate_telegram_token(token)

def check_rate_limit(user_id: str, action: str = 'comando') -> bool:
    """Verifica rate limit"""
    return security_manager.check_rate_limit(user_id, action)

def log_audit(action: str, details: str, user_id: str = None, severity: str = 'INFO'):
    """Registra evento de auditoria"""
    security_manager._log_audit(action, details, user_id, severity)

def is_admin(user_id: str) -> bool:
    """Verifica se é admin"""
    return security_manager.is_admin(user_id)

if __name__ == "__main__":
    # Teste do sistema de segurança
    print("🧪 Testando sistema de segurança do SNE Radar 3.0...")
    
    try:
        # Inicializar security manager
        sm = SecurityManager()
        
        # Testar validação de token Telegram
        print("\n🔍 Testando validação de token Telegram...")
        if sm.validate_telegram_token(sm.config.TELEGRAM_TOKEN):
            print("✅ Token Telegram válido!")
        else:
            print("❌ Token Telegram inválido!")
        
        # Testar rate limiting
        print("\n⏱️ Testando rate limiting...")
        test_user = "test_user_123"
        
        for i in range(7):  # Testar além do limite
            allowed = sm.check_rate_limit(test_user, 'comando')
            print(f"   Tentativa {i+1}: {'✅ Permitido' if allowed else '❌ Bloqueado'}")
        
        # Mostrar informações de rate limit
        rate_info = sm.get_rate_limit_info(test_user, 'comando')
        print(f"   Rate limit info: {rate_info}")
        
        # Testar logs de auditoria
        print("\n📝 Testando logs de auditoria...")
        sm._log_audit("TEST_ACTION", "Teste de auditoria", test_user)
        logs = sm.get_audit_logs(limit=5)
        print(f"   Logs recentes: {len(logs)}")
        
        # Mostrar status de segurança
        print("\n🔒 Status de segurança:")
        status = sm.get_security_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Sistema de segurança testado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao testar sistema de segurança: {e}")
