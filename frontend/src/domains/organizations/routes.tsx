// src/domains/organizations/routes.tsx
import React from 'react';
import { Route, Routes } from 'react-router-dom';
import OrganizationDashboard from './components/OrganizationDashboard';
import OrganizationList from './components/OrganizationList';
import OrganizationDetail from './components/OrganizationDetail';
import OrganizationForm from './components/OrganizationForm';
import { ProtectedRoute } from '../../components/auth';

const OrganizationRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<ProtectedRoute allowedRoles={['Admin']} element={<OrganizationDashboard />} />} />
      <Route path="/list" element={<ProtectedRoute allowedRoles={['Admin']} element={<OrganizationList />} />} />
      <Route path="/new" element={<ProtectedRoute allowedRoles={['Admin']} element={<OrganizationForm />} />} />
      <Route path="/:id" element={<ProtectedRoute allowedRoles={['Admin']} element={<OrganizationDetail />} />} />
      <Route path="/:id/edit" element={<ProtectedRoute allowedRoles={['Admin']} element={<OrganizationForm />} />} />
    </Routes>
  );
};

export default OrganizationRoutes;