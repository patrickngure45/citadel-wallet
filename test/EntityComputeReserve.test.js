import { expect } from "chai";
import { ethers } from "hardhat";
import { time } from "@nomicfoundation/hardhat-network-helpers";

describe("EntityComputeReserve", function () {
  let tst, reserve;
  let owner, user1, user2;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    // Deploy TST
    const TST = await ethers.getContractFactory("TST");
    tst = await TST.deploy();
    await tst.waitForDeployment();

    // Deploy Reserve
    const Reserve = await ethers.getContractFactory("EntityComputeReserve");
    reserve = await Reserve.deploy(await tst.getAddress());
    await reserve.waitForDeployment();

    // Transfer TST to users
    await tst.connect(owner).transfer(user1.address, ethers.parseEther("1000"));
    await tst.connect(owner).transfer(user2.address, ethers.parseEther("1000"));
  });

  describe("Entity Types", function () {
    it("Should have correct entity constants", async function () {
      expect(await reserve.ENTITY_RISK()).to.equal(1);
      expect(await reserve.ENTITY_STRATEGY()).to.equal(2);
      expect(await reserve.ENTITY_MEMORY()).to.equal(3);
    });
  });

  describe("Reserve For Entity", function () {
    it("Should reserve for Risk entity", async function () {
      const tx = await reserve.connect(user1).reserveForEntity(1);
      await expect(tx).to.emit(reserve, "ComputeReserved");

      const reservations = await reserve.getReservationsByUser(user1.address);
      expect(reservations.length).to.equal(1);
    });

    it("Should reserve for Strategy entity", async function () {
      const tx = await reserve.connect(user1).reserveForEntity(2);
      await expect(tx).to.emit(reserve, "ComputeReserved");

      const reservations = await reserve.getReservationsByUser(user1.address);
      expect(reservations.length).to.equal(1);
    });

    it("Should reserve for Memory entity", async function () {
      const tx = await reserve.connect(user1).reserveForEntity(3);
      await expect(tx).to.emit(reserve, "ComputeReserved");

      const reservations = await reserve.getReservationsByUser(user1.address);
      expect(reservations.length).to.equal(1);
    });

    it("Should prevent invalid entity", async function () {
      await expect(reserve.connect(user1).reserveForEntity(4)).to.be.revertedWith(
        "Invalid entity type"
      );
    });
  });

  describe("Quota Management", function () {
    it("Should return correct daily quota for Tier 0", async function () {
      const riskQuota = await reserve.getDailyQuota(1, 0);
      const strategyQuota = await reserve.getDailyQuota(2, 0);
      const memoryQuota = await reserve.getDailyQuota(3, 0);

      expect(riskQuota).to.equal(1);
      expect(strategyQuota).to.equal(4);
      expect(memoryQuota).to.equal(2);
    });

    it("Should return correct daily quota for Tier 1", async function () {
      const riskQuota = await reserve.getDailyQuota(1, 1);
      const strategyQuota = await reserve.getDailyQuota(2, 1);
      const memoryQuota = await reserve.getDailyQuota(3, 1);

      expect(riskQuota).to.equal(3);
      expect(strategyQuota).to.equal(12);
      expect(memoryQuota).to.equal(7);
    });

    it("Should return correct daily quota for Tier 2", async function () {
      const riskQuota = await reserve.getDailyQuota(1, 2);
      const strategyQuota = await reserve.getDailyQuota(2, 2);
      const memoryQuota = await reserve.getDailyQuota(3, 2);

      expect(riskQuota).to.equal(10);
      expect(strategyQuota).to.equal(28);
      expect(memoryQuota).to.equal(28);
    });

    it("Should return unlimited for Tier 3", async function () {
      const riskQuota = await reserve.getDailyQuota(1, 3);
      const strategyQuota = await reserve.getDailyQuota(2, 3);
      const memoryQuota = await reserve.getDailyQuota(3, 3);

      expect(riskQuota).to.equal(1000);
      expect(strategyQuota).to.equal(1000);
      expect(memoryQuota).to.equal(1000);
    });
  });

  describe("Get Quota Remaining", function () {
    it("Should return full quota initially", async function () {
      const remaining = await reserve.getQuotaRemaining(user1.address, 1, 1);
      expect(remaining).to.equal(3); // Tier 1 Risk quota
    });

    it("Should decrease quota after consumption", async function () {
      await reserve.connect(reserve).consumeQuota(user1.address, 1, 1, 1);

      const remaining = await reserve.getQuotaRemaining(user1.address, 1, 1);
      expect(remaining).to.equal(2);
    });

    it("Should return zero when quota exceeded", async function () {
      await reserve.connect(reserve).consumeQuota(user1.address, 1, 1, 3);

      const remaining = await reserve.getQuotaRemaining(user1.address, 1, 1);
      expect(remaining).to.equal(0);
    });
  });

  describe("Consume Quota", function () {
    it("Should consume quota successfully", async function () {
      const tx = await reserve.connect(reserve).consumeQuota(user1.address, 1, 1, 1);
      await expect(tx).to.emit(reserve, "QuotaConsumed");
    });

    it("Should prevent exceeding quota", async function () {
      await reserve.connect(reserve).consumeQuota(user1.address, 1, 1, 3);

      await expect(
        reserve.connect(reserve).consumeQuota(user1.address, 1, 1, 1)
      ).to.be.revertedWith("Quota exceeded");
    });

    it("Should require valid entity", async function () {
      await expect(
        reserve.connect(reserve).consumeQuota(user1.address, 4, 1, 1)
      ).to.be.revertedWith("Invalid entity type");
    });

    it("Should reset quota daily", async function () {
      await reserve.connect(reserve).consumeQuota(user1.address, 1, 1, 3);

      let remaining = await reserve.getQuotaRemaining(user1.address, 1, 1);
      expect(remaining).to.equal(0);

      // Wait for quota reset (1 day)
      await time.increase(24 * 60 * 60 + 1);

      remaining = await reserve.getQuotaRemaining(user1.address, 1, 1);
      expect(remaining).to.equal(3);
    });

    it("Should emit reset event after 24 hours", async function () {
      await reserve.connect(reserve).consumeQuota(user1.address, 1, 1, 1);

      await time.increase(24 * 60 * 60 + 1);

      const tx = await reserve.connect(reserve).consumeQuota(user1.address, 1, 1, 1);
      await expect(tx).to.emit(reserve, "QuotaReset");
    });
  });

  describe("End Reservation", function () {
    it("Should end reservation", async function () {
      await reserve.connect(user1).reserveForEntity(1);

      const reservations = await reserve.getReservationsByUser(user1.address);
      const resId = reservations[0];

      const tx = await reserve.connect(user1).endReservation(resId);
      await expect(tx).to.emit(reserve, "ReservationEnded");
    });

    it("Should prevent ending by non-owner", async function () {
      await reserve.connect(user1).reserveForEntity(1);

      const reservations = await reserve.getReservationsByUser(user1.address);
      const resId = reservations[0];

      await expect(
        reserve.connect(user2).endReservation(resId)
      ).to.be.revertedWith("Only owner can end");
    });

    it("Should prevent ending twice", async function () {
      await reserve.connect(user1).reserveForEntity(1);

      const reservations = await reserve.getReservationsByUser(user1.address);
      const resId = reservations[0];

      await reserve.connect(user1).endReservation(resId);

      await expect(
        reserve.connect(user1).endReservation(resId)
      ).to.be.revertedWith("Reservation already ended");
    });
  });

  describe("Query Reservations", function () {
    it("Should get all reservations", async function () {
      await reserve.connect(user1).reserveForEntity(1);
      await reserve.connect(user2).reserveForEntity(2);

      const allReservations = await reserve.getAllReservations();
      expect(allReservations.length).to.equal(2);
    });

    it("Should get reservations by user", async function () {
      await reserve.connect(user1).reserveForEntity(1);
      await reserve.connect(user1).reserveForEntity(2);
      await reserve.connect(user2).reserveForEntity(3);

      const user1Reservations = await reserve.getReservationsByUser(user1.address);
      expect(user1Reservations.length).to.equal(2);

      const user2Reservations = await reserve.getReservationsByUser(user2.address);
      expect(user2Reservations.length).to.equal(1);
    });
  });
});
