// frontend/src/domains/statements/api/statements.ts
import { useMutation, useQuery, useQueryClient } from 'react-query';
import {
  Statement,
  CreateStatementRequest,
  UpdateStatementRequest,
  GradeStatementRequest,
  GradingStatistics
} from '../types';
import apiClient from '../../../core/api/client';

// Query keys
const STATEMENTS_KEY = 'statements';
const STATEMENT_KEY = 'statement';
const UNGRADED_STATEMENTS_KEY = 'ungraded-statements';
const GRADING_STATISTICS_KEY = 'grading-statistics';

// Get all statements with optional filters
export const useStatements = (filters?: {
  student?: string;
  area_of_law?: string;
  graded?: boolean;
  search?: string;
}) => {
  const queryString = new URLSearchParams();

  if (filters?.student) {
    queryString.append('student', filters.student);
  }

  if (filters?.area_of_law) {
    queryString.append('area_of_law', filters.area_of_law);
  }

  if (filters?.graded !== undefined) {
    queryString.append('graded', filters.graded.toString());
  }

  if (filters?.search) {
    queryString.append('search', filters.search);
  }

  const url = `/statements/?${queryString.toString()}`;

  return useQuery<Statement[], Error>(
    [STATEMENTS_KEY, filters],
    async () => {
      const response = await apiClient.get(url);
      return response.data;
    }
  );
};

// Get a single statement by ID
export const useStatement = (id: string) => {
  return useQuery<Statement, Error>(
    [STATEMENT_KEY, id],
    async () => {
      const response = await apiClient.get(`/statements/${id}/`);
      return response.data;
    },
    {
      enabled: !!id // Only run if ID is provided
    }
  );
};

// Get ungraded statements
export const useUngradedStatements = () => {
  return useQuery<Statement[], Error>(
    UNGRADED_STATEMENTS_KEY,
    async () => {
      const response = await apiClient.get('/statements/ungraded/');
      return response.data;
    }
  );
};

// Get grading statistics
export const useGradingStatistics = () => {
  return useQuery<GradingStatistics, Error>(
    GRADING_STATISTICS_KEY,
    async () => {
      const response = await apiClient.get('/statements/statistics/');
      return response.data;
    }
  );
};

// Create a new statement
export const useCreateStatement = () => {
  const queryClient = useQueryClient();

  return useMutation<Statement, Error, CreateStatementRequest>(
    async (data: CreateStatementRequest) => {
      const response = await apiClient.post('/statements/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(STATEMENTS_KEY);
      }
    }
  );
};

// Update an existing statement
export const useUpdateStatement = (id: string) => {
  const queryClient = useQueryClient();

  return useMutation<Statement, Error, UpdateStatementRequest>(
    async (data: UpdateStatementRequest) => {
      const response = await apiClient.patch(`/statements/${id}/`, data);
      return response.data;
    },
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries([STATEMENT_KEY, id]);
        queryClient.invalidateQueries(STATEMENTS_KEY);
      }
    }
  );
};

// Delete a statement
export const useDeleteStatement = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>(
    async (id: string) => {
      await apiClient.delete(`/statements/${id}/`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(STATEMENTS_KEY);
      }
    }
  );
};

// Grade a statement
export const useGradeStatement = (id: string) => {
  const queryClient = useQueryClient();

  return useMutation<Statement, Error, GradeStatementRequest>(
    async (data: GradeStatementRequest) => {
      const response = await apiClient.post(`/statements/${id}/grade/`, data);
    },
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries([STATEMENT_KEY, id]);
        queryClient.invalidateQueries(STATEMENTS_KEY);
        queryClient.invalidateQueries(UNGRADED_STATEMENTS_KEY);
        queryClient.invalidateQueries(GRADING_STATISTICS_KEY);
      }
    }
  );
};