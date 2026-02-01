"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { 
  ArrowLeft, 
  Plus, 
  Shield, 
  Lock, 
  CheckCircle, 
  XCircle, 
  Clock, 
  RefreshCw, 
  X,
  ExternalLink,
  Coins,
  AlertTriangle,
  Bot
} from "lucide-react";
import clsx from "clsx";
import { WalletConnect } from "@/components/WalletConnect";
import { useWeb3 } from "@/hooks/useWeb3";
import { NETWORK, CONTRACTS, AGREEMENT_STATUS } from "@/lib/contracts";
import { 
  createEscrowAgreement, 
  releaseEscrowFunds, 
  getUserEscrowAgreements,
  EscrowAgreement,
  shortenAddress
} from "@/lib/web3";

// Format large numbers
function formatAmount(num: number): string {
  if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
  if (num >= 1e3) return (num / 1e3).toFixed(2) + "K";
  return num.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

export default function AgreementsPage() {
  const router = useRouter();
  const { isConnected, address: walletAddress, tstBalance } = useWeb3();
  
  // State
  const [agreements, setAgreements] = useState<EscrowAgreement[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  // Create form state
  const [payeeAddress, setPayeeAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [createStatus, setCreateStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [createMessage, setCreateMessage] = useState("");
  
  // Release state
  const [releasingId, setReleasingId] = useState<number | null>(null);

  // Check if escrow is available (Supports BNB or TST)
  const escrowAvailable = !!CONTRACTS.ESCROW || !!CONTRACTS.TST_ESCROW;

  // Fetch agreements when wallet connects
  useEffect(() => {
    if (walletAddress && escrowAvailable) {
      fetchAgreements();
    }
  }, [walletAddress]);

  const fetchAgreements = async () => {
    if (!walletAddress) return;
    setLoading(true);
    try {
      const userAgreements = await getUserEscrowAgreements(walletAddress);
      setAgreements(userAgreements);
    } catch (error) {
      console.error("Failed to fetch agreements:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentCreate = async () => {
    // Navigate to Entity Matrix with pre-filled intent
    const intent = `Lock ${amount} TST in Escrow for ${payeeAddress}. Context: ${description}`;
    router.push(`/hearing?intent=${encodeURIComponent(intent)}`);
  };

  const handleCreate = async () => {
    // Validation
    if (!payeeAddress || !amount || !description) {
      setCreateMessage("Please fill in all fields");
      setCreateStatus("error");
      return;
    }

    if (!/^0x[a-fA-F0-9]{40}$/.test(payeeAddress)) {
      setCreateMessage("Invalid wallet address");
      setCreateStatus("error");
      return;
    }

    if (payeeAddress.toLowerCase() === walletAddress?.toLowerCase()) {
      setCreateMessage("Cannot create agreement with yourself");
      setCreateStatus("error");
      return;
    }

    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      setCreateMessage("Invalid amount");
      setCreateStatus("error");
      return;
    }

    setCreateStatus("loading");
    setCreateMessage("Approve TST spending in MetaMask...");

    const result = await createEscrowAgreement(payeeAddress, amount, description);

    if (result.success) {
      setCreateStatus("success");
      setCreateMessage(`Agreement #${result.agreementId} created!`);
      setPayeeAddress("");
      setAmount("");
      setDescription("");
      fetchAgreements();
      
      // Close modal after 2 seconds
      setTimeout(() => {
        setShowCreateModal(false);
        setCreateStatus("idle");
        setCreateMessage("");
      }, 2000);
    } else {
      setCreateStatus("error");
      setCreateMessage(result.error || "Failed to create agreement");
    }
  };

  const handleRelease = async (agreementId: number, isTst: boolean) => {
    setReleasingId(agreementId);
    
    const result = await releaseEscrowFunds(agreementId, isTst);
    
    if (result.success) {
      fetchAgreements();
    } else {
      alert(result.error || "Failed to release funds");
    }
    
    setReleasingId(null);
  };

  const getStatusColor = (status: number) => {
    switch (status) {
      case 0: return "bg-gray-500/20 text-gray-400"; // Created
      case 1: return "bg-amber-500/20 text-amber-400"; // Funded
      case 2: return "bg-green-500/20 text-green-400"; // Released
      case 3: return "bg-red-500/20 text-red-400"; // Refunded
      case 4: return "bg-gray-500/20 text-gray-500"; // Cancelled
      default: return "bg-white/10 text-white/50";
    }
  };

  const getStatusIcon = (status: number) => {
    switch (status) {
      case 0: return <Clock className="w-4 h-4" />;
      case 1: return <Lock className="w-4 h-4" />;
      case 2: return <CheckCircle className="w-4 h-4" />;
      case 3: return <XCircle className="w-4 h-4" />;
      case 4: return <XCircle className="w-4 h-4" />;
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white font-sans">
      {/* Header */}
      <nav className="border-b border-white/10 bg-white/5 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => router.push("/dashboard")}
                className="p-2 hover:bg-white/5 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-white/60" />
              </button>
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-indigo-400" />
                <span className="font-bold">P2P Escrow</span>
              </div>
            </div>
            <WalletConnect />
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Escrow Not Available Warning */}
        {!escrowAvailable && (
          <div className="mb-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-amber-400">Escrow Not Available</h3>
              <p className="text-sm text-white/60 mt-1">
                The escrow contract is not yet deployed on {NETWORK.name}. 
                This feature will be available soon.
              </p>
            </div>
          </div>
        )}

        {/* Not Connected State */}
        {!isConnected && (
          <div className="text-center py-12">
            <Shield className="w-12 h-12 mx-auto mb-4 text-indigo-400 opacity-50" />
            <h2 className="text-xl font-bold mb-2">Connect Your Wallet</h2>
            <p className="text-white/50 mb-6">Connect your wallet to create and manage P2P escrow agreements</p>
            <WalletConnect />
          </div>
        )}

        {/* Connected State */}
        {isConnected && escrowAvailable && (
          <>
            {/* Header with Create Button */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold">Your Agreements</h1>
                <p className="text-white/50 text-sm mt-1">
                  Secure P2P escrow using TST tokens
                </p>
              </div>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold flex items-center gap-2 transition-colors"
              >
                <Plus className="w-4 h-4" /> New Agreement
              </button>
            </div>

            {/* Agreements List */}
            {loading ? (
              <div className="space-y-3">
                {[1,2,3].map(i => (
                  <div key={i} className="h-24 rounded-xl bg-white/5 animate-pulse" />
                ))}
              </div>
            ) : agreements.length > 0 ? (
              <div className="space-y-4">
                {agreements.map((agr) => {
                  const isPayer = agr.payer.toLowerCase() === walletAddress?.toLowerCase();
                  const canRelease = isPayer && agr.status === 1;
                  
                  return (
                    <motion.div
                      key={agr.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-5 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center">
                            <Lock className="w-5 h-5 text-indigo-400" />
                          </div>
                          <div>
                            <h3 className="font-bold text-white">Agreement #{agr.id}</h3>
                            <p className="text-xs text-white/40">
                              {agr.createdAt.toLocaleDateString()} {agr.createdAt.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </p>
                          </div>
                        </div>
                        <div className={clsx(
                          "px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1",
                          getStatusColor(agr.status)
                        )}>
                          {getStatusIcon(agr.status)}
                          {AGREEMENT_STATUS[agr.status as keyof typeof AGREEMENT_STATUS]}
                          {agr.token === "TST" && (
                             <span className="ml-1 px-1 bg-black/30 rounded text-emerald-400">TST</span>
                          )}
                        </div>
                      </div>

                      <p className="text-white/70 text-sm mb-3">{agr.description}</p>
                      
                      <div className="flex items-center gap-2 mb-4 p-2 bg-black/20 rounded">
                         <span className="text-white/50 text-xs">Amount:</span>
                         <span className="font-mono text-lg font-bold">
                             {agr.amount} {agr.token || "BNB"}
                         </span>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                        <div>
                          <span className="text-white/40 block text-xs mb-1">Payer</span>
                          <span className="font-mono text-white/80">
                            {isPayer ? "You" : shortenAddress(agr.payer)}
                          </span>
                        </div>
                        <div>
                          <span className="text-white/40 block text-xs mb-1">Payee</span>
                          <span className="font-mono text-white/80">
                            {!isPayer ? "You" : shortenAddress(agr.payee)}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Coins className="w-4 h-4 text-amber-400" />
                          <span className="font-bold font-mono text-amber-400">
                            {formatAmount(parseFloat(agr.amount))} {agr.token || "BNB"}
                          </span>
                        </div>
                        
                        {canRelease && (
                          <button
                            onClick={() => handleRelease(agr.id, agr.token === "TST")}
                            disabled={releasingId === agr.id}
                            className={clsx(
                              "px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors",
                              releasingId === agr.id 
                                ? "bg-green-500/20 text-green-400 cursor-not-allowed"
                                : "bg-green-600 hover:bg-green-500 text-white"
                            )}
                          >
                            {releasingId === agr.id ? (
                              <RefreshCw className="w-4 h-4 animate-spin" />
                            ) : (
                              <CheckCircle className="w-4 h-4" />
                            )}
                            Release Funds
                          </button>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12 border border-dashed border-white/10 rounded-xl">
                <Shield className="w-12 h-12 mx-auto mb-4 text-indigo-400 opacity-30" />
                <h3 className="font-bold text-white/60 mb-2">No Agreements Yet</h3>
                <p className="text-white/40 text-sm mb-4">
                  Create your first P2P escrow agreement
                </p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold inline-flex items-center gap-2 transition-colors"
                >
                  <Plus className="w-4 h-4" /> Create Agreement
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Create Agreement Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-full max-w-md"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">New Escrow Agreement</h2>
              <button 
                onClick={() => {
                  setShowCreateModal(false);
                  setCreateStatus("idle");
                  setCreateMessage("");
                }}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-white/60" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-white/60 mb-2">Payee Address</label>
                <input
                  type="text"
                  value={payeeAddress}
                  onChange={(e) => setPayeeAddress(e.target.value)}
                  placeholder="0x..."
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-indigo-500/50 font-mono text-sm"
                />
                <p className="text-xs text-white/40 mt-1">The address that will receive the funds</p>
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">Amount (TST)</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  step="any"
                  min="0"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-indigo-500/50 font-mono"
                />
                {tstBalance && (
                  <p className="text-xs text-white/40 mt-1">
                    Your balance: {formatAmount(parseFloat(tstBalance.formatted))} TST
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">Description</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="What is this payment for?"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-indigo-500/50 text-sm"
                />
              </div>

              {createMessage && (
                <div className={clsx(
                  "p-3 rounded-lg text-sm",
                  createStatus === "success" ? "bg-green-500/20 text-green-400" :
                  createStatus === "error" ? "bg-red-500/20 text-red-400" :
                  "bg-indigo-500/20 text-indigo-400"
                )}>
                  {createMessage}
                </div>
              )}

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <button
                  onClick={handleCreate}
                  disabled={createStatus === "loading" || createStatus === "success"}
                  className={clsx(
                    "py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all",
                    createStatus === "loading" 
                      ? "bg-indigo-500/20 text-indigo-400 cursor-not-allowed"
                      : createStatus === "success"
                      ? "bg-green-500/20 text-green-400 cursor-not-allowed"
                      : "bg-white/5 hover:bg-white/10 text-white/80"
                  )}
                >
                  {createStatus === "loading" ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Lock className="w-4 h-4" />
                  )}
                  <span>Manual Lock</span>
                </button>

                <button
                  onClick={handleAgentCreate}
                  className="py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all bg-gradient-to-r from-emerald-500/20 to-teal-500/20 hover:from-emerald-500/30 hover:to-teal-500/30 text-emerald-400 border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.1)] group"
                >
                  <Bot className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                  <span>Agent Auto-Lock</span>
                </button>
              </div>

              <p className="text-xs text-center text-white/30">
                You'll need to approve 2 transactions: TST approval + escrow creation
              </p>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
