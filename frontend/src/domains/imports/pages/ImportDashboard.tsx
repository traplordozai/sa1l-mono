import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Card, CardHeader, CardTitle, CardDescription, CardContent
} from '../../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Button } from '../../../components/ui/button';
import { Alert, AlertTitle, AlertDescription } from '../../../components/ui/alert';
import ImportStudentsForm from '../components/ImportStudentsForm';
import ImportGradesForm from '../components/ImportGradesForm';
import ImportOrganizationsForm from '../components/ImportOrganizationsForm';
import ImportHistoryTable from '../components/ImportHistoryTable';
import { getImportLogs } from '../services/importApi';
import { useToast } from '../../../components/ui/toast';

const ImportDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('students');
  const { toast } = useToast();

  // Fetch import history
  const {
    data: importLogs,
    isLoading,
    isError,
    refetch
  } = useQuery({
    queryKey: ['importLogs'],
    queryFn: getImportLogs,
  });

  const handleImportSuccess = () => {
    toast({
      title: 'Import started',
      description: 'Your import has been queued and will process in the background.',
      variant: 'default',
    });
    refetch();
  };

  const handleImportError = (error: Error) => {
    toast({
      title: 'Import failed',
      description: error.message || 'There was an error processing your import.',
      variant: 'destructive',
    });
  };

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Data Import Dashboard</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Import Data</CardTitle>
          <CardDescription>
            Import student records, organization data, or grades from CSV and PDF files.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid grid-cols-3 w-[400px]">
              <TabsTrigger value="students">Students</TabsTrigger>
              <TabsTrigger value="organizations">Organizations</TabsTrigger>
              <TabsTrigger value="grades">Grades</TabsTrigger>
            </TabsList>

            <TabsContent value="students" className="mt-6">
              <Alert variant="info" className="mb-4">
                <AlertTitle>Student CSV Import</AlertTitle>
                <AlertDescription>
                  Upload a CSV file containing student information. The file should include columns for
                  First Name, Last Name, Email, Student ID, Program, and optional area preferences.
                </AlertDescription>
              </Alert>
              <ImportStudentsForm
                onSuccess={handleImportSuccess}
                onError={handleImportError}
              />
            </TabsContent>

            <TabsContent value="organizations" className="mt-6">
              <Alert variant="info" className="mb-4">
                <AlertTitle>Organization CSV Import</AlertTitle>
                <AlertDescription>
                  Upload a CSV file containing organization information. The file should include columns for
                  Organization Name, Contact Information, Location, and Areas of Law.
                </AlertDescription>
              </Alert>
              <ImportOrganizationsForm
                onSuccess={handleImportSuccess}
                onError={handleImportError}
              />
            </TabsContent>

            <TabsContent value="grades" className="mt-6">
              <Alert variant="info" className="mb-4">
                <AlertTitle>Student Grades PDF Import</AlertTitle>
                <AlertDescription>
                  Upload a PDF file containing student grades. The system will extract course grades
                  and associate them with the specified student ID.
                </AlertDescription>
              </Alert>
              <ImportGradesForm
                onSuccess={handleImportSuccess}
                onError={handleImportError}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Import History</CardTitle>
          <CardDescription>
            View past and current imports with their status and results.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <span className="loading loading-spinner loading-lg"></span>
            </div>
          ) : isError ? (
            <Alert variant="destructive">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>Failed to load import history.</AlertDescription>
              <Button variant="outline" className="mt-2" onClick={() => refetch()}>
                Retry
              </Button>
            </Alert>
          ) : (
            <ImportHistoryTable importLogs={importLogs || []} onRefresh={() => refetch()} />
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ImportDashboard;