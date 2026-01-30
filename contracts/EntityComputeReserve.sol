// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "./TST.sol";

/**
 * @title EntityComputeReserve
 * @notice Reserve TST for entity compute access with daily quotas
 * @dev Quotas reset daily, no yield, usage-based allocation
 */
contract EntityComputeReserve {
    TST public tst;

    // Entity types
    uint8 public constant ENTITY_RISK = 1;
    uint8 public constant ENTITY_STRATEGY = 2;
    uint8 public constant ENTITY_MEMORY = 3;

    struct Reservation {
        address user;
        uint8 entity;
        uint256 amount;
        uint256 reservedAt;
        uint256 expiresAt;
        bool active;
    }

    struct QuotaUsage {
        address user;
        uint8 entity;
        uint256 usedToday;
        uint256 lastResetTime;
    }

    /// @notice Mapping of reservation ID to reservation details
    mapping(bytes32 => Reservation) public reservations;

    /// @notice Array of all reservation IDs
    bytes32[] public reservationIds;

    /// @notice Mapping of user + entity to quota usage
    mapping(bytes32 => QuotaUsage) public quotaUsage;

    /// @notice 30-day reservation period
    uint256 public constant RESERVATION_DURATION = 30 days;

    /// @notice 1 day for quota reset
    uint256 public constant QUOTA_RESET_PERIOD = 1 days;

    /// @notice Daily quota amounts per tier (no TST = Tier 0)
    mapping(uint8 => mapping(uint8 => uint256)) public dailyQuotaByTier;

    /// @notice Event emitted when TST is reserved for compute
    event ComputeReserved(
        bytes32 indexed reservationId,
        address indexed user,
        uint8 entity,
        uint256 amount,
        uint256 expiresAt
    );

    /// @notice Event emitted when reservation ends
    event ReservationEnded(bytes32 indexed reservationId, address indexed user);

    /// @notice Event emitted when quota is consumed
    event QuotaConsumed(address indexed user, uint8 entity, uint256 amount);

    /// @notice Event emitted when quota resets
    event QuotaReset(address indexed user, uint8 entity);

    /**
     * @notice Initialize compute reserve with TST token reference
     * @param _tst Address of TST token contract
     */
    constructor(address _tst) {
        require(_tst != address(0), "Invalid TST address");
        tst = TST(_tst);

        // Set up quotas for each entity and tier
        // ENTITY_RISK
        dailyQuotaByTier[ENTITY_RISK][0] = 1;      // No TST: 1x/day
        dailyQuotaByTier[ENTITY_RISK][1] = 3;      // Tier 1 (5 TST): 3x/day
        dailyQuotaByTier[ENTITY_RISK][2] = 10;     // Tier 2 (25 TST): 10x/day
        dailyQuotaByTier[ENTITY_RISK][3] = 1000;   // Tier 3 (100 TST): unlimited

        // ENTITY_STRATEGY
        dailyQuotaByTier[ENTITY_STRATEGY][0] = 4;   // No TST: ~1x/week
        dailyQuotaByTier[ENTITY_STRATEGY][1] = 12;  // Tier 1: ~3x/week
        dailyQuotaByTier[ENTITY_STRATEGY][2] = 28;  // Tier 2: daily
        dailyQuotaByTier[ENTITY_STRATEGY][3] = 1000; // Tier 3: unlimited

        // ENTITY_MEMORY
        dailyQuotaByTier[ENTITY_MEMORY][0] = 2;     // No TST: ~1x/month
        dailyQuotaByTier[ENTITY_MEMORY][1] = 7;     // Tier 1: ~1x/week
        dailyQuotaByTier[ENTITY_MEMORY][2] = 28;    // Tier 2: daily
        dailyQuotaByTier[ENTITY_MEMORY][3] = 1000;  // Tier 3: unlimited
    }

    /**
     * @notice Reserve TST for entity access
     * @param entity Entity type (1=Risk, 2=Strategy, 3=Memory)
     * @return reservationId Unique identifier for this reservation
     */
    function reserveForEntity(uint8 entity) external returns (bytes32) {
        require(entity >= 1 && entity <= 3, "Invalid entity type");

        // Determine amount based on tier (to be called from backend with tier context)
        // For now, this records the reservation
        // Backend will handle tier validation and amount

        uint256 amount = 0; // Backend sets via recordStake

        // Generate unique reservation ID
        bytes32 reservationId = keccak256(abi.encodePacked(msg.sender, block.timestamp, entity));

        // Calculate expiry
        uint256 expiresAt = block.timestamp + RESERVATION_DURATION;

        // Create reservation record
        reservations[reservationId] = Reservation({
            user: msg.sender,
            entity: entity,
            amount: amount,
            reservedAt: block.timestamp,
            expiresAt: expiresAt,
            active: true
        });

        reservationIds.push(reservationId);

        emit ComputeReserved(reservationId, msg.sender, entity, amount, expiresAt);

        return reservationId;
    }

    /**
     * @notice Get remaining quota for user + entity today
     * @param user User address
     * @param entity Entity type
     * @param tier Current tier level
     * @return Remaining quota for today
     */
    function getQuotaRemaining(
        address user,
        uint8 entity,
        uint8 tier
    ) external view returns (uint256) {
        require(entity >= 1 && entity <= 3, "Invalid entity type");
        require(tier >= 0 && tier <= 3, "Invalid tier");

        bytes32 key = keccak256(abi.encodePacked(user, entity));
        QuotaUsage memory usage = quotaUsage[key];

        // Check if quota needs reset
        bool needsReset = block.timestamp >= usage.lastResetTime + QUOTA_RESET_PERIOD;

        uint256 dailyQuota = dailyQuotaByTier[entity][tier];

        if (needsReset) {
            return dailyQuota;
        } else {
            uint256 used = usage.usedToday;
            return used >= dailyQuota ? 0 : dailyQuota - used;
        }
    }

    /**
     * @notice Consume quota for entity usage (called by backend)
     * @param user User address
     * @param entity Entity type
     * @param tier Current tier level
     * @param amount Amount to consume
     */
    function consumeQuota(
        address user,
        uint8 entity,
        uint8 tier,
        uint256 amount
    ) external {
        require(entity >= 1 && entity <= 3, "Invalid entity type");
        require(tier >= 0 && tier <= 3, "Invalid tier");
        require(amount > 0, "Amount must be > 0");

        bytes32 key = keccak256(abi.encodePacked(user, entity));
        QuotaUsage storage usage = quotaUsage[key];

        // Reset if needed
        if (block.timestamp >= usage.lastResetTime + QUOTA_RESET_PERIOD) {
            usage.usedToday = 0;
            usage.lastResetTime = block.timestamp;
            emit QuotaReset(user, entity);
        }

        uint256 dailyQuota = dailyQuotaByTier[entity][tier];
        require(usage.usedToday + amount <= dailyQuota, "Quota exceeded");

        usage.usedToday += amount;
        emit QuotaConsumed(user, entity, amount);
    }

    /**
     * @notice End a reservation
     * @param reservationId ID of the reservation to end
     */
    function endReservation(bytes32 reservationId) external {
        Reservation storage reservation = reservations[reservationId];

        require(reservation.user != address(0), "Reservation does not exist");
        require(reservation.active, "Reservation already ended");
        require(reservation.user == msg.sender, "Only owner can end");

        reservation.active = false;

        if (reservation.amount > 0) {
            tst.recordUnstake(reservation.amount);
        }

        emit ReservationEnded(reservationId, msg.sender);
    }

    /**
     * @notice Get reservation details
     * @param reservationId ID of the reservation
     * @return Reservation details
     */
    function getReservation(bytes32 reservationId) external view returns (Reservation memory) {
        return reservations[reservationId];
    }

    /**
     * @notice Get all reservation IDs
     * @return Array of reservation IDs
     */
    function getAllReservations() external view returns (bytes32[] memory) {
        return reservationIds;
    }

    /**
     * @notice Get reservations for a specific user
     * @param user Address to query
     * @return Array of reservation IDs for user
     */
    function getReservationsByUser(address user) external view returns (bytes32[] memory) {
        uint256 count = 0;
        for (uint256 i = 0; i < reservationIds.length; i++) {
            if (reservations[reservationIds[i]].user == user) {
                count++;
            }
        }

        bytes32[] memory userReservations = new bytes32[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < reservationIds.length; i++) {
            if (reservations[reservationIds[i]].user == user) {
                userReservations[index] = reservationIds[i];
                index++;
            }
        }

        return userReservations;
    }

    /**
     * @notice Get daily quota for entity and tier
     * @param entity Entity type
     * @param tier Tier level
     * @return Daily quota amount
     */
    function getDailyQuota(uint8 entity, uint8 tier) external view returns (uint256) {
        require(entity >= 1 && entity <= 3, "Invalid entity type");
        require(tier >= 0 && tier <= 3, "Invalid tier");
        return dailyQuotaByTier[entity][tier];
    }
}
