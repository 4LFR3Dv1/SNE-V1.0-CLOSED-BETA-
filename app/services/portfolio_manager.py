#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Portfólio
Gerencia portfólio completo e calcula métricas
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.trading_models import Portfolio, Position, Trade, db
from app.models.trading_models import PRECISION_PNL, SCALE_PNL


class PortfolioManager:
    """
    Gerenciador de portfólio
    """
    
    def __init__(self, db_session=None):
        self.db = db_session or db
    
    def get_portfolio(self, user_id: int) -> Optional[Portfolio]:
        """Obtém portfólio do usuário"""
        return Portfolio.query.filter_by(user_id=user_id).first()
    
    def update_portfolio(self, user_id: int, total_balance: Decimal, 
                        available_balance: Decimal) -> Portfolio:
        """
        Atualiza snapshot do portfólio
        
        Args:
            user_id: ID do usuário
            total_balance: Saldo total
            available_balance: Saldo disponível
        
        Returns:
            Portfolio: Portfólio atualizado
        """
        portfolio = self.get_portfolio(user_id)
        
        # Calcular métricas
        positions = Position.query.filter_by(user_id=user_id).all()
        unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        margin_used = sum(pos.margin or Decimal('0.00') for pos in positions)
        
        # Calcular realized PnL (trades fechados hoje)
        today = datetime.utcnow().date()
        today_trades = Trade.query.filter(
            Trade.user_id == user_id,
            Trade.closed_at >= datetime.combine(today, datetime.min.time())
        ).all()
        realized_pnl = sum(trade.pnl for trade in today_trades)
        
        total_pnl = unrealized_pnl + realized_pnl
        equity = total_balance + unrealized_pnl
        
        if portfolio:
            # Atualizar existente
            portfolio.total_balance = total_balance
            portfolio.available_balance = available_balance
            portfolio.margin_used = margin_used
            portfolio.unrealized_pnl = unrealized_pnl
            portfolio.realized_pnl = realized_pnl
            portfolio.total_pnl = total_pnl
            portfolio.equity = equity
            portfolio.timestamp = datetime.utcnow()
        else:
            # Criar novo
            portfolio = Portfolio(
                user_id=user_id,
                total_balance=total_balance,
                available_balance=available_balance,
                margin_used=margin_used,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                total_pnl=total_pnl,
                equity=equity,
                timestamp=datetime.utcnow()
            )
            self.db.session.add(portfolio)
        
        self.db.session.commit()
        return portfolio
    
    def calculate_pnl(self, user_id: int) -> Dict:
        """
        Calcula P&L das posições abertas
        
        Returns:
            Dict: Métricas de P&L
        """
        positions = Position.query.filter_by(user_id=user_id).all()
        
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        total_unrealized_pnl_pct = sum(pos.unrealized_pnl_pct for pos in positions)
        
        return {
            'unrealized_pnl': total_unrealized_pnl,
            'unrealized_pnl_pct': total_unrealized_pnl_pct,
            'positions_count': len(positions)
        }
    
    def allocate_capital(self, strategy_id: int, amount: Decimal) -> bool:
        """
        Aloca capital para estratégia
        
        Args:
            strategy_id: ID da estratégia
            amount: Quantidade a alocar
        
        Returns:
            bool: True se alocado com sucesso
        """
        # TODO: Implementar lógica de alocação
        return True
    
    def calculate_performance_metrics(self, user_id: int, period_days: int = 30) -> Dict:
        """
        Calcula métricas de performance
        
        Args:
            user_id: ID do usuário
            period_days: Período em dias
        
        Returns:
            Dict: Métricas de performance
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Buscar trades do período
        trades = Trade.query.filter(
            Trade.user_id == user_id,
            Trade.closed_at >= start_date,
            Trade.closed_at <= end_date
        ).all()
        
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': Decimal('0.00'),
                'average_win': Decimal('0.00'),
                'average_loss': Decimal('0.00'),
                'profit_factor': Decimal('0.00')
            }
        
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]
        
        total_pnl = sum(t.pnl for t in trades)
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        total_wins = sum(t.pnl for t in winning_trades) if winning_trades else Decimal('0.00')
        total_losses = abs(sum(t.pnl for t in losing_trades)) if losing_trades else Decimal('0.00')
        
        average_win = total_wins / len(winning_trades) if winning_trades else Decimal('0.00')
        average_loss = total_losses / len(losing_trades) if losing_trades else Decimal('0.00')
        
        profit_factor = total_wins / total_losses if total_losses > 0 else Decimal('0.00')
        
        return {
            'total_trades': len(trades),
            'win_rate': float(win_rate),
            'total_pnl': total_pnl,
            'average_win': average_win,
            'average_loss': average_loss,
            'profit_factor': profit_factor,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades)
        }
    
    def generate_report(self, user_id: int, period_days: int = 30) -> Dict:
        """
        Gera relatório do portfólio
        
        Args:
            user_id: ID do usuário
            period_days: Período em dias
        
        Returns:
            Dict: Relatório completo
        """
        portfolio = self.get_portfolio(user_id)
        performance = self.calculate_performance_metrics(user_id, period_days)
        pnl = self.calculate_pnl(user_id)
        
        return {
            'portfolio': {
                'total_balance': float(portfolio.total_balance) if portfolio else 0,
                'available_balance': float(portfolio.available_balance) if portfolio else 0,
                'equity': float(portfolio.equity) if portfolio else 0,
                'unrealized_pnl': float(portfolio.unrealized_pnl) if portfolio else 0,
                'realized_pnl': float(portfolio.realized_pnl) if portfolio else 0,
            },
            'performance': {
                k: float(v) if isinstance(v, Decimal) else v
                for k, v in performance.items()
            },
            'pnl': {
                k: float(v) if isinstance(v, Decimal) else v
                for k, v in pnl.items()
            }
        }


