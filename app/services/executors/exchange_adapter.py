#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exchange Adapter - Padrão Adapter para múltiplas exchanges
"""
import os
import logging
from typing import Optional

from app.services.executors import ExchangeExecutor
from app.services.executors.bybit_executor import BybitExecutor

logger = logging.getLogger(__name__)


class ExchangeAdapter:
    """
    Adapter para escolher e usar o executor correto baseado na configuração
    """
    
    def __init__(self, exchange_name: Optional[str] = None):
        """
        Inicializa adapter com executor da exchange especificada
        
        Args:
            exchange_name: Nome da exchange ('bybit', 'binance', etc.)
                          Se None, usa variável de ambiente EXCHANGE_NAME ou 'bybit' como padrão
        """
        self.exchange_name = exchange_name or os.environ.get('EXCHANGE_NAME', 'bybit').lower()
        self.executor: Optional[ExchangeExecutor] = None
        
        self._initialize_executor()
    
    def _initialize_executor(self):
        """Inicializa o executor baseado na exchange configurada"""
        try:
            if self.exchange_name == 'bybit':
                self.executor = BybitExecutor(
                    testnet=os.environ.get('BYBIT_TESTNET', 'false').lower() == 'true'
                )
                logger.info("✅ ExchangeAdapter: BybitExecutor inicializado")
                
            elif self.exchange_name == 'binance':
                # TODO: Atualizar BinanceExecutor para seguir interface ExchangeExecutor
                from app.services.binance_executor import BinanceExecutor
                self.executor = BinanceExecutor(
                    testnet=os.environ.get('BINANCE_TESTNET', 'false').lower() == 'true'
                )
                logger.info("✅ ExchangeAdapter: BinanceExecutor inicializado")
                
            else:
                raise ValueError(f"Exchange não suportada: {self.exchange_name}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar executor {self.exchange_name}: {e}")
            raise
    
    def get_balance(self, coin: str = "USDT") -> float:
        """Retorna saldo disponível"""
        return self.executor.get_balance(coin)
    
    def place_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        order_type: str = "Market",
        price: Optional[float] = None,
        client_order_id: Optional[str] = None
    ) -> dict:
        """Envia ordem para exchange"""
        return self.executor.place_order(
            symbol=symbol,
            side=side,
            qty=qty,
            order_type=order_type,
            price=price,
            client_order_id=client_order_id
        )
    
    def get_positions(self) -> list:
        """Retorna posições abertas"""
        return self.executor.get_positions()
    
    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> dict:
        """Cancela ordem"""
        return self.executor.cancel_order(
            symbol=symbol,
            order_id=order_id,
            client_order_id=client_order_id
        )
    
    def get_order_status(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> dict:
        """Obtém status da ordem"""
        return self.executor.get_order_status(
            symbol=symbol,
            order_id=order_id,
            client_order_id=client_order_id
        )


# Instância global (singleton)
_adapter_instance: Optional[ExchangeAdapter] = None


def get_exchange_adapter() -> ExchangeAdapter:
    """
    Retorna instância singleton do ExchangeAdapter
    
    Returns:
        ExchangeAdapter: Instância do adapter
    """
    global _adapter_instance
    
    if _adapter_instance is None:
        _adapter_instance = ExchangeAdapter()
    
    return _adapter_instance


