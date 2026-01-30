from datetime import datetime
from app.entities.base import BaseEntity
from app.schemas.hearing import HearingRecord, PerceptionOutput, PerceptionFact

class PerceptionEntity(BaseEntity):
    def process(self, record: HearingRecord) -> HearingRecord:
        # crude parsing of intent to simulate "reading the world"
        # e.g. "send 500 USDC"
        
        facts = []
        status = "CLEAR"
        
        try:
            # Mock Fact Gathering
            facts.append(PerceptionFact(
                source="simulated_rpc",
                timestamp=datetime.utcnow(),
                key="network_status",
                value="ONLINE",
                confidence=1.0
            ))
            
            # Simple heuristic: extract numbers from intent
            # In production, this would use NLP or regex on the structured request
            import re
            numbers = re.findall(r'\d+', record.intent)
            if numbers:
                amount = float(numbers[0])
                facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_amount",
                    value=amount,
                    confidence=0.9
                ))
            else:
                # If we cant see a number, maybe we shouldn't proceed? 
                # For now let it pass but log it.
                pass
                
        except Exception:
            status = "OBSTRUCTED"
            
        record.perception = PerceptionOutput(
            facts=facts,
            contradictions=[],
            status=status
        )
        return record
