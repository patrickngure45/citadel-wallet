"""
Citadel - Multi-Signature Signing Logic
Implements 2-of-3 and 3-of-3 multi-sig for wallet tiers.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import hashlib


class EntityType(Enum):
    """Entity types that can sign transactions."""
    RISK = "risk"
    STRATEGY = "strategy"
    EXECUTION = "execution"


@dataclass
class Signature:
    """Represents a cryptographic signature."""
    signer_entity: EntityType
    signature_hex: str
    timestamp: datetime
    approved: bool


class SigningPolicy:
    """Base class for signing policies."""
    
    def __init__(self, required_signers: int, total_signers: int):
        self.required_signers = required_signers
        self.total_signers = total_signers
        self.signatures: List[Signature] = []
    
    def add_signature(self, entity: EntityType, signature_hex: str, approved: bool = True) -> bool:
        """
        Add a signature from an entity.
        
        Returns: True if threshold met, False otherwise
        """
        # Prevent duplicate signatures from same entity
        if any(sig.signer_entity == entity for sig in self.signatures):
            raise ValueError(f"{entity.value} has already signed")
        
        sig = Signature(
            signer_entity=entity,
            signature_hex=signature_hex,
            timestamp=datetime.utcnow(),
            approved=approved
        )
        self.signatures.append(sig)
        
        return self.is_satisfied()
    
    def is_satisfied(self) -> bool:
        """Check if signing threshold is met."""
        approved_count = sum(1 for sig in self.signatures if sig.approved)
        return approved_count >= self.required_signers
    
    def get_approval_status(self) -> Dict:
        """Get current approval status."""
        approved = sum(1 for sig in self.signatures if sig.approved)
        return {
            "required": self.required_signers,
            "approved": approved,
            "total_signers": self.total_signers,
            "satisfied": self.is_satisfied(),
            "signers": [
                {
                    "entity": sig.signer_entity.value,
                    "approved": sig.approved,
                    "timestamp": sig.timestamp.isoformat()
                }
                for sig in self.signatures
            ]
        }


class MasterWalletPolicy(SigningPolicy):
    """
    2-of-3 multi-sig for MASTER_WALLET.
    
    Requires 2 approvals from:
    - Risk Entity
    - Strategy Entity
    - Execution Entity
    
    Purpose: Consolidate user deposits (funds sweep)
    """
    
    def __init__(self):
        super().__init__(required_signers=2, total_signers=3)


class SigningWalletPolicy(SigningPolicy):
    """
    3-of-3 multi-sig for SIGNING_WALLET.
    
    Requires ALL 3 entities to approve:
    - Risk Entity (confidence check)
    - Strategy Entity (decision confirmation)
    - Execution Entity (broadcast authorization)
    
    Purpose: Execute strategy trades
    """
    
    def __init__(self):
        super().__init__(required_signers=3, total_signers=3)


class UserWalletPolicy(SigningPolicy):
    """
    Single-signature for USER_WALLET.
    
    User signs directly via MetaMask.
    Citadel never holds private key.
    
    Purpose: Receive user deposits
    """
    
    def __init__(self):
        # User wallets don't need multi-sig
        # They just receive transfers (signatures not checked)
        super().__init__(required_signers=1, total_signers=1)


class TransactionSigningManager:
    """Manages signing of transactions with appropriate policies."""
    
    def __init__(self):
        self.pending_signatures: Dict[str, SigningPolicy] = {}
    
    def create_signing_request(self, tx_hash: str, wallet_tier: str) -> str:
        """
        Create a new signing request.
        
        Args:
            tx_hash: Hash of transaction to sign
            wallet_tier: "user", "master", or "signing"
        
        Returns: Request ID for tracking
        """
        if wallet_tier == "master":
            policy = MasterWalletPolicy()
        elif wallet_tier == "signing":
            policy = SigningWalletPolicy()
        elif wallet_tier == "user":
            policy = UserWalletPolicy()
        else:
            raise ValueError(f"Unknown wallet tier: {wallet_tier}")
        
        self.pending_signatures[tx_hash] = policy
        return tx_hash
    
    def add_signature(self, tx_hash: str, entity: EntityType, signature_hex: str, approved: bool = True) -> bool:
        """
        Add a signature to pending transaction.
        
        Returns: True if all signatures collected, False if waiting for more
        """
        if tx_hash not in self.pending_signatures:
            raise ValueError(f"No pending signature request for {tx_hash}")
        
        policy = self.pending_signatures[tx_hash]
        return policy.add_signature(entity, signature_hex, approved)
    
    def get_status(self, tx_hash: str) -> Dict:
        """Get signing status for transaction."""
        if tx_hash not in self.pending_signatures:
            raise ValueError(f"No pending signature request for {tx_hash}")
        
        return self.pending_signatures[tx_hash].get_approval_status()
    
    def can_execute(self, tx_hash: str) -> bool:
        """Check if transaction can be executed."""
        if tx_hash not in self.pending_signatures:
            return False
        
        return self.pending_signatures[tx_hash].is_satisfied()


class WalletRotationSigningManager:
    """
    Manages signatures for wallet rotation.
    
    Requirements:
    - Risk Entity approves rotation
    - Strategy Entity confirms
    - Execution Entity broadcasts new wallet setup
    """
    
    @staticmethod
    def create_rotation_request(old_address: str, new_address: str) -> Dict:
        """
        Create wallet rotation request.
        
        Returns request object awaiting signatures.
        """
        return {
            "type": "wallet_rotation",
            "old_address": old_address,
            "new_address": new_address,
            "requested_at": datetime.utcnow().isoformat(),
            "policy": MasterWalletPolicy().get_approval_status(),
            "status": "pending_signatures"
        }


# Example usage
if __name__ == "__main__":
    from datetime import datetime
    
    # Create signing manager
    manager = TransactionSigningManager()
    
    # Simulate: User deposits $1000 USDT to user wallet
    # This needs to be swept to MASTER_WALLET
    # Requires 2-of-3 approvals
    
    tx_hash = "0x1234567890abcdef"
    request_id = manager.create_signing_request(tx_hash, "master")
    print(f"Created signing request: {request_id}")
    
    # Check initial status
    status = manager.get_status(tx_hash)
    print(f"\nInitial status: {status}")
    
    # Risk entity approves
    print("\n--- Risk Entity Approves ---")
    manager.add_signature(tx_hash, EntityType.RISK, "0xrisk_sig_123", approved=True)
    status = manager.get_status(tx_hash)
    print(f"After Risk approval: {status['approved']}/{status['required']}")
    print(f"Can execute: {manager.can_execute(tx_hash)}")
    
    # Strategy entity approves
    print("\n--- Strategy Entity Approves ---")
    manager.add_signature(tx_hash, EntityType.STRATEGY, "0xstrategy_sig_456", approved=True)
    status = manager.get_status(tx_hash)
    print(f"After Strategy approval: {status['approved']}/{status['required']}")
    print(f"Can execute: {manager.can_execute(tx_hash)}")
    print(f"\n✅ Transaction ready for execution!")
