/**
 * Student API service for making requests to the backend
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '.venv/lib/apiClient';
import {
  Student, StudentDetailResponse, CSVImportResult, PDFImportResult, Statement
} from '../types/Student';

// Query keys for React Query
const STUDENTS_KEYS = {
  all: ['students'] as const,
  lists: () => [...STUDENTS_KEYS.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...STUDENTS_KEYS.lists(), { ...filters }] as const,
  details: () => [...STUDENTS_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...STUDENTS_KEYS.details(), id] as const,
};

/**
 * Get a list of students
 */
export const useStudents = (filters?: Record<string, any>) => {
  return useQuery({
    queryKey: STUDENTS_KEYS.list(filters || {}),
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: Student[] }>('/students/', { params: filters });
      return data.results;
    },
  });
};

/**
 * Get a single student by ID
 */
export const useStudent = (id: string) => {
  return useQuery({
    queryKey: STUDENTS_KEYS.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<StudentDetailResponse>(`/students/${id}/profile/`);
      return data;
    },
    enabled: !!id,
  });
};

/**
 * Get unmatched students
 */
export const useUnmatchedStudents = () => {
  return useQuery({
    queryKey: [...STUDENTS_KEYS.lists(), 'unmatched'],
    queryFn: async () => {
      const { data } = await apiClient.get<Student[]>('/students/unmatched/');
      return data;
    },
  });
};

/**
 * Get students needing approval
 */
export const useStudentsNeedingApproval = () => {
  return useQuery({
    queryKey: [...STUDENTS_KEYS.lists(), 'needs-approval'],
    queryFn: async () => {
      const { data } = await apiClient.get<Student[]>('/students/needs_approval/');
      return data;
    },
  });
};

/**
 * Create a new student
 */
export const useCreateStudent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (student: Partial<Student>) => {
      const { data } = await apiClient.post<Student>('/students/', student);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: STUDENTS_KEYS.lists() });
    },
  });
};

/**
 * Update an existing student
 */
export const useUpdateStudent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...student }: Partial<Student> & { id: string }) => {
      const { data } = await apiClient.put<Student>(`/students/${id}/`, student);
      return data;
    },
    onSuccess: (data: { id: string; }) => {
      queryClient.invalidateQueries({ queryKey: STUDENTS_KEYS.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: STUDENTS_KEYS.lists() });
    },
  });
};

/**
 * Delete a student
 */
export const useDeleteStudent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/students/${id}/`);
      return id;
    },
    onSuccess: (id: string) => {
      queryClient.invalidateQueries({ queryKey: STUDENTS_KEYS.detail(id) });
      queryClient.invalidateQueries({ queryKey: STUDENTS_KEYS.lists() });
    },
  });
};

/**
 * Import students from CSV
 */
export const useImportStudentsCSV = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('csv_file', file);

      const { data } = await apiClient.post<CSVImportResult>('/students/import_csv/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: STUDENTS_KEYS.lists() });
    },
  });
};

/**
 * Upload student grades from PDF
 */
export const useUploadStudentGrades = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ studentId, file }: { studentId: string; file: File }) => {
      const formData = new FormData();
      formData.append('student_id', studentId);
      formData.append('grades_pdf', file);

      const { data } = await apiClient.post<PDFImportResult>(
        `/students/${studentId}/upload_grades/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return data;
    },
    onSuccess: (data: { student_id: string; }) => {
      if (data.student_id) {
        queryClient.invalidateQueries({ queryKey: STUDENTS_KEYS.detail(data.student_id) });
      }
    },
  });
};

/**
 * Grade a student statement
 */
export const useGradeStatement = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ statementId, grade }: { statementId: string; grade: number }) => {
      const { data } = await apiClient.post<Statement>(`/statements/${statementId}/grade/`, {
        grade,
      });
      return data;
    },
    onSuccess: (data: { student: string; }) => {
      // Invalidate the student detail query to refetch the updated statement
      if (data.student) {
        queryClient.invalidateQueries({ queryKey: STUDENTS_KEYS.detail(data.student) });
      }
    },
  });
};