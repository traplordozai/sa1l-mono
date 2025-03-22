// frontend/src/domains/matching/components/MatchDetail.tsx
import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useMatch, useUpdateMatchStatus } from '../hooks';
import {
  CheckCircleIcon,
  XCircleIcon,
  ArrowUturnLeftIcon,
  ClipboardDocumentCheckIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const MatchDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: match, isLoading } = useMatch(id!);
  const updateStatus = useUpdateMatchStatus();

  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [notes, setNotes] = useState('');

  const handleStatusUpdate = async (newStatus: string) => {
    setIsUpdating(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await updateStatus.mutateAsync({
        id: id!,
        data: { status: newStatus, notes }
      });
      setSuccessMessage(`Match status updated to ${newStatus}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update match status');
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <p className="text-red-700">Match not found.</p>
      </div>
    );
  }

  // Calculate percentage components of match score
  const scoreComponents = match.score_details ? [
    {
      name: 'Area of Law',
      score: match.score_details.area_of_law_score * match.score_details.area_of_law_weight,
      percentage: (match.score_details.area_of_law_score * match.score_details.area_of_law_weight) / match.match_score * 100
    },
    {
      name: 'Statement',
      score: (match.score_details.statement_score || 0) * (match.score_details.statement_weight || 0),
      percentage: ((match.score_details.statement_score || 0) * (match.score_details.statement_weight || 0)) / match.match_score * 100
    },
    {
      name: 'Location',
      score: (match.score_details.location_score || 0) * (match.score_details.location_weight || 0),
      percentage: ((match.score_details.location_score || 0) * (match.score_details.location_weight || 0)) / match.match_score * 100
    },
    {
      name: 'Work Preference',
      score: (match.score_details.work_preference_score || 0) * (match.score_details.work_preference_weight || 0),
      percentage: ((match.score_details.work_preference_score || 0) * (match.score_details.work_preference_weight || 0)) / match.match_score * 100
    },
    {
      name: 'Grade',
      score: (match.score_details.grade_score || 0) * (match.score_details.grade_weight || 0),
      percentage: ((match.score_details.grade_score || 0) * (match.score_details.grade_weight || 0)) / match.match_score * 100
    }
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Match Details</h1>
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          <ArrowUturnLeftIcon className="h-5 w-5 mr-1" />
          Back
        </button>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Match Overview Card */}
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Match Overview</h3>
            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
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
          </div>
          <div className="border-t border-gray-200">
            <dl>
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Student</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <Link to={`/students/${match.student}`} className="text-purple-600 hover:text-purple-900">
                    {match.student_name}
                  </Link>
                </dd>
              </div>
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Organization</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <Link to={`/organizations/${match.organization}`} className="text-purple-600 hover:text-purple-900">
                    {match.organization_name}
                  </Link>
                </dd>
              </div>
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Area of Law</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {match.area_of_law}
                </dd>
              </div>
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Match Score</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <div className="font-bold text-lg">{match.match_score.toFixed(2)}</div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div className="bg-purple-600 h-2.5 rounded-full" style={{ width: `${match.match_score * 100}%` }}></div>
                  </div>
                </dd>
              </div>
              {match.student_rank && (
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Student Rank</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    {match.student_rank}
                  </dd>
                </div>
              )}
              {match.organization_rank && (
                <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Organization Rank</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    {match.organization_rank}
                  </dd>
                </div>
              )}
              {match.statement_score && (
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Statement Score</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    {match.statement_score.toFixed(2)}
                  </dd>
                </div>
              )}
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {format(new Date(match.created_at), 'MMMM d, yyyy h:mm a')}
                </dd>
              </div>
              {match.approved_at && (
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Approved</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    {format(new Date(match.approved_at), 'MMMM d, yyyy h:mm a')}
                  </dd>
                </div>
              )}
              {match.rejected_at && (
                <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Rejected</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    {format(new Date(match.rejected_at), 'MMMM d, yyyy h:mm a')}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Score Breakdown</h3>
          </div>
          <div className="border-t border-gray-200">
            {match.score_details ? (
              <div className="px-4 py-5">
                {scoreComponents.map((component, index) => (
                  <div key={index} className="mb-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700">{component.name}</span>
                      <span className="text-sm text-gray-900">{component.score.toFixed(2)} ({component.percentage.toFixed(0)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full"
                        style={{ width: `${component.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="px-4 py-5">
                <p className="text-sm text-gray-500">No detailed score breakdown available.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      {match.status === 'PENDING' && (
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Update Match Status</h3>
            <div className="mt-4">
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                Notes (optional)
              </label>
              <textarea
                id="notes"
                name="notes"
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
              />
            </div>
            <div className="mt-5 flex space-x-3">
              <button
                onClick={() => handleStatusUpdate('ACCEPTED')}
                disabled={isUpdating}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                <CheckCircleIcon className="h-5 w-5 mr-1" />
                Accept Match
              </button>
              <button
                onClick={() => handleStatusUpdate('REJECTED')}
                disabled={isUpdating}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
              >
                <XCircleIcon className="h-5 w-5 mr-1" />
                Reject Match
              </button>
            </div>
          </div>
        </div>
      )}

      {match.status === 'ACCEPTED' && (
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Confirm Match</h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>
                This match has been accepted. You can now confirm it to finalize the placement.
              </p>
            </div>
            <div className="mt-5">
              <button
                onClick={() => handleStatusUpdate('CONFIRMED')}
                disabled={isUpdating}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <ClipboardDocumentCheckIcon className="h-5 w-5 mr-1" />
                Confirm Placement
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Notes */}
      {match.notes && (
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Notes</h3>
            <div className="mt-2 text-sm text-gray-500">
              <p>{match.notes}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MatchDetail;