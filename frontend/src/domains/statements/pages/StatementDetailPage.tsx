// frontend/src/domains/statements/pages/StatementDetailPage.tsx
import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useStatement } from '../api/statements';
import { StatementDetail } from '../components/StatementDetail';
import { Button } from '../../../components/ui/button';
import { Alert, AlertTitle, AlertDescription } from '../../../components/ui/alert';

export const StatementDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: statement,
    isLoading,
    error
  } = useStatement(id!);

  const handleBack = () => {
    navigate('/statements');
  };

  const handleGrade = () => {
    navigate(`/statements/${id}/grade`);
  };

  const handleEdit = () => {
    navigate(`/statements/${id}/edit`);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 flex justify-center">
        <div>Loading statement...</div>
      </div>
    );
  }

  if (error || !statement) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error ? (error as Error).message : 'Statement not found'}
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button onClick={handleBack}>Back to Statements</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <StatementDetail
        statement={statement}
        onBack={handleBack}
        onGrade={handleGrade}
        onEdit={handleEdit}
      />
    </div>
  );
};