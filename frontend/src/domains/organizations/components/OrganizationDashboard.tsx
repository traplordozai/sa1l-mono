import React from 'react';
import { Link } from 'react-router-dom';
import { useOrganizationStatistics } from '../hooks';
import {
  BuildingOfficeIcon,
  UserIcon,
  BriefcaseIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#4F46E5', '#7C3AED', '#8B5CF6', '#A78BFA', '#C4B5FD'];

const OrganizationDashboard: React.FC = () => {
  const { data: stats, isLoading, error } = useOrganizationStatistics();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <p className="text-red-700">
          {error ? `Error loading statistics: ${error.message}` : 'No statistics available'}
        </p>
      </div>
    );
  }

  // Prepare data for pie chart
  const positionsData = [
    { name: 'Filled', value: stats.filled_positions },
    { name: 'Available', value: stats.available_positions },
  ];

  // Calculate percentage filled
  const percentageFilled = Math.round((stats.filled_positions / (stats.filled_positions + stats.available_positions)) * 100) || 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Organizations Dashboard</h1>
        <Link
          to="/organizations/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          Add Organization
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Organizations */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-100 rounded-md p-3">
                <BuildingOfficeIcon className="h-6 w-6 text-purple-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Organizations
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {stats.total_count}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Active Organizations */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                <CheckCircleIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Active Organizations
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {stats.active_count}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Total Positions */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                <BriefcaseIcon className="h-6 w-6 text-blue-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Positions
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {stats.total_positions}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Positions Filled */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
                <UserIcon className="h-6 w-6 text-yellow-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Positions Filled
                  </dt>
                  <dd>
      // Continuing OrganizationDashboard.tsx
                    <div className="text-lg font-medium text-gray-900">
                      {stats.filled_positions} / {stats.total_positions}
                    </div>
                    <div className="mt-1">
                      <div className="relative w-full h-4 bg-gray-200 rounded">
                        <div
                          className="absolute top-0 left-0 h-4 bg-yellow-500 rounded"
                          style={{
                            width: `${percentageFilled}%`
                          }}
                        />
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {percentageFilled}% of positions filled
                      </p>
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Positions Pie Chart */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Positions Overview</h3>
            <div className="mt-2 h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={positionsData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {positionsData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} positions`, '']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Areas of Law Bar Chart */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Organizations by Area of Law</h3>
            <div className="mt-2 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={stats.areas_of_law_breakdown}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 50, bottom: 5 }}
                >
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="name" width={120} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8">
                    {stats.areas_of_law_breakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Organizations */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Organizations</h3>
        </div>
        <ul className="divide-y divide-gray-200">
          {stats.recent_organizations.map((org) => (
            <li key={org.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
              <Link to={`/organizations/${org.id}`} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-purple-100 rounded-md p-2">
                    <BuildingOfficeIcon className="h-5 w-5 text-purple-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">{org.name}</p>
                    <p className="text-sm text-gray-500">{org.location}</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${org.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {org.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="ml-2 text-sm text-gray-500">
                    {org.filled_positions}/{org.available_positions} positions
                  </span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
        <div className="px-4 py-4 border-t border-gray-200 sm:px-6">
          <Link
            to="/organizations"
            className="text-sm font-medium text-purple-600 hover:text-purple-500"
          >
            View all organizations
          </Link>
        </div>
      </div>
    </div>
  );
};

export default OrganizationDashboard;
