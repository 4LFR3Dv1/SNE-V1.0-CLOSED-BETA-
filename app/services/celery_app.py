#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração Celery para filas assíncronas
"""

import os
from celery import Celery
from flask import Flask


def make_celery(app: Flask = None) -> Celery:
    """
    Cria e configura instância Celery
    
    Args:
        app: Flask app (opcional)
    
    Returns:
        Celery: Instância configurada
    """
    broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    celery = Celery(
        'sne_trading',
        broker=broker_url,
        backend=result_backend
    )
    
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_routes={
            'app.tasks.order_tasks.*': {'queue': 'high_priority'},
            'app.tasks.reconciliation_tasks.*': {'queue': 'low_priority'},
        },
        task_default_queue='normal',
        task_default_exchange='tasks',
        task_default_routing_key='normal',
    )
    
    if app:
        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context."""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery


# Criar instância global (será inicializada com app)
celery = None


