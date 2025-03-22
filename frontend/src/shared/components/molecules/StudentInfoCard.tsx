import * as React from 'react';
import { Student } from '../../../types/Student.ts';
import StatusBadge from '../atoms/StatusBadge.tsx';

interface StudentInfoCardProps {
  student: Student;
  onClick?: () => void;
  className?: string;
}

const StudentInfoCard: React.FC<StudentInfoCardProps> = ({
  student,
  onClick,
  className = '',
}) => {
  return (
    <div
      className={`bg-white shadow rounded-lg p-6 transition hover:shadow-md ${onClick ? 'cursor-pointer' : ''} ${className}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{student.full_name}</h3>
          <p className="text-sm text-gray-500">{student.student_id}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge
            status={student.is_active ? 'success' : 'error'}
            label={student.is_active ? 'Active' : 'Inactive'}
          />
          <StatusBadge
            status={student.is_matched ? 'info' : 'warning'}
            label={student.is_matched ? 'Matched' : 'Unmatched'}
          />
          {student.needs_approval && (
            <StatusBadge status="warning" label="Needs Approval" />
          )}
        </div>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <div className="col-span-1">
          <dt className="text-gray-500">Email</dt>
          <dd className="text-gray-900 truncate">{student.email}</dd>
        </div>
        <div className="col-span-1">
          <dt className="text-gray-500">Program</dt>
          <dd className="text-gray-900">{student.program}</dd>
        </div>
        <div className="col-span-2">
          <dt className="text-gray-500">Profile Completion</dt>
          <dd className="mt-1">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full"
                style={{ width: `${student.profile_completion}%` }}
              ></div>
            </div>
            <span className="text-xs text-gray-500 mt-1">{student.profile_completion}%</span>
          </dd>
        </div>
      </dl>
    </div>
  );
};

export default StudentInfoCard;