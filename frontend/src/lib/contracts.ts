/**
 * Smart Contract Configuration & ABIs
 * 
 * Supports BOTH BSC Testnet and BSC Mainnet.
 * Toggle via NEXT_PUBLIC_USE_MAINNET environment variable.
 */

// ═══════════════════════════════════════════════════════════════════
// NETWORK CONFIGURATION
// ═══════════════════════════════════════════════════════════════════

// Check if we should use mainnet (default: false = testnet)
export const USE_MAINNET = process.env.NEXT_PUBLIC_USE_MAINNET === "true";

// Network Definitions
const NETWORKS = {
  mainnet: {
    chainId: 56,
    name: "BNB Smart Chain",
    rpcUrl: "https://bsc-dataseed1.binance.org",
    explorer: "https://bscscan.com",
    currency: {
      name: "BNB",
      symbol: "BNB",
      decimals: 18,
    },
  },
  testnet: {
    chainId: 97,
    name: "BSC Testnet",
    rpcUrl: "https://data-seed-prebsc-1-s1.binance.org:8545/",
    explorer: "https://testnet.bscscan.com",
    currency: {
      name: "Test BNB",
      symbol: "tBNB",
      decimals: 18,
    },
  },
};

// Contract Addresses per Network
const CONTRACT_ADDRESSES = {
  mainnet: {
    // Your EXISTING mainnet TST token (TradeSynapse Token)
    TST_TOKEN: "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71",
    TST_ORACLE: "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5",
    // TSTEscrow contract on mainnet
    ESCROW: "0xEd6C769f17d6462A5DB87395a9Ae30A274afAE49", // Native BNB Escrow
    TST_ESCROW: "0x922bA3bD7866F92F0Caa2A544bb303A38922fb12", 
  },
  testnet: {
    // Testnet deployments (for development)
    TST_TOKEN: "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5",
    TST_ORACLE: null as string | null,
    ESCROW: "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71", // Native BNB Escrow
    TST_ESCROW: "0x922bA3bD7866F92F0Caa2A544bb303A38922fb12", // TST Token Escrow
  },
};

// ═══════════════════════════════════════════════════════════════════
// EXPORTS - Use these in your app
// ═══════════════════════════════════════════════════════════════════

// Active Network Configuration
export const NETWORK = USE_MAINNET ? NETWORKS.mainnet : NETWORKS.testnet;

// Active Contract Addresses
export const CONTRACTS = USE_MAINNET ? CONTRACT_ADDRESSES.mainnet : {
    ...CONTRACT_ADDRESSES.testnet,
    // Fallback if TST_ESCROW is missing in testnet config above
    TST_ESCROW: "0x922bA3bD7866F92F0Caa2A544bb303A38922fb12"
};

// Helper to check network status
export const getNetworkInfo = () => ({
  isMainnet: USE_MAINNET,
  networkName: NETWORK.name,
  chainId: NETWORK.chainId,
  explorer: NETWORK.explorer,
  tstAddress: CONTRACTS.TST_TOKEN,
});

// ═══════════════════════════════════════════════════════════════════
// ABIs (Same for both networks)
// ═══════════════════════════════════════════════════════════════════

// TST Token ABI (ERC20 Standard Functions)
// This tells the frontend how to call token functions
export const TST_ABI = [
  // Read Functions
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address account) view returns (uint256)",
  "function allowance(address owner, address spender) view returns (uint256)",
  
  // Write Functions
  "function transfer(address to, uint256 amount) returns (bool)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function transferFrom(address from, address to, uint256 amount) returns (bool)",
  
  // Events
  "event Transfer(address indexed from, address indexed to, uint256 value)",
  "event Approval(address indexed owner, address indexed spender, uint256 value)",
];

// TST Escrow Contract ABI (for P2P agreements)
export const ESCROW_ABI = [
  // Read Functions
  "function agreements(uint256) view returns (address payer, address payee, uint256 amount, bool isActive)",
  
  // Write Functions
  "function createAgreement(uint256 agreementId, address payee) payable",
  "function releaseFunds(uint256 agreementId)",
  "function refundPayer(uint256 agreementId)",
  
  // Events
  "event AgreementCreated(uint256 indexed agreementId, address indexed payer, address indexed payee, uint256 amount)",
  "event FundsReleased(uint256 indexed agreementId, address indexed payee, uint256 amount)",
  "event FundsRefunded(uint256 indexed agreementId, address indexed payer, uint256 amount)",
];

export const TST_ESCROW_ABI = [
  // Read
  "function agreements(uint256) view returns (address payer, address payee, uint256 amount, string description, uint8 status, uint256 createdAt, uint256 completedAt)",
  "function userAgreements(address, uint256) view returns (uint256)", 
  
  // Write
  "function createAndFund(address payee, uint256 amount, string description) returns (uint256)",
  "function releaseFunds(uint256 agreementId)",
  
  // Events
  "event AgreementCreated(uint256 indexed agreementId, address indexed payer, address indexed payee, uint256 amount, string description)",
  "event FundsReleased(uint256 indexed agreementId, address indexed payee, uint256 amount)",
];


// Agreement Status Enum (matches Solidity contract)
export const AGREEMENT_STATUS = {
  0: "Created",
  1: "Funded",
  2: "Released",
  3: "Refunded",
  4: "Cancelled",
} as const;

export type AgreementStatusType = keyof typeof AGREEMENT_STATUS;
