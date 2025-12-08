#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Estratégias
Executa estratégias automaticamente
"""

from typing import Dict, Optional
from datetime import datetime
import threading
import logging
import sys
import os
from decimal import Decimal

# Adicionar diretório raiz ao path para importar motor_renan
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.trading_models import Strategy, db
from app.services.order_manager import OrderManager
from app.services.risk_manager import RiskManager
from app.services.portfolio_manager import PortfolioManager

logger = logging.getLogger(__name__)


class StrategyEngine:
    """
    Motor de execução de estratégias
    """
    
    def __init__(self, db_session=None):
        self.db = db_session or db
        self.running_strategies = {}  # {strategy_id: thread}
        self.stop_flags = {}  # {strategy_id: bool}
        self.order_manager = OrderManager(db_session=db_session)
        self.risk_manager = RiskManager(db_session=db_session)
        self.portfolio_manager = PortfolioManager(db_session=db_session)
    
    def start_strategy(self, strategy_id: int) -> bool:
        """
        Inicia execução de estratégia
        
        Args:
            strategy_id: ID da estratégia
        
        Returns:
            bool: True se iniciada com sucesso
        """
        strategy = Strategy.query.get(strategy_id)
        if not strategy:
            return False
        
        if strategy.status == 'active':
            return True  # Já está ativa
        
        # Verificar se já está rodando
        if strategy_id in self.running_strategies:
            return True
        
        # Atualizar status
        strategy.status = 'active'
        strategy.health_status = 'healthy'
        self.db.session.commit()
        
        # Iniciar thread de execução
        stop_flag = threading.Event()
        self.stop_flags[strategy_id] = stop_flag
        
        thread = threading.Thread(
            target=self._execute_strategy_loop,
            args=(strategy_id, stop_flag),
            daemon=True
        )
        thread.start()
        
        self.running_strategies[strategy_id] = thread
        
        return True
    
    def stop_strategy(self, strategy_id: int) -> bool:
        """
        Para execução de estratégia
        
        Args:
            strategy_id: ID da estratégia
        
        Returns:
            bool: True se parada com sucesso
        """
        strategy = Strategy.query.get(strategy_id)
        if not strategy:
            return False
        
        # Parar thread
        if strategy_id in self.stop_flags:
            self.stop_flags[strategy_id].set()
            del self.stop_flags[strategy_id]
        
        if strategy_id in self.running_strategies:
            del self.running_strategies[strategy_id]
        
        # Atualizar status
        strategy.status = 'stopped'
        self.db.session.commit()
        
        return True
    
    def pause_strategy(self, strategy_id: int) -> bool:
        """
        Pausa execução de estratégia
        
        Args:
            strategy_id: ID da estratégia
        
        Returns:
            bool: True se pausada com sucesso
        """
        strategy = Strategy.query.get(strategy_id)
        if not strategy:
            return False
        
        strategy.status = 'paused'
        self.db.session.commit()
        
        return True
    
    def _execute_strategy_loop(self, strategy_id: int, stop_flag: threading.Event):
        """
        Loop de execução da estratégia (roda em thread separada)
        
        Args:
            strategy_id: ID da estratégia
            stop_flag: Event para parar execução
        """
        while not stop_flag.is_set():
            try:
                strategy = Strategy.query.get(strategy_id)
                if not strategy or strategy.status != 'active':
                    break
                
                # Executar estratégia
                self._execute_strategy(strategy)
                
                # Atualizar last_execution
                strategy.last_execution = datetime.utcnow()
                strategy.health_status = 'healthy'
                self.db.session.commit()
                
                # Aguardar antes da próxima execução
                stop_flag.wait(timeout=60)  # Executar a cada 60 segundos
                
            except Exception as e:
                # Registrar erro
                strategy = Strategy.query.get(strategy_id)
                if strategy:
                    strategy.last_error = datetime.utcnow()
                    strategy.error_count += 1
                    strategy.health_status = 'critical' if strategy.error_count > 5 else 'warning'
                    self.db.session.commit()
                
                # Aguardar antes de tentar novamente
                stop_flag.wait(timeout=300)  # 5 minutos em caso de erro
    
    def _execute_strategy(self, strategy: Strategy):
        """
        Executa uma iteração da estratégia
        
        Args:
            strategy: Objeto Strategy
        """
        try:
            logger.info(f"🔄 Executando estratégia: {strategy.name} (ID: {strategy.id})")
            
            # 1. Verificar se estratégia tem símbolos configurados
            if not strategy.symbols or len(strategy.symbols) == 0:
                logger.warning(f"⚠️ Estratégia {strategy.name} não tem símbolos configurados")
                return
            
            # 2. Verificar se estratégia tem timeframes configurados
            if not strategy.timeframes or len(strategy.timeframes) == 0:
                logger.warning(f"⚠️ Estratégia {strategy.name} não tem timeframes configurados")
                return
            
            # 3. Processar cada símbolo
            for symbol in strategy.symbols:
                try:
                    # Usar o primeiro timeframe como principal
                    primary_timeframe = strategy.timeframes[0] if strategy.timeframes else '1h'
                    
                    logger.info(f"   📊 Analisando {symbol} no timeframe {primary_timeframe}")
                    
                    # 4. Gerar sinal usando motor_renan.py
                    signal = self.generate_signal(strategy, symbol, primary_timeframe)
                    
                    if not signal:
                        logger.debug(f"   ⏸️ Nenhum sinal gerado para {symbol}")
                        continue
                    
                    if signal.get('action') == 'HOLD':
                        logger.debug(f"   ⏸️ Sinal HOLD para {symbol} - aguardando")
                        continue
                    
                    # 5. Validar trade com RiskManager
                    trade_data = {
                        'entry': Decimal(str(signal.get('entry_price', 0))),
                        'stop_loss': Decimal(str(signal.get('stop_loss', 0))),
                        'take_profit': Decimal(str(signal.get('take_profit', 0))),
                        'quantity': Decimal(str(signal.get('quantity', 0))),
                        'symbol': symbol,
                        'user_id': strategy.user_id
                    }
                    
                    is_valid, error_msg = self.risk_manager.validate_trade(trade_data)
                    
                    if not is_valid:
                        logger.warning(f"   ❌ Trade rejeitado pelo RiskManager: {error_msg}")
                        continue
                    
                    # 6. Criar ordem
                    logger.info(f"   ✅ Trade aprovado! Criando ordem para {symbol}")
                    
                    order_data = {
                        'symbol': symbol,
                        'side': 'buy' if signal.get('action') == 'BUY' else 'sell',
                        'type': 'market',  # Por enquanto, sempre market
                        'quantity': signal.get('quantity'),
                        'price': signal.get('entry_price'),  # Preço de referência
                        'stop_price': signal.get('stop_loss'),
                        'strategy_id': strategy.id,
                        'user_id': strategy.user_id,
                        'queue_priority': 'normal'
                    }
                    
                    order = self.order_manager.create_order(order_data)
                    logger.info(f"   ✅ Ordem criada: {order.client_order_id} para {symbol}")
                    
                    # 7. Enviar ordem para exchange (via Celery ou síncrono)
                    # Por enquanto, vamos deixar para o OrderManager processar
                    # Em produção, isso seria feito via fila (Celery)
                    
                except Exception as e:
                    logger.error(f"   ❌ Erro ao processar {symbol}: {str(e)}", exc_info=True)
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Erro ao executar estratégia {strategy.name}: {str(e)}", exc_info=True)
            raise
    
    def generate_signal(self, strategy: Strategy, symbol: str, timeframe: str) -> Optional[Dict]:
        """
        Gera sinal de trading baseado na estratégia usando motor_renan.py
        
        Args:
            strategy: Objeto Strategy
            symbol: Símbolo do par (ex: 'BTCUSDT')
            timeframe: Timeframe (ex: '1h', '4h')
        
        Returns:
            Dict: Sinal gerado com:
                - action: 'BUY', 'SELL', ou 'HOLD'
                - entry_price: Decimal
                - stop_loss: Decimal
                - take_profit: Decimal
                - quantity: Decimal
                - confluencia: float (0-100)
                - confidence: float (0-100)
            Ou None se houver erro
        """
        try:
            # 1. Importar motor_renan (com fallback se não disponível)
            try:
                from motor_renan import analise_completa
            except ImportError:
                logger.error("❌ motor_renan.py não encontrado. Instale as dependências.")
                return None
            
            # 2. Executar análise completa
            logger.debug(f"   🔬 Executando análise completa para {symbol}...")
            analise = analise_completa(symbol, timeframe)
            
            if not analise or 'erro' in analise:
                logger.warning(f"   ⚠️ Erro na análise: {analise.get('erro', 'Erro desconhecido')}")
                return None
            
            # 3. Extrair informações da análise
            sintese = analise.get('sintese', {})
            confluencia = analise.get('confluencia', {})
            niveis = analise.get('niveis_operacionais', {})
            indicadores = analise.get('indicadores', {})
            
            # 4. Extrair recomendação e bias
            recomendacao = sintese.get('recomendacao', 'HOLD').upper()
            bias = sintese.get('bias', 'NEUTRAL').upper()
            
            # 5. Calcular confluência score
            confluencia_score = 0.0
            if isinstance(confluencia, dict):
                confluencia_score = float(confluencia.get('score', 0))
            elif isinstance(confluencia, (int, float)):
                confluencia_score = float(confluencia)
            
            # 6. Determinar ação baseado na recomendação e confluência
            action = 'HOLD'
            if recomendacao in ['BUY', 'COMPRA', 'LONG']:
                action = 'BUY'
            elif recomendacao in ['SELL', 'VENDA', 'SHORT']:
                action = 'SELL'
            
            # 7. Filtrar por confluência mínima (configurável)
            min_confluencia = strategy.config.get('min_confluencia', 70) if strategy.config else 70
            if confluencia_score < min_confluencia:
                logger.debug(f"   ⏸️ Confluência {confluencia_score:.1f}% abaixo do mínimo {min_confluencia}%")
                return {
                    'action': 'HOLD',
                    'confluencia': confluencia_score,
                    'reason': f'Confluência insuficiente ({confluencia_score:.1f}% < {min_confluencia}%)'
                }
            
            # 8. Extrair níveis operacionais
            entry_price = Decimal(str(niveis.get('entry_price', 0)))
            stop_loss = Decimal(str(niveis.get('stop_loss', 0)))
            take_profit = Decimal(str(niveis.get('tp1', 0)))
            
            if entry_price == 0 or stop_loss == 0:
                logger.warning(f"   ⚠️ Níveis operacionais inválidos para {symbol}")
                return None
            
            # 9. Calcular quantidade baseado no risco por trade
            # Buscar portfolio do usuário (criar se não existir)
            portfolio = self.portfolio_manager.get_portfolio(strategy.user_id)
            if not portfolio:
                # Criar portfolio inicial se não existir
                from app.services.executors.exchange_adapter import get_exchange_adapter
                try:
                    adapter = get_exchange_adapter()
                    balance = Decimal(str(adapter.get_balance("USDT")))
                    portfolio = self.portfolio_manager.update_portfolio(
                        strategy.user_id,
                        balance,
                        balance
                    )
                    logger.info(f"   ✅ Portfolio criado para usuário {strategy.user_id}: ${balance}")
                except Exception as e:
                    logger.error(f"   ❌ Erro ao criar portfolio: {str(e)}")
                    return None
            
            # Calcular quantidade baseado no risco
            risk_per_trade_pct = strategy.risk_per_trade
            capital_risk = (portfolio.equity * risk_per_trade_pct) / Decimal('100.00')
            
            # Calcular risco por unidade (entry - stop_loss)
            risk_per_unit = abs(entry_price - stop_loss)
            if risk_per_unit == 0:
                logger.warning(f"   ⚠️ Risk per unit é zero para {symbol}")
                return None
            
            # Quantidade = Capital de risco / Risco por unidade
            quantity = capital_risk / risk_per_unit
            
            # 10. Aplicar limites de quantidade (se configurado)
            max_quantity = strategy.config.get('max_quantity') if strategy.config else None
            if max_quantity:
                quantity = min(quantity, Decimal(str(max_quantity)))
            
            # 11. Calcular confiança (baseado em confluência e outros fatores)
            confidence = confluencia_score  # Por enquanto, usar confluência como confiança
            
            # 12. Retornar sinal
            signal = {
                'action': action,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'quantity': quantity,
                'confluencia': confluencia_score,
                'confidence': confidence,
                'bias': bias,
                'recomendacao': recomendacao,
                'symbol': symbol,
                'timeframe': timeframe
            }
            
            logger.info(f"   ✅ Sinal gerado: {action} {symbol} @ {entry_price} (Confluência: {confluencia_score:.1f}%)")
            
            return signal
            
        except Exception as e:
            logger.error(f"   ❌ Erro ao gerar sinal para {symbol}: {str(e)}", exc_info=True)
            return None

