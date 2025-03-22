// frontend/src/domains/statements/components/StatementDetail.tsx
import React from 'react';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Statement } from '../types';

interface StatementDetailProps {
  statement: Statement;
  onBack?: () => void;
  onGrade?: () => void;
  onEdit?: () => void;
}

export const StatementDetail: React.FC<StatementDetailProps> = ({
  statement,
  onBack,
  onGrade,
  onEdit
}) => {
  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>{statement.area_of_law_name} Statement</CardTitle>
          <div className="text-sm text-gray-500">Submitted by {statement.student_name}</div>
        </div>

        <div className="flex space-x-2">
          {onBack && (
            <Button variant="ghost" onClick={onBack}>
              Back
            </Button>
          )}

          {!statement.is_graded && onGrade && (
            <Button variant="default" onClick={onGrade}>
              Grade Statement
            </Button>
          )}

          {!statement.is_graded && onEdit && (
            <Button variant="outline" onClick={onEdit}>
              Edit
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="flex justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">Submission Date</p>
            <p>{new Date(statement.created_at).toLocaleDateString()}</p>
          </div>

          <div>
            <p className="text-sm font-medium text-gray-500">Status</p>
            {statement.is_graded ? (
              <Badge variant="success">Graded</Badge>
            ) : (
              <Badge variant="warning">Pending</Badge>
            )}
          </div>

          {statement.is_graded && (
            <div>
              <p className="text-sm font-medium text-gray-500">Grade</p>
              <p className="font-semibold">{statement.grade}/25</p>
            </div>
          )}

          {statement.is_graded && statement.graded_by_name && (
            <div>
              <p className="text-sm font-medium text-gray-500">Graded By</p>
              <p>{statement.graded_by_name}</p>
            </div>
          )}
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-2">Statement Content</h3>
          <div className="bg-gray-50 p-4 rounded-md whitespace-pre-line">
            {statement.content}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};