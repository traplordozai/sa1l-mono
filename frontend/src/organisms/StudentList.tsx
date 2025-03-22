import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Student } from '../types/Student';
import { useStudents } from '../services/studentService';
import StudentInfoCard from '../shared/components/molecules/StudentInfoCard';

interface StudentListProps {
  filters?: Record<string, any>;
  title?: string;
  emptyMessage?: string;
}

const StudentList: React.FC<StudentListProps> = ({
  filters = {},
  title = 'Students',
  emptyMessage = 'No students found',
}) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const { data: students, isLoading, error } = useStudents(filters);

  const filteredStudents = students
    ? students.filter((student: { given_names: any; last_name: any; email: string; student_id: string; }) => {
        const fullName = `${student.given_names} ${student.last_name}`.toLowerCase();
        const searchTerms = searchQuery.toLowerCase();

        return fullName.includes(searchTerms) ||
               student.email.toLowerCase().includes(searchTerms) ||
               student.student_id.toLowerCase().includes(searchTerms);
      })
    : [];

  const handleStudentClick = (studentId: string) => {
    navigate(`/admin/students/${studentId}`);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>

        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search students..."
            className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-60">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Error loading students: {(error as Error).message}
        </div>
      ) : filteredStudents.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 text-gray-500 px-4 py-8 rounded text-center">
          {emptyMessage}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredStudents.map((student: Student) => (
            <StudentInfoCard
              key={student.id}
              student={student}
              onClick={() => handleStudentClick(student.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default StudentList;