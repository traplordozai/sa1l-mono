import * as React from 'react';

type StatusType = 'success' | 'warning' | 'error' | 'info' | 'default';

interface StatusBadgeProps {
  status: StatusType | string;
  label: string;
  className?: string;
}

const statusClasses: Record<StatusType, string> = {
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
  default: 'bg-gray-100 text-gray-800',
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, className = '' }) => {
  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';

  // Determine the status class
  let statusClass = statusClasses.default;

  if (typeof status === 'string') {
    const normalizedStatus = status.toLowerCase();

    // Map status string to status type
    if (['active', 'approved', 'completed', 'matched', 'success'].includes(normalizedStatus)) {
      statusClass = statusClasses.success;
    } else if (['pending', 'waiting', 'in progress', 'warning'].includes(normalizedStatus)) {
      statusClass = statusClasses.warning;
    } else if (['inactive', 'rejected', 'failed', 'error'].includes(normalizedStatus)) {
      statusClass = statusClasses.error;
    } else if (['info', 'notice'].includes(normalizedStatus)) {
      statusClass = statusClasses.info;
    }
  } else {
    statusClass = statusClasses[status];
  }

  return (
    <span className={`${baseClasses} ${statusClass} ${className}`}>
      {label}
    </span>
  );
};

export default StatusBadge;