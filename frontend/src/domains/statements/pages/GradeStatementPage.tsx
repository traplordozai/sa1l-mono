// frontend/src/domains/statements/pages/GradeStatementPage.tsx
import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useStatement, useGradeStatement } from '../api/statements';
import { GradeStatementForm } from '../components/GradeStatementForm';
import { Alert, AlertTitle, AlertDescription } from '../../../components/ui/alert';
import { Button } from '../../../components/ui/button';
import { GradeStatementRequest } from '../types';

export const GradeStatementPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: statement,
    isLoading: statementLoading,
    error: statementError
  } = useStatement(id!);

  const gradeMutation = useGradeStatement(id!);

  const handleSubmit = (data: GradeStatementRequest) => {
    gradeMutation.mutate(data, {
      onSuccess: () => {
        navigate(`/statements/${id}`);
      }
    });
  };

  const handleCancel = () => {
    navigate(`/statements/${id}`);
  };

  if (statementLoading) {
    return (
      <div className="container mx-auto py-8 flex justify-center">
        <div>Loading statement...</div>
      </div>
    );
  }

  if (statementError || !statement) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {statementError ? (statementError as Error).message : 'Statement not found'}
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button onClick={() => navigate('/statements')}>Back to Statements</Button>
        </div>
      </div>
    );
  }

  // Prevent grading if already graded
  if (statement.is_graded) {
    return (
      <div className="container mx-auto py-8">
        <Alert>
          <AlertTitle>Statement Already Graded</AlertTitle>
          <AlertDescription>
            This statement has already been graded and cannot be modified.
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button onClick={() => navigate(`/statements/${id}`)}>
            View Statement
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <GradeStatementForm
        statement={statement}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={gradeMutation.isLoading}
      />

      {gradeMutation.isError && (
        <div className="mt-4">
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              {(gradeMutation.error as Error).message || 'Failed to submit grade'}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
};