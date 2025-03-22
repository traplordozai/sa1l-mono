// frontend/src/domains/dashboard/hooks/useDashboardStats.ts
import { useQuery } from 'react-query';
import { fetchDashboardStats } from '../api/dashboardApi';

export const useDashboardStats = () => {
  return useQuery(
    ['dashboardStats'],
    fetchDashboardStats,
    {
      refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
      staleTime: 60 * 1000, // Consider data stale after 1 minute
    }
  );
};