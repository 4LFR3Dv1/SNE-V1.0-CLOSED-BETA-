#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executor Binance
Integração direta com Binance API para execução de ordens
"""

import os
from decimal import Decimal
from typing import Dict, Optional, List
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
from app.models.trading_models import Order


class BinanceExecutor:
    """
    Executor de ordens na Binance
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = False):
        """
        Inicializa cliente Binance
        
        Args:
            api_key: API Key da Binance (ou usa env var)
            api_secret: API Secret da Binance (ou usa env var)
            testnet: Se True, usa Binance Testnet
        """
        self.api_key = api_key or os.environ.get('BINANCE_API_KEY')
        self.api_secret = api_secret or os.environ.get('BINANCE_SECRET_KEY')
        self.testnet = testnet
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Binance API credentials não configuradas")
        
        # Criar cliente Binance
        if testnet:
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=True
            )
        else:
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.api_secret
            )
    
    def place_order(self, order: Order) -> Dict:
        """
        Envia ordem para Binance usando client_order_id
        
        Args:
            order: Objeto Order do banco de dados
        
        Returns:
            Dict: Resposta da Binance
        """
        try:
            # Preparar parâmetros
            params = {
                'symbol': order.symbol,
                'side': order.side.upper(),
                'type': order.type.upper(),
                'quantity': float(order.quantity),
                'newClientOrderId': order.client_order_id,  # ← ID do SNE
            }
            
            # Adicionar preço se for ordem limit
            if order.type.upper() in ['LIMIT', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT']:
                if not order.price:
                    raise ValueError(f"Preço necessário para ordem {order.type}")
                params['price'] = float(order.price)
                params['timeInForce'] = 'GTC'  # Good Till Cancel
            
            # Adicionar stop price se necessário
            if order.type.upper() in ['STOP_LOSS', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT', 'TAKE_PROFIT_LIMIT']:
                if not order.stop_price:
                    raise ValueError(f"Stop price necessário para ordem {order.type}")
                params['stopPrice'] = float(order.stop_price)
            
            # Enviar ordem para Binance
            response = self.client.create_order(**params)
            
            return response
            
        except BinanceAPIException as e:
            raise Exception(f"Erro Binance API: {e.message} (code: {e.code})")
        except Exception as e:
            raise Exception(f"Erro ao enviar ordem: {str(e)}")
    
    def get_order_by_client_id(self, symbol: str, client_order_id: str) -> Optional[Dict]:
        """
        Busca ordem na Binance usando client_order_id
        
        Args:
            symbol: Símbolo (ex: 'BTCUSDT')
            client_order_id: Client Order ID gerado pelo SNE
        
        Returns:
            Dict: Dados da ordem ou None se não encontrada
        """
        try:
            order = self.client.get_order(
                symbol=symbol,
                origClientOrderId=client_order_id  # ← Usar client_order_id
            )
            return order
        except BinanceAPIException as e:
            if e.code == -2013:  # Order does not exist
                return None
            raise Exception(f"Erro ao buscar ordem: {e.message}")
        except Exception as e:
            raise Exception(f"Erro ao buscar ordem: {str(e)}")
    
    def get_order_status(self, symbol: str, order_id: str) -> Optional[Dict]:
        """
        Busca status da ordem usando orderId da Binance
        
        Args:
            symbol: Símbolo
            order_id: Order ID da Binance
        
        Returns:
            Dict: Status da ordem
        """
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return order
        except BinanceAPIException as e:
            if e.code == -2013:
                return None
            raise
        except Exception as e:
            raise Exception(f"Erro ao buscar status: {str(e)}")
    
    def cancel_order(self, symbol: str, order_id: Optional[str] = None, client_order_id: Optional[str] = None) -> Dict:
        """
        Cancela ordem na Binance
        
        Args:
            symbol: Símbolo
            order_id: Order ID da Binance (prioridade)
            client_order_id: Client Order ID (alternativa)
        
        Returns:
            Dict: Resposta da Binance
        """
        try:
            if order_id:
                result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            elif client_order_id:
                result = self.client.cancel_order(symbol=symbol, origClientOrderId=client_order_id)
            else:
                raise ValueError("order_id ou client_order_id deve ser fornecido")
            
            return result
        except BinanceAPIException as e:
            raise Exception(f"Erro ao cancelar ordem: {e.message}")
        except Exception as e:
            raise Exception(f"Erro ao cancelar ordem: {str(e)}")
    
    def get_account_balance(self) -> Dict:
        """Obtém saldo da conta"""
        try:
            account = self.client.get_account()
            return account
        except Exception as e:
            raise Exception(f"Erro ao obter saldo: {str(e)}")
    
    def get_all_positions(self) -> List[Dict]:
        """
        Obtém todas as posições abertas
        
        Returns:
            List[Dict]: Lista de posições
        """
        try:
            # Para futures/perpetual
            positions = self.client.futures_position_information()
            # Filtrar apenas posições com quantidade > 0
            open_positions = [p for p in positions if float(p.get('positionAmt', 0)) != 0]
            return open_positions
        except Exception as e:
            # Se não for futures, retornar lista vazia
            # TODO: Implementar para spot se necessário
            return []


