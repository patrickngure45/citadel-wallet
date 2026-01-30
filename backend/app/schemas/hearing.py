from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

# --- 1. Perception Logic ---
class PerceptionFact(BaseModel):
    source: str  # e.g., "rpc_mainnet", "user_input"
    timestamp: datetime
    key: str     # e.g., "eth_balance"
    value: Any
    confidence: float = Field(..., ge=0, le=1.0)

class PerceptionOutput(BaseModel):
    facts: List[PerceptionFact] = []
    contradictions: List[str] = []
    # If perception fails to get inconsistent data, it must flag it
    status: Literal["CLEAR", "OBSTRUCTED"]

# --- 2. Memory Logic ---
class Precedent(BaseModel):
    event_id: str
    similarity_score: float
    description: str

class MemoryOutput(BaseModel):
    known_user: bool
    relevant_precedents: List[Precedent] = []
    anomalies: List[str] = [] 

# --- 3. Risk Logic ---
class RiskRule(BaseModel):
    rule_id: str
    passed: bool
    reason: str
    severity: Literal["CRITICAL", "WARNING", "INFO"]

class RiskOutput(BaseModel):
    verdict: Literal["APPROVE", "VETO"]
    rules_checked: List[RiskRule]
    blockers: List[str] = []

# --- 4. Strategy Logic ---
class StrategyPlan(BaseModel):
    action_type: str # e.g., "TRANSFER", "SWAP"
    target_chain: str
    calldata: Optional[str] = None
    steps: List[str] = []
    
class StrategyOutput(BaseModel):
    feasible_options: List[StrategyPlan]
    selected_option_index: int
    reasoning: str

# --- 5. Execution Logic ---
class ExecutionResult(BaseModel):
    tx_hash: Optional[str]
    broadcast_time: Optional[datetime]
    status: Literal["SUCCESS", "FAILED", "PENDING"]
    logs: List[str] = []

# --- The Master Record ---
class HearingRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    
    # The Intent (Input)
    user_id: str
    intent: str
    
    # The Cross-Examination Chain
    perception: PerceptionOutput
    memory: Optional[MemoryOutput] = None
    risk: Optional[RiskOutput] = None
    strategy: Optional[StrategyOutput] = None
    execution: Optional[ExecutionResult] = None
    
    # Final Disposition
    final_verdict: Literal["ALLOWED", "BLOCKED", "ERROR"] = "BLOCKED"
    final_reason: str = "Hearing in progress"

    class Config:
        arbitrary_types_allowed = True
