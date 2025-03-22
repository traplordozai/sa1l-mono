// src/config/apiConfig.ts
/**
 * Centralized API endpoint configuration
 */

/**
 * Get the base API URL based on current environment
 */
export const getApiBaseUrl = (): string => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // For local development, connect to port 8000
    return `${protocol}//${hostname}:8000/api`;
  } else {
    // For production, use same hostname but with API path
    return `${protocol}//${hostname}/api`;
  }
};

/**
 * API endpoints for various services
 */
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    REFRESH: '/token/refresh/',
    VERIFY: '/token/verify/',
  },
  STUDENTS: {
    LIST: '/students/',
    DETAIL: (id: string) => `/students/${id}/`,
    PROFILE: (id: string) => `/students/${id}/profile/`,
    IMPORT_CSV: '/students/import_csv/',
    UPLOAD_GRADES: (id: string) => `/students/${id}/upload_grades_pdf/`,
  },
  ORGANIZATIONS: {
    LIST: '/organizations/',
    DETAIL: (id: string) => `/organizations/${id}/`,
    IMPORT_CSV: '/organizations/import_csv/',
  },
  MATCHING: {
    ROUNDS: '/matching-rounds/',
    RUN_ALGORITHM: (id: string) => `/matching-rounds/${id}/run_algorithm/`,
    MATCHES: '/matches/',
  },
  DASHBOARD: {
    STATS: '/dashboard/stats/',
    ACTIVITY: '/dashboard/activity/',
  },
  SETTINGS: {
    LIST: '/settings/',
    BY_CATEGORY: '/settings/by_category/',
  },
};

export default {
  getApiBaseUrl,
  API_ENDPOINTS
};