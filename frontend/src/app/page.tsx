"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { Copy, Shield, Wallet, ChevronRight, Check, ArrowRight } from "lucide-react";
import clsx from "clsx";

interface UserResponse {
  id: string;
  email: string;
  name: string;
  derivation_index: number;
  wallets: {
    chain: string;
    address: string;
    derivation_path: string;
  }[];
}

export default function Home() {
  const router = useRouter();
  const [step, setStep] = useState<"form" | "loading" | "success">("form");
  const [formData, setFormData] = useState({ name: "", email: "" });
  const [userData, setUserData] = useState<UserResponse | null>(null);
  const [error, setError] = useState("");
  const API_URL = "/api/v1";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.email) return;

    setStep("loading");
    setError("");

    try {
      const res = await axios.post<UserResponse>(`${API_URL}/users/`, {
        email: formData.email,
        name: formData.name,
      });
      setUserData(res.data);
      // Save ID to local storage for persistence
      localStorage.setItem("citadel_user_id", res.data.id.toString());

      // Artificial delay for "effect"
      setTimeout(() => setStep("success"), 1500);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to initialize identity");
      setStep("form");
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Could add toast here
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 overflow-hidden relative">
      {/* Background Ambience */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-900/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-indigo-900/20 rounded-full blur-[120px]" />
      </div>

      <div className="z-10 w-full max-w-md">
        <div className="mb-8 text-center space-y-2">
          <div className="mx-auto w-12 h-12 bg-white/5 rounded-xl border border-white/10 flex items-center justify-center mb-6 backdrop-blur-sm">
            <Shield className="w-6 h-6 text-indigo-400" />
          </div>
          <h1 className="text-3xl font-bold tracking-tighter text-white">Citadel Protocol</h1>
          <p className="text-white/40 text-sm font-medium tracking-wide uppercase">Custodial Identity System</p>
        </div>

        <AnimatePresence mode="wait">
          {step === "form" && (
            <motion.form
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              onSubmit={handleSubmit}
              className="bg-white/5 border border-white/10 p-8 rounded-2xl backdrop-blur-xl space-y-4 shadow-2xl"
            >
              <div className="space-y-1">
                <label className="text-xs font-semibold text-white/50 uppercase tracking-wider">Full Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="John Doe"
                  className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-500/50 transition-colors"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-white/50 uppercase tracking-wider">Email Address</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="citizen@citadel.com"
                  required
                  className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-indigo-500/50 transition-colors"
                />
              </div>

              {error && <p className="text-red-400 text-xs">{error}</p>}

              <button
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-lg transition-all active:scale-[0.98] flex items-center justify-center gap-2 mt-4"
              >
                Initialize Identity <ChevronRight className="w-4 h-4" />
              </button>
            </motion.form>
          )}

          {step === "loading" && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-6"
            >
              <div className="relative w-16 h-16">
                <motion.span
                  className="absolute inset-0 border-2 border-indigo-500/30 rounded-full"
                  animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                />
                 <motion.span
                  className="absolute inset-0 border-t-2 border-indigo-400 rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                />
              </div>
              <p className="text-white/50 text-sm font-mono animate-pulse">DERIVING CRYPTOGRAPHIC KEYS...</p>
            </motion.div>
          )}

          {step === "success" && userData && (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white/5 border border-white/10 p-6 rounded-2xl backdrop-blur-xl space-y-6 shadow-2xl"
            >
              <div className="flex items-center gap-4 border-b border-white/5 pb-6">
                <div className="w-12 h-12 bg-green-500/10 rounded-full flex items-center justify-center border border-green-500/20">
                  <Check className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <h3 className="text-white font-semibold">Identity Established</h3>
                  <p className="text-white/40 text-xs">Derivation Index #{userData.derivation_index}</p>
                </div>
              </div>

              <div className="space-y-4">
                <p className="text-xs font-semibold text-white/50 uppercase tracking-wider px-1">Custodial Deposit Addresses</p>
                {userData.wallets.map((wallet) => (
                  <div key={wallet.chain} className="bg-black/20 rounded-lg p-3 group hover:bg-black/30 transition-colors cursor-pointer" onClick={() => copyToClipboard(wallet.address)}>
                    <div className="flex items-center justify-between mb-2">
                       <div className="flex items-center gap-2">
                          <span className={clsx(
                            "w-2 h-2 rounded-full",
                            wallet.chain === "ethereum" ? "bg-purple-500" : 
                            wallet.chain === "bsc" ? "bg-yellow-500" : "bg-blue-500"
                          )}/>
                          <span className="text-xs font-medium text-white/70 uppercase">{wallet.chain}</span>
                       </div>
                       <Copy className="w-3 h-3 text-white/20 group-hover:text-white/70" />
                    </div>
                    <p className="text-xs font-mono text-white/90 break-all">{wallet.address}</p>
                    <p className="text-[10px] text-white/20 mt-1 font-mono">{wallet.derivation_path}</p>
                  </div>
                ))}
              </div>

              <button
                onClick={() => router.push("/dashboard")}
                className="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-medium py-3 rounded-lg transition-all text-sm flex items-center justify-center gap-2"
              >
                Enter Dashboard <ArrowRight className="w-4 h-4" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
