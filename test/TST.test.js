import { expect } from "chai";
import { ethers } from "hardhat";

describe("TST Token", function () {
  let tst;
  let owner, user1, user2;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    const TST = await ethers.getContractFactory("TST");
    tst = await TST.deploy();
    await tst.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should mint 1M TST to owner", async function () {
      const balance = await tst.balanceOf(owner.address);
      expect(balance).to.equal(ethers.parseEther("1000000"));
    });

    it("Should have correct name and symbol", async function () {
      expect(await tst.name()).to.equal("TradeSynapse Token");
      expect(await tst.symbol()).to.equal("TST");
    });

    it("Should have correct total supply", async function () {
      const supply = await tst.totalSupply();
      expect(supply).to.equal(ethers.parseEther("1000000"));
    });
  });

  describe("Locking", function () {
    it("Should record lock for user", async function () {
      const amount = ethers.parseEther("100");
      const lockId = ethers.id("lock-1");

      // Transfer TST to user1
      await tst.connect(owner).transfer(user1.address, amount);
      
      // Mock: user1 has TST, now try to lock
      // Note: In real scenario, recordLock would be called by escrow contract
      await expect(tst.connect(user1).recordLock(amount, lockId))
        .to.emit(tst, "TokensLocked");

      const lockedBalance = await tst.lockedBalance(user1.address);
      expect(lockedBalance).to.equal(amount);
    });

    it("Should prevent transfer when locked", async function () {
      const amount = ethers.parseEther("100");
      const lockId = ethers.id("lock-1");

      await expect(
        tst.connect(owner).transfer(user1.address, amount)
      ).to.be.revertedWith("TST: Transfer disabled");
    });

    it("Should release locked TST", async function () {
      const amount = ethers.parseEther("100");
      const lockId = ethers.id("lock-1");

      // Manually set up lock (in real scenario, escrow does this)
      await tst.connect(user1).recordLock(amount, lockId);
      let lockedBalance = await tst.lockedBalance(user1.address);
      expect(lockedBalance).to.equal(0); // user1 has no balance initially

      // Give user1 some TST first
      await tst.connect(owner).transfer(user1.address, amount);
      await tst.connect(user1).recordLock(amount, lockId);

      lockedBalance = await tst.lockedBalance(user1.address);
      expect(lockedBalance).to.equal(amount);

      // Release lock
      await tst.connect(user1).releaseLock(amount, lockId);
      lockedBalance = await tst.lockedBalance(user1.address);
      expect(lockedBalance).to.equal(0);
    });
  });

  describe("Staking", function () {
    it("Should record stake for user", async function () {
      const amount = ethers.parseEther("5");

      // Give user1 some TST
      await tst.connect(owner).transfer(user1.address, amount);

      // Record stake
      await expect(tst.connect(user1).recordStake(amount, 1))
        .to.emit(tst, "TokensStaked");

      const stakedBalance = await tst.stakedBalance(user1.address);
      expect(stakedBalance).to.equal(amount);
    });

    it("Should prevent invalid tier", async function () {
      const amount = ethers.parseEther("5");
      await tst.connect(owner).transfer(user1.address, amount);

      await expect(
        tst.connect(user1).recordStake(amount, 4)
      ).to.be.revertedWith("Invalid tier");
    });

    it("Should unstake TST", async function () {
      const amount = ethers.parseEther("5");

      await tst.connect(owner).transfer(user1.address, amount);
      await tst.connect(user1).recordStake(amount, 1);

      let stakedBalance = await tst.stakedBalance(user1.address);
      expect(stakedBalance).to.equal(amount);

      await tst.connect(user1).recordUnstake(amount);
      stakedBalance = await tst.stakedBalance(user1.address);
      expect(stakedBalance).to.equal(0);
    });
  });

  describe("Available Balance", function () {
    it("Should calculate available balance correctly", async function () {
      const total = ethers.parseEther("100");
      const locked = ethers.parseEther("30");
      const staked = ethers.parseEther("20");

      await tst.connect(owner).transfer(user1.address, total);

      const lockId = ethers.id("lock-1");
      await tst.connect(user1).recordLock(locked, lockId);
      await tst.connect(user1).recordStake(staked, 1);

      const available = await tst.getAvailableBalance(user1.address);
      expect(available).to.equal(ethers.parseEther("50"));
    });

    it("Should verify available balance requirement", async function () {
      const amount = ethers.parseEther("100");
      const required = ethers.parseEther("50");

      await tst.connect(owner).transfer(user1.address, amount);

      const hasBalance = await tst.hasAvailableBalance(user1.address, required);
      expect(hasBalance).to.be.true;

      const lockId = ethers.id("lock-1");
      await tst.connect(user1).recordLock(ethers.parseEther("60"), lockId);

      const hasBalanceAfter = await tst.hasAvailableBalance(user1.address, required);
      expect(hasBalanceAfter).to.be.false;
    });
  });

  describe("Transfer Restrictions", function () {
    it("Should block transfer", async function () {
      await expect(
        tst.connect(owner).transfer(user1.address, ethers.parseEther("100"))
      ).to.be.revertedWith("TST: Transfer disabled");
    });

    it("Should block transferFrom", async function () {
      await expect(
        tst.connect(owner).transferFrom(owner.address, user1.address, ethers.parseEther("100"))
      ).to.be.revertedWith("TST: Transfer disabled");
    });

    it("Should block approve", async function () {
      await expect(
        tst.connect(owner).approve(user1.address, ethers.parseEther("100"))
      ).to.be.revertedWith("TST: Approve disabled");
    });
  });
});
