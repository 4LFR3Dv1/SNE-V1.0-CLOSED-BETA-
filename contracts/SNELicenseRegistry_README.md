# 📜 SNELicenseRegistry - Smart Contract Documentation

## 📋 Visão Geral

O **SNELicenseRegistry** é um Smart Contract desenvolvido em Solidity (^0.8.20) que implementa um sistema de DRM (Digital Rights Management) descentralizado para controle de acesso do **SNE Radar**.

## 🏗️ Arquitetura Híbrida

Este contrato funciona como a camada **"Verdade On-Chain"** na arquitetura híbrida do SNE Radar:

```
┌─────────────────────────────────────────────────────────┐
│              SNE RADAR - Arquitetura Híbrida            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CÉREBRO OFF-CHAIN (Python)                             │
│  • Análise Técnica (20+ Indicadores)                    │
│  • Machine Learning                                     │
│  • Processamento em Tempo Real                         │
│         │                                                │
│         │ Validação & Controle                          │
│         ▼                                                │
│  VERDADE ON-CHAIN (Scroll L2)                           │
│  • SNELicenseRegistry (Este Contrato)                   │
│  • Validação de Licenças                                │
│  • Auditoria e Compliance                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Funcionalidades Principais

### 1. **Controle de Acesso Descentralizado**
- Verificação on-chain de licenças antes de iniciar o sistema
- Impossível falsificar sem acesso à blockchain
- Histórico imutável de todas as concessões/revogações

### 2. **Licenças Vitalícias**
- Modelo de licença permanente (não expira)
- Pode ser revogada apenas pelo Owner
- Preparado para distribuição inicial de 100 licenças

### 3. **Auditoria On-Chain**
- Eventos `LicenseGranted` e `LicenseRevoked` registrados permanentemente
- Qualquer um pode verificar histórico de licenças
- Compliance e transparência total

## 📝 Estrutura do Contrato

### State Variables

```solidity
mapping(address => bool) public authorizedUsers;      // Lista de usuários autorizados
mapping(address => uint256) public licenseExpiry;     // Timestamp de expiração
uint256 public totalLicensesGranted;                   // Total histórico
uint256 public activeLicensesCount;                   // Licenças ativas
```

### Events

```solidity
event LicenseGranted(address indexed user, address indexed grantedBy, uint256 expiryTimestamp, uint256 timestamp);
event LicenseRevoked(address indexed user, address indexed revokedBy, uint256 timestamp);
```

### Funções Principais

#### Owner Functions

- `grantLifetimeLicense(address user)` - Concede licença vitalícia
- `grantLicense(address user, uint256 expiryTimestamp)` - Concede licença com expiração
- `revokeLicense(address user)` - Revoga licença
- `grantLifetimeLicensesBatch(address[] users)` - Concede múltiplas licenças (até 100)

#### Public View Functions

- `checkAccess(address user) returns (bool)` - Verifica se endereço tem acesso
- `getLicenseInfo(address user)` - Retorna informações detalhadas da licença
- `getStats()` - Retorna estatísticas do contrato

## 🚀 Deploy e Configuração

### Pré-requisitos

1. **Node.js** e **npm** instalados
2. **Hardhat** ou **Foundry** para desenvolvimento
3. **OpenZeppelin Contracts** (via npm)

### Instalação

```bash
# Instalar dependências
npm install @openzeppelin/contracts

# Ou com yarn
yarn add @openzeppelin/contracts
```

### Deploy na Scroll Sepolia (Testnet)

```javascript
// hardhat.config.js
module.exports = {
  networks: {
    scrollSepolia: {
      url: "https://sepolia-rpc.scroll.io",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 534351
    }
  }
};

// deploy.js
const hre = require("hardhat");

async function main() {
  const SNELicenseRegistry = await hre.ethers.getContractFactory("SNELicenseRegistry");
  const registry = await SNELicenseRegistry.deploy();
  
  await registry.waitForDeployment();
  
  console.log("SNELicenseRegistry deployed to:", await registry.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

### Deploy na Scroll Mainnet

```javascript
// Similar ao acima, mas com:
url: "https://rpc.scroll.io",
chainId: 534352
```

## 💻 Integração com Python (SNE Radar)

### Exemplo de Uso

```python
from web3 import Web3
import json

# Conecta à Scroll L2
w3 = Web3(Web3.HTTPProvider("https://sepolia-rpc.scroll.io"))

# Carrega ABI do contrato
with open("SNELicenseRegistry.abi.json") as f:
    abi = json.load(f)

# Endereço do contrato deployado
contract_address = "0x..."  # Substituir pelo endereço real

# Instancia o contrato
contract = w3.eth.contract(address=contract_address, abi=abi)

def check_license(wallet_address):
    """Verifica se a carteira possui licença válida"""
    try:
        is_valid = contract.functions.checkAccess(wallet_address).call()
        return is_valid
    except Exception as e:
        print(f"Erro ao verificar licença: {e}")
        return False

def get_license_info(wallet_address):
    """Retorna informações detalhadas da licença"""
    try:
        info = contract.functions.getLicenseInfo(wallet_address).call()
        return {
            'has_access': info[0],
            'is_lifetime': info[1],
            'expiry_timestamp': info[2]
        }
    except Exception as e:
        print(f"Erro ao obter informações: {e}")
        return None

# Uso no sistema
wallet_address = "0x..."  # Endereço do usuário

if check_license(wallet_address):
    print("✅ Licença válida. Iniciando SNE Radar...")
    # Inicia o sistema normalmente
else:
    print("❌ Licença inválida ou expirada. Acesso negado.")
    # Bloqueia acesso ao sistema
```

## 🔐 Segurança

### Medidas Implementadas

1. **Ownable do OpenZeppelin**: Apenas Owner pode conceder/revogar licenças
2. **Validações**: Verifica endereços zero e duplicatas
3. **Events**: Histórico completo de ações para auditoria
4. **View Functions**: Funções de leitura não modificam estado

### Boas Práticas

- ✅ Use multisig para Owner em produção
- ✅ Implemente upgradeability se necessário (UUPS Proxy)
- ✅ Monitore eventos para compliance
- ✅ Faça auditoria do código antes do deploy

## 📊 Estatísticas e Monitoramento

### Consultar Estatísticas

```python
stats = contract.functions.getStats().call()
print(f"Total de licenças concedidas: {stats[0]}")
print(f"Licenças ativas: {stats[1]}")
```

### Monitorar Eventos

```python
# Filtrar eventos LicenseGranted
from web3.middleware import geth_poa_middleware

w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Obter eventos
event_filter = contract.events.LicenseGranted.create_filter(
    fromBlock=0,
    argument_filters={'user': wallet_address}
)

events = event_filter.get_all_entries()
for event in events:
    print(f"Licença concedida em: {event.args.timestamp}")
```

## 🗺️ Roadmap Futuro

### Fase 1: MVP (Atual)
- ✅ Controle básico de acesso
- ✅ Licenças vitalícias
- ✅ Auditoria on-chain

### Fase 2: Melhorias
- ⏳ Integração com NFT License (ERC-721)
- ⏳ Sistema de staking (ERC-20)
- ⏳ Healthcheck on-chain (Proof of Uptime)

### Fase 3: DePIN
- ⏳ Rede descentralizada de nós
- ⏳ Governança descentralizada
- ⏳ Mineração de tokens

## 📚 Referências

- **OpenZeppelin Contracts**: https://docs.openzeppelin.com/contracts
- **Scroll Documentation**: https://docs.scroll.io
- **Solidity Documentation**: https://docs.soliditylang.org
- **Web3.py**: https://web3py.readthedocs.io

## 📄 Licença

Este contrato é parte do sistema SNE Radar e está sujeito aos termos de licenciamento do projeto.

---

**Versão**: 1.0  
**Última Atualização**: 2025-01-15  
**Rede**: Scroll L2 (Sepolia Testnet / Mainnet)

