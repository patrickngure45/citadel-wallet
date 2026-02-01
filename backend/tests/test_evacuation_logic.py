import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from app.entities.perception import PerceptionEntity
from app.entities.strategy import StrategyEntity
from app.entities.execution import ExecutionEntity
from app.entities.memory import MemoryEntity
from app.schemas.hearing import HearingRecord, PerceptionOutput, MemoryOutput
from app.services.cex_service import CexService

# Mock Config
MOCK_CEX_CONFIG = {
    "binance": {
        "api_key": "mock_key",
        "api_secret": "mock_secret"
    }
}

async def run_test():
    print("--- 🧪 Testing CEX Evacuation Pipeline ---")
    
    # 1. Setup Record
    record = HearingRecord(
        id="test-1",
        user_id="00000000-0000-0000-0000-000000000000", # Mock UUID
        intent="Evacuate 500 ETH from Binance",
        hearing_room_id="room-1"
    )
    
    # 2. Memory (Mock DB fetch)
    # We patch MemoryEntity to inject our mock config
    print("Step 1: Memory")
    with patch("app.entities.memory.AsyncSessionLocal"): 
        # We short-circuit the DB logic by just manually setting memory
        record.memory = MemoryOutput(
            known_user=True,
            derivation_index=1,
            cex_config=MOCK_CEX_CONFIG
        )

    # 3. Perception
    print("Step 2: Perception")
    # We mock the CexService call inside Perception
    with patch("app.entities.perception.CexService") as MockCex:
        instance = MockCex.return_value
        instance.get_market_price = AsyncMock(return_value=2000.0)
        
        perception_entity = PerceptionEntity()
        record = await perception_entity.process(record)
        
    print(f"Perception Facts: {[f.key for f in record.perception.facts]}")
    assert any(f.key == "cex_price_ETH" for f in record.perception.facts)
    assert any(f.key == "detected_amount" and f.value == 500.0 for f in record.perception.facts)

    # 4. Strategy
    print("Step 3: Strategy")
    # We mock LLM debate to force a WITHDRAW_CEX decision
    mock_plan_json = """
    {
        "action": "WITHDRAW_CEX",
        "amount": 500,
        "target": "ETHEREUM",
        "reasoning": "Evacuation triggered by user."
    }
    """
    with patch("app.services.llm_service.llm_service.run_debate", new_callable=AsyncMock) as mock_debate:
        mock_debate.return_value = mock_plan_json
        
        strategy_entity = StrategyEntity()
        record = await strategy_entity.process(record)
        
    print(f"Strategy Selected: {record.strategy.feasible_options[0].action_type}")
    assert record.strategy.feasible_options[0].action_type == "WITHDRAW_CEX"

    # 5. Execution
    print("Step 4: Execution")
    # We mock WalletService to return a dummy address
    # We mock CexService to track the withdraw call
    with patch("app.entities.execution.wallet_service") as mock_wallet_service, \
         patch("app.entities.execution.CexService") as MockCexExec:
         
        mock_wallet_service.generate_evm_address.return_value = {"address": "0xUserWallet"}
        
        cex_instance = MockCexExec.return_value
        cex_instance.withdraw_to_chain = AsyncMock(return_value="0xTXHASH123")
        
        execution_entity = ExecutionEntity()
        record = await execution_entity.process(record)
        
        # Verify CexService was called with correct params
        cex_instance.withdraw_to_chain.assert_called_once()
        call_args = cex_instance.withdraw_to_chain.call_args[1]
        assert call_args['amount'] == 500.0
        assert call_args['exchange_id'] == "binance"
        assert call_args['address'] == "0xUserWallet"
        
        print(f"Execution Status: {record.execution.status}")
        print(f"Execution Logs: {record.execution.logs}")

    print("--- ✅ Test Passed: Full Evacuation Logic Verified ---")

if __name__ == "__main__":
    asyncio.run(run_test())
