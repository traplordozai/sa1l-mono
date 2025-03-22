// frontend/src/domains/statements/components/GradeImportForm.tsx
import React, { useState } from 'react';
import { useImportGrades } from '../api/gradeImports';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '../../../components/ui/alert';

export const GradeImportForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const importGradesMutation = useImportGrades();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      importGradesMutation.mutate(file);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Import Grades</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="grades-file" className="block text-sm font-medium text-gray-700 mb-1">
              Select File
            </label>
            <input
              id="grades-file"
              type="file"
              accept=".csv,.pdf,.xlsx"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-purple-50 file:text-purple-700
                hover:file:bg-purple-100"
            />
            <p className="mt-1 text-xs text-gray-500">
              Supported formats: CSV, PDF, Excel
            </p>
          </div>

          <Button
            type="submit"
            disabled={!file || importGradesMutation.isLoading}
          >
            {importGradesMutation.isLoading ? 'Importing...' : 'Import Grades'}
          </Button>

          {importGradesMutation.isError && (
            <Alert variant="destructive">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                {(importGradesMutation.error as Error).message || 'Failed to import grades'}
              </AlertDescription>
            </Alert>
          )}

          {importGradesMutation.isSuccess && (
            <Alert variant="success">
              <AlertTitle>Success</AlertTitle>
              <AlertDescription>
                {importGradesMutation.data?.message || 'Grades imported successfully'}
                {importGradesMutation.data?.success_count > 0 && (
                  <div className="mt-2">
                    Successfully imported {importGradesMutation.data.success_count} grades.
                    {importGradesMutation.data.error_count > 0 && (
                      <span> {importGradesMutation.data.error_count} errors occurred.</span>
                    )}
                  </div>
                )}
              </AlertDescription>
            </Alert>
          )}
        </form>
      </CardContent>
    </Card>
  );
};