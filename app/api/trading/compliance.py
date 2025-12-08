#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints para compliance e auditoria
"""

from flask import request, jsonify
from app.api.trading import trading_bp
from app.models.trading_models import ComplianceLog, RiskAlert, db
from app.services.compliance_engine import ComplianceEngine
from flask_login import login_required, current_user
from datetime import datetime, timedelta


compliance = ComplianceEngine()


@trading_bp.route('/compliance/logs', methods=['GET'])
@login_required
def get_compliance_logs():
    """Obtém logs de compliance"""
    try:
        days = int(request.args.get('days', 7))
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        logs = compliance.generate_audit_log(start_date, end_date, current_user.id)
        
        return jsonify({
            'success': True,
            'logs': [{
                'id': log.id,
                'action': log.action,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'details': log.details,
                'amount': float(log.amount) if log.amount else None,
                'timestamp': log.timestamp.isoformat(),
                'ip_address': log.ip_address,
                'approved_by': log.approved_by
            } for log in logs]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/compliance/risk-alerts', methods=['GET'])
@login_required
def get_risk_alerts():
    """Obtém alertas de risco"""
    try:
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        
        query = RiskAlert.query.filter_by(user_id=current_user.id)
        if not resolved:
            query = query.filter_by(resolved=False)
        
        alerts = query.order_by(RiskAlert.created_at.desc()).limit(50).all()
        
        return jsonify({
            'success': True,
            'alerts': [{
                'id': a.id,
                'type': a.type,
                'severity': a.severity,
                'message': a.message,
                'details': a.details,
                'threshold_value': float(a.threshold_value) if a.threshold_value else None,
                'current_value': float(a.current_value) if a.current_value else None,
                'resolved': a.resolved,
                'created_at': a.created_at.isoformat()
            } for a in alerts]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


