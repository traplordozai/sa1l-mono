// frontend/src/domains/matching/components/MatchingDashboard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import {
  useMatchingRounds,
  useMatchingStatistics
} from '../hooks';
import {
  ChartPieIcon,
  UsersIcon,
  BuildingOfficeIcon,
  ClipboardDocumentListIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
const STATUS_COLORS = {
  PENDING: '#F59E0B',  // amber
  ACCEPTED: '#10B981', // green
  REJECTED: '#EF4444', // red
  CONFIRMED: '#3B82F6', // blue
};

const MatchingDashboard: React.FC = () => {
  const { data: rounds, isLoading: roundsLoading } = useMatchingRounds();
  const { data: stats, isLoading: statsLoading } = useMatchingStatistics();

  const isLoading = roundsLoading || statsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  if (!rounds || !stats) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <p className="text-red-700">Failed to load matching data.</p>
      </div>
    );
  }

  // Prepare data for charts
  const matchStatusData = Object.entries(stats.matches.by_status || {}).map(([status, count]) => ({
    name: status,
    value: count,
    color: STATUS_COLORS[status as keyof typeof STATUS_COLORS] || '#A1A1AA'
  }));

  const areaOfLawData = Object.entries(stats.matches.by_area || {}).map(([area, count], index) => ({
    name: area,
    count: count,
    color: COLORS[index % COLORS.length]
  }));

  // Calculate percentage of matched students if possible
  const matchPercentage = stats.round
    ? stats.round.match_percentage
    : stats.overall.total_rounds > 0
      ? (stats.overall.confirmed_matches / stats.matches.total * 100) || 0
      : 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Matching Dashboard</h1>
        <Link
          to="/matching/rounds/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          New Matching Round
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Rounds */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-100 rounded-md p-3">
                <ChartPieIcon className="h-6 w-6 text-purple-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Rounds
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {stats.overall.total_rounds}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Matched Students */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                <UsersIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Matched Students
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {stats.overall.confirmed_matches}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Total Matches */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                <ClipboardDocumentListIcon className="h-6 w-6 text-blue-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Matches
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {stats.matches.total}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Average Match Score */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
                <BuildingOfficeIcon className="h-6 w-6 text-yellow-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Average Match Score
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {stats.matches.avg_score ? stats.matches.avg_score.toFixed(2) : 'N/A'}
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
        {/* Match Status Pie Chart */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Matches by Status</h3>
            <div className="mt-2 h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={matchStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {matchStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} matches`, '']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Areas of Law Bar Chart */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Matches by Area of Law</h3>
            <div className="mt-2 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={areaOfLawData}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
                >
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="name" width={120} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8">
                    {areaOfLawData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Matching Rounds */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Matching Rounds</h3>
        </div>
        <ul className="divide-y divide-gray-200">
          {rounds.slice(0, 5).map((round) => (
            <li key={round.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
              <Link to={`/matching/rounds/${round.id}`} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`flex-shrink-0 rounded-md p-2 ${
                    round.status === 'COMPLETED' 
                      ? 'bg-green-100' 
                      : round.status === 'FAILED' 
                        ? 'bg-red-100' 
                        : round.status === 'IN_PROGRESS' 
                          ? 'bg-blue-100' 
                          : 'bg-gray-100'
                    }`}
                  >
                    {round.status === 'COMPLETED' ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-600" />
                    ) : round.status === 'FAILED' ? (
                      <XCircleIcon className="h-5 w-5 text-red-600" />
                    ) : (
                      <ClipboardDocumentListIcon className="h-5 w-5 text-gray-600" />
                    )}
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">{round.name}</p>
                    <p className="text-sm text-gray-500">
                      {round.total_students > 0
                        ? `${round.matched_students} of ${round.total_students} students matched`
                        : 'No students processed'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    round.status === 'COMPLETED' 
                      ? 'bg-green-100 text-green-800' 
                      : round.status === 'FAILED' 
                        ? 'bg-red-100 text-red-800' 
                        : round.status === 'IN_PROGRESS' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {round.status}
                  </span>
                  {round.average_match_score !== null && (
                    <span className="ml-2 text-sm text-gray-500">
                      Score: {round.average_match_score.toFixed(2)}
                    </span>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ul>
        <div className="px-4 py-4 border-t border-gray-200 sm:px-6">
          <Link
            to="/matching/rounds"
            className="text-sm font-medium text-purple-600 hover:text-purple-500"
          >
            View all matching rounds
          </Link>
        </div>
      </div>
    </div>
  );
};

export default MatchingDashboard;