import React, { useState } from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Alert, AlertTitle, AlertDescription } from '../../../components/ui/alert';
import { useDropzone } from 'react-dropzone';
import { importGradesPdf } from '../services/importApi';
import { useMutation } from '@tanstack/react-query';
import { Progress } from '../../../components/ui/progress';
import { ImportStatus } from '../types';
import { useImportStatus } from '../hooks/useImportStatus';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';

interface ImportGradesFormProps {
  onSuccess: () => void;
  onError: (error: Error) => void;
}

const ImportGradesForm: React.FC<ImportGradesFormProps> = ({ onSuccess, onError }) => {
  const [file, setFile] = useState<File | null>(null);
  const [studentId, setStudentId] = useState<string>('');
  const [importLogId, setImportLogId] = useState<string | null>(null);

  // Monitor import status if we have an importLogId
  const { status, progress, refreshStatus } = useImportStatus(importLogId);

  // Handle file drop and selection
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    onDrop: acceptedFiles => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0]);
      }
    }
  });

  // Mutation for importing grades
  const importMutation = useMutation({
    mutationFn: importGradesPdf,
    onSuccess: (data) => {
      setImportLogId(data.import_log_id);
      onSuccess();
    },
    onError: (error: Error) => {
      onError(error);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    if (studentId.trim()) {
      formData.append('student_id', studentId);
    }

    importMutation.mutate(formData);
  };

  const resetForm = () => {
    setFile(null);
    setStudentId('');
    setImportLogId(null);
  };

  // Determine if we should show the status
  const showStatus = importLogId && status !== null;

  // Determine button state
  const isButtonDisabled = !file || importMutation.isPending || (showStatus && status !== ImportStatus.FAILED);

  return (
    <form onSubmit={handleSubmit}>
      <Card className="bg-slate-50">
        <CardContent className="pt-6">
          {/* Student ID input */}
          <div className="mb-4">
            <Label htmlFor="student-id">Student ID (Optional)</Label>
            <Input
              id="student-id"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="Enter student ID if known"
              className="mt-1"
            />
            <p className="text-sm text-gray-500 mt-1">
              If left blank, the system will try to extract student information from the PDF
            </p>
          </div>

          {/* File dropzone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-md p-6 text-center cursor-pointer mb-4
              ${isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-primary'}
              ${file ? 'border-green-500 bg-green-50' : ''}
            `}
          >
            <input {...getInputProps()} />
            {file ? (
              <div className="text-green-600">
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-green-500">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            ) : (
              <div>
                {isDragActive ? (
                  <p className="text-primary">Drop the PDF file here...</p>
                ) : (
                  <p>Drag and drop a PDF file here, or click to select file</p>
                )}
                <p className="text-sm text-gray-500 mt-1">
                  Only .pdf files are supported
                </p>
              </div>
            )}
          </div>

          {/* Import progress and status */}
          {showStatus && (
            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">
                  Import Status: <span className="font-bold">{status}</span>
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={refreshStatus}
                  disabled={status === ImportStatus.COMPLETED}
                >
                  Refresh
                </Button>
              </div>
              <Progress value={progress} className="h-2 mb-2" />

              {status === ImportStatus.COMPLETED && (
                <Alert variant="success" className="mt-2">
                  <AlertTitle>Import Complete</AlertTitle>
                  <AlertDescription>
                    The grades were successfully processed.
                  </AlertDescription>
                </Alert>
              )}

              {status === ImportStatus.FAILED && (
                <Alert variant="destructive" className="mt-2">
                  <AlertTitle>Import Failed</AlertTitle>
                  <AlertDescription>
                    There was an error processing the grades. Please check the import logs for details.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={resetForm}
              disabled={importMutation.isPending}
            >
              Clear
            </Button>
            <Button
              type="submit"
              disabled={isButtonDisabled}
            >
              {importMutation.isPending ? 'Uploading...' : 'Upload & Process'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </form>
  );
};

export default ImportGradesForm;