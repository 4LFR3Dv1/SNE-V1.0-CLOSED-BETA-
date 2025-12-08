#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bybit Executor - Implementação para Bybit usando pybit SDK
"""
import os
import logging
from typing import Optional, Dict, List
from decimal import Decimal

try:
    from pybit.unified_trading import HTTP
    PYBIT_AVAILABLE = True
except ImportError:
    PYBIT_AVAILABLE = False
    logging.warning("pybit não instalado. Instale com: pip install pybit")

from app.services.executors import ExchangeExecutor

logger = logging.getLogger(__name__)


class BybitExecutor(ExchangeExecutor):
    """
    Executor para Bybit usando Unified Trading Account (UTA)
    """
    
    def __init__(self, testnet: bool = False):
        """
        Inicializa executor Bybit
        
        Args:
            testnet: Se True, usa testnet da Bybit
        """
        if not PYBIT_AVAILABLE:
            raise ImportError("pybit não está instalado. Instale com: pip install pybit")
        
        self.testnet = testnet
        self.api_key = os.environ.get('BYBIT_API_KEY')
        self.api_secret = os.environ.get('BYBIT_SECRET_KEY')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("BYBIT_API_KEY e BYBIT_SECRET_KEY devem estar configuradas nas variáveis de ambiente")
        
        # Criar sessão HTTP
        self.session = HTTP(
            testnet=testnet,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        
        logger.info(f"✅ BybitExecutor inicializado (testnet={testnet})")
        
        # Configurar modo One-Way (importante para evitar posições duplicadas)
        self._configure_position_mode()
    
    def _configure_position_mode(self):
        """
        Configura modo One-Way para evitar posições Long e Short simultâneas
        """
        try:
            # Tentar configurar modo global (se suportado)
            # Por símbolo, será feito quando necessário
            logger.info("Configurando modo One-Way na Bybit")
        except Exception as e:
            logger.warning(f"Não foi possível configurar modo One-Way: {e}")
    
    def _set_one_way_mode(self, symbol: str):
        """
        Configura modo One-Way para um símbolo específico
        
        Args:
            symbol: Símbolo do par (ex: BTCUSDT)
        """
        try:
            self.session.switch_position_mode(
                category="linear",
                symbol=symbol,
                mode=0  # 0 = One-Way Mode, 3 = Hedge Mode
            )
            logger.info(f"Modo One-Way configurado para {symbol}")
        except Exception as e:
            # Pode falhar se já estiver configurado ou se não tiver permissão
            logger.debug(f"Modo One-Way para {symbol}: {e}")
    
    def get_balance(self, coin: str = "USDT") -> float:
        """
        Retorna saldo disponível
        
        Args:
            coin: Moeda (padrão: USDT)
            
        Returns:
            Saldo disponível em float
        """
        try:
            response = self.session.get_wallet_balance(
                accountType="UNIFIED",
                coin=coin
            )
            
            # Estrutura da resposta Bybit
            if response.get('retCode') == 0:
                result = response.get('result', {})
                coin_list = result.get('list', [{}])[0].get('coin', [])
                
                for coin_data in coin_list:
                    if coin_data.get('coin') == coin:
                        balance = float(coin_data.get('walletBalance', 0))
                        logger.debug(f"Saldo {coin}: {balance}")
                        return balance
                
                logger.warning(f"Moeda {coin} não encontrada no wallet")
                return 0.0
            else:
                error_msg = response.get('retMsg', 'Unknown error')
                logger.error(f"Erro ao buscar saldo Bybit: {error_msg}")
                raise Exception(f"Bybit API Error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Erro ao buscar saldo Bybit: {e}")
            raise
    
    def place_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        order_type: str = "Market",
        price: Optional[float] = None,
        client_order_id: Optional[str] = None
    ) -> Dict:
        """
        Envia ordem para Bybit
        
        Args:
            symbol: Símbolo do par (ex: BTCUSDT)
            side: 'Buy' ou 'Sell' (Bybit usa capitalizado)
            qty: Quantidade
            order_type: Tipo de ordem (Market, Limit, etc.)
            price: Preço (obrigatório para Limit)
            client_order_id: ID único para idempotência (orderLinkId)
            
        Returns:
            Resposta da API com orderId
        """
        try:
            # Garantir modo One-Way
            self._set_one_way_mode(symbol)
            
            # Adaptar side (Bybit usa 'Buy'/'Sell' capitalizado)
            side_fmt = side.capitalize()
            
            # Preparar parâmetros
            params = {
                "category": "linear",  # Futuros Perpétuos
                "symbol": symbol,
                "side": side_fmt,
                "orderType": order_type,
                "qty": str(qty),
            }
            
            # Adicionar preço se for Limit
            if order_type == "Limit" and price:
                params["price"] = str(price)
            
            # Adicionar orderLinkId para idempotência
            if client_order_id:
                params["orderLinkId"] = client_order_id
            
            # Enviar ordem
            response = self.session.place_order(**params)
            
            if response.get('retCode') == 0:
                result = response.get('result', {})
                order_id = result.get('orderId')
                
                logger.info(f"✅ Ordem Bybit criada: {order_id} ({symbol} {side_fmt} {qty})")
                
                return {
                    'success': True,
                    'order_id': str(order_id),
                    'client_order_id': client_order_id,
                    'symbol': symbol,
                    'side': side_fmt,
                    'qty': qty,
                    'status': 'New'
                }
            else:
                error_msg = response.get('retMsg', 'Unknown error')
                logger.error(f"Erro ao criar ordem Bybit: {error_msg}")
                raise Exception(f"Bybit API Error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Erro ao criar ordem Bybit: {e}")
            raise
    
    def get_positions(self) -> List[Dict]:
        """
        Retorna posições abertas
        
        Returns:
            Lista de posições abertas
        """
        try:
            response = self.session.get_positions(
                category="linear",
                settleCoin="USDT"
            )
            
            positions = []
            
            if response.get('retCode') == 0:
                result = response.get('result', {})
                position_list = result.get('list', [])
                
                for p in position_list:
                    size = float(p.get('size', 0))
                    if size > 0:  # Apenas posições abertas
                        positions.append({
                            'symbol': p.get('symbol'),
                            'side': p.get('side'),  # 'Buy' ou 'Sell'
                            'size': size,
                            'entry_price': float(p.get('avgPrice', 0)),
                            'current_price': float(p.get('markPrice', 0)),
                            'pnl': float(p.get('unrealisedPnl', 0)),
                            'leverage': float(p.get('leverage', 1)),
                            'margin': float(p.get('positionIM', 0)),  # Initial Margin
                        })
                
                logger.debug(f"Posições Bybit encontradas: {len(positions)}")
                return positions
            else:
                error_msg = response.get('retMsg', 'Unknown error')
                logger.error(f"Erro ao buscar posições Bybit: {error_msg}")
                raise Exception(f"Bybit API Error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Erro ao buscar posições Bybit: {e}")
            raise
    
    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> Dict:
        """
        Cancela ordem
        
        Args:
            symbol: Símbolo do par
            order_id: ID da ordem na exchange
            client_order_id: ID do cliente (orderLinkId)
            
        Returns:
            Resultado do cancelamento
        """
        try:
            params = {
                "category": "linear",
                "symbol": symbol,
            }
            
            if client_order_id:
                params["orderLinkId"] = client_order_id
            elif order_id:
                params["orderId"] = order_id
            else:
                raise ValueError("order_id ou client_order_id deve ser fornecido")
            
            response = self.session.cancel_order(**params)
            
            if response.get('retCode') == 0:
                logger.info(f"✅ Ordem Bybit cancelada: {symbol}")
                return {'success': True}
            else:
                error_msg = response.get('retMsg', 'Unknown error')
                logger.error(f"Erro ao cancelar ordem Bybit: {error_msg}")
                raise Exception(f"Bybit API Error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Erro ao cancelar ordem Bybit: {e}")
            raise
    
    def get_order_status(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> Dict:
        """
        Obtém status da ordem
        
        Args:
            symbol: Símbolo do par
            order_id: ID da ordem na exchange
            client_order_id: ID do cliente (orderLinkId)
            
        Returns:
            Status da ordem
        """
        try:
            params = {
                "category": "linear",
                "symbol": symbol,
            }
            
            if client_order_id:
                params["orderLinkId"] = client_order_id
            elif order_id:
                params["orderId"] = order_id
            else:
                raise ValueError("order_id ou client_order_id deve ser fornecido")
            
            response = self.session.get_open_orders(**params)
            
            if response.get('retCode') == 0:
                result = response.get('result', {})
                orders = result.get('list', [])
                
                if orders:
                    order = orders[0]
                    return {
                        'order_id': order.get('orderId'),
                        'client_order_id': order.get('orderLinkId'),
                        'symbol': order.get('symbol'),
                        'side': order.get('side'),
                        'status': order.get('orderStatus'),
                        'qty': float(order.get('qty', 0)),
                        'filled_qty': float(order.get('cumExecQty', 0)),
                        'price': float(order.get('price', 0)) if order.get('price') else None,
                    }
                else:
                    # Ordem não encontrada (pode estar preenchida ou cancelada)
                    return {'status': 'NotFound'}
            else:
                error_msg = response.get('retMsg', 'Unknown error')
                logger.error(f"Erro ao buscar status da ordem Bybit: {error_msg}")
                raise Exception(f"Bybit API Error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Erro ao buscar status da ordem Bybit: {e}")
            raise


