// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "./TST.sol";

/**
 * @title P2PAgreementEscrow
 * @notice Escrow for P2P agreement locks - TST locked for agreement duration
 * @dev Lock TST → agreement active → agreement ends → TST released
 */
contract P2PAgreementEscrow {
    TST public tst;

    struct Lock {
        address user;
        uint256 amount;
        uint256 lockedUntil;
        string agreementId;
        bool released;
    }

    /// @notice Mapping of lock ID to lock details
    mapping(bytes32 => Lock) public locks;

    /// @notice Array of all lock IDs (for tracking)
    bytes32[] public lockIds;

    /// @notice Event emitted when TST is locked for agreement
    event AgreementLocked(
        bytes32 indexed lockId,
        address indexed user,
        uint256 amount,
        string agreementId,
        uint256 lockedUntil
    );

    /// @notice Event emitted when locked TST is released
    event AgreementReleased(bytes32 indexed lockId, address indexed user, uint256 amount);

    /// @notice Event emitted when agreement is terminated early
    event AgreementTerminated(bytes32 indexed lockId, address indexed user, uint256 amountReturned);

    /**
     * @notice Initialize escrow with TST token reference
     * @param _tst Address of TST token contract
     */
    constructor(address _tst) {
        require(_tst != address(0), "Invalid TST address");
        tst = TST(_tst);
    }

    /**
     * @notice Lock TST for P2P agreement
     * @param amount Amount of TST to lock
     * @param duration Duration in seconds to lock
     * @param agreementId Reference to agreement ID
     * @return lockId Unique identifier for this lock
     */
    function lockForAgreement(
        uint256 amount,
        uint256 duration,
        string memory agreementId
    ) external returns (bytes32) {
        require(amount > 0, "Amount must be > 0");
        require(duration > 0, "Duration must be > 0");
        require(bytes(agreementId).length > 0, "Agreement ID required");

        // Check TST balance
        require(tst.balanceOf(msg.sender) >= amount, "Insufficient TST balance");

        // Generate unique lock ID
        bytes32 lockId = keccak256(abi.encodePacked(msg.sender, block.timestamp, amount));

        // Calculate unlock time
        uint256 unlockTime = block.timestamp + duration;

        // Create lock record
        locks[lockId] = Lock({
            user: msg.sender,
            amount: amount,
            lockedUntil: unlockTime,
            agreementId: agreementId,
            released: false
        });

        lockIds.push(lockId);

        // Record lock in TST contract
        tst.recordLock(amount, lockId);

        emit AgreementLocked(lockId, msg.sender, amount, agreementId, unlockTime);

        return lockId;
    }

    /**
     * @notice Release TST after agreement expires
     * @param lockId ID of the lock to release
     */
    function releaseAfterExpiry(bytes32 lockId) external {
        Lock storage lock = locks[lockId];

        require(lock.user != address(0), "Lock does not exist");
        require(!lock.released, "Lock already released");
        require(block.timestamp >= lock.lockedUntil, "Lock period not complete");
        require(lock.user == msg.sender, "Only lock owner can release");

        // Mark as released
        lock.released = true;

        // Release lock in TST contract
        tst.releaseLock(lock.amount, lockId);

        emit AgreementReleased(lockId, msg.sender, lock.amount);
    }

    /**
     * @notice Terminate agreement early and release TST (no penalties)
     * @param lockId ID of the lock to terminate
     */
    function earlyTerminate(bytes32 lockId) external {
        Lock storage lock = locks[lockId];

        require(lock.user != address(0), "Lock does not exist");
        require(!lock.released, "Lock already released");
        require(lock.user == msg.sender, "Only lock owner can terminate");

        // Mark as released
        lock.released = true;

        // Release lock in TST contract (no penalties)
        tst.releaseLock(lock.amount, lockId);

        emit AgreementTerminated(lockId, msg.sender, lock.amount);
    }

    /**
     * @notice Check if a lock is still active
     * @param lockId ID of the lock to check
     * @return True if lock is active (not released and not expired)
     */
    function isLocked(bytes32 lockId) external view returns (bool) {
        Lock storage lock = locks[lockId];
        return lock.user != address(0) && !lock.released && block.timestamp < lock.lockedUntil;
    }

    /**
     * @notice Get lock details
     * @param lockId ID of the lock
     * @return Lock details
     */
    function getLock(bytes32 lockId) external view returns (Lock memory) {
        return locks[lockId];
    }

    /**
     * @notice Get all lock IDs
     * @return Array of lock IDs
     */
    function getAllLocks() external view returns (bytes32[] memory) {
        return lockIds;
    }

    /**
     * @notice Get locks for a specific user
     * @param user Address to query
     * @return Array of lock IDs for user
     */
    function getLocksByUser(address user) external view returns (bytes32[] memory) {
        uint256 count = 0;
        for (uint256 i = 0; i < lockIds.length; i++) {
            if (locks[lockIds[i]].user == user) {
                count++;
            }
        }

        bytes32[] memory userLocks = new bytes32[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < lockIds.length; i++) {
            if (locks[lockIds[i]].user == user) {
                userLocks[index] = lockIds[i];
                index++;
            }
        }

        return userLocks;
    }
}
