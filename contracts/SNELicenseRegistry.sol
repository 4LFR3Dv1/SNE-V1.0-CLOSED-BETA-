// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SNELicenseRegistry
 * @author SNE Radar Development Team
 * @notice Smart Contract para controle de acesso e validação de licenças do SNE Radar
 * @dev Este contrato implementa um sistema de DRM descentralizado para o SNE Radar,
 *      funcionando como a camada "Verdade On-Chain" na arquitetura híbrida do sistema.
 * 
 * @dev Arquitetura Híbrida:
 *      - Off-Chain (Python): Processamento de análise técnica, ML e execução de trades
 *      - On-Chain (Este Contrato): Validação de licenças, auditoria e controle de acesso
 * 
 * @dev O SNE Radar utiliza este contrato na rede Scroll L2 para:
 *      1. Verificar se um endereço possui licença válida antes de iniciar o sistema
 *      2. Registrar eventos de acesso para auditoria on-chain
 *      3. Implementar sistema anti-pirataria descentralizado
 *      4. Preparar infraestrutura para rede DePIN (Decentralized Physical Infrastructure Network)
 * 
 * @dev Licenças Vitalícias:
 *      - Uma vez concedida, a licença não expira (licenseExpiry = 0 ou timestamp muito futuro)
 *      - Pode ser revogada apenas pelo Owner do contrato
 *      - Histórico completo de concessões/revogações registrado on-chain
 */
contract SNELicenseRegistry is Ownable {
    
    // ============ State Variables ============
    
    /**
     * @notice Mapping que armazena se um endereço possui licença autorizada
     * @dev true = licença ativa, false = sem licença ou revogada
     */
    mapping(address => bool) public authorizedUsers;
    
    /**
     * @notice Mapping que armazena timestamp de expiração da licença
     * @dev 0 = licença vitalícia, timestamp > 0 = data de expiração
     * @dev Para licenças vitalícias, pode ser definido como type(uint256).max
     */
    mapping(address => uint256) public licenseExpiry;
    
    /**
     * @notice Contador total de licenças emitidas (apenas para estatísticas)
     */
    uint256 public totalLicensesGranted;
    
    /**
     * @notice Contador de licenças ativas no momento
     */
    uint256 public activeLicensesCount;
    
    // ============ Events ============
    
    /**
     * @notice Emitido quando uma licença é concedida a um endereço
     * @param user Endereço que recebeu a licença
     * @param grantedBy Endereço que concedeu a licença (Owner)
     * @param expiryTimestamp Timestamp de expiração (0 = vitalícia)
     * @param timestamp Timestamp do bloco em que a licença foi concedida
     */
    event LicenseGranted(
        address indexed user,
        address indexed grantedBy,
        uint256 expiryTimestamp,
        uint256 timestamp
    );
    
    /**
     * @notice Emitido quando uma licença é revogada de um endereço
     * @param user Endereço que teve a licença revogada
     * @param revokedBy Endereço que revogou a licença (Owner)
     * @param timestamp Timestamp do bloco em que a licença foi revogada
     */
    event LicenseRevoked(
        address indexed user,
        address indexed revokedBy,
        uint256 timestamp
    );
    
    // ============ Modifiers ============
    
    /**
     * @notice Modifier que verifica se o endereço possui licença válida
     * @param user Endereço a ser verificado
     */
    modifier onlyAuthorized(address user) {
        require(
            checkAccess(user),
            "SNELicenseRegistry: Address does not have valid license"
        );
        _;
    }
    
    // ============ Constructor ============
    
    /**
     * @notice Construtor do contrato
     * @dev O deployer do contrato se torna o Owner inicial
     * @dev Pode ser transferido para um multisig ou DAO no futuro
     */
    constructor() Ownable(msg.sender) {
        // Owner inicial não precisa de licença, mas pode ser adicionado se necessário
    }
    
    // ============ Owner Functions ============
    
    /**
     * @notice Concede licença vitalícia a um endereço
     * @dev Apenas o Owner pode executar esta função
     * @dev Licença vitalícia = licenseExpiry definido como type(uint256).max
     * @param user Endereço que receberá a licença vitalícia
     * 
     * @dev Fluxo de uso no SNE Radar:
     *      1. Cliente Python conecta à Scroll L2
     *      2. Chama checkAccess(wallet_address) antes de iniciar
     *      3. Se retornar true, sistema inicia normalmente
     *      4. Se retornar false, sistema bloqueia acesso
     * 
     * @dev Emite evento LicenseGranted para auditoria on-chain
     */
    function grantLifetimeLicense(address user) external onlyOwner {
        require(user != address(0), "SNELicenseRegistry: Cannot grant license to zero address");
        require(!authorizedUsers[user], "SNELicenseRegistry: User already has active license");
        
        // Concede licença vitalícia
        authorizedUsers[user] = true;
        licenseExpiry[user] = type(uint256).max; // Vitalícia = valor máximo
        
        // Atualiza contadores
        totalLicensesGranted++;
        activeLicensesCount++;
        
        // Emite evento para auditoria
        emit LicenseGranted(
            user,
            msg.sender,
            type(uint256).max,
            block.timestamp
        );
    }
    
    /**
     * @notice Concede licença com expiração a um endereço
     * @dev Apenas o Owner pode executar esta função
     * @dev Útil para licenças temporárias ou de teste
     * @param user Endereço que receberá a licença
     * @param expiryTimestamp Timestamp Unix de expiração (0 = vitalícia)
     * 
     * @dev Exemplo de uso:
     *      - Licença de 1 ano: expiryTimestamp = block.timestamp + 365 days
     *      - Licença vitalícia: expiryTimestamp = type(uint256).max
     */
    function grantLicense(address user, uint256 expiryTimestamp) external onlyOwner {
        require(user != address(0), "SNELicenseRegistry: Cannot grant license to zero address");
        require(!authorizedUsers[user], "SNELicenseRegistry: User already has active license");
        
        // Se expiryTimestamp for 0, trata como vitalícia
        uint256 expiry = expiryTimestamp == 0 ? type(uint256).max : expiryTimestamp;
        
        authorizedUsers[user] = true;
        licenseExpiry[user] = expiry;
        
        totalLicensesGranted++;
        activeLicensesCount++;
        
        emit LicenseGranted(
            user,
            msg.sender,
            expiry,
            block.timestamp
        );
    }
    
    /**
     * @notice Revoga licença de um endereço
     * @dev Apenas o Owner pode executar esta função
     * @dev Remove o endereço da lista de autorizados e zera o expiry
     * @param user Endereço que terá a licença revogada
     * 
     * @dev Casos de uso:
     *      - Violação de termos de serviço
     *      - Transferência de licença para novo endereço
     *      - Revogação temporária para manutenção
     * 
     * @dev Emite evento LicenseRevoked para auditoria on-chain
     */
    function revokeLicense(address user) external onlyOwner {
        require(user != address(0), "SNELicenseRegistry: Cannot revoke license from zero address");
        require(authorizedUsers[user], "SNELicenseRegistry: User does not have active license");
        
        // Revoga licença
        authorizedUsers[user] = false;
        licenseExpiry[user] = 0;
        
        // Atualiza contador
        activeLicensesCount--;
        
        // Emite evento para auditoria
        emit LicenseRevoked(
            user,
            msg.sender,
            block.timestamp
        );
    }
    
    /**
     * @notice Concede múltiplas licenças vitalícias em uma única transação
     * @dev Apenas o Owner pode executar esta função
     * @dev Otimiza gas para distribuição em massa (ex: 100 licenças iniciais)
     * @param users Array de endereços que receberão licenças
     * 
     * @dev Exemplo de uso na Fase 1 (Distribution):
     *      - Distribuir 100 licenças vitalícias para early adopters
     *      - Reduz custo de gas comparado a múltiplas transações individuais
     */
    function grantLifetimeLicensesBatch(address[] calldata users) external onlyOwner {
        require(users.length > 0, "SNELicenseRegistry: Empty array");
        require(users.length <= 100, "SNELicenseRegistry: Batch too large (max 100)");
        
        uint256 granted = 0;
        
        for (uint256 i = 0; i < users.length; i++) {
            address user = users[i];
            
            // Validações
            if (user == address(0)) continue;
            if (authorizedUsers[user]) continue;
            
            // Concede licença
            authorizedUsers[user] = true;
            licenseExpiry[user] = type(uint256).max;
            
            granted++;
            
            // Emite evento individual para cada licença
            emit LicenseGranted(
                user,
                msg.sender,
                type(uint256).max,
                block.timestamp
            );
        }
        
        // Atualiza contadores
        totalLicensesGranted += granted;
        activeLicensesCount += granted;
    }
    
    // ============ Public View Functions ============
    
    /**
     * @notice Verifica se um endereço possui acesso autorizado ao SNE Radar
     * @dev Esta é a função principal chamada pelo cliente Python antes de iniciar o sistema
     * @param user Endereço a ser verificado
     * @return bool true se o endereço possui licença válida, false caso contrário
     * 
     * @dev Validações realizadas:
     *      1. Verifica se está na lista authorizedUsers
     *      2. Verifica se a licença não expirou (se expiry > 0)
     *      3. Retorna false se qualquer validação falhar
     * 
     * @dev Integração com SNE Radar (Python):
     *      ```python
     *      def check_license(self, wallet_address):
     *          is_valid = self.contract.functions.checkAccess(wallet_address).call()
     *          if not is_valid:
     *              raise LicenseError("Acesso negado: Licença inválida ou expirada")
     *          return True
     *      ```
     */
    function checkAccess(address user) public view returns (bool) {
        // Verifica se está na lista de autorizados
        if (!authorizedUsers[user]) {
            return false;
        }
        
        // Verifica se a licença não expirou
        uint256 expiry = licenseExpiry[user];
        
        // Se expiry for 0, licença foi revogada
        if (expiry == 0) {
            return false;
        }
        
        // Se expiry for type(uint256).max, é vitalícia (sempre válida)
        if (expiry == type(uint256).max) {
            return true;
        }
        
        // Verifica se não expirou
        return block.timestamp < expiry;
    }
    
    /**
     * @notice Verifica se um endereço possui licença e retorna informações detalhadas
     * @param user Endereço a ser verificado
     * @return hasAccess true se possui acesso válido
     * @return isLifetime true se é licença vitalícia
     * @return expiryTimestamp Timestamp de expiração (0 se revogada, type(uint256).max se vitalícia)
     * 
     * @dev Útil para frontend/dashboard exibir status detalhado da licença
     */
    function getLicenseInfo(address user) 
        external 
        view 
        returns (
            bool hasAccess,
            bool isLifetime,
            uint256 expiryTimestamp
        ) 
    {
        hasAccess = checkAccess(user);
        expiryTimestamp = licenseExpiry[user];
        isLifetime = (expiryTimestamp == type(uint256).max);
        
        return (hasAccess, isLifetime, expiryTimestamp);
    }
    
    /**
     * @notice Retorna estatísticas do contrato
     * @return totalGranted Total de licenças já concedidas (histórico)
     * @return activeCount Número de licenças ativas no momento
     * 
     * @dev Útil para dashboards e análises
     */
    function getStats() external view returns (uint256 totalGranted, uint256 activeCount) {
        return (totalLicensesGranted, activeLicensesCount);
    }
    
    // ============ Emergency Functions ============
    
    /**
     * @notice Função de emergência para pausar todas as verificações
     * @dev Pode ser implementado com Pausable do OpenZeppelin se necessário
     * @dev Por enquanto, mantemos simples - Owner pode revogar todas as licenças se necessário
     */
    
    // ============ Future Enhancements ============
    
    /**
     * @dev Roadmap para futuras implementações:
     *      - Integração com NFT License (ERC-721) para licenças transferíveis
     *      - Sistema de staking de tokens (ERC-20) como alternativa de licenciamento
     *      - Healthcheck on-chain (Proof of Uptime) - registro de atividade dos nós
     *      - Multi-signature para Owner (transferência para multisig/DAO)
     *      - Upgradeability via Proxy Pattern (UUPS) se necessário
     */
}

