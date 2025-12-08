"""
Executors para diferentes exchanges
Padrão Adapter para suportar múltiplas corretoras
"""
from abc import ABC, abstractmethod

class ExchangeExecutor(ABC):
    """Interface base para executors de exchange"""
    
    @abstractmethod
    def get_balance(self, coin="USDT"):
        """Retorna saldo disponível"""
        pass
    
    @abstractmethod
    def place_order(self, symbol, side, qty, order_type="Market", price=None, client_order_id=None):
        """Envia ordem para exchange"""
        pass
    
    @abstractmethod
    def get_positions(self):
        """Retorna posições abertas"""
        pass
    
    @abstractmethod
    def cancel_order(self, symbol, order_id=None, client_order_id=None):
        """Cancela ordem"""
        pass
    
    @abstractmethod
    def get_order_status(self, symbol, order_id=None, client_order_id=None):
        """Obtém status da ordem"""
        pass


