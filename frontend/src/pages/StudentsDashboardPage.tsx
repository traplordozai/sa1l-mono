import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StudentList from '../organisms/StudentList';

const StudentsDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('all');

  const tabs = [
    { id: 'all', label: 'All Students', filters: {} },
    { id: 'unmatched', label: 'Unmatched', filters: { is_matched: false } },
    { id: 'needs-approval', label: 'Needs Approval', filters: { needs_approval: true } },
    { id: 'active', label: 'Active', filters: { is_active: true } },
    { id: 'inactive', label: 'Inactive', filters: { is_active: false } },
  ];

  const currentTab = tabs.find(tab => tab.id === activeTab) || tabs[0];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Students</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage student profiles, grades, and statements.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:flex-none">
          <button
            type="button"
            onClick={() => navigate('/admin/students/import')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Import Students
          </button>
        </div>
      </div>

      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <StudentList
        filters={currentTab.filters}
        title={currentTab.label}
        emptyMessage={`No ${currentTab.label.toLowerCase()} found.`}
      />
    </div>
  );
};

export default StudentsDashboardPage;