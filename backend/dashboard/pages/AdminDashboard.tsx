// frontend/src/domains/dashboard/pages/AdminDashboard.tsx
import React from 'react';
import {
  UserIcon,
  UserGroupIcon,
  ClockIcon,
  ShieldCheckIcon,
  OfficeBuildingIcon,
  DocumentTextIcon,
  RefreshIcon
} from '@heroicons/react/outline';
import { useDashboardStats } from '../hooks/useDashboardStats';
import { StatCard } from '../components/StatCard';
import { ActivityFeed } from '../components/ActivityFeed';
import { DashboardCharts } from '../components/DashboardCharts';

export const AdminDashboard: React.FC = () => {
  const { data: stats, isLoading, error, refetch } = useDashboardStats();

  const handleRefresh = () => {
    refetch();
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <button
          onClick={handleRefresh}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          <RefreshIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          Refresh Data
        </button>
      </div>

      {error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline"> Failed to load dashboard data. Please try again.</span>
        </div>
      ) : isLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-700"></div>
        </div>
      ) : stats ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Students"
              value={stats.total_students}
              description="Total registered students"
              change={stats.student_growth}
              icon={<UserIcon className="h-6 w-6" />}
              colorScheme="blue"
            />
            <StatCard
              title="Matched Students"
              value={stats.matched_students}
              description={`${stats.match_rate.percentage}% match rate`}
              icon={<UserGroupIcon className="h-6 w-6" />}
              colorScheme="green"
            />
            <StatCard
              title="Pending Matches"
              value={stats.pending_matches}
              description="Waiting for placement"
              icon={<ClockIcon className="h-6 w-6" />}
              colorScheme="yellow"
            />
            <StatCard
              title="Needs Approval"
              value={stats.approval_needed}
              description="Requires admin action"
              icon={<ShieldCheckIcon className="h-6 w-6" />}
              colorScheme="red"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <DashboardCharts stats={stats} />
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
              <ActivityFeed limit={8} />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Organization Overview</h2>
              <div className="grid grid-cols-2 gap-4">
                <StatCard
                  title="Organizations"
                  value={stats.total_organizations}
                  description="Total registered organizations"
                  change={stats.organization_growth}
                  icon={<OfficeBuildingIcon className="h-6 w-6" />}
                  colorScheme="purple"
                />
                <StatCard
                  title="Available Positions"
                  value={stats.available_positions}
                  description={`${stats.filled_positions} positions filled`}
                  colorScheme="gray"
                />
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Statements</h2>
              <StatCard
                title="Ungraded Statements"
                value={stats.ungraded_statements}
                description="Pending evaluation"
                icon={<DocumentTextIcon className="h-6 w-6" />}
                colorScheme="yellow"
              />
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-12 text-gray-500">
          No dashboard data available
        </div>
      )}
    </div>
  );
};