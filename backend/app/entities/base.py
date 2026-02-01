from abc import ABC, abstractmethod
from app.schemas.hearing import HearingRecord

class BaseEntity(ABC):
    """
    Abstract base class for all Entities (Perception, Memory, Risk, Strategy, Execution).
    Enforces the 'Input -> Output' discipline.
    """
    
    @abstractmethod
    async def process(self, record: HearingRecord) -> HearingRecord:
        """
        Takes the current state of the HearingRecord, appends its unique contribution,
        and returns the updated record.
        
        Entities are NOT allowed to modify the contributions of previous entities.
        """
        pass
