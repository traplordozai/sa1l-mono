// frontend/src/shared/api/authService.ts
import axios from 'axios';
import { API_ENDPOINTS } from '../../config/apiConfig';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: string;
  orgName?: string;
}

interface AuthResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    email: string;
    role: string;
  };
}

const API_URL = typeof window !== 'undefined'
  ? `${window.location.protocol}//${window.location.hostname}${window.location.hostname === 'localhost' ? ':8000' : ''}/api`
  : 'http://localhost:8000/api';

export const loginService = (credentials: LoginCredentials) => {
  return axios.post<AuthResponse>(`${API_URL}${API_ENDPOINTS.AUTH.LOGIN}`, credentials);
};

export const registerService = (data: RegisterData) => {
  return axios.post<AuthResponse>(`${API_URL}${API_ENDPOINTS.AUTH.REGISTER}`, data);
};

export const refreshTokenService = (refreshToken: string) => {
  return axios.post<{access: string}>(`${API_URL}${API_ENDPOINTS.AUTH.REFRESH}`, {
    refresh: refreshToken
  });
};

export const verifyTokenService = (token: string) => {
  return axios.post(`${API_URL}${API_ENDPOINTS.AUTH.VERIFY}`, { token });
};