> **Note (EM PORTUGUES!!!):** Este documento descreve a arquitetura alvo para a Versão de Produção (V2). O MVP atual implementa a lógica central de Verificação de Licença na Scroll Sepolia.

> **Note:** This document outlines the target architecture for the Production Release (V2). The current MVP implements the core License Verification logic on Scroll Sepolia.

---

# 🔐 Arquitetura Técnica Alvo: Integração Web3 - Scroll L2 (V2)

## 📋 Visão Geral

O **SNE RADAR** implementa uma arquitetura híbrida inovadora que combina processamento off-chain (Python) com validação e controle on-chain (Scroll Layer 2). Esta integração Web3 fornece três componentes principais:

1. **Smart License Check** - DRM Descentralizado
2. **Healthcheck On-Chain** - Proof of Uptime
3. **Tokenized Access** - Licença como NFT/Token em Stake

---

## 🏗️ Arquitetura da Integração Web3

```
┌─────────────────────────────────────────────────────────────┐
│                    SNE RADAR SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         CÉREBRO OFF-CHAIN (Python)                 │    │
│  │  • Análise Técnica (20+ Indicadores)              │    │
│  │  • Machine Learning                                │    │
│  │  • Processamento em Tempo Real                     │    │
│  └──────────────────┬─────────────────────────────────┘    │
│                     │                                        │
│                     │ Validação & Controle                   │
│                     ▼                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │         VERDADE ON-CHAIN (Scroll L2)                │    │
│  │  • Smart License Check                             │    │
│  │  • Proof of Uptime                                 │    │
│  │  • Tokenized Access (NFT/Stake)                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ Smart License Check (DRM Descentralizado)

### 📌 Conceito

O **Smart License Check** é um sistema de gerenciamento de direitos digitais (DRM) descentralizado que utiliza contratos inteligentes na rede Scroll para verificar e validar licenças de uso do software.

### 🔧 Funcionamento Técnico

#### **Fluxo de Verificação de Licença:**

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   Cliente   │─────▶│  SNE Client  │─────▶│ Scroll L2    │
│  (Desktop/  │      │   (Python)   │      │  Smart       │
│    Web)     │      │              │      │  Contract    │
└─────────────┘      └──────────────┘      └──────────────┘
                            │                       │
                            │ 1. Verifica Wallet   │
                            │ 2. Consulta Contract │
                            │ 3. Valida Stake      │
                            │                       │
                            ▼                       ▼
                     ┌──────────────┐      ┌──────────────┐
                     │  License     │◀────│  Registry    │
                     │  Validated   │      │  Contract    │
                     └──────────────┘      └──────────────┘
```

#### **Componentes Principais:**

1. **Smart Contract (LicenseRegistry.sol)**
   - Armazena mapeamento de endereços → status de licença
   - Gerencia tokens/NFTs de licença
   - Valida stake de tokens
   - Registra histórico de verificações

2. **Cliente Python (web3_service.py)**
   - Conecta à rede Scroll via Web3.py
   - Interage com o contrato inteligente
   - Verifica status da licença antes de iniciar
   - Cache local para otimização

3. **Frontend (Vue.js)**
   - Integração com MetaMask/WalletConnect
   - Conexão de carteira
   - Exibição de status de licença
   - Solicitação de assinatura de transações

### 🔐 Características de Segurança

- **Verificação On-Chain**: Impossível falsificar sem acesso à blockchain
- **Imutabilidade**: Histórico de verificações registrado permanentemente
- **Descentralização**: Não depende de servidor centralizado
- **Transparência**: Código do contrato auditável publicamente

### 💻 Implementação (MVP - Atual)

```python
# Implementação atual do MVP - Scroll Sepolia
from web3 import Web3
import json

class LicenseChecker:
    def __init__(self, scroll_rpc_url=None, contract_address=None):
        # Configuração padrão para Scroll Sepolia (MVP)
        self.scroll_rpc_url = scroll_rpc_url or "https://sepolia-rpc.scroll.io"
        self.contract_address = contract_address or "0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7"
        
        # Conecta à Scroll Sepolia
        self.w3 = Web3(Web3.HTTPProvider(self.scroll_rpc_url))
        
        # Carrega ABI (pode ser carregado de arquivo ou hardcoded)
        # O ABI completo está disponível em deploy_info.json
        with open('deploy_info.json', 'r') as f:
            deploy_info = json.load(f)
            abi = deploy_info['abi']
        
        # Instancia o contrato
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=abi
        )
    
    def check_license(self, wallet_address):
        """Verifica se a carteira possui licença válida"""
        try:
            # Chama a função checkAccess do contrato
            is_valid = self.contract.functions.checkAccess(
                wallet_address
            ).call()
            
            # Obtém informações detalhadas
            license_info = self.contract.functions.getLicenseInfo(
                wallet_address
            ).call()
            
            return {
                'valid': is_valid,
                'has_access': license_info[0],
                'is_lifetime': license_info[1],
                'expiry_timestamp': license_info[2]
            }
        except Exception as e:
            print(f"Erro ao verificar licença: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_stats(self):
        """Retorna estatísticas do contrato"""
        try:
            stats = self.contract.functions.getStats().call()
            return {
                'total_granted': stats[0],
                'active_count': stats[1]
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return None

# Exemplo de uso
if __name__ == "__main__":
    checker = LicenseChecker()
    
    # Verificar licença de um endereço
    wallet = "0x285df7643e6BD727527Fa3BA4Ff39dA729511bde"  # Owner
    result = checker.check_license(wallet)
    
    if result['valid']:
        print("✅ Licença válida!")
        if result['is_lifetime']:
            print("   Tipo: Licença Vitalícia")
    else:
        print("❌ Licença inválida ou não encontrada")
    
    # Obter estatísticas
    stats = checker.get_stats()
    if stats:
        print(f"\n📊 Estatísticas:")
        print(f"   Total de licenças concedidas: {stats['total_granted']}")
        print(f"   Licenças ativas: {stats['active_count']}")
```

### 🔮 Implementação Futura (V2 - Produção)

```python
# Implementação futura com Healthcheck On-Chain
class LicenseCheckerV2(LicenseChecker):
    def register_healthcheck(self, wallet_address, node_id, timestamp):
        """Registra healthcheck on-chain (V2)"""
        # Gera hash do healthcheck
        healthcheck_hash = self._generate_hash(node_id, timestamp)
        
        # Registra na blockchain (função a ser implementada no contrato V2)
        tx_hash = self.contract.functions.recordHealthcheck(
            wallet_address,
            healthcheck_hash,
            timestamp
        ).transact({'from': wallet_address})
        
        return tx_hash
```

---

## 2️⃣ Healthcheck On-Chain (Proof of Uptime)

### 📌 Conceito

O **Healthcheck On-Chain** é um mecanismo de verificação de disponibilidade que registra periodicamente o status operacional do sistema diretamente na blockchain Scroll, criando um histórico auditável e imutável de uptime.

### 🔧 Funcionamento Técnico

#### **Fluxo de Healthcheck:**

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   SNE Node  │─────▶│  Healthcheck │─────▶│ Scroll L2    │
│  (Running)  │      │   Service    │      │  Registry    │
└─────────────┘      └──────────────┘      └──────────────┘
      │                      │                      │
      │ 1. Coleta Status     │ 2. Gera Hash        │ 3. Registra
      │ 2. Métricas          │ 3. Assina           │    On-Chain
      │ 3. Timestamp         │ 4. Envia            │
      │                      │                      │
      ▼                      ▼                      ▼
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  Metrics    │      │  Signed      │      │  Immutable   │
│  Collected  │      │  Hash        │      │  Record      │
└─────────────┘      └──────────────┘      └──────────────┘
```

#### **Dados Registrados:**

1. **Node ID**: Identificador único do nó
2. **Timestamp**: Momento do healthcheck
3. **Status Hash**: Hash dos componentes críticos
4. **Uptime**: Tempo de operação contínua
5. **Version**: Versão do software

#### **Frequência de Registro:**

- **Intervalo**: A cada inicialização + heartbeat periódico
- **Otimização**: Batch de múltiplos healthchecks em uma transação
- **Custo**: Minimizado através de Scroll L2 (baixas taxas)

### 📊 Benefícios

- **Auditabilidade**: Histórico completo e verificável
- **Transparência**: Qualquer um pode verificar uptime
- **Compliance**: Prova de operação contínua
- **DePIN Ready**: Preparado para rede descentralizada de nós

### 💻 Implementação Esperada

```python
# Exemplo de implementação

class OnChainHealthcheck:
    def __init__(self, license_checker, interval_minutes=60):
        self.license_checker = license_checker
        self.interval = interval_minutes * 60
        self.node_id = self._generate_node_id()
    
    def generate_healthcheck_data(self):
        """Gera dados do healthcheck"""
        return {
            'node_id': self.node_id,
            'timestamp': int(time.time()),
            'version': self._get_version(),
            'components': {
                'api': self._check_api(),
                'database': self._check_database(),
                'scanner': self._check_scanner(),
                'trading': self._check_trading()
            },
            'uptime': self._get_uptime()
        }
    
    def record_healthcheck(self, wallet_address):
        """Registra healthcheck na blockchain"""
        data = self.generate_healthcheck_data()
        hash_data = self._hash_healthcheck(data)
        
        # Registra via contrato inteligente
        tx_hash = self.license_checker.register_healthcheck(
            wallet_address,
            self.node_id,
            data['timestamp'],
            hash_data
        )
        
        return {
            'tx_hash': tx_hash,
            'data': data,
            'recorded_at': datetime.now()
        }
    
    def start_periodic_healthcheck(self, wallet_address):
        """Inicia healthcheck periódico"""
        while True:
            try:
                self.record_healthcheck(wallet_address)
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Healthcheck failed: {e}")
                time.sleep(60)  # Retry em 1 minuto
```

---

## 3️⃣ Tokenized Access (Licença como NFT/Token em Stake)

### 📌 Conceito

O **Tokenized Access** transforma a licença de uso do software em um ativo digital (NFT ou Token) que deve estar em stake (bloqueado) na carteira do usuário para permitir acesso ao sistema.

### 🔧 Funcionamento Técnico

#### **Modelo de Licenciamento:**

```
┌─────────────────────────────────────────────────────────┐
│              TOKENIZED ACCESS MODEL                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Opção 1: NFT License (ERC-721)                         │
│  ┌──────────────┐      ┌──────────────┐                │
│  │  License NFT │─────▶│  SNE Access  │                │
│  │  (ERC-721)   │      │  Granted     │                │
│  └──────────────┘      └──────────────┘                │
│                                                          │
│  Opção 2: Token Stake (ERC-20)                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │  SNE Token   │─────▶│  Staked       │                │
│  │  (ERC-20)    │      │  (Locked)     │                │
│  └──────────────┘      └──────────────┘                │
│                                                          │
│  Opção 3: Hybrid (NFT + Token Stake)                    │
│  ┌──────────────┐      ┌──────────────┐                │
│  │  License NFT │  +   │  Token Stake  │                │
│  │  (Required)  │      │  (Optional)   │                │
│  └──────────────┘      └──────────────┘                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### **Fluxo de Acesso:**

```
1. Usuário conecta carteira (MetaMask/WalletConnect)
   ↓
2. Sistema verifica posse de NFT ou tokens em stake
   ↓
3. Se válido: Sistema inicia normalmente
   ↓
4. Se inválido: Sistema bloqueia acesso
   ↓
5. Healthcheck periódico valida licença continuamente
```

### 🎫 Tipos de Licença

#### **1. NFT License (ERC-721)**
- **Vantagens**: 
  - Licença única e transferível
  - Pode ter metadados (tier, expiração, etc.)
  - Facilita revenda no mercado secundário
  
- **Implementação**:
  ```solidity
  contract SNELicenseNFT is ERC721 {
      mapping(address => bool) public activeLicenses;
      mapping(uint256 => LicenseData) public licenses;
      
      function hasActiveLicense(address user) public view returns (bool) {
          return activeLicenses[user];
      }
  }
  ```

#### **2. Token Stake (ERC-20)**
- **Vantagens**:
  - Modelo de staking tradicional
  - Permite diferentes tiers baseados em quantidade
  - Tokens podem gerar yield
  
- **Implementação**:
  ```solidity
  contract SNELicenseStake {
      IERC20 public sneToken;
      mapping(address => uint256) public stakes;
      uint256 public minimumStake;
      
      function stake(uint256 amount) external {
          require(amount >= minimumStake, "Insufficient stake");
          sneToken.transferFrom(msg.sender, address(this), amount);
          stakes[msg.sender] += amount;
      }
      
      function getStakeAmount(address user) public view returns (uint256) {
          return stakes[user];
      }
  }
  ```

#### **3. Hybrid Model**
- Combina NFT (requisito) + Token Stake (opcional para benefícios)
- NFT garante acesso básico
- Token stake desbloqueia features premium

### 💰 Modelo Econômico

#### **Distribuição de Licenças:**

- **Fase 1 (Atual)**: 100 Licenças Vitalícias (Stake)
- **Modelo**: Stake único, acesso permanente
- **Transferibilidade**: Licença pode ser transferida/revendida
- **Valor**: Definido pelo mercado (NFT) ou fixo (Stake)

#### **Benefícios do Stake:**

1. **Acesso Permanente**: Uma vez em stake, acesso vitalício
2. **Transferível**: Pode vender/transferir licença
3. **Auditável**: Histórico completo na blockchain
4. **Sem Renovação**: Não precisa renovar anualmente

### 💻 Implementação Esperada

```python
# Exemplo de implementação

class TokenizedAccess:
    def __init__(self, scroll_rpc_url, nft_contract, stake_contract):
        self.w3 = Web3(Web3.HTTPProvider(scroll_rpc_url))
        self.nft_contract = self.w3.eth.contract(
            address=nft_contract['address'],
            abi=nft_contract['abi']
        )
        self.stake_contract = self.w3.eth.contract(
            address=stake_contract['address'],
            abi=stake_contract['abi']
        )
    
    def check_access(self, wallet_address):
        """Verifica acesso via NFT ou Token Stake"""
        # Verifica NFT
        nft_balance = self.nft_contract.functions.balanceOf(
            wallet_address
        ).call()
        
        # Verifica Token Stake
        stake_amount = self.stake_contract.functions.getStakeAmount(
            wallet_address
        ).call()
        
        minimum_stake = self.stake_contract.functions.minimumStake().call()
        
        return {
            'has_nft': nft_balance > 0,
            'has_stake': stake_amount >= minimum_stake,
            'stake_amount': stake_amount,
            'access_granted': nft_balance > 0 or stake_amount >= minimum_stake
        }
    
    def stake_tokens(self, wallet_address, amount, private_key):
        """Realiza stake de tokens"""
        account = self.w3.eth.account.from_key(private_key)
        
        # Aprova tokens primeiro (se necessário)
        # ... código de aprovação ...
        
        # Realiza stake
        tx = self.stake_contract.functions.stake(amount).buildTransaction({
            'from': wallet_address,
            'nonce': self.w3.eth.get_transaction_count(wallet_address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return tx_hash.hex()
```

---

## 🔗 Integração Scroll L2

### 🌐 Por que Scroll L2?

1. **Baixas Taxas**: Transações muito mais baratas que Ethereum mainnet
2. **Compatibilidade EVM**: Código Solidity funciona sem modificações
3. **Segurança**: Herda segurança da Ethereum mainnet
4. **Escalabilidade**: Suporta alto throughput de transações

### 📡 Configuração da Rede

```python
# Configuração Scroll Sepolia (Testnet) - MVP ATUAL
SCROLL_RPC_URL = "https://sepolia-rpc.scroll.io"
SCROLL_CHAIN_ID = 534351
CONTRACT_ADDRESS = "0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7"  # SNELicenseRegistry deployado

# Configuração Scroll Mainnet (Produção) - V2
SCROLL_MAINNET_RPC = "https://rpc.scroll.io"
SCROLL_MAINNET_CHAIN_ID = 534352
CONTRACT_ADDRESS_MAINNET = "0x..."  # A ser deployado na V2
```

### 🚀 Contrato Deployado (MVP - Scroll Sepolia)

**Status**: ✅ **DEPLOYADO E OPERACIONAL**

- **Endereço do Contrato**: `0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7`
- **Rede**: Scroll Sepolia Testnet
- **Chain ID**: 534351
- **Block Number**: 15460541
- **Transaction Hash**: `9d3f023a84c498402eb8ccdf5926628c2d2f42de8734edf301f89ec681cab61d`
- **Gas Used**: 672,612
- **Explorer**: https://sepolia-blockscout.scroll.io/address/0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7

**Owner Atual**: `0x285df7643e6BD727527Fa3BA4Ff39dA729511bde`

> ⚠️ **Nota**: Este é o contrato de teste na Scroll Sepolia. Para produção (V2), será necessário fazer novo deploy na Scroll Mainnet.

### 🔄 Fluxo Completo de Integração

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO COMPLETO                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Inicialização do Sistema                                │
│     ├─ Conecta à Scroll L2                                  │
│     ├─ Carrega contrato inteligente                         │
│     └─ Verifica conexão                                     │
│                                                              │
│  2. Verificação de Licença (Startup)                        │
│     ├─ Solicita conexão de carteira                         │
│     ├─ Verifica posse de NFT/Stake                          │
│     ├─ Valida status on-chain                               │
│     └─ Se válido: Inicia sistema                            │
│                                                              │
│  3. Healthcheck Periódico                                   │
│     ├─ Coleta métricas do sistema                           │
│     ├─ Gera hash do healthcheck                             │
│     ├─ Registra na blockchain                               │
│     └─ Atualiza Proof of Uptime                             │
│                                                              │
│  4. Validação Contínua                                      │
│     ├─ Verifica licença a cada X minutos                    │
│     ├─ Se licença revogada: Bloqueia acesso                 │
│     └─ Log de eventos                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Segurança e Anti-Pirataria

### 🔒 Medidas Implementadas

1. **Verificação On-Chain**: Impossível burlar sem acesso à blockchain
2. **Assinatura de Transações**: Requer chave privada da carteira
3. **Validação Periódica**: Verifica licença continuamente
4. **Registro Imutável**: Histórico de uso registrado permanentemente
5. **Node ID Único**: Cada instalação tem identificador único

### ⚠️ Limitações e Considerações

1. **Custo de Transações**: Mesmo em L2, há custos (minimizados)
2. **Dependência de Internet**: Requer conexão para verificar licença
3. **Latência**: Verificação on-chain pode ter latência
4. **Cache Local**: Necessário para otimização (com expiração)

---

## 📊 Métricas e Monitoramento

### 📈 Dados Coletados

- **Uptime por Node**: Tempo de operação de cada instalação
- **Healthcheck Frequency**: Frequência de healthchecks
- **License Status**: Status de todas as licenças
- **Transaction History**: Histórico de transações relacionadas

### 🔍 Auditoria

- **On-Chain**: Qualquer um pode verificar na blockchain
- **Off-Chain**: Dashboard administrativo para análise
- **Relatórios**: Geração automática de relatórios de compliance

---

## 🚀 Roadmap e Evolução

### Fase 1: Distribution (Atual) - MVP
- ✅ Integração Scroll Testnet (Sepolia)
- ✅ Smart License Check básico - **CONTRATO DEPLOYADO**
- ✅ Contrato SNELicenseRegistry operacional: `0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7`
- ⏳ Lançamento 100 Licenças Vitalícias
- ⏳ Integração com cliente Python do SNE Radar

### Fase 2: The SNE Box (Q1 2026)
- ⏳ Hardware proprietário (Raspberry Pi Custom)
- ⏳ Integração Starlink
- ⏳ Mineração de tokens via Proof of Stake

### Fase 3: The Sovereign Network
- ⏳ Rede Mesh descentralizada
- ⏳ Dados financeiros descentralizados
- ⏳ Governança descentralizada

---

## 📚 Referências Técnicas

- **Scroll Documentation**: https://docs.scroll.io
- **Web3.py**: https://web3py.readthedocs.io
- **Solidity**: https://docs.soliditylang.org
- **ERC-721**: https://eips.ethereum.org/EIPS/eip-721
- **ERC-20**: https://eips.ethereum.org/EIPS/eip-20

---

## 🔍 Conclusão

A integração Web3 do SNE RADAR representa uma inovação significativa no licenciamento de software, combinando:

- **Descentralização**: Sem dependência de servidores centrais
- **Transparência**: Código e histórico auditáveis
- **Segurança**: Impossível falsificar sem acesso à blockchain
- **Flexibilidade**: Modelo de licenciamento tokenizado e transferível

Esta arquitetura prepara o sistema para a evolução para uma rede DePIN (Decentralized Physical Infrastructure Network), onde múltiplos nós operam de forma descentralizada, validando e registrando atividade on-chain.

---

**Última Atualização**: 2025-01-15  
**Versão do Documento**: 2.0  
**Status**: Arquitetura Alvo para Produção (V2)

