import React, { useState } from 'react';
import { useUploadStudentGrades } from '../services/studentService';
import FileInput from '../shared/components/atoms/FileInput';
import ImportStatusMessage from '../shared/components/molecules/ImportStatusMessage';

interface StudentGradesPDFImportProps {
  onSuccess?: () => void;
  className?: string;
}

const StudentGradesPDFImport: React.FC<StudentGradesPDFImportProps> = ({
  onSuccess,
  className = '',
}) => {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [studentId, setStudentId] = useState('');
  const [importMessage, setImportMessage] = useState('');

  const uploadGradesMutation = useUploadStudentGrades();

  const handlePdfUpload = async () => {
    if (!pdfFile || !studentId) {
      setImportMessage('Please provide both a student ID and a PDF file');
      return;
    }

    try {
      const result = await uploadGradesMutation.mutateAsync({
        studentId,
        file: pdfFile
      });

      setImportMessage(result.message);

      // Clear inputs on success
      if (result.success) {
        setPdfFile(null);
        setStudentId('');

        // Call success callback if provided
        if (onSuccess) {
          onSuccess();
        }
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Error uploading PDF';
      setImportMessage(errorMessage);
      console.error('PDF upload error:', error);
    }
  };

  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
      <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Student Grades PDF</h3>
      <div className="text-sm text-gray-500 mb-4">
        <p>
          Upload a PDF containing a student's grades. The system will extract course grades
          and associate them with the specified student ID.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label htmlFor="student-id" className="block text-sm font-medium text-gray-700 mb-1">
            Student ID <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="student-id"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="Enter student ID"
          />
        </div>

        <FileInput
          id="pdf-file-input"
          label="Grades PDF"
          accept=".pdf"
          onChange={setPdfFile}
          disabled={uploadGradesMutation.isPending}
          required
        />

        <div className="flex justify-end">
          <button
            onClick={handlePdfUpload}
            disabled={!pdfFile || !studentId || uploadGradesMutation.isPending}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {uploadGradesMutation.isPending ? 'Uploading...' : 'Upload PDF'}
          </button>
        </div>
      </div>

      {importMessage && (
        <div className="mt-4">
          <ImportStatusMessage message={importMessage} />
        </div>
      )}
    </div>
  );
};

export default StudentGradesPDFImport;