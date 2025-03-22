// frontend/src/domains/statements/pages/GradingDashboardPage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { StatementsList } from '../components/StatementsList';
import { GradingStatisticsCard } from '../components/GradingStatisticsCard';
import { GradeImportForm } from '../components/GradeImportForm';
import { Button } from '../../../components/ui/button';
import { useUngradedStatements } from '../api/statements';
import { Statement } from '../types';

export const GradingDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { 
    data: ungradedStatements = [], 
    isLoading, 
    error 
  } = useUngradedStatements();
  
  const handleGradeStatement = (statement: Statement) => {
    navigate(`/statements/${statement.id}/grade`);
  };
  
  const handleViewStatement = (statement: Statement) => {
    navigate(`/statements/${statement.id}`);
  };
  
  return (
    <div className="container mx-auto py-6 space-y-6">
      <h1 className="text-2xl font-bold">Grading Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-xl font-semibold">Statements Awaiting Review</h2>
          
          <StatementsList
            statements={ungradedStatements}
            isLoading={isLoading}
            error={error as Error}
            onViewStatement={handleViewStatement}
            onGradeStatement={handleGradeStatement}
          />
        </div>
        
        <div className="space-y-6">
          <GradingStatisticsCard />
          <GradeImportForm />
        </div>
      </div>
    </div>
  );
};