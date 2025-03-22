// frontend/src/domains/matching/components/MatchList.tsx
import React, { useState } from 'react';
import { useMatches, useUpdateMatchStatus } from '../hooks';
import { Link, useParams } from 'react-router-dom';
import { CheckCircleIcon, XCircleIcon, EyeIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const MatchList: React.FC = () => {
  const { roundId } = useParams<{ roundId?: string }>();
  const [status, setStatus] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState('');

  const params = {
    ...(roundId && { round_id: roundId }),
    ...(status !== 'All' && { status }),
  };

  const { data: matches, isLoading } = useMatches(params);
  const updateStatus = useUpdateMatchStatus();

  const [isUpdating, setIsUpdating] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleStatusUpdate = async (id: string, newStatus: string) => {
    setIsUpdating(true);
    setUpdatingId(id);
    setError(null);
    setSuccessMessage(null);

    try {
      await updateStatus.mutateAsync({
        id,
        data: { status: newStatus }
      });
      setSuccessMessage(`Match status updated to ${newStatus}`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to update match status');
      setTimeout(() => setError(null), 3000);
    } finally {
      setIsUpdating(false);
      setUpdatingId(null);
    }
  };

  const filteredMatches = matches ? matches.filter(match => {
    const matchesQuery = searchQuery.toLowerCase();
    return (
      match.student_name.toLowerCase().includes(matchesQuery) ||
      match.organization_name.toLowerCase().includes(matchesQuery) ||
      match.area_of_law.toLowerCase().includes(matchesQuery)
    );
  }) : [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">
          {roundId ? 'Round Matches' : 'All Matches'}
        </h1>
        {roundId && (
          <Link
            to={`/matching/rounds/${roundId}`}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
          >
            Back to Round
          </Link>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="bg-green-50 border-l-4 border-green-400 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-green-700">{successMessage}</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex flex-col sm:flex-row sm:items-center justify-between space-y-3 sm:space-y-0">
          <div className="w-full sm:w-64">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search matches..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

          <div>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm rounded-md"
            >
              <option value="All">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="ACCEPTED">Accepted</option>
              <option value="REJECTED">Rejected</option>
              <option value="CONFIRMED">Confirmed</option>
            </select>
          </div>
        </div>

        {filteredMatches.length === 0 ? (
          <div className="px-4 py-5 text-center">
            <p className="text-sm text-gray-500">No matches found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Organization
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Area of Law
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredMatches.map((match) => (
                  <tr key={match.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      <Link to={`/students/${match.student}`} className="hover:text-purple-600">
                        {match.student_name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <Link to={`/organizations/${match.organization}`} className="hover:text-purple-600">
                        {match.organization_name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {match.area_of_law}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {match.match_score.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        match.status === 'ACCEPTED' 
                          ? 'bg-green-100 text-green-800' 
                          : match.status === 'REJECTED' 
                            ? 'bg-red-100 text-red-800' 
                            : match.status === 'CONFIRMED' 
                              ? 'bg-blue-100 text-blue-800' 
                              : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {match.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {format(new Date(match.created_at), 'MMM d, yyyy')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-3">
                        <Link
                          to={`/matching/matches/${match.id}`}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          <EyeIcon className="h-5 w-5" />
                          <span className="sr-only">View</span>
                        </Link>

                        {match.status === 'PENDING' && (
                          <>
                            <button
                              onClick={() => handleStatusUpdate(match.id, 'ACCEPTED')}
                              disabled={isUpdating && updatingId === match.id}
                              className="text-green-600 hover:text-green-900 disabled:opacity-50"
                            >
                              <CheckCircleIcon className="h-5 w-5" />
                              <span className="sr-only">Accept</span>
                            </button>

                            <button
                              onClick={() => handleStatusUpdate(match.id, 'REJECTED')}
                              disabled={isUpdating && updatingId === match.id}
                              className="text-red-600 hover:text-red-900 disabled:opacity-50"
                            >
                              <XCircleIcon className="h-5 w-5" />
                              <span className="sr-only">Reject</span>
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default MatchList;