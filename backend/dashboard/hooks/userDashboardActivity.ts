// frontend/src/domains/dashboard/hooks/useDashboardActivity.ts
import { useQuery } from 'react-query';
import { fetchDashboardActivity } from '../api/dashboardApi';

export const useDashboardActivity = (limit: number = 10) => {
  return useQuery(
    ['dashboardActivity', limit],
    () => fetchDashboardActivity(limit),
    {
      refetchInterval: 2 * 60 * 1000, // Refetch every 2 minutes
      staleTime: 30 * 1000, // Consider data stale after 30 seconds
    }
  );
};