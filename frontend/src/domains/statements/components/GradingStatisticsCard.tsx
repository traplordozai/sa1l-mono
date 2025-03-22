// frontend/src/domains/statements/components/GradingStatisticsCard.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Progress } from '../../../components/ui/progress';
import { useGradingStatistics } from '../api/statements';

export const GradingStatisticsCard: React.FC = () => {
  const { data: statistics, isLoading, error } = useGradingStatistics();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Grading Progress</CardTitle>
        </CardHeader>
        <CardContent className="py-4">
          <div className="flex justify-center">Loading statistics...</div>
        </CardContent>
      </Card>
    );
  }

  if (error || !statistics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Grading Progress</CardTitle>
        </CardHeader>
        <CardContent className="py-4">
          <div className="text-red-500">Error loading statistics</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Grading Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{statistics.completion_percentage.toFixed(1)}%</span>
          </div>
          <Progress value={statistics.completion_percentage} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 p-3 rounded-md">
            <div className="text-sm font-medium text-gray-500">Statements</div>
            <div className="text-2xl font-bold">{statistics.total_statements}</div>
          </div>

          <div className="bg-gray-50 p-3 rounded-md">
            <div className="text-sm font-medium text-gray-500">Graded</div>
            <div className="text-2xl font-bold">{statistics.graded_statements}</div>
          </div>

          <div className="bg-gray-50 p-3 rounded-md">
            <div className="text-sm font-medium text-gray-500">Pending</div>
            <div className="text-2xl font-bold">{statistics.ungraded_statements}</div>
          </div>
        </div>

        {statistics.area_statistics.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">Average Grades by Area</h3>
            <div className="space-y-2">
              {statistics.area_statistics.map((areaStat, index) => (
                <div key={index} className="bg-gray-50 p-2 rounded-md flex justify-between">
                  <span>{areaStat.area}</span>
                  <span className="font-medium">
                    {areaStat.average_grade !== null
                      ? `${areaStat.average_grade.toFixed(1)}/25`
                      : 'No grades'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};