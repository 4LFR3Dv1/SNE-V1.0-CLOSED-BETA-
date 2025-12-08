#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoPilot Engine - Motor Autônomo
Analisa mercado e distribui trades para pools de alocação
"""

from typing import Dict, Optional, List
from datetime import datetime
import threading
import logging
import sys
import os
from decimal import Decimal
import time

# Adicionar diretório raiz ao path para importar motor_renan
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.trading_models import TradingGlobalConfig, CapitalPool, db
from app.services.order_manager import OrderManager
from app.services.risk_manager import RiskManager
from app.services.portfolio_manager import PortfolioManager

logger = logging.getLogger(__name__)


class AutoPilotEngine:
    """
    Motor Autônomo - Analisa mercado e distribui trades para pools
    """
    
    def __init__(self, db_session=None):
        self.db = db_session or db
        self.running = False
        self.thread = None
        self.stop_flag = threading.Event()
        self.order_manager = OrderManager(db_session=db_session)
        self.risk_manager = RiskManager(db_session=db_session)
        self.portfolio_manager = PortfolioManager(db_session=db_session)
        
        # Cache de análises (evitar analisar o mesmo par múltiplas vezes)
        self.analysis_cache = {}  # {symbol: {'analysis': ..., 'timestamp': ...}}
        self.cache_ttl = 60  # Cache válido por 60 segundos
    
    def start(self, user_id: int) -> bool:
        """
        Inicia o motor autônomo
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se iniciado com sucesso
        """
        if self.running:
            logger.warning("Motor já está rodando")
            return True
        
        # Verificar se há configuração global
        config = TradingGlobalConfig.query.filter_by(user_id=user_id).first()
        if not config:
            logger.error(f"Configuração global não encontrada para usuário {user_id}")
            return False
        
        if not config.monitored_symbols or len(config.monitored_symbols) == 0:
            logger.warning("Nenhum símbolo configurado para monitorar")
            return False
        
        # Atualizar status
        config.motor_enabled = True
        self.db.session.commit()
        
        # Iniciar thread
        self.stop_flag.clear()
        self.running = True
        
        self.thread = threading.Thread(
            target=self._main_loop,
            args=(user_id,),
            daemon=True
        )
        self.thread.start()
        
        logger.info(f"✅ Motor Autônomo iniciado para usuário {user_id}")
        return True
    
    def stop(self, user_id: int) -> bool:
        """
        Para o motor autônomo
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se parado com sucesso
        """
        if not self.running:
            return True
        
        # Parar thread
        self.stop_flag.set()
        self.running = False
        
        # Atualizar status
        config = TradingGlobalConfig.query.filter_by(user_id=user_id).first()
        if config:
            config.motor_enabled = False
            self.db.session.commit()
        
        logger.info(f"🛑 Motor Autônomo parado para usuário {user_id}")
        return True
    
    def _main_loop(self, user_id: int):
        """
        Loop principal - analisa mercado continuamente
        
        Args:
            user_id: ID do usuário
        """
        logger.info("🔄 Loop principal do Motor Autônomo iniciado")
        
        while not self.stop_flag.is_set() and self.running:
            try:
                # 1. Buscar configuração global
                config = TradingGlobalConfig.query.filter_by(user_id=user_id).first()
                if not config or not config.motor_enabled:
                    logger.info("Motor desabilitado, parando loop")
                    break
                
                # 2. Para cada par monitorado
                for symbol in config.monitored_symbols:
                    if self.stop_flag.is_set():
                        break
                    
                    try:
                        # 3. Analisar UMA VEZ com motor_renan (usar cache se disponível)
                        analysis = self._get_analysis(symbol, config.default_timeframe)
                        
                        if not analysis or 'erro' in analysis:
                            logger.warning(f"⚠️ Erro na análise de {symbol}")
                            continue
                        
                        # 4. Extrair sinal
                        signal = self._extract_signal(analysis, config)
                        
                        # 5. Se sinal válido, verificar pools interessados
                        if signal and signal.get('action') != 'HOLD':
                            pools = self._get_interested_pools(user_id, symbol)
                            
                            if not pools:
                                logger.debug(f"   ⏸️ Nenhum pool interessado em {symbol}")
                                continue
                            
                            # 6. Para cada pool, calcular alocação e executar
                            for pool in pools:
                                if self.stop_flag.is_set():
                                    break
                                
                                if self._validate_pool_trade(pool, signal, config):
                                    self._execute_pool_trade(pool, signal)
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao processar {symbol}: {str(e)}", exc_info=True)
                        continue
                
                # Aguardar antes da próxima análise
                self.stop_flag.wait(timeout=60)  # 1 minuto
                
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {str(e)}", exc_info=True)
                self.stop_flag.wait(timeout=300)  # 5 minutos em caso de erro
    
    def _get_analysis(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """
        Obtém análise do motor_renan (com cache)
        
        Args:
            symbol: Símbolo do par
            timeframe: Timeframe
            
        Returns:
            Dict: Análise completa ou None
        """
        # Verificar cache
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.analysis_cache:
            cached = self.analysis_cache[cache_key]
            age = (datetime.utcnow() - cached['timestamp']).total_seconds()
            if age < self.cache_ttl:
                logger.debug(f"   📦 Usando análise em cache para {symbol}")
                return cached['analysis']
        
        # Executar análise
        try:
            from motor_renan import analise_completa
            
            logger.debug(f"   🔬 Analisando {symbol} no timeframe {timeframe}...")
            analysis = analise_completa(symbol, timeframe)
            
            # Atualizar cache
            self.analysis_cache[cache_key] = {
                'analysis': analysis,
                'timestamp': datetime.utcnow()
            }
            
            return analysis
            
        except ImportError:
            logger.error("❌ motor_renan.py não encontrado")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao analisar {symbol}: {str(e)}")
            return None
    
    def _extract_signal(self, analysis: Dict, config: TradingGlobalConfig) -> Optional[Dict]:
        """
        Extrai sinal da análise
        
        Args:
            analysis: Análise completa do motor_renan
            config: Configuração global
            
        Returns:
            Dict: Sinal extraído ou None
        """
        try:
            sintese = analysis.get('sintese', {})
            confluencia = analysis.get('confluencia', {})
            niveis = analysis.get('niveis_operacionais', {})
            
            # Extrair recomendação
            recomendacao = sintese.get('recomendacao', 'HOLD').upper()
            
            # Calcular confluência score
            confluencia_score = 0.0
            if isinstance(confluencia, dict):
                confluencia_score = float(confluencia.get('score', 0))
            elif isinstance(confluencia, (int, float)):
                confluencia_score = float(confluencia)
            
            # Filtrar por confluência mínima global
            min_confluencia = float(config.min_confluencia_global)
            if confluencia_score < min_confluencia:
                logger.debug(f"   ⏸️ Confluência {confluencia_score:.1f}% abaixo do mínimo global {min_confluencia}%")
                return {
                    'action': 'HOLD',
                    'confluencia': confluencia_score,
                    'reason': f'Confluência insuficiente ({confluencia_score:.1f}% < {min_confluencia}%)'
                }
            
            # Determinar ação
            action = 'HOLD'
            if recomendacao in ['BUY', 'COMPRA', 'LONG']:
                action = 'BUY'
            elif recomendacao in ['SELL', 'VENDA', 'SHORT']:
                action = 'SELL'
            
            if action == 'HOLD':
                return {'action': 'HOLD'}
            
            # Extrair níveis operacionais
            entry_price = Decimal(str(niveis.get('entry_price', 0)))
            stop_loss = Decimal(str(niveis.get('stop_loss', 0)))
            take_profit = Decimal(str(niveis.get('tp1', 0)))
            
            if entry_price == 0 or stop_loss == 0:
                logger.warning(f"   ⚠️ Níveis operacionais inválidos")
                return None
            
            return {
                'action': action,
                'symbol': analysis.get('symbol'),
                'timeframe': analysis.get('timeframe'),
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confluencia': confluencia_score,
                'bias': sintese.get('bias', 'NEUTRAL'),
                'recomendacao': recomendacao
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair sinal: {str(e)}", exc_info=True)
            return None
    
    def _get_interested_pools(self, user_id: int, symbol: str) -> List[CapitalPool]:
        """
        Retorna pools que querem operar este símbolo
        
        Args:
            user_id: ID do usuário
            symbol: Símbolo do par
            
        Returns:
            List[CapitalPool]: Lista de pools interessados
        """
        pools = CapitalPool.query.filter(
            CapitalPool.user_id == user_id,
            CapitalPool.status == 'active'
        ).all()
        
        # Filtrar pools que têm este símbolo
        interested = []
        for pool in pools:
            if pool.symbols and symbol in pool.symbols:
                # Verificar se pool tem capital disponível
                if pool.capital_available > Decimal('0.00'):
                    interested.append(pool)
        
        return interested
    
    def _validate_pool_trade(self, pool: CapitalPool, signal: Dict, config: TradingGlobalConfig) -> bool:
        """
        Valida se pool pode executar este trade
        
        Args:
            pool: Pool de capital
            signal: Sinal gerado
            config: Configuração global
            
        Returns:
            bool: True se válido
        """
        try:
            # Verificar confluência mínima do pool (se configurado)
            if pool.min_confluencia:
                min_confluencia = float(pool.min_confluencia)
                if signal.get('confluencia', 0) < min_confluencia:
                    logger.debug(f"   ⏸️ Pool {pool.name}: Confluência insuficiente")
                    return False
            
            # Verificar se pool tem posições abertas demais
            from app.models.trading_models import Position
            open_positions = Position.query.filter_by(
                pool_id=pool.id,
                status='open'
            ).count()
            
            if open_positions >= pool.max_positions:
                logger.debug(f"   ⏸️ Pool {pool.name}: Máximo de posições atingido ({open_positions}/{pool.max_positions})")
                return False
            
            # Validar com RiskManager
            trade_data = {
                'entry': signal['entry_price'],
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'quantity': self._calculate_pool_quantity(pool, signal),  # Quantidade estimada
                'symbol': signal['symbol'],
                'user_id': pool.user_id
            }
            
            is_valid, error_msg = self.risk_manager.validate_trade(trade_data)
            if not is_valid:
                logger.debug(f"   ⏸️ Pool {pool.name}: Trade rejeitado pelo RiskManager: {error_msg}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao validar trade do pool {pool.name}: {str(e)}")
            return False
    
    def _calculate_pool_quantity(self, pool: CapitalPool, signal: Dict) -> Decimal:
        """
        Calcula quantidade baseado no capital do pool
        
        Args:
            pool: Pool de capital
            signal: Sinal gerado
            
        Returns:
            Decimal: Quantidade calculada
        """
        try:
            # Calcular risco por trade
            risk_per_trade_pct = pool.risk_per_trade_pct
            capital_risk = (pool.capital_available * risk_per_trade_pct) / Decimal('100.00')
            
            # Calcular risco por unidade
            risk_per_unit = abs(signal['entry_price'] - signal['stop_loss'])
            if risk_per_unit == 0:
                return Decimal('0.00')
            
            # Quantidade = Capital de risco / Risco por unidade
            quantity = capital_risk / risk_per_unit
            
            # Limitar pela disponibilidade do pool
            max_quantity_by_capital = pool.capital_available / signal['entry_price']
            quantity = min(quantity, max_quantity_by_capital)
            
            return quantity
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular quantidade: {str(e)}")
            return Decimal('0.00')
    
    def _execute_pool_trade(self, pool: CapitalPool, signal: Dict):
        """
        Executa trade para um pool específico
        
        Args:
            pool: Pool de capital
            signal: Sinal gerado
        """
        try:
            # Calcular quantidade
            quantity = self._calculate_pool_quantity(pool, signal)
            
            if quantity <= Decimal('0.00'):
                logger.warning(f"   ⚠️ Quantidade inválida para pool {pool.name}")
                return
            
            logger.info(f"   ✅ Executando trade para pool {pool.name}: {signal['action']} {signal['symbol']} @ {signal['entry_price']}")
            
            # Criar ordem
            order_data = {
                'symbol': signal['symbol'],
                'side': 'buy' if signal['action'] == 'BUY' else 'sell',
                'type': 'market',
                'quantity': quantity,
                'price': signal['entry_price'],
                'stop_price': signal['stop_loss'],
                'pool_id': pool.id,  # ← Novo campo
                'user_id': pool.user_id,
                'queue_priority': 'normal'
            }
            
            order = self.order_manager.create_order(order_data)
            logger.info(f"   ✅ Ordem criada: {order.client_order_id} para pool {pool.name}")
            
            # TODO: Enviar ordem para exchange (via Celery ou síncrono)
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar trade do pool {pool.name}: {str(e)}", exc_info=True)


