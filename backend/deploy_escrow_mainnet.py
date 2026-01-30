"""
Deploy TSTEscrow Contract to BSC Mainnet

This script deploys the TSTEscrow contract which allows P2P escrow agreements
using TST tokens.

Prerequisites:
1. DEPLOYER_PRIVATE_KEY in .env (wallet with BNB for gas)
2. TST token already deployed (0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71)

Usage:
    python backend/deploy_escrow_mainnet.py
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import solcx

# Load environment
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION - BSC MAINNET
# ═══════════════════════════════════════════════════════════════════

# BSC Mainnet RPC
RPC_URL = "https://bsc-dataseed1.binance.org"

# Your existing TST Token on mainnet
TST_TOKEN_ADDRESS = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"

# Deployer wallet private key (from .env)
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

if not PRIVATE_KEY:
    print("❌ Error: DEPLOYER_PRIVATE_KEY not found in .env")
    print("   Add your wallet private key to the .env file")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
# CONTRACT SOURCE (Flattened - no imports needed)
# ═══════════════════════════════════════════════════════════════════

# Flattened TSTEscrow contract (OpenZeppelin code inlined)
ESCROW_SOURCE = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// OpenZeppelin IERC20 Interface
interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

/**
 * @title TSTEscrow
 * @dev Escrow contract for TST token P2P agreements
 */
contract TSTEscrow {

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

    function depositFunds(uint256 agreementId) external agreementExists(agreementId) {
        Agreement storage agr = agreements[agreementId];
        require(msg.sender == agr.payer, "Only payer can deposit");
        require(agr.status == Status.Created, "Invalid status");

        agr.status = Status.Funded;
        require(tstToken.transferFrom(msg.sender, address(this), agr.amount), "Transfer failed");

        emit FundsDeposited(agreementId, agr.amount);
    }

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

        require(tstToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");

        emit AgreementCreated(agreementId, msg.sender, payee, amount, description);
        emit FundsDeposited(agreementId, amount);
        
        return agreementId;
    }

    function releaseFunds(uint256 agreementId) external agreementExists(agreementId) {
        Agreement storage agr = agreements[agreementId];
        require(agr.status == Status.Funded, "Not funded");
        require(msg.sender == agr.payer || msg.sender == admin, "Unauthorized");

        agr.status = Status.Released;
        agr.completedAt = block.timestamp;
        require(tstToken.transfer(agr.payee, agr.amount), "Transfer failed");

        emit FundsReleased(agreementId, agr.payee, agr.amount);
    }

    function refundFunds(uint256 agreementId) external onlyAdmin agreementExists(agreementId) {
        Agreement storage agr = agreements[agreementId];
        require(agr.status == Status.Funded, "Not funded");

        agr.status = Status.Refunded;
        agr.completedAt = block.timestamp;
        require(tstToken.transfer(agr.payer, agr.amount), "Transfer failed");

        emit FundsRefunded(agreementId, agr.payer, agr.amount);
    }

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

    function setAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "Invalid admin");
        admin = newAdmin;
    }
}
'''

def compile_contract():
    """Compile the flattened contract source"""
    print("📝 Compiling TSTEscrow contract...")
    
    # Install solc if needed
    try:
        solcx.install_solc('0.8.0')
    except:
        pass
    
    compiled = solcx.compile_source(
        ESCROW_SOURCE,
        output_values=['abi', 'bin'],
        solc_version='0.8.0'
    )
    
    # Get TSTEscrow interface
    contract_id = '<stdin>:TSTEscrow'
    if contract_id not in compiled:
        # Try to find it
        for key in compiled.keys():
            if 'TSTEscrow' in key:
                contract_id = key
                break
    
    return compiled[contract_id]


def main():
    print("="*60)
    print("TSTEscrow Deployment to BSC Mainnet")
    print("="*60)
    
    # Setup Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    if not w3.is_connected():
        print("❌ Failed to connect to BSC Mainnet")
        return
    
    print(f"✅ Connected to BSC Mainnet (Chain ID: {w3.eth.chain_id})")
    
    # Load account
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"📍 Deployer Address: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    balance_bnb = w3.from_wei(balance, 'ether')
    print(f"💰 Balance: {balance_bnb} BNB")
    
    if balance_bnb < 0.01:
        print("⚠️  Warning: Low BNB balance. Need ~0.01 BNB for deployment gas.")
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            return
    
    # Compile contract
    contract_interface = compile_contract()
    print("✅ Contract compiled successfully")
    
    # Prepare deployment
    Contract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )
    
    # Build transaction
    print(f"\n🔗 Deploying with TST Token: {TST_TOKEN_ADDRESS}")
    
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price
    
    construct_txn = Contract.constructor(TST_TOKEN_ADDRESS).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 3000000,  # Increased gas limit
        'gasPrice': gas_price
    })
    
    # Estimate actual gas
    try:
        estimated_gas = w3.eth.estimate_gas(construct_txn)
        print(f"⛽ Estimated Gas: {estimated_gas}")
        construct_txn['gas'] = int(estimated_gas * 1.2)  # 20% buffer
    except Exception as e:
        print(f"⚠️  Gas estimation failed: {e}")
    
    # Confirm deployment
    gas_cost = w3.from_wei(construct_txn['gas'] * gas_price, 'ether')
    print(f"💸 Estimated Cost: ~{gas_cost:.6f} BNB")
    
    confirm = input("\n🚀 Deploy to MAINNET? This is irreversible! (yes/no): ")
    if confirm.lower() != 'yes':
        print("Deployment cancelled.")
        return
    
    # Sign and send
    print("\n📤 Sending deployment transaction...")
    signed = w3.eth.account.sign_transaction(construct_txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"📋 TX Hash: {tx_hash.hex()}")
    print(f"🔍 View on BscScan: https://bscscan.com/tx/{tx_hash.hex()}")
    
    # Wait for confirmation
    print("\n⏳ Waiting for confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    if tx_receipt.status == 1:
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("="*60)
        print(f"📍 TSTEscrow Address: {tx_receipt.contractAddress}")
        print(f"🔗 TST Token: {TST_TOKEN_ADDRESS}")
        print(f"⛽ Gas Used: {tx_receipt.gasUsed}")
        print(f"🔍 https://bscscan.com/address/{tx_receipt.contractAddress}")
        print("="*60)
        print("\n📝 Next Steps:")
        print(f"1. Update frontend/src/lib/contracts.ts:")
        print(f'   ESCROW: "{tx_receipt.contractAddress}",')
        print("2. Commit and push to deploy changes")
        print("="*60)
        
        # Save deployment info
        deployment_info = {
            "network": "BSC Mainnet",
            "chainId": 56,
            "escrowAddress": tx_receipt.contractAddress,
            "tstTokenAddress": TST_TOKEN_ADDRESS,
            "deployerAddress": account.address,
            "txHash": tx_hash.hex(),
            "blockNumber": tx_receipt.blockNumber,
            "gasUsed": tx_receipt.gasUsed
        }
        
        with open("escrow_deployment.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        print("\n💾 Deployment info saved to escrow_deployment.json")
        
    else:
        print("❌ Deployment failed! Check transaction on BscScan.")


if __name__ == "__main__":
    main()
