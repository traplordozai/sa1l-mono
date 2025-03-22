// frontend/src/domains/statements/components/GradeStatementForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage
} from '../../../components/ui/form';
import { Input } from '../../../components/ui/input';
import { Textarea } from '../../../components/ui/textarea';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '../../../components/ui/card';
import { GradeStatementRequest, Statement } from '../types';

// Validation schema
const gradeFormSchema = z.object({
  grade: z.coerce
    .number()
    .min(0, "Grade must be at least 0")
    .max(25, "Grade cannot exceed 25"),
  comments: z.string().optional()
});

interface GradeStatementFormProps {
  statement: Statement;
  onSubmit: (data: GradeStatementRequest) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export const GradeStatementForm: React.FC<GradeStatementFormProps> = ({
  statement,
  onSubmit,
  onCancel,
  isSubmitting
}) => {
  const form = useForm<GradeStatementRequest>({
    resolver: zodResolver(gradeFormSchema),
    defaultValues: {
      grade: 0,
      comments: ''
    }
  });

  const handleSubmit = (data: GradeStatementRequest) => {
    onSubmit(data);
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Grade Statement</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500">Student</h3>
          <p>{statement.student_name}</p>

          <h3 className="text-sm font-medium text-gray-500 mt-4">Area of Law</h3>
          <p>{statement.area_of_law_name}</p>

          <h3 className="text-sm font-medium text-gray-500 mt-4">Statement</h3>
          <div className="bg-gray-50 p-4 rounded-md mt-1 max-h-48 overflow-y-auto">
            {statement.content}
          </div>
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="grade"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Grade (0-25)</FormLabel>
                  <FormControl>
                    <Input type="number" {...field} min={0} max={25} />
                  </FormControl>
                  <FormDescription>
                    Assign a grade between 0 and 25 points
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="comments"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Comments (Optional)</FormLabel>
                  <FormControl>
                    <Textarea {...field} rows={4} />
                  </FormControl>
                  <FormDescription>
                    Provide feedback or comments about the grade
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex justify-end space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Grade'}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};