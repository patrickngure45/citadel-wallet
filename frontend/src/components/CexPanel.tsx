"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Building2, Save, AlertTriangle, ArrowRightCircle, RefreshCw } from "lucide-react";
import axios from "axios";
import { useRouter } from "next/navigation";

interface CexPanelProps {
  userId: string;
  hasKeys: boolean;
  onUpdate: () => void;
}

export function CexPanel({ userId, hasKeys, onUpdate }: CexPanelProps) {
  const router = useRouter();
  const [isExpanded, setIsExpanded] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [loading, setLoading] = useState(false);
  const [balances, setBalances] = useState<any[]>([]);

  // Fetch balances when connected
  useEffect(() => {
    if (hasKeys && userId) {
        axios.get(`/api/v1/users/${userId}/cex-balances`)
             .then(res => {
                 if(res.data.balances) setBalances(res.data.balances);
             })
             .catch(console.error);
    }
  }, [hasKeys, userId]);

  const handleSave = async () => {
    setLoading(true);
    try {
      const payload = {
        cex_config: {
          binance: {
            api_key: apiKey,
            api_secret: apiSecret
          }
        }
      };
      
      await axios.put(`/api/v1/users/${userId}/cex-config`, payload);
      onUpdate();
      setIsExpanded(false);
      alert("Exchange Keys Saved Securely");
    } catch (error) {
      console.error(error);
      alert("Failed to save keys");
    } finally {
      setLoading(false);
    }
  };

  const handleEvacuate = () => {
    // Navigate to Hearing Room with Preset Intent
    const encoded = encodeURIComponent("Evacuate everything from Binance immediately");
    router.push(`/hearing?intent=${encoded}`);
  };

  return (
    <div className="p-6 rounded-2xl bg-gradient-to-br from-yellow-500/10 to-amber-500/5 border border-yellow-500/20 hover:border-yellow-500/40 transition-all mb-6 relative overflow-hidden group">
      {/* Background Glow Effect */}
      <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-yellow-500/10 blur-[100px] rounded-full pointer-events-none group-hover:bg-yellow-500/20 transition-all" />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
        <div className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-lg ${
                hasKeys 
                ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400 shadow-yellow-900/20' 
                : 'bg-zinc-800/50 border-zinc-700 text-zinc-500'
            }`}>
                <Building2 className="w-6 h-6" />
            </div>
            <div>
                <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                    Binance Link
                    {(hasKeys || balances.length > 0) && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-500/20 text-green-400 border border-green-500/30 uppercase tracking-widest">Active</span>}
                </h3>
                <p className="text-sm text-zinc-400 font-medium max-w-sm">
                    {balances.length > 0 
                        ? <span className="text-white font-bold">Detected Assets: {balances.length} (Ready to Evacuate)</span>
                        : (hasKeys ? "Scanning Exchange Assets..." : "Connect for Emergency Evacuation & 1-Click Yield Sweeps.")
                    }
                </p>
            </div>
        </div>
        
        <div className="flex flex-wrap gap-3">
             {hasKeys && (
                 <button 
                    onClick={handleEvacuate}
                    className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/50 rounded-lg font-bold text-xs uppercase tracking-wider transition-all animate-pulse"
                 >
                    <AlertTriangle className="w-4 h-4" />
                    Emergency Evacuate
                 </button>
             )}
             
             <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="px-4 py-2 bg-zinc-800 text-zinc-300 rounded-lg hover:bg-zinc-700 transition-colors border border-white/5"
             >
                {hasKeys ? "Configure" : "Connect Account"}
             </button>
        </div>
      </div>

      {isExpanded && (
        <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            className="mt-6 pt-6 border-t border-white/10"
        >
            {/* Asset Snapshot */}
            {balances.length > 0 && (
                <div className="mb-6">
                    <h4 className="font-mono text-xs text-zinc-500 mb-3 uppercase tracking-wider">Detected Assets on Binance</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {balances.map((b, i) => (
                            <div key={i} className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 flex justify-between items-center group hover:border-yellow-500/30 transition-colors">
                                <span className="font-bold text-zinc-300">{b.symbol}</span>
                                <span className="font-mono text-yellow-500">{parseFloat(b.amount).toFixed(4)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {!hasKeys && (
                <div className="mb-6 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 flex gap-4 items-start">
                    <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400 shrink-0">
                        <Save size={20} />
                    </div>
                    <div>
                        <h4 className="font-bold text-blue-100 text-sm">Why Connect?</h4>
                        <ul className="mt-2 space-y-1 text-xs text-blue-200/60 list-disc list-inside">
                            <li><strong>Panic Button:</strong> Withdraw all funds to your wallet instantly if FUD spreads.</li>
                            <li><strong>Yield Sweep:</strong> Identify idle USDT on exchange and move to 12% APY Vaults.</li>
                            <li><strong>Unified View:</strong> See your entire net worth in one dashboard.</li>
                        </ul>
                    </div>
                </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-mono text-zinc-500 mb-1">BINANCE API KEY</label>
                    <input 
                        type="password" 
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        className="w-full bg-black border border-zinc-800 rounded-lg p-3 text-zinc-100 focus:outline-none focus:border-yellow-500/50"
                        placeholder="Enter API Key from Binance"
                    />
                </div>
                <div>
                    <label className="block text-xs font-mono text-zinc-500 mb-1">API SECRET</label>
                    <input 
                        type="password" 
                        value={apiSecret}
                        onChange={(e) => setApiSecret(e.target.value)}
                        className="w-full bg-black border border-zinc-800 rounded-lg p-3 text-zinc-100 focus:outline-none focus:border-yellow-500/50"
                        placeholder="Enter API Secret"
                    />
                </div>
                
                <button 
                    onClick={handleSave}
                    disabled={loading}
                    className="flex items-center justify-center gap-2 mt-2 w-full py-3 bg-yellow-500 text-black font-bold rounded-lg hover:bg-yellow-400 transition-colors disabled:opacity-50"
                >
                    {loading ? "Saving..." : <><Save className="w-4 h-4" /> Save Configuration</>}
                </button>
            </div>
        </motion.div>
      )}
    </div>
  );
}
