"""
Citadel - Key Derivation (BIP44)
Hierarchical deterministic wallet key generation

Follows BIP44: m/44'/60'/0'/0/index
- 44': Purpose (HD wallets)
- 60': Coin type (Ethereum/EVM)
- 0': Account (first account)
- 0': Change (external addresses)
- index: Wallet index (0, 1, 2, ...)
"""

from mnemonic import Mnemonic
from eth_account import Account
from eth_keys import keys
from typing import Tuple, Dict

# Enable HDwallet features
Account.enable_unaudited_hdwallet_features()


class BIP44Derivation:
    """Hierarchical key derivation following BIP44 standard."""
    
    COIN_TYPE = 60  # Ethereum
    ACCOUNT = 0
    CHANGE = 0
    
    # Wallet tier definitions
    TIERS = {
        "master": 0,          # m/44'/60'/0'/0/0
        "signing": 255,       # m/44'/60'/0'/0/255
        "user": (1, 254),     # m/44'/60'/0'/0/1 to 254
    }
    
    @staticmethod
    def derive_private_key(seed_phrase: str, derivation_index: int) -> Tuple[str, str]:
        """
        Derive private key and address from seed phrase using BIP44.
        
        Args:
            seed_phrase: 24-word BIP39 mnemonic
            derivation_index: Wallet index (0=master, 1-254=users, 255=signing)
        
        Returns:
            Tuple[private_key_hex, address]
        
        Example:
            private_key, address = derive_private_key(seed_phrase, 1)
            # Returns: ("0xabc...", "0x123...")
        """
        # Create mnemonic object
        mnemonic = Mnemonic("english")
        
        # Generate seed from mnemonic
        seed_bytes = mnemonic.to_seed(seed_phrase)
        
        # Create account from seed with BIP44 path
        path = f"m/44'/60'/0'/0/{derivation_index}"
        account = Account.from_mnemonic(seed_phrase, account_path=path)
        
        private_key = account.key.hex()  # Returns with "0x" prefix
        address = account.address
        
        return private_key, address
    
    @staticmethod
    def get_path(derivation_index: int) -> str:
        """Get BIP44 derivation path for index."""
        return f"m/44'/60'/0'/0/{derivation_index}"
    
    @staticmethod
    def classify_wallet(derivation_index: int) -> str:
        """
        Classify wallet tier based on derivation index.
        
        Returns: "master", "signing", or "user"
        """
        if derivation_index == BIP44Derivation.TIERS["master"]:
            return "master"
        elif derivation_index == BIP44Derivation.TIERS["signing"]:
            return "signing"
        elif BIP44Derivation.TIERS["user"][0] <= derivation_index <= BIP44Derivation.TIERS["user"][1]:
            return "user"
        else:
            raise ValueError(f"Invalid derivation index: {derivation_index}")


class WalletKeyManager:
    """Manages wallet keys and their security properties."""
    
    def __init__(self, master_seed: str):
        """
        Initialize with master seed (24-word mnemonic).
        
        Args:
            master_seed: "word1 word2 ... word24"
        
        Security: In production, load from HSM/secure vault, never store plaintext
        """
        self.master_seed = master_seed
        self._validate_seed()
    
    def _validate_seed(self):
        """Validate that seed is valid BIP39 mnemonic."""
        mnemonic = Mnemonic("english")
        if not mnemonic.check(self.master_seed):
            raise ValueError("Invalid BIP39 mnemonic seed phrase")
    
    def derive_wallet(self, index: int, chain: str = "bsc") -> Dict:
        """
        Derive a wallet at the given index.
        
        Args:
            index: Derivation index (0=master, 1-254=users, 255=signing)
            chain: Blockchain chain ("bsc" or "polygon")
        
        Returns:
            {
                "address": "0x123...",
                "private_key": "0xabc...",
                "derivation_path": "m/44'/60'/0'/0/1",
                "tier": "user",
                "chain": "bsc",
                "signing_policy": "single-sig"
            }
        """
        private_key, address = BIP44Derivation.derive_private_key(self.master_seed, index)
        tier = BIP44Derivation.classify_wallet(index)
        path = BIP44Derivation.get_path(index)
        
        # Determine signing policy based on tier
        signing_policy = self._get_signing_policy(tier)
        
        return {
            "address": address,
            "private_key": private_key,
            "derivation_path": path,
            "derivation_index": index,
            "tier": tier,
            "chain": chain,
            "signing_policy": signing_policy,
        }
    
    def _get_signing_policy(self, tier: str) -> str:
        """Get signing policy for wallet tier."""
        policies = {
            "user": "single-sig",         # User only
            "master": "multi-sig-2-of-3", # Risk + Strategy + Execution
            "signing": "multi-sig-3-of-3", # All 3 entities required
        }
        return policies.get(tier, "unknown")
    
    def derive_next_user_wallet(self, last_index: int = 0, chain: str = "bsc") -> Dict:
        """
        Derive the next available user wallet.
        
        Args:
            last_index: Index of last created wallet (to find next)
            chain: Blockchain chain
        
        Returns: Wallet dictionary
        
        Example:
            # User 1 created at index 1
            # User 2 should be at index 2
            wallet = manager.derive_next_user_wallet(last_index=1)
        """
        next_index = last_index + 1
        
        if next_index < BIP44Derivation.TIERS["user"][0]:
            next_index = BIP44Derivation.TIERS["user"][0]
        
        if next_index > BIP44Derivation.TIERS["user"][1]:
            raise ValueError(f"Maximum user wallets (254) exceeded")
        
        return self.derive_wallet(next_index, chain)
    
    def get_master_wallet(self, chain: str = "bsc") -> Dict:
        """Get master wallet (consolidation vault)."""
        return self.derive_wallet(BIP44Derivation.TIERS["master"], chain)
    
    def get_signing_wallet(self, chain: str = "bsc") -> Dict:
        """Get signing wallet (entity execution)."""
        return self.derive_wallet(BIP44Derivation.TIERS["signing"], chain)


# Example usage
if __name__ == "__main__":
    seed = "produce dice skin segment album section group lawn cup wisdom rich frequent pledge bright cage barrel demise sell sunset picnic lend post race pact"
    
    manager = WalletKeyManager(seed)
    
    # Derive master wallet
    master = manager.get_master_wallet("bsc")
    print(f"\nMaster Wallet:")
    print(f"  Address: {master['address']}")
    print(f"  Path: {master['derivation_path']}")
    print(f"  Tier: {master['tier']}")
    print(f"  Policy: {master['signing_policy']}")
    
    # Derive user wallet 1
    user1 = manager.derive_wallet(1, "bsc")
    print(f"\nUser Wallet 1:")
    print(f"  Address: {user1['address']}")
    print(f"  Path: {user1['derivation_path']}")
    print(f"  Tier: {user1['tier']}")
    print(f"  Policy: {user1['signing_policy']}")
    
    # Derive next user wallet
    user2 = manager.derive_next_user_wallet(last_index=1, chain="bsc")
    print(f"\nUser Wallet 2 (next):")
    print(f"  Address: {user2['address']}")
    print(f"  Path: {user2['derivation_path']}")
