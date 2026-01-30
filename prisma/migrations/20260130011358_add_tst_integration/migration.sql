-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "phone" TEXT,
    "phoneVerified" BOOLEAN NOT NULL DEFAULT false,
    "emailVerified" BOOLEAN NOT NULL DEFAULT false,
    "avatar" TEXT,
    "kycStatus" TEXT NOT NULL DEFAULT 'pending',
    "kycSubmittedAt" TIMESTAMP(3),
    "kycApprovedAt" TIMESTAMP(3),
    "riskProfile" TEXT NOT NULL DEFAULT 'moderate',
    "status" TEXT NOT NULL DEFAULT 'active',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Wallet" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "address" TEXT NOT NULL,
    "chain" TEXT NOT NULL,
    "walletType" TEXT NOT NULL DEFAULT 'user',
    "derivationPath" TEXT,
    "balanceUSDT" DECIMAL(28,8) NOT NULL DEFAULT 0,
    "balanceUSDC" DECIMAL(28,8) NOT NULL DEFAULT 0,
    "balanceNative" DECIMAL(28,8) NOT NULL DEFAULT 0,
    "balanceTST" DECIMAL(28,8) NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Wallet_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Transaction" (
    "id" TEXT NOT NULL,
    "walletId" TEXT NOT NULL,
    "txHash" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "amount" DECIMAL(28,8) NOT NULL,
    "assetType" TEXT NOT NULL,
    "chain" TEXT NOT NULL,
    "fromAddress" TEXT NOT NULL,
    "toAddress" TEXT NOT NULL,
    "gasUsed" DECIMAL(20,8),
    "gasPaid" DECIMAL(28,8),
    "blockNumber" BIGINT,
    "blockTimestamp" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "confirmedAt" TIMESTAMP(3),

    CONSTRAINT "Transaction_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Strategy" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "type" TEXT NOT NULL,
    "initialCapital" DECIMAL(28,8) NOT NULL,
    "currentValue" DECIMAL(28,8) NOT NULL,
    "targetAsset" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'paused',
    "vetoStatus" TEXT NOT NULL DEFAULT 'none',
    "totalReturn" DECIMAL(28,8) NOT NULL DEFAULT 0,
    "returnPercentage" DECIMAL(10,4) NOT NULL DEFAULT 0,
    "winRate" DECIMAL(5,2) NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "startedAt" TIMESTAMP(3),
    "endedAt" TIMESTAMP(3),
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Strategy_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StrategyDecision" (
    "id" TEXT NOT NULL,
    "strategyId" TEXT NOT NULL,
    "decision" TEXT NOT NULL,
    "confidence" DECIMAL(5,4) NOT NULL,
    "reasoning" TEXT NOT NULL,
    "perceptionScore" DECIMAL(5,4) NOT NULL,
    "memoryScore" DECIMAL(5,4) NOT NULL,
    "riskScore" DECIMAL(5,4) NOT NULL,
    "executed" BOOLEAN NOT NULL DEFAULT false,
    "executionPrice" DECIMAL(28,8),
    "executionTxHash" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "executedAt" TIMESTAMP(3),

    CONSTRAINT "StrategyDecision_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "EntityLog" (
    "id" TEXT NOT NULL,
    "entityType" TEXT NOT NULL,
    "cycle" INTEGER NOT NULL,
    "startTime" TIMESTAMP(3) NOT NULL,
    "endTime" TIMESTAMP(3) NOT NULL,
    "duration" INTEGER NOT NULL,
    "dataPointsProcessed" INTEGER NOT NULL,
    "anomaliesDetected" INTEGER NOT NULL,
    "decisionsGenerated" INTEGER NOT NULL,
    "status" TEXT NOT NULL,
    "errorMessage" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "EntityLog_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GuardianCheck" (
    "id" TEXT NOT NULL,
    "checkType" TEXT NOT NULL,
    "severity" TEXT NOT NULL,
    "userId" TEXT,
    "strategyId" TEXT,
    "description" TEXT NOT NULL,
    "anomalyScore" DECIMAL(5,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "approverNotes" TEXT,
    "approvedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "resolvedAt" TIMESTAMP(3),

    CONSTRAINT "GuardianCheck_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "P2PAgreement" (
    "id" TEXT NOT NULL,
    "borrowerId" TEXT NOT NULL,
    "lenderId" TEXT NOT NULL,
    "principalAmount" DECIMAL(28,8) NOT NULL,
    "interestRate" DECIMAL(5,2) NOT NULL,
    "duration" INTEGER NOT NULL,
    "assetType" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "approvalCount" INTEGER NOT NULL DEFAULT 0,
    "lenderApproved" BOOLEAN NOT NULL DEFAULT false,
    "borrowerApproved" BOOLEAN NOT NULL DEFAULT false,
    "disbursedAt" TIMESTAMP(3),
    "repaidAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "P2PAgreement_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "APIKey" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "keyPrefix" TEXT NOT NULL,
    "keyHash" TEXT NOT NULL,
    "tier" TEXT NOT NULL DEFAULT 'free',
    "requestsPerDay" INTEGER NOT NULL DEFAULT 100,
    "requestsUsedToday" INTEGER NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" TIMESTAMP(3),
    "lastUsedAt" TIMESTAMP(3),

    CONSTRAINT "APIKey_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PerformanceMetric" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "totalValue" DECIMAL(28,8) NOT NULL,
    "totalDeposits" DECIMAL(28,8) NOT NULL,
    "totalWithdrawals" DECIMAL(28,8) NOT NULL,
    "totalReturn" DECIMAL(28,8) NOT NULL,
    "returnPercentage" DECIMAL(10,4) NOT NULL,
    "volatility" DECIMAL(5,4) NOT NULL,
    "sharpeRatio" DECIMAL(5,2) NOT NULL,
    "maxDrawdown" DECIMAL(5,4) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "PerformanceMetric_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AuditTrail" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "resourceType" TEXT,
    "resourceId" TEXT,
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "status" TEXT NOT NULL,
    "oldValue" TEXT,
    "newValue" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AuditTrail_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TST_Lock" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "agreementId" TEXT,
    "amount" DECIMAL(28,8) NOT NULL,
    "lockedUntil" TIMESTAMP(3) NOT NULL,
    "released" BOOLEAN NOT NULL DEFAULT false,
    "releasedAt" TIMESTAMP(3),
    "contractLockId" TEXT NOT NULL,
    "txHash" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "TST_Lock_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TST_Stake" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "tier" INTEGER NOT NULL,
    "amount" DECIMAL(28,8) NOT NULL,
    "stakedAt" TIMESTAMP(3) NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "unstakedAt" TIMESTAMP(3),
    "contractStakeId" TEXT NOT NULL,
    "txHash" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "TST_Stake_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "EntityAccessTier" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "entityType" INTEGER NOT NULL,
    "tstReserved" DECIMAL(28,8) NOT NULL,
    "quotaPerDay" INTEGER NOT NULL,
    "quotaUsedToday" INTEGER NOT NULL DEFAULT 0,
    "lastResetTime" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "contractResId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "EntityAccessTier_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "FeatureFlag" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "isEnabled" BOOLEAN NOT NULL DEFAULT false,
    "rolloutPercentage" INTEGER NOT NULL DEFAULT 0,
    "targetUsers" TEXT[],
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "FeatureFlag_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE INDEX "User_email_idx" ON "User"("email");

-- CreateIndex
CREATE INDEX "User_kycStatus_idx" ON "User"("kycStatus");

-- CreateIndex
CREATE UNIQUE INDEX "Wallet_address_key" ON "Wallet"("address");

-- CreateIndex
CREATE INDEX "Wallet_address_idx" ON "Wallet"("address");

-- CreateIndex
CREATE INDEX "Wallet_userId_idx" ON "Wallet"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "Wallet_userId_chain_key" ON "Wallet"("userId", "chain");

-- CreateIndex
CREATE UNIQUE INDEX "Transaction_txHash_key" ON "Transaction"("txHash");

-- CreateIndex
CREATE INDEX "Transaction_walletId_idx" ON "Transaction"("walletId");

-- CreateIndex
CREATE INDEX "Transaction_txHash_idx" ON "Transaction"("txHash");

-- CreateIndex
CREATE INDEX "Transaction_status_idx" ON "Transaction"("status");

-- CreateIndex
CREATE INDEX "Transaction_createdAt_idx" ON "Transaction"("createdAt");

-- CreateIndex
CREATE INDEX "Strategy_userId_idx" ON "Strategy"("userId");

-- CreateIndex
CREATE INDEX "Strategy_status_idx" ON "Strategy"("status");

-- CreateIndex
CREATE INDEX "StrategyDecision_strategyId_idx" ON "StrategyDecision"("strategyId");

-- CreateIndex
CREATE INDEX "StrategyDecision_createdAt_idx" ON "StrategyDecision"("createdAt");

-- CreateIndex
CREATE INDEX "EntityLog_entityType_idx" ON "EntityLog"("entityType");

-- CreateIndex
CREATE INDEX "EntityLog_createdAt_idx" ON "EntityLog"("createdAt");

-- CreateIndex
CREATE INDEX "GuardianCheck_userId_idx" ON "GuardianCheck"("userId");

-- CreateIndex
CREATE INDEX "GuardianCheck_checkType_idx" ON "GuardianCheck"("checkType");

-- CreateIndex
CREATE INDEX "GuardianCheck_status_idx" ON "GuardianCheck"("status");

-- CreateIndex
CREATE INDEX "P2PAgreement_borrowerId_idx" ON "P2PAgreement"("borrowerId");

-- CreateIndex
CREATE INDEX "P2PAgreement_lenderId_idx" ON "P2PAgreement"("lenderId");

-- CreateIndex
CREATE INDEX "P2PAgreement_status_idx" ON "P2PAgreement"("status");

-- CreateIndex
CREATE UNIQUE INDEX "APIKey_keyHash_key" ON "APIKey"("keyHash");

-- CreateIndex
CREATE INDEX "APIKey_userId_idx" ON "APIKey"("userId");

-- CreateIndex
CREATE INDEX "APIKey_keyHash_idx" ON "APIKey"("keyHash");

-- CreateIndex
CREATE UNIQUE INDEX "PerformanceMetric_date_key" ON "PerformanceMetric"("date");

-- CreateIndex
CREATE INDEX "PerformanceMetric_userId_idx" ON "PerformanceMetric"("userId");

-- CreateIndex
CREATE INDEX "PerformanceMetric_date_idx" ON "PerformanceMetric"("date");

-- CreateIndex
CREATE INDEX "AuditTrail_userId_idx" ON "AuditTrail"("userId");

-- CreateIndex
CREATE INDEX "AuditTrail_action_idx" ON "AuditTrail"("action");

-- CreateIndex
CREATE INDEX "AuditTrail_createdAt_idx" ON "AuditTrail"("createdAt");

-- CreateIndex
CREATE INDEX "TST_Lock_userId_idx" ON "TST_Lock"("userId");

-- CreateIndex
CREATE INDEX "TST_Lock_agreementId_idx" ON "TST_Lock"("agreementId");

-- CreateIndex
CREATE INDEX "TST_Lock_released_idx" ON "TST_Lock"("released");

-- CreateIndex
CREATE UNIQUE INDEX "TST_Lock_contractLockId_key" ON "TST_Lock"("contractLockId");

-- CreateIndex
CREATE INDEX "TST_Stake_userId_idx" ON "TST_Stake"("userId");

-- CreateIndex
CREATE INDEX "TST_Stake_active_idx" ON "TST_Stake"("active");

-- CreateIndex
CREATE INDEX "TST_Stake_tier_idx" ON "TST_Stake"("tier");

-- CreateIndex
CREATE UNIQUE INDEX "TST_Stake_contractStakeId_key" ON "TST_Stake"("contractStakeId");

-- CreateIndex
CREATE INDEX "EntityAccessTier_userId_idx" ON "EntityAccessTier"("userId");

-- CreateIndex
CREATE INDEX "EntityAccessTier_entityType_idx" ON "EntityAccessTier"("entityType");

-- CreateIndex
CREATE UNIQUE INDEX "EntityAccessTier_userId_entityType_key" ON "EntityAccessTier"("userId", "entityType");

-- CreateIndex
CREATE UNIQUE INDEX "FeatureFlag_name_key" ON "FeatureFlag"("name");

-- CreateIndex
CREATE INDEX "FeatureFlag_name_idx" ON "FeatureFlag"("name");

-- AddForeignKey
ALTER TABLE "Wallet" ADD CONSTRAINT "Wallet_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Transaction" ADD CONSTRAINT "Transaction_walletId_fkey" FOREIGN KEY ("walletId") REFERENCES "Wallet"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Strategy" ADD CONSTRAINT "Strategy_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StrategyDecision" ADD CONSTRAINT "StrategyDecision_strategyId_fkey" FOREIGN KEY ("strategyId") REFERENCES "Strategy"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "P2PAgreement" ADD CONSTRAINT "P2PAgreement_borrowerId_fkey" FOREIGN KEY ("borrowerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "P2PAgreement" ADD CONSTRAINT "P2PAgreement_lenderId_fkey" FOREIGN KEY ("lenderId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "APIKey" ADD CONSTRAINT "APIKey_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PerformanceMetric" ADD CONSTRAINT "PerformanceMetric_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AuditTrail" ADD CONSTRAINT "AuditTrail_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TST_Lock" ADD CONSTRAINT "TST_Lock_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TST_Lock" ADD CONSTRAINT "TST_Lock_agreementId_fkey" FOREIGN KEY ("agreementId") REFERENCES "P2PAgreement"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TST_Stake" ADD CONSTRAINT "TST_Stake_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "EntityAccessTier" ADD CONSTRAINT "EntityAccessTier_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
