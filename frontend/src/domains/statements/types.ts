// frontend/src/domains/statements/types.ts
export interface AreaOfLaw {
  id: string;
  name: string;
  description?: string;
  statement_count?: number;
}

export interface Statement {
  id: string;
  student: string;
  student_name: string;
  area_of_law: string;
  area_of_law_name: string;
  content: string;
  grade: number | null;
  graded_by: string | null;
  graded_by_name: string | null;
  graded_at: string | null;
  is_graded: boolean;
  created_at: string;
  updated_at: string;
}

export interface RubricCriterion {
  id: string;
  name: string;
  description: string;
  max_points: number;
}

export interface GradingRubric {
  id: string;
  name: string;
  description: string;
  area_of_law: string;
  area_of_law_name: string;
  max_points: number;
  is_active: boolean;
  criteria: RubricCriterion[];
}

export interface GradeImport {
  id: string;
  imported_by: string;
  imported_by_name: string;
  file_name: string;
  import_date: string;
  success_count: number;
  error_count: number;
  errors: string;
}

export interface GradingStatistics {
  total_statements: number;
  graded_statements: number;
  ungraded_statements: number;
  completion_percentage: number;
  area_statistics: Array<{
    area: string;
    average_grade: number | null;
    count: number;
  }>;
}

export interface CreateStatementRequest {
  student: string;
  area_of_law: string;
  content: string;
}

export interface UpdateStatementRequest {
  content: string;
}

export interface GradeStatementRequest {
  grade: number;
  comments?: string;
}