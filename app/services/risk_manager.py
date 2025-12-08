#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Risco
Valida trades antes de execução e monitora limites de risco
"""

from decimal import Decimal
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from app.models.trading_models import (
    RiskAlert, Portfolio, Position, Strategy, db,
    PRECISION_PERCENT, SCALE_PERCENT, PRECISION_PNL, SCALE_PNL
)


class RiskManager:
    """
    Gerenciador de risco institucional
    """
    
    # Limites de risco padrão
    RISK_LIMITS = {
        'max_position_size_pct': Decimal('20.00'),  # 20% do capital por posição
        'max_total_exposure_pct': Decimal('100.00'),  # 100% do capital total
        'max_daily_loss_pct': Decimal('5.00'),  # 5% de perda máxima diária
        'max_drawdown_pct': Decimal('15.00'),  # 15% de drawdown máximo
        'min_risk_reward_ratio': Decimal('1.50'),  # R:R mínimo 1.5:1
        'max_leverage': Decimal('10.00'),  # Alavancagem máxima 10x
    }
    
    def __init__(self, db_session=None, risk_limits: Optional[Dict] = None):
        self.db = db_session or db
        if risk_limits:
            self.RISK_LIMITS.update(risk_limits)
    
    def validate_trade(self, trade_data: Dict, portfolio: Optional[Portfolio] = None) -> Tuple[bool, Optional[str]]:
        """
        Valida trade antes de execução
        
        Args:
            trade_data: Dicionário com dados do trade
                - entry: Decimal (preço de entrada)
                - stop_loss: Decimal (stop loss)
                - take_profit: Decimal (take profit)
                - quantity: Decimal (quantidade)
                - symbol: str
                - user_id: int
            portfolio: Portfolio do usuário (opcional, busca se não fornecido)
        
        Returns:
            Tuple[bool, Optional[str]]: (aprovado, mensagem_erro)
        """
        user_id = trade_data.get('user_id')
        if not portfolio and user_id:
            portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        
        if not portfolio:
            return False, "Portfolio não encontrado"
        
        # 1. Validar Risk:Reward
        entry = Decimal(str(trade_data['entry']))
        stop_loss = Decimal(str(trade_data['stop_loss']))
        take_profit = Decimal(str(trade_data['take_profit']))
        
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk == 0:
            return False, "Stop loss igual ao preço de entrada"
        
        rr_ratio = reward / risk
        if rr_ratio < self.RISK_LIMITS['min_risk_reward_ratio']:
            return False, f"R:R {rr_ratio:.2f} abaixo do mínimo {self.RISK_LIMITS['min_risk_reward_ratio']}"
        
        # 2. Validar tamanho da posição
        quantity = Decimal(str(trade_data['quantity']))
        position_value = quantity * entry
        position_pct = (position_value / portfolio.equity) * Decimal('100.00')
        
        if position_pct > self.RISK_LIMITS['max_position_size_pct']:
            return False, f"Tamanho da posição {position_pct:.2f}% excede máximo {self.RISK_LIMITS['max_position_size_pct']}%"
        
        # 3. Validar exposição total
        total_exposure = self._calculate_total_exposure(user_id, portfolio)
        if total_exposure > self.RISK_LIMITS['max_total_exposure_pct']:
            return False, f"Exposição total {total_exposure:.2f}% excede máximo {self.RISK_LIMITS['max_total_exposure_pct']}%"
        
        # 4. Validar perda diária
        daily_loss = self._calculate_daily_loss(user_id)
        if daily_loss < -self.RISK_LIMITS['max_daily_loss_pct']:
            return False, f"Perda diária {abs(daily_loss):.2f}% excede máximo {self.RISK_LIMITS['max_daily_loss_pct']}%"
        
        # 5. Validar drawdown
        drawdown = self._calculate_drawdown(portfolio)
        if drawdown > self.RISK_LIMITS['max_drawdown_pct']:
            return False, f"Drawdown {drawdown:.2f}% excede máximo {self.RISK_LIMITS['max_drawdown_pct']}%"
        
        return True, None
    
    def calculate_position_size(self, entry: Decimal, stop_loss: Decimal, risk_pct: Decimal, equity: Decimal) -> Decimal:
        """
        Calcula tamanho da posição baseado no risco
        
        Args:
            entry: Preço de entrada
            stop_loss: Preço de stop loss
            risk_pct: Percentual de risco (ex: 1.0 para 1%)
            equity: Equity do portfólio
        
        Returns:
            Decimal: Quantidade da posição
        """
        risk_amount = equity * (risk_pct / Decimal('100.00'))
        risk_per_unit = abs(entry - stop_loss)
        
        if risk_per_unit == 0:
            return Decimal('0.00')
        
        quantity = risk_amount / risk_per_unit
        return quantity
    
    def check_risk_limits(self, portfolio: Portfolio) -> Dict[str, bool]:
        """
        Verifica se limites de risco estão sendo respeitados
        
        Returns:
            Dict com status de cada limite
        """
        user_id = portfolio.user_id
        
        # Calcular métricas
        total_exposure = self._calculate_total_exposure(user_id, portfolio)
        daily_loss = self._calculate_daily_loss(user_id)
        drawdown = self._calculate_drawdown(portfolio)
        
        return {
            'total_exposure_ok': total_exposure <= self.RISK_LIMITS['max_total_exposure_pct'],
            'daily_loss_ok': abs(daily_loss) <= self.RISK_LIMITS['max_daily_loss_pct'],
            'drawdown_ok': drawdown <= self.RISK_LIMITS['max_drawdown_pct'],
        }
    
    def generate_risk_alert(self, alert_type: str, severity: str, message: str, 
                           user_id: int, details: Optional[Dict] = None,
                           threshold_value: Optional[Decimal] = None,
                           current_value: Optional[Decimal] = None) -> RiskAlert:
        """
        Gera alerta de risco
        
        Args:
            alert_type: Tipo do alerta
            severity: Severidade ('low', 'medium', 'high', 'critical')
            message: Mensagem do alerta
            user_id: ID do usuário
            details: Detalhes adicionais (JSON)
            threshold_value: Valor do limite
            current_value: Valor atual
        
        Returns:
            RiskAlert: Alerta criado
        """
        alert = RiskAlert(
            type=alert_type,
            severity=severity,
            message=message,
            details=details or {},
            threshold_value=threshold_value,
            current_value=current_value,
            user_id=user_id,
            resolved=False
        )
        
        self.db.session.add(alert)
        self.db.session.commit()
        
        return alert
    
    def block_execution(self, reason: str) -> bool:
        """
        Bloqueia execução de trades (implementar lógica de bloqueio global)
        """
        # TODO: Implementar flag global de bloqueio
        return False
    
    def _calculate_total_exposure(self, user_id: int, portfolio: Portfolio) -> Decimal:
        """Calcula exposição total do portfólio"""
        positions = Position.query.filter_by(user_id=user_id).all()
        total_value = sum(pos.quantity * (pos.current_price or pos.entry_price) for pos in positions)
        
        if portfolio.equity == 0:
            return Decimal('0.00')
        
        return (total_value / portfolio.equity) * Decimal('100.00')
    
    def _calculate_daily_loss(self, user_id: int) -> Decimal:
        """Calcula perda do dia"""
        today = datetime.utcnow().date()
        # TODO: Implementar cálculo de perda diária baseado em trades do dia
        return Decimal('0.00')
    
    def _calculate_drawdown(self, portfolio: Portfolio) -> Decimal:
        """Calcula drawdown atual"""
        # TODO: Implementar cálculo de drawdown baseado em histórico
        return Decimal('0.00')


