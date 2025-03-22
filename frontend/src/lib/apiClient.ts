/**
 * API client for making authenticated requests to the backend
 */
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
// Make sure to install axios with: npm install axios

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config: { headers: { Authorization: string; }; }) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => Promise.reject(error)
);

// Response interceptor for handling token refresh
apiClient.interceptors.response.use(
  (response: any) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // If error is 401 and we haven't already tried to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          // No refresh token, redirect to login
          window.location.href = '/';
          return Promise.reject(error);
        }

        // Get new access token
        const response = await axios.post(
          `${apiClient.defaults.baseURL}/token/refresh/`,
          { refresh: refreshToken }
        );

        // Update tokens in storage
        localStorage.setItem('access_token', response.data.access);

        // Update authorization header and retry original request
        apiClient.defaults.headers.common.Authorization = `Bearer ${response.data.access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh token expired or invalid, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }

    // Extract error message for better error handling
    const errorMessage =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.response?.data?.error ||
      error.message ||
      'Unknown error occurred';

    // Convert to Error object with the message
    const enhancedError = new Error(errorMessage);

    // Add original error properties
    (enhancedError as any).status = error.response?.status;
    (enhancedError as any).data = error.response?.data;

    return Promise.reject(enhancedError);
  }
);

export default apiClient;