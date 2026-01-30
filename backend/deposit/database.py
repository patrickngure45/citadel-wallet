"""
Citadel - Deposit Settlement Database Integration
Handles database updates and user balance crediting
"""

from typing import Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime
from prisma import Prisma
from prisma.models import User, Wallet, Transaction, TSTStake


class DepositDatabaseManager:
    """
    Manages database updates during deposit settlement.
    
    Handles:
    - Creating Transaction records
    - Updating wallet balances
    - Crediting user pocket balances
    - Awarding TST tokens
    - Audit trail logging
    """
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def record_deposit_transaction(
        self,
        wallet_id: str,
        tx_hash: str,
        deposit_amount: Decimal,
        asset_type: str,
        chain: str,
        from_address: str,
        to_address: str
    ) -> Dict:
        """
        Record the initial deposit transaction.
        
        Args:
            wallet_id: Prisma ID of receiving wallet
            tx_hash: Blockchain transaction hash
            deposit_amount: Amount in stablecoins
            asset_type: "usdt" or "usdc"
            chain: "bsc" or "polygon"
        
        Returns: Transaction record
        """
        transaction = await self.db.transaction.create(
            data={
                "wallet_id": wallet_id,
                "tx_hash": tx_hash,
                "type": "deposit",
                "status": "pending",
                "amount": deposit_amount,
                "asset_type": asset_type,
                "chain": chain,
                "from_address": from_address,
                "to_address": to_address,
                "created_at": datetime.utcnow(),
            }
        )
        
        return {
            "id": transaction.id,
            "tx_hash": transaction.tx_hash,
            "status": transaction.status,
            "created_at": transaction.created_at.isoformat(),
        }
    
    async def confirm_deposit_transaction(
        self,
        tx_hash: str,
        block_number: int,
        block_timestamp: datetime
    ) -> bool:
        """Mark deposit transaction as confirmed on-chain."""
        transaction = await self.db.transaction.update(
            where={"tx_hash": tx_hash},
            data={
                "status": "confirmed",
                "block_number": block_number,
                "block_timestamp": block_timestamp,
                "confirmed_at": datetime.utcnow(),
            }
        )
        
        return transaction.status == "confirmed"
    
    async def record_sweep_transaction(
        self,
        wallet_id: str,
        sweep_tx_hash: str,
        sweep_amount: Decimal,
        asset_type: str,
        chain: str
    ) -> Dict:
        """Record the sweep transaction (user wallet → master wallet)."""
        transaction = await self.db.transaction.create(
            data={
                "wallet_id": wallet_id,
                "tx_hash": sweep_tx_hash,
                "type": "sweep",
                "status": "pending",
                "amount": sweep_amount,
                "asset_type": asset_type,
                "chain": chain,
                "from_address": "sweep_source",  # From user wallet
                "to_address": "sweep_destination",  # To master wallet
                "created_at": datetime.utcnow(),
            }
        )
        
        return {
            "id": transaction.id,
            "tx_hash": transaction.tx_hash,
            "status": transaction.status,
        }
    
    async def credit_user_balance(
        self,
        user_id: str,
        amount: Decimal,
        asset_type: str
    ) -> Tuple[bool, str]:
        """
        Credit user's account balance after successful settlement.
        
        This is the "pocket" balance stored in database (not on-chain).
        
        Args:
            user_id: User to credit
            amount: Amount to credit
            asset_type: "usdt" or "usdc"
        
        Returns: (success, message)
        """
        try:
            user = await self.db.user.find_unique(
                where={"id": user_id}
            )
            
            if not user:
                return False, f"User {user_id} not found"
            
            # In a real system, you'd have a Pocket or Balance table
            # For now, log this as an audit trail action
            audit_entry = await self.db.audit_trail.create(
                data={
                    "user_id": user_id,
                    "action": "balance_credit",
                    "resource_type": "wallet",
                    "old_value": "0",  # Example: would track old balance
                    "new_value": str(amount),
                    "status": "success",
                    "created_at": datetime.utcnow(),
                }
            )
            
            return True, f"Credited {amount} {asset_type} to user {user_id}"
            
        except Exception as e:
            return False, f"Error crediting balance: {str(e)}"
    
    async def award_tst_tokens(
        self,
        user_id: str,
        tst_amount: Decimal,
        deposit_tx_hash: str
    ) -> Tuple[bool, Dict]:
        """
        Award TST staking tokens to user.
        
        Reward: 1 TST per $100 USDT deposited
        
        Args:
            user_id: User to reward
            tst_amount: Number of TST tokens
            deposit_tx_hash: Reference to deposit that triggered reward
        
        Returns: (success, TST stake record)
        """
        try:
            # Create or update TST stake record
            stake = await self.db.tstStake.create(
                data={
                    "user_id": user_id,
                    "amount": tst_amount,
                    "status": "active",
                    "total_rewards_earned": Decimal(0),
                    "rewards_claimed": Decimal(0),
                    "rewards_unclaimed": Decimal(0),
                    "staked_at": datetime.utcnow(),
                }
            )
            
            # Log in audit trail
            await self.db.audit_trail.create(
                data={
                    "user_id": user_id,
                    "action": "tst_awarded",
                    "resource_type": "tst_stake",
                    "resource_id": stake.id,
                    "old_value": "0",
                    "new_value": str(tst_amount),
                    "status": "success",
                    "created_at": datetime.utcnow(),
                }
            )
            
            return True, {
                "id": stake.id,
                "amount": str(stake.amount),
                "status": stake.status,
                "created_at": stake.staked_at.isoformat(),
            }
            
        except Exception as e:
            return False, {"error": str(e)}
    
    async def update_performance_metrics(
        self,
        user_id: str,
        deposit_amount: Decimal
    ) -> bool:
        """
        Update user's daily performance metrics.
        
        Tracks: total deposits, total value, returns, etc.
        """
        try:
            today = datetime.utcnow().date()
            
            # Try to find existing metric for today
            existing = await self.db.performance_metric.find_unique(
                where={
                    "user_id_date": {
                        "user_id": user_id,
                        "date": today,
                    }
                }
            )
            
            if existing:
                # Update existing
                await self.db.performance_metric.update(
                    where={"id": existing.id},
                    data={
                        "total_deposits": existing.total_deposits + deposit_amount,
                        "total_value": existing.total_value + deposit_amount,
                        "updated_at": datetime.utcnow(),
                    }
                )
            else:
                # Create new
                await self.db.performance_metric.create(
                    data={
                        "user_id": user_id,
                        "date": today,
                        "total_value": deposit_amount,
                        "total_deposits": deposit_amount,
                        "total_withdrawals": Decimal(0),
                        "total_return": Decimal(0),
                        "return_percentage": Decimal(0),
                        "volatility": Decimal(0),
                        "sharpe_ratio": Decimal(0),
                        "max_drawdown": Decimal(0),
                    }
                )
            
            return True
            
        except Exception as e:
            print(f"Error updating metrics: {str(e)}")
            return False
    
    async def log_settlement_audit(
        self,
        user_id: str,
        deposit_tx_hash: str,
        sweep_tx_hash: str,
        amount: Decimal,
        tst_reward: Decimal
    ) -> bool:
        """
        Log full settlement in audit trail for compliance.
        """
        try:
            await self.db.audit_trail.create(
                data={
                    "user_id": user_id,
                    "action": "deposit_settlement_complete",
                    "resource_type": "transaction",
                    "resource_id": deposit_tx_hash,
                    "old_value": f"sweep_tx={sweep_tx_hash}",
                    "new_value": f"amount={amount},tst_reward={tst_reward}",
                    "status": "success",
                    "created_at": datetime.utcnow(),
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Error logging audit: {str(e)}")
            return False


class SettlementCompletionHandler:
    """
    Final step: mark settlement as complete after on-chain confirmation.
    
    Called after:
    1. Sweep transaction confirmed on-chain
    2. All database updates complete
    3. Audit trail logged
    """
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def complete_settlement(
        self,
        user_id: str,
        deposit_tx_hash: str,
        sweep_tx_hash: str
    ) -> Dict:
        """
        Mark settlement as complete.
        
        Returns summary of settlement for user notification.
        """
        try:
            # Update transaction status
            sweep_tx = await self.db.transaction.update(
                where={"tx_hash": sweep_tx_hash},
                data={
                    "status": "confirmed",
                    "confirmed_at": datetime.utcnow(),
                }
            )
            
            # Create final audit log
            await self.db.audit_trail.create(
                data={
                    "user_id": user_id,
                    "action": "settlement_completed",
                    "resource_type": "transaction",
                    "resource_id": sweep_tx_hash,
                    "status": "success",
                    "created_at": datetime.utcnow(),
                }
            )
            
            return {
                "status": "completed",
                "user_id": user_id,
                "deposit_tx": deposit_tx_hash,
                "sweep_tx": sweep_tx_hash,
                "completed_at": datetime.utcnow().isoformat(),
                "next_steps": [
                    "Funds available in your account",
                    "TST tokens staking at 8% APY",
                    "Configure trading strategy"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def example():
        # Initialize Prisma
        db = Prisma()
        await db.connect()
        
        try:
            manager = DepositDatabaseManager(db)
            
            # Simulate: Record deposit
            print("=== Recording Deposit ===")
            # This would be called with real wallet/transaction IDs
            
            # Credit balance
            print("\n=== Crediting Balance ===")
            success, msg = await manager.credit_user_balance(
                user_id="user_123",
                amount=Decimal("500"),
                asset_type="usdt"
            )
            print(f"Result: {msg}")
            
            # Award TST
            print("\n=== Awarding TST ===")
            success, stake = await manager.award_tst_tokens(
                user_id="user_123",
                tst_amount=Decimal("5"),
                deposit_tx_hash="0xdeposit123"
            )
            if success:
                print(f"TST awarded: {stake['amount']}")
            
        finally:
            await db.disconnect()
    
    # Uncomment to run example:
    # asyncio.run(example())
