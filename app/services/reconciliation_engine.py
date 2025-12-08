#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Reconciliação
Sincroniza dados locais com Binance
"""

from typing import Dict, List
from datetime import datetime
from decimal import Decimal
from app.models.trading_models import (
    Position, Order, ReconciliationLog, db
)
from app.services.executors.exchange_adapter import get_exchange_adapter
from app.services.compliance_engine import ComplianceEngine
from app.services.risk_manager import RiskManager


class ReconciliationEngine:
    """
    Motor de reconciliação que sincroniza dados locais com exchange
    """
    
    def __init__(self, db_session=None):
        self.adapter = get_exchange_adapter()  # Usa ExchangeAdapter
        self.db = db_session or db
        self.compliance = ComplianceEngine(db_session)
        self.risk_manager = RiskManager(db_session)
    
    def run_full_reconciliation(self, user_id: int) -> Dict:
        """
        Executa reconciliação completa:
        1. Posições
        2. Ordens pendentes
        3. Balances
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dict: Resultados da reconciliação
        """
        results = {
            'positions': self.reconcile_positions(user_id),
            'orders': self.reconcile_orders(user_id),
            'balance': self.reconcile_balance(user_id),
            'timestamp': datetime.utcnow()
        }
        return results
    
    def reconcile_positions(self, user_id: int) -> Dict:
        """
        Reconcilia posições abertas
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dict: Resultado da reconciliação
        """
        try:
            # 1. Buscar posições da exchange
            exchange_positions = self.adapter.get_positions()
            
            # 2. Buscar posições do DB
            db_positions = Position.query.filter_by(
                user_id=user_id,
                reconciliation_status='pending'
            ).all()
            
            # 3. Comparar
            discrepancies = []
            synced_count = 0
            
            for exchange_pos in exchange_positions:
                symbol = exchange_pos.get('symbol')
                db_pos = next((p for p in db_positions if p.symbol == symbol), None)
                
                if not db_pos:
                    # Posição na exchange que não está no DB
                    discrepancies.append({
                        'type': 'missing_in_db',
                        'symbol': symbol,
                        'exchange_data': exchange_pos
                    })
                elif self._compare_positions(db_pos, exchange_pos):
                    # Discrepância encontrada
                    discrepancies.append({
                        'type': 'discrepancy',
                        'symbol': symbol,
                        'db_data': self._position_to_dict(db_pos),
                        'exchange_data': exchange_pos
                    })
                else:
                    # Sincronizado
                    db_pos.reconciliation_status = 'synced'
                    db_pos.last_reconciled = datetime.utcnow()
                    synced_count += 1
            
            # 4. Processar discrepâncias
            for disc in discrepancies:
                self._handle_discrepancy(disc, 'position', user_id)
            
            self.db.session.commit()
            
            return {
                'checked': len(exchange_positions),
                'synced': synced_count,
                'discrepancies': len(discrepancies)
            }
            
        except Exception as e:
            self._log_reconciliation_error('position', str(e), user_id)
            return {'error': str(e)}
    
    def reconcile_orders(self, user_id: int) -> Dict:
        """
        Reconcilia ordens pendentes usando client_order_id
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dict: Resultado da reconciliação
        """
        try:
            # 1. Buscar ordens pendentes no DB
            pending_orders = Order.query.filter_by(
                user_id=user_id,
                status='pending',
                reconciliation_status='pending'
            ).all()
            
            synced_count = 0
            discrepancies = []
            
            for order in pending_orders:
                try:
                    # 2. Verificar na exchange usando client_order_id
                    exchange_order = self.adapter.get_order_status(
                        symbol=order.symbol,
                        client_order_id=order.client_order_id
                    )
                    
                    if exchange_order and exchange_order.get('status') != 'NotFound':
                        # 3. Ordem existe na exchange - atualizar DB
                        order.exchange_order_id = str(exchange_order.get('order_id', ''))
                        order.status = self._map_exchange_status(exchange_order.get('status', ''))
                        order.filled_quantity = Decimal(str(exchange_order.get('filled_qty', 0)))
                        order.filled_price = Decimal(str(exchange_order.get('price', 0))) if exchange_order.get('price') else None
                        order.reconciliation_status = 'synced'
                        order.last_reconciled = datetime.utcnow()
                        synced_count += 1
                        
                        # Log de reconciliação
                        self._log_reconciliation(
                            'order',
                            'success',
                            {
                                'client_order_id': order.client_order_id,
                                'exchange_order_id': order.exchange_order_id,
                                'action': f'updated_from_{order.exchange_name}'
                            },
                            user_id
                        )
                    else:
                        # 4. Ordem NÃO existe na exchange - possível falha no envio
                        order.reconciliation_status = 'discrepancy'
                        order.last_reconciled = datetime.utcnow()
                        
                        discrepancies.append({
                            'type': 'missing_in_exchange',
                            'client_order_id': order.client_order_id,
                            'symbol': order.symbol
                        })
                        
                        # Gerar alerta crítico
                        self._handle_discrepancy(
                            {
                                'type': 'missing_in_exchange',
                                'client_order_id': order.client_order_id,
                                'symbol': order.symbol,
                                'message': f'Ordem existe no DB mas não na {order.exchange_name}'
                            },
                            'order',
                            user_id
                        )
                        
                except Exception as e:
                    discrepancies.append({
                        'type': 'error',
                        'client_order_id': order.client_order_id,
                        'error': str(e)
                    })
            
            self.db.session.commit()
            
            return {
                'checked': len(pending_orders),
                'synced': synced_count,
                'discrepancies': len(discrepancies)
            }
            
        except Exception as e:
            self._log_reconciliation_error('order', str(e), user_id)
            return {'error': str(e)}
    
    def reconcile_balance(self, user_id: int) -> Dict:
        """
        Reconcilia saldo da conta
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dict: Resultado da reconciliação
        """
        try:
            balance = self.adapter.get_balance("USDT")
            # TODO: Comparar com Portfolio no DB
            return {'status': 'success', 'balance': balance}
        except Exception as e:
            self._log_reconciliation_error('balance', str(e), user_id)
            return {'error': str(e)}
    
    def _map_exchange_status(self, exchange_status: str) -> str:
        """
        Mapeia status da exchange para status interno
        
        Args:
            exchange_status: Status retornado pela exchange
            
        Returns:
            str: Status padronizado
        """
        status_map = {
            # Bybit
            'New': 'pending',
            'PartiallyFilled': 'partially_filled',
            'Filled': 'filled',
            'Cancelled': 'cancelled',
            'Rejected': 'rejected',
            # Binance (se ainda usar)
            'NEW': 'pending',
            'PARTIALLY_FILLED': 'partially_filled',
            'FILLED': 'filled',
            'CANCELED': 'cancelled',
            'REJECTED': 'rejected',
        }
        return status_map.get(exchange_status, 'pending')
    
    def _compare_positions(self, db_pos: Position, binance_pos: Dict) -> bool:
        """Compara posição do DB com posição da Binance"""
        # TODO: Implementar comparação detalhada
        return False
    
    def _position_to_dict(self, position: Position) -> Dict:
        """Converte Position para dict"""
        return {
            'id': position.id,
            'symbol': position.symbol,
            'side': position.side,
            'quantity': float(position.quantity),
            'entry_price': float(position.entry_price),
            'current_price': float(position.current_price) if position.current_price else None,
        }
    
    def _handle_discrepancy(self, discrepancy: Dict, entity_type: str, user_id: int):
        """
        Trata discrepância encontrada
        """
        # 1. Log de auditoria
        self.compliance.log_discrepancy(
            entity_type=entity_type,
            entity_id=discrepancy.get('id'),
            user_id=user_id,
            discrepancy_details=discrepancy
        )
        
        # 2. Criar alerta de risco
        self.risk_manager.generate_risk_alert(
            type='reconciliation_failure',
            severity='critical',
            message=f"Discrepância encontrada em {entity_type}: {discrepancy.get('symbol', discrepancy.get('client_order_id', 'unknown'))}",
            user_id=user_id,
            details=discrepancy
        )
        
        # 3. Salvar log de reconciliação
        self._log_reconciliation(
            entity_type,
            'discrepancy',
            discrepancy,
            user_id,
            action_taken='alerted'
        )
    
    def _log_reconciliation(self, reconciliation_type: str, status: str, details: Dict,
                           user_id: int, action_taken: str = 'none'):
        """Registra log de reconciliação"""
        log = ReconciliationLog(
            reconciliation_type=reconciliation_type,
            status=status,
            details=details,
            action_taken=action_taken,
            timestamp=datetime.utcnow(),
            user_id=user_id
        )
        self.db.session.add(log)
        self.db.session.commit()
    
    def _log_reconciliation_error(self, reconciliation_type: str, error: str, user_id: int):
        """Registra erro na reconciliação"""
        self._log_reconciliation(
            reconciliation_type,
            'error',
            {'error': error},
            user_id,
            action_taken='none'
        )

