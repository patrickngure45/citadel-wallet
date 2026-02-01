
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.entities.strategy import StrategyEntity
from app.schemas.hearing import HearingRecord, PerceptionOutput, PerceptionFact

async def test_priority():
    print("🧪 Testing Strategy Priority Logic...")
    
    # 1. Setup Mock Record with BOTH Arb and Transfer facts
    facts = [
        PerceptionFact(source="mock", key="detected_amount", value=0.01, timestamp=datetime.now(), confidence=1.0),
        PerceptionFact(source="mock", key="detected_recipient", value="0x123", timestamp=datetime.now(), confidence=1.0),
        PerceptionFact(source="mock", key="detected_chain", value="ETHEREUM", timestamp=datetime.now(), confidence=1.0),
        PerceptionFact(source="mock", key="detected_token", value="ETH", timestamp=datetime.now(), confidence=1.0),
        # Arbitrage Facts
        PerceptionFact(source="mock", key="cex_price_ETH", value=3000.0, timestamp=datetime.now(), confidence=1.0),
        PerceptionFact(source="mock", key="dex_price_ETH", value=2900.0, timestamp=datetime.now(), confidence=1.0), # >1% Spread
    ]
    
    record = HearingRecord(
        user_id="test_user",
        intent="Send 0.01 ETH to 0x123",
        perception=PerceptionOutput(facts=facts, status="CLEAR")
    )
    
    entity = StrategyEntity()
    processed_record = await entity.process(record)
    
    strat = processed_record.strategy
    print(f"✅ Generated {len(strat.feasible_options)} options.")
    
    for i, opt in enumerate(strat.feasible_options):
        print(f"   [{i}] {opt.action_type}")
        
    selected = strat.feasible_options[strat.selected_option_index]
    print(f"🎯 Selected Option Index: {strat.selected_option_index}")
    print(f"🏆 Selected Action: {selected.action_type}")
    
    if selected.action_type == "TRANSFER":
        print("✅ SUCCESS: User Intent prioritized over Arbitrage.")
    else:
        print("❌ FAILURE: Wrong action selected.")

if __name__ == "__main__":
    asyncio.run(test_priority())
