import { expect } from "chai";
import { ethers } from "hardhat";
import { time } from "@nomicfoundation/hardhat-network-helpers";

describe("AccessTierStaking", function () {
  let tst, staking;
  let owner, user1, user2;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    // Deploy TST
    const TST = await ethers.getContractFactory("TST");
    tst = await TST.deploy();
    await tst.waitForDeployment();

    // Deploy Staking
    const Staking = await ethers.getContractFactory("AccessTierStaking");
    staking = await Staking.deploy(await tst.getAddress());
    await staking.waitForDeployment();

    // Transfer TST to users
    await tst.connect(owner).transfer(user1.address, ethers.parseEther("1000"));
    await tst.connect(owner).transfer(user2.address, ethers.parseEther("1000"));
  });

  describe("Stake For Tier", function () {
    it("Should stake for Tier 1", async function () {
      const tx = await staking.connect(user1).stakeForTier(1);
      await expect(tx).to.emit(staking, "Staked");

      const stakes = await staking.getStakesByUser(user1.address);
      expect(stakes.length).to.equal(1);
    });

    it("Should stake for Tier 2", async function () {
      const tx = await staking.connect(user1).stakeForTier(2);
      await expect(tx).to.emit(staking, "Staked");

      const stakes = await staking.getStakesByUser(user1.address);
      expect(stakes.length).to.equal(1);
    });

    it("Should stake for Tier 3", async function () {
      const tx = await staking.connect(user1).stakeForTier(3);
      await expect(tx).to.emit(staking, "Staked");

      const stakes = await staking.getStakesByUser(user1.address);
      expect(stakes.length).to.equal(1);
    });

    it("Should prevent invalid tier", async function () {
      await expect(staking.connect(user1).stakeForTier(4)).to.be.revertedWith(
        "Invalid tier"
      );
    });

    it("Should prevent staking without balance", async function () {
      const user3 = await ethers.provider.getSigner(3);

      await expect(staking.connect(user3).stakeForTier(1)).to.be.revertedWith(
        "Insufficient TST balance"
      );
    });
  });

  describe("Unstake", function () {
    it("Should unstake after 30 days", async function () {
      const stakeId = (await staking.connect(user1).stakeForTier(1)).wait();

      const stakes = await staking.getStakesByUser(user1.address);
      const sID = stakes[0];

      // Wait 30 days
      await time.increase(30 * 24 * 60 * 60 + 1);

      const tx = await staking.connect(user1).unstake(sID);
      await expect(tx).to.emit(staking, "Unstaked");
    });

    it("Should prevent unstaking before 30 days", async function () {
      await staking.connect(user1).stakeForTier(1);

      const stakes = await staking.getStakesByUser(user1.address);
      const sID = stakes[0];

      await expect(
        staking.connect(user1).unstake(sID)
      ).to.be.revertedWith("30-day period not complete");
    });

    it("Should prevent double unstake", async function () {
      await staking.connect(user1).stakeForTier(1);

      const stakes = await staking.getStakesByUser(user1.address);
      const sID = stakes[0];

      await time.increase(30 * 24 * 60 * 60 + 1);

      await staking.connect(user1).unstake(sID);

      await expect(
        staking.connect(user1).unstake(sID)
      ).to.be.revertedWith("Stake already unstaked");
    });

    it("Should prevent unstaking by non-owner", async function () {
      await staking.connect(user1).stakeForTier(1);

      const stakes = await staking.getStakesByUser(user1.address);
      const sID = stakes[0];

      await time.increase(30 * 24 * 60 * 60 + 1);

      await expect(
        staking.connect(user2).unstake(sID)
      ).to.be.revertedWith("Only stake owner can unstake");
    });
  });

  describe("Check Active Tier", function () {
    it("Should verify active Tier 1", async function () {
      await staking.connect(user1).stakeForTier(1);

      const hasTier1 = await staking.hasActiveTier(user1.address, 1);
      expect(hasTier1).to.be.true;
    });

    it("Should verify higher tier qualifies for lower tier", async function () {
      await staking.connect(user1).stakeForTier(3);

      const hasTier1 = await staking.hasActiveTier(user1.address, 1);
      const hasTier2 = await staking.hasActiveTier(user1.address, 2);
      const hasTier3 = await staking.hasActiveTier(user1.address, 3);

      expect(hasTier1).to.be.true;
      expect(hasTier2).to.be.true;
      expect(hasTier3).to.be.true;
    });

    it("Should return false when no stake", async function () {
      const hasTier1 = await staking.hasActiveTier(user2.address, 1);
      expect(hasTier1).to.be.false;
    });

    it("Should return false after unstaking", async function () {
      await staking.connect(user1).stakeForTier(1);

      const stakes = await staking.getStakesByUser(user1.address);
      const sID = stakes[0];

      await time.increase(30 * 24 * 60 * 60 + 1);
      await staking.connect(user1).unstake(sID);

      const hasTier1 = await staking.hasActiveTier(user1.address, 1);
      expect(hasTier1).to.be.false;
    });
  });

  describe("Get Highest Tier", function () {
    it("Should return Tier 0 for no stake", async function () {
      const highest = await staking.getHighestActiveTier(user1.address);
      expect(highest).to.equal(0);
    });

    it("Should return highest tier", async function () {
      await staking.connect(user1).stakeForTier(2);

      const highest = await staking.getHighestActiveTier(user1.address);
      expect(highest).to.equal(2);
    });

    it("Should return multiple stakes' highest", async function () {
      await staking.connect(user1).stakeForTier(1);
      await staking.connect(user1).stakeForTier(3);

      const highest = await staking.getHighestActiveTier(user1.address);
      expect(highest).to.equal(3);
    });
  });

  describe("Tier Amounts", function () {
    it("Should return correct tier amounts", async function () {
      const tier1 = await staking.getTierAmount(1);
      const tier2 = await staking.getTierAmount(2);
      const tier3 = await staking.getTierAmount(3);

      expect(tier1).to.equal(ethers.parseEther("5"));
      expect(tier2).to.equal(ethers.parseEther("25"));
      expect(tier3).to.equal(ethers.parseEther("100"));
    });
  });

  describe("Query Stakes", function () {
    it("Should get all stakes", async function () {
      await staking.connect(user1).stakeForTier(1);
      await staking.connect(user2).stakeForTier(2);

      const allStakes = await staking.getAllStakes();
      expect(allStakes.length).to.equal(2);
    });

    it("Should get stakes by user", async function () {
      await staking.connect(user1).stakeForTier(1);
      await staking.connect(user1).stakeForTier(2);
      await staking.connect(user2).stakeForTier(3);

      const user1Stakes = await staking.getStakesByUser(user1.address);
      expect(user1Stakes.length).to.equal(2);

      const user2Stakes = await staking.getStakesByUser(user2.address);
      expect(user2Stakes.length).to.equal(1);
    });
  });
});
