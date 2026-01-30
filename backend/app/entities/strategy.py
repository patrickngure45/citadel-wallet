from app.entities.base import BaseEntity
from app.schemas.hearing import HearingRecord, StrategyOutput, StrategyPlan

class StrategyEntity(BaseEntity):
    def process(self, record: HearingRecord) -> HearingRecord:
        # If Risk Vetoed, the Arena would have stopped us.
        # So if we run, we assume we are clear to plan.
        
        # In prod: Select between Uniswap vs Sushi vs 1inch
        
        plan = StrategyPlan(
            action_type="TRANSFER",
            target_chain="ETHEREUM",
            calldata="0x0000000..." # Mock
        )
        
        record.strategy = StrategyOutput(
            feasible_options=[plan],
            selected_option_index=0,
            reasoning="Standard transfer selected based on lowest gas presumption."
        )
        return record
