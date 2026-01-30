from typing import List
from app.entities.base import BaseEntity
from app.schemas.hearing import HearingRecord, RiskOutput, RiskRule

class RiskEntity(BaseEntity):
    def process(self, record: HearingRecord) -> HearingRecord:
        verdict = "APPROVE"
        blockers = []
        rules_checked = []
        
        # 1. Extract the amount perception saw
        perceived_amount = 0.0
        for fact in record.perception.facts:
            if fact.key == "detected_amount":
                perceived_amount = float(fact.value)
        
        # Rule 1: The "Whale" Cap
        # Hard limit: No transactions over 1000 units without manual override
        MAX_AMOUNT = 1000.0
        passed_cap = perceived_amount <= MAX_AMOUNT
        
        rules_checked.append(RiskRule(
            rule_id="RISK-001-MAX-CAP",
            passed=passed_cap,
            reason=f"Amount {perceived_amount} <= {MAX_AMOUNT}",
            severity="CRITICAL"
        ))
        
        if not passed_cap:
            verdict = "VETO"
            blockers.append("Transaction amount exceeds global safety cap of 1000.")
            
        record.risk = RiskOutput(
            verdict=verdict,
            rules_checked=rules_checked,
            blockers=blockers
        )
        return record
