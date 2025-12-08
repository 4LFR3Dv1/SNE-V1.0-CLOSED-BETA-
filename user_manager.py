#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE GESTÃO DE USUÁRIOS E PLANOS - SNE RADAR 3.0
Integração com sistema de segurança existente
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Lock

# ===========================================
# CONFIGURAÇÃO DE LOGGING
# ===========================================
logger = logging.getLogger(__name__)

class UserManager:
    """
    Gerenciador de usuários e planos para o SNE Radar 3.0
    Integra com sistema de segurança existente
    """
    
    def __init__(self):
        """Inicializa o gerenciador de usuários"""
        self._users = {}  # Cache local de usuários
        self._lock = Lock()
        
        # Importar sistema de segurança existente
        try:
            from security_manager import security_manager
            self.security = security_manager
        except ImportError:
            logger.warning("⚠️ security_manager não encontrado. Criando instância local.")
            self.security = None
        
        # Importar configurações
        try:
            from config_seguro import config
            self.config = config
        except ImportError:
            logger.warning("⚠️ config_seguro não encontrado. Usando configurações padrão.")
            self.config = type('Config', (), {
                'DATABASE_URL': 'sqlite:///sne_radar.db',
                'ADMIN_USER_ID': '6457067653'
            })()
        
        # Inicializar banco de dados
        self._init_database()
        
        logger.info("👥 UserManager inicializado")
    
    def _init_database(self):
        """Inicializa banco de dados (SQLite para simplicidade)"""
        try:
            import sqlite3
            
            self.db_path = 'sne_users.db'
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            # Criar tabelas
            self._create_tables()
            
            logger.info("✅ Banco de dados de usuários inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            # Fallback para armazenamento em memória
            self.conn = None
    
    def _create_tables(self):
        """Cria tabelas necessárias"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id TEXT PRIMARY KEY,
                email TEXT,
                nome TEXT,
                plano TEXT DEFAULT 'free',
                expires_at TEXT,
                is_active BOOLEAN DEFAULT 0,
                created_at TEXT,
                last_activity TEXT,
                analises_hoje INTEGER DEFAULT 0,
                ultimo_reset TEXT
            )
        ''')
        
        # Tabela de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                par TEXT,
                preco REAL,
                ativo BOOLEAN DEFAULT 1,
                criado_em TEXT,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # Tabela de pagamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                plano TEXT,
                valor REAL,
                metodo TEXT,
                status TEXT,
                payment_id TEXT,
                data TEXT,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        
        self.conn.commit()
    
    # ===========================================
    # GESTÃO DE USUÁRIOS
    # ===========================================
    def create_user(self, telegram_id: str, plano: str = 'free', email: str = None, nome: str = None) -> bool:
        """
        Cria um novo usuário
        
        Args:
            telegram_id: ID do Telegram
            plano: Plano inicial (free, premium, institutional)
            email: Email do usuário (opcional)
            nome: Nome do usuário (opcional)
            
        Returns:
            bool: True se criado com sucesso
        """
        try:
            # Verificar se usuário já existe (sem lock para evitar deadlock)
            if self.is_user_registered(telegram_id):
                logger.warning(f"⚠️ Usuário {telegram_id} já existe")
                return False
            
            # Criar usuário
            user_data = {
                'telegram_id': str(telegram_id),
                'email': email,
                'nome': nome,
                'plano': plano,
                'expires_at': None if plano == 'free' else (datetime.now() + timedelta(days=30)).isoformat(),
                'is_active': plano != 'free',
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'analises_hoje': 0,
                'ultimo_reset': datetime.now().isoformat()
            }
            
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO users (telegram_id, email, nome, plano, expires_at, 
                                     is_active, created_at, last_activity, analises_hoje, ultimo_reset)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['telegram_id'], user_data['email'], user_data['nome'],
                    user_data['plano'], user_data['expires_at'], user_data['is_active'],
                    user_data['created_at'], user_data['last_activity'],
                    user_data['analises_hoje'], user_data['ultimo_reset']
                ))
                self.conn.commit()
            else:
                # Fallback para memória
                self._users[telegram_id] = user_data
            
            # Log de auditoria
            if self.security:
                self.security._log_audit("USER_CREATED", f"Usuário {telegram_id} criado com plano {plano}", str(telegram_id))
            
            logger.info(f"✅ Usuário {telegram_id} criado com plano {plano}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário {telegram_id}: {e}")
            return False
    
    def get_user_data(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém dados do usuário
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            Dict: Dados do usuário ou None
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (str(telegram_id),))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
            else:
                # Fallback para memória
                return self._users.get(str(telegram_id))
            
            return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuário {telegram_id}: {e}")
            return None
    
    def is_user_registered(self, telegram_id: str) -> bool:
        """
        Verifica se usuário está registrado
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            bool: True se registrado
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute('SELECT telegram_id FROM users WHERE telegram_id = ?', (str(telegram_id),))
                return cursor.fetchone() is not None
            else:
                # Fallback para memória
                return str(telegram_id) in self._users
        except Exception as e:
            logger.error(f"❌ Erro ao verificar registro do usuário {telegram_id}: {e}")
            return False
    
    def update_user_plan(self, telegram_id: str, plano: str, expires_at: datetime = None) -> bool:
        """
        Atualiza plano do usuário
        
        Args:
            telegram_id: ID do Telegram
            plano: Novo plano
            expires_at: Data de expiração
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            with self._lock:
                if not expires_at:
                    expires_at = datetime.now() + timedelta(days=30) if plano != 'free' else None
                
                if self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        UPDATE users 
                        SET plano = ?, expires_at = ?, is_active = ?
                        WHERE telegram_id = ?
                    ''', (plano, expires_at.isoformat() if expires_at else None, plano != 'free', str(telegram_id)))
                    self.conn.commit()
                else:
                    # Fallback para memória
                    if str(telegram_id) in self._users:
                        self._users[str(telegram_id)]['plano'] = plano
                        self._users[str(telegram_id)]['expires_at'] = expires_at.isoformat() if expires_at else None
                        self._users[str(telegram_id)]['is_active'] = plano != 'free'
                
                # Log de auditoria
                if self.security:
                    self.security._log_audit("PLAN_UPDATED", f"Usuário {telegram_id} atualizado para plano {plano}", str(telegram_id))
                
                logger.info(f"✅ Plano do usuário {telegram_id} atualizado para {plano}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar plano do usuário {telegram_id}: {e}")
            return False
    
    def update_user_activity(self, telegram_id: str) -> bool:
        """
        Atualiza atividade do usuário
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            with self._lock:
                now = datetime.now().isoformat()
                
                if self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        UPDATE users 
                        SET last_activity = ?
                        WHERE telegram_id = ?
                    ''', (now, str(telegram_id)))
                    self.conn.commit()
                else:
                    # Fallback para memória
                    if str(telegram_id) in self._users:
                        self._users[str(telegram_id)]['last_activity'] = now
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar atividade do usuário {telegram_id}: {e}")
            return False
    
    # ===========================================
    # VERIFICAÇÕES DE ACESSO
    # ===========================================
    def verificar_acesso_premium(self, telegram_id: str) -> bool:
        """
        Verifica se usuário tem acesso premium
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            bool: True se tem acesso premium
        """
        user_data = self.get_user_data(telegram_id)
        if not user_data:
            return False
        
        # Verificar se é admin (acesso total)
        if str(telegram_id) == self.config.ADMIN_USER_ID:
            return True
        
        # Verificar plano e status
        if user_data['plano'] in ['premium', 'institutional'] and user_data['is_active']:
            # Verificar se não expirou
            if user_data['expires_at']:
                expires_at = datetime.fromisoformat(user_data['expires_at'])
                if datetime.now() > expires_at:
                    # Desativar usuário expirado
                    self.update_user_plan(telegram_id, 'free')
                    return False
            return True
        
        return False
    
    def verificar_acesso_institutional(self, telegram_id: str) -> bool:
        """
        Verifica se usuário tem acesso institucional
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            bool: True se tem acesso institucional
        """
        user_data = self.get_user_data(telegram_id)
        if not user_data:
            return False
        
        # Verificar se é admin (acesso total)
        if str(telegram_id) == self.config.ADMIN_USER_ID:
            return True
        
        # Verificar plano institucional
        return (user_data['plano'] == 'institutional' and 
                user_data['is_active'] and
                (not user_data['expires_at'] or datetime.now() <= datetime.fromisoformat(user_data['expires_at'])))
    
    def verificar_limite_analises(self, telegram_id: str) -> bool:
        """
        Verifica se usuário pode fazer mais análises hoje
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            bool: True se pode fazer mais análises
        """
        user_data = self.get_user_data(telegram_id)
        if not user_data:
            return False
        
        # Reset diário se necessário
        self._reset_daily_counter_if_needed(telegram_id, user_data)
        
        # Obter limites por plano
        from plan_config import PLANOS
        limite = PLANOS.get(user_data['plano'], {}).get('analises_dia', 3)
        
        return user_data['analises_hoje'] < limite
    
    def incrementar_analise(self, telegram_id: str) -> bool:
        """
        Incrementa contador de análises do usuário
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            bool: True se incrementado com sucesso
        """
        try:
            with self._lock:
                if self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        UPDATE users 
                        SET analises_hoje = analises_hoje + 1
                        WHERE telegram_id = ?
                    ''', (str(telegram_id),))
                    self.conn.commit()
                else:
                    # Fallback para memória
                    if str(telegram_id) in self._users:
                        self._users[str(telegram_id)]['analises_hoje'] += 1
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao incrementar análise do usuário {telegram_id}: {e}")
            return False
    
    def _reset_daily_counter_if_needed(self, telegram_id: str, user_data: Dict[str, Any]):
        """Reset contador diário se necessário"""
        try:
            ultimo_reset = datetime.fromisoformat(user_data['ultimo_reset'])
            hoje = datetime.now().date()
            
            if ultimo_reset.date() < hoje:
                # Reset necessário
                if self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        UPDATE users 
                        SET analises_hoje = 0, ultimo_reset = ?
                        WHERE telegram_id = ?
                    ''', (datetime.now().isoformat(), str(telegram_id)))
                    self.conn.commit()
                else:
                    # Fallback para memória
                    if str(telegram_id) in self._users:
                        self._users[str(telegram_id)]['analises_hoje'] = 0
                        self._users[str(telegram_id)]['ultimo_reset'] = datetime.now().isoformat()
                
                logger.info(f"🔄 Contador diário resetado para usuário {telegram_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao resetar contador do usuário {telegram_id}: {e}")
    
    # ===========================================
    # GESTÃO DE ALERTAS
    # ===========================================
    def criar_alerta(self, telegram_id: str, par: str, preco: float) -> Optional[int]:
        """
        Cria um alerta para o usuário
        
        Args:
            telegram_id: ID do Telegram
            par: Par de trading
            preco: Preço alvo
            
        Returns:
            int: ID do alerta criado ou None
        """
        try:
            with self._lock:
                if self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        INSERT INTO alertas (user_id, par, preco, criado_em)
                        VALUES (?, ?, ?, ?)
                    ''', (str(telegram_id), par.upper(), preco, datetime.now().isoformat()))
                    alerta_id = cursor.lastrowid
                    self.conn.commit()
                    
                    # Log de auditoria
                    if self.security:
                        self.security._log_audit("ALERT_CREATED", f"Alerta {par} @ {preco} criado", str(telegram_id))
                    
                    logger.info(f"✅ Alerta criado: {par} @ {preco} para usuário {telegram_id}")
                    return alerta_id
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar alerta para usuário {telegram_id}: {e}")
            return None
    
    def get_alertas_usuario(self, telegram_id: str) -> List[Dict[str, Any]]:
        """
        Obtém alertas ativos do usuário
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            List: Lista de alertas
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT * FROM alertas 
                    WHERE user_id = ? AND ativo = 1
                    ORDER BY criado_em DESC
                ''', (str(telegram_id),))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar alertas do usuário {telegram_id}: {e}")
            return []
    
    def desativar_alerta(self, alerta_id: int) -> bool:
        """
        Desativa um alerta
        
        Args:
            alerta_id: ID do alerta
            
        Returns:
            bool: True se desativado com sucesso
        """
        try:
            with self._lock:
                if self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        UPDATE alertas 
                        SET ativo = 0
                        WHERE id = ?
                    ''', (alerta_id,))
                    self.conn.commit()
                    
                    logger.info(f"✅ Alerta {alerta_id} desativado")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao desativar alerta {alerta_id}: {e}")
            return False
    
    # ===========================================
    # ESTATÍSTICAS E RELATÓRIOS
    # ===========================================
    def get_user_stats(self, telegram_id: str) -> Dict[str, Any]:
        """
        Obtém estatísticas do usuário
        
        Args:
            telegram_id: ID do Telegram
            
        Returns:
            Dict: Estatísticas do usuário
        """
        user_data = self.get_user_data(telegram_id)
        if not user_data:
            return {}
        
        # Reset contador se necessário
        self._reset_daily_counter_if_needed(telegram_id, user_data)
        
        # Obter alertas
        alertas = self.get_alertas_usuario(telegram_id)
        
        return {
            'plano': user_data['plano'],
            'is_active': user_data['is_active'],
            'expires_at': user_data['expires_at'],
            'analises_hoje': user_data['analises_hoje'],
            'alertas_ativos': len(alertas),
            'created_at': user_data['created_at'],
            'last_activity': user_data['last_activity']
        }
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os usuários (admin only)
        
        Returns:
            List: Lista de todos os usuários
        """
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            
            return list(self._users.values())
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar todos os usuários: {e}")
            return []
    
    def cleanup_expired_users(self) -> int:
        """
        Limpa usuários expirados
        
        Returns:
            int: Número de usuários desativados
        """
        try:
            with self._lock:
                if not self.conn:
                    return 0
                
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET is_active = 0
                    WHERE expires_at IS NOT NULL 
                    AND datetime(expires_at) < datetime('now')
                    AND is_active = 1
                ''')
                
                count = cursor.rowcount
                self.conn.commit()
                
                if count > 0:
                    logger.info(f"🧹 {count} usuários expirados desativados")
                
                return count
                
        except Exception as e:
            logger.error(f"❌ Erro ao limpar usuários expirados: {e}")
            return 0

# ===========================================
# INSTÂNCIA GLOBAL
# ===========================================
user_manager = UserManager()

# ===========================================
# FUNÇÕES UTILITÁRIAS
# ===========================================
def criar_usuario(telegram_id: str, plano: str = 'free', email: str = None, nome: str = None) -> bool:
    """Cria um novo usuário"""
    return user_manager.create_user(telegram_id, plano, email, nome)

def verificar_acesso_premium(telegram_id: str) -> bool:
    """Verifica acesso premium"""
    return user_manager.verificar_acesso_premium(telegram_id)

def verificar_acesso_institutional(telegram_id: str) -> bool:
    """Verifica acesso institucional"""
    return user_manager.verificar_acesso_institutional(telegram_id)

def obter_dados_usuario(telegram_id: str) -> Optional[Dict[str, Any]]:
    """Obtém dados do usuário"""
    return user_manager.get_user_data(telegram_id)

if __name__ == "__main__":
    # Teste do sistema de usuários
    print("🧪 Testando sistema de usuários do SNE Radar 3.0...")
    
    try:
        # Criar usuário de teste
        test_user = "123456789"
        
        print(f"\n👤 Criando usuário de teste: {test_user}")
        if user_manager.create_user(test_user, 'free'):
            print("✅ Usuário criado com sucesso!")
        else:
            print("❌ Erro ao criar usuário")
        
        # Verificar dados do usuário
        print(f"\n📊 Dados do usuário:")
        user_data = user_manager.get_user_data(test_user)
        if user_data:
            for key, value in user_data.items():
                print(f"   {key}: {value}")
        
        # Testar verificações de acesso
        print(f"\n🔐 Testando verificações de acesso:")
        print(f"   Premium: {user_manager.verificar_acesso_premium(test_user)}")
        print(f"   Institutional: {user_manager.verificar_acesso_institutional(test_user)}")
        
        # Criar alerta de teste
        print(f"\n🔔 Criando alerta de teste:")
        alerta_id = user_manager.criar_alerta(test_user, 'BTCUSDT', 100000)
        if alerta_id:
            print(f"✅ Alerta criado com ID: {alerta_id}")
        
        # Listar alertas
        alertas = user_manager.get_alertas_usuario(test_user)
        print(f"📋 Alertas ativos: {len(alertas)}")
        
        # Estatísticas
        print(f"\n📈 Estatísticas do usuário:")
        stats = user_manager.get_user_stats(test_user)
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Sistema de usuários testado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao testar sistema de usuários: {e}")
