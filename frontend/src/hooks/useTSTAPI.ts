/**
 * useTSTAPI - React hook for TST API integration
 * Handles all API calls to TST endpoints
 */

import { useState, useCallback } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface UseTSTAPIState {
  loading: boolean;
  error: string | null;
}

export interface LockResponse {
  lock_id: string;
  user_id: string;
  amount: number;
  locked_until: string;
  tx_hash: string;
  contract_lock_id: string;
  created_at: string;
}

export interface UpgradeTierResponse {
  stake_id: string;
  user_id: string;
  tier: number;
  amount: number;
  expires_at: string;
  tx_hash: string;
  contract_stake_id: string;
  benefits: string[];
  created_at: string;
}

export interface ReserveComputeResponse {
  reservation_id: string;
  user_id: string;
  entity_type: number;
  entity_id: string;
  quota_reserved: number;
  quota_remaining_today: number;
  reservation_expires_at: string;
  contract_res_id: string | null;
  created_at: string;
}

export interface TierInfo {
  tier: number;
  required_tst: number;
  duration_days: number;
  benefits: string[];
}

export interface RequirementResponse {
  action: string;
  requirements: {
    action: string;
    description: string;
    tiers_available: TierInfo[];
    min_balance_required: number;
  };
}

export interface TSTAccessResponse {
  user_id: string;
  total_tst_balance: number;
  available_tst: number;
  locked_tst: number;
  staked_tst: number;
  current_tier: number | null;
  tier_expires_at: string | null;
  active_locks: Array<{
    lock_id: string;
    amount: number;
    locked_until: string;
    agreement_id?: string;
  }>;
  active_stakes: Array<{
    stake_id: string;
    tier: number;
    amount: number;
    expires_at: string;
  }>;
  entity_quotas: Array<{
    entity_type: number;
    quota_today: number;
    quota_used_today: number;
    quota_remaining: number;
    last_reset: string;
  }>;
}

export const useTSTAPI = () => {
  const [state, setState] = useState<UseTSTAPIState>({
    loading: false,
    error: null,
  });

  const handleError = (error: unknown): string => {
    if (error instanceof Error) return error.message;
    if (typeof error === 'string') return error;
    return 'An unknown error occurred';
  };

  /**
   * Lock TST for P2P agreement
   */
  const lockTSTForAgreement = useCallback(
    async (
      agreementId: string,
      amount: number
    ): Promise<LockResponse | null> => {
      setState({ loading: true, error: null });
      try {
        const response = await fetch(
          `${API_BASE_URL}/p2p/${agreementId}/lock-tst`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
            },
            body: JSON.stringify({
              amount,
              agreement_id: agreementId,
            }),
          }
        );

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'Failed to lock TST');
        }

        const data = await response.json();
        setState({ loading: false, error: null });
        return data;
      } catch (error) {
        const errorMsg = handleError(error);
        setState({ loading: false, error: errorMsg });
        return null;
      }
    },
    []
  );

  /**
   * Upgrade access tier
   */
  const upgradeTier = useCallback(
    async (
      strategyId: string,
      tier: number
    ): Promise<UpgradeTierResponse | null> => {
      setState({ loading: true, error: null });
      try {
        const response = await fetch(
          `${API_BASE_URL}/strategies/${strategyId}/upgrade-tier`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
            },
            body: JSON.stringify({
              tier,
              strategy_id: strategyId,
            }),
          }
        );

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'Failed to upgrade tier');
        }

        const data = await response.json();
        setState({ loading: false, error: null });
        return data;
      } catch (error) {
        const errorMsg = handleError(error);
        setState({ loading: false, error: errorMsg });
        return null;
      }
    },
    []
  );

  /**
   * Reserve entity compute quota
   */
  const reserveComputeQuota = useCallback(
    async (
      entityId: string,
      entityType: number
    ): Promise<ReserveComputeResponse | null> => {
      setState({ loading: true, error: null });
      try {
        const response = await fetch(
          `${API_BASE_URL}/entities/${entityId}/reserve-compute`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
            },
            body: JSON.stringify({
              entity_type: entityType,
              entity_id: entityId,
            }),
          }
        );

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'Failed to reserve quota');
        }

        const data = await response.json();
        setState({ loading: false, error: null });
        return data;
      } catch (error) {
        const errorMsg = handleError(error);
        setState({ loading: false, error: errorMsg });
        return null;
      }
    },
    []
  );

  /**
   * Get TST requirements for an action
   */
  const getTSTRequirements = useCallback(
    async (action: string): Promise<RequirementResponse | null> => {
      setState({ loading: true, error: null });
      try {
        const response = await fetch(`${API_BASE_URL}/tst/requirements/${action}`);

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'Failed to fetch requirements');
        }

        const data = await response.json();
        setState({ loading: false, error: null });
        return data;
      } catch (error) {
        const errorMsg = handleError(error);
        setState({ loading: false, error: errorMsg });
        return null;
      }
    },
    []
  );

  /**
   * Get user's TST access status
   */
  const getTSTAccessStatus = useCallback(
    async (userId: string): Promise<TSTAccessResponse | null> => {
      setState({ loading: true, error: null });
      try {
        const response = await fetch(`${API_BASE_URL}/tst/access/${userId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'Failed to fetch access status');
        }

        const data = await response.json();
        setState({ loading: false, error: null });
        return data;
      } catch (error) {
        const errorMsg = handleError(error);
        setState({ loading: false, error: errorMsg });
        return null;
      }
    },
    []
  );

  /**
   * Health check
   */
  const healthCheck = useCallback(async (): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/tst/health`);
      return response.ok;
    } catch {
      return false;
    }
  }, []);

  return {
    state,
    lockTSTForAgreement,
    upgradeTier,
    reserveComputeQuota,
    getTSTRequirements,
    getTSTAccessStatus,
    healthCheck,
  };
};

export default useTSTAPI;
