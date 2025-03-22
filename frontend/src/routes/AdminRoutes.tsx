import React from 'react';
import { ImportDashboard } from '../components/ImportDashboard';

// Define the routes as a proper array
const AdminRoutes = [
  {
    path: 'imports',
    element: <ImportDashboard />
  },
  // You can add more admin routes here as needed
];

export default AdminRoutes;