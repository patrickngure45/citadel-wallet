from datetime import datetime
from app.entities.base import BaseEntity
from app.schemas.hearing import HearingRecord, PerceptionOutput, PerceptionFact
from app.services.cex_service import cex_service
from app.services.wallet_service import wallet_service
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select
from app.core.config import settings
import re

class PerceptionEntity(BaseEntity):
    
    async def _get_binance_keys(self, user_id: str):
        """Helper to get keys from DB or env"""
        try:
            import uuid
            u_uuid = uuid.UUID(user_id)
            async with AsyncSessionLocal() as db:
                 result = await db.execute(select(User).where(User.id == u_uuid))
                 user = result.scalars().first()
                 if user and user.cex_config:
                     b_conf = user.cex_config.get("binance", {})
                     return b_conf.get("api_key"), b_conf.get("api_secret")
        except:
            pass
        # Fallback
        return settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET

    async def process(self, record: HearingRecord) -> HearingRecord:
        # crude parsing of intent to simulate "reading the world"
        # e.g. "send 500 USDC"
        
        facts = []
        status = "CLEAR"
        
        try:
            # 0. SPECIAL: EVACUATION PROTOCOL
            # "Evacuate everything from Binance"
            is_evacuate = any(w in record.intent.upper() for w in ["EVACUATE", "WITHDRAW ALL", "EMPTY BINANCE"])
            if is_evacuate:
                facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_verb",
                    value="EVACUATE",
                    confidence=1.0
                ))
                
                # Active Recon: Check CEX Balance
                api_key, api_secret = await self._get_binance_keys(record.user_id)
                if api_key:
                    balances = await cex_service.get_user_balance("binance", api_key, api_secret)
                    for asset, amount in balances.items():
                        facts.append(PerceptionFact(
                            source="cex_rpc",
                            timestamp=datetime.utcnow(),
                            key=f"detected_cex_balance_{asset}",
                            value=amount,
                            confidence=1.0
                        ))
                else:
                    status = "OBSTRUCTED" # Can't evacuate if can't see

            # Mock Fact Gathering
            facts.append(PerceptionFact(
                source="simulated_rpc",
                timestamp=datetime.utcnow(),
                key="network_status",
                value="ONLINE",
                confidence=1.0
            ))
            
            import re
            
            # 1. Detect Amount
            # Pre-filter: Identify Agreement IDs to exclude from Amount logic (e.g. "Agreement 12345")
            exclude_values = []
            agreement_pattern = re.search(r'(?:Agreement|ID)\s*#?(\d+)', record.intent, re.IGNORECASE)
            if agreement_pattern:
                exclude_values.append(agreement_pattern.group(1))

            # Matches "500", "0.5", "1,000"
            numbers = re.findall(r'[\d\.,]+', record.intent)
            # Filter for pure numbers (rudimentary)
            valid_numbers = [n.replace(",", "") for n in numbers if n.replace(",", "").replace(".", "").isdigit()]
            
            # Remove excluded values (IDs) from potential amounts
            valid_numbers = [n for n in valid_numbers if n not in exclude_values]

            if valid_numbers:
                # Take the first valid number as amount
                amount = float(valid_numbers[0])
                facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_amount",
                    value=amount,
                    confidence=0.9
                ))

            # 2. Detect Address (EVM)
            address_match = re.search(r'0x[a-fA-F0-9]{40}', record.intent)
            if address_match:
                facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_recipient",
                    value=address_match.group(0),
                    confidence=1.0
                ))
            # 2a. Detect "Admin" or "Citadel" alias
            elif any(x in record.intent.upper() for x in ["ADMIN", "CITADEL", "TREASURY"]):
                # Hardcoded Deployer/Admin Address for the Demo
                admin_address = "0x571E52efc50055d760CEaE2446aE3B469a806279"
                facts.append(PerceptionFact(
                    source="alias_resolution",
                    timestamp=datetime.utcnow(),
                    key="detected_recipient",
                    value=admin_address,
                    confidence=0.95
                ))

            # 2d. Corporate Services (Subscription Demos)
            elif any(x in record.intent.upper() for x in ["NETFLIX", "SPOTIFY", "PRIME", "TWITTER", "X.COM"]):
                 # Route to External Wallet to simulate real payment
                 service_address = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"
                 facts.append(PerceptionFact(
                    source="alias_resolution",
                    timestamp=datetime.utcnow(),
                    key="detected_recipient",
                    value=service_address,
                    confidence=0.95
                 ))

            # 2b. Detect Alice/Bob (Demo Personas)
            elif "ALICE" in record.intent.upper():
                alice_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8" # Hardhat Account #1
                facts.append(PerceptionFact(
                    source="alias_resolution",
                    timestamp=datetime.utcnow(),
                    key="detected_recipient",
                    value=alice_address,
                    confidence=0.95
                ))
            elif "BOB" in record.intent.upper():
                bob_address = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC" # Hardhat Account #2
                facts.append(PerceptionFact(
                    source="alias_resolution",
                    timestamp=datetime.utcnow(),
                    key="detected_recipient",
                    value=bob_address,
                    confidence=0.95
                ))

            # 2c. Detect Escrow/Lock Keywords
            if any(x in record.intent.upper() for x in ["LOCK", "ESCROW"]):
                 facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_verb",
                    value="ESCROW",
                    confidence=0.9
                ))

            # 3. Detect Token / Chain
            intent_upper = record.intent.upper()
            detected_token = None
            detected_chain = "ETHEREUM" # Default
            
            # --- IMPROVED TOKEN DETECTION (Proximity to Amount) ---
            # Try to associate token with the detected amount first: "10 TST", "500 USDC"
            proximity_match = re.search(r'(\d+(?:\.\d+)?)\s*([A-Za-z]+)', record.intent)
            known_tokens = ["ETH", "BNB", "TST", "MATIC", "USDC", "USDT"]
            
            if proximity_match:
                candidate_token = proximity_match.group(2).upper()
                if candidate_token in known_tokens:
                    detected_token = candidate_token
            
            # Fallback to standard check
            if not detected_token:
                if "TST" in intent_upper: detected_token = "TST"
                elif "BNB" in intent_upper: detected_token = "BNB"
                elif "MATIC" in intent_upper: detected_token = "MATIC"
                elif "ETH" in intent_upper: detected_token = "ETH"
                elif "USDC" in intent_upper: detected_token = "USDC"
                elif "USDT" in intent_upper: detected_token = "USDT"

            # --- INTELLIGENT DEFAULTING ---
            # If the user asks to "Analyze Market" or "Scan", they likely mean the major benchmarks (ETH/BNB)
            # This triggers the price fetchers below
            scan_intent = any(w in intent_upper for w in ["SCAN", "ANALYZE", "MARKET", "OPPORTUNITIES", "ARBITRAGE"])
            if scan_intent:
                # If no specific token was mentioned, default to ETH so we have something to scan
                if not detected_token:
                    detected_token = "ETH"
                
                # Flag the intent type
                facts.append(PerceptionFact(
                    source="intent_inference",
                    timestamp=datetime.utcnow(),
                    key="detected_verb",
                    value="ANALYZE",
                    confidence=0.8
                ))

            # Chain Inference based on Token
            if detected_token == "BNB":
                detected_chain = "BSC"
            elif detected_token == "TST":
                from app.core.config import settings
                detected_chain = "BSC" if settings.NEXT_PUBLIC_USE_MAINNET else "BSC_TESTNET"
            elif detected_token == "MATIC":
                detected_chain = "POLYGON"
            elif detected_token == "ETH":
                detected_chain = "ETHEREUM"
            elif detected_token == "USDC" or detected_token == "USDT":
                 # Default to BSC Testnet for this demo environment
                 detected_chain = "BSC_TESTNET"
            
            if detected_token:
                facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_token",
                    value=detected_token,
                    confidence=0.8
                ))
            
            # 4. Detect Target Token (for Swaps)
            # Look for "for BNB", "to USDT", "swap X to Y", "buy TST"
            target_token = None
            # Regex to find "for XXX", "to XXX"
            # We want to capture the token AFTER 'for' or 'to'
            target_token_match = re.search(r'(?:to|for|buy)\s+([A-Za-z]{2,5})', record.intent, re.IGNORECASE)
            
            if target_token_match:
                candidate = target_token_match.group(1).upper()
                # Basic Noise Info Filter
                ignored_words = ["TEST", "ME", "HIM", "HER", "IT", "THEM", "MY", "WALLET", "ADDRESS", "ACCOUNT", "COIN", "TOKEN", "ADMIN", "ALICE", "BOB", "EVE"]
                if candidate not in ignored_words and candidate != detected_token:
                     target_token = candidate

            if target_token:
                 facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_target_token",
                    value=target_token,
                    confidence=0.8
                ))

            # 5. Detect Verb (Action) - For Escrow
            # Look for "LOCK", "DEPOSIT", "ESCROW" or "RELEASE", "UNLOCK"
            detected_verb = None
            if any(k in intent_upper for k in ["RELEASE", "UNLOCK", "CLAIM"]):
                detected_verb = "RELEASE"
                # Try to extract Agreement ID (Look for "Agreement #1", "ID 5", or just digits)
                import re
                match = re.search(r'(?:Agreement|ID|#)?\s*(\d+)', record.intent, re.IGNORECASE)
                if match:
                    facts.append(PerceptionFact(
                        source="intent_parser",
                        timestamp=datetime.utcnow(),
                        key="detected_agreement_id",
                        value=match.group(1),
                        confidence=0.9
                    ))
            elif any(k in intent_upper for k in ["LOCK", "ESCROW", "DEPOSIT"]):
                detected_verb = "ESCROW"

            # 5a. Detect Investment/Yield Intent
            if any(k in intent_upper for k in ["INVEST", "STAKE", "YIELD", "FARM", "EARN", "DEPOSIT AAVE", "DEPOSIT COMPOUND"]):
                detected_verb = "INVEST"
                facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_verb",
                    value="INVEST",
                    confidence=0.95
                ))

            if detected_verb:
                facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_verb",
                    value=detected_verb,
                    confidence=0.9
                ))

            # 6. Detect Description context
            context_match = re.search(r'Context:\s*(.+)', record.intent, re.IGNORECASE)
            if context_match:
                 facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_description",
                    value=context_match.group(1).strip(),
                    confidence=0.9
                ))

            # 7. Detect Frequency (Subscription Manager)
            frequency = None
            if "MONTHLY" in intent_upper or "EVERY MONTH" in intent_upper: frequency = "MONTHLY"
            elif "WEEKLY" in intent_upper or "EVERY WEEK" in intent_upper: frequency = "WEEKLY"
            elif "DAILY" in intent_upper or "EVERY DAY" in intent_upper: frequency = "DAILY"
            
            if frequency:
                facts.append(PerceptionFact(
                    source="intent_parser",
                    timestamp=datetime.utcnow(),
                    key="detected_frequency",
                    value=frequency,
                    confidence=0.9
                ))

            facts.append(PerceptionFact(
                source="intent_parser",
                timestamp=datetime.utcnow(),
                key="detected_chain",
                value=detected_chain,
                confidence=0.7
            ))

            # 4. Detect CEX Context (The "Eyes" looking at Binance)
            # PROACTIVE MODE: Always check price if Token is known, even if user didn't say "Binance"
            if detected_token and detected_token in ["ETH", "BNB", "BTC", "MATIC", "TST", "USDT", "USDC"]:
                symbol = f"{detected_token}/USDT"
                if detected_token == "TST": symbol = "ETH/USDT"
                if detected_token in ["USDT", "USDC"]: symbol = "ETH/USDT" # Stablecoin check hack for demo - actually we want USDT price? 
                # Wait, USDT/USDT is 1. We should check USDT/DAI or something to see depeg?
                # For demo simplicity:
                if detected_token == "USDT": symbol = "USDC/USDT" # Check stable curve
                if detected_token == "USDC": symbol = "USDC/USDT"

                # A. Check CEX Price
                # Uses the singleton instance now
                cex_price = await cex_service.get_market_price(symbol)
                
                facts.append(PerceptionFact(
                    source="cex_service",
                    timestamp=datetime.utcnow(),
                    key=f"cex_price_{detected_token}",
                    value=cex_price,
                    confidence=0.95
                ))
                
                # B. Check DEX Price (Alpha Hunter)
                dex_price = await wallet_service.get_onchain_price(detected_token, detected_chain)
                facts.append(PerceptionFact(
                    source="dex_oracle",
                    timestamp=datetime.utcnow(),
                    key=f"dex_price_{detected_token}",
                    value=dex_price,
                    confidence=0.90
                ))

            # 5. Cec Key Status
            if "BINANCE" in intent_upper or "BYBIT" in intent_upper or "CEX" in intent_upper:
                # Check for Keys in Settings (Mock logic from previous iteration)
                from app.core.config import settings
                # ... existing logic preserved below ...
                from app.core.config import settings
                if settings.BINANCE_API_KEY:
                     facts.append(PerceptionFact(
                        source="cex_service",
                        timestamp=datetime.utcnow(),
                        key="cex_status",
                        value="KEYS_PRESENT", 
                        confidence=1.0
                    ))
                else:
                    facts.append(PerceptionFact(
                        source="cex_service",
                        timestamp=datetime.utcnow(),
                        key="cex_status",
                        value="WAITING_FOR_KEYS", 
                        confidence=1.0
                    ))

        except Exception as e:
            print(f"Perception Error: {e}")
            status = "OBSTRUCTED"
            
        record.perception = PerceptionOutput(
            facts=facts,
            contradictions=[],
            status=status
        )
        return record
