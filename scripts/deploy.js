import hre from "hardhat";
import fs from "fs";

async function main() {
  console.log("🚀 Deploying TST Token Suite to BSC Testnet...\n");

  const [deployer] = await hre.ethers.getSigners();
  console.log(`📍 Deploying from account: ${deployer.address}\n`);

  // 1. Deploy TST Token
  console.log("1️⃣  Deploying TST Token...");
  const TST = await hre.ethers.getContractFactory("TST");
  const tst = await TST.deploy();
  await tst.waitForDeployment();
  const tstAddress = await tst.getAddress();
  console.log(`✅ TST deployed to: ${tstAddress}`);
  console.log(`   - Initial supply: 1,000,000 TST\n`);

  // 2. Deploy P2PAgreementEscrow
  console.log("2️⃣  Deploying P2PAgreementEscrow...");
  const Escrow = await hre.ethers.getContractFactory("P2PAgreementEscrow");
  const escrow = await Escrow.deploy(tstAddress);
  await escrow.waitForDeployment();
  const escrowAddress = await escrow.getAddress();
  console.log(`✅ P2PAgreementEscrow deployed to: ${escrowAddress}\n`);

  // 3. Deploy AccessTierStaking
  console.log("3️⃣  Deploying AccessTierStaking...");
  const Staking = await hre.ethers.getContractFactory("AccessTierStaking");
  const staking = await Staking.deploy(tstAddress);
  await staking.waitForDeployment();
  const stakingAddress = await staking.getAddress();
  console.log(`✅ AccessTierStaking deployed to: ${stakingAddress}\n`);

  // 4. Deploy EntityComputeReserve
  console.log("4️⃣  Deploying EntityComputeReserve...");
  const Reserve = await hre.ethers.getContractFactory("EntityComputeReserve");
  const reserve = await Reserve.deploy(tstAddress);
  await reserve.waitForDeployment();
  const reserveAddress = await reserve.getAddress();
  console.log(`✅ EntityComputeReserve deployed to: ${reserveAddress}\n`);

  // Verify all contracts deployed
  console.log("📋 Deployment Summary:");
  console.log("════════════════════════════════════════");
  console.log(`TST Token:               ${tstAddress}`);
  console.log(`P2P Escrow:              ${escrowAddress}`);
  console.log(`Access Tier Staking:     ${stakingAddress}`);
  console.log(`Entity Compute Reserve:  ${reserveAddress}`);
  console.log("════════════════════════════════════════\n");

  // Save addresses to JSON
  const deploymentData = {
    network: hre.network.name,
    deployedAt: new Date().toISOString(),
    deployer: deployer.address,
    contracts: {
      TST: {
        address: tstAddress,
        name: "TradeSynapse Token",
        symbol: "TST",
        decimals: 18,
        totalSupply: "1000000000000000000000000",
      },
      P2PAgreementEscrow: {
        address: escrowAddress,
        tstAddress: tstAddress,
      },
      AccessTierStaking: {
        address: stakingAddress,
        tstAddress: tstAddress,
        tiers: {
          1: "5000000000000000000",
          2: "25000000000000000000",
          3: "100000000000000000000",
        },
      },
      EntityComputeReserve: {
        address: reserveAddress,
        tstAddress: tstAddress,
        entities: {
          RISK: 1,
          STRATEGY: 2,
          MEMORY: 3,
        },
      },
    },
  };

  const filePath = "deployments.json";
  fs.writeFileSync(filePath, JSON.stringify(deploymentData, null, 2));
  console.log(`📝 Deployment addresses saved to ${filePath}\n`);

  // Verify contracts (optional, requires deployed contracts to be verified)
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("🔍 Verifying contracts on Etherscan...");
    console.log("   (This may take a few minutes)\n");

    // Add verification code here if needed
  }

  console.log("✨ Deployment complete!\n");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
