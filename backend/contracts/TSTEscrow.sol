// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title TSTEscrow
 * @dev Escrow contract for TST token P2P agreements
 * 
 * Flow:
 * 1. Payer creates agreement, specifying payee and TST amount
 * 2. Payer deposits TST tokens into escrow
 * 3. When deal is complete, payer (or admin) releases funds to payee
 * 4. If dispute, admin can refund to payer
 */
contract TSTEscrow {
    using SafeERC20 for IERC20;

    // Events
    event AgreementCreated(
        uint256 indexed agreementId, 
        address indexed payer, 
        address indexed payee, 
        uint256 amount,
        string description
    );
    event FundsDeposited(uint256 indexed agreementId, uint256 amount);
    event FundsReleased(uint256 indexed agreementId, address indexed payee, uint256 amount);
    event FundsRefunded(uint256 indexed agreementId, address indexed payer, uint256 amount);
    event AgreementCancelled(uint256 indexed agreementId);

    // Agreement states
    enum Status { Created, Funded, Released, Refunded, Cancelled }

    struct Agreement {
        address payer;
        address payee;
        uint256 amount;
        string description;
        Status status;
        uint256 createdAt;
        uint256 completedAt;
    }

    // State
    IERC20 public immutable tstToken;
    address public admin;
    uint256 public agreementCount;
    
    mapping(uint256 => Agreement) public agreements;
    mapping(address => uint256[]) public userAgreements;

    // Modifiers
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    modifier agreementExists(uint256 agreementId) {
        require(agreements[agreementId].payer != address(0), "Agreement not found");
        _;
    }

    constructor(address _tstToken) {
        require(_tstToken != address(0), "Invalid token address");
        tstToken = IERC20(_tstToken);
        admin = msg.sender;
    }

    /**
     * @dev Create a new escrow agreement
     * @param payee Address of the recipient
     * @param amount Amount of TST to escrow
     * @param description Description of the agreement
     */
    function createAgreement(
        address payee, 
        uint256 amount, 
        string calldata description
    ) external returns (uint256) {
        require(payee != address(0), "Invalid payee");
        require(payee != msg.sender, "Cannot escrow to self");
        require(amount > 0, "Amount must be > 0");

        agreementCount++;
        uint256 agreementId = agreementCount;

        agreements[agreementId] = Agreement({
            payer: msg.sender,
            payee: payee,
            amount: amount,
            description: description,
            status: Status.Created,
            createdAt: block.timestamp,
            completedAt: 0
        });

        userAgreements[msg.sender].push(agreementId);
        userAgreements[payee].push(agreementId);

        emit AgreementCreated(agreementId, msg.sender, payee, amount, description);
        return agreementId;
    }

    /**
     * @dev Deposit TST tokens into the escrow
     * @param agreementId The agreement to fund
     * 
     * NOTE: User must first approve this contract to spend TST tokens
     */
    function depositFunds(uint256 agreementId) external agreementExists(agreementId) {
        Agreement storage agr = agreements[agreementId];
        require(msg.sender == agr.payer, "Only payer can deposit");
        require(agr.status == Status.Created, "Invalid status");

        agr.status = Status.Funded;
        tstToken.safeTransferFrom(msg.sender, address(this), agr.amount);

        emit FundsDeposited(agreementId, agr.amount);
    }

    /**
     * @dev Create and fund agreement in one transaction
     * NOTE: User must first approve this contract to spend TST tokens
     */
    function createAndFund(
        address payee, 
        uint256 amount, 
        string calldata description
    ) external returns (uint256) {
        require(payee != address(0), "Invalid payee");
        require(payee != msg.sender, "Cannot escrow to self");
        require(amount > 0, "Amount must be > 0");

        agreementCount++;
        uint256 agreementId = agreementCount;

        agreements[agreementId] = Agreement({
            payer: msg.sender,
            payee: payee,
            amount: amount,
            description: description,
            status: Status.Funded,
            createdAt: block.timestamp,
            completedAt: 0
        });

        userAgreements[msg.sender].push(agreementId);
        userAgreements[payee].push(agreementId);

        tstToken.safeTransferFrom(msg.sender, address(this), amount);

        emit AgreementCreated(agreementId, msg.sender, payee, amount, description);
        emit FundsDeposited(agreementId, amount);
        
        return agreementId;
    }

    /**
     * @dev Release funds to the payee (payer confirms deal is complete)
     * @param agreementId The agreement to release
     */
    function releaseFunds(uint256 agreementId) external agreementExists(agreementId) {
        Agreement storage agr = agreements[agreementId];
        require(agr.status == Status.Funded, "Not funded");
        require(msg.sender == agr.payer || msg.sender == admin, "Unauthorized");

        agr.status = Status.Released;
        agr.completedAt = block.timestamp;
        tstToken.safeTransfer(agr.payee, agr.amount);

        emit FundsReleased(agreementId, agr.payee, agr.amount);
    }

    /**
     * @dev Refund funds to the payer (admin dispute resolution)
     * @param agreementId The agreement to refund
     */
    function refundFunds(uint256 agreementId) external onlyAdmin agreementExists(agreementId) {
        Agreement storage agr = agreements[agreementId];
        require(agr.status == Status.Funded, "Not funded");

        agr.status = Status.Refunded;
        agr.completedAt = block.timestamp;
        tstToken.safeTransfer(agr.payer, agr.amount);

        emit FundsRefunded(agreementId, agr.payer, agr.amount);
    }

    /**
     * @dev Cancel an unfunded agreement
     * @param agreementId The agreement to cancel
     */
    function cancelAgreement(uint256 agreementId) external agreementExists(agreementId) {
        Agreement storage agr = agreements[agreementId];
        require(agr.status == Status.Created, "Cannot cancel funded agreement");
        require(msg.sender == agr.payer, "Only payer can cancel");

        agr.status = Status.Cancelled;
        agr.completedAt = block.timestamp;

        emit AgreementCancelled(agreementId);
    }

    // View functions
    function getAgreement(uint256 agreementId) external view returns (
        address payer,
        address payee,
        uint256 amount,
        string memory description,
        Status status,
        uint256 createdAt,
        uint256 completedAt
    ) {
        Agreement storage agr = agreements[agreementId];
        return (
            agr.payer,
            agr.payee,
            agr.amount,
            agr.description,
            agr.status,
            agr.createdAt,
            agr.completedAt
        );
    }

    function getUserAgreements(address user) external view returns (uint256[] memory) {
        return userAgreements[user];
    }

    function getAgreementCount() external view returns (uint256) {
        return agreementCount;
    }

    // Admin functions
    function setAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "Invalid admin");
        admin = newAdmin;
    }
}
