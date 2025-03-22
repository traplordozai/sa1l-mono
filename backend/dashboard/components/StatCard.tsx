// frontend/src/domains/dashboard/components/StatCard.tsx
import React from 'react';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/solid';

interface StatCardProps {
  title: string;
  value: number | string;
  description?: string;
  change?: {
    value: number;
    direction: 'increase' | 'decrease';
  };
  icon?: React.ReactNode;
  colorScheme?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'gray';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  description,
  change,
  icon,
  colorScheme = 'blue',
}) => {
  const colorMap = {
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-500',
      text: 'text-blue-700',
      iconBg: 'bg-blue-100',
      iconText: 'text-blue-500',
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-500',
      text: 'text-green-700',
      iconBg: 'bg-green-100',
      iconText: 'text-green-500',
    },
    yellow: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-500',
      text: 'text-yellow-700',
      iconBg: 'bg-yellow-100',
      iconText: 'text-yellow-500',
    },
    red: {
      bg: 'bg-red-50',
      border: 'border-red-500',
      text: 'text-red-700',
      iconBg: 'bg-red-100',
      iconText: 'text-red-500',
    },
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-500',
      text: 'text-purple-700',
      iconBg: 'bg-purple-100',
      iconText: 'text-purple-500',
    },
    gray: {
      bg: 'bg-gray-50',
      border: 'border-gray-300',
      text: 'text-gray-700',
      iconBg: 'bg-gray-100',
      iconText: 'text-gray-500',
    },
  };

  const colors = colorMap[colorScheme];

  return (
    <div className={`${colors.bg} p-6 rounded-lg shadow-sm border-l-4 ${colors.border}`}>
      <div className="flex items-center">
        {icon && (
          <div className={`mr-4 p-3 rounded-full ${colors.iconBg} ${colors.iconText}`}>
            {icon}
          </div>
        )}
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className={`text-2xl font-bold ${colors.text}`}>{value}</p>

          {(description || change) && (
            <div className="mt-1 flex items-center">
              {change && (
                <span
                  className={`mr-2 flex items-center text-sm ${
                    change.direction === 'increase' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {change.direction === 'increase' ? (
                    <ArrowUpIcon className="h-4 w-4 mr-1" />
                  ) : (
                    <ArrowDownIcon className="h-4 w-4 mr-1" />
                  )}
                  {change.value}%
                </span>
              )}

              {description && (
                <span className="text-sm text-gray-500">{description}</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};