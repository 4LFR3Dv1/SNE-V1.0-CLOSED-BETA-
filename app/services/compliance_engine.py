#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Compliance
Registra todas as ações para auditoria
"""

from typing import Dict, Optional
from datetime import datetime
from flask import request
from app.models.trading_models import ComplianceLog, db
from app.models.trading_models import PRECISION_PNL, SCALE_PNL
from decimal import Decimal


class ComplianceEngine:
    """
    Motor de compliance e auditoria
    """
    
    def __init__(self, db_session=None):
        self.db = db_session or db
    
    def log_action(self, action: str, entity_type: str, entity_id: Optional[int],
                   user_id: int, details: Optional[Dict] = None,
                   amount: Optional[Decimal] = None,
                   approved_by: Optional[int] = None) -> ComplianceLog:
        """
        Registra ação para auditoria
        
        Args:
            action: Tipo de ação ('trade_executed', 'order_placed', 'strategy_started', etc)
            entity_type: Tipo de entidade ('order', 'position', 'strategy', etc)
            entity_id: ID da entidade
            user_id: ID do usuário que executou a ação
            details: Detalhes adicionais (JSON)
            amount: Valor monetário envolvido
            approved_by: ID do usuário que aprovou (se aplicável)
        
        Returns:
            ComplianceLog: Log criado
        """
        # Obter IP e User Agent da requisição
        ip_address = None
        user_agent = None
        
        try:
            if request:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent')
        except:
            pass  # Se não houver request context
        
        log = ComplianceLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            details=details or {},
            amount=amount,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            approved_by=approved_by,
            approved_at=datetime.utcnow() if approved_by else None
        )
        
        self.db.session.add(log)
        self.db.session.commit()
        
        return log
    
    def validate_compliance(self, trade_data: Dict) -> bool:
        """
        Valida se trade está em compliance
        
        Args:
            trade_data: Dados do trade
        
        Returns:
            bool: True se em compliance
        """
        # TODO: Implementar regras de compliance específicas
        return True
    
    def check_permissions(self, user_id: int, action: str) -> bool:
        """
        Verifica se usuário tem permissão para ação
        
        Args:
            user_id: ID do usuário
            action: Ação a ser executada
        
        Returns:
            bool: True se tem permissão
        """
        # TODO: Implementar sistema de permissões
        return True
    
    def generate_audit_log(self, start_date: datetime, end_date: datetime, 
                          user_id: Optional[int] = None) -> list:
        """
        Gera log de auditoria para período
        
        Args:
            start_date: Data inicial
            end_date: Data final
            user_id: ID do usuário (opcional, filtra se fornecido)
        
        Returns:
            list: Lista de logs
        """
        query = ComplianceLog.query.filter(
            ComplianceLog.timestamp >= start_date,
            ComplianceLog.timestamp <= end_date
        )
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(ComplianceLog.timestamp.desc()).all()
    
    def log_discrepancy(self, entity_type: str, entity_id: int, user_id: int,
                       discrepancy_details: Dict) -> ComplianceLog:
        """
        Registra discrepância encontrada na reconciliação
        
        Args:
            entity_type: Tipo de entidade
            entity_id: ID da entidade
            user_id: ID do usuário
            discrepancy_details: Detalhes da discrepância
        
        Returns:
            ComplianceLog: Log criado
        """
        return self.log_action(
            action='reconciliation_discrepancy',
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            details=discrepancy_details
        )


