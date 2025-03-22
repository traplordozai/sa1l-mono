// frontend/src/domains/statements/pages/StatementsPage.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { StatementsList } from '../components/StatementsList';
import { GradingStatisticsCard } from '../components/GradingStatisticsCard';
import { Button } from '../../../components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../../../components/ui/select';
import { useStatements } from '../api/statements';
import { useAreasOfLaw } from '../api/areasOfLaw';
import { Statement } from '../types';

export const StatementsPage: React.FC = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    area_of_law: '',
    graded: undefined as boolean | undefined,
  });

  const { data: statements = [], isLoading, error } = useStatements(filters);
  const { data: areas = [] } = useAreasOfLaw();

  const handleViewStatement = (statement: Statement) => {
    navigate(`/statements/${statement.id}`);
  };

  const handleGradeStatement = (statement: Statement) => {
    navigate(`/statements/${statement.id}/grade`);
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Statements</h1>

        <Button
          onClick={() => navigate('/statements/new')}
          variant="default"
        >
          Create Statement
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white p-4 rounded-md shadow-sm mb-4">
            <div className="flex flex-wrap gap-4">
              <div className="w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Area of Law
                </label>
                <Select
                  value={filters.area_of_law}
                  onValueChange={(value) => setFilters({ ...filters, area_of_law: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All areas" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All areas</SelectItem>
                    {areas.map((area) => (
                      <SelectItem key={area.id} value={area.id}>
                        {area.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <Select
                  value={filters.graded === undefined ? '' : String(filters.graded)}
                  onValueChange={(value) => {
                    if (value === '') {
                      setFilters({ ...filters, graded: undefined });
                    } else {
                      setFilters({ ...filters, graded: value === 'true' });
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All statements" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All statements</SelectItem>
                    <SelectItem value="true">Graded</SelectItem>
                    <SelectItem value="false">Ungraded</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <StatementsList
            statements={statements}
            isLoading={isLoading}
            error={error as Error}
            onViewStatement={handleViewStatement}
            onGradeStatement={handleGradeStatement}
          />
        </div>

        <div>
          <GradingStatisticsCard />
        </div>
      </div>
    </div>
  );
};