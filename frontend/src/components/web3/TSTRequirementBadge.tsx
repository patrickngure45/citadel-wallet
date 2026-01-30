/**
 * TST Requirement Badge - Display TST requirement for an action
 * Shows: Required amount, current balance, deficit (if any)
 */

import React from 'react';

export interface TSTRequirementBadgeProps {
  requiredAmount: number;
  currentBalance: number;
  actionName: string;
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
  variant?: 'default' | 'compact' | 'inline';
}

export const TSTRequirementBadge: React.FC<TSTRequirementBadgeProps> = ({
  requiredAmount,
  currentBalance,
  actionName,
  size = 'md',
  showDetails = true,
  variant = 'default',
}) => {
  const hasEnough = currentBalance >= requiredAmount;
  const deficit = Math.max(0, requiredAmount - currentBalance);

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-2',
    lg: 'text-base px-4 py-3',
  };

  const baseClasses = sizeClasses[size];

  if (variant === 'compact') {
    return (
      <div
        className={`rounded-full font-semibold inline-flex items-center gap-1 ${baseClasses} ${
          hasEnough
            ? 'bg-green-100 text-green-700 border border-green-300'
            : 'bg-red-100 text-red-700 border border-red-300'
        }`}
      >
        <span>{hasEnough ? '✓' : '✗'}</span>
        <span>{requiredAmount} TST</span>
      </div>
    );
  }

  if (variant === 'inline') {
    return (
      <span
        className={`${baseClasses} rounded ${
          hasEnough
            ? 'bg-green-50 text-green-700 border-l-2 border-green-500'
            : 'bg-red-50 text-red-700 border-l-2 border-red-500'
        }`}
      >
        {hasEnough ? '✓' : '✗'} {requiredAmount} TST
      </span>
    );
  }

  // Default variant - detailed card
  return (
    <div
      className={`rounded-lg border-2 p-4 ${
        hasEnough
          ? 'bg-green-50 border-green-300'
          : 'bg-red-50 border-red-300'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-lg font-bold ${
              hasEnough ? 'text-green-700' : 'text-red-700'
            }`}>
              {hasEnough ? '✓' : '✗'}
            </span>
            <p className="font-semibold text-gray-800">{actionName}</p>
          </div>

          {showDetails && (
            <div className="mt-3 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Required:</span>
                <span className="font-semibold text-gray-800">
                  {requiredAmount} TST
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Your Balance:</span>
                <span
                  className={`font-semibold ${
                    hasEnough ? 'text-green-700' : 'text-red-700'
                  }`}
                >
                  {currentBalance.toFixed(2)} TST
                </span>
              </div>

              {!hasEnough && (
                <div className="flex items-center justify-between text-sm pt-2 border-t border-red-200">
                  <span className="text-red-600">Need:</span>
                  <span className="font-bold text-red-700">
                    {deficit.toFixed(2)} more
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TSTRequirementBadge;
