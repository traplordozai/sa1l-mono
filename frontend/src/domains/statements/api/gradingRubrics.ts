// frontend/src/domains/statements/api/gradingRubrics.ts
import { useQuery } from 'react-query';
import { GradingRubric } from '../types';
import apiClient from '../../../core/api/client';

// Query keys
const RUBRICS_KEY = 'grading-rubrics';
const ACTIVE_RUBRICS_KEY = 'active-grading-rubrics';
const AREA_RUBRIC_KEY = 'area-grading-rubric';

// Get all grading rubrics
export const useGradingRubrics = () => {
  return useQuery<GradingRubric[], Error>(
    RUBRICS_KEY,
    async () => {
      const response = await apiClient.get('/grading-rubrics/');
      return response.data;
    }
  );
};

// Get active grading rubrics
export const useActiveGradingRubrics = () => {
  return useQuery<GradingRubric[], Error>(
    ACTIVE_RUBRICS_KEY,
    async () => {
      const response = await apiClient.get('/grading-rubrics/active/');
      return response.data;
    }
  );
};

// Get rubric for an area of law
export const useAreaGradingRubric = (areaId: string) => {
  return useQuery<GradingRubric, Error>(
    [AREA_RUBRIC_KEY, areaId],
    async () => {
      const response = await apiClient.get(`/grading-rubrics/for_area/?area_id=${areaId}`);
      return response.data;
    },
    {
      enabled: !!areaId, // Only run if areaId is provided
      onError: () => {
        // If no rubric found, just return null
        return null;
      }
    }
  );
};