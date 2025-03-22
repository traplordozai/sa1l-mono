// src/domains/auth/components/ProtectedRoute.tsx
import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles = ['Admin', 'admin']
}) => {
  const { isAuthenticated, isLoading, user, verifyAuth } = useAuthContext();
  const [isVerifying, setIsVerifying] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated) {
        const verified = await verifyAuth();
        setIsVerifying(false);

        if (verified && user && allowedRoles.includes(user.role)) {
          setIsAuthorized(true);
        }
      } else if (user && allowedRoles.includes(user.role)) {
        setIsAuthorized(true);
        setIsVerifying(false);
      } else {
        setIsVerifying(false);
      }
    };

    checkAuth();
  }, [isAuthenticated, user, verifyAuth, allowedRoles]);

  if (isLoading || isVerifying) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-700 mb-4"></div>
        <p className="text-gray-600">Verifying authentication...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  if (!isAuthorized) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};