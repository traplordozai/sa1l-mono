import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStudent } from '../../../services/studentService.ts';
import StatusBadge from '../../../shared/components/atoms/StatusBadge.tsx';

const StudentProfilePage: React.FC = () => {
  const { studentId } = useParams<{ studentId: string }>();
  const navigate = useNavigate();

  const {
    data: student,
    isLoading,
    error
  } = useStudent(studentId || '');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> Failed to load student profile.</span>
        </div>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded shadow hover:bg-indigo-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!student) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative">
          <strong className="font-bold">Not Found!</strong>
          <span className="block sm:inline"> Student not found.</span>
        </div>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded shadow hover:bg-indigo-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-start mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Student Profile</h1>
        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 bg-indigo-600 text-white rounded shadow hover:bg-indigo-700"
        >
          Back
        </button>
      </div>

      {/* Student Personal Information */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Personal Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Student ID</p>
            <p className="font-medium">{student.student_id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Name</p>
            <p className="font-medium">{student.full_name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Email</p>
            <p className="font-medium">{student.email}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Program</p>
            <p className="font-medium">{student.program}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Profile Completion</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
              <div
                className="bg-indigo-600 h-2.5 rounded-full"
                style={{ width: `${student.profile_completion}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">{student.profile_completion}% complete</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Status</p>
            <div className="flex flex-wrap gap-2 mt-1">
              <StatusBadge
                status={student.is_active ? 'success' : 'error'}
                label={student.is_active ? 'Active' : 'Inactive'}
              />
              <StatusBadge
                status={student.is_matched ? 'success' : 'warning'}
                label={student.is_matched ? 'Matched' : 'Unmatched'}
              />
              {student.needs_approval && (
                <StatusBadge status="warning" label="Needs Approval" />
              )}
            </div>
          </div>
        </div>

        <div className="mt-4">
          <p className="text-sm text-gray-600">Preferences</p>
          <div className="mt-2 space-y-2">
            <div>
              <p className="text-xs text-gray-500">Location Preferences</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {student.location_preferences.length > 0 ? (
                  student.location_preferences.map((location: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined, i: React.Key | null | undefined) => (
                    <span key={i} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {location}
                    </span>
                  ))
                ) : (
                  <span className="text-gray-400">None specified</span>
                )}
              </div>
            </div>
            <div>
              <p className="text-xs text-gray-500">Work Preferences</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {student.work_preferences.length > 0 ? (
                  student.work_preferences.map((preference: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined, i: React.Key | null | undefined) => (
                    <span key={i} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {preference}
                    </span>
                  ))
                ) : (
                  <span className="text-gray-400">None specified</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Area Rankings */}
      {student.area_rankings && student.area_rankings.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Area Rankings</h2>
          <div className="space-y-4">
            {student.area_rankings
              .sort((a: { rank: number; }, b: { rank: number; }) => a.rank - b.rank)
              .map((ranking: { id: React.Key | null | undefined; area_name: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined; comments: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined; rank: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined; }) => (
                <div key={ranking.id} className="flex justify-between items-center border-b pb-2 last:border-0">
                  <div>
                    <p className="font-medium">{ranking.area_name}</p>
                    {ranking.comments && (
                      <p className="text-sm text-gray-500 mt-1">{ranking.comments}</p>
                    )}
                  </div>
                  <div className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium">
                    Rank: {ranking.rank}
                  </div>
                </div>
            ))}
          </div>
        </div>
      )}

      {/* Grades */}
      {student.grades && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Grades</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Constitutional Law</p>
              <p className="font-medium">{student.grades.constitutional_law || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Contracts</p>
              <p className="font-medium">{student.grades.contracts || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Criminal Law</p>
              <p className="font-medium">{student.grades.criminal_law || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Property Law</p>
              <p className="font-medium">{student.grades.property_law || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Torts</p>
              <p className="font-medium">{student.grades.torts || 'N/A'}</p>
            </div>
          </div>

          <h3 className="text-lg font-semibold text-gray-800 mt-5 mb-3">Legal Research and Writing</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Case Brief</p>
              <p className="font-medium">{student.grades.lrw_case_brief || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Multiple Case Analysis</p>
              <p className="font-medium">{student.grades.lrw_multiple_case || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Short Memo</p>
              <p className="font-medium">{student.grades.lrw_short_memo || 'N/A'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Statements */}
      {student.statements && student.statements.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Statements</h2>
          {student.statements.map((statement: { id: React.Key | null | undefined; area_name: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined; statement_grade: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined; graded_by_name: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined; content: string | number | bigint | boolean | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | Promise<string | number | bigint | boolean | React.ReactPortal | React.ReactElement<unknown, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | null | undefined> | null | undefined; }) => (
            <div key={statement.id} className="mb-5 pb-5 border-b border-gray-200 last:border-0 last:mb-0 last:pb-0">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-md font-medium text-gray-900">
                    {statement.area_name}
                  </h3>
                  {statement.statement_grade !== null && (
                    <div className="mt-1">
                      <span className="text-sm text-gray-600">Grade: </span>
                      <span className="font-medium">{statement.statement_grade}/25</span>
                      {statement.graded_by_name && (
                        <span className="text-sm text-gray-500 ml-2">
                          by {statement.graded_by_name}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
              <div className="mt-2 prose prose-sm max-w-none text-gray-700 whitespace-pre-line">
                {statement.content}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Self-Proposed Externship */}
      {student.self_proposed && (
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Self-Proposed Externship</h2>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
            <div className="md:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Organization</dt>
              <dd className="mt-1 text-gray-900">{student.self_proposed.organization}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Supervisor</dt>
              <dd className="mt-1 text-gray-900">{student.self_proposed.supervisor}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Contact Email</dt>
              <dd className="mt-1 text-gray-900">{student.self_proposed.supervisor_email}</dd>
            </div>
            {student.self_proposed.website && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Website</dt>
                <dd className="mt-1 text-gray-900">
                  <a
                    href={student.self_proposed.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-600 hover:text-indigo-800"
                  >
                    {student.self_proposed.website}
                  </a>
                </dd>
              </div>
            )}
            {student.self_proposed.address && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Address</dt>
                <dd className="mt-1 text-gray-900">{student.self_proposed.address}</dd>
              </div>
            )}
            <div className="md:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Description</dt>
              <dd className="mt-1 text-gray-900 whitespace-pre-line">{student.self_proposed.description}</dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
};

export default StudentProfilePage;