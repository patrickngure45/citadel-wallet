/**
 * Web3 Utilities
 * 
 * Helper functions to interact with the blockchain.
 * Uses ethers.js v6 for all blockchain operations.
 * Supports both BSC Testnet and Mainnet via environment toggle.
 */

import { ethers, BrowserProvider, JsonRpcProvider, Contract, formatUnits } from "ethers";
import { CONTRACTS, NETWORK, TST_ABI, ESCROW_ABI, TST_ESCROW_ABI, USE_MAINNET, getNetworkInfo } from "./contracts";

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
  token?: string; // "BNB" or "TST"
  createdAt: Date;
  completedAt: Date | null;
}

/**
 * Get Escrow contract instance with signer (for write operations)
 * Returns null if escrow not deployed on current network
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
 * Get TST Escrow contract instance (read-only)
 */
export function getTSTEscrowContract(provider?: JsonRpcProvider): Contract | null {
  if (!CONTRACTS.TST_ESCROW) return null;
  const p = provider || getReadOnlyProvider();
  return new Contract(CONTRACTS.TST_ESCROW, TST_ESCROW_ABI, p);
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
 * Create and fund a TST escrow agreement (Mainnet Compatible)
 * 1. Checks Allowance
 * 2. Approves if needed
 * 3. Calls createAndFund
 */
export async function createEscrowAgreement(
  payeeAddress: string,
  amount: string,
  description: string
): Promise<{ success: boolean; agreementId?: number; txHash?: string; error?: string }> {
  try {
    if (!isWalletInstalled()) return { success: false, error: "Wallet not connected" };
    
    // We use TST_ESCROW for everything now on Mainnet
    const contractAddress = CONTRACTS.TST_ESCROW;
    if (!contractAddress) return { success: false, error: "Escrow not available on this network" };

    const provider = new BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    
    // 1. Setup Contracts
    const tstToken = new Contract(CONTRACTS.TST_TOKEN, TST_ABI, signer);
    const escrow = new Contract(contractAddress, TST_ESCROW_ABI, signer);
    
    const amountWei = ethers.parseUnits(amount, 18);
    const userAddress = await signer.getAddress();

    // 2. Check Allowance
    // ABI must support allowance. TST_ABI usually does (ERC20 standard)
    // If TST_ABI in contracts.ts is minimal string array, ensure it has "allowance"
    try {
        const allowance = await tstToken.allowance(userAddress, contractAddress);
        if (allowance < amountWei) {
            console.log("Approving TST...");
            const approveTx = await tstToken.approve(contractAddress, amountWei);
            await approveTx.wait();
            console.log("Approved.");
        }
    } catch (e) {
        // Fallback: Just try to approve if allowance check fails (or if ABI missing)
        console.warn("Allowance check failed, blindly approving...", e);
        const approveTx = await tstToken.approve(contractAddress, amountWei);
        await approveTx.wait();
    }

    // 3. Create and Fund
    // function createAndFund(address payee, uint256 amount, string calldata description) returns (uint256)
    const tx = await escrow.createAndFund(payeeAddress, amountWei, description);
    
    console.log("Transaction sent:", tx.hash);
    const receipt = await tx.wait();
    
    // 4. Find Agreement ID from logs
    // Event: AgreementCreated(uint256 indexed agreementId, ...)
    let agreementId = 0;
    
    // Parse logs
    // This is a bit tricky with ethers v6, but usually receipt.logs has it.
    // For now, we return success and the TX hash. The frontend can optimize ID retrieval if needed.
    // Ideally we parse the event topics.
    
    try {
        // Try to decode if we can, otherwise return 0
        // Topic 0 is event signature
        // agreementId is indexed param 1 (topics[1])
        for (const log of receipt.logs) {
            // We assume the first log or one of them is AgreementCreated
            // TSTEscrow AgreementCreated topic[1] is agreementId
            if (log.topics && log.topics[1]) {
                agreementId = parseInt(log.topics[1], 16);
            }
        }
    } catch (e) { console.warn("Could not parse ID", e); }
    
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
 * Supports both BNB Only (legacy) and TST Escrow based on token type
 */
export async function releaseEscrowFunds(
  agreementId: number,
  isTst = false
): Promise<{ success: boolean; txHash?: string; error?: string }> {
  try {
    // Determine which contract to use
    let contractAddress = isTst ? CONTRACTS.TST_ESCROW : CONTRACTS.ESCROW;
    let abi = isTst ? TST_ESCROW_ABI : ESCROW_ABI;
    
    if (!contractAddress) return { success: false, error: "Escrow unavailable" };
    
    if (!isWalletInstalled()) return { success: false, error: "Wallet not connected" };

    const provider = new BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    const escrow = new Contract(contractAddress, abi, signer);
    
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
 * Fetches from BOTH Native Escrow and TST Escrow contracts
 */
export async function getUserEscrowAgreements(userAddress: string): Promise<EscrowAgreement[]> {
  const agreements: EscrowAgreement[] = [];
  const provider = getReadOnlyProvider();
  
  // 1. Fetch NATIVE (BNB) Agreements
  if (CONTRACTS.ESCROW) {
    try {
      const bnbEscrow = new Contract(CONTRACTS.ESCROW, ESCROW_ABI, provider);
      const eventFilter = bnbEscrow.filters.AgreementCreated();
      const currentBlock = await provider.getBlockNumber();
      const fromBlock = currentBlock - 10000; 

      const events = await bnbEscrow.queryFilter(eventFilter, fromBlock);
      
      for (const event of events) {
        if ('args' in event) {
          const id = Number(event.args[0]);
          const payer = String(event.args[1]);
          const payee = String(event.args[2]);
          const amount = event.args[3];
          
          if (payer.toLowerCase() === userAddress.toLowerCase() || 
              payee.toLowerCase() === userAddress.toLowerCase()) {
              try {
                  const details = await bnbEscrow.agreements(id);
                  const isActive = details[3];
                  
                  agreements.push({
                    id: id,
                    payer,
                    payee,
                    amount: formatUnits(amount, 18),
                    description: `Agreement #${id}`,
                    status: isActive ? 1 : 2,
                    token: "BNB",
                    createdAt: new Date(), 
                    completedAt: isActive ? null : new Date() 
                  });
              } catch (e) { console.warn(`Failed fetch BNB agr ${id}`, e); }
          }
        }
      }
    } catch (e) { console.error("BNB Escrow fetch error", e); }
  }

  // 2. Fetch TST Agreements
  if (CONTRACTS.TST_ESCROW) {
      try {
        const tstEscrow = new Contract(CONTRACTS.TST_ESCROW, TST_ESCROW_ABI, provider);
        const eventFilter = tstEscrow.filters.AgreementCreated();
        const currentBlock = await provider.getBlockNumber();
        const fromBlock = currentBlock - 10000; 

        const events = await tstEscrow.queryFilter(eventFilter, fromBlock);
        
        for (const event of events) {
          if ('args' in event) {
            const id = Number(event.args[0]);
            const payer = String(event.args[1]);
            const payee = String(event.args[2]);
            const amount = event.args[3];
            const description = String(event.args[4]);
            
            if (payer.toLowerCase() === userAddress.toLowerCase() || 
                payee.toLowerCase() === userAddress.toLowerCase()) {
                
                try {
                    const details = await tstEscrow.agreements(id);
                    // struct Agreement { payer, payee, amount, description, status, ... }
                    // status is index 4 (0-based) in struct ABI often, but ethers returns object or array
                    // Check ABI: returns (address payer, address payee, uint256 amount, string description, uint8 status, ...)
                    
                    const status = Number(details[4]); // 0=Created, 1=Funded, 2=Released

                    agreements.push({
                      id: id,
                      payer,
                      payee,
                      amount: formatUnits(amount, 18),
                      description: description || `TST Agreement #${id}`,
                      status: status,
                      token: "TST",
                      createdAt: new Date(Number(details[5]) * 1000), 
                      completedAt: Number(details[6]) > 0 ? new Date(Number(details[6]) * 1000) : null
                    });
                } catch (e) { console.warn(`Failed fetch TST agr ${id}`, e); }
            }
          }
        }
      } catch (e) { console.error("TST Escrow fetch error", e); }
  }
    
  // Sort by ID descending (rough proxy for time)
  return agreements.sort((a, b) => b.id - a.id);
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
