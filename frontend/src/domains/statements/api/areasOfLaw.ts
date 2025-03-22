// frontend/src/domains/statements/api/areasOfLaw.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { AreaOfLaw } from '../types';
import apiClient from '../../../core/api/client';

// Query keys
const AREAS_KEY = 'areas-of-law';
const AREAS_WITH_COUNTS_KEY = 'areas-of-law-with-counts';

// Get all areas of law
export const useAreasOfLaw = () => {
  return useQuery<AreaOfLaw[], Error>(
    AREAS_KEY,
    async () => {
      const response = await apiClient.get('/areas-of-law/');
      return response.data;
    }
  );
};

// Get areas of law with statement counts
export const useAreasOfLawWithCounts = () => {
  return useQuery<AreaOfLaw[], Error>(
    AREAS_WITH_COUNTS_KEY,
    async () => {
      const response = await apiClient.get('/areas-of-law/with_counts/');
      return response.data;
    }
  );
};

// Create a new area of law (admin only)
export const useCreateAreaOfLaw = () => {
  const queryClient = useQueryClient();

  return useMutation<AreaOfLaw, Error, { name: string; description?: string }>(
    async (data) => {
      const response = await apiClient.post('/areas-of-law/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(AREAS_KEY);
        queryClient.invalidateQueries(AREAS_WITH_COUNTS_KEY);
      }
    }
  );
};