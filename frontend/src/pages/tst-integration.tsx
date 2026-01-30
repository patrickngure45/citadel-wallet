/**
 * TST Integration Demo Page
 * Shows all TST components working together
 */

import React, { useState, useEffect } from 'react';
import TierUpgradeModal from '@/components/web3/TierUpgradeModal';
import TSTAccessStatus from '@/components/web3/TSTAccessStatus';
import TSTRequirementBadge from '@/components/web3/TSTRequirementBadge';
import useTSTAPI from '@/hooks/useTSTAPI';

export default function TSTIntegrationPage() {
  const api = useTSTAPI();
  const [userId] = useState('user_demo_123'); // In production: from auth context
  const [modalOpen, setModalOpen] = useState(false);

  // State from API
  const [requirements, setRequirements] = useState<any>(null);
  const [accessStatus, setAccessStatus] = useState<any>(null);

  // UI State
  const [activeTab, setActiveTab] = useState<'overview' | 'details'>('overview');

  // Load data on mount
  useEffect(() => {
    const loadData = async () => {
      const [reqs, access] = await Promise.all([
        api.getTSTRequirements('upgrade_tier'),
        api.getTSTAccessStatus(userId),
      ]);

      if (reqs) setRequirements(reqs);
      if (access) setAccessStatus(access);
    };

    loadData();
  }, [userId, api]);

  const handleUpgradeTier = async (tier: number) => {
    const result = await api.upgradeTier(userId, tier);
    if (result) {
      // Refresh access status
      const updated = await api.getTSTAccessStatus(userId);
      if (updated) setAccessStatus(updated);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">TST Access Token</h1>
              <p className="text-gray-600 mt-1">
                Manage your access tier, locks, and compute quotas
              </p>
            </div>
            <button
              onClick={() => setModalOpen(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              Upgrade Tier
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-3 font-semibold border-b-2 transition-colors ${
              activeTab === 'overview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('details')}
            className={`px-4 py-3 font-semibold border-b-2 transition-colors ${
              activeTab === 'details'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Details & Requirements
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && accessStatus && (
          <TSTAccessStatus
            userId={userId}
            balances={{
              total_balance: accessStatus.total_tst_balance,
              available: accessStatus.available_tst,
              locked: accessStatus.locked_tst,
              staked: accessStatus.staked_tst,
            }}
            tier={{
              tier: accessStatus.current_tier,
              expires_at: accessStatus.tier_expires_at,
            }}
            locks={accessStatus.active_locks}
            stakes={accessStatus.active_stakes}
            quotas={accessStatus.entity_quotas}
            loading={api.state.loading}
            error={api.state.error || ''}
            onOpenUpgrade={() => setModalOpen(true)}
          />
        )}

        {/* Details Tab */}
        {activeTab === 'details' && requirements && (
          <div className="space-y-6">
            {/* Tier Requirements */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Tier Requirements
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {requirements.requirements.tiers_available.map(
                  (tier: any) => (
                    <div
                      key={tier.tier}
                      className="border-2 border-gray-200 rounded-lg p-6 hover:border-blue-400 transition-colors"
                    >
                      <h3 className="text-lg font-bold text-gray-900 mb-2">
                        Tier {tier.tier}
                      </h3>
                      <p className="text-2xl font-bold text-blue-600 mb-4">
                        {tier.required_tst} TST
                      </p>
                      <div className="space-y-2 mb-4">
                        {tier.benefits.map((benefit: string, idx: number) => (
                          <p key={idx} className="text-sm text-gray-700">
                            • {benefit}
                          </p>
                        ))}
                      </div>
                      <p className="text-xs text-gray-500">
                        Duration: {tier.duration_days} days
                      </p>
                    </div>
                  )
                )}
              </div>
            </div>

            {/* Action Requirements */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Action Requirements
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <TSTRequirementBadge
                  actionName="Lock P2P Agreement"
                  requiredAmount={10}
                  currentBalance={
                    accessStatus?.available_tst || 0
                  }
                  variant="default"
                  showDetails
                />

                <TSTRequirementBadge
                  actionName="Upgrade to Tier 2"
                  requiredAmount={25}
                  currentBalance={
                    accessStatus?.available_tst || 0
                  }
                  variant="default"
                  showDetails
                />

                <TSTRequirementBadge
                  actionName="Reserve Entity (Tier 1)"
                  requiredAmount={5}
                  currentBalance={
                    accessStatus?.available_tst || 0
                  }
                  variant="default"
                  showDetails
                />

                <TSTRequirementBadge
                  actionName="Upgrade to Tier 3"
                  requiredAmount={100}
                  currentBalance={
                    accessStatus?.available_tst || 0
                  }
                  variant="default"
                  showDetails
                />
              </div>
            </div>

            {/* Badge Variants */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Badge Variants
              </h2>

              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">Compact:</h3>
                  <div className="flex gap-3 flex-wrap">
                    <TSTRequirementBadge
                      actionName="Lock"
                      requiredAmount={10}
                      currentBalance={150}
                      variant="compact"
                      size="sm"
                    />
                    <TSTRequirementBadge
                      actionName="Tier 2"
                      requiredAmount={25}
                      currentBalance={150}
                      variant="compact"
                      size="md"
                    />
                    <TSTRequirementBadge
                      actionName="Tier 3"
                      requiredAmount={100}
                      currentBalance={50}
                      variant="compact"
                      size="lg"
                    />
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">Inline:</h3>
                  <div className="space-y-2">
                    <TSTRequirementBadge
                      actionName=""
                      requiredAmount={10}
                      currentBalance={150}
                      variant="inline"
                      size="sm"
                    />
                    <TSTRequirementBadge
                      actionName=""
                      requiredAmount={50}
                      currentBalance={30}
                      variant="inline"
                      size="md"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tier Upgrade Modal */}
      {requirements && (
        <TierUpgradeModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          onUpgrade={handleUpgradeTier}
          currentTier={accessStatus?.current_tier || null}
          userBalance={accessStatus?.available_tst || 0}
          tiers={requirements.requirements.tiers_available}
          loading={api.state.loading}
          error={api.state.error || ''}
        />
      )}

      {/* API Status Indicator */}
      <div className="fixed bottom-6 right-6">
        <div className="bg-white rounded-lg shadow-lg p-4 text-sm">
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                !api.state.loading && !api.state.error
                  ? 'bg-green-500'
                  : api.state.loading
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
            />
            <span className="text-gray-700">
              {api.state.loading ? 'Loading...' : api.state.error ? 'Error' : 'Connected'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
