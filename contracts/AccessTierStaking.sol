// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "./TST.sol";

/**
 * @title AccessTierStaking
 * @notice Stake TST for 30-day tier access (no perpetual, no yield)
 * @dev Tiers: 1 (5 TST), 2 (25 TST), 3 (100 TST)
 */
contract AccessTierStaking {
    TST public tst;

    /// @notice Tier requirements in TST
    mapping(uint8 => uint256) public tierAmounts;

    struct Stake {
        address user;
        uint256 amount;
        uint8 tier;
        uint256 stakedAt;
        uint256 unstakedAt;
        bool active;
    }

    /// @notice Mapping of stake ID to stake details
    mapping(bytes32 => Stake) public stakes;

    /// @notice Array of all stake IDs (for tracking)
    bytes32[] public stakeIds;

    /// @notice 30-day lock period
    uint256 public constant STAKE_DURATION = 30 days;

    /// @notice Event emitted when TST is staked
    event Staked(bytes32 indexed stakeId, address indexed user, uint256 amount, uint8 tier, uint256 expiresAt);

    /// @notice Event emitted when TST is unstaked
    event Unstaked(bytes32 indexed stakeId, address indexed user, uint256 amount);

    /**
     * @notice Initialize staking with TST token reference and tier amounts
     * @param _tst Address of TST token contract
     */
    constructor(address _tst) {
        require(_tst != address(0), "Invalid TST address");
        tst = TST(_tst);

        // Set tier amounts
        tierAmounts[1] = 5 * 10 ** 18;   // Tier 1: 5 TST
        tierAmounts[2] = 25 * 10 ** 18;  // Tier 2: 25 TST
        tierAmounts[3] = 100 * 10 ** 18; // Tier 3: 100 TST
    }

    /**
     * @notice Stake TST for tier access
     * @param tier Access tier (1, 2, or 3)
     * @return stakeId Unique identifier for this stake
     */
    function stakeForTier(uint8 tier) external returns (bytes32) {
        require(tier >= 1 && tier <= 3, "Invalid tier");

        uint256 amount = tierAmounts[tier];

        // Check TST balance
        require(tst.balanceOf(msg.sender) >= amount, "Insufficient TST balance");

        // Generate unique stake ID
        bytes32 stakeId = keccak256(abi.encodePacked(msg.sender, block.timestamp, tier));

        // Calculate expiry
        uint256 expiresAt = block.timestamp + STAKE_DURATION;

        // Create stake record
        stakes[stakeId] = Stake({
            user: msg.sender,
            amount: amount,
            tier: tier,
            stakedAt: block.timestamp,
            unstakedAt: 0,
            active: true
        });

        stakeIds.push(stakeId);

        // Record stake in TST contract
        tst.recordStake(amount, tier);

        emit Staked(stakeId, msg.sender, amount, tier, expiresAt);

        return stakeId;
    }

    /**
     * @notice Unstake TST after 30-day period
     * @param stakeId ID of the stake to unstake
     */
    function unstake(bytes32 stakeId) external {
        Stake storage stake = stakes[stakeId];

        require(stake.user != address(0), "Stake does not exist");
        require(stake.active, "Stake already unstaked");
        require(stake.user == msg.sender, "Only stake owner can unstake");
        require(block.timestamp >= stake.stakedAt + STAKE_DURATION, "30-day period not complete");

        // Mark as inactive
        stake.active = false;
        stake.unstakedAt = block.timestamp;

        // Release stake in TST contract (no penalties)
        tst.recordUnstake(stake.amount);

        emit Unstaked(stakeId, msg.sender, stake.amount);
    }

    /**
     * @notice Check if user has active tier
     * @param user Address to check
     * @param tier Tier level to verify
     * @return True if user has active stake for this tier or higher
     */
    function hasActiveTier(address user, uint8 tier) external view returns (bool) {
        require(tier >= 1 && tier <= 3, "Invalid tier");

        for (uint256 i = 0; i < stakeIds.length; i++) {
            Stake storage stake = stakes[stakeIds[i]];
            if (
                stake.user == user &&
                stake.active &&
                stake.tier >= tier &&
                block.timestamp < stake.stakedAt + STAKE_DURATION
            ) {
                return true;
            }
        }

        return false;
    }

    /**
     * @notice Get highest active tier for user
     * @param user Address to check
     * @return Highest active tier (0 if none)
     */
    function getHighestActiveTier(address user) external view returns (uint8) {
        uint8 highest = 0;

        for (uint256 i = 0; i < stakeIds.length; i++) {
            Stake storage stake = stakes[stakeIds[i]];
            if (
                stake.user == user &&
                stake.active &&
                block.timestamp < stake.stakedAt + STAKE_DURATION
            ) {
                if (stake.tier > highest) {
                    highest = stake.tier;
                }
            }
        }

        return highest;
    }

    /**
     * @notice Get stake details
     * @param stakeId ID of the stake
     * @return Stake details
     */
    function getStake(bytes32 stakeId) external view returns (Stake memory) {
        return stakes[stakeId];
    }

    /**
     * @notice Get all stake IDs
     * @return Array of stake IDs
     */
    function getAllStakes() external view returns (bytes32[] memory) {
        return stakeIds;
    }

    /**
     * @notice Get stakes for a specific user
     * @param user Address to query
     * @return Array of stake IDs for user
     */
    function getStakesByUser(address user) external view returns (bytes32[] memory) {
        uint256 count = 0;
        for (uint256 i = 0; i < stakeIds.length; i++) {
            if (stakes[stakeIds[i]].user == user) {
                count++;
            }
        }

        bytes32[] memory userStakes = new bytes32[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < stakeIds.length; i++) {
            if (stakes[stakeIds[i]].user == user) {
                userStakes[index] = stakeIds[i];
                index++;
            }
        }

        return userStakes;
    }

    /**
     * @notice Get tier requirements
     * @param tier Tier level
     * @return Amount of TST required
     */
    function getTierAmount(uint8 tier) external view returns (uint256) {
        require(tier >= 1 && tier <= 3, "Invalid tier");
        return tierAmounts[tier];
    }
}
