"""
Citadel - Wallet Manager
Handles wallet lifecycle: creation, rotation, recovery
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from .derivation import WalletKeyManager


class WalletStatus(Enum):
    """Wallet lifecycle status."""
    ACTIVE = "active"
    ROTATING = "rotating"
    ROTATED = "rotated"
    COMPROMISED = "compromised"
    RECOVERED = "recovered"


class WalletManager:
    """
    Professional wallet lifecycle management.
    
    Handles:
    - Wallet creation (derivation from seed)
    - Status tracking (active, rotating, rotated)
    - Key rotation (periodic or anomaly-triggered)
    - Recovery (compromise or loss)
    """
    
    # Rotation policy: every 90 days
    ROTATION_INTERVAL_DAYS = 90
    
    # Grace period: old address still works for N days after rotation
    GRACE_PERIOD_DAYS = 30
    
    def __init__(self, key_manager: WalletKeyManager):
        """Initialize with key manager."""
        self.key_manager = key_manager
        self.wallet_history: Dict[str, list] = {}  # Track wallet versions per user
    
    def create_user_wallet(self, user_id: str, chain: str = "bsc") -> Dict:
        """
        Create new wallet for user (first time signup).
        
        Args:
            user_id: Unique user identifier
            chain: "bsc" or "polygon"
        
        Returns: Wallet object
        """
        # Find next available index
        next_index = self._get_next_user_index()
        
        # Derive wallet
        wallet_data = self.key_manager.derive_wallet(next_index, chain)
        
        # Create wallet object
        wallet = {
            "user_id": user_id,
            "address": wallet_data["address"],
            "derivation_index": next_index,
            "derivation_path": wallet_data["derivation_path"],
            "tier": "user",
            "chain": chain,
            "status": WalletStatus.ACTIVE.value,
            "created_at": datetime.utcnow().isoformat(),
            "rotated_at": None,
            "previous_address": None,
            "private_key_hash": self._hash_key(wallet_data["private_key"]),  # Never store plaintext
        }
        
        # Track in history
        if user_id not in self.wallet_history:
            self.wallet_history[user_id] = []
        self.wallet_history[user_id].append(wallet)
        
        return wallet
    
    def rotate_wallet(self, user_id: str, reason: str = "periodic", chain: str = "bsc") -> Tuple[Dict, Dict]:
        """
        Rotate user's wallet (create new, retire old).
        
        Args:
            user_id: User to rotate wallet for
            reason: "periodic", "anomaly", "compromise", "request"
            chain: Blockchain chain
        
        Returns: (old_wallet_status, new_wallet_data)
        """
        # Get current wallet
        current = self._get_current_wallet(user_id)
        if not current:
            raise ValueError(f"No current wallet for user {user_id}")
        
        # Get next available index (increment)
        next_index = current["derivation_index"] + 1000  # Large gap for new version
        
        # Derive new wallet
        new_wallet_data = self.key_manager.derive_wallet(next_index, chain)
        
        # Mark old wallet as rotating
        current_copy = current.copy()
        current_copy["status"] = WalletStatus.ROTATING.value
        current_copy["rotation_reason"] = reason
        current_copy["grace_period_until"] = (
            datetime.utcnow() + timedelta(days=self.GRACE_PERIOD_DAYS)
        ).isoformat()
        
        # Create new wallet
        new_wallet = {
            "user_id": user_id,
            "address": new_wallet_data["address"],
            "derivation_index": next_index,
            "derivation_path": new_wallet_data["derivation_path"],
            "tier": "user",
            "chain": chain,
            "status": WalletStatus.ACTIVE.value,
            "created_at": datetime.utcnow().isoformat(),
            "rotated_at": None,
            "previous_address": current["address"],
            "private_key_hash": self._hash_key(new_wallet_data["private_key"]),
        }
        
        # Update history
        self.wallet_history[user_id].append(new_wallet)
        
        return current_copy, new_wallet
    
    def mark_compromised(self, user_id: str, reason: str = "unknown") -> Dict:
        """
        Mark wallet as compromised and initiate recovery.
        
        Returns: Recovery instructions
        """
        current = self._get_current_wallet(user_id)
        if not current:
            raise ValueError(f"No current wallet for user {user_id}")
        
        # Mark as compromised
        current["status"] = WalletStatus.COMPROMISED.value
        current["compromised_at"] = datetime.utcnow().isoformat()
        current["compromise_reason"] = reason
        
        # Create recovery workflow
        recovery = {
            "type": "wallet_recovery",
            "user_id": user_id,
            "compromised_wallet": current["address"],
            "status": "pending_recovery",
            "actions": [
                "1. Risk Entity: Flag wallet as compromised",
                "2. Automatic rotation: New wallet created",
                "3. User notification: New deposit address provided",
                "4. Fund recovery: Remaining balance swept to MASTER_WALLET",
                "5. Guardian approval: If > $100k at risk"
            ],
            "initiated_at": datetime.utcnow().isoformat()
        }
        
        return recovery
    
    def should_rotate(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if wallet should be rotated (periodic policy).
        
        Returns: (should_rotate: bool, reason: str or None)
        """
        current = self._get_current_wallet(user_id)
        if not current:
            return False, None
        
        # Parse created_at
        created_at = datetime.fromisoformat(current["created_at"])
        age_days = (datetime.utcnow() - created_at).days
        
        if age_days >= self.ROTATION_INTERVAL_DAYS:
            return True, f"Periodic rotation after {age_days} days"
        
        return False, None
    
    def get_wallet_info(self, user_id: str) -> Dict:
        """Get current wallet information for user."""
        current = self._get_current_wallet(user_id)
        if not current:
            raise ValueError(f"No wallet found for user {user_id}")
        
        # Check if rotation pending
        should_rotate, reason = self.should_rotate(user_id)
        
        return {
            "address": current["address"],
            "chain": current["chain"],
            "status": current["status"],
            "derivation_path": current["derivation_path"],
            "created_at": current["created_at"],
            "rotation_pending": should_rotate,
            "rotation_reason": reason,
        }
    
    def get_wallet_history(self, user_id: str) -> list:
        """Get all wallet versions for user (for audit trail)."""
        return self.wallet_history.get(user_id, [])
    
    # Private helpers
    
    def _get_current_wallet(self, user_id: str) -> Optional[Dict]:
        """Get the currently active wallet for user."""
        wallets = self.wallet_history.get(user_id, [])
        if not wallets:
            return None
        
        # Return the most recent active wallet
        for wallet in reversed(wallets):
            if wallet["status"] in [WalletStatus.ACTIVE.value, WalletStatus.ROTATING.value]:
                return wallet
        
        return None
    
    def _get_next_user_index(self) -> int:
        """Get next available user wallet derivation index."""
        # Check all user histories to find highest index used
        max_index = 0
        for user_id, wallets in self.wallet_history.items():
            for wallet in wallets:
                if wallet["tier"] == "user":
                    idx = wallet["derivation_index"]
                    if 1 <= idx <= 254:  # Valid user range
                        max_index = max(max_index, idx)
        
        next_index = max_index + 1
        if next_index > 254:
            raise ValueError("Maximum user wallets (254) exceeded")
        
        return next_index
    
    @staticmethod
    def _hash_key(private_key: str) -> str:
        """Hash private key (never store plaintext)."""
        import hashlib
        return hashlib.sha256(private_key.encode()).hexdigest()


# Example usage
if __name__ == "__main__":
    seed = "produce dice skin segment album section group lawn cup wisdom rich frequent pledge bright cage barrel demise sell sunset picnic lend post race pact"
    
    key_manager = WalletKeyManager(seed)
    wallet_manager = WalletManager(key_manager)
    
    # User 1 signs up
    print("=== User Signup ===")
    user1_wallet = wallet_manager.create_user_wallet("user_123", "bsc")
    print(f"Created wallet: {user1_wallet['address']}")
    print(f"Path: {user1_wallet['derivation_path']}")
    
    # Get wallet info
    print("\n=== Wallet Info ===")
    info = wallet_manager.get_wallet_info("user_123")
    print(f"Status: {info['status']}")
    print(f"Rotation pending: {info['rotation_pending']}")
    
    # Rotate wallet (anomaly detected)
    print("\n=== Wallet Rotation ===")
    old_status, new_wallet = wallet_manager.rotate_wallet("user_123", reason="anomaly_detected")
    print(f"Old wallet: {old_status['address']} → {old_status['status']}")
    print(f"New wallet: {new_wallet['address']} → {new_wallet['status']}")
    print(f"Grace period: {old_status['grace_period_until']}")
    
    # Check history
    print("\n=== Wallet History ===")
    history = wallet_manager.get_wallet_history("user_123")
    for i, wallet in enumerate(history):
        print(f"  V{i+1}: {wallet['address']} ({wallet['status']})")
