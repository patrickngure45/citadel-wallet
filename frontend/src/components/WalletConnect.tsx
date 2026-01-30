/**
 * WalletConnect Component
 * 
 * Button to connect MetaMask wallet and display connection status.
 */

"use client";

import { useWeb3 } from "@/hooks/useWeb3";
import { Wallet, ExternalLink, Plus, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";

export function WalletConnect() {
  const {
    address,
    isConnected,
    isCorrectNetwork,
    isLoading,
    isMainnet,
    networkName,
    tstBalance,
    bnbBalance,
    connect,
    disconnect,
    switchNetwork,
    addTokenToWallet,
    refreshBalances,
    shortenedAddress,
    explorerUrl,
  } = useWeb3();

  // Not connected - show connect button
  if (!isConnected) {
    return (
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={connect}
        disabled={isLoading}
        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 rounded-lg text-black font-semibold hover:from-amber-400 hover:to-orange-400 transition-all disabled:opacity-50"
      >
        <Wallet className="w-4 h-4" />
        {isLoading ? "Connecting..." : "Connect Wallet"}
      </motion.button>
    );
  }

  // Connected but wrong network
  if (!isCorrectNetwork) {
    return (
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={switchNetwork}
        disabled={isLoading}
        className="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500 rounded-lg text-red-400 font-medium hover:bg-red-500/30 transition-all"
      >
        {isMainnet ? "⚠️ Switch to BSC Mainnet" : "⚠️ Switch to BSC Testnet"}
      </motion.button>
    );
  }

  // Connected and correct network - show wallet info
  return (
    <div className="flex items-center gap-3">
      {/* Network Badge */}
      <div className={`hidden sm:flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium ${
        isMainnet 
          ? "bg-green-500/20 text-green-400 border border-green-500/30" 
          : "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
      }`}>
        <div className={`w-1.5 h-1.5 rounded-full ${isMainnet ? "bg-green-400" : "bg-yellow-400"}`} />
        {isMainnet ? "Mainnet" : "Testnet"}
      </div>

      {/* Balances */}
      <div className="hidden md:flex items-center gap-4 px-4 py-2 bg-zinc-800/50 rounded-lg border border-zinc-700">
        <div className="text-sm">
          <span className="text-zinc-400">TST:</span>{" "}
          <span className="text-amber-400 font-mono">
            {tstBalance ? parseFloat(tstBalance.formatted).toLocaleString() : "0"}
          </span>
        </div>
        <div className="w-px h-4 bg-zinc-700" />
        <div className="text-sm">
          <span className="text-zinc-400">BNB:</span>{" "}
          <span className="text-white font-mono">
            {parseFloat(bnbBalance).toFixed(4)}
          </span>
        </div>
        <button
          onClick={refreshBalances}
          className="text-zinc-400 hover:text-white transition-colors"
          title="Refresh balances"
        >
          <RefreshCw className="w-3 h-3" />
        </button>
      </div>

      {/* Wallet Address Dropdown */}
      <div className="relative group">
        <button className="flex items-center gap-2 px-4 py-2 bg-zinc-800 rounded-lg border border-zinc-700 hover:border-amber-500/50 transition-all">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="font-mono text-sm">{shortenedAddress}</span>
        </button>

        {/* Dropdown Menu */}
        <div className="absolute right-0 mt-2 w-48 py-2 bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
          <a
            href={explorerUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800 hover:text-white"
          >
            <ExternalLink className="w-4 h-4" />
            View on Explorer
          </a>
          <button
            onClick={addTokenToWallet}
            className="flex items-center gap-2 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800 hover:text-white w-full"
          >
            <Plus className="w-4 h-4" />
            Add TST to Wallet
          </button>
          <hr className="my-2 border-zinc-700" />
          <button
            onClick={disconnect}
            className="flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-zinc-800 w-full"
          >
            Disconnect
          </button>
        </div>
      </div>
    </div>
  );
}
