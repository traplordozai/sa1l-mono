// frontend/src/domains/statements/types.ts
export interface Statement {
  id: string;
  student: string;
  student_name: string;
  area_of_law: string;
  area_name: string;
  content: string;
  is_graded: boolean;
  created_at: string;
  updated_at: string;
}

export interface Grade {
  id: string;
  statement: string;
  score: number;
  graded_by: string;
  graded_by_name: string;
  graded_at: string;
  comments: string | null;
  criteria_scores: CriteriaScore[];
}

export interface CriteriaScore {
  id: string;
  criteria: string;
  criteria_name: string;
  criteria_weight: number;
  score: number;
}

export interface GradingCriteria {
  id: string;
  name: string;
  description: string;
  weight: number;
}

export interface StatementWithGrade extends Statement {
  grade: Grade | null;
}