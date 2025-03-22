import api from '../../../services/api';
import { ImportLog, ImportDetail, ImportResponse, ImportStatusResponse } from '../types';

/**
 * Import students from a CSV file
 */
export const importStudentsCsv = async (formData: FormData): Promise<ImportResponse> => {
  const response = await api.post('/imports/students', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Import organizations from a CSV file
 */
export const importOrganizationsCsv = async (formData: FormData): Promise<ImportResponse> => {
  const response = await api.post('/imports/organizations', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Import student grades from a PDF file
 */
export const importGradesPdf = async (formData: FormData): Promise<ImportResponse> => {
  const response = await api.post('/imports/grades', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Get import status by ID
 */
export const getImportStatus = async (importLogId: string): Promise<ImportStatusResponse> => {
  const response = await api.get(`/imports/status?import_log_id=${importLogId}`);
  return response.data;
};

/**
 * Get all import logs
 */
export const getImportLogs = async (): Promise<ImportLog[]> => {
  const response = await api.get('/imports/logs');
  return response.data;
};

/**
 * Get details for a specific import
 */
export const getImportDetails = async (importLogId: string): Promise<ImportDetail[]> => {
  const response = await api.get(`/imports/logs/${importLogId}/details`);
  return response.data;
};