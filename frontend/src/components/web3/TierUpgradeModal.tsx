/**
 * Tier Upgrade Modal - Allow users to upgrade their access tier
 * Components: Tier selection, requirements display, upgrade button
 */

import React, { useState } from 'react';

export interface TierOption {
  tier: number;
  required_tst: number;
  duration_days: number;
  benefits: string[];
}

export interface TierUpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpgrade: (tier: number) => Promise<void>;
  currentTier: number | null;
  userBalance: number;
  tiers: TierOption[];
  loading?: boolean;
  error?: string;
}

export const TierUpgradeModal: React.FC<TierUpgradeModalProps> = ({
  isOpen,
  onClose,
  onUpgrade,
  currentTier,
  userBalance,
  tiers,
  loading = false,
  error = '',
}) => {
  const [selectedTier, setSelectedTier] = useState<number | null>(null);
  const [upgrading, setUpgrading] = useState(false);

  if (!isOpen) return null;

  const handleUpgrade = async () => {
    if (!selectedTier) return;

    setUpgrading(true);
    try {
      await onUpgrade(selectedTier);
      setSelectedTier(null);
      onClose();
    } finally {
      setUpgrading(false);
    }
  };

  const selectedTierData = tiers.find((t) => t.tier === selectedTier);
  const hasEnoughBalance = selectedTierData
    ? userBalance >= selectedTierData.required_tst
    : false;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
          <h2 className="text-xl font-bold text-white">Upgrade Access Tier</h2>
          <p className="text-blue-100 text-sm mt-1">
            Unlock more compute quota and benefits
          </p>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Current Balance */}
          <div className="mb-6 bg-blue-50 rounded-lg p-4 border border-blue-100">
            <p className="text-sm text-gray-600">Current TST Balance</p>
            <p className="text-2xl font-bold text-blue-600">{userBalance.toFixed(2)}</p>
          </div>

          {/* Tier Selection */}
          <div className="space-y-3 mb-6">
            <p className="font-semibold text-gray-700">Select Tier</p>
            {tiers.map((tier) => {
              const canAfford = userBalance >= tier.required_tst;
              const isCurrentTier = currentTier === tier.tier;

              return (
                <button
                  key={tier.tier}
                  onClick={() => !isCurrentTier && setSelectedTier(tier.tier)}
                  disabled={isCurrentTier || loading}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    isCurrentTier
                      ? 'border-green-500 bg-green-50 cursor-default'
                      : selectedTier === tier.tier
                      ? 'border-blue-500 bg-blue-50'
                      : canAfford
                      ? 'border-gray-200 bg-white hover:border-blue-400'
                      : 'border-red-200 bg-red-50 opacity-75 cursor-not-allowed'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-semibold text-gray-800">
                        Tier {tier.tier}
                        {isCurrentTier && (
                          <span className="ml-2 text-xs bg-green-500 text-white px-2 py-1 rounded">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {tier.required_tst} TST • {tier.duration_days}-day duration
                      </p>
                      <div className="mt-2 space-y-1">
                        {tier.benefits.map((benefit, idx) => (
                          <p key={idx} className="text-xs text-gray-700">
                            • {benefit}
                          </p>
                        ))}
                      </div>
                    </div>
                    <div className="text-right">
                      {!canAfford && !isCurrentTier && (
                        <span className="text-xs text-red-600 font-semibold">
                          Insufficient
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Selected Tier Details */}
          {selectedTierData && (
            <div className="mb-6 bg-amber-50 rounded-lg p-4 border border-amber-200">
              <p className="text-sm text-gray-600">Required TST</p>
              <p className="text-lg font-bold text-amber-700">
                {selectedTierData.required_tst} TST
              </p>
              <p className="text-xs text-amber-600 mt-2">
                {hasEnoughBalance
                  ? '✓ You have sufficient balance'
                  : `✗ Need ${(selectedTierData.required_tst - userBalance).toFixed(2)} more TST`}
              </p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={upgrading}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleUpgrade}
              disabled={!selectedTier || !hasEnoughBalance || upgrading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {upgrading ? 'Upgrading...' : 'Upgrade Tier'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TierUpgradeModal;
