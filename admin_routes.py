#!/usr/bin/env python3
# -*- coding: utf-8
"""
Rotas administrativas para o SNE Radar Web
Adicionar este arquivo ao sne_radar_web.py para funcionalidades admin
"""

from flask import jsonify, render_template, request
from flask_login import login_required, current_user
from functools import wraps

# Estas variáveis serão importadas do arquivo principal
# app, db, User serão disponibilizados quando o arquivo for importado

def admin_required(f):
    """Decorator para verificar se o usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            return jsonify({'error': 'Acesso negado. Apenas administradores.'}), 403
        return f(*args, **kwargs)
    return decorated_function

# === ROTAS ADMINISTRATIVAS ===
# Adicionar estas rotas ao arquivo sne_radar_web.py

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Dashboard administrativo"""
    return render_template('admin_dashboard.html')

@app.route('/api/admin/users/stats')
@login_required
@admin_required
def api_admin_user_stats():
    """API para estatísticas gerais de usuários"""
    try:
        # Total de usuários
        total_usuarios = User.query.count()
        
        # Usuários por tier
        from sqlalchemy import func
        usuarios_por_tier = db.session.query(
            User.tier, 
            func.count(User.id).label('quantidade')
        ).group_by(User.tier).all()
        
        # Usuários ativos (últimos 30 dias)
        from datetime import datetime, timedelta
        data_limite = datetime.now() - timedelta(days=30)
        usuarios_ativos = User.query.filter(
            User.last_api_reset >= data_limite.date()
        ).count()
        
        # Usuários inativos
        usuarios_inativos = total_usuarios - usuarios_ativos
        
        # Taxa de atividade
        taxa_atividade = (usuarios_ativos / total_usuarios * 100) if total_usuarios > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_usuarios': total_usuarios,
                'usuarios_ativos': usuarios_ativos,
                'usuarios_inativos': usuarios_inativos,
                'taxa_atividade': round(taxa_atividade, 1),
                'por_tier': [
                    {
                        'tier': row.tier,
                        'quantidade': row.quantidade,
                        'porcentagem': round((row.quantidade / total_usuarios * 100), 1)
                    }
                    for row in usuarios_por_tier
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/list')
@login_required
@admin_required
def api_admin_users_list():
    """API para listar usuários com paginação"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        
        # Query base
        query = User.query
        
        # Filtro de busca
        if search:
            query = query.filter(User.username.ilike(f'%{search}%'))
        
        # Paginação
        pagination = query.order_by(User.last_api_reset.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        usuarios = []
        for user in pagination.items:
            usuarios.append({
                'id': user.id,
                'username': user.username,
                'tier': user.tier,
                'api_calls_today': user.api_calls_today,
                'last_api_reset': user.last_api_reset.isoformat() if user.last_api_reset else None,
                'subscription_expires': user.subscription_expires.isoformat() if user.subscription_expires else None,
                'has_api_key': bool(user.api_key)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'usuarios': usuarios,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/<int:user_id>')
@login_required
@admin_required
def api_admin_user_detail(user_id):
    """API para detalhes de um usuário específico"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Buscar assinaturas do usuário
        subscriptions = Subscription.query.filter_by(user_id=user_id).all()
        
        # Buscar alertas do usuário (se houver relacionamento)
        alerts = Alert.query.filter_by(user_id=user_id).all() if hasattr(Alert, 'user_id') else []
        
        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'tier': user.tier,
                'api_calls_today': user.api_calls_today,
                'last_api_reset': user.last_api_reset.isoformat() if user.last_api_reset else None,
                'subscription_expires': user.subscription_expires.isoformat() if user.subscription_expires else None,
                'has_api_key': bool(user.api_key),
                'subscriptions': [
                    {
                        'id': sub.id,
                        'tier': sub.tier,
                        'start_date': sub.start_date.isoformat(),
                        'end_date': sub.end_date.isoformat(),
                        'payment_method': sub.payment_method,
                        'amount': sub.amount,
                        'status': sub.status
                    }
                    for sub in subscriptions
                ],
                'alerts_count': len(alerts)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/<int:user_id>/tier', methods=['PUT'])
@login_required
@admin_required
def api_admin_update_user_tier(user_id):
    """API para atualizar tier de um usuário"""
    try:
        data = request.json
        new_tier = data.get('tier')
        
        if new_tier not in ['free', 'pro', 'institutional']:
            return jsonify({'success': False, 'error': 'Tier inválido'})
        
        user = User.query.get_or_404(user_id)
        old_tier = user.tier
        user.tier = new_tier
        
        # Se upgrade, definir data de expiração
        if new_tier in ['pro', 'institutional'] and old_tier == 'free':
            user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Tier do usuário {user.username} atualizado de {old_tier} para {new_tier}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/<int:user_id>/reset-api-calls', methods=['POST'])
@login_required
@admin_required
def api_admin_reset_user_api_calls(user_id):
    """API para resetar contador de API calls de um usuário"""
    try:
        user = User.query.get_or_404(user_id)
        user.api_calls_today = 0
        user.last_api_reset = datetime.date.today()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Contador de API calls do usuário {user.username} foi resetado'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/system/stats')
@login_required
@admin_required
def api_admin_system_stats():
    """API para estatísticas do sistema"""
    try:
        # Estatísticas gerais
        total_users = User.query.count()
        total_alerts = Alert.query.count()
        total_market_data = MarketData.query.count()
        
        # Usuários por tier
        from sqlalchemy import func
        users_by_tier = db.session.query(
            User.tier, 
            func.count(User.id).label('count')
        ).group_by(User.tier).all()
        
        # Alertas por tipo
        alerts_by_type = db.session.query(
            Alert.tipo, 
            func.count(Alert.id).label('count')
        ).group_by(Alert.tipo).all()
        
        # Dados de mercado por símbolo
        market_data_by_symbol = db.session.query(
            MarketData.symbol, 
            func.count(MarketData.id).label('count')
        ).group_by(MarketData.symbol).all()
        
        return jsonify({
            'success': True,
            'data': {
                'users': {
                    'total': total_users,
                    'by_tier': [{'tier': row.tier, 'count': row.count} for row in users_by_tier]
                },
                'alerts': {
                    'total': total_alerts,
                    'by_type': [{'type': row.tipo, 'count': row.count} for row in alerts_by_type]
                },
                'market_data': {
                    'total': total_market_data,
                    'by_symbol': [{'symbol': row.symbol, 'count': row.count} for row in market_data_by_symbol]
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# === TEMPLATE ADMIN DASHBOARD ===
# Criar arquivo: templates/admin_dashboard.html

"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - SNE Radar</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { color: #7f8c8d; margin-top: 5px; }
        .section { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .section h3 { margin-top: 0; color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; margin: 2px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-warning { background: #f39c12; color: white; }
        .search-box { padding: 10px; border: 1px solid #ddd; border-radius: 5px; width: 300px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-shield-alt"></i> Admin Dashboard - SNE Radar</h1>
            <p>Painel administrativo para gerenciamento de usuários e sistema</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="total-users">-</div>
                <div class="stat-label">Total de Usuários</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="active-users">-</div>
                <div class="stat-label">Usuários Ativos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-alerts">-</div>
                <div class="stat-label">Total de Alertas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-market-data">-</div>
                <div class="stat-label">Dados de Mercado</div>
            </div>
        </div>
        
        <div class="section">
            <h3><i class="fas fa-users"></i> Gerenciamento de Usuários</h3>
            <input type="text" class="search-box" id="user-search" placeholder="Buscar usuário...">
            <div id="users-table-container">
                <table id="users-table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Tier</th>
                            <th>API Calls</th>
                            <th>Último Acesso</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody id="users-tbody">
                        <!-- Usuários serão carregados aqui -->
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="section">
            <h3><i class="fas fa-chart-pie"></i> Estatísticas por Tier</h3>
            <div id="tier-stats">
                <!-- Estatísticas por tier serão carregadas aqui -->
            </div>
        </div>
    </div>
    
    <script>
        // Carregar estatísticas ao iniciar
        document.addEventListener('DOMContentLoaded', function() {
            loadUserStats();
            loadUsersList();
            loadSystemStats();
        });
        
        // Busca de usuários
        document.getElementById('user-search').addEventListener('input', function(e) {
            const searchTerm = e.target.value;
            if (searchTerm.length >= 2 || searchTerm.length === 0) {
                loadUsersList(searchTerm);
            }
        });
        
        function loadUserStats() {
            fetch('/api/admin/users/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('total-users').textContent = data.data.total_usuarios;
                        document.getElementById('active-users').textContent = data.data.usuarios_ativos;
                        
                        // Atualizar estatísticas por tier
                        updateTierStats(data.data.por_tier);
                    }
                })
                .catch(error => console.error('Erro ao carregar estatísticas:', error));
        }
        
        function loadUsersList(search = '') {
            const url = search ? `/api/admin/users/list?search=${encodeURIComponent(search)}` : '/api/admin/users/list';
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateUsersTable(data.data.usuarios);
                    }
                })
                .catch(error => console.error('Erro ao carregar usuários:', error));
        }
        
        function loadSystemStats() {
            fetch('/api/admin/system/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('total-alerts').textContent = data.data.alerts.total;
                        document.getElementById('total-market-data').textContent = data.data.market_data.total;
                    }
                })
                .catch(error => console.error('Erro ao carregar estatísticas do sistema:', error));
        }
        
        function updateTierStats(tierStats) {
            const container = document.getElementById('tier-stats');
            container.innerHTML = '';
            
            tierStats.forEach(stat => {
                const div = document.createElement('div');
                div.style.cssText = 'display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; text-align: center;';
                div.innerHTML = `
                    <div style="font-size: 1.5em; font-weight: bold; color: #3498db;">${stat.quantidade}</div>
                    <div style="color: #7f8c8d;">${stat.tier.toUpperCase()}</div>
                    <div style="font-size: 0.9em; color: #95a5a6;">${stat.porcentagem}%</div>
                `;
                container.appendChild(div);
            });
        }
        
        function updateUsersTable(users) {
            const tbody = document.getElementById('users-tbody');
            tbody.innerHTML = '';
            
            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td><span class="badge badge-${user.tier}">${user.tier.toUpperCase()}</span></td>
                    <td>${user.api_calls_today}</td>
                    <td>${user.last_api_reset ? new Date(user.last_api_reset).toLocaleDateString('pt-BR') : 'Nunca'}</td>
                    <td>
                        <button class="btn btn-primary" onclick="viewUser(${user.id})">Ver</button>
                        <button class="btn btn-warning" onclick="resetApiCalls(${user.id})">Reset API</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function viewUser(userId) {
            fetch(`/api/admin/users/${userId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`Detalhes do usuário:\nUsername: ${data.data.username}\nTier: ${data.data.tier}\nAPI Calls: ${data.data.api_calls_today}`);
                    }
                })
                .catch(error => console.error('Erro ao carregar usuário:', error));
        }
        
        function resetApiCalls(userId) {
            if (confirm('Tem certeza que deseja resetar o contador de API calls deste usuário?')) {
                fetch(`/api/admin/users/${userId}/reset-api-calls`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            loadUsersList();
                            loadUserStats();
                        }
                    })
                    .catch(error => console.error('Erro ao resetar API calls:', error));
            }
        }
    </script>
</body>
</html>
"""
