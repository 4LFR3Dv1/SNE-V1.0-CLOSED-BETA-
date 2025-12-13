# 📜 SNELicenseRegistry - Informações de Deploy

## ✅ Status: DEPLOYADO E OPERACIONAL

O contrato **SNELicenseRegistry** foi deployado com sucesso na rede **Scroll Sepolia Testnet** e está pronto para uso no MVP do SNE Radar.

---

## 📍 Informações do Contrato

### Endereço do Contrato
```
0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7
```

### Rede
- **Network**: Scroll Sepolia Testnet
- **Chain ID**: 534351
- **RPC URL**: https://sepolia-rpc.scroll.io
- **Explorer**: https://sepolia-blockscout.scroll.io

### Informações de Deploy
- **Transaction Hash**: `9d3f023a84c498402eb8ccdf5926628c2d2f42de8734edf301f89ec681cab61d`
- **Block Number**: 15460541
- **Gas Used**: 672,612
- **Gas Price**: 0.02 Gwei
- **Custo Total**: ~0.000011 ETH

### Owner do Contrato
```
0x285df7643e6BD727527Fa3BA4Ff39dA729511bde
```

---

## 🔗 Links Úteis

- **Explorer (Contrato)**: https://sepolia-blockscout.scroll.io/address/0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7
- **Explorer (Transação)**: https://sepolia-blockscout.scroll.io/tx/9d3f023a84c498402eb8ccdf5926628c2d2f42de8734edf301f89ec681cab61d
- **Scroll Sepolia RPC**: https://sepolia-rpc.scroll.io
- **Scroll Documentation**: https://docs.scroll.io

---

## 📋 Funções Disponíveis

### Funções Públicas (View)

#### `checkAccess(address user) returns (bool)`
Verifica se um endereço possui licença válida.

**Uso no Python:**
```python
is_valid = contract.functions.checkAccess(wallet_address).call()
```

#### `getLicenseInfo(address user) returns (bool, bool, uint256)`
Retorna informações detalhadas da licença.

**Retorna:**
- `hasAccess`: Se possui acesso válido
- `isLifetime`: Se é licença vitalícia
- `expiryTimestamp`: Timestamp de expiração (ou `type(uint256).max` se vitalícia)

**Uso no Python:**
```python
info = contract.functions.getLicenseInfo(wallet_address).call()
has_access, is_lifetime, expiry = info
```

#### `getStats() returns (uint256, uint256)`
Retorna estatísticas do contrato.

**Retorna:**
- `totalGranted`: Total de licenças já concedidas (histórico)
- `activeCount`: Número de licenças ativas no momento

**Uso no Python:**
```python
stats = contract.functions.getStats().call()
total, active = stats
```

### Funções do Owner

#### `grantLifetimeLicense(address user)`
Concede licença vitalícia a um endereço.

**Requisitos:**
- Apenas Owner pode executar
- Endereço não pode ser zero
- Endereço não pode já ter licença ativa

**Uso no Python (requer chave privada do Owner):**
```python
from web3 import Web3

account = w3.eth.account.from_key(PRIVATE_KEY)
tx = contract.functions.grantLifetimeLicense(user_address).buildTransaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 200000,
    'gasPrice': w3.eth.gas_price
})
signed_tx = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
```

#### `grantLicense(address user, uint256 expiryTimestamp)`
Concede licença com expiração.

**Parâmetros:**
- `user`: Endereço que receberá a licença
- `expiryTimestamp`: Timestamp Unix de expiração (0 = vitalícia)

#### `revokeLicense(address user)`
Revoga licença de um endereço.

#### `grantLifetimeLicensesBatch(address[] users)`
Concede múltiplas licenças vitalícias em uma única transação (até 100 endereços).

---

## 📊 Estado Atual

### Estatísticas
- **Total de Licenças Concedidas**: 0 (inicial)
- **Licenças Ativas**: 0 (inicial)

### Próximos Passos

1. **Conceder Licença ao Owner** (se necessário):
   ```python
   # O Owner pode se auto-conceder uma licença
   contract.functions.grantLifetimeLicense(owner_address).transact(...)
   ```

2. **Distribuir Primeiras Licenças**:
   - Usar `grantLifetimeLicense()` para licenças individuais
   - Usar `grantLifetimeLicensesBatch()` para distribuição em massa

3. **Integrar no SNE Radar**:
   - Usar o endereço do contrato no código Python
   - Implementar verificação de licença no startup do sistema

---

## 🔐 Segurança

### Boas Práticas

1. **Owner Management**:
   - ⚠️ O Owner atual é uma carteira simples
   - 🔒 **Recomendado**: Transferir ownership para multisig em produção
   - 🔒 **Recomendado**: Usar hardware wallet para Owner

2. **Validação de Licenças**:
   - ✅ Sempre verificar `checkAccess()` antes de permitir acesso
   - ✅ Implementar cache local com expiração (ex: 5 minutos)
   - ✅ Re-validar periodicamente durante operação

3. **Monitoramento**:
   - 📊 Monitorar eventos `LicenseGranted` e `LicenseRevoked`
   - 📊 Acompanhar estatísticas via `getStats()`
   - 📊 Verificar logs no Explorer

---

## 📝 ABI do Contrato

O ABI completo está disponível em `deploy_info.json` após o deploy.

Para usar no código Python:

```python
import json

with open('deploy_info.json', 'r') as f:
    deploy_info = json.load(f)
    abi = deploy_info['abi']
    contract_address = deploy_info['contract_address']
```

---

## 🚀 Integração com SNE Radar

### Exemplo Completo

```python
from web3 import Web3
import json

# Configuração
SCROLL_RPC = "https://sepolia-rpc.scroll.io"
CONTRACT_ADDRESS = "0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7"

# Carregar ABI
with open('deploy_info.json', 'r') as f:
    abi = json.load(f)['abi']

# Conectar
w3 = Web3(Web3.HTTPProvider(SCROLL_RPC))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Verificar licença
wallet = "0x285df7643e6BD727527Fa3BA4Ff39dA729511bde"
is_valid = contract.functions.checkAccess(wallet).call()

if is_valid:
    print("✅ Acesso autorizado - Iniciando SNE Radar...")
    # Iniciar sistema
else:
    print("❌ Acesso negado - Licença inválida")
    # Bloquear acesso
```

---

## 📅 Histórico

- **2025-01-15**: Deploy inicial na Scroll Sepolia
- **Status**: MVP operacional, pronto para testes

---

## 🔮 Próximas Versões

### V2 (Produção - Scroll Mainnet)
- Deploy na Scroll Mainnet
- Transferência de ownership para multisig
- Integração completa com Healthcheck On-Chain
- Sistema de Tokenized Access (NFT/Stake)

---

**Última Atualização**: 2025-01-15  
**Versão do Contrato**: 1.0 (MVP)  
**Status**: ✅ Operacional

