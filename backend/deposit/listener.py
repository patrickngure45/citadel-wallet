"""
Citadel - Deposit Listener & Fund Settlement
Monitors user wallets for deposits and sweeps to MASTER_WALLET
"""

from typing import Dict, Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum
from web3 import Web3


class DepositStatus(Enum):
    """Deposit lifecycle status."""
    DETECTED = "detected"
    VERIFIED = "verified"
    APPROVED = "approved"
    SWEEPING = "sweeping"
    SWEPT = "swept"
    SETTLED = "settled"
    FAILED = "failed"


class Deposit:
    """Represents a user deposit event."""
    
    def __init__(
        self,
        tx_hash: str,
        from_address: str,
        to_address: str,  # User wallet
        amount: Decimal,
        asset_type: str,  # "usdt", "usdc"
        chain: str,  # "bsc", "polygon"
        block_number: int,
        timestamp: datetime
    ):
        self.tx_hash = tx_hash
        self.from_address = from_address
        self.to_address = to_address  # User wallet receiving deposit
        self.amount = amount
        self.asset_type = asset_type
        self.chain = chain
        self.block_number = block_number
        self.timestamp = timestamp
        
        self.status = DepositStatus.DETECTED.value
        self.user_id: Optional[str] = None
        self.tst_reward: Decimal = Decimal(0)
        self.sweep_tx_hash: Optional[str] = None
        self.settled_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "tx_hash": self.tx_hash,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": str(self.amount),
            "asset_type": self.asset_type,
            "chain": self.chain,
            "block_number": self.block_number,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "user_id": self.user_id,
            "tst_reward": str(self.tst_reward),
            "sweep_tx_hash": self.sweep_tx_hash,
            "settled_at": self.settled_at.isoformat() if self.settled_at else None,
        }


class DepositListener:
    """
    Listens for deposits to user wallets.
    
    Process:
    1. Monitor blockchain for transfers to user wallet addresses
    2. Detect deposits (track tx_hash, amount, timestamp)
    3. Route to settlement (Risk entity approval)
    4. Sweep to MASTER_WALLET
    5. Credit user balance in database
    """
    
    # Minimum confirmations before processing
    MIN_CONFIRMATIONS = 12  # ~3 minutes on BSC
    
    # Supported assets
    SUPPORTED_ASSETS = {
        "bsc": {
            "usdt": "0x55d398326f99059fF775485246999027B3197955",
            "usdc": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
        },
        "polygon": {
            "usdt": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
            "usdc": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        }
    }
    
    def __init__(self, web3_providers: Dict[str, str]):
        """
        Initialize listener with Web3 providers.
        
        Args:
            web3_providers: {
                "bsc": "https://bsc-dataseed1.binance.org",
                "polygon": "https://polygon-rpc.com"
            }
        """
        self.web3 = {
            chain: Web3(Web3.HTTPProvider(url))
            for chain, url in web3_providers.items()
        }
        
        self.pending_deposits: Dict[str, Deposit] = {}
        self.settled_deposits: List[Deposit] = []
    
    def process_transfer_event(
        self,
        from_address: str,
        to_address: str,
        amount: Decimal,
        asset_type: str,
        chain: str,
        tx_hash: str,
        block_number: int,
        timestamp: datetime
    ) -> Optional[Deposit]:
        """
        Process a detected transfer event.
        
        This is called by a blockchain listener (e.g., Web3 event listener)
        when a transfer is detected to a user wallet.
        
        Args:
            to_address: User wallet receiving deposit
            amount: Amount transferred
            asset_type: "usdt" or "usdc"
            chain: "bsc" or "polygon"
        
        Returns: Deposit object if valid, None if filtered
        """
        # Validate asset
        if asset_type not in self.SUPPORTED_ASSETS.get(chain, {}):
            return None
        
        # Create deposit
        deposit = Deposit(
            tx_hash=tx_hash,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            asset_type=asset_type,
            chain=chain,
            block_number=block_number,
            timestamp=timestamp
        )
        
        # Store in pending
        self.pending_deposits[tx_hash] = deposit
        
        return deposit
    
    def get_pending_deposits(self) -> List[Deposit]:
        """Get all pending deposits."""
        return list(self.pending_deposits.values())
    
    def mark_verified(self, tx_hash: str, user_id: str) -> bool:
        """
        Mark deposit as verified (linked to user).
        
        Called after confirming deposit is from legitimate source.
        """
        if tx_hash not in self.pending_deposits:
            return False
        
        deposit = self.pending_deposits[tx_hash]
        deposit.status = DepositStatus.VERIFIED.value
        deposit.user_id = user_id
        
        return True
    
    def calculate_tst_reward(self, amount_usd: Decimal) -> Decimal:
        """
        Calculate TST reward for deposit.
        
        Reward: 1 TST per $100 USDT deposited
        Example: $500 deposit → 5 TST
        """
        reward = amount_usd / Decimal(100)
        return reward.quantize(Decimal("0.01"))
    
    def mark_approved(self, tx_hash: str, tst_reward: Decimal) -> bool:
        """Mark deposit as approved by Risk entity."""
        if tx_hash not in self.pending_deposits:
            return False
        
        deposit = self.pending_deposits[tx_hash]
        deposit.status = DepositStatus.APPROVED.value
        deposit.tst_reward = tst_reward
        
        return True
    
    def mark_sweep_initiated(self, tx_hash: str) -> bool:
        """Mark sweep transaction as initiated."""
        if tx_hash not in self.pending_deposits:
            return False
        
        deposit = self.pending_deposits[tx_hash]
        deposit.status = DepositStatus.SWEEPING.value
        
        return True
    
    def mark_swept(self, deposit_tx_hash: str, sweep_tx_hash: str) -> bool:
        """Mark deposit as swept to MASTER_WALLET."""
        if deposit_tx_hash not in self.pending_deposits:
            return False
        
        deposit = self.pending_deposits[deposit_tx_hash]
        deposit.status = DepositStatus.SWEPT.value
        deposit.sweep_tx_hash = sweep_tx_hash
        
        return True
    
    def mark_settled(self, tx_hash: str) -> bool:
        """
        Mark deposit as fully settled (user balance credited).
        
        Moves from pending to settled.
        """
        if tx_hash not in self.pending_deposits:
            return False
        
        deposit = self.pending_deposits[tx_hash]
        deposit.status = DepositStatus.SETTLED.value
        deposit.settled_at = datetime.utcnow()
        
        # Move to settled list
        self.settled_deposits.append(deposit)
        del self.pending_deposits[tx_hash]
        
        return True
    
    def mark_failed(self, tx_hash: str, reason: str) -> bool:
        """Mark deposit as failed."""
        if tx_hash not in self.pending_deposits:
            return False
        
        deposit = self.pending_deposits[tx_hash]
        deposit.status = DepositStatus.FAILED.value
        
        return True


class FundSettlement:
    """
    Handles fund settlement workflow.
    
    Process:
    1. Deposit detected in user wallet
    2. Risk entity verifies (checks for anomalies)
    3. If approved: create multi-sig sweep transaction
    4. Strategy entity confirms sweep is sound
    5. Execution entity broadcasts sweep
    6. Monitor sweep confirmation
    7. Credit user balance in database
    8. Award TST tokens
    """
    
    def __init__(self, master_wallet_address: str):
        self.master_wallet_address = master_wallet_address
        self.settlement_queue: List[Deposit] = []
    
    def queue_for_settlement(self, deposit: Deposit) -> bool:
        """Queue deposit for settlement after Risk approval."""
        if deposit.status != DepositStatus.APPROVED.value:
            return False
        
        self.settlement_queue.append(deposit)
        return True
    
    def get_next_to_settle(self) -> Optional[Deposit]:
        """Get next deposit to settle."""
        if not self.settlement_queue:
            return None
        
        return self.settlement_queue[0]
    
    def create_sweep_transaction(self, deposit: Deposit) -> Dict:
        """
        Create sweep transaction to MASTER_WALLET.
        
        Returns transaction object awaiting signatures.
        """
        sweep_tx = {
            "type": "sweep_deposit",
            "from_address": deposit.to_address,  # User wallet
            "to_address": self.master_wallet_address,  # Master wallet
            "amount": str(deposit.amount),
            "asset_type": deposit.asset_type,
            "chain": deposit.chain,
            "deposit_tx_hash": deposit.tx_hash,
            "created_at": datetime.utcnow().isoformat(),
            "signers_required": 2,  # 2-of-3 multi-sig
            "signatures": [],
            "status": "awaiting_signatures"
        }
        
        return sweep_tx
    
    def process_sweep_confirmation(self, deposit_tx_hash: str, sweep_tx_hash: str) -> Dict:
        """
        After sweep is confirmed on-chain, create settlement record.
        
        Returns settlement summary for database credit.
        """
        settlement = {
            "deposit_tx_hash": deposit_tx_hash,
            "sweep_tx_hash": sweep_tx_hash,
            "settled_at": datetime.utcnow().isoformat(),
            "status": "confirmed",
            "next_steps": [
                "1. Credit user balance in database",
                "2. Award TST tokens",
                "3. Update performance metrics",
                "4. Log in audit trail"
            ]
        }
        
        return settlement


class DepositSettlementOrchestrator:
    """
    Orchestrates the full deposit → settlement flow.
    
    Coordinates:
    - Deposit detection
    - Risk entity verification
    - Multi-sig sweep approval
    - Database updates
    - TST rewards
    """
    
    def __init__(
        self,
        listener: DepositListener,
        settlement: FundSettlement,
        master_wallet: str
    ):
        self.listener = listener
        self.settlement = settlement
        self.master_wallet = master_wallet
    
    def process_deposit_workflow(
        self,
        deposit: Deposit,
        user_id: str,
        risk_approved: bool,
        tst_reward: Decimal
    ) -> Dict:
        """
        Execute full deposit workflow.
        
        Args:
            deposit: Detected deposit
            user_id: User to credit
            risk_approved: Risk entity approval status
            tst_reward: TST tokens to award
        
        Returns: Settlement workflow summary
        """
        workflow_log = {
            "deposit_tx_hash": deposit.tx_hash,
            "user_id": user_id,
            "amount": str(deposit.amount),
            "asset_type": deposit.asset_type,
            "steps_completed": []
        }
        
        # Step 1: Mark as verified
        self.listener.mark_verified(deposit.tx_hash, user_id)
        workflow_log["steps_completed"].append("verified")
        
        # Step 2: Risk entity approval
        if not risk_approved:
            workflow_log["status"] = "rejected_by_risk"
            return workflow_log
        
        self.listener.mark_approved(deposit.tx_hash, tst_reward)
        workflow_log["steps_completed"].append("approved_by_risk")
        
        # Step 3: Queue for settlement
        self.settlement.queue_for_settlement(deposit)
        workflow_log["steps_completed"].append("queued_for_settlement")
        
        # Step 4: Create sweep transaction (awaits multi-sig)
        sweep_tx = self.settlement.create_sweep_transaction(deposit)
        workflow_log["sweep_tx"] = sweep_tx
        workflow_log["steps_completed"].append("sweep_tx_created")
        
        # Step 5: (After sweep is confirmed) Mark as swept
        # This would be done by sweep confirmation listener
        # self.listener.mark_swept(deposit.tx_hash, sweep_tx_hash)
        # workflow_log["steps_completed"].append("swept")
        
        # Step 6: (After swap confirmation) Settle
        # This would be done after on-chain confirmation
        # self.listener.mark_settled(deposit.tx_hash)
        # workflow_log["steps_completed"].append("settled")
        
        workflow_log["status"] = "awaiting_sweep_signatures"
        workflow_log["next_action"] = "Entity system to collect 2-of-3 signatures"
        
        return workflow_log


# Example usage
if __name__ == "__main__":
    from decimal import Decimal
    
    # Initialize listener
    listener = DepositListener({
        "bsc": "https://bsc-dataseed1.binance.org",
        "polygon": "https://polygon-mainnet.g.alchemy.com/v2/a-dy4J4WsLejZXeEHWtnB"
    })
    
    # Simulate: User deposits $500 USDT to BSC
    deposit = listener.process_transfer_event(
        from_address="0xSenderAddress",
        to_address="0x578FC7311a846997dc99bF2d4C651418DcFe309A",  # User wallet 1
        amount=Decimal("500"),
        asset_type="usdt",
        chain="bsc",
        tx_hash="0xdeposit123",
        block_number=12345,
        timestamp=datetime.utcnow()
    )
    
    print(f"Deposit detected: {deposit.tx_hash}")
    print(f"Amount: ${deposit.amount} {deposit.asset_type}")
    print(f"Status: {deposit.status}")
    
    # Calculate reward
    tst_reward = listener.calculate_tst_reward(Decimal("500"))
    print(f"TST Reward: {tst_reward}")
    
    # Initialize settlement
    master_wallet = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"
    settlement = FundSettlement(master_wallet)
    
    # Initialize orchestrator
    orchestrator = DepositSettlementOrchestrator(
        listener,
        settlement,
        master_wallet
    )
    
    # Process workflow
    print("\n=== Processing Deposit Workflow ===")
    workflow = orchestrator.process_deposit_workflow(
        deposit=deposit,
        user_id="user_123",
        risk_approved=True,
        tst_reward=tst_reward
    )
    
    print(f"Status: {workflow['status']}")
    print(f"Steps: {workflow['steps_completed']}")
    print(f"Next action: {workflow['next_action']}")
    print(f"\nSweep transaction awaiting signatures:")
    print(f"  From: {workflow['sweep_tx']['from_address']}")
    print(f"  To: {workflow['sweep_tx']['to_address']}")
    print(f"  Amount: {workflow['sweep_tx']['amount']} {workflow['sweep_tx']['asset_type']}")
