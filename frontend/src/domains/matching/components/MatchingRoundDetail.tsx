// frontend/src/domains/matching/components/MatchingRoundDetail.tsx
import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useMatchingRound, useRoundMatches, useRunMatchingAlgorithm, useRoundStatistics, useDeleteMatchingRound } from '../hooks';
import {
  CheckCircleIcon,
  XCircleIcon,
  PlayIcon,
  PencilIcon,
  TrashIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const MatchingRoundDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: round, isLoading: roundLoading } = useMatchingRound(id!);
  const { data: matches, isLoading: matchesLoading } = useRoundMatches(id!);
  const { data: statistics, isLoading: statsLoading } = useRoundStatistics(id!);
  const runAlgorithm = useRunMatchingAlgorithm();
  const deleteRound = useDeleteMatchingRound();

  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const isLoading = roundLoading || matchesLoading || statsLoading;

  const handleRunAlgorithm = async () => {
    if (!id) return;

    setIsRunning(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await runAlgorithm.mutateAsync(id);
      setSuccessMessage(result.message || 'Matching algorithm completed successfully.');
    } catch (err: any) {
      setError(err.message || 'An error occurred while running the matching algorithm.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleDeleteRound = async () => {
    if (!id) return;

    if (window.confirm('Are you sure you want to delete this matching round? This action cannot be undone.')) {
      try {
        await deleteRound.mutateAsync(id);
        navigate('/matching/rounds');
      } catch (err: any) {
        setError(err.message || 'An error occurred while deleting the matching round.');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  if (!round) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <p className="text-red-700">Matching round not found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">{round.name}</h1>
        <div className="flex space-x-2">
          {round.status !== 'COMPLETED' && round.status !== 'IN_PROGRESS' && (
            <button
              onClick={handleRunAlgorithm}
              disabled={isRunning}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              <PlayIcon className="h-5 w-5 mr-1" />
              {isRunning ? 'Running...' : 'Run Algorithm'}
            </button>
          )}
          <Link
            to={`/matching/rounds/${id}/edit`}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
          >
            <PencilIcon className="h-5 w-5 mr-1" />
            Edit
          </Link>
          <button
            onClick={handleDeleteRound}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <TrashIcon className="h-5 w-5 mr-1" />
            Delete
          </button>
        </div>
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

      {/* Round Details Card */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">Round Details</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              {round.description || 'No description provided.'}
            </p>
          </div>
          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
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
        </div>
        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {format(new Date(round.created_at), 'MMMM d, yyyy h:mm a')}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Algorithm</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {round.algorithm_type}
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Students</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {round.matched_students} matched of {round.total_students} total
                {round.total_students > 0 && ` (${Math.round((round.matched_students / round.total_students) * 100)}%)`}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Average Score</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {round.average_match_score !== null ? round.average_match_score.toFixed(2) : 'N/A'}
              </dd>
            </div>
            {round.started_at && (
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Started</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {format(new Date(round.started_at), 'MMMM d, yyyy h:mm a')}
                </dd>
              </div>
            )}
            {round.completed_at && (
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Completed</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {format(new Date(round.completed_at), 'MMMM d, yyyy h:mm a')}
                </dd>
              </div>
            )}
            {round.initiated_by_name && (
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Initiated By</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {round.initiated_by_name}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* Matches Summary */}
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 border-b border-gray-200 sm:px-6 flex justify-between items-center">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Matches ({round.matches_count || 0})
          </h3>
          <Link
            to={`/matching/rounds/${id}/matches`}
            className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-purple-700 bg-purple-100 hover:bg-purple-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
          >
            <ClipboardDocumentListIcon className="h-4 w-4 mr-1" />
            View All
          </Link>
        </div>

        {matches && matches.length > 0 ? (
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
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {matches.slice(0, 5).map((match) => (
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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-6 py-4 text-sm text-gray-500">
            No matches found for this round.
          </div>
        )}
      </div>
    </div>
  );
};

export default MatchingRoundDetail;