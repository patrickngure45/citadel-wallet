"""
Citadel - Entity System Integration
Connects deposit system with Risk, Strategy, and Execution entities
"""

from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from decimal import Decimal
import json


class EntityType(Enum):
    """System entity types"""
    RISK = "risk"
    STRATEGY = "strategy"
    EXECUTION = "execution"
    PERCEPTION = "perception"
    MEMORY = "memory"


@dataclass
class DepositApprovalRequest:
    """Request sent to entities for approval"""
    deposit_id: str
    user_id: str
    amount: Decimal
    asset_type: str
    chain: str
    timestamp: datetime
    
    def to_json(self) -> str:
        """Serialize for Ably messaging"""
        return json.dumps({
            "deposit_id": self.deposit_id,
            "user_id": self.user_id,
            "amount": str(self.amount),
            "asset_type": self.asset_type,
            "chain": self.chain,
            "timestamp": self.timestamp.isoformat(),
        })


@dataclass
class DepositApprovalResponse:
    """Response from entity approval"""
    entity_type: EntityType
    deposit_id: str
    approved: bool
    score: float  # 0.0 to 1.0
    reasoning: str
    timestamp: datetime
    signature: Optional[str] = None  # For multi-sig sweep
    
    def to_json(self) -> str:
        return json.dumps({
            "entity_type": self.entity_type.value,
            "deposit_id": self.deposit_id,
            "approved": self.approved,
            "score": self.score,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
        })


class DepositEntityIntegration:
    """
    Connects deposit system with entity services.
    
    Flow:
    1. User deposits → Deposit created (DETECTED)
    2. Risk entity checks (3-min cycle) → Anomaly detection
    3. If Risk approves → Sweep TX created
    4. Strategy entity confirms (2-min cycle) → Strategy alignment
    5. Risk + Strategy sign (2-of-3 threshold)
    6. Execution broadcasts sweep
    """
    
    def __init__(self):
        self.pending_approvals: Dict[str, list] = {}  # deposit_id -> [responses]
        self.approval_callbacks: Dict[EntityType, Callable] = {}
        
    def register_entity_callback(
        self,
        entity_type: EntityType,
        callback: Callable[[DepositApprovalRequest], DepositApprovalResponse]
    ):
        """
        Register callback for entity response.
        
        Entity services will call these during their cycles.
        """
        self.approval_callbacks[entity_type] = callback
    
    async def request_deposit_approval(
        self,
        deposit_id: str,
        user_id: str,
        amount: Decimal,
        asset_type: str,
        chain: str,
    ) -> Dict[str, Any]:
        """
        Request entity system to approve/reject deposit.
        
        In production with Ably:
        1. Publish approval request to entity channels
        2. Entities respond via their own channels
        3. Collect responses until threshold met
        4. Return aggregated decision
        
        For now, use registered callbacks.
        
        Returns: {
            "approved": bool,
            "responses": [entity responses],
            "required_threshold": "2-of-3",
            "next_step": "awaiting_sweep_signatures"
        }
        """
        
        # Create approval request
        request = DepositApprovalRequest(
            deposit_id=deposit_id,
            user_id=user_id,
            amount=amount,
            asset_type=asset_type,
            chain=chain,
            timestamp=datetime.utcnow(),
        )
        
        # Collect responses from entities
        responses = []
        
        # Risk entity (3-min cycle, but we'll check immediately)
        if EntityType.RISK in self.approval_callbacks:
            try:
                risk_response = self.approval_callbacks[EntityType.RISK](request)
                responses.append(risk_response)
                print(f"  ✓ Risk Entity: Score {risk_response.score:.2f} - {risk_response.reasoning}")
            except Exception as e:
                print(f"  ✗ Risk Entity error: {str(e)}")
        
        # Strategy entity (2-min cycle)
        if EntityType.STRATEGY in self.approval_callbacks:
            try:
                strategy_response = self.approval_callbacks[EntityType.STRATEGY](request)
                responses.append(strategy_response)
                print(f"  ✓ Strategy Entity: Score {strategy_response.score:.2f} - {strategy_response.reasoning}")
            except Exception as e:
                print(f"  ✗ Strategy Entity error: {str(e)}")
        
        # Store pending responses
        self.pending_approvals[deposit_id] = responses
        
        # Check if threshold met (2 out of 2 so far = 100%)
        approvals = sum(1 for r in responses if r.approved)
        threshold = len(responses)
        
        approved = approvals >= 2  # At least 2 entities must approve
        
        return {
            "deposit_id": deposit_id,
            "approved": approved,
            "approvals": f"{approvals}/{threshold}",
            "responses": [
                {
                    "entity": r.entity_type.value,
                    "approved": r.approved,
                    "score": r.score,
                    "reasoning": r.reasoning,
                }
                for r in responses
            ],
            "next_step": "sweep_ready_for_signatures" if approved else "rejected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def request_sweep_signatures(
        self,
        deposit_id: str,
        sweep_tx_hash: str,
        amount: Decimal,
    ) -> Dict[str, Any]:
        """
        Request entity system to sign sweep transaction.
        
        Multi-sig policy: 2-of-3 (Risk + Strategy)
        
        Execution entity will:
        1. Collect signatures
        2. Broadcast when threshold met
        3. Return confirmation
        
        Returns: {
            "tx_hash": sweep_tx_hash,
            "status": "signed_and_broadcast" | "awaiting_signatures",
            "signatures": 1-3,
            "confirmed_on_chain": bool
        }
        """
        
        return {
            "tx_hash": sweep_tx_hash,
            "status": "awaiting_signatures",
            "signatures": 0,
            "required": 2,
            "signers": ["risk_entity", "strategy_entity"],
            "next_step": "entities_will_collect_and_broadcast",
            "timestamp": datetime.utcnow().isoformat(),
        }


# ==================== Example Entity Implementations ====================

class RiskEntityMock:
    """Mock Risk entity for testing"""
    
    def __init__(self):
        self.name = "Risk Entity"
    
    def evaluate_deposit(self, request: DepositApprovalRequest) -> DepositApprovalResponse:
        """
        Analyze deposit for anomalies.
        
        Risk Service runs every 3 minutes:
        1. Check anomaly detection model
        2. Verify against user history
        3. Check suspicious pattern library
        4. Return approval + anomaly score
        """
        
        # Simplified: all deposits < $10K pass
        anomaly_score = Decimal(str(request.amount)) / Decimal("100000")  # Normalized
        approved = float(anomaly_score) < 0.95
        
        return DepositApprovalResponse(
            entity_type=EntityType.RISK,
            deposit_id=request.deposit_id,
            approved=approved,
            score=float(anomaly_score),
            reasoning=f"Anomaly score: {float(anomaly_score):.2f}. User deposit pattern normal.",
            timestamp=datetime.utcnow(),
        )


class StrategyEntityMock:
    """Mock Strategy entity for testing"""
    
    def __init__(self):
        self.name = "Strategy Entity"
    
    def evaluate_deposit(self, request: DepositApprovalRequest) -> DepositApprovalResponse:
        """
        Analyze deposit alignment with strategy.
        
        Strategy Service runs every 2 minutes:
        1. Check portfolio allocation rules
        2. Verify compliance with current strategy
        3. Estimate impact on returns
        4. Return approval + alignment score
        """
        
        # Simplified: all deposits approved (92% alignment)
        alignment_score = Decimal("0.92")
        
        return DepositApprovalResponse(
            entity_type=EntityType.STRATEGY,
            deposit_id=request.deposit_id,
            approved=True,
            score=float(alignment_score),
            reasoning="Deposit aligns with current strategy allocation targets.",
            timestamp=datetime.utcnow(),
        )


# ==================== Example Usage ====================

if __name__ == "__main__":
    import asyncio
    
    async def demo():
        print("=== ENTITY INTEGRATION DEMO ===\n")
        
        # Initialize integration
        integration = DepositEntityIntegration()
        
        # Register mock entities
        risk_entity = RiskEntityMock()
        strategy_entity = StrategyEntityMock()
        
        integration.register_entity_callback(
            EntityType.RISK,
            risk_entity.evaluate_deposit
        )
        integration.register_entity_callback(
            EntityType.STRATEGY,
            strategy_entity.evaluate_deposit
        )
        
        # Test deposit approval flow
        print("1. REQUEST ENTITY APPROVAL\n")
        print("   Deposit ID: deposit_0x123")
        print("   Amount: $500 USDT")
        print("   User: user_demo_001\n")
        
        result = await integration.request_deposit_approval(
            deposit_id="deposit_0x123",
            user_id="user_demo_001",
            amount=Decimal("500"),
            asset_type="usdt",
            chain="bsc",
        )
        
        print(f"   Status: {result['approved']}")
        print(f"   Approvals: {result['approvals']}\n")
        
        for response in result["responses"]:
            print(f"   {response['entity'].upper()}: {response['score']:.2f} - {response['reasoning']}")
        
        # Next step
        print(f"\n2. {result['next_step'].upper()}\n")
        
        if result['approved']:
            print("   ✓ Ready for sweep signatures (2-of-3 multi-sig)")
            print("   Entities: Risk, Strategy")
            print("   Pending: Execution entity to collect and broadcast")
        else:
            print("   ✗ Deposit rejected - no settlement")
        
        print("\n=== DEMO COMPLETE ===")
    
    asyncio.run(demo())
