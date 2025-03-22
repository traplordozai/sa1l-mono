// frontend/src/domains/matching/routes.tsx
import React from 'react';
import { Route, Routes } from 'react-router-dom';
import MatchingDashboard from './components/MatchingDashboard';
import MatchingRoundList from './components/MatchingRoundList';
import MatchingRoundDetail from './components/MatchingRoundDetail';
import MatchingRoundForm from './components/MatchingRoundForm';
import MatchList from './components/MatchList';
import MatchDetail from './components/MatchDetail';
import { ProtectedRoute } from '.../../domains/auth/components/ProtectedRoute';
import { useAppStore } from '../../store';

// Using discriminated unions for route permissions management
type RouteConfig = {
  path: string;
  element: JSX.Element;
} & (
  | { access: 'public' }
  | { access: 'protected'; roles: string[] }
);

const MatchingRoutes: React.FC = () => {
  // Get user role from Zustand store
  const { user } = useAppStore();
  
  // Define routes with discriminated unions for access control
  const routes: RouteConfig[] = [
    { path: "/", access: "protected", roles: ["Admin"], element: <MatchingDashboard /> },
    { path: "/rounds", access: "protected", roles: ["Admin"], element: <MatchingRoundList /> },
    { path: "/rounds/new", access: "protected", roles: ["Admin"], element: <MatchingRoundForm /> },
    { path: "/rounds/:id", access: "protected", roles: ["Admin"], element: <MatchingRoundDetail /> },
    { path: "/rounds/:id/edit", access: "protected", roles: ["Admin"], element: <MatchingRoundForm /> },
    { path: "/rounds/:roundId/matches", access: "protected", roles: ["Admin"], element: <MatchList /> },
    { path: "/matches", access: "protected", roles: ["Admin"], element: <MatchList /> },
    { path: "/matches/:id", access: "protected", roles: ["Admin"], element: <MatchDetail /> },
  ];

  return (
    <Routes>
      {routes.map((route) => (
        <Route
          key={route.path}
          path={route.path}
          element={
            route.access === "public" ? (
              route.element
            ) : (
              <ProtectedRoute 
                allowedRoles={route.roles} 
                element={route.element} 
              />
            )
          }
        />
      ))}
    </Routes>
  );
};

export default MatchingRoutes;