from typing import Optional
from app.schemas.hearing import HearingRecord
from app.entities.perception import PerceptionEntity
from app.entities.memory import MemoryEntity
from app.entities.risk import RiskEntity
from app.entities.strategy import StrategyEntity
from app.entities.execution import ExecutionEntity

class Arena:
    """
    The Orchestrator. 
    It ensures the pipeline runs in exactly one direction:
    Perception -> Memory -> Risk -> Strategy -> Execution.
    """
    
    def __init__(self):
        # In a real DI system, these would be injected
        self.perception = PerceptionEntity()
        self.memory = MemoryEntity()
        self.risk = RiskEntity()
        self.strategy = StrategyEntity()
        self.execution = ExecutionEntity()

    def conduct_hearing(self, user_id: str, intent: str, execute: bool = False) -> HearingRecord:
        """
        Runs the full cross-examination pipeline.
        
        Args:
            execute: If False, stops after Strategy (Dry Run). If True, allows Execution.
        """
        # 1. Initialize the Record
        record = HearingRecord(user_id=user_id, intent=intent, perception=None) # type: ignore (perception init later)
        
        try:
            # 2. Perception (The Eyes) -> Must always run
            record = self.perception.process(record)
            if record.perception.status == "OBSTRUCTED":
                return self._finalize(record, "BLOCKED", "Perception failed to verify reality.")

            # 3. Memory (The Context)
            record = self.memory.process(record)

            # 4. Risk (The Veto)
            record = self.risk.process(record)
            if record.risk.verdict == "VETO":
                return self._finalize(record, "BLOCKED", f"Risk Veto: {record.risk.blockers}")

            # 5. Strategy (The Plan)
            record = self.strategy.process(record)
            if not record.strategy.feasible_options:
                return self._finalize(record, "BLOCKED", "Strategy found no feasible path under Risk constraints.")

            # 6. Execution (The Hands)
            if execute:
                record = self.execution.process(record)
                if record.execution.status == "SUCCESS":
                    return self._finalize(record, "ALLOWED", "Execution successful.")
                else:
                    return self._finalize(record, "ERROR", "Execution failed on chain.")
            else:
                return self._finalize(record, "ALLOWED", "Plan approved (Dry Run).")

        except Exception as e:
            # The Arena catches all crashes to ensure a record is returned
            import traceback
            traceback.print_exc()
            return self._finalize(record, "ERROR", f"Arena Crash: {str(e)}")

    def _finalize(self, record: HearingRecord, verdict: str, reason: str) -> HearingRecord:
        record.final_verdict = verdict
        record.final_reason = reason
        return record
