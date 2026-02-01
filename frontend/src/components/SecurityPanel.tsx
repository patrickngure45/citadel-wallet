"use client";

import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Shield, ShieldAlert, ShieldCheck, UserCheck, Plus, X } from "lucide-react";

interface TrustedContact {
  name: string;
  address: string;
  type: "User" | "Contract" | "Admin";
}

export function SecurityPanel() {
  const [shieldActive, setShieldActive] = useState(true);
  const [contacts, setContacts] = useState<TrustedContact[]>([
    { name: "Citadel Admin", address: "0x57...279", type: "Admin" },
    { name: "Alice (Friend)", address: "0x70...9C8", type: "User" },
    { name: "Bob (Dev)", address: "0x3C...3BC", type: "User" },
  ]);

  const [newContact, setNewContact] = useState({ name: "", address: "" });
  const [adding, setAdding] = useState(false);

  const toggleShield = () => {
      // In a real app, this would update the backend config
      // For demo, we just toggle local state
      setShieldActive(!shieldActive);
  };

  const addContact = () => {
    if (!newContact.name || !newContact.address) return;
    setContacts([...contacts, { ...newContact, type: "User" }]);
    setNewContact({ name: "", address: "" });
    setAdding(false);
  };

  return (
    <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-6 rounded-2xl border transition-all ${shieldActive ? 'bg-indigo-950/20 border-indigo-500/30' : 'bg-red-950/10 border-red-500/30'}`}
    >
        <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${shieldActive ? 'bg-indigo-500/20' : 'bg-red-500/20'}`}>
                    {shieldActive ? <ShieldCheck className="w-5 h-5 text-indigo-400" /> : <ShieldAlert className="w-5 h-5 text-red-400" />}
                </div>
                <div>
                    <h2 className="text-xl font-bold text-white">Security Matrix</h2>
                    <p className="text-xs text-white/40">{shieldActive ? "Shield Protocol Active" : "Shield Suspended"}</p>
                </div>
            </div>
            
            <button 
                onClick={toggleShield}
                className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider transition-colors ${shieldActive ? 'bg-indigo-500 hover:bg-indigo-400 text-white' : 'bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30'}`}
            >
                {shieldActive ? "Enabled" : "Disabled"}
            </button>
        </div>

        <div className="space-y-4">
            <div className="flex items-center justify-between">
                 <h3 className="text-xs font-bold uppercase text-white/50 tracking-wider">Allowlist</h3>
                 <button onClick={() => setAdding(!adding)} className="text-white/40 hover:text-white transition-colors">
                    {adding ? <X size={14} /> : <Plus size={14} />}
                 </button>
            </div>
            
            {adding && (
                <div className="grid grid-cols-3 gap-2 p-2 bg-black/40 rounded-lg animate-in slide-in-from-top-2 fade-in duration-200">
                    <input 
                        className="bg-transparent border-b border-white/20 text-xs p-1 focus:outline-none focus:border-indigo-500 text-white col-span-1"
                        placeholder="Name"
                        value={newContact.name}
                        onChange={e => setNewContact({...newContact, name: e.target.value})}
                    />
                    <input 
                        className="bg-transparent border-b border-white/20 text-xs p-1 focus:outline-none focus:border-indigo-500 text-white col-span-1"
                        placeholder="0x..."
                        value={newContact.address}
                        onChange={e => setNewContact({...newContact, address: e.target.value})}
                    />
                    <button onClick={addContact} className="bg-white/10 hover:bg-white/20 rounded text-xs text-white font-bold h-6">Add</button>
                </div>
            )}

            <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
                {contacts.map((c, i) => (
                    <div key={i} className="flex items-center justify-between p-2 rounded bg-black/20 hover:bg-white/5 border border-white/5 transition-colors group">
                        <div className="flex items-center gap-2">
                            <UserCheck size={12} className="text-emerald-500" />
                            <span className="text-sm font-medium text-white/90">{c.name}</span>
                        </div>
                        <span className="text-[10px] font-mono text-white/30 group-hover:text-white/50 transition-colors">
                            {c.address}
                        </span>
                    </div>
                ))}
            </div>
            
            {shieldActive && (
               <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                  <p className="text-[10px] text-indigo-300 leading-relaxed">
                     <strong className="text-indigo-200">System Lock:</strong> Only listed addresses can receive funds. Unknown active addresses will trigger a <span className="font-mono bg-black/30 px-1 rounded">VETO</span> unless overridden manually.
                  </p>
               </div>
            )}
        </div>
    </motion.div>
  );
}
