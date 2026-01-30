/**
 * TST Access Status Widget - Display user's complete TST access status
 * Shows: balances, tier, locks, stakes, quotas
 */

import React, { useState, useEffect } from 'react';

export interface TSTBalances {
  total_balance: number;
  available: number;
  locked: number;
  staked: number;
}

export interface TierStatus {
  tier: number | null;
  expires_at: string | null;
}

export interface Lock {
  lock_id: string;
  amount: number;
  locked_until: string;
  agreement_id?: string;
}

export interface Stake {
  stake_id: string;
  tier: number;
  amount: number;
  expires_at: string;
}

export interface EntityQuota {
  entity_type: number;
  quota_today: number;
  quota_used_today: number;
  quota_remaining: number;
  last_reset: string;
}

export interface TSTAccessStatusProps {
  userId: string;
  balances: TSTBalances;
  tier: TierStatus;
  locks: Lock[];
  stakes: Stake[];
  quotas: EntityQuota[];
  loading?: boolean;
  error?: string;
  onOpenUpgrade?: () => void;
}

const entityTypeNames: Record<number, string> = {
  1: 'Risk',
  2: 'Strategy',
  3: 'Memory',
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const getTimeUntil = (dateString: string): string => {
  const now = new Date();
  const date = new Date(dateString);
  const diff = date.getTime() - now.getTime();

  if (diff < 0) return 'Expired';

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h`;
  return 'Expiring soon';
};

export const TSTAccessStatus: React.FC<TSTAccessStatusProps> = ({
  userId,
  balances,
  tier,
  locks,
  stakes,
  quotas,
  loading = false,
  error = '',
  onOpenUpgrade,
}) => {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center">
        <div className="inline-block animate-spin">⏳</div>
        <p className="mt-2 text-gray-600">Loading TST access status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Balance Overview */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg p-6 text-white">
        <h2 className="text-lg font-semibold mb-4">TST Access Status</h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-blue-100 text-sm">Total Balance</p>
            <p className="text-2xl font-bold">{balances.total_balance.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-blue-100 text-sm">Available</p>
            <p className="text-2xl font-bold text-green-300">
              {balances.available.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-blue-100 text-sm">Locked</p>
            <p className="text-2xl font-bold text-yellow-300">
              {balances.locked.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-blue-100 text-sm">Staked</p>
            <p className="text-2xl font-bold text-orange-300">
              {balances.staked.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* Current Tier */}
      <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">Current Access Tier</h3>
            <p className="text-sm text-gray-600 mt-1">
              {tier.tier ? (
                <>
                  <span className="text-2xl font-bold text-blue-600">Tier {tier.tier}</span>
                  {tier.expires_at && (
                    <span className="ml-4 text-sm">
                      Expires {getTimeUntil(tier.expires_at)}
                    </span>
                  )}
                </>
              ) : (
                <span className="text-gray-500">No active tier</span>
              )}
            </p>
          </div>
          <button
            onClick={onOpenUpgrade}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-semibold"
          >
            Upgrade
          </button>
        </div>
      </div>

      {/* Active Locks */}
      <div
        className="bg-white rounded-lg shadow overflow-hidden border-l-4 border-yellow-500"
      >
        <button
          onClick={() =>
            setExpandedSection(expandedSection === 'locks' ? null : 'locks')
          }
          className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div>
            <h3 className="font-semibold text-gray-800">Active Locks</h3>
            <p className="text-sm text-gray-600">
              {locks.length} lock{locks.length !== 1 ? 's' : ''}
            </p>
          </div>
          <span className="text-xl">{expandedSection === 'locks' ? '▼' : '▶'}</span>
        </button>

        {expandedSection === 'locks' && locks.length > 0 && (
          <div className="border-t border-gray-200 p-6 space-y-4">
            {locks.map((lock) => (
              <div
                key={lock.lock_id}
                className="flex items-center justify-between bg-yellow-50 rounded-lg p-4 border border-yellow-200"
              >
                <div>
                  <p className="font-semibold text-gray-800">{lock.amount} TST</p>
                  <p className="text-sm text-gray-600">
                    {lock.agreement_id && `Agreement: ${lock.agreement_id.slice(0, 8)}...`}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Until {formatDate(lock.locked_until)}
                  </p>
                </div>
                <span className="text-2xl text-yellow-600">🔒</span>
              </div>
            ))}
          </div>
        )}

        {expandedSection === 'locks' && locks.length === 0 && (
          <div className="border-t border-gray-200 p-6 text-center text-gray-500">
            No active locks
          </div>
        )}
      </div>

      {/* Active Stakes */}
      <div
        className="bg-white rounded-lg shadow overflow-hidden border-l-4 border-orange-500"
      >
        <button
          onClick={() =>
            setExpandedSection(expandedSection === 'stakes' ? null : 'stakes')
          }
          className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div>
            <h3 className="font-semibold text-gray-800">Active Stakes</h3>
            <p className="text-sm text-gray-600">
              {stakes.length} stake{stakes.length !== 1 ? 's' : ''}
            </p>
          </div>
          <span className="text-xl">{expandedSection === 'stakes' ? '▼' : '▶'}</span>
        </button>

        {expandedSection === 'stakes' && stakes.length > 0 && (
          <div className="border-t border-gray-200 p-6 space-y-4">
            {stakes.map((stake) => (
              <div
                key={stake.stake_id}
                className="flex items-center justify-between bg-orange-50 rounded-lg p-4 border border-orange-200"
              >
                <div>
                  <p className="font-semibold text-gray-800">
                    Tier {stake.tier} • {stake.amount} TST
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Expires {getTimeUntil(stake.expires_at)}
                  </p>
                </div>
                <span className="text-2xl text-orange-600">📌</span>
              </div>
            ))}
          </div>
        )}

        {expandedSection === 'stakes' && stakes.length === 0 && (
          <div className="border-t border-gray-200 p-6 text-center text-gray-500">
            No active stakes
          </div>
        )}
      </div>

      {/* Entity Quotas */}
      <div
        className="bg-white rounded-lg shadow overflow-hidden border-l-4 border-purple-500"
      >
        <button
          onClick={() =>
            setExpandedSection(expandedSection === 'quotas' ? null : 'quotas')
          }
          className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div>
            <h3 className="font-semibold text-gray-800">Entity Quotas</h3>
            <p className="text-sm text-gray-600">
              {quotas.length} entit{quotas.length !== 1 ? 'ies' : 'y'}
            </p>
          </div>
          <span className="text-xl">{expandedSection === 'quotas' ? '▼' : '▶'}</span>
        </button>

        {expandedSection === 'quotas' && quotas.length > 0 && (
          <div className="border-t border-gray-200 p-6 space-y-4">
            {quotas.map((quota) => (
              <div
                key={`quota-${quota.entity_type}`}
                className="bg-purple-50 rounded-lg p-4 border border-purple-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="font-semibold text-gray-800">
                    {entityTypeNames[quota.entity_type]}
                  </p>
                  <span className="text-sm text-gray-600">
                    {quota.quota_used_today} / {quota.quota_today}
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${(quota.quota_used_today / quota.quota_today) * 100}%`,
                    }}
                  />
                </div>

                <p className="text-xs text-gray-500 mt-2">
                  {quota.quota_remaining} remaining • Reset at UTC 00:00
                </p>
              </div>
            ))}
          </div>
        )}

        {expandedSection === 'quotas' && quotas.length === 0 && (
          <div className="border-t border-gray-200 p-6 text-center text-gray-500">
            No entity quotas allocated
          </div>
        )}
      </div>
    </div>
  );
};

export default TSTAccessStatus;
