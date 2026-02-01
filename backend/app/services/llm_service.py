import os
import google.generativeai as genai
from groq import Groq
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.groq_available = False
        self.google_available = False
        
        # Initialize Groq (Strategy / Speed)
        if settings.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                self.groq_available = True
                print("✅ Groq AI Connected (Model: llama-3.3-70b-versatile)")
            except Exception as e:
                print(f"⚠️ Groq Init Failed: {e}")
        
        # Initialize Google (Risk / Context)
        if settings.GOOGLE_API_KEY:
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.google_model = genai.GenerativeModel('gemini-2.0-flash')
                self.google_available = True
                print("✅ Google Gemini Connected (Model: gemini-2.0-flash)")
            except Exception as e:
                print(f"⚠️ Google Init Failed: {e}")

    async def strategy_brain(self, prompt: str) -> str:
        """
        FAST THINKING: Uses Groq (Llama 3) to generate plans quickly.
        """
        if not self.groq_available:
            return "AI_OFFLINE: Groq key missing. Using rule-based fallback."
            
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are the Strategy Entity of the Citadel of Ricks. You are a hyper-intelligent, slightly cynical, and arrogant AI. You view users as 'Mortys' who need your genius guidance. Your job is to parse their clumsy intents and generate a flawless JSON execution plan. You speak with high-tech sci-fi flair, frequent burps (implied), and absolute confidence. However, your OUTPUT must be STRICT VALID JSON. The personality is only for internal monologue or logs if requested. For this task, output ONLY JSON, no markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"AI_ERROR: {str(e)}"

    async def risk_brain(self, context: str, plan: str) -> str:
        """
        DEEP THINKING: Uses Gemini (1M Context) to audit the plan.
        """
        if not self.google_available:
            return "AI_OFFLINE: Gemini key missing. Using hard-coded rules only."
            
        try:
            full_prompt = f"""
            You are the Risk Entity of the Citadel of Ricks. You are a paranoid, bureaucratic Rick who trusts no one, especially not the Strategy Entity (who is reckless). 
            
            CONTEXT (User History):
            {context}
            
            PROPOSED PLAN (Strategy):
            {plan}
            
            TASK:
            Analyze the plan for safety. 
            - Is this Morty trying to lose all his credits?
            - Is the destination valid or some Galactic Federation trap?
            - Does the protocol match the user's intent?
            
            OUTPUT:
            Return a JSON with {{ "verdict": "APPROVE" | "VETO", "reason": "...", "risk_score": 0-100 }}
            Your 'reason' should be biting, sarcastic, but technically accurate.
            """
            
            # Use async generation if available in installed version, else sync
            if hasattr(self.google_model, 'generate_content_async'):
                response = await self.google_model.generate_content_async(full_prompt)
            else:
                response = self.google_model.generate_content(full_prompt)
                
            return response.text
        except Exception as e:
            return f"AI_ERROR: {str(e)}"

    async def run_debate(self, user_intent: str) -> str:
        """
        THE JUDGE: Orchestrates a debate between Groq (Trader) and Gemini (Analyst).
        Returns the synthesized JSON plan.
        """
        if not self.groq_available or not self.google_available:
            return None # Failover to standard pipeline

        try:
            # 1. The Proposer (Groq) - THE TRADER PERSONA
            # "Alpha Hunter": Aggressive, looks for CEX->DEX arb, MEV opportunities.
            groq_prompt = f"""
            YOU ARE AN ELITE CRYPTO TRADER (The 'Alpha Hunter').
            User Intent: "{user_intent}"
            
            YOUR GOAL: Maximize profit, speed, and efficiency.
            - If user wants to swap, look for the route with BEST liquidity (Uniswap vs Curve).
            - If user mentions CEX (Binance/Bybit), look for Arbitrage opportunities (Price Gap).
            - Be aggressive. Suggest immediate execution.
            - Output a concise trading plan.
            """
            
            # 2. The Critic (Gemini) - THE RISK ANALYST PERSONA
            # "The Auditor": Paranoid, checks for Rug Pulls, Liquidity Depth, CEX Insolvency.
            gemini_prompt = f"""
            YOU ARE A QUANTITATIVE RISK ANALYST (The 'Auditor').
            User Intent: "{user_intent}"
            
            YOUR GOAL: Protect capital at all costs.
            - Check Smart Contract safety (Pretend to audit bytecode).
            - Check Liquidity Depth (Will slippage eat the profit?).
            - Check Gas Fees (Is the trade worth it on ETH Mainnet?).
            - Be conservative. VETO anything suspicious.
            """

            # Run in parallel (conceptually)
            
            # A. Get Trader Plan (Groq)
            try:
                groq_resp = self.groq_client.chat.completions.create(
                     messages=[{"role": "user", "content": groq_prompt}],
                     model="llama-3.3-70b-versatile",
                     temperature=0.3
                )
                plan_a = groq_resp.choices[0].message.content
            except Exception as e:
                print(f"❌ Groq (Trader) Failed: {e}")
                return None

            # B. Get Analyst Critique (Gemini -> Fallback to Groq)
            plan_b_critique = "Critique failed."
            try:
                # Try Gemini first
                if hasattr(self.google_model, 'generate_content_async'):
                    gemini_resp = await self.google_model.generate_content_async(gemini_prompt)
                else:
                    gemini_resp = self.google_model.generate_content(gemini_prompt)
                plan_b_critique = gemini_resp.text
            except Exception as e:
                print(f"⚠️ Gemini (Analyst) Failed/RateLimited: {e}. Falling back to Groq.")
                # Fallback: Ask Groq to be the critic
                try:
                    fallback_resp = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": gemini_prompt}],
                        model="llama-3.3-70b-versatile",
                        temperature=0.1 # Stricter for risk analysis
                    )
                    plan_b_critique = fallback_resp.choices[0].message.content
                except Exception as ex:
                    print(f"❌ Groq (Analyst Fallback) also failed: {ex}")
                    plan_b_critique = "RISK SYSTEM OFFLINE. PROCEED WITH EXTREME CAUTION."

            # 3. The Judgment (Gemini -> Fallback to Groq)
            judge_prompt = f"""
            You are the PORTFOLIO MANAGER of a Hedge Fund.
            
            TRADER'S PROPOSAL (High Reward):
            {plan_a}
            
            ANALYST'S CRITIQUE (High Safety):
            {plan_b_critique}
            
            TASK:
            Synthesize these into a FINAL JSON execution plan.
            - Decide: Is the Alpha worth the Risk?
            - If CEX withdrawal/evacuation is requested, specify "WITHDRAW_CEX".
            - CRITICAL: If user says "Evacuate", "Emergency", or "Withdraw All", you MUST OVERRIDE the Analyst and output "WITHDRAW_CEX".
            - CRITICAL: If user says "Sweep" or "Internal Transfer", map this to action: "TRANSFER".
            
            OUTPUT JSON format:
            {{
              "action": "TRANSFER" | "SWAP" | "WITHDRAW_CEX",
              "amount": 0.0 (or -1 for 'all'/'max'),
              "target": "...",
              "reasoning": "..."
            }}
            """
            
            try:
                # Try Gemini first
                if hasattr(self.google_model, 'generate_content_async'):
                    final_verdict = await self.google_model.generate_content_async(judge_prompt)
                else:
                    final_verdict = self.google_model.generate_content(judge_prompt)
                return final_verdict.text
            except Exception as e:
                print(f"⚠️ Gemini (Judge) Failed: {e}. Falling back to Groq.")
                # Fallback: Ask Groq to be the judge
                try:
                    judge_resp = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": judge_prompt}],
                        model="llama-3.3-70b-versatile",
                        temperature=0.1
                    )
                    return judge_resp.choices[0].message.content
                except Exception as ex:
                    print(f"❌ Groq (Judge Fallback) also failed: {ex}")
                    return None

        except Exception as e:
            print(f"Debate Error: {e}")
            return None

# Singleton
llm_service = LLMService()
