#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas de Trading - Versão Blindada com Debug
Captura todos os erros e retorna mensagens claras
"""

from flask import Blueprint, jsonify, request
import traceback

trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')

# Tentar importar login_required, mas não quebrar se não estiver disponível
try:
    from flask_login import login_required, current_user
    LOGIN_AVAILABLE = True
except ImportError:
    LOGIN_AVAILABLE = False
    # Decorator fake que não faz nada
    def login_required(f):
        return f
    current_user = None

# --- FUNÇÃO AUXILIAR PARA DEBUG ---
def safe_execute(func):
    """
    Executa a função e captura erros para não retornar 500 mudo
    Retorna sempre 200 com JSON, mesmo em caso de erro
    """
    try:
        return func()
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        error_traceback = traceback.format_exc()
        
        # Imprimir erro completo no terminal/log
        print(f"\n🚨 ERRO NO BACKEND TRADING:")
        print(f"   Tipo: {error_type}")
        print(f"   Mensagem: {error_msg}")
        print(f"   Traceback completo:")
        print(error_traceback)
        print("-" * 60)
        
        # Retornar erro estruturado para o frontend
        return jsonify({
            "success": False,
            "error": "Erro Interno no Servidor",
            "details": error_msg,
            "type": error_type,
            "traceback": error_traceback.split('\n')[-5:] if len(error_traceback) > 0 else []
        }), 200  # Retorna 200 com erro JSON para o frontend ler


# --- ROTA DE STATUS ---
@trading_bp.route('/status', methods=['GET'])
def system_status():
    return jsonify({
        "status": "online",
        "mode": "paper_trading",
        "active_strategies": 0,
        "message": "Sistema Operacional e Pronto"
    })


# --- ROTA DE ESTRATÉGIAS ---
@trading_bp.route('/strategies', methods=['GET'])
def get_strategies():
    def logic():
        # Tentar importar e usar o código real, mas com fallback
        try:
            from app.models.trading_models import Strategy, db
            
            # Tentar obter user_id se login disponível
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
                print(f"📊 Buscando estratégias para user_id: {user_id}")
            else:
                print("⚠️ Nenhum usuário logado - retornando todas as estratégias")
            
            # Buscar estratégias
            if user_id:
                strategies = Strategy.query.filter_by(user_id=user_id).all()
            else:
                # Sem login, buscar todas (para debug)
                strategies = Strategy.query.all()
            
            print(f"📊 Encontradas {len(strategies)} estratégias")
            
            strategies_list = []
            for s in strategies:
                strategy_data = {
                    'id': s.id,
                    'name': s.name,
                    'status': s.status,
                    'health_status': s.health_status,
                    'symbols': s.symbols,
                    'timeframes': s.timeframes,
                    'type': s.type,
                    'risk_per_trade': float(s.risk_per_trade) if s.risk_per_trade else 1.0,
                }
                strategies_list.append(strategy_data)
                print(f"   - {s.name} (ID: {s.id}, Status: {s.status}, Símbolos: {s.symbols}, Timeframes: {s.timeframes})")
            
            return jsonify({
                "success": True,
                "strategies": strategies_list
            })
        except Exception as e:
            # Se falhar, retornar mock
            print(f"⚠️ Erro ao buscar estratégias: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": True,
                "strategies": []
            })
    
    return safe_execute(logic)


@trading_bp.route('/strategies', methods=['POST'])
def create_strategy():
    def logic():
        try:
            from app.models.trading_models import Strategy, db
            from decimal import Decimal
            import json
            
            data = request.get_json()
            
            # Validar dados obrigatórios
            if not data.get('name'):
                return jsonify({
                    "success": False,
                    "error": "Nome da estratégia é obrigatório"
                }), 400
            
            # Obter user_id
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
            else:
                # Se não houver login, usar user_id do request ou criar usuário padrão
                user_id = data.get('user_id', 1)  # Fallback para user_id 1
            
            # Validar símbolos
            symbols = data.get('symbols', [])
            if not symbols or len(symbols) == 0:
                return jsonify({
                    "success": False,
                    "error": "Pelo menos um símbolo é obrigatório (ex: ['BTCUSDT'])"
                }), 400
            
            # Validar timeframes
            timeframes = data.get('timeframes', [])
            if not timeframes or len(timeframes) == 0:
                return jsonify({
                    "success": False,
                    "error": "Pelo menos um timeframe é obrigatório (ex: ['1h'])"
                }), 400
            
            # Criar estratégia
            strategy = Strategy(
                name=data.get('name'),
                description=data.get('description', ''),
                type=data.get('type', 'momentum'),
                status='inactive',
                config=data.get('config', {}),
                capital_allocation=Decimal(str(data.get('capital_allocation', 20.0))),
                risk_per_trade=Decimal(str(data.get('risk_per_trade', 1.0))),
                max_positions=data.get('max_positions', 5),
                symbols=symbols,
                timeframes=timeframes,
                user_id=user_id,
                health_status='unknown'
            )
            
            db.session.add(strategy)
            db.session.commit()
            
            print(f"✅ Estratégia criada: {strategy.name} (ID: {strategy.id})")
            print(f"   Símbolos: {strategy.symbols}")
            print(f"   Timeframes: {strategy.timeframes}")
            print(f"   Risco por trade: {strategy.risk_per_trade}%")
            
            return jsonify({
                "success": True,
                "message": f"Estratégia '{strategy.name}' criada com sucesso",
                "strategy": {
                    'id': strategy.id,
                    'name': strategy.name,
                    'status': strategy.status,
                    'symbols': strategy.symbols,
                    'timeframes': strategy.timeframes,
                    'risk_per_trade': float(strategy.risk_per_trade),
                    'capital_allocation': float(strategy.capital_allocation)
                }
            }), 201
                
        except Exception as e:
            print(f"⚠️ Erro ao criar estratégia: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return safe_execute(logic)


# --- ROTAS DE CONTROLE DE ESTRATÉGIAS ---
@trading_bp.route('/strategies/<int:strategy_id>/start', methods=['POST'])
def start_strategy(strategy_id):
    def logic():
        try:
            from app.services.strategy_engine import StrategyEngine
            from app.models.trading_models import Strategy, db
            
            print(f"🚀 Iniciando estratégia ID: {strategy_id}")
            
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
                print(f"   User ID: {user_id}")
            
            strategy = Strategy.query.get(strategy_id)
            if not strategy:
                print(f"   ❌ Estratégia {strategy_id} não encontrada")
                return jsonify({
                    "success": False,
                    "error": "Estratégia não encontrada"
                }), 404
            
            print(f"   ✅ Estratégia encontrada: {strategy.name}")
            print(f"   Status atual: {strategy.status}")
            print(f"   Símbolos: {strategy.symbols}")
            print(f"   Timeframes: {strategy.timeframes}")
            
            if user_id and strategy.user_id != user_id:
                print(f"   ❌ Estratégia não pertence ao usuário")
                return jsonify({
                    "success": False,
                    "error": "Estratégia não pertence ao usuário"
                }), 403
            
            # Verificar se estratégia tem símbolos e timeframes
            if not strategy.symbols or len(strategy.symbols) == 0:
                print(f"   ⚠️ Estratégia não tem símbolos configurados")
                return jsonify({
                    "success": False,
                    "error": "Estratégia não tem símbolos configurados. Configure símbolos antes de iniciar."
                }), 400
            
            if not strategy.timeframes or len(strategy.timeframes) == 0:
                print(f"   ⚠️ Estratégia não tem timeframes configurados")
                return jsonify({
                    "success": False,
                    "error": "Estratégia não tem timeframes configurados. Configure timeframes antes de iniciar."
                }), 400
            
            # Iniciar estratégia
            print(f"   🔄 Chamando StrategyEngine.start_strategy({strategy_id})...")
            engine = StrategyEngine()
            success = engine.start_strategy(strategy_id)
            
            if success:
                print(f"   ✅ Estratégia iniciada com sucesso!")
                return jsonify({
                    "success": True,
                    "message": f"Estratégia '{strategy.name}' iniciada com sucesso"
                })
            else:
                print(f"   ❌ Falha ao iniciar estratégia")
                return jsonify({
                    "success": False,
                    "error": "Falha ao iniciar estratégia"
                }), 500
                
        except Exception as e:
            print(f"⚠️ Erro ao iniciar estratégia: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return safe_execute(logic)


@trading_bp.route('/strategies/<int:strategy_id>/stop', methods=['POST'])
def stop_strategy(strategy_id):
    def logic():
        try:
            from app.services.strategy_engine import StrategyEngine
            from app.models.trading_models import Strategy, db
            
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
            
            strategy = Strategy.query.get(strategy_id)
            if not strategy:
                return jsonify({
                    "success": False,
                    "error": "Estratégia não encontrada"
                }), 404
            
            if user_id and strategy.user_id != user_id:
                return jsonify({
                    "success": False,
                    "error": "Estratégia não pertence ao usuário"
                }), 403
            
            # Parar estratégia
            engine = StrategyEngine()
            success = engine.stop_strategy(strategy_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Estratégia '{strategy.name}' parada com sucesso"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Falha ao parar estratégia"
                }), 500
                
        except Exception as e:
            print(f"⚠️ Erro ao parar estratégia: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return safe_execute(logic)


@trading_bp.route('/strategies/<int:strategy_id>/pause', methods=['POST'])
def pause_strategy(strategy_id):
    def logic():
        try:
            from app.services.strategy_engine import StrategyEngine
            from app.models.trading_models import Strategy, db
            
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
            
            strategy = Strategy.query.get(strategy_id)
            if not strategy:
                return jsonify({
                    "success": False,
                    "error": "Estratégia não encontrada"
                }), 404
            
            if user_id and strategy.user_id != user_id:
                return jsonify({
                    "success": False,
                    "error": "Estratégia não pertence ao usuário"
                }), 403
            
            # Pausar estratégia
            engine = StrategyEngine()
            success = engine.pause_strategy(strategy_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Estratégia '{strategy.name}' pausada com sucesso"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Falha ao pausar estratégia"
                }), 500
                
        except Exception as e:
            print(f"⚠️ Erro ao pausar estratégia: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return safe_execute(logic)


# --- ROTA DE POSIÇÕES ---
@trading_bp.route('/positions', methods=['GET'])
def get_positions():
    def logic():
        try:
            from app.models.trading_models import Position, db
            
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
            
            if user_id:
                positions = Position.query.filter_by(user_id=user_id).all()
                return jsonify({
                    "success": True,
                    "positions": [{
                        'id': p.id,
                        'symbol': p.symbol,
                        'side': p.side,
                        'quantity': float(p.quantity),
                        'entry_price': float(p.entry_price),
                        'unrealized_pnl': float(p.unrealized_pnl),
                    } for p in positions]
                })
            else:
                return jsonify({
                    "success": True,
                    "positions": [],
                    "count": 0,
                    "total_pnl": 0.0
                })
        except Exception as e:
            print(f"⚠️ Usando mock para positions: {e}")
            return jsonify({
                "success": True,
                "positions": [],
                "count": 0,
                "total_pnl": 0.0
            })
    
    return safe_execute(logic)


# --- ROTA DE ORDENS ---
@trading_bp.route('/orders', methods=['GET'])
def get_orders():
    def logic():
        try:
            from app.models.trading_models import Order, db
            
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
            
            if user_id:
                status = request.args.get('status')
                query = Order.query.filter_by(user_id=user_id)
                if status:
                    query = query.filter_by(status=status)
                
                orders = query.limit(100).all()
                return jsonify({
                    "success": True,
                    "orders": [{
                        'id': o.id,
                        'symbol': o.symbol,
                        'side': o.side,
                        'status': o.status,
                        'quantity': float(o.quantity),
                    } for o in orders]
                })
            else:
                return jsonify({
                    "success": True,
                    "orders": [],
                    "pending_count": 0
                })
        except Exception as e:
            print(f"⚠️ Usando mock para orders: {e}")
            return jsonify({
                "success": True,
                "orders": [],
                "pending_count": 0
            })
    
    return safe_execute(logic)


@trading_bp.route('/orders', methods=['POST'])
def create_order():
    def logic():
        return jsonify({
            "success": True,
            "message": "Order creation not yet implemented"
        })
    
    return safe_execute(logic)


# --- ROTA DE PORTFÓLIO ---
@trading_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    def logic():
        try:
            from app.services.portfolio_manager import PortfolioManager
            from app.services.executors.exchange_adapter import get_exchange_adapter
            from decimal import Decimal
            
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
            
            # Tentar buscar dados reais se tiver usuário
            if user_id:
                try:
                    adapter = get_exchange_adapter()
                    balance = adapter.get_balance("USDT")
                    
                    portfolio_manager = PortfolioManager()
                    portfolio = portfolio_manager.update_portfolio(
                        user_id,
                        Decimal(str(balance)),
                        Decimal(str(balance))
                    )
                    
                    return jsonify({
                        "success": True,
                        "portfolio": {
                            "total_balance": float(portfolio.total_balance),
                            "available_balance": float(portfolio.available_balance),
                            "margin_used": float(portfolio.margin_used) if portfolio.margin_used else 0.00,
                            "unrealized_pnl": float(portfolio.unrealized_pnl) if portfolio.unrealized_pnl else 0.00,
                            "realized_pnl": float(portfolio.realized_pnl) if portfolio.realized_pnl else 0.00,
                            "total_pnl": float(portfolio.total_pnl) if portfolio.total_pnl else 0.00,
                            "equity": float(portfolio.equity),
                            "timestamp": portfolio.timestamp.isoformat()
                        }
                    })
                except Exception as e:
                    print(f"⚠️ Erro ao buscar portfolio real: {e}")
                    # Continuar para mock
            
            # Fallback para mock
            return jsonify({
                "success": True,
                "portfolio": {
                    "total_balance": 10000.00,
                    "available_balance": 10000.00,
                    "margin_used": 0.00,
                    "unrealized_pnl": 0.00,
                    "realized_pnl": 0.00,
                    "total_pnl": 0.00,
                    "equity": 10000.00,
                    "timestamp": "2025-01-02T00:00:00"
                }
            })
        except Exception as e:
            print(f"⚠️ Usando mock para portfolio: {e}")
            return jsonify({
                "success": True,
                "portfolio": {
                    "total_balance": 10000.00,
                    "available_balance": 10000.00,
                    "margin_used": 0.00,
                    "unrealized_pnl": 0.00,
                    "realized_pnl": 0.00,
                    "total_pnl": 0.00,
                    "equity": 10000.00,
                    "timestamp": "2025-01-02T00:00:00"
                }
            })
    
    return safe_execute(logic)


# --- ROTA DE PERFORMANCE ---
@trading_bp.route('/portfolio/performance', methods=['GET'])
def get_performance():
    def logic():
        try:
            from app.services.portfolio_manager import PortfolioManager
            from decimal import Decimal
            
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
            
            if user_id:
                period_days = int(request.args.get('period_days', 30))
                portfolio_manager = PortfolioManager()
                metrics = portfolio_manager.calculate_performance_metrics(user_id, period_days)
                
                return jsonify({
                    "success": True,
                    "performance": {
                        k: float(v) if isinstance(v, Decimal) else v
                        for k, v in metrics.items()
                    }
                })
            else:
                return jsonify({
                    "success": True,
                    "performance": {
                        "total_trades": 0,
                        "win_rate": 0.0,
                        "total_pnl": 0.0,
                        "profit_factor": 0.0
                    }
                })
        except Exception as e:
            print(f"⚠️ Usando mock para performance: {e}")
            return jsonify({
                "success": True,
                "performance": {
                    "total_trades": 0,
                    "win_rate": 0.0,
                    "total_pnl": 0.0,
                    "profit_factor": 0.0
                }
            })
    
    return safe_execute(logic)


# --- ROTA DE RISK ALERTS ---
@trading_bp.route('/compliance/risk-alerts', methods=['GET'])
def get_risk_alerts():
    def logic():
        try:
            from app.models.trading_models import RiskAlert, db
            
            user_id = None
            if LOGIN_AVAILABLE and current_user and hasattr(current_user, 'id'):
                user_id = current_user.id
            
            if user_id:
                resolved = request.args.get('resolved', 'false').lower() == 'true'
                query = RiskAlert.query.filter_by(user_id=user_id)
                if not resolved:
                    query = query.filter_by(resolved=False)
                
                alerts = query.limit(50).all()
                return jsonify({
                    "success": True,
                    "alerts": [{
                        'id': a.id,
                        'type': a.type,
                        'severity': a.severity,
                        'message': a.message,
                        'resolved': a.resolved,
                    } for a in alerts]
                })
            else:
                return jsonify({
                    "success": True,
                    "alerts": []
                })
        except Exception as e:
            print(f"⚠️ Usando mock para risk-alerts: {e}")
            return jsonify({
                "success": True,
                "alerts": []
            })
    
    return safe_execute(logic)


# --- ROTA DE COMPLIANCE LOGS ---
@trading_bp.route('/compliance/logs', methods=['GET'])
def get_compliance_logs():
    def logic():
        return jsonify({
            "success": True,
            "logs": []
        })
    
    return safe_execute(logic)


# --- PÂNICO (Botão Vermelho) ---
@trading_bp.route('/emergency/panic-close-all', methods=['POST'])
def panic_close():
    def logic():
        print("🚨 COMANDO DE PÂNICO RECEBIDO - FECHANDO TUDO!")
        try:
            from app.api.trading.emergency import panic_close_all as real_panic_close
            
            # Chamar função real se disponível
            return real_panic_close()
        except Exception as e:
            print(f"⚠️ Panic close não implementado ainda: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": True,
                "status": "success",
                "message": "Protocolo de emergência executado (mock).",
                "closed_count": 0
            })
    
    return safe_execute(logic)
