/**
 * useWeb3 Hook
 * 
 * React hook for blockchain interactions.
 * Handles wallet connection, balances, and contract calls.
 * Supports both BSC Testnet and Mainnet.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  connectWallet,
  switchToCorrectNetwork,
  getTSTBalance,
  getBNBBalance,
  addTSTToWallet,
  isWalletInstalled,
  shortenAddress,
  getNetworkInfo,
  USE_MAINNET,
  TokenBalance,
} from "@/lib/web3";
import { NETWORK, CONTRACTS } from "@/lib/contracts";

interface UseWeb3Return {
  // State
  address: string | null;
  isConnected: boolean;
  isCorrectNetwork: boolean;
  isLoading: boolean;
  isMainnet: boolean;
  
  // Network Info
  networkName: string;
  
  // Balances
  tstBalance: TokenBalance | null;
  bnbBalance: string;
  
  // Actions
  connect: () => Promise<void>;
  disconnect: () => void;
  switchNetwork: () => Promise<void>;
  addTokenToWallet: () => Promise<void>;
  refreshBalances: () => Promise<void>;
  
  // Helpers
  shortenedAddress: string;
  explorerUrl: string;
}

export function useWeb3(): UseWeb3Return {
  const [address, setAddress] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [tstBalance, setTstBalance] = useState<TokenBalance | null>(null);
  const [bnbBalance, setBnbBalance] = useState("0");

  const isConnected = !!address;
  const isCorrectNetwork = chainId === NETWORK.chainId;

  // Fetch balances
  const refreshBalances = useCallback(async () => {
    if (!address) return;
    
    try {
      const [tst, bnb] = await Promise.all([
        getTSTBalance(address),
        getBNBBalance(address),
      ]);
      setTstBalance(tst);
      setBnbBalance(bnb);
    } catch (error) {
      console.error("Failed to fetch balances:", error);
    }
  }, [address]);

  // Connect wallet
  const connect = async () => {
    setIsLoading(true);
    try {
      const addr = await connectWallet();
      if (addr) {
        setAddress(addr);
        // Get chain ID
        const chainIdHex = await window.ethereum.request({ method: "eth_chainId" });
        setChainId(parseInt(chainIdHex, 16));
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Disconnect
  const disconnect = () => {
    setAddress(null);
    setChainId(null);
    setTstBalance(null);
    setBnbBalance("0");
  };

  // Switch to correct network
  const switchNetwork = async () => {
    setIsLoading(true);
    try {
      await switchToCorrectNetwork();
      setChainId(NETWORK.chainId);
    } finally {
      setIsLoading(false);
    }
  };

  // Add TST token to wallet
  const addTokenToWallet = async () => {
    await addTSTToWallet();
  };

  // Listen for account/chain changes
  useEffect(() => {
    if (!isWalletInstalled()) return;

    const handleAccountsChanged = (accounts: string[]) => {
      if (accounts.length === 0) {
        disconnect();
      } else {
        setAddress(accounts[0]);
      }
    };

    const handleChainChanged = (chainIdHex: string) => {
      setChainId(parseInt(chainIdHex, 16));
    };

    window.ethereum.on("accountsChanged", handleAccountsChanged);
    window.ethereum.on("chainChanged", handleChainChanged);

    return () => {
      window.ethereum.removeListener("accountsChanged", handleAccountsChanged);
      window.ethereum.removeListener("chainChanged", handleChainChanged);
    };
  }, []);

  // Fetch balances when address or network changes
  useEffect(() => {
    if (address && isCorrectNetwork) {
      refreshBalances();
    }
  }, [address, isCorrectNetwork, refreshBalances]);

  return {
    address,
    isConnected,
    isCorrectNetwork,
    isLoading,
    isMainnet: USE_MAINNET,
    networkName: NETWORK.name,
    tstBalance,
    bnbBalance,
    connect,
    disconnect,
    switchNetwork,
    addTokenToWallet,
    refreshBalances,
    shortenedAddress: address ? shortenAddress(address) : "",
    explorerUrl: address ? `${NETWORK.explorer}/address/${address}` : "",
  };
}
