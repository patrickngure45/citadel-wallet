"use client";

import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Calendar, Clock, Plus, Trash2, Check, User, DollarSign, Repeat } from "lucide-react";

interface Subscription {
  id: string;
  name: string;
  amount: string;
  frequency: string;
  nextPayment: string;
  status: "Active" | "Paused";
}

export function SubscriptionPanel() {
  const [activeView, setActiveView] = useState<"list" | "create">("list");
  const [loading, setLoading] = useState(false);
  const [subs, setSubs] = useState<Subscription[]>([]);

  // Fetch real subscriptions on mount
  useState(() => {
    const fetchSubs = async () => {
      try {
        const { data } = await axios.get("/api/v1/agreements/subscriptions");
        if (data && Array.isArray(data)) {
            setSubs(data);
        }
      } catch (e) {
        console.error("Failed to load subscriptions", e);
      }
    };
    fetchSubs();
    // Poll for updates every 5s
    const interval = setInterval(fetchSubs, 5000);
    return () => clearInterval(interval);
  });

  const [formData, setFormData] = useState({
    recipient: "",
    amount: "",
    token: "USDC",
    frequency: "MONTHLY"
  });

  const handleCreate = async () => {
    setLoading(true);
    const userId = localStorage.getItem("citadel_user_id");
    if (!userId) return;

    try {
        // Construct natural language command
        // "pay Alice 50 USDC every month"
        const intent = `pay ${formData.recipient} ${formData.amount} ${formData.token} every ${formData.frequency.toLowerCase()}`;
        
        await axios.post("/api/v1/hearing/gate", {
            user_id: userId,
            intent: intent,
            execute: true
        });

        // Optimistically add to list for demo feel
        setSubs(prev => [...prev, {
            id: `SUB-${Math.floor(Math.random() * 900) + 100}`,
            name: formData.recipient.length > 10 ? `Transfer to...${formData.recipient.slice(0,4)}` : formData.recipient,
            amount: `${formData.amount} ${formData.token}`,
            frequency: formData.frequency,
            nextPayment: "Immediate",
            status: "Active"
        }]);
        
        setActiveView("list");
        setFormData({ recipient: "", amount: "", token: "USDC", frequency: "MONTHLY" });
    } catch (e) {
        console.error(e);
        alert("Failed to create subscription");
    } finally {
        setLoading(false);
    }
  };

  const handleDelete = (id: string) => {
      setSubs(prev => prev.filter(s => s.id !== id));
  };

  return (
    <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6 rounded-2xl bg-gradient-to-br from-indigo-900/10 to-blue-900/10 border border-indigo-500/20 hover:border-indigo-500/30 transition-all"
    >
        <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center">
                    <Calendar className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-white">Subscriptions</h2>
                    <p className="text-xs text-white/40">Recurring Payments</p>
                </div>
            </div>
            
            {activeView === "list" && (
                <button 
                    onClick={() => setActiveView("create")}
                    className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-indigo-400 transition-colors"
                >
                    <Plus size={20} />
                </button>
            )}
        </div>

        {activeView === "list" ? (
            <div className="space-y-3">
                {subs.length === 0 ? (
                    <div className="text-center py-8 text-white/30 text-sm">No active subscriptions</div>
                ) : (
                    subs.map((sub) => (
                        <div key={sub.id} className="p-3 rounded-lg bg-black/20 border border-white/5 flex items-center justify-between group hover:bg-white/5 transition-colors">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded bg-indigo-500/10 text-indigo-400">
                                    <Clock size={16} />
                                </div>
                                <div>
                                    <h3 className="text-sm font-bold text-white">{sub.name}</h3>
                                    <p className="text-[10px] text-white/40">{sub.frequency} • Next: {sub.nextPayment}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="font-mono text-sm font-bold">{sub.amount}</span>
                                <button 
                                    onClick={() => handleDelete(sub.id)}
                                    className="text-white/20 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        ) : (
            <div className="space-y-4">
                <div className="space-y-2">
                    <label className="text-xs font-bold text-white/50 uppercase flex items-center gap-2">
                        <User size={12} /> Recipient
                    </label>
                    <input 
                        type="text" 
                        value={formData.recipient}
                        onChange={(e) => setFormData({...formData, recipient: e.target.value})}
                        placeholder="Address or Alice/Bob"
                        className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-white/50 uppercase flex items-center gap-2">
                            <DollarSign size={12} /> Amount
                        </label>
                        <input 
                            type="number" 
                            value={formData.amount}
                            onChange={(e) => setFormData({...formData, amount: e.target.value})}
                            placeholder="0.00"
                            className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-white/50 uppercase flex items-center gap-2">
                            <Repeat size={12} /> Frequency
                        </label>
                        <select 
                            value={formData.frequency}
                            onChange={(e) => setFormData({...formData, frequency: e.target.value})}
                            className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                        >
                            <option value="MONTHLY">Monthly</option>
                            <option value="WEEKLY">Weekly</option>
                            <option value="DAILY">Daily</option>
                        </select>
                    </div>
                </div>

                <div className="pt-2 flex gap-2">
                    <button 
                        onClick={() => setActiveView("list")}
                        className="flex-1 py-2 rounded-lg text-xs font-bold text-white/40 hover:bg-white/5 transition-colors"
                    >
                        Cancel
                    </button>
                    <button 
                        onClick={handleCreate}
                        disabled={loading || !formData.recipient || !formData.amount}
                        className="flex-[2] py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-xs font-bold text-white transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                        {loading ? "Scheduling..." : "Create Schedule"}
                    </button>
                </div>
            </div>
        )}
    </motion.div>
  );
}
