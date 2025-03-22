// frontend/src/domains/statements/components/StatementsList.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell
} from '../../../components/ui/table';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Statement } from '../types';

interface StatementsListProps {
  statements: Statement[];
  isLoading: boolean;
  error: Error | null;
  onViewStatement?: (statement: Statement) => void;
  onGradeStatement?: (statement: Statement) => void;
}

export const StatementsList: React.FC<StatementsListProps> = ({
  statements,
  isLoading,
  error,
  onViewStatement,
  onGradeStatement
}) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredStatements = statements.filter(statement =>
    statement.student_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    statement.area_of_law_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    statement.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return <div className="flex justify-center py-8">Loading statements...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-500 p-4 rounded-md">
        Error loading statements: {error.message}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Statements</h2>
        <Input
          type="search"
          placeholder="Search statements..."
          className="w-64"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {filteredStatements.length === 0 ? (
        <div className="bg-gray-50 p-8 text-center rounded-md">
          No statements found.
        </div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Student</TableHead>
              <TableHead>Area of Law</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Grade</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredStatements.map((statement) => (
              <TableRow key={statement.id}>
                <TableCell className="font-medium">{statement.student_name}</TableCell>
                <TableCell>{statement.area_of_law_name}</TableCell>
                <TableCell>{new Date(statement.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  {statement.grade !== null ? (
                    <span className="font-semibold">{statement.grade}/25</span>
                  ) : (
                    <span className="text-gray-400">Not graded</span>
                  )}
                </TableCell>
                <TableCell>
                  {statement.is_graded ? (
                    <Badge variant="success">Graded</Badge>
                  ) : (
                    <Badge variant="warning">Pending</Badge>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewStatement ? onViewStatement(statement) : navigate(`/statements/${statement.id}`)}
                    >
                      View
                    </Button>

                    {!statement.is_graded && onGradeStatement && (
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => onGradeStatement(statement)}
                      >
                        Grade
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
};