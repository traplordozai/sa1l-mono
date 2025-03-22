import React, { useState } from 'react';
import StudentCSVImport from '../organisms/StudentCSVImport';
import StudentGradesPDFImport from '../organisms/StudentGradesPDFImport';

const StudentImportPage: React.FC = () => {
  const [importSuccess, setImportSuccess] = useState(false);

  const handleImportSuccess = () => {
    setImportSuccess(true);
    // Reset the success message after 3 seconds
    setTimeout(() => {
      setImportSuccess(false);
    }, 3000);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Import Student Data</h1>
        <p className="mt-1 text-sm text-gray-500">
          Use this page to import student data into the system.
        </p>
      </div>

      {importSuccess && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
          Import completed successfully! The data has been processed and is now available in the system.
        </div>
      )}

      <div className="space-y-6">
        <StudentCSVImport onSuccess={handleImportSuccess} />
        <StudentGradesPDFImport onSuccess={handleImportSuccess} />
      </div>
    </div>
  );
};

export default StudentImportPage;