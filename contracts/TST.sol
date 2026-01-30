// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TST (TradeSynapse Token)
 * @notice Fixed supply access token (1M, no inflation ever)
 * @dev No minting capability, no yield promises, access control only
 */
contract TST is ERC20, Ownable {
    /// @notice Fixed total supply: 1,000,000 TST (18 decimals)
    uint256 public constant TOTAL_SUPPLY = 1_000_000 * 10 ** 18;

    /// @notice Mapping to track locks for each user
    mapping(address => uint256) public lockedBalance;

    /// @notice Mapping to track stakes for each user
    mapping(address => uint256) public stakedBalance;

    /// @notice Event emitted when TST is locked
    event TokensLocked(address indexed user, uint256 amount, bytes32 indexed lockId);

    /// @notice Event emitted when locked TST is released
    event TokensReleased(address indexed user, uint256 amount, bytes32 indexed lockId);

    /// @notice Event emitted when TST is staked for tier access
    event TokensStaked(address indexed user, uint256 amount, uint8 tier);

    /// @notice Event emitted when staked TST is unstaked
    event TokensUnstaked(address indexed user, uint256 amount);

    /**
     * @notice Initialize TST with 1M fixed supply sent to owner
     */
    constructor() ERC20("TradeSynapse Token", "TST") {
        _mint(msg.sender, TOTAL_SUPPLY);
    }

    /**
     * @notice Record TST as locked (for P2P agreements)
     * @param amount Amount of TST to lock
     * @param lockId Unique identifier for the lock
     */
    function recordLock(uint256 amount, bytes32 lockId) external {
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        require(lockedBalance[msg.sender] + amount <= balanceOf(msg.sender), "Insufficient unlocked balance");
        
        lockedBalance[msg.sender] += amount;
        emit TokensLocked(msg.sender, amount, lockId);
    }

    /**
     * @notice Release previously locked TST
     * @param amount Amount of TST to release
     * @param lockId Unique identifier for the lock
     */
    function releaseLock(uint256 amount, bytes32 lockId) external {
        require(lockedBalance[msg.sender] >= amount, "Insufficient locked balance");
        
        lockedBalance[msg.sender] -= amount;
        emit TokensReleased(msg.sender, amount, lockId);
    }

    /**
     * @notice Record TST as staked (for tier access)
     * @param amount Amount of TST to stake
     * @param tier Access tier (1, 2, or 3)
     */
    function recordStake(uint256 amount, uint8 tier) external {
        require(tier >= 1 && tier <= 3, "Invalid tier");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        require(stakedBalance[msg.sender] + amount <= balanceOf(msg.sender), "Insufficient unlocked balance");
        
        stakedBalance[msg.sender] += amount;
        emit TokensStaked(msg.sender, amount, tier);
    }

    /**
     * @notice Release previously staked TST
     * @param amount Amount of TST to unstake
     */
    function recordUnstake(uint256 amount) external {
        require(stakedBalance[msg.sender] >= amount, "Insufficient staked balance");
        
        stakedBalance[msg.sender] -= amount;
        emit TokensUnstaked(msg.sender, amount);
    }

    /**
     * @notice Get available balance (not locked or staked)
     * @param account Account to check
     * @return Available balance
     */
    function getAvailableBalance(address account) external view returns (uint256) {
        uint256 total = balanceOf(account);
        uint256 locked = lockedBalance[account];
        uint256 staked = stakedBalance[account];
        
        return total > (locked + staked) ? total - locked - staked : 0;
    }

    /**
     * @notice Check if account has sufficient unlocked balance
     * @param account Account to check
     * @param amount Amount required
     * @return True if available balance >= amount
     */
    function hasAvailableBalance(address account, uint256 amount) external view returns (bool) {
        uint256 total = balanceOf(account);
        uint256 locked = lockedBalance[account];
        uint256 staked = stakedBalance[account];
        
        return (total - locked - staked) >= amount;
    }

    /**
     * @notice Transfer is blocked - TST is non-transferable except for unlocking mechanisms
     * @dev Override transfer to prevent trading
     */
    function transfer(address, uint256) public pure override returns (bool) {
        revert("TST: Transfer disabled - use locking/staking mechanisms");
    }

    /**
     * @notice TransferFrom is blocked - TST is non-transferable except for unlocking mechanisms
     * @dev Override transferFrom to prevent trading
     */
    function transferFrom(address, address, uint256) public pure override returns (bool) {
        revert("TST: Transfer disabled - use locking/staking mechanisms");
    }

    /**
     * @notice Approve is blocked - no transfers allowed
     * @dev Override approve to prevent trading setup
     */
    function approve(address, uint256) public pure override returns (bool) {
        revert("TST: Approve disabled - transfer not allowed");
    }
}
