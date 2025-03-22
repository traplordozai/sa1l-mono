// frontend/src/domains/statements/api/gradeImports.ts
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { GradeImport } from '../types';
import apiClient from '../../../core/api/client';

// Query keys
const GRADE_IMPORTS_KEY = 'grade-imports';

// Get all grade imports
export const useGradeImports = () => {
  return useQuery<GradeImport[], Error>(
    GRADE_IMPORTS_KEY,
    async () => {
      const response = await apiClient.get('/grade-imports/');
      return response.data;
    }
  );
};

// Import grades from a file
export const useImportGrades = () => {
  const queryClient = useQueryClient();

  return useMutation<
    { message: string; success_count: number; error_count: number; errors: string[] },
    Error,
    File
  >(
    async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/grade-imports/import_file/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(GRADE_IMPORTS_KEY);
        // Also invalidate related queries
        queryClient.invalidateQueries('statements');
        queryClient.invalidateQueries('ungraded-statements');
        queryClient.invalidateQueries('grading-statistics');
      }
    }
  );
};