import { useAuthStore } from "@/shared/stores/authStore";

export const useAuth = () => {
  const token = useAuthStore((s) => s.token);
  return {
    token,
    isAuthenticated: !!token,
  };
};