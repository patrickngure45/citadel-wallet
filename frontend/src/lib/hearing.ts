// Matching backend/app/schemas/hearing.py

export interface PerceptionFact {
  source: string;
  timestamp: string;
  key: string;
  value: any;
  confidence: number;
}

export interface PerceptionOutput {
  facts: PerceptionFact[];
  contradictions: string[];
  status: "CLEAR" | "OBSTRUCTED";
}

export interface RiskRule {
  rule_id: string;
  passed: boolean;
  reason: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
}

export interface RiskOutput {
  verdict: "APPROVE" | "VETO";
  rules_checked: RiskRule[];
  blockers: string[];
}

export interface StrategyPlan {
  action_type: string;
  target_chain: string;
  calldata?: string;
  steps: string[];
}

export interface StrategyOutput {
  feasible_options: StrategyPlan[];
  selected_option_index: number;
  reasoning: string;
}

export interface ExecutionResult {
  tx_hash?: string;
  broadcast_time?: string;
  status: "SUCCESS" | "FAILED" | "PENDING";
  logs: string[];
}

export interface HearingRecord {
  id: string;
  started_at: string;
  user_id: string;
  intent: string;
  
  perception: PerceptionOutput;
  memory?: any; // Simplified for MVP
  risk?: RiskOutput;
  strategy?: StrategyOutput;
  execution?: ExecutionResult;
  
  final_verdict: "ALLOWED" | "BLOCKED" | "ERROR";
  final_reason: string;
}
