// frontend/src/domains/statements/pages/CreateStatementPage.tsx
import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { CreateStatementForm } from '../components/CreateStatementForm';
import { Alert, AlertTitle, AlertDescription } from '../../../components/ui/alert';
import { Button } from '../../../components/ui/button';
import { useCreateStatement } from '../api/statements';
import { CreateStatementRequest } from '../types';

export const CreateStatementPage: React.FC = () => {
  const navigate = useNavigate();
  const { studentId } = useParams<{ studentId?: string }>();
  const createStatementMutation = useCreateStatement();

  // If no student ID was provided, we need to handle that case
  if (!studentId) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            Student ID is required to create a statement
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button onClick={() => navigate('/students')}>
            Select a Student
          </Button>
        </div>
      </div>
    );
  }

  const handleSubmit = (data: CreateStatementRequest) => {
    createStatementMutation.mutate(data, {
      onSuccess: (statement) => {
        navigate(`/statements/${statement.id}`);
      }
    });
  };

  const handleCancel = () => {
    navigate(-1);
  };

  return (
    <div className="container mx-auto py-8">
      <CreateStatementForm
        studentId={studentId}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={createStatementMutation.isLoading}
      />

      {createStatementMutation.isError && (
        <div className="mt-4">
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              {(createStatementMutation.error as Error).message || 'Failed to create statement'}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
};