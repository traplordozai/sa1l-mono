// frontend/src/domains/dashboard/api/dashboardApi.ts
import { apiClient } from '../../../shared/api/apiClient';
import { DashboardStats, ActivityItem } from '../types';
import { API_ENDPOINTS } from '../../../config/apiConfig';

export const fetchDashboardStats = async (): Promise<DashboardStats> => {
  const response = await apiClient.get<DashboardStats>(API_ENDPOINTS.DASHBOARD.STATS);
  return response.data;
};

export const fetchDashboardActivity = async (limit: number = 10): Promise<ActivityItem[]> => {
  const response = await apiClient.get<ActivityItem[]>(
    `${API_ENDPOINTS.DASHBOARD.ACTIVITY}?limit=${limit}`
  );
  return response.data;
};

export const fetchPublicStats = async (): Promise<Partial<DashboardStats>> => {
  const response = await apiClient.get<Partial<DashboardStats>>(
    '/public/dashboard/stats/'
  );
  return response.data;
};