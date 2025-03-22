import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LoginCredentials, RegisterData, AuthTokens, User } from '../types';
import { login, register, refreshToken, logout } from '../services/authService';
import useLocalStorage from './useLocalStorage';

export interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export const useAuth = (): AuthContextType => {
  const [user, setUser] = useLocalStorage<User | null>('user', null);
  const [tokens, setTokens] = useLocalStorage<AuthTokens | null>('tokens', null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshTimer, setRefreshTimer] = useState<NodeJS.Timeout | null>(null);

  const navigate = useNavigate();
  const location = useLocation();

  // Check if user is authenticated based on stored tokens
  const isAuthenticated = !!tokens?.access_token && !!user;

  // Clear auth error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Set up automatic token refresh
  useEffect(() => {
    if (tokens?.access_token && tokens?.refresh_token) {
      // Calculate when to refresh token (5 minutes before expiry)
      const expiresIn = tokens.expires_in || 3600; // Default to 1 hour
      const refreshTime = (expiresIn - 300) * 1000; // Convert to milliseconds

      // Set up timer to refresh token
      const timer = setTimeout(async () => {
        try {
          const result = await refreshToken(tokens.refresh_token);
          setTokens(result.tokens);
          setUser(result.user);
        } catch (err) {
          // If refresh fails, log out
          console.error('Failed to refresh token:', err);
          handleLogout();
        }
      }, refreshTime);

      setRefreshTimer(timer);

      // Clean up timer on unmount
      return () => {
        if (refreshTimer) {
          clearTimeout(refreshTimer);
        }
      };
    }
  }, [tokens]);

  // Handle login
  const handleLogin = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await login(credentials);
      setTokens(result.tokens);
      setUser(result.user);

      // Redirect to dashboard based on user role
      const role = result.user.primary_role;
      if (role === 'admin') {
        navigate('/admin/dashboard');
      } else if (role === 'faculty') {
        navigate('/faculty/dashboard');
      } else if (role === 'student') {
        navigate('/student/dashboard');
      } else if (role === 'organization') {
        navigate('/organization/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle registration
  const handleRegister = async (data: RegisterData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await register(data);
      setTokens(result.tokens);
      setUser(result.user);

      // Redirect to dashboard based on user role
      const role = result.user.primary_role;
      if (role === 'admin') {
        navigate('/admin/dashboard');
      } else if (role === 'faculty') {
        navigate('/faculty/dashboard');
      } else if (role === 'student') {
        navigate('/student/dashboard');
      } else if (role === 'organization') {
        navigate('/organization/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle logout
  const handleLogout = async () => {
    setIsLoading(true);
    setError(null);

    try {
      if (tokens?.access_token) {
        await logout(tokens.access_token);
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // Clear user data and tokens regardless of API call success
      setUser(null);
      setTokens(null);

      // Clear any refresh timer
      if (refreshTimer) {
        clearTimeout(refreshTimer);
        setRefreshTimer(null);
      }

      // Redirect to login page
      navigate('/login', { state: { from: location } });

      setIsLoading(false);
    }
  };

  return {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    clearError,
  };
};

export default useAuth;