// frontend/src/domains/matching/components/MatchingRoundList.tsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMatchingRounds, useDeleteMatchingRound } from '../hooks';
import { CheckCircleIcon, XCircleIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const MatchingRoundList: React.FC = () => {
  const { data: rounds, isLoading } = useMatchingRounds();
  const deleteRound = useDeleteMatchingRound();
  const [isDeleting, setIsDeleting] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this matching round?')) {
      setIsDeleting(true);
      setDeletingId(id);
      try {
        await deleteRound.mutateAsync(id);
      } catch (error) {
        console.error('Error deleting round:', error);
      } finally {
        setIsDeleting(false);
        setDeletingId(null);
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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Matching Rounds</h1>
        <Link
          to="/matching/rounds/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          New Matching Round
        </Link>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {!rounds || rounds.length === 0 ? (
            <li className="px-4 py-4 sm:px-6">
              <p className="text-gray-500">No matching rounds found.</p>
            </li>
          ) : (
            rounds.map((round) => (
              <li key={round.id}>
                <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${
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
                          <CheckCircleIcon className="h-6 w-6 text-green-600" />
                        ) : round.status === 'FAILED' ? (
                          <XCircleIcon className="h-6 w-6 text-red-600" />
                        ) : (
                          <div className="h-6 w-6 rounded-full border-2 border-gray-300 border-t-purple-600 animate-spin"></div>
                        )}
                      </div>
                      <div className="ml-4">
                        <h2 className="text-lg font-medium text-gray-900">
                          <Link to={`/matching/rounds/${round.id}`} className="hover:underline">
                            {round.name}
                          </Link>
                        </h2>
                        <div className="text-sm text-gray-500">
                          <span>Created: {format(new Date(round.created_at), 'MMM d, yyyy')}</span>
                          {round.completed_at && (
                            <span> • Completed: {format(new Date(round.completed_at), 'MMM d, yyyy')}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
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
                      <div className="flex space-x-1">
                        <Link
                          to={`/matching/rounds/${round.id}`}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          <span className="sr-only">View</span>
                          <PencilIcon className="h-5 w-5" />
                        </Link>
                        <button
                          onClick={() => handleDelete(round.id)}
                          disabled={isDeleting && deletingId === round.id}
                          className="text-red-600 hover:text-red-900 disabled:opacity-50"
                        >
                          <span className="sr-only">Delete</span>
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      <p className="flex items-center text-sm text-gray-500">
                        Algorithm: {round.algorithm_type}
                      </p>
                      <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                        {round.initiated_by_name && `Initiated by: ${round.initiated_by_name}`}
                      </p>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      <p>
                        {round.matched_students} of {round.total_students} students matched
                        {round.average_match_score !== null && ` (Avg. score: ${round.average_match_score.toFixed(2)})`}
                      </p>
                    </div>
                  </div>
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
};

export default MatchingRoundList;