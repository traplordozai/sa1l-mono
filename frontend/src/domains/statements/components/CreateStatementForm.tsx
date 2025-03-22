// frontend/src/domains/statements/components/CreateStatementForm.tsx
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../../../components/ui/select';
import { Textarea } from '../../../components/ui/textarea';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '../../../components/ui/card';
import { useAreasOfLaw } from '../api/areasOfLaw';
import { CreateStatementRequest } from '../types';

// Validation schema
const createStatementSchema = z.object({
  student: z.string().min(1, "Student is required"),
  area_of_law: z.string().min(1, "Area of law is required"),
  content: z.string().min(10, "Statement must be at least 10 characters")
});

interface CreateStatementFormProps {
  studentId: string;
  onSubmit: (data: CreateStatementRequest) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export const CreateStatementForm: React.FC<CreateStatementFormProps> = ({
  studentId,
  onSubmit,
  onCancel,
  isSubmitting
}) => {
  const { data: areas, isLoading: areasLoading } = useAreasOfLaw();

  const form = useForm<CreateStatementRequest>({
    resolver: zodResolver(createStatementSchema),
    defaultValues: {
      student: studentId,
      area_of_law: '',
      content: ''
    }
  });

  const handleSubmit = (data: CreateStatementRequest) => {
    onSubmit(data);
  };

  return (
    <Card className="max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Create New Statement</CardTitle>
      </CardHeader>

      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="area_of_law"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Area of Law</FormLabel>
                  <Select
                    disabled={areasLoading || isSubmitting}
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select an area of law" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {areas?.map((area) => (
                        <SelectItem key={area.id} value={area.id}>
                          {area.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Choose the area of law for your statement
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="content"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Statement Content</FormLabel>
                  <FormControl>
                    <Textarea
                      {...field}
                      rows={8}
                      placeholder="Write your statement here..."
                      disabled={isSubmitting}
                    />
                  </FormControl>
                  <FormDescription>
                    Provide a detailed statement explaining your interest in this area of law
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
                disabled={isSubmitting || areasLoading}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Statement'}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};