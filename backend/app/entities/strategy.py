
from app.entities.base import BaseEntity
from app.schemas.hearing import HearingRecord, StrategyOutput, StrategyPlan
from app.services.llm_service import llm_service
from app.services.market_data_service import market_data
from app.services.wallet_service import wallet_service  # <--- Added Import
import json
import random

class StrategyEntity(BaseEntity):
    async def process(self, record: HearingRecord) -> HearingRecord:
        # If Risk Vetoed, the Arena would have stopped us.
        # So if we run, we assume we are clear to plan.

        
        # 1. Gather Facts from Perception (The Robot Eyes)
        amount = 0.0
        recipient = None
        chain = "ETHEREUM"
        token = "ETH"
        target_token = None
        verb = None
        frequency = None
        
        for f in record.perception.facts:
            if f.key == "detected_amount": amount = float(f.value)
            if f.key == "detected_recipient": recipient = f.value
            if f.key == "detected_chain": chain = f.value
            if f.key == "detected_token": token = f.value
            if f.key == "detected_target_token": target_token = f.value
            if f.key == "detected_verb": verb = f.value
            if f.key == "detected_frequency": frequency = f.value
            
        # ALPHA HUNTER: Check for Arbitrage Facts
        cex_price = 0.0
        dex_price = 0.0
        for f in record.perception.facts:
            if f.key.startswith("cex_price_"): cex_price = float(f.value)
            if f.key.startswith("dex_price_"): dex_price = float(f.value)
        
        feasible_options = []
        reasoning = "Insufficient data to form a plan."

        # 0.0 ALPHA HUNTER INTERCEPT
        # If we see a price gap > 1%, we inject an Opportunity, regardless of user intent (Proactive!)
        if cex_price > 0 and dex_price > 0:
            # Spread Calculation
            diff = cex_price - dex_price
            spread_pct = (diff / dex_price) * 100
            
            # Arbitrage Logic: 
            # If CEX > DEX => Buy on DEX, Sell on CEX
            # If DEX > CEX => Buy on CEX, Sell on DEX
            
            if abs(spread_pct) > 0.1: # 0.1% threshold for Demo (Alpha Hunter Active)
                direction = "Buy DEX -> Sell CEX" if spread_pct > 0 else "Buy CEX -> Sell DEX"
                profit_est = abs(diff) * (amount if amount > 0 else 1.0) # Estimate based on dry run amount or 1 unit
                
                print(f"🐺 ALPHA HUNTER: Discovered Arbitrage! Spread: {spread_pct:.2f}%")
                
                arb_plan = StrategyPlan(
                    action_type="ARBITRAGE_SIGNAL",
                    target_chain=chain,
                    calldata="SIGNAL_ONLY",
                    steps=[
                        f"🐺 ALPHA PREY DETECTED: {token}",
                        f"CEX Price: ${cex_price} | DEX Price: ${dex_price}",
                        f"Spread: {spread_pct:.2f}% ({direction})",
                        f"Est. Profit per Unit: ${abs(diff):.2f}",
                        "RECOMMENDATION: EXECUTE ARBITRAGE"
                    ]
                )
                feasible_options.append(arb_plan)
                
                # If the user didn't ask for anything specific (e.g. just "look at ETH"), we default to this.
                # BUT: If the user explicitly wants to SEND/TRANSFER/ESCROW, we must NOT let this block the main action.
                # We append it to options, but do NOT return early if there are other intents.
                
                # Check for active intent signals
                has_active_intent = (amount > 0 and recipient) or (verb in ["ESCROW", "RELEASE", "SWAP", "INVEST"])
                is_explicit_transfer = any(w in record.intent.upper() for w in ["SEND", "TRANSFER", "PAY", "GIVE"])
                
                if not has_active_intent and not is_explicit_transfer:
                    # Passive Mode: The Arbitrage is the main event.
                    record.strategy = StrategyOutput(
                        feasible_options=[arb_plan],
                        selected_option_index=0,
                        reasoning=f"Identified high-value arbitrage opportunity for {token}. Advising immediate action."
                    )
                    return record
                
                # Active Mode: We found an arb, but user wants to do something else.
                # We KEEP the plan in feasible_options, but we let the code flow proceed 
                # so the Transfer/Escrow plan gets generated and selected.
                print("🐺 ALPHA HUNTER: Signal found, but User Intent takes priority. Continuing strategy generation...")

        # 1.4 Special Case: Escrow / Lock
        if verb == "ESCROW" and amount > 0:
            print(f"🔒 Strategy: Detected Escrow Lock: {amount} {token}")
            
            # Generate random agreement ID (uint256 compatible)
            agreement_id = random.randint(100000, 999999999)
            
            escrow_plan = StrategyPlan(
                action_type="ESCROW_LOCK",
                target_chain="BSC_TESTNET", # Contract is on BSC Testnet
                calldata=f"ESCROW_AGREEMENT_{agreement_id}", # Store ID in calldata placeholder
                steps=[
                    f"Identified Escrow Lock detected.",
                    f"Contract: CitadelEscrow (BSC Testnet)",
                    f"generated_agreement_id: {agreement_id}",
                    f"Action: Lock {amount} {token} for {recipient or 'Admin'}"
                ]
            )
            
            record.strategy = StrategyOutput(
                feasible_options=[escrow_plan],
                selected_option_index=0,
                reasoning="Detected clear Escrow/Lock intent."
            )
            return record

        # 1.4b Special Case: Escrow Release
        if verb == "RELEASE":
            agreement_id_str = None
            for f in record.perception.facts:
                if f.key == "detected_agreement_id": agreement_id_str = f.value
            
            if agreement_id_str:
                print(f"🔓 Strategy: Detected Escrow Release for ID {agreement_id_str}")
                release_plan = StrategyPlan(
                    action_type="ESCROW_RELEASE",
                    target_chain="BSC_TESTNET",
                    calldata=agreement_id_str,
                    steps=[
                        f"Action: Release Funds for Agreement {agreement_id_str}",
                        f"Contract: CitadelEscrow (BSC Testnet)"
                    ]
                )
                record.strategy = StrategyOutput(
                    feasible_options=[release_plan],
                    selected_option_index=0,
                    reasoning=f"Detected Release intent for Agreement {agreement_id_str}"
                )
                return record
            else:
                reasoning = "Detected Release intent but no Agreement ID found (e.g. 'Release Agreement 12345')"

        # 1.5 Special Case: Citadel OTC Swap
        # If we detect a swap intent with clear parameters, we bypass the AI debate for a snappy experience (and safety)
        is_swap_intent = any(k in record.intent.lower() for k in ["swap", "trade", "exchange", "convert", "buy"])
        if is_swap_intent and amount > 0 and token and target_token:
            print(f"⚡ Strategy: Detected OTC Swap: {amount} {token} -> {target_token}")
            
            otc_plan = StrategyPlan(
                action_type="SWAP",
                target_chain=chain,
                calldata=f"OTC_SWAP_{token}_TO_{target_token}",
                steps=[
                    f"Identified OTC Swap Opportunity: {token} to {target_token}",
                    f"Quote: 1 TST = 0.01 BNB (Mock Rate)", 
                    f"Action: Swap {amount} {token} for {target_token}"
                ]
            )
            
            record.strategy = StrategyOutput(
                feasible_options=[otc_plan],
                selected_option_index=0,
                reasoning=f"Detected clear OTC Swap intent. Executing Citadel Market Maker protocol."
            )
            return record

        # 1.6 Special Case: Investment / Yield Farming
        if verb == "INVEST" and amount > 0:
            print(f"🌾 Strategy: Detected Yield Farming Intent: {amount} {token}")

            # FETCH REAL DATA
            yield_options = await market_data.get_current_yields(chain=chain, token=token)
            
            # Simple Logic: Pick the highest yield (Citadel is usually last/appended as best)
            best_option = yield_options[-1] 
            comparison_text = "\n".join([f"Found {o['protocol']}: {o['apy']} APY" for o in yield_options[:-1]])

            invest_plan = StrategyPlan(
                action_type="INVEST",
                target_chain=chain,
                calldata=f"DEPOSIT_{best_option['protocol'].upper().replace(' ', '_')}",
                steps=[
                    f"Scanning Real-Time Lending Markets for {token}...",
                    comparison_text,
                    f"Selected Best: {best_option['protocol']} ({best_option['apy']})",
                    f"Action: Deposit {amount} {token} into Citadel Vault"
                ]
            )

            record.strategy = StrategyOutput(
                feasible_options=[invest_plan],
                selected_option_index=0,
                reasoning=f"Optimized Yield Strategy: Selected {best_option['protocol']} for {best_option['apy']} APY."
            )
            return record

        # 1.7 Special Case: Subscription / Recurring Payment
        if frequency and amount > 0 and recipient:
            print(f"📅 Strategy: Detected Recurring Payment: {amount} {token} {frequency}")
            
            sub_plan = StrategyPlan(
                action_type="SUBSCRIPTION",
                target_chain=chain,
                calldata=f"CREATE_SUBSCRIPTION_{frequency}_{recipient}",
                steps=[
                    f"Configuring Autopilot for {frequency} payments...",
                    f"Recipient: {recipient}",
                    f"Amount: {amount} {token}",
                    f"Schedule: {frequency} (Next run: Immediate)",
                    "Action: Register Task in Citadel Scheduler"
                ]
            )
            
            record.strategy = StrategyOutput(
                feasible_options=[sub_plan],
                selected_option_index=0,
                reasoning=f"Detected recurring intent. Handing off to Subscription Manager ({frequency})."
            )
            return record


        # 1.8 Special Case: EMERGENCY EVACUATION (CEX -> CHAIN)
        if verb == "EVACUATE":
            print("🚨 Strategy: Creating Emergency Evacuation Plan")
            
            # Extract balances from Perception Facts
            cex_holdings = []
            for fact in record.perception.facts:
                if fact.key.startswith("detected_cex_balance_"):
                     # Fact value is already the amount (float/string)
                     asset_name = fact.key.replace("detected_cex_balance_", "")
                     cex_holdings.append({"asset": asset_name, "amount": fact.value})

            steps = ["Authenticated with Binance via CexService"]
            
            if not cex_holdings:
                 steps.append("⚠️ No CEX balances found to evacuate.")
            else:
                 # CONSOLIDATION STRATEGY: Send to the Deployer Address (The one with Gas)
                 # This centralizes all assets into the "Citadel Treasury"
                 vault_addr = "0x571E52efc50055d760CEaE2446aE3B469a806279"
                 
                 for h in cex_holdings:
                     steps.append(f"Found {h['amount']} {h['asset']} on Exchange")
                     steps.append(f"Queuing Withdrawal: {h['asset']} -> Citadel Treasury ({vault_addr[:6]}...)")

            steps.append("Executing Batch Transfer Protocol...")

            evac_plan = StrategyPlan(
                action_type="CEX_WITHDRAWAL_BATCH",
                target_chain=chain or "ethereum",
                calldata="EXECUTE_CEX_SWEEP",
                steps=steps
            )

            record.strategy = StrategyOutput(
                feasible_options=[evac_plan],
                selected_option_index=0,
                reasoning=f"Emergency Protocol Initiated. Evacuating {len(cex_holdings)} assets from Centralized Exchange."
            )
            return record


        # 2. Check for High-Complexity Intent (The Trigger)
        # We invoke the AI Committee if:
        # A) Explicit complex keywords are found
        # B) We found an amount but NO recipient (implies "do something with this money")
        keywords = ["swap", "bridge", "invest", "yield", "optimize", "best", "cheapest", "trade", "buy", "sell", "withdraw", "evacuate", "binance", "sweep"]
        is_complex = any(k in record.intent.lower() for k in keywords)
        
        if is_complex or (amount >= 0 and not recipient) or ("from" in record.intent.lower() and "to" in record.intent.lower()):
            print(f"🧠 Strategy: Convening AI Committee for intent: '{record.intent}'")
            
            # --- THE COMMITTEE SESSION ---
            # Calls Groq (Proposer) vs Gemini (Judge)
            ai_verdict_json = await llm_service.run_debate(record.intent)
            
            if ai_verdict_json:
                try:
                    # Clean json string (LLMs often wrap in markdown blocks)
                    clean_json = ai_verdict_json.replace("```json", "").replace("```", "").strip()
                    
                    # Robust JSON Extraction using raw_decode
                    # This allows parsing "{"a":1} extra text" without crashing
                    start_idx = clean_json.find("{")
                    if start_idx != -1:
                         clean_json = clean_json[start_idx:]
                         decoder = json.JSONDecoder()
                         plan_data, _ = decoder.raw_decode(clean_json)
                    else:
                        raise ValueError("No JSON object found in AI response")
                    
                    raw_action = plan_data.get("action", "AI_EXECUTION").upper()
                    action_type = raw_action
                    
                    # Handle CEX Specifcs
                    calldata = "0x_AI_PENDING_SAFETY_CHECK"
                    if "WITHDRAW" in raw_action or "CEX" in raw_action:
                        action_type = "WITHDRAW_CEX"
                        calldata = "0x_CEX_API_CALL"

                    # Construct Plan from AI
                    ai_plan = StrategyPlan(
                        action_type=action_type,
                        target_chain=plan_data.get("target", chain), 
                        calldata=calldata, # We do NOT let AI write raw bytes yet
                        steps=[
                            f"Committee Synthesis: {plan_data.get('reasoning', 'No reasoning provided')}",
                            f"Rec: {plan_data.get('action')}",
                            f"Est. Amount: {plan_data.get('amount', amount)}"
                        ]
                    )
                    
                    record.strategy = StrategyOutput(
                        feasible_options=[ai_plan],
                        selected_option_index=0,
                        reasoning=f"AI Committee Consensus: {plan_data.get('reasoning')}"
                    )
                    return record
                    
                except Exception as e:
                    print(f"⚠️ AI Strategy Parse Error: {e}. Falling back to robot logic.")
                    # Fallthrough to standard logic if AI produces garbage
        
        # 3. Formulate Plan (Standard Robot Logic)
        if amount > 0 and recipient:
            # Native Transfer Plan
            # In a real app, we would calculate gas, check balances (Memory), etc.
            
            plan = StrategyPlan(
                action_type="TRANSFER",
                target_chain=chain,
                calldata=f"transfer({recipient}, {amount} {token})",
                steps=[
                    f"Check balance on {chain}",
                    f"Construct native transfer of {amount} {token} to {recipient}",
                    "Sign and Broadcast"
                ]
            )
            feasible_options.append(plan)
            reasoning = f"Identified native transfer of {amount} {token} on {chain}."
        elif not feasible_options:
            reasoning = "Could not identify amount or recipient within intent, and AI Committee did not engage."

        # 4. Output
        # Selection Logic: Prioritize Explicit User Intent over Passive Signals
        selected_idx = 0
        if feasible_options:
            for i, plan in enumerate(feasible_options):
                # If we find a hard action (Transfer, Swap, Escrow), we prefer that over "Signal" or "Advice"
                if plan.action_type in ["TRANSFER", "SWAP", "ESCROW_LOCK", "ESCROW_RELEASE", "WITHDRAW_CEX"]:
                    selected_idx = i
                    break

        record.strategy = StrategyOutput(
            feasible_options=feasible_options,
            selected_option_index=selected_idx if feasible_options else -1,
            reasoning=reasoning
        )
        return record
