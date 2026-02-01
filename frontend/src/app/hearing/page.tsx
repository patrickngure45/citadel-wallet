"use client";

import { useState, Suspense } from "react";
import axios from "axios";
import { ArrowRight, ShieldAlert, CheckCircle, XCircle, BrainCircuit, Activity, Eye, Zap } from "lucide-react";
import { HearingRecord } from "@/lib/hearing";
import { useSearchParams } from "next/navigation";
import { useEffect } from "react";

const API_URL = "/api/v1";

function HearingContent() {
  const searchParams = useSearchParams();
  const [intent, setIntent] = useState("");
  const [loading, setLoading] = useState(false);
  const [record, setRecord] = useState<HearingRecord | null>(null);
  const [history, setHistory] = useState<HearingRecord[]>([]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get<HearingRecord[]>(`${API_URL}/hearing/`);
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  // Auto-refresh history every 5s to show Autopilot activity
  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const presetIntent = searchParams.get('intent');
    const presetId = searchParams.get('id');
    
    if (presetIntent) {
        setIntent(presetIntent);
    }
    
    if (presetId && history.length > 0) {
        const target = history.find(h => h.id === presetId);
        if (target) setRecord(target);
    }
    
    fetchHistory();
  }, [searchParams, history.length]); // Re-run when history loads to find the ID

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
      fetchHistory(); // Refresh sidebar
    } catch (err) {
      console.error(err);
      alert("Hearing failed to start");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0d14] text-[#e0e7ff] font-sans">
      <header className="fixed top-0 left-0 right-0 h-16 border-b border-white/5 bg-[#0b0d14]/80 backdrop-blur-md z-50 flex items-center px-6">
        <div className="flex items-center gap-2">
          <BrainCircuit className="text-indigo-500 w-6 h-6" />
          <span className="font-bold tracking-tight">Citadel Entity Plane</span>
        </div>
      </header>

      <div className="max-w-7xl mx-auto pt-24 px-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Sidebar: History */}
        <aside className="lg:col-span-1 space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold uppercase tracking-wider text-white/50">Audit Log</h3>
                <button onClick={fetchHistory} className="p-1 hover:bg-white/5 rounded"><Activity size={14}/></button>
            </div>
            <div className="space-y-2 max-h-[calc(100vh-160px)] overflow-y-auto pr-1"> 
                {history.map((h) => (
                    <div 
                        key={h.id}
                        onClick={() => setRecord(h)}
                        className={`p-3 rounded-lg border cursor-pointer hover:bg-white/5 transition-all group ${record?.id === h.id ? 'bg-white/5 border-indigo-500/50' : 'border-white/5 bg-[#151923]'}`}
                    >
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-mono opacity-50">{h.id.slice(0,6)}</span>
                            {h.intent.startsWith("AUTOPILOT") && (
                                <span className="bg-cyan-500/20 text-cyan-400 text-[10px] px-1.5 rounded border border-cyan-500/30 uppercase tracking-wider font-bold">
                                    AUTO
                                </span>
                            )}
                            <StatusBadgeTiny verdict={h.final_verdict} />
                        </div>
                        <div className="text-sm font-medium line-clamp-2 text-white/80 group-hover:text-white">
                            {h.intent}
                        </div>
                        <div className="text-[10px] text-white/30 mt-2 text-right">
                           {new Date(h.started_at).toLocaleTimeString()}
                        </div>
                    </div>
                ))}
                {history.length === 0 && <div className="text-white/20 text-xs text-center py-8">No recent activity</div>}
            </div>
        </aside>

        {/* Main Workspace */}
        <main className="lg:col-span-3 space-y-8 pb-24">
            
            {/* --- NEW CHAT INTERFACE --- */}
            <section className="bg-gradient-to-r from-indigo-900/10 via-purple-900/10 to-indigo-900/10 rounded-2xl border border-white/5 p-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-grid-white/5 mask-linear-gradient" />
                <div className="relative z-10">
                    <div className="flex flex-col gap-4">
                      <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-white">
                        Submit Intent
                      </h2>
                      <div className="relative">
                        <input
                          value={intent}
                          onChange={(e) => setIntent(e.target.value)}
                          placeholder="e.g. 'Send 500 USDC to Alice', 'Evacuate Assets', 'Check Gas'"
                          className="w-full bg-[#0b0d14] border border-white/10 rounded-xl p-6 text-xl text-white placeholder-white/20 focus:outline-none focus:border-indigo-500/50 shadow-xl transition-all font-mono"
                          onKeyDown={(e) => {
                              if (e.key === "Enter") runHearing(false);
                          }}
                        />
                        {loading && (
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-indigo-400 animate-pulse font-mono text-sm">
                                PROCESSING...
                            </div>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 justify-end">
                          <button 
                            disabled={loading || !intent}
                            onClick={() => runHearing(false)}
                            className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition flex items-center gap-2 font-medium disabled:opacity-50"
                          >
                              <Eye size={18} /> Visualize (Dry Run)
                          </button>
                          
                          <button 
                            disabled={loading || !intent}
                            onClick={() => runHearing(true)}
                            className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 transition shadow-[0_0_20px_rgba(79,70,229,0.3)] flex items-center gap-2 font-bold disabled:opacity-50"
                          >
                              <Zap size={18} /> Execute Protocol
                          </button>
                      </div>
                    </div>
                </div>
            </section>

            {/* Visualization of the Entities */}
            
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
                      <div key={i} className="flex flex-col sm:flex-row sm:justify-between text-sm bg-black/20 p-2 rounded gap-1">
                        <span className="text-white/60">{f.key}</span>
                        <span className="font-mono text-indigo-300 break-all text-left sm:text-right">{String(f.value)}</span>
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
                             <div key={i} className="space-y-2">
                                 <div className="bg-indigo-500/10 border border-indigo-500/20 p-2 rounded font-mono text-xs text-indigo-300 font-bold">
                                    Option {i+1}: {opt.action_type} via {opt.target_chain}
                                 </div>
                                 {opt.steps && opt.steps.length > 0 && (
                                     <div className="bg-black/30 rounded p-2 text-xs font-mono text-white/70 space-y-1 ml-2 border-l-2 border-indigo-500/30">
                                         {opt.steps.map((step, k) => (
                                             <div key={k}>{step}</div>
                                         ))}
                                     </div>
                                 )}
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
                        <div className="space-y-2 w-full overflow-hidden">
                            <div className="text-sm opacity-60">Transaction Broadcasted</div>
                            {record.execution.tx_hash && (
                                <div className="font-mono text-sm text-green-400 break-all whitespace-normal bg-green-900/10 p-2 rounded border border-green-500/20">
                                    {record.execution.tx_hash}
                                </div>
                            )}
                            
                            {/* Execution Logs (Always visible for transparency) */}
                            {record.execution.logs && record.execution.logs.length > 0 && (
                                <div className="mt-2">
                                    <div className="text-xs uppercase tracking-wider opacity-40 mb-1">Execution Trace</div>
                                    <div className="text-xs text-white/50 font-mono bg-black/40 p-2 rounded max-h-40 overflow-y-auto whitespace-pre-wrap">
                                        {record.execution.logs.map((log: string, i: number) => (
                                            <div key={i} className={log.includes("FAILURE") || log.includes("Error") ? "text-red-400" : ""}>
                                                &gt; {log}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                  </EntityCard>
              )}
            </div>

            <div className="bg-white/5 p-4 rounded-xl text-center overflow-hidden">
                <div className="text-sm uppercase tracking-widest opacity-50 mb-1">Final Verdict</div>
                <div className="text-xl font-bold break-words whitespace-pre-wrap">{record.final_reason}</div>
            </div>

          </section>
        )}
      </main>
      </div>
    </div>
  );
}

export default function HearingPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0b0d14] flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-indigo-500/30 border-t-indigo-500 animate-spin" />
          <div className="text-indigo-400 font-mono text-sm tracking-widest">INITIALIZING AUDIT PLANE...</div>
        </div>
      </div>
    }>
      <HearingContent />
    </Suspense>
  );
}

function StatusBadgeTiny({ verdict }: { verdict: string }) {
    if (verdict === "ALLOWED") return <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" />;
    if (verdict === "BLOCKED") return <div className="w-2 h-2 rounded-full bg-red-500" />;
    return <div className="w-2 h-2 rounded-full bg-yellow-500" />;
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
