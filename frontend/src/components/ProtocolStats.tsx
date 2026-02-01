"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Coins, Database, Activity, ShieldCheck, TrendingUp } from "lucide-react";
import clsx from "clsx";

interface ProtocolData {
  network: string;
  treasury: {
    address: string;
    bnb: number;
    tst: number;
  };
  pilots: {
    alice_tst: number;
  };
}

function formatCompactNumber(num: number): string {
  if (num === 0) return "0";
  // Handle very large numbers safely
  if (num > 1e15) {
     return (num / 1e18).toFixed(2) + "Qi"; // Quintillion/Quinquagesimal placeholder or similar
  }
  return new Intl.NumberFormat('en-US', {
    notation: "compact",
    maximumFractionDigits: 2
  }).format(num);
}

export function ProtocolStats() {
  const [data, setData] = useState<ProtocolData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch("/api/v1/protocol/stats");
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (e) {
        console.error("Failed to fetch protocol stats", e);
      } finally {
        setLoading(false);
      }
    }
    
    fetchStats();
    // Poll every 30s
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="animate-pulse h-24 bg-white/5 rounded-xl w-full"></div>;
  }

  if (!data) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
    >
      {/* Treasury Card */}
      <div className="bg-gradient-to-br from-indigo-900/40 to-purple-900/40 border border-indigo-500/20 rounded-xl p-5 backdrop-blur-sm min-w-0">
        <div className="flex justify-between items-start mb-2">
          <div className="min-w-0 flex-1 mr-2">
            <h3 className="text-sm font-medium text-gray-400 truncate">Citadel Treasury</h3>
            <div className="text-xl md:text-2xl font-bold text-white mt-1 truncate" title={data.treasury.tst.toLocaleString()}>
              {formatCompactNumber(data.treasury.tst)} TST
            </div>
            <div className="text-xs text-indigo-300 mt-1 truncate">
              & {data.treasury.bnb.toFixed(4)} BNB Gas
            </div>
          </div>
          <div className="bg-indigo-500/20 p-2 rounded-lg flex-shrink-0">
            <Database className="w-5 h-5 text-indigo-400" />
          </div>
        </div>
      </div>

      {/* Network Health */}
      <div className="bg-gradient-to-br from-emerald-900/40 to-teal-900/40 border border-emerald-500/20 rounded-xl p-5 backdrop-blur-sm min-w-0">
        <div className="flex justify-between items-start mb-2">
          <div className="min-w-0 flex-1 mr-2">
            <h3 className="text-sm font-medium text-gray-400 truncate">System Status</h3>
            <div className="flex items-center mt-1">
              <div className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse flex-shrink-0"></div>
              <span className="text-lg md:text-xl font-bold text-white uppercase truncate">{data.network}</span>
            </div>
            <div className="text-xs text-emerald-300 mt-1 truncate">
              Escrow Protocol Active
            </div>
          </div>
          <div className="bg-emerald-500/20 p-2 rounded-lg flex-shrink-0">
            <Activity className="w-5 h-5 text-emerald-400" />
          </div>
        </div>
      </div>

       {/* Pilot Stats (Alice) */}
       <div className="bg-gradient-to-br from-amber-900/40 to-orange-900/40 border border-amber-500/20 rounded-xl p-5 backdrop-blur-sm min-w-0">
        <div className="flex justify-between items-start mb-2">
          <div className="min-w-0 flex-1 mr-2">
            <h3 className="text-sm font-medium text-gray-400 truncate">Total Settled Volume</h3>
            <div className="text-xl md:text-2xl font-bold text-white mt-1 truncate" title={data.pilots.alice_tst.toLocaleString()}>
              {formatCompactNumber(data.pilots.alice_tst)} TST
            </div>
            <div className="text-xs text-amber-300 mt-1 truncate">
               Latest Payout to Alice
            </div>
          </div>
          <div className="bg-amber-500/20 p-2 rounded-lg flex-shrink-0">
            <ShieldCheck className="w-5 h-5 text-amber-400" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
