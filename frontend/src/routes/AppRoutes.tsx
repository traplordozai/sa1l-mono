import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "@/domains/auth/hooks/useAuth";
import LoginForm from "@/domains/auth/components/LoginForm";
import MatchingDashboard from "@/domains/matching/components/MatchingDashboard";
import OrganizationDashboard from "@/domains/matching/components/OrganizationDashboard"; // Updated path

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const AppRoutes = () => (
  <BrowserRouter basename="/v1">
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route
        path="/dashboard/matching"
        element={
          <ProtectedRoute>
            <MatchingDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard/organizations"
        element={
          <ProtectedRoute>
            <OrganizationDashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;