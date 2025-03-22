/**
 * Student domain type definitions
 */

export interface Student {
  id: string;
  student_id: string;
  given_names: string;
  last_name: string;
  full_name: string;
  email: string;
  backup_email?: string;
  program: string;
  location_preferences: string[];
  work_preferences: string[];
  is_matched: boolean;
  needs_approval: boolean;
  is_active: boolean;
  last_active?: string;
  profile_completion: number;
  created_at: string;
  updated_at: string;
}

export interface StudentGrade {
  id: string;
  student: string;
  constitutional_law?: string;
  contracts?: string;
  criminal_law?: string;
  property_law?: string;
  torts?: string;
  lrw_case_brief?: string;
  lrw_multiple_case?: string;
  lrw_short_memo?: string;
  grade_pdf?: string;
}

export interface AreaOfLaw {
  id: string;
  name: string;
  description?: string;
}

export interface StudentAreaRanking {
  id: string;
  student: string;
  area: string;
  area_name: string;
  rank: number;
  comments?: string;
}

export interface Statement {
  id: string;
  student: string;
  area_of_law: string;
  area_name: string;
  content: string;
  statement_grade?: number;
  graded_by?: string;
  graded_by_name?: string;
  graded_at?: string;
}

export interface SelfProposedExternship {
  id: string;
  student: string;
  organization: string;
  supervisor: string;
  supervisor_email: string;
  address?: string;
  website?: string;
  description: string;
}

export interface StudentDetailResponse extends Student {
  grades?: StudentGrade;
  statements: Statement[];
  area_rankings: StudentAreaRanking[];
  self_proposed?: SelfProposedExternship;
}

export interface CSVImportResult {
  success_count: number;
  error_count: number;
  errors: string[];
}

export interface PDFImportResult {
  success: boolean;
  message: string;
  student_id?: string;
  grades?: Record<string, string>;
}