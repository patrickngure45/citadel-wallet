// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CitadelEscrow {
    event AgreementCreated(uint256 indexed agreementId, address indexed payer, address indexed payee, uint256 amount);
    event FundsReleased(uint256 indexed agreementId, address indexed payee, uint256 amount);
    event FundsRefunded(uint256 indexed agreementId, address indexed payer, uint256 amount);

    struct Agreement {
        address payer;
        address payee;
        uint256 amount;
        bool isActive;
    }

    mapping(uint256 => Agreement) public agreements;
    address public admin;

    constructor() {
        admin = msg.sender;
    }

    // 1. Payer creates an agreement and locks ETH/BNB
    function createAgreement(uint256 agreementId, address payee) external payable {
        require(msg.value > 0, "Amount must be > 0");
        require(!agreements[agreementId].isActive, "ID already exists");

        agreements[agreementId] = Agreement({
            payer: msg.sender,
            payee: payee,
            amount: msg.value,
            isActive: true
        });

        emit AgreementCreated(agreementId, msg.sender, payee, msg.value);
    }

    // 2. Payer (or Admin) releases funds to Payee
    function releaseFunds(uint256 agreementId) external {
        Agreement storage agr = agreements[agreementId];
        require(agr.isActive, "Agreement not active");
        require(msg.sender == agr.payer || msg.sender == admin, "Unauthorized");

        agr.isActive = false;
        payable(agr.payee).transfer(agr.amount);

        emit FundsReleased(agreementId, agr.payee, agr.amount);
    }

    // 3. Admin can force refund to Payer (Safety hatch)
    function refundPayer(uint256 agreementId) external {
        require(msg.sender == admin, "Only Admin");
        Agreement storage agr = agreements[agreementId];
        require(agr.isActive, "Agreement not active");

        agr.isActive = false;
        payable(agr.payer).transfer(agr.amount);

        emit FundsRefunded(agreementId, agr.payer, agr.amount);
    }
}
