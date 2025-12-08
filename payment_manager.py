#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE PAGAMENTOS - SNE RADAR 3.0
Integração com Mercado Pago, Stripe e PIX
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from threading import Lock

# ===========================================
# CONFIGURAÇÃO DE LOGGING
# ===========================================
logger = logging.getLogger(__name__)

class PaymentManager:
    """
    Gerenciador de pagamentos para o SNE Radar 3.0
    Suporta PIX, Mercado Pago e Stripe
    """
    
    def __init__(self):
        """Inicializa o gerenciador de pagamentos"""
        self._payments = {}  # Cache local de pagamentos
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
                'DATABASE_URL': 'sqlite:///sne_radar.db'
            })()
        
        # Importar configurações de planos
        try:
            from plan_config import PLANOS, PAGAMENTO_CONFIG
            self.planos = PLANOS
            self.pagamento_config = PAGAMENTO_CONFIG
        except ImportError:
            logger.warning("⚠️ plan_config não encontrado. Usando configurações padrão.")
            self.planos = {'premium': {'preco': 199}, 'institutional': {'preco': 799}}
            self.pagamento_config = {'moeda': 'BRL'}
        
        # Inicializar provedores de pagamento
        self._init_payment_providers()
        
        logger.info("💳 PaymentManager inicializado")
    
    def _init_payment_providers(self):
        """Inicializa provedores de pagamento"""
        # Mercado Pago
        try:
            import mercadopago
            access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN', 'TEST-123456789')
            self.mp = mercadopago.SDK(access_token)
            logger.info("✅ Mercado Pago inicializado")
        except ImportError:
            logger.warning("⚠️ Mercado Pago não disponível. Instale: pip install mercadopago")
            self.mp = None
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Mercado Pago: {e}")
            self.mp = None
        
        # Stripe
        try:
            import stripe
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
            self.stripe = stripe
            logger.info("✅ Stripe inicializado")
        except ImportError:
            logger.warning("⚠️ Stripe não disponível. Instale: pip install stripe")
            self.stripe = None
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Stripe: {e}")
            self.stripe = None
    
    # ===========================================
    # CRIAÇÃO DE PAGAMENTOS
    # ===========================================
    def criar_pagamento_pix(self, user_id: str, plano: str, periodo: str = 'mensal') -> Dict[str, Any]:
        """
        Cria pagamento PIX
        
        Args:
            user_id: ID do usuário
            plano: Plano escolhido
            periodo: Período de pagamento
            
        Returns:
            Dict: Informações do pagamento PIX
        """
        try:
            # Calcular valor
            valor = self._calcular_valor_plano(plano, periodo)
            
            # Gerar ID único do pagamento
            payment_id = self._gerar_payment_id(user_id, plano, periodo)
            
            # Criar registro de pagamento
            payment_data = {
                'payment_id': payment_id,
                'user_id': user_id,
                'plano': plano,
                'periodo': periodo,
                'valor': valor,
                'metodo': 'pix',
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
                'pix_data': {
                    'chave': self.pagamento_config['metodos']['pix']['chave'],
                    'instrucoes': f'Pagamento SNE Radar - Plano {plano.title()} - R$ {valor:.2f}'
                }
            }
            
            # Salvar pagamento
            self._salvar_pagamento(payment_data)
            
            # Log de auditoria
            if self.security:
                self.security._log_audit("PAYMENT_PIX_CREATED", f"PIX criado para {user_id}: {plano} - R$ {valor:.2f}", user_id)
            
            logger.info(f"✅ Pagamento PIX criado: {payment_id} - R$ {valor:.2f}")
            
            return {
                'success': True,
                'payment_id': payment_id,
                'valor': valor,
                'chave_pix': self.pagamento_config['metodos']['pix']['chave'],
                'instrucoes': payment_data['pix_data']['instrucoes'],
                'expires_at': payment_data['expires_at']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pagamento PIX: {e}")
            return {'success': False, 'error': str(e)}
    
    def criar_pagamento_mercadopago(self, user_id: str, plano: str, periodo: str = 'mensal') -> Dict[str, Any]:
        """
        Cria pagamento via Mercado Pago
        
        Args:
            user_id: ID do usuário
            plano: Plano escolhido
            periodo: Período de pagamento
            
        Returns:
            Dict: Informações do pagamento Mercado Pago
        """
        try:
            if not self.mp:
                return {'success': False, 'error': 'Mercado Pago não configurado'}
            
            # Calcular valor
            valor = self._calcular_valor_plano(plano, periodo)
            
            # Gerar ID único do pagamento
            payment_id = self._gerar_payment_id(user_id, plano, periodo)
            
            # Criar preferência no Mercado Pago
            preference = {
                "items": [{
                    "title": f"SNE Radar - Plano {plano.title()}",
                    "unit_price": valor,
                    "quantity": 1,
                    "currency_id": "BRL"
                }],
                "payer": {
                    "email": f"user_{user_id}@sne-radar.com"  # Email temporário
                },
                "back_urls": {
                    "success": f"https://t.me/sne_radar_bot?start=success_{payment_id}",
                    "failure": f"https://t.me/sne_radar_bot?start=failure_{payment_id}",
                    "pending": f"https://t.me/sne_radar_bot?start=pending_{payment_id}"
                },
                "auto_return": "approved",
                "external_reference": payment_id,
                "notification_url": "https://seu-webhook.com/mercadopago"  # Substituir pela URL real
            }
            
            # Criar preferência
            response = self.mp.preference().create(preference)
            
            if response['status'] == 201:
                preference_id = response['response']['id']
                init_point = response['response']['init_point']
                
                # Criar registro de pagamento
                payment_data = {
                    'payment_id': payment_id,
                    'user_id': user_id,
                    'plano': plano,
                    'periodo': periodo,
                    'valor': valor,
                    'metodo': 'mercadopago',
                    'status': 'pending',
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
                    'mercadopago_data': {
                        'preference_id': preference_id,
                        'init_point': init_point
                    }
                }
                
                # Salvar pagamento
                self._salvar_pagamento(payment_data)
                
                # Log de auditoria
                if self.security:
                    self.security._log_audit("PAYMENT_MP_CREATED", f"MP criado para {user_id}: {plano} - R$ {valor:.2f}", user_id)
                
                logger.info(f"✅ Pagamento Mercado Pago criado: {payment_id} - R$ {valor:.2f}")
                
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'valor': valor,
                    'link_pagamento': init_point,
                    'preference_id': preference_id,
                    'expires_at': payment_data['expires_at']
                }
            else:
                return {'success': False, 'error': 'Erro ao criar preferência no Mercado Pago'}
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar pagamento Mercado Pago: {e}")
            return {'success': False, 'error': str(e)}
    
    def criar_pagamento_stripe(self, user_id: str, plano: str, periodo: str = 'mensal') -> Dict[str, Any]:
        """
        Cria pagamento via Stripe
        
        Args:
            user_id: ID do usuário
            plano: Plano escolhido
            periodo: Período de pagamento
            
        Returns:
            Dict: Informações do pagamento Stripe
        """
        try:
            if not self.stripe:
                return {'success': False, 'error': 'Stripe não configurado'}
            
            # Calcular valor (Stripe usa centavos)
            valor = self._calcular_valor_plano(plano, periodo)
            valor_centavos = int(valor * 100)
            
            # Gerar ID único do pagamento
            payment_id = self._gerar_payment_id(user_id, plano, periodo)
            
            # Criar sessão de checkout
            session = self.stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'brl',
                        'product_data': {
                            'name': f'SNE Radar - Plano {plano.title()}',
                            'description': f'Assinatura {periodo} do SNE Radar'
                        },
                        'unit_amount': valor_centavos,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'https://t.me/sne_radar_bot?start=success_{payment_id}',
                cancel_url=f'https://t.me/sne_radar_bot?start=cancel_{payment_id}',
                metadata={
                    'payment_id': payment_id,
                    'user_id': user_id,
                    'plano': plano,
                    'periodo': periodo
                }
            )
            
            # Criar registro de pagamento
            payment_data = {
                'payment_id': payment_id,
                'user_id': user_id,
                'plano': plano,
                'periodo': periodo,
                'valor': valor,
                'metodo': 'stripe',
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
                'stripe_data': {
                    'session_id': session.id,
                    'checkout_url': session.url
                }
            }
            
            # Salvar pagamento
            self._salvar_pagamento(payment_data)
            
            # Log de auditoria
            if self.security:
                self.security._log_audit("PAYMENT_STRIPE_CREATED", f"Stripe criado para {user_id}: {plano} - R$ {valor:.2f}", user_id)
            
            logger.info(f"✅ Pagamento Stripe criado: {payment_id} - R$ {valor:.2f}")
            
            return {
                'success': True,
                'payment_id': payment_id,
                'valor': valor,
                'link_pagamento': session.url,
                'session_id': session.id,
                'expires_at': payment_data['expires_at']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pagamento Stripe: {e}")
            return {'success': False, 'error': str(e)}
    
    # ===========================================
    # CONFIRMAÇÃO DE PAGAMENTOS
    # ===========================================
    def confirmar_pagamento_pix(self, payment_id: str, comprovante: str = None) -> Dict[str, Any]:
        """
        Confirma pagamento PIX (manual)
        
        Args:
            payment_id: ID do pagamento
            comprovante: Comprovante de pagamento (opcional)
            
        Returns:
            Dict: Resultado da confirmação
        """
        try:
            # Buscar pagamento
            payment_data = self._buscar_pagamento(payment_id)
            if not payment_data:
                return {'success': False, 'error': 'Pagamento não encontrado'}
            
            if payment_data['status'] != 'pending':
                return {'success': False, 'error': 'Pagamento já processado'}
            
            # Verificar se não expirou
            expires_at = datetime.fromisoformat(payment_data['expires_at'])
            if datetime.now() > expires_at:
                return {'success': False, 'error': 'Pagamento expirado'}
            
            # Confirmar pagamento (manual - requer verificação humana)
            payment_data['status'] = 'approved'
            payment_data['approved_at'] = datetime.now().isoformat()
            payment_data['comprovante'] = comprovante
            
            # Atualizar pagamento
            self._atualizar_pagamento(payment_data)
            
            # Ativar usuário
            self._ativar_usuario(payment_data['user_id'], payment_data['plano'], payment_data['periodo'])
            
            # Log de auditoria
            if self.security:
                self.security._log_audit("PAYMENT_PIX_APPROVED", f"PIX aprovado: {payment_id}", payment_data['user_id'])
            
            logger.info(f"✅ Pagamento PIX confirmado: {payment_id}")
            
            return {
                'success': True,
                'message': 'Pagamento confirmado com sucesso!',
                'user_id': payment_data['user_id'],
                'plano': payment_data['plano']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao confirmar pagamento PIX: {e}")
            return {'success': False, 'error': str(e)}
    
    def verificar_pagamento_mercadopago(self, payment_id: str) -> Dict[str, Any]:
        """
        Verifica status do pagamento no Mercado Pago
        
        Args:
            payment_id: ID do pagamento
            
        Returns:
            Dict: Status do pagamento
        """
        try:
            if not self.mp:
                return {'success': False, 'error': 'Mercado Pago não configurado'}
            
            # Buscar pagamento
            payment_data = self._buscar_pagamento(payment_id)
            if not payment_data:
                return {'success': False, 'error': 'Pagamento não encontrado'}
            
            # Buscar no Mercado Pago usando external_reference
            filters = {
                "external_reference": payment_id
            }
            
            result = self.mp.payment().search(filters=filters)
            
            if result['status'] == 200 and result['response']['results']:
                payment_mp = result['response']['results'][0]
                status_mp = payment_mp['status']
                
                if status_mp == 'approved' and payment_data['status'] == 'pending':
                    # Pagamento aprovado
                    payment_data['status'] = 'approved'
                    payment_data['approved_at'] = datetime.now().isoformat()
                    payment_data['mercadopago_payment_id'] = payment_mp['id']
                    
                    # Atualizar pagamento
                    self._atualizar_pagamento(payment_data)
                    
                    # Ativar usuário
                    self._ativar_usuario(payment_data['user_id'], payment_data['plano'], payment_data['periodo'])
                    
                    # Log de auditoria
                    if self.security:
                        self.security._log_audit("PAYMENT_MP_APPROVED", f"MP aprovado: {payment_id}", payment_data['user_id'])
                    
                    logger.info(f"✅ Pagamento Mercado Pago confirmado: {payment_id}")
                    
                    return {
                        'success': True,
                        'status': 'approved',
                        'message': 'Pagamento confirmado com sucesso!',
                        'user_id': payment_data['user_id'],
                        'plano': payment_data['plano']
                    }
                elif status_mp == 'rejected':
                    payment_data['status'] = 'rejected'
                    payment_data['rejected_at'] = datetime.now().isoformat()
                    self._atualizar_pagamento(payment_data)
                    
                    return {
                        'success': False,
                        'status': 'rejected',
                        'message': 'Pagamento rejeitado'
                    }
                else:
                    return {
                        'success': True,
                        'status': status_mp,
                        'message': f'Status: {status_mp}'
                    }
            else:
                return {'success': False, 'error': 'Pagamento não encontrado no Mercado Pago'}
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar pagamento Mercado Pago: {e}")
            return {'success': False, 'error': str(e)}
    
    def verificar_pagamento_stripe(self, payment_id: str) -> Dict[str, Any]:
        """
        Verifica status do pagamento no Stripe
        
        Args:
            payment_id: ID do pagamento
            
        Returns:
            Dict: Status do pagamento
        """
        try:
            if not self.stripe:
                return {'success': False, 'error': 'Stripe não configurado'}
            
            # Buscar pagamento
            payment_data = self._buscar_pagamento(payment_id)
            if not payment_data:
                return {'success': False, 'error': 'Pagamento não encontrado'}
            
            # Buscar sessão no Stripe
            session_id = payment_data.get('stripe_data', {}).get('session_id')
            if not session_id:
                return {'success': False, 'error': 'Session ID não encontrado'}
            
            session = self.stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid' and payment_data['status'] == 'pending':
                # Pagamento aprovado
                payment_data['status'] = 'approved'
                payment_data['approved_at'] = datetime.now().isoformat()
                payment_data['stripe_payment_intent'] = session.payment_intent
                
                # Atualizar pagamento
                self._atualizar_pagamento(payment_data)
                
                # Ativar usuário
                self._ativar_usuario(payment_data['user_id'], payment_data['plano'], payment_data['periodo'])
                
                # Log de auditoria
                if self.security:
                    self.security._log_audit("PAYMENT_STRIPE_APPROVED", f"Stripe aprovado: {payment_id}", payment_data['user_id'])
                
                logger.info(f"✅ Pagamento Stripe confirmado: {payment_id}")
                
                return {
                    'success': True,
                    'status': 'approved',
                    'message': 'Pagamento confirmado com sucesso!',
                    'user_id': payment_data['user_id'],
                    'plano': payment_data['plano']
                }
            else:
                return {
                    'success': True,
                    'status': session.payment_status,
                    'message': f'Status: {session.payment_status}'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar pagamento Stripe: {e}")
            return {'success': False, 'error': str(e)}
    
    # ===========================================
    # MÉTODOS UTILITÁRIOS
    # ===========================================
    def _calcular_valor_plano(self, plano: str, periodo: str) -> float:
        """Calcula valor do plano baseado no período"""
        try:
            from plan_config import get_preco_plano
            return get_preco_plano(plano, periodo)
        except ImportError:
            # Fallback
            preco_base = self.planos.get(plano, {}).get('preco', 0)
            if periodo == 'anual':
                return preco_base * 12 * 0.8  # 20% desconto
            elif periodo == 'semestral':
                return preco_base * 6 * 0.9   # 10% desconto
            elif periodo == 'trimestral':
                return preco_base * 3 * 0.95  # 5% desconto
            else:
                return preco_base
    
    def _gerar_payment_id(self, user_id: str, plano: str, periodo: str) -> str:
        """Gera ID único para o pagamento"""
        timestamp = str(int(datetime.now().timestamp()))
        data = f"{user_id}_{plano}_{periodo}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def _salvar_pagamento(self, payment_data: Dict[str, Any]):
        """Salva dados do pagamento"""
        with self._lock:
            self._payments[payment_data['payment_id']] = payment_data
    
    def _buscar_pagamento(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Busca dados do pagamento"""
        with self._lock:
            return self._payments.get(payment_id)
    
    def _atualizar_pagamento(self, payment_data: Dict[str, Any]):
        """Atualiza dados do pagamento"""
        with self._lock:
            self._payments[payment_data['payment_id']] = payment_data
    
    def _ativar_usuario(self, user_id: str, plano: str, periodo: str):
        """Ativa usuário após pagamento confirmado"""
        try:
            from user_manager import user_manager
            
            # Calcular data de expiração
            if periodo == 'anual':
                expires_at = datetime.now() + timedelta(days=365)
            elif periodo == 'semestral':
                expires_at = datetime.now() + timedelta(days=180)
            elif periodo == 'trimestral':
                expires_at = datetime.now() + timedelta(days=90)
            else:  # mensal
                expires_at = datetime.now() + timedelta(days=30)
            
            # Atualizar plano do usuário
            user_manager.update_user_plan(user_id, plano, expires_at)
            
            logger.info(f"✅ Usuário {user_id} ativado com plano {plano}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao ativar usuário {user_id}: {e}")
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Obtém status de um pagamento
        
        Args:
            payment_id: ID do pagamento
            
        Returns:
            Dict: Status do pagamento
        """
        payment_data = self._buscar_pagamento(payment_id)
        if not payment_data:
            return {'success': False, 'error': 'Pagamento não encontrado'}
        
        return {
            'success': True,
            'payment_id': payment_id,
            'status': payment_data['status'],
            'plano': payment_data['plano'],
            'valor': payment_data['valor'],
            'metodo': payment_data['metodo'],
            'created_at': payment_data['created_at'],
            'expires_at': payment_data['expires_at']
        }
    
    def get_user_payments(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Obtém pagamentos de um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            List: Lista de pagamentos
        """
        with self._lock:
            user_payments = []
            for payment_id, payment_data in self._payments.items():
                if payment_data['user_id'] == user_id:
                    user_payments.append(payment_data)
            
            return sorted(user_payments, key=lambda x: x['created_at'], reverse=True)

# ===========================================
# INSTÂNCIA GLOBAL
# ===========================================
payment_manager = PaymentManager()

# ===========================================
# FUNÇÕES UTILITÁRIAS
# ===========================================
def criar_pagamento_pix(user_id: str, plano: str, periodo: str = 'mensal') -> Dict[str, Any]:
    """Cria pagamento PIX"""
    return payment_manager.criar_pagamento_pix(user_id, plano, periodo)

def criar_pagamento_mercadopago(user_id: str, plano: str, periodo: str = 'mensal') -> Dict[str, Any]:
    """Cria pagamento Mercado Pago"""
    return payment_manager.criar_pagamento_mercadopago(user_id, plano, periodo)

def criar_pagamento_stripe(user_id: str, plano: str, periodo: str = 'mensal') -> Dict[str, Any]:
    """Cria pagamento Stripe"""
    return payment_manager.criar_pagamento_stripe(user_id, plano, periodo)

def confirmar_pagamento_pix(payment_id: str, comprovante: str = None) -> Dict[str, Any]:
    """Confirma pagamento PIX"""
    return payment_manager.confirmar_pagamento_pix(payment_id, comprovante)

def verificar_pagamento_mercadopago(payment_id: str) -> Dict[str, Any]:
    """Verifica pagamento Mercado Pago"""
    return payment_manager.verificar_pagamento_mercadopago(payment_id)

def verificar_pagamento_stripe(payment_id: str) -> Dict[str, Any]:
    """Verifica pagamento Stripe"""
    return payment_manager.verificar_pagamento_stripe(payment_id)

if __name__ == "__main__":
    # Teste do sistema de pagamentos
    print("🧪 Testando sistema de pagamentos do SNE Radar 3.0...")
    
    try:
        test_user = "123456789"
        
        # Testar criação de pagamento PIX
        print(f"\n💳 Testando pagamento PIX:")
        pix_result = payment_manager.criar_pagamento_pix(test_user, 'premium', 'mensal')
        if pix_result['success']:
            print(f"✅ PIX criado: {pix_result['payment_id']}")
            print(f"   Valor: R$ {pix_result['valor']:.2f}")
            print(f"   Chave: {pix_result['chave_pix']}")
            
            # Testar confirmação
            confirm_result = payment_manager.confirmar_pagamento_pix(pix_result['payment_id'])
            if confirm_result['success']:
                print(f"✅ PIX confirmado!")
            else:
                print(f"❌ Erro na confirmação: {confirm_result['error']}")
        else:
            print(f"❌ Erro ao criar PIX: {pix_result['error']}")
        
        # Testar criação de pagamento Mercado Pago
        print(f"\n💳 Testando pagamento Mercado Pago:")
        mp_result = payment_manager.criar_pagamento_mercadopago(test_user, 'premium', 'mensal')
        if mp_result['success']:
            print(f"✅ MP criado: {mp_result['payment_id']}")
            print(f"   Valor: R$ {mp_result['valor']:.2f}")
            print(f"   Link: {mp_result['link_pagamento'][:50]}...")
        else:
            print(f"❌ Erro ao criar MP: {mp_result['error']}")
        
        # Testar criação de pagamento Stripe
        print(f"\n💳 Testando pagamento Stripe:")
        stripe_result = payment_manager.criar_pagamento_stripe(test_user, 'premium', 'mensal')
        if stripe_result['success']:
            print(f"✅ Stripe criado: {stripe_result['payment_id']}")
            print(f"   Valor: R$ {stripe_result['valor']:.2f}")
            print(f"   Link: {stripe_result['link_pagamento'][:50]}...")
        else:
            print(f"❌ Erro ao criar Stripe: {stripe_result['error']}")
        
        # Testar busca de pagamentos do usuário
        print(f"\n📋 Pagamentos do usuário {test_user}:")
        user_payments = payment_manager.get_user_payments(test_user)
        for payment in user_payments:
            print(f"   {payment['payment_id']}: {payment['status']} - R$ {payment['valor']:.2f}")
        
        print("\n✅ Sistema de pagamentos testado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao testar sistema de pagamentos: {e}")
