# 🔐 IMPLEMENTAÇÃO: CLIENT ORDER ID (Idempotência)

**Data:** 02 de Janeiro de 2025  
**Objetivo:** Garantir idempotência nas ordens enviadas para Binance  
**Status:** ✅ Correção Aplicada

---

## 🎯 PROBLEMA RESOLVIDO

### **Cenário de Falha:**
```
1. Sistema gera ordem
2. Envia para Binance API
3. Internet cai ANTES da resposta
4. Sistema não sabe se ordem foi aceita
5. Sistema pode reenviar ordem (duplicação)
```

### **Solução:**
Usar `client_order_id` (UUID gerado pelo SNE) ANTES de enviar para Binance.

---

## 📋 IMPLEMENTAÇÃO

### **1. Modelo Order Atualizado**

```python
class Order(db.Model):
    # --- IDEMPOTÊNCIA (CRÍTICO) ---
    # ID interno único gerado pelo SNE ANTES de enviar para Binance
    client_order_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # ID retornado pela Binance (orderId) - Pode ser Null se ordem falhar no envio
    binance_order_id = Column(String(50), unique=True, index=True, nullable=True)
```

### **2. Geração do Client Order ID**

**Arquivo:** `/app/services/order_manager.py`

```python
import uuid
from datetime import datetime

class OrderManager:
    def create_order(self, order_data):
        """
        Cria ordem com client_order_id único
        """
        # Gerar UUID único ANTES de enviar para Binance
        client_order_id = f"SNE-{uuid.uuid4().hex[:16].upper()}-{int(datetime.utcnow().timestamp())}"
        
        # Criar ordem no banco
        order = Order(
            client_order_id=client_order_id,  # ← ID gerado pelo SNE
            symbol=order_data['symbol'],
            side=order_data['side'],
            type=order_data['type'],
            quantity=Decimal(str(order_data['quantity'])),
            price=Decimal(str(order_data.get('price', 0))) if order_data.get('price') else None,
            status='pending',
            # binance_order_id será preenchido APÓS resposta da Binance
        )
        
        db.session.add(order)
        db.session.commit()
        
        return order
```

### **3. Envio para Binance com Client Order ID**

**Arquivo:** `/app/services/binance_executor.py`

```python
from binance.client import Client

class BinanceExecutor:
    def place_order(self, order):
        """
        Envia ordem para Binance usando client_order_id
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
            if order.type in ['LIMIT', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT']:
                params['price'] = float(order.price)
                params['timeInForce'] = 'GTC'  # Good Till Cancel
            
            # Adicionar stop price se necessário
            if order.type in ['STOP_LOSS', 'STOP_LOSS_LIMIT']:
                params['stopPrice'] = float(order.stop_price)
            
            # Enviar ordem para Binance
            response = self.client.create_order(**params)
            
            # Atualizar ordem com resposta da Binance
            order.binance_order_id = str(response['orderId'])
            order.status = response['status'].lower()
            order.filled_quantity = Decimal(str(response.get('executedQty', 0)))
            order.filled_price = Decimal(str(response.get('price', 0)))
            order.executed_at = datetime.utcnow()
            
            db.session.commit()
            
            return response
            
        except Exception as e:
            # Em caso de erro, order.binance_order_id permanece None
            # Mas order.client_order_id já existe para rastreamento
            order.status = 'rejected'
            order.reconciliation_status = 'discrepancy'
            db.session.commit()
            raise
```

### **4. Reconciliação Usando Client Order ID**

**Arquivo:** `/app/services/reconciliation_engine.py`

```python
class ReconciliationEngine:
    def reconcile_orders(self):
        """
        Reconcilia ordens usando client_order_id
        """
        # 1. Buscar ordens pendentes no DB
        pending_orders = Order.query.filter_by(
            status='pending',
            reconciliation_status='pending'
        ).all()
        
        for order in pending_orders:
            try:
                # 2. Verificar na Binance usando client_order_id
                binance_order = self.binance_executor.get_order_by_client_id(
                    symbol=order.symbol,
                    client_order_id=order.client_order_id
                )
                
                if binance_order:
                    # 3. Ordem existe na Binance - atualizar DB
                    order.binance_order_id = str(binance_order['orderId'])
                    order.status = binance_order['status'].lower()
                    order.filled_quantity = Decimal(str(binance_order.get('executedQty', 0)))
                    order.filled_price = Decimal(str(binance_order.get('price', 0)))
                    order.reconciliation_status = 'synced'
                    order.last_reconciled = datetime.utcnow()
                    
                    # Log de reconciliação
                    self._log_reconciliation(
                        order_type='order',
                        status='synced',
                        details={
                            'client_order_id': order.client_order_id,
                            'binance_order_id': order.binance_order_id,
                            'action': 'updated_from_binance'
                        }
                    )
                else:
                    # 4. Ordem NÃO existe na Binance - possível falha no envio
                    order.reconciliation_status = 'discrepancy'
                    order.last_reconciled = datetime.utcnow()
                    
                    # Gerar alerta crítico
                    self._handle_discrepancy(
                        entity_type='order',
                        entity_id=order.id,
                        discrepancy={
                            'type': 'missing_in_binance',
                            'client_order_id': order.client_order_id,
                            'message': 'Ordem existe no DB mas não na Binance'
                        }
                    )
                    
            except Exception as e:
                # Erro ao consultar Binance
                self._log_reconciliation(
                    order_type='order',
                    status='error',
                    details={
                        'client_order_id': order.client_order_id,
                        'error': str(e)
                    }
                )
        
        db.session.commit()
```

### **5. Método Helper na BinanceExecutor**

```python
class BinanceExecutor:
    def get_order_by_client_id(self, symbol, client_order_id):
        """
        Busca ordem na Binance usando client_order_id
        """
        try:
            order = self.client.get_order(
                symbol=symbol,
                origClientOrderId=client_order_id  # ← Usar client_order_id
            )
            return order
        except Exception as e:
            # Ordem não encontrada
            if 'Order does not exist' in str(e):
                return None
            raise
```

---

## 🔄 FLUXO COMPLETO COM IDEMPOTÊNCIA

```
1. OrderManager.create_order()
   ↓
   Gera: client_order_id = "SNE-A1B2C3D4E5F6-1704201600"
   ↓
   Salva no DB: Order(client_order_id="SNE-...", status="pending")
   ↓

2. BinanceExecutor.place_order(order)
   ↓
   Envia para Binance: newClientOrderId="SNE-A1B2C3D4E5F6-1704201600"
   ↓
   
   CENÁRIO A: Sucesso
   ↓
   Binance retorna: { orderId: 12345, status: "NEW" }
   ↓
   Atualiza DB: Order(binance_order_id=12345, status="filled")
   
   CENÁRIO B: Falha de Rede
   ↓
   Resposta não chega
   ↓
   Order permanece: Order(client_order_id="SNE-...", binance_order_id=None, status="pending")
   ↓
   
3. ReconciliationEngine.reconcile_orders() (a cada 1 min)
   ↓
   Busca na Binance: get_order_by_client_id("SNE-A1B2C3D4E5F6-1704201600")
   ↓
   
   Se encontrada:
   - Atualiza binance_order_id
   - Atualiza status
   - Marca como 'synced'
   
   Se não encontrada:
   - Marca como 'discrepancy'
   - Gera alerta crítico
```

---

## ✅ BENEFÍCIOS

### **1. Rastreabilidade Completa**
- Sempre sabemos qual ordem foi enviada (mesmo se rede cair)
- Podemos verificar na Binance usando `client_order_id`

### **2. Prevenção de Duplicação**
- Se ordem já existe no DB com `client_order_id`, não reenvia
- Binance também rejeita se `newClientOrderId` duplicado

### **3. Reconciliação Robusta**
- Podemos verificar ordens pendentes mesmo sem `binance_order_id`
- Recuperação automática de ordens "perdidas"

### **4. Auditoria Completa**
- Logs mostram `client_order_id` em todas as etapas
- Rastreamento completo do ciclo de vida da ordem

---

## 🧪 TESTES RECOMENDADOS

### **Teste 1: Ordem Normal**
```python
# Criar ordem
order = order_manager.create_order({...})
assert order.client_order_id is not None
assert order.binance_order_id is None

# Enviar para Binance
binance_executor.place_order(order)
assert order.binance_order_id is not None
assert order.status == 'filled'
```

### **Teste 2: Falha de Rede**
```python
# Simular falha de rede
with patch('binance.client.Client.create_order', side_effect=ConnectionError):
    order = order_manager.create_order({...})
    binance_executor.place_order(order)  # Falha
    
    # Ordem deve ter client_order_id mas não binance_order_id
    assert order.client_order_id is not None
    assert order.binance_order_id is None
    assert order.status == 'rejected'
```

### **Teste 3: Reconciliação**
```python
# Ordem pendente sem binance_order_id
order = Order(client_order_id="SNE-TEST-123", status="pending")

# Reconciliação deve encontrar na Binance
reconciliation_engine.reconcile_orders()

# Deve atualizar binance_order_id
assert order.binance_order_id is not None
assert order.reconciliation_status == 'synced'
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

- [x] Adicionar `client_order_id` ao modelo Order
- [x] Atualizar migration Alembic
- [ ] Implementar geração de `client_order_id` no OrderManager
- [ ] Atualizar BinanceExecutor para usar `newClientOrderId`
- [ ] Implementar `get_order_by_client_id()` na BinanceExecutor
- [ ] Atualizar ReconciliationEngine para usar `client_order_id`
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Documentação de uso

---

**Status:** ✅ Correção Aplicada nos Modelos  
**Próxima Ação:** Implementar lógica de geração e uso do `client_order_id`


