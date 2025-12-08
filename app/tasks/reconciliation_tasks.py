#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tasks Celery para reconciliação periódica
"""

from app.services.celery_app import make_celery
from app.services.reconciliation_engine import ReconciliationEngine
from app.models.trading_models import User, Strategy, db


# Celery será inicializado quando app Flask estiver disponível
celery = None


def init_celery(app):
    """Inicializa Celery com Flask app"""
    global celery
    from app.services.celery_app import make_celery
    celery = make_celery(app)
    return celery


@celery.task
def run_reconciliation_task(user_id: int):
    """
    Task para executar reconciliação completa
    
    Args:
        user_id: ID do usuário
    """
    try:
        # ReconciliationEngine agora usa ExchangeAdapter internamente
        reconciliation = ReconciliationEngine(db.session)
        
        results = reconciliation.run_full_reconciliation(user_id)
        
        return {'status': 'success', 'user_id': user_id, 'results': results}
        
    except Exception as e:
        return {'status': 'error', 'user_id': user_id, 'error': str(e)}


@celery.task
def periodic_reconciliation():
    """
    Task periódica para reconciliar todos os usuários ativos
    """
    try:
        # Buscar todos os usuários com estratégias ativas
        users = User.query.join('strategies').filter(
            Strategy.status == 'active'
        ).distinct().all()
        
        results = []
        for user in users:
            try:
                # ReconciliationEngine agora usa ExchangeAdapter internamente
                reconciliation = ReconciliationEngine(db.session)
                result = reconciliation.run_full_reconciliation(user.id)
                results.append({'user_id': user.id, 'result': result})
            except Exception as e:
                results.append({'user_id': user.id, 'error': str(e)})
        
        return {'status': 'success', 'results': results}
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

