#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints para gestão de portfólio
"""

from flask import request, jsonify
from app.api.trading import trading_bp
from app.services.portfolio_manager import PortfolioManager
from app.services.executors.exchange_adapter import get_exchange_adapter
from flask_login import login_required, current_user
from decimal import Decimal


portfolio_manager = PortfolioManager()


@trading_bp.route('/portfolio', methods=['GET'])
@login_required
def get_portfolio():
    """Obtém visão geral do portfólio"""
    try:
        portfolio = portfolio_manager.get_portfolio(current_user.id)
        
        if not portfolio:
            return jsonify({
                'success': True,
                'portfolio': {
                    'total_balance': 0,
                    'available_balance': 0,
                    'equity': 0,
                    'unrealized_pnl': 0,
                    'realized_pnl': 0
                }
            }), 200
        
        return jsonify({
            'success': True,
            'portfolio': {
                'total_balance': float(portfolio.total_balance),
                'available_balance': float(portfolio.available_balance),
                'margin_used': float(portfolio.margin_used),
                'equity': float(portfolio.equity),
                'unrealized_pnl': float(portfolio.unrealized_pnl),
                'realized_pnl': float(portfolio.realized_pnl),
                'total_pnl': float(portfolio.total_pnl),
                'timestamp': portfolio.timestamp.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/portfolio/performance', methods=['GET'])
@login_required
def get_performance():
    """Obtém métricas de performance"""
    try:
        period_days = int(request.args.get('period_days', 30))
        metrics = portfolio_manager.calculate_performance_metrics(current_user.id, period_days)
        
        return jsonify({
            'success': True,
            'performance': metrics
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/portfolio/report', methods=['GET'])
@login_required
def get_report():
    """Gera relatório completo do portfólio"""
    try:
        period_days = int(request.args.get('period_days', 30))
        report = portfolio_manager.generate_report(current_user.id, period_days)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

