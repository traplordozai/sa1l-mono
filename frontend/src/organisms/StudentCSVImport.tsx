import React, { useState } from 'react';
import { useImportStudentsCSV } from '../services/studentService';
import FileInput from '../shared/components/atoms/FileInput';
import ImportStatusMessage from '../shared/components/molecules/ImportStatusMessage';

interface StudentCSVImportProps {
  onSuccess?: () => void;
  className?: string;
}

const StudentCSVImport: React.FC<StudentCSVImportProps> = ({
  onSuccess,
  className = '',
}) => {
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [importMessage, setImportMessage] = useState('');
  const [importErrors, setImportErrors] = useState<string[]>([]);
  
  const importCsvMutation = useImportStudentsCSV();
  
  const handleCsvUpload = async () => {
    if (!csvFile) {
      setImportMessage('Please select a CSV file');
      return;
    }

    setImportErrors([]);
    
    try {
      const result = await importCsvMutation.mutateAsync(csvFile);
      
      setImportMessage(`Successfully imported ${result.success_count} students`);
      if (result.errors?.length) {
        setImportErrors(result.errors);
      }
      
      // Clear file input on success
      setCsvFile(null);
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Error importing CSV';
      setImportMessage(errorMessage);
      console.error('CSV upload error:', error);
    }
  };
  
  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
      <h3 className="text-lg font-medium text-gray-900 mb-4">Import Students from CSV</h3>
      <div className="text-sm text-gray-500 mb-4">
        <p>
          Upload a CSV file containing student information. The file should include columns for:
        </p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>Student ID</li>
          <li>Given Names</li>
          <li>Last Name</li>
          <li>Email</li>
          <li>Program</li>
          <li>Location Preferences (optional)</li>
          <li>Work Preferences (optional)</li>
        </ul>
      </div>
      
      <div className="flex items-end space-x-4">
        <FileInput
          id="csv-file-input"
          label="CSV File"
          accept=".csv"
          onChange={setCsvFile}
          disabled={importCsvMutation.isPending}
          className="flex-grow"
        />
        
        <button
          onClick={handleCsvUpload}
          disabled={!csvFile || importCsvMutation.isPending}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {importCsvMutation.isPending ? 'Uploading...' : 'Upload CSV'}
        </button>
      </div>
      
      {(importMessage || importErrors.length > 0) && (
        <div className="mt-4">
          <ImportStatusMessage 
            message={importMessage} 
            errors={importErrors} 
          />
        </div>
      )}
    </div>
  );
};

export default StudentCSVImport;