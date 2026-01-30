"use client";

import { useState } from "react";
import axios from "axios";
import { ArrowRight, ShieldAlert, CheckCircle, XCircle, BrainCircuit, Activity, Eye, Zap } from "lucide-react";
import { HearingRecord } from "@/lib/hearing";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function HearingPage() {
  const [intent, setIntent] = useState("");
  const [loading, setLoading] = useState(false);
  const [record, setRecord] = useState<HearingRecord | null>(null);

  const runHearing = async (execute: boolean) => {
    if (!intent) return;
    const userId = localStorage.getItem("citadel_user_id");
    if (!userId) {
      alert("Please login first");
      return;
    }

    setLoading(true);
    setRecord(null);

    try {
      const res = await axios.post<HearingRecord>(`${API_URL}/hearing/gate`, {
        user_id: userId,
        intent: intent,
        execute: execute
      });
      setRecord(res.data);
    } catch (err) {
      console.error(err);
      alert("Hearing failed to start");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0d14] text-[#e0e7ff] p-6 font-sans">
      <header className="fixed top-0 left-0 right-0 h-16 border-b border-white/5 bg-[#0b0d14]/80 backdrop-blur-md z-50 flex items-center px-6">
        <div className="flex items-center gap-2">
          <BrainCircuit className="text-indigo-500 w-6 h-6" />
          <span className="font-bold tracking-tight">Citadel Entity Plane</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto pt-24 space-y-8">
        {/* Input Zone */}
        <section className="space-y-4">
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold">State Your Intent</h1>
            <p className="text-white/40">The bureaucracy will review your request before execution.</p>
          </div>
          
          <div className="relative">
            <textarea
              className="w-full bg-[#151923] border border-white/10 rounded-xl p-4 text-lg focus:outline-none focus:border-indigo-500 transition-colors h-32 resize-none"
              placeholder="e.g. Transfer 500 USDC to 0x123..."
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
            />
            <div className="absolute bottom-4 right-4 flex gap-2">
              <button
                onClick={() => runHearing(false)}
                disabled={loading}
                className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm font-medium transition-colors border border-white/5"
              >
                Dry Run (Test)
              </button>
              <button
                 onClick={() => runHearing(true)}
                 disabled={loading}
                 className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
              >
                {loading ? "Running..." : "Execute"} <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </section>

        {/* The Hearing Record Display */}
        {record && (
          <section className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold opacity-80">Hearing Transcript #{record.id.slice(0, 8)}</h2>
              <StatusBadge verdict={record.final_verdict} />
            </div>

            {/* Timelines / Entities */}
            <div className="grid gap-4">
                
              {/* 1. Perception */}
              <EntityCard 
                name="Perception" 
                icon={Eye} 
                status={record.perception.status === "CLEAR" ? "PASS" : "FAIL"}
              >
                <div className="space-y-2">
                   {record.perception.facts.map((f, i) => (
                      <div key={i} className="flex justify-between text-sm bg-black/20 p-2 rounded">
                        <span className="text-white/60">{f.key}</span>
                        <span className="font-mono text-indigo-300">{String(f.value)}</span>
                      </div>
                   ))}
                </div>
              </EntityCard>

              {/* 2. Risk (The Veto) */}
              {record.risk && (
                <EntityCard 
                    name="Risk" 
                    icon={ShieldAlert}
                    status={record.risk.verdict === "APPROVE" ? "PASS" : "FAIL"}
                >
                    <div className="space-y-2">
                        {record.risk.rules_checked.map((rule, i) => (
                            <div key={i} className="flex items-start gap-3 text-sm border-b border-white/5 last:border-0 pb-2 last:pb-0">
                                <div className={rule.passed ? "text-green-500" : "text-red-500"}>
                                    {rule.passed ? <CheckCircle size={16}/> : <XCircle size={16}/>}
                                </div>
                                <div>
                                    <div className="font-mono text-xs opacity-50">{rule.rule_id}</div>
                                    <div>{rule.reason}</div>
                                </div>
                            </div>
                        ))}
                         {record.risk.blockers.map((b, i) => (
                            <div key={i} className="text-red-400 text-sm font-medium">
                                VETO: {b}
                            </div>
                         ))}
                    </div>
                </EntityCard>
              )}

              {/* 3. Strategy */}
              {record.strategy && (
                <EntityCard name="Strategy" icon={BrainCircuit} status="PASS">
                    <div className="text-sm space-y-2">
                        <p className="opacity-60">{record.strategy.reasoning}</p>
                        {record.strategy.feasible_options.map((opt, i) => (
                             <div key={i} className="bg-indigo-500/10 border border-indigo-500/20 p-2 rounded font-mono text-xs text-indigo-300">
                                {opt.action_type} via {opt.target_chain}
                             </div>
                        ))}
                    </div>
                </EntityCard>
              )}

              {/* 4. Execution */}
              {record.execution && (
                  <EntityCard 
                    name="Execution" 
                    icon={Zap} 
                    status={record.execution.status === "SUCCESS" ? "PASS" : "FAIL"}
                  >
                        <div className="space-y-1">
                            <div className="text-sm opacity-60">Transaction Broadcasted</div>
                            <div className="font-mono text-sm text-green-400 break-all">
                                {record.execution.tx_hash}
                            </div>
                        </div>
                  </EntityCard>
              )}
            </div>

            <div className="bg-white/5 p-4 rounded-xl text-center">
                <div className="text-sm uppercase tracking-widest opacity-50 mb-1">Final Verdict</div>
                <div className="text-xl font-bold">{record.final_reason}</div>
            </div>

          </section>
        )}
      </main>
    </div>
  );
}

function StatusBadge({ verdict }: { verdict: string }) {
    if (verdict === "ALLOWED") return <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-bold border border-green-500/30">ALLOWED</span>;
    if (verdict === "BLOCKED") return <span className="bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-xs font-bold border border-red-500/30">BLOCKED</span>;
    return <span className="bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full text-xs font-bold border border-yellow-500/30">ERROR</span>;
}

function EntityCard({ name, icon: Icon, children, status }: any) {
    const isFail = status === "FAIL";
    return (
        <div className={`border rounded-xl p-4 transition-all ${isFail ? 'bg-red-900/10 border-red-500/30' : 'bg-[#151923] border-white/5'}`}>
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-lg ${isFail ? 'bg-red-500/20 text-red-400' : 'bg-white/5 text-indigo-400'}`}>
                        <Icon size={18} />
                    </div>
                    <span className="font-semibold">{name}</span>
                </div>
                <div className={`text-xs font-bold px-2 py-0.5 rounded ${isFail ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                    {status}
                </div>
            </div>
            <div className="pl-10">
                {children}
            </div>
        </div>
    )
}
