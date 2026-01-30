/**
 * Web3 Utilities
 * 
 * Helper functions to interact with the blockchain.
 * Uses ethers.js v6 for all blockchain operations.
 * Supports both BSC Testnet and Mainnet via environment toggle.
 */

import { ethers, BrowserProvider, JsonRpcProvider, Contract, formatUnits } from "ethers";
import { CONTRACTS, NETWORK, TST_ABI, ESCROW_ABI, USE_MAINNET, getNetworkInfo } from "./contracts";

// Types
export interface WalletState {
  address: string | null;
  isConnected: boolean;
  chainId: number | null;
}

export interface TokenBalance {
  raw: bigint;
  formatted: string;
  symbol: string;
}

/**
 * Get a read-only provider (no wallet needed)
 * Use this to READ data from the blockchain
 */
export function getReadOnlyProvider(): JsonRpcProvider {
  return new JsonRpcProvider(NETWORK.rpcUrl);
}

/**
 * Get TST Token contract instance (read-only)
 */
export function getTSTContract(provider?: JsonRpcProvider): Contract {
  const p = provider || getReadOnlyProvider();
  return new Contract(CONTRACTS.TST_TOKEN, TST_ABI, p);
}

/**
 * Get Escrow contract instance (read-only)
 * Returns null if escrow not deployed on current network
 */
export function getEscrowContract(provider?: JsonRpcProvider): Contract | null {
  if (!CONTRACTS.ESCROW) {
    console.warn("Escrow contract not deployed on", NETWORK.name);
    return null;
  }
  const p = provider || getReadOnlyProvider();
  return new Contract(CONTRACTS.ESCROW, ESCROW_ABI, p);
}

/**
 * Get TST balance for any address
 * No wallet connection needed - just reads from blockchain
 */
export async function getTSTBalance(address: string): Promise<TokenBalance> {
  try {
    const contract = getTSTContract();
    const balance = await contract.balanceOf(address);
    const decimals = await contract.decimals();
    const symbol = await contract.symbol();
    
    return {
      raw: balance,
      formatted: formatUnits(balance, decimals),
      symbol,
    };
  } catch (error) {
    console.error("Error fetching TST balance:", error);
    return { raw: BigInt(0), formatted: "0", symbol: "TST" };
  }
}

/**
 * Get native BNB balance for any address
 */
export async function getBNBBalance(address: string): Promise<string> {
  try {
    const provider = getReadOnlyProvider();
    const balance = await provider.getBalance(address);
    return formatUnits(balance, 18);
  } catch (error) {
    console.error("Error fetching BNB balance:", error);
    return "0";
  }
}

/**
 * Check if MetaMask (or other wallet) is installed
 */
export function isWalletInstalled(): boolean {
  return typeof window !== "undefined" && typeof window.ethereum !== "undefined";
}

/**
 * Connect to user's wallet (MetaMask, etc.)
 * Returns the connected address with timeout protection
 */
export async function connectWallet(): Promise<string | null> {
  if (!isWalletInstalled()) {
    alert("Please install MetaMask to connect your wallet!");
    return null;
  }

  try {
    // Create a timeout promise
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error("Connection timeout - please check MetaMask")), 30000);
    });

    // Race between connection and timeout
    const accounts = await Promise.race([
      window.ethereum.request({ method: "eth_requestAccounts" }),
      timeoutPromise,
    ]) as string[];
    
    return accounts[0] || null;
  } catch (error: any) {
    if (error.message?.includes("timeout")) {
      alert("Connection timed out. Please open MetaMask and try again.");
    } else if (error.code === 4001) {
      // User rejected the request
      console.log("User rejected connection");
    } else {
      console.error("Failed to connect wallet:", error);
    }
    return null;
  }
}

/**
 * Switch to the correct BSC network (Testnet or Mainnet based on config)
 */
export async function switchToCorrectNetwork(): Promise<boolean> {
  if (!isWalletInstalled()) return false;

  try {
    await window.ethereum.request({
      method: "wallet_switchEthereumChain",
      params: [{ chainId: `0x${NETWORK.chainId.toString(16)}` }],
    });
    return true;
  } catch (switchError: any) {
    // Network not added yet, let's add it
    if (switchError.code === 4902) {
      try {
        await window.ethereum.request({
          method: "wallet_addEthereumChain",
          params: [{
            chainId: `0x${NETWORK.chainId.toString(16)}`,
            chainName: NETWORK.name,
            nativeCurrency: NETWORK.currency,
            rpcUrls: [NETWORK.rpcUrl],
            blockExplorerUrls: [NETWORK.explorer],
          }],
        });
        return true;
      } catch (addError) {
        console.error("Failed to add network:", addError);
        return false;
      }
    }
    console.error("Failed to switch network:", switchError);
    return false;
  }
}

// Alias for backward compatibility
export const switchToBSCTestnet = switchToCorrectNetwork;

/**
 * Add TST token to MetaMask
 */
export async function addTSTToWallet(): Promise<boolean> {
  if (!isWalletInstalled()) return false;

  try {
    await window.ethereum.request({
      method: "wallet_watchAsset",
      params: {
        type: "ERC20",
        options: {
          address: CONTRACTS.TST_TOKEN,
          symbol: "TST",
          decimals: 18,
          // image: "https://your-token-logo.png", // Optional
        },
      },
    });
    return true;
  } catch (error) {
    console.error("Failed to add token:", error);
    return false;
  }
}

/**
 * Transfer TST tokens to another address
 * Requires connected wallet
 */
export async function transferTST(
  toAddress: string,
  amount: string
): Promise<{ success: boolean; txHash?: string; error?: string }> {
  if (!isWalletInstalled()) {
    return { success: false, error: "Wallet not installed" };
  }

  try {
    const provider = new BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    
    // Create contract instance with signer (for write operations)
    const contract = new Contract(CONTRACTS.TST_TOKEN, TST_ABI, signer);
    
    // Convert amount to wei (18 decimals)
    const amountWei = ethers.parseUnits(amount, 18);
    
    // Send transaction
    const tx = await contract.transfer(toAddress, amountWei);
    
    // Wait for confirmation
    const receipt = await tx.wait();
    
    return { success: true, txHash: receipt.hash };
  } catch (error: any) {
    console.error("Transfer failed:", error);
    
    if (error.code === 4001 || error.code === "ACTION_REJECTED") {
      return { success: false, error: "Transaction rejected by user" };
    }
    if (error.message?.includes("insufficient")) {
      return { success: false, error: "Insufficient balance" };
    }
    
    return { success: false, error: error.message || "Transfer failed" };
  }
}

/**
 * Get PancakeSwap URL for TST token
 */
export function getPancakeSwapUrl(): string {
  // PancakeSwap URL for the token on mainnet or testnet
  const baseUrl = USE_MAINNET 
    ? "https://pancakeswap.finance/swap"
    : "https://pancakeswap.finance/swap"; // Same URL, it auto-detects network
  
  return `${baseUrl}?outputCurrency=${CONTRACTS.TST_TOKEN}`;
}

// ═══════════════════════════════════════════════════════════════════
// ESCROW FUNCTIONS
// ═══════════════════════════════════════════════════════════════════

export interface EscrowAgreement {
  id: number;
  payer: string;
  payee: string;
  amount: string;
  description: string;
  status: number;
  createdAt: Date;
  completedAt: Date | null;
}

/**
 * Get Escrow contract instance with signer (for write operations)
 */
async function getEscrowContractWithSigner(): Promise<Contract | null> {
  if (!CONTRACTS.ESCROW) {
    console.warn("Escrow not deployed on", NETWORK.name);
    return null;
  }
  if (!isWalletInstalled()) return null;
  
  const provider = new BrowserProvider(window.ethereum);
  const signer = await provider.getSigner();
  return new Contract(CONTRACTS.ESCROW, ESCROW_ABI, signer);
}

/**
 * Approve escrow contract to spend TST tokens
 */
export async function approveEscrow(amount: string): Promise<{ success: boolean; error?: string }> {
  if (!CONTRACTS.ESCROW) {
    return { success: false, error: "Escrow not deployed on this network" };
  }
  
  try {
    const provider = new BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    const tstContract = new Contract(CONTRACTS.TST_TOKEN, TST_ABI, signer);
    
    const amountWei = ethers.parseUnits(amount, 18);
    const tx = await tstContract.approve(CONTRACTS.ESCROW, amountWei);
    await tx.wait();
    
    return { success: true };
  } catch (error: any) {
    console.error("Approve failed:", error);
    return { success: false, error: error.message || "Approval failed" };
  }
}

/**
 * Create and fund an escrow agreement in one transaction
 */
export async function createEscrowAgreement(
  payeeAddress: string,
  amount: string,
  description: string
): Promise<{ success: boolean; agreementId?: number; txHash?: string; error?: string }> {
  try {
    const escrow = await getEscrowContractWithSigner();
    if (!escrow) {
      return { success: false, error: "Escrow not available" };
    }
    
    // First approve the escrow to spend tokens
    const approveResult = await approveEscrow(amount);
    if (!approveResult.success) {
      return { success: false, error: approveResult.error };
    }
    
    // Create and fund the agreement
    const amountWei = ethers.parseUnits(amount, 18);
    const tx = await escrow.createAndFund(payeeAddress, amountWei, description);
    const receipt = await tx.wait();
    
    // Get agreement ID from event
    const event = receipt.logs.find((log: any) => {
      try {
        const parsed = escrow.interface.parseLog(log);
        return parsed?.name === "AgreementCreated";
      } catch { return false; }
    });
    
    let agreementId = 0;
    if (event) {
      const parsed = escrow.interface.parseLog(event);
      agreementId = Number(parsed?.args[0]);
    }
    
    return { success: true, agreementId, txHash: receipt.hash };
  } catch (error: any) {
    console.error("Create escrow failed:", error);
    if (error.code === 4001 || error.code === "ACTION_REJECTED") {
      return { success: false, error: "Transaction rejected" };
    }
    return { success: false, error: error.message || "Failed to create agreement" };
  }
}

/**
 * Release funds from escrow to payee
 */
export async function releaseEscrowFunds(
  agreementId: number
): Promise<{ success: boolean; txHash?: string; error?: string }> {
  try {
    const escrow = await getEscrowContractWithSigner();
    if (!escrow) {
      return { success: false, error: "Escrow not available" };
    }
    
    const tx = await escrow.releaseFunds(agreementId);
    const receipt = await tx.wait();
    
    return { success: true, txHash: receipt.hash };
  } catch (error: any) {
    console.error("Release failed:", error);
    return { success: false, error: error.message || "Failed to release funds" };
  }
}

/**
 * Get user's escrow agreements
 */
export async function getUserEscrowAgreements(userAddress: string): Promise<EscrowAgreement[]> {
  if (!CONTRACTS.ESCROW) return [];
  
  try {
    const provider = getReadOnlyProvider();
    const escrow = new Contract(CONTRACTS.ESCROW, ESCROW_ABI, provider);
    
    const agreementIds = await escrow.getUserAgreements(userAddress);
    const agreements: EscrowAgreement[] = [];
    
    for (const id of agreementIds) {
      const [payer, payee, amount, description, status, createdAt, completedAt] = 
        await escrow.getAgreement(id);
      
      agreements.push({
        id: Number(id),
        payer,
        payee,
        amount: formatUnits(amount, 18),
        description,
        status: Number(status),
        createdAt: new Date(Number(createdAt) * 1000),
        completedAt: completedAt > 0 ? new Date(Number(completedAt) * 1000) : null,
      });
    }
    
    return agreements;
  } catch (error) {
    console.error("Failed to fetch agreements:", error);
    return [];
  }
}

/**
 * Shorten address for display
 * 0x1234...5678
 */
export function shortenAddress(address: string): string {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

/**
 * Get current network info for display
 */
export { getNetworkInfo, USE_MAINNET };

// TypeScript declaration for window.ethereum
declare global {
  interface Window {
    ethereum?: any;
  }
}
