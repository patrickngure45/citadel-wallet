import { expect } from "chai";
import { ethers } from "hardhat";
import { time } from "@nomicfoundation/hardhat-network-helpers";

describe("P2PAgreementEscrow", function () {
  let tst, escrow;
  let owner, user1, user2;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    // Deploy TST
    const TST = await ethers.getContractFactory("TST");
    tst = await TST.deploy();
    await tst.waitForDeployment();

    // Deploy Escrow
    const Escrow = await ethers.getContractFactory("P2PAgreementEscrow");
    escrow = await Escrow.deploy(await tst.getAddress());
    await escrow.waitForDeployment();

    // Transfer TST to users
    await tst.connect(owner).transfer(user1.address, ethers.parseEther("1000"));
    await tst.connect(owner).transfer(user2.address, ethers.parseEther("1000"));
  });

  describe("Lock Agreement", function () {
    it("Should lock TST for agreement", async function () {
      const amount = ethers.parseEther("10");
      const duration = 30 * 24 * 60 * 60; // 30 days
      const agreementId = "agreement-1";

      const tx = await escrow
        .connect(user1)
        .lockForAgreement(amount, duration, agreementId);

      await expect(tx).to.emit(escrow, "AgreementLocked");

      const locks = await escrow.getLocksByUser(user1.address);
      expect(locks.length).to.equal(1);
    });

    it("Should prevent lock without balance", async function () {
      const amount = ethers.parseEther("2000");
      const duration = 30 * 24 * 60 * 60;
      const agreementId = "agreement-1";

      await expect(
        escrow.connect(user1).lockForAgreement(amount, duration, agreementId)
      ).to.be.revertedWith("Insufficient TST balance");
    });

    it("Should require non-zero amount", async function () {
      const amount = 0;
      const duration = 30 * 24 * 60 * 60;
      const agreementId = "agreement-1";

      await expect(
        escrow.connect(user1).lockForAgreement(amount, duration, agreementId)
      ).to.be.revertedWith("Amount must be > 0");
    });

    it("Should require agreement ID", async function () {
      const amount = ethers.parseEther("10");
      const duration = 30 * 24 * 60 * 60;
      const agreementId = "";

      await expect(
        escrow.connect(user1).lockForAgreement(amount, duration, agreementId)
      ).to.be.revertedWith("Agreement ID required");
    });
  });

  describe("Release After Expiry", function () {
    it("Should release TST after expiry", async function () {
      const amount = ethers.parseEther("10");
      const duration = 2; // 2 seconds for testing
      const agreementId = "agreement-1";

      const lockTx = await escrow
        .connect(user1)
        .lockForAgreement(amount, duration, agreementId);

      const receipt = await lockTx.wait();
      const event = receipt.events.find((e) => e.event === "AgreementLocked");
      const lockId = event.args.lockId;

      // Wait for expiry
      await time.increase(duration + 1);

      const releaseTx = await escrow.connect(user1).releaseAfterExpiry(lockId);
      await expect(releaseTx).to.emit(escrow, "AgreementReleased");
    });

    it("Should prevent release before expiry", async function () {
      const amount = ethers.parseEther("10");
      const duration = 100; // 100 seconds
      const agreementId = "agreement-1";

      const lockTx = await escrow
        .connect(user1)
        .lockForAgreement(amount, duration, agreementId);

      const receipt = await lockTx.wait();
      const event = receipt.events.find((e) => e.event === "AgreementLocked");
      const lockId = event.args.lockId;

      await expect(
        escrow.connect(user1).releaseAfterExpiry(lockId)
      ).to.be.revertedWith("Lock period not complete");
    });

    it("Should prevent double release", async function () {
      const amount = ethers.parseEther("10");
      const duration = 2;
      const agreementId = "agreement-1";

      const lockTx = await escrow
        .connect(user1)
        .lockForAgreement(amount, duration, agreementId);

      const receipt = await lockTx.wait();
      const event = receipt.events.find((e) => e.event === "AgreementLocked");
      const lockId = event.args.lockId;

      await time.increase(duration + 1);
      await escrow.connect(user1).releaseAfterExpiry(lockId);

      await expect(
        escrow.connect(user1).releaseAfterExpiry(lockId)
      ).to.be.revertedWith("Lock already released");
    });
  });

  describe("Early Termination", function () {
    it("Should allow early termination", async function () {
      const amount = ethers.parseEther("10");
      const duration = 100;
      const agreementId = "agreement-1";

      const lockTx = await escrow
        .connect(user1)
        .lockForAgreement(amount, duration, agreementId);

      const receipt = await lockTx.wait();
      const event = receipt.events.find((e) => e.event === "AgreementLocked");
      const lockId = event.args.lockId;

      const terminateTx = await escrow.connect(user1).earlyTerminate(lockId);
      await expect(terminateTx).to.emit(escrow, "AgreementTerminated");
    });

    it("Should prevent termination by non-owner", async function () {
      const amount = ethers.parseEther("10");
      const duration = 100;
      const agreementId = "agreement-1";

      const lockTx = await escrow
        .connect(user1)
        .lockForAgreement(amount, duration, agreementId);

      const receipt = await lockTx.wait();
      const event = receipt.events.find((e) => e.event === "AgreementLocked");
      const lockId = event.args.lockId;

      await expect(
        escrow.connect(user2).earlyTerminate(lockId)
      ).to.be.revertedWith("Only lock owner can terminate");
    });
  });

  describe("Check Lock Status", function () {
    it("Should check if lock is active", async function () {
      const amount = ethers.parseEther("10");
      const duration = 100;
      const agreementId = "agreement-1";

      const lockTx = await escrow
        .connect(user1)
        .lockForAgreement(amount, duration, agreementId);

      const receipt = await lockTx.wait();
      const event = receipt.events.find((e) => e.event === "AgreementLocked");
      const lockId = event.args.lockId;

      const isLocked = await escrow.isLocked(lockId);
      expect(isLocked).to.be.true;
    });

    it("Should return false for expired lock", async function () {
      const amount = ethers.parseEther("10");
      const duration = 2;
      const agreementId = "agreement-1";

      const lockTx = await escrow
        .connect(user1)
        .lockForAgreement(amount, duration, agreementId);

      const receipt = await lockTx.wait();
      const event = receipt.events.find((e) => e.event === "AgreementLocked");
      const lockId = event.args.lockId;

      await time.increase(duration + 1);

      const isLocked = await escrow.isLocked(lockId);
      expect(isLocked).to.be.false;
    });
  });

  describe("Query Locks", function () {
    it("Should get all locks", async function () {
      const amount = ethers.parseEther("10");
      const duration = 100;

      await escrow.connect(user1).lockForAgreement(amount, duration, "agreement-1");
      await escrow.connect(user2).lockForAgreement(amount, duration, "agreement-2");

      const allLocks = await escrow.getAllLocks();
      expect(allLocks.length).to.equal(2);
    });

    it("Should get locks by user", async function () {
      const amount = ethers.parseEther("10");
      const duration = 100;

      await escrow.connect(user1).lockForAgreement(amount, duration, "agreement-1");
      await escrow.connect(user1).lockForAgreement(amount, duration, "agreement-2");
      await escrow.connect(user2).lockForAgreement(amount, duration, "agreement-3");

      const user1Locks = await escrow.getLocksByUser(user1.address);
      expect(user1Locks.length).to.equal(2);

      const user2Locks = await escrow.getLocksByUser(user2.address);
      expect(user2Locks.length).to.equal(1);
    });
  });
});
