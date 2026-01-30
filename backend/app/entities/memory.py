from app.entities.base import BaseEntity
from app.schemas.hearing import HearingRecord, MemoryOutput

class MemoryEntity(BaseEntity):
    def process(self, record: HearingRecord) -> HearingRecord:
        # In prod: Check DB for user's last 5 txs.
        
        record.memory = MemoryOutput(
            known_user=True,
            relevant_precedents=[],
            anomalies=[]
        )
        return record
