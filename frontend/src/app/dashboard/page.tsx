"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { motion } from "framer-motion";
import { 
  Wallet, ArrowUpRight, ArrowDownLeft, RefreshCw, LogOut, 
  Shield, Lock, CheckCircle, XCircle, ExternalLink, Coins, 
  Send, X, ShoppingCart, History, Clock, Bot, Activity, BrainCircuit
} from "lucide-react";
import clsx from "clsx";
import { WalletConnect } from "@/components/WalletConnect";
import { CexPanel } from "@/components/CexPanel";
import { YieldPanel } from "@/components/YieldPanel";
import { SubscriptionPanel } from "@/components/SubscriptionPanel";
import { SecurityPanel } from "@/components/SecurityPanel";
import { ProtocolStats } from "@/components/ProtocolStats";
import { useWeb3 } from "@/hooks/useWeb3";
import { NETWORK, CONTRACTS } from "@/lib/contracts";
import { transferTST, getPancakeSwapUrl } from "@/lib/web3";

// Format large numbers with suffixes (K, M, B, T, Q for quadrillion, etc.)
function formatLargeNumber(num: number): string {
  if (num === 0) return "0";
  
  const suffixes = [
    { value: 1e18, symbol: "Qi" },  // Quintillion
    { value: 1e15, symbol: "Q" },   // Quadrillion
    { value: 1e12, symbol: "T" },   // Trillion
    { value: 1e9, symbol: "B" },    // Billion
    { value: 1e6, symbol: "M" },    // Million
    { value: 1e3, symbol: "K" },    // Thousand
  ];
  
  for (const suffix of suffixes) {
    if (num >= suffix.value) {
      const formatted = (num / suffix.value).toFixed(2);
      // Remove trailing zeros
      return parseFloat(formatted).toString() + suffix.symbol;
    }
  }
  
  // For numbers < 1000, show up to 4 decimal places
  return num.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

interface BalanceData {
  chain: string;
  address: string;
  balance: number;
  symbol: string;
}

interface Agreement {
  id: string;
  title: string;
  counterparty_email: string;
  token_symbol: string;
  amount: number;
  status: string;
  created_at: string;
}

interface TxHistory {
  hash: string;
  from: string;
  to: string;
  value: string;
  timeStamp: string;
  type: "in" | "out";
}

export default function Dashboard() {
  const router = useRouter();
  const [balances, setBalances] = useState<BalanceData[]>([]);
  const [agreements, setAgreements] = useState<Agreement[]>([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [hasCexKeys, setHasCexKeys] = useState(false);
  
  // Web3 Hook for blockchain interactions
  const { 
    isConnected, 
    tstBalance, 
    bnbBalance, 
    address: walletAddress,
    shortenedAddress,
    explorerUrl,
  } = useWeb3();
  
  // Agreement State
  const [agreementStatus, setAgreementStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [agreementMessage, setAgreementMessage] = useState("");
  
  // Transfer Modal State
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferTo, setTransferTo] = useState("");
  const [transferAmount, setTransferAmount] = useState("");
  const [transferStatus, setTransferStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [transferMessage, setTransferMessage] = useState("");
  
  // Transaction History State
  const [txHistory, setTxHistory] = useState<TxHistory[]>([]);
  const [loadingTx, setLoadingTx] = useState(false);

  // Agent State
  interface AgentStatus {
     status: string;
     last_active: string | null;
     recent_actions: any[];
  }
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({ status: "LOADING", last_active: null, recent_actions: [] });

  // Use relative path so Next.js Proxy handles it
  const API_URL = "/api/v1"; 

  // Fetch transaction history when wallet connects
  useEffect(() => {
    if (walletAddress) {
      fetchTxHistory(walletAddress);
    }
  }, [walletAddress]);
  
  // Check login
  useEffect(() => {
    const storedUserId = localStorage.getItem("citadel_user_id");
    if (!storedUserId) {
      router.push("/");
      return;
    }
    setUserId(storedUserId);
    fetchBalances(storedUserId);
    fetchAgreements(storedUserId);
    fetchUserPermissions(storedUserId);
    fetchAgentStatus(storedUserId);
  }, [router]);

  const fetchAgentStatus = async (id: string) => {
      try {
          const res = await axios.get(`${API_URL}/agent/summary`);
          setAgentStatus(res.data);
      } catch (e) {
          console.error("Failed to fetch agent status", e);
      }
  };

  // Real-time Autopilot Monitoring (Poll every 2s)
  useEffect(() => {
    if (!userId) return;
    const interval = setInterval(() => fetchAgentStatus(userId), 2000);
    return () => clearInterval(interval);
  }, [userId]);

  const fetchTxHistory = async (address: string) => {
    setLoadingTx(true);
    try {
      // Use BscScan API to get token transfers
      const apiKey = "YourApiKeyToken"; // Free tier works without key
      const baseUrl = NETWORK.chainId === 56 
        ? "https://api.bscscan.com/api"
        : "https://api-testnet.bscscan.com/api";
      
      const response = await axios.get(baseUrl, {
        params: {
          module: "account",
          action: "tokentx",
          contractaddress: CONTRACTS.TST_TOKEN,
          address: address,
          page: 1,
          offset: 10,
          sort: "desc",
        }
      });

      if (response.data.status === "1" && response.data.result) {
        const txs: TxHistory[] = response.data.result.map((tx: any) => ({
          hash: tx.hash,
          from: tx.from,
          to: tx.to,
          value: tx.value,
          timeStamp: tx.timeStamp,
          type: tx.to.toLowerCase() === address.toLowerCase() ? "in" : "out",
        }));
        setTxHistory(txs);
      }
    } catch (error) {
      console.error("Failed to fetch tx history:", error);
    } finally {
      setLoadingTx(false);
    }
  };

  // REPLACED BY NEW LOGIN CHECK IN LINES 95-108
  // Keeping simple user permission fetch if needed standalone
  
  const fetchUserPermissions = async (id: string) => {
    try {
        const res = await axios.get(`${API_URL}/users/${id}`);
        if (res.data.cex_config && res.data.cex_config.binance) {
            setHasCexKeys(true);
        }
    } catch (error) {
        console.error("Failed to fetch user permissions", error);
    }
  };

  const fetchAgreements = async (id: string) => {
    try {
      const res = await axios.get<Agreement[]>(`${API_URL}/agreements/${id}/list`);
      setAgreements(res.data);
    } catch (error) {
      console.error("Failed to fetch agreements", error);
    }
  };

  const fetchBalances = async (id: string) => {
    setLoading(true);
    try {
      const res = await axios.get<BalanceData[]>(`${API_URL}/wallets/${id}/balances`);
      setBalances(res.data);
    } catch (error) {
      console.error("Failed to fetch balances", error);
    } finally {
      setLoading(false);
    }
  };

  const createAgreement = async () => {
    if (!userId) return;
    setAgreementStatus("loading");
    setAgreementMessage("");
    
    // MOCK DATA for now, until we add a proper modal form
    const agreementPayload = {
        title: "Test Agreement",
        counterparty_email: "bob@example.com",
        chain: "ethereum",
        token_symbol: "ETH",
        amount: 0.1
    };
    
    try {
        await axios.post(`${API_URL}/agreements/${userId}/create`, agreementPayload);
        setAgreementStatus("success");
        setAgreementMessage("Secure P2P Agreement Initialized");
        fetchAgreements(userId);
    } catch (err: any) {
        setAgreementStatus("error");
        setAgreementMessage(err.response?.data?.detail || "Access Denied");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("citadel_user_id");
    router.push("/");
  };
  
  // Remove the old useEffect that was failing


  const handleTransfer = async () => {
    if (!transferTo || !transferAmount) {
      setTransferMessage("Input Directive Incomplete");
      setTransferStatus("error");
      return;
    }

    // Validate address
    if (!/^0x[a-fA-F0-9]{40}$/.test(transferTo)) {
      setTransferMessage("Invalid Vector Destination");
      setTransferStatus("error");
      return;
    }

    // Validate amount
    const amount = parseFloat(transferAmount);
    if (isNaN(amount) || amount <= 0) {
      setTransferMessage("Invalid Vector Quantity");
      setTransferStatus("error");
      return;
    }

    setTransferStatus("loading");
    setTransferMessage("");

    const result = await transferTST(transferTo, transferAmount);

    if (result.success) {
      setTransferStatus("success");
      setTransferMessage(`Transmission Output: ${result.txHash?.slice(0, 10)}...`);
      setTransferTo("");
      setTransferAmount("");
      // Refresh balance after 3 seconds
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    } else {
      setTransferStatus("error");
      setTransferMessage(result.error || "Transmission Failed");
    }
  };

  const getTotalValue = () => {
    // Mock price data for demo since we only have native amounts
    return balances.reduce((acc, curr) => {
      let price = 0;
      if (curr.chain === "ethereum") price = 2200;
      if (curr.chain === "bsc") price = 300;
      if (curr.chain === "polygon") price = 0.8;
      return acc + (curr.balance * price);
    }, 0);
  };

  if (!userId) return null;

  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-indigo-500/30">
      
      {/* Navbar */}
      <nav className="border-b border-white/10 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-cyan-500/10 rounded-lg border border-cyan-500/30 flex items-center justify-center">
                <Wallet className="w-4 h-4 text-cyan-400" />
              </div>
              <span className="font-bold tracking-tight text-lg">CITADEL <span className="text-white/30 font-light">CORE</span></span>
            </div>
            <div className="flex items-center gap-4">
              <button 
                  onClick={() => router.push('/hearing')} 
                  className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-cyan-300 hover:text-white transition-colors bg-cyan-500/10 hover:bg-cyan-500/20 px-4 py-1.5 rounded-sm border border-cyan-500/20"
              >
                 <span className="hidden sm:inline">Entity Matrix</span>
                 <ExternalLink size={14} />
              </button>

              {/* Web3 Wallet Connect */}
              <WalletConnect />
              <button onClick={() => fetchBalances(userId!)} className="p-2 hover:bg-white/5 rounded-full transition-colors" title="Sync">
                <RefreshCw className={clsx("w-4 h-4 text-white/50", loading && "animate-spin")} />
              </button>
              <button onClick={handleLogout} className="p-2 hover:bg-white/5 rounded-full transition-colors text-red-400" title="Exit">
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Protocol Network Status */}
        <ProtocolStats />

        {/* Portfolio Value */}
        <section>
            <p className="text-white/40 text-xs font-bold uppercase tracking-widest mb-1">Total System Liquidity (Est.)</p>
            <h1 className="text-4xl font-mono font-bold tracking-tighter text-white">
                ${getTotalValue().toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h1>
        </section>

        <CexPanel 
            userId={userId} 
            hasKeys={hasCexKeys} 
            onUpdate={() => userId && fetchUserPermissions(userId)} 
        />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <YieldPanel />
            <div className="space-y-4">
                <SubscriptionPanel />
                <SecurityPanel />
            </div>
        </div>

        {/* Assets Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            
            {/* TST Token Card - Real Blockchain Data */}
            {isConnected && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-6 rounded-2xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/30 hover:border-amber-500/50 transition-all group overflow-hidden"
              >
                <div className="flex items-start justify-between mb-4 gap-2">
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center">
                      <Coins className="w-5 h-5 text-amber-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-amber-400">TST Token</h3>
                      <p className="text-xs text-white/40">{NETWORK.name}</p>
                    </div>
                  </div>
                  <div className="text-right min-w-0 flex-shrink">
                    <p className="text-lg font-bold font-mono text-white truncate" title={tstBalance?.formatted || "0"}>
                      {tstBalance ? formatLargeNumber(parseFloat(tstBalance.formatted)) : "0"}
                    </p>
                    <p className="text-xs text-amber-400">TST</p>
                  </div>
                </div>
                
                <div className="text-xs text-white/30 font-mono mb-2 truncate">
                  {CONTRACTS.TST_TOKEN}
                </div>
                
                {/* Gas Balance */}
                <div className="flex items-center justify-between text-xs mb-3 px-2 py-1.5 bg-black/30 rounded-lg">
                  <span className="text-white/40">Gas (BNB):</span>
                  <span className={clsx(
                    "font-mono",
                    parseFloat(bnbBalance || "0") < 0.001 ? "text-red-400" : "text-green-400"
                  )}>
                    {parseFloat(bnbBalance || "0").toFixed(4)} BNB
                  </span>
                </div>
                
                {/* Action Buttons */}
                <div className="grid grid-cols-2 gap-2 mb-2">
                  <button
                    onClick={() => setShowTransferModal(true)}
                    className="flex items-center justify-center gap-1 py-2 bg-amber-500/20 hover:bg-amber-500/30 rounded-lg text-xs font-medium text-amber-400 transition-colors"
                  >
                    <Send className="w-3 h-3" /> Send
                  </button>
                  <a 
                    href={getPancakeSwapUrl()}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-1 py-2 bg-green-500/20 hover:bg-green-500/30 rounded-lg text-xs font-medium text-green-400 transition-colors"
                  >
                    <ShoppingCart className="w-3 h-3" /> Trade
                  </a>
                </div>
                
                <a 
                  href={`${NETWORK.explorer}/token/${CONTRACTS.TST_TOKEN}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-1 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-medium text-white/60 transition-colors"
                >
                  <ExternalLink className="w-3 h-3" /> View on Explorer
                </a>
              </motion.div>
            )}
            
            {/* Existing balance cards */}
            {balances.map((asset) => (
                <motion.div 
                    key={asset.chain}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all group"
                >
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className={clsx(
                                "w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold",
                                asset.chain === "ethereum" ? "bg-purple-500/20 text-purple-400" :
                                asset.chain === "bsc" ? "bg-yellow-500/20 text-yellow-400" :
                                "bg-blue-500/20 text-blue-400"
                            )}>
                                {asset.symbol[0]}
                            </div>
                            <div>
                                <h3 className="font-semibold capitalize">{asset.chain}</h3>
                                <p className="text-xs text-white/40 font-mono">{asset.address.slice(0, 6)}...{asset.address.slice(-4)}</p>
                            </div>
                        </div>
                        <div className="text-right">
                             <p className="text-lg font-bold font-mono">{asset.balance.toFixed(4)}</p>
                             <p className="text-xs text-white/40">{asset.symbol}</p>
                        </div>
                    </div>
                    
                    <div className="flex gap-2 mt-4">
                        <button className="flex-1 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-medium flex items-center justify-center gap-1 transition-colors">
                            <ArrowDownLeft className="w-3 h-3" /> Deposit
                        </button>
                        <button className="flex-1 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-medium flex items-center justify-center gap-1 transition-colors">
                            <ArrowUpRight className="w-3 h-3" /> Withdraw
                        </button>
                    </div>
                </motion.div>
            ))}
            
            {loading && balances.length === 0 && (
                [1,2,3].map(i => (
                    <div key={i} className="h-[180px] rounded-2xl bg-white/5 animate-pulse" />
                ))
            )}
        </div>

        {/* Transaction History */}
        {isConnected && (
          <section>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-amber-400" />
                <h2 className="text-xl font-bold text-white">Recent TST Transfers</h2>
              </div>
              {walletAddress && (
                <button 
                  onClick={() => fetchTxHistory(walletAddress)}
                  className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                >
                  <RefreshCw className={clsx("w-4 h-4 text-white/50", loadingTx && "animate-spin")} />
                </button>
              )}
            </div>

            {loadingTx ? (
              <div className="space-y-3">
                {[1,2,3].map(i => (
                  <div key={i} className="h-16 rounded-xl bg-white/5 animate-pulse" />
                ))}
              </div>
            ) : txHistory.length > 0 ? (
              <div className="space-y-2">
                {txHistory.map((tx) => {
                  const amount = parseFloat(tx.value) / 1e18;
                  const date = new Date(parseInt(tx.timeStamp) * 1000);
                  const isIncoming = tx.type === "in";
                  
                  return (
                    <motion.a
                      key={tx.hash}
                      href={`${NETWORK.explorer}/tx/${tx.hash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <div className={clsx(
                          "w-10 h-10 rounded-full flex items-center justify-center",
                          isIncoming ? "bg-green-500/20" : "bg-red-500/20"
                        )}>
                          {isIncoming ? (
                            <ArrowDownLeft className="w-5 h-5 text-green-400" />
                          ) : (
                            <ArrowUpRight className="w-5 h-5 text-red-400" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-white text-sm">
                            {isIncoming ? "Received" : "Sent"}
                          </p>
                          <p className="text-xs text-white/40 font-mono">
                            {isIncoming ? `From: ${tx.from.slice(0,6)}...${tx.from.slice(-4)}` : `To: ${tx.to.slice(0,6)}...${tx.to.slice(-4)}`}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={clsx(
                          "font-bold font-mono text-sm",
                          isIncoming ? "text-green-400" : "text-red-400"
                        )}>
                          {isIncoming ? "+" : "-"}{formatLargeNumber(amount)} TST
                        </p>
                        <div className="flex items-center gap-1 text-xs text-white/40">
                          <Clock className="w-3 h-3" />
                          {date.toLocaleDateString()} {date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </div>
                      </div>
                    </motion.a>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-white/40">
                <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No TST transfers yet</p>
              </div>
            )}
          </section>
        )}

        {/* Agent Status Panel - INTELLIGENCE PLANE */}
        <section className="mt-8 mb-8">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Bot className="w-5 h-5 text-emerald-400" />
                    <h2 className="text-xl font-bold text-white">Agent Status</h2>
                </div>
                <button 
                  onClick={() => router.push("/hearing")} 
                  className="text-xs text-white/50 hover:text-white flex items-center gap-1"
                >
                  <ExternalLink size={12} /> Console
                </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1. Health Card */}
                <div className="p-6 rounded-2xl bg-[#0F1218] border border-white/5 relative overflow-hidden group">
                   <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="text-xs text-white/40 uppercase tracking-widest font-bold mb-1">AUTOPILOT</div>
                        <div className="flex items-center gap-2">
                            <div className={clsx("w-3 h-3 rounded-full animate-pulse", 
                                agentStatus.status === "ONLINE" ? "bg-emerald-500" : "bg-red-500"
                            )} />
                            <span className={clsx("font-mono font-bold text-xl",
                                agentStatus.status === "ONLINE" ? "text-emerald-400" : "text-white/40"
                            )}>
                                {agentStatus.status}
                            </span>
                        </div>
                      </div>
                      <BrainCircuit className={clsx("w-8 h-8 opacity-20", agentStatus.status === "ONLINE" ? "text-emerald-500" : "text-gray-500")} />
                   </div>
                   {agentStatus.last_active && (
                       <div className="text-xs text-white/30 font-mono">
                           Last Heartbeat: {new Date(agentStatus.last_active).toLocaleTimeString()}
                       </div>
                   )}
                </div>

                {/* 2. Recent Actions Feed */}
                <div className="p-6 rounded-2xl bg-[#0F1218] border border-white/5">
                    <div className="text-xs text-white/40 uppercase tracking-widest font-bold mb-3">RECENT DECISIONS</div>
                    <div className="space-y-3">
                        {agentStatus.recent_actions.length === 0 && (
                            <div className="text-white/20 text-xs italic">No info in the cortex.</div>
                        )}
                        {agentStatus.recent_actions.map((act: any) => {
                            // Extract Strategy/Profit Info if available
                            let strategyInfo = null;
                            const steps = act.transcript?.strategy?.feasible_options?.[0]?.steps;
                            if (steps) {
                                const spread = steps.find((s: string) => s.includes("Spread:"));
                                const profit = steps.find((s: string) => s.includes("Profit"));
                                if (spread || profit) strategyInfo = spread || profit;
                            }
                            if (!strategyInfo && act.transcript?.execution?.tx_hash?.includes("Arb Profit")) {
                                strategyInfo = act.transcript.execution.tx_hash;
                            }

                            return (
                                <div key={act.id} className="flex flex-col gap-1 text-sm group cursor-pointer p-2 rounded hover:bg-white/5 transition-colors" onClick={() => router.push(`/hearing?id=${act.id}`)}>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2 overflow-hidden">
                                             <div className={clsx("w-1.5 h-1.5 rounded-full flex-shrink-0",
                                                 (act.verdict === "ALLOWED" || act.verdict === "EXECUTED") ? "bg-green-500" : "bg-red-500"
                                             )} />
                                             <span className="truncate text-white/90 font-medium">{act.intent.replace("AUTOPILOT: ", "")}</span>
                                        </div>
                                        <span className="text-[10px] text-white/30 font-mono">{new Date(act.time).toLocaleTimeString()}</span>
                                    </div>
                                    {act.reason && (
                                        <div className="pl-3.5 text-xs text-indigo-400/80 font-mono truncate">
                                            ↳ {act.reason}
                                        </div>
                                    )}
                                    {strategyInfo && (
                                        <div className="pl-3.5 text-xs text-emerald-400 font-mono font-bold truncate flex items-center gap-1">
                                            <ArrowUpRight className="w-3 h-3" /> {strategyInfo}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </section>

        {/* Premium Services / TST Gate */}
        <section>
            <div className="flex items-center gap-2 mb-4">
                <Shield className="w-5 h-5 text-indigo-400" />
                <h2 className="text-xl font-bold text-white">Premium Services</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* On-Chain Escrow - New */}
              <div className="p-1 rounded-2xl bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20">
                <div className="bg-black/90 p-6 rounded-xl backdrop-blur-sm h-full">
                    <div className="flex items-start justify-between mb-4">
                        <h3 className="text-lg font-bold text-white">On-Chain Escrow</h3>
                        <div className="w-10 h-10 bg-indigo-500/10 rounded-full flex items-center justify-center border border-indigo-500/20">
                            <Lock className="w-5 h-5 text-indigo-400" />
                        </div>
                    </div>
                    <p className="text-sm text-white/50 mb-4">
                        Lock TST tokens in a smart contract escrow. Release funds when the deal is complete.
                    </p>
                    <button 
                        onClick={() => router.push("/agreements")}
                        className="w-full px-4 py-2 rounded-lg text-sm font-bold flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white transition-all"
                    >
                        <Shield className="w-4 h-4" />
                        Manage Escrow Agreements
                    </button>
                </div>
              </div>
              
              {/* P2P Agreement - Legacy Backend */}
              <div className="p-1 rounded-2xl bg-gradient-to-r from-amber-500/20 via-orange-500/20 to-red-500/20">
                <div className="bg-black/90 p-6 rounded-xl backdrop-blur-sm h-full">
                    <div className="flex items-start justify-between mb-4">
                        <h3 className="text-lg font-bold text-white">P2P Agreement</h3>
                        <div className="w-10 h-10 bg-amber-500/10 rounded-full flex items-center justify-center border border-amber-500/20">
                            <Shield className="w-5 h-5 text-amber-400" />
                        </div>
                    </div>
                    <p className="text-sm text-white/50 mb-4">
                        Create tracked agreements with counterparties.
                        <span className="text-amber-400 block mt-1 font-medium">Requires 100 TST Holdings</span>
                    </p>
                    
                    <button 
                        onClick={createAgreement}
                        disabled={agreementStatus === "loading" || agreementStatus === "success"}
                        className={clsx(
                            "w-full px-4 py-2 rounded-lg text-sm font-bold flex items-center justify-center gap-2 transition-all",
                            agreementStatus === "success" ? "bg-green-500/20 text-green-400 cursor-default" :
                            agreementStatus === "error" ? "bg-red-500/20 text-red-100 hover:bg-red-500/30" :
                            "bg-amber-600 hover:bg-amber-500 text-white"
                        )}
                    >
                        {agreementStatus === "loading" ? (
                            <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : agreementStatus === "success" ? (
                            <CheckCircle className="w-4 h-4" />
                        ) : agreementStatus === "error" ? (
                            <Lock className="w-4 h-4" />
                        ) : (
                            <Shield className="w-4 h-4" />
                        )}
                        
                        {agreementStatus === "loading" ? "Verifying Holdings..." :
                         agreementStatus === "success" ? "Access Granted" :
                         agreementStatus === "error" ? "Retry Access" :
                         "Initialize Agreement"}
                    </button>

                    {agreementMessage && (
                        <motion.div 
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            className={clsx(
                                "mt-3 text-xs font-mono p-2 rounded border",
                                agreementStatus === "success" ? "bg-green-500/10 border-green-500/20 text-green-400" :
                                "bg-red-500/10 border-red-500/20 text-red-400"
                            )}
                        >
                            {agreementStatus === "error" && <Lock className="w-3 h-3 inline mr-1" />}
                            {agreementMessage}
                        </motion.div>
                    )}
                </div>
              </div>
            </div>

            {/* Active Agreements List */}
            {agreements.length > 0 && (
                <div className="mt-8">
                    <h3 className="text-lg font-bold text-white mb-4">On-Chain Escrows (Verified)</h3>
                    <div className="space-y-3">
                        {agreements.map((agreement) => (
                            <motion.div 
                                key={agreement.id} 
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between group"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                                        <Lock className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-white text-sm">{agreement.counterparty_email}</h4>
                                        <div className="flex items-center gap-2 text-xs text-white/50">
                                            {agreement.contract_address && agreement.contract_address !== "OFF_CHAIN_NEGOTIATION" && (
                                                <a 
                                                    href={`${NETWORK.explorer}/address/${agreement.contract_address}`}
                                                    target="_blank"
                                                    className="flex items-center gap-1 hover:text-indigo-400 transition-colors"
                                                >
                                                    <ExternalLink size={10} /> Smart Contract
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="font-mono font-bold text-indigo-400 text-sm">{agreement.amount} {agreement.token_symbol}</p>
                                    <div className="flex items-center gap-2 justify-end">
                                        <span className={clsx(
                                            "text-[10px] uppercase font-bold px-2 py-0.5 rounded",
                                            agreement.status === "PENDING" ? "bg-yellow-500/20 text-yellow-500" :
                                            agreement.status === "ACTIVE" ? "bg-green-500/20 text-green-500" :
                                            "bg-white/10 text-white/50"
                                        )}>{agreement.status}</span>
                                        <button className="text-white/20 hover:text-white transition-colors" title="Release Funds (Coming Soon)">
                                            <CheckCircle className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

        </section>

      </main>

      {/* Transfer Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-full max-w-md"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Send TST Tokens</h2>
              <button 
                onClick={() => {
                  setShowTransferModal(false);
                  setTransferStatus("idle");
                  setTransferMessage("");
                }}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-white/60" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-white/60 mb-2">Recipient Address</label>
                <input
                  type="text"
                  value={transferTo}
                  onChange={(e) => setTransferTo(e.target.value)}
                  placeholder="0x..."
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-amber-500/50 font-mono text-sm"
                />
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">Amount (TST)</label>
                <input
                  type="number"
                  value={transferAmount}
                  onChange={(e) => setTransferAmount(e.target.value)}
                  placeholder="0.00"
                  step="any"
                  min="0"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-amber-500/50 font-mono"
                />
                {tstBalance && (
                  <p className="text-xs text-white/40 mt-1">
                    Balance: {formatLargeNumber(parseFloat(tstBalance.formatted))} TST
                  </p>
                )}
              </div>

              {transferMessage && (
                <div className={clsx(
                  "p-3 rounded-lg text-sm",
                  transferStatus === "success" ? "bg-green-500/20 text-green-400" :
                  transferStatus === "error" ? "bg-red-500/20 text-red-400" :
                  "bg-white/5 text-white/60"
                )}>
                  {transferMessage}
                </div>
              )}

              <button
                onClick={handleTransfer}
                disabled={transferStatus === "loading"}
                className={clsx(
                  "w-full py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all",
                  transferStatus === "loading" 
                    ? "bg-amber-500/20 text-amber-400 cursor-not-allowed"
                    : "bg-amber-500 hover:bg-amber-600 text-black"
                )}
              >
                {transferStatus === "loading" ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send TST
                  </>
                )}
              </button>

              <p className="text-xs text-center text-white/30">
                Transaction will be sent on {NETWORK.name}
              </p>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
