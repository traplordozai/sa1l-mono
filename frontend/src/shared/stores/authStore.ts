// frontend/src/shared/stores/authStore.ts
import create from 'zustand';
import { loginService, registerService, refreshTokenService, verifyTokenService } from '../api/authService';

interface User {
  id: number;
  email: string;
  role: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    role: string;
    orgName?: string;
  }) => Promise<void>;
  logout: () => void;
  verifyAuth: () => Promise<boolean>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });

    try {
      const response = await loginService({ email, password });
      const { access, refresh, user } = response.data;

      // Store tokens in localStorage
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_role', user.role);
      localStorage.setItem('user_id', user.id.toString());
      localStorage.setItem('user_email', user.email);

      set({
        user,
        isAuthenticated: true,
        isLoading: false
      });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || error.message || 'Authentication failed'
      });
      throw error;
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null });

    try {
      const response = await registerService(userData);
      const { access, refresh, user } = response.data;

      // Store tokens in localStorage
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_role', user.role);
      localStorage.setItem('user_id', user.id.toString());
      localStorage.setItem('user_email', user.email);

      set({
        user,
        isAuthenticated: true,
        isLoading: false
      });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || error.message || 'Registration failed'
      });
      throw error;
    }
  },

  logout: () => {
    // Clear localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');

    // Reset state
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
  },

  verifyAuth: async () => {
    const accessToken = localStorage.getItem('access_token');

    if (!accessToken) {
      return false;
    }

    try {
      await verifyTokenService(accessToken);

      // If verification is successful, update user state if needed
      if (!get().user) {
        const userId = localStorage.getItem('user_id');
        const userEmail = localStorage.getItem('user_email');
        const userRole = localStorage.getItem('user_role');

        if (userId && userEmail && userRole) {
          set({
            user: {
              id: parseInt(userId),
              email: userEmail,
              role: userRole
            },
            isAuthenticated: true
          });
        }
      }

      return true;
    } catch (error) {
      // Try to refresh the token
      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        get().logout();
        return false;
      }

      try {
        const response = await refreshTokenService(refreshToken);
        localStorage.setItem('access_token', response.data.access);
        return true;
      } catch (refreshError) {
        get().logout();
        return false;
      }
    }
  },

  clearError: () => set({ error: null })
}));