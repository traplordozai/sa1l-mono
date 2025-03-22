// frontend/src/domains/matching/types.ts
export interface MatchingRound {
  id: string;
  name: string;
  description?: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  started_at?: string;
  completed_at?: string;
  initiated_by?: string;
  initiated_by_name?: string;
  algorithm_type: string;
  algorithm_settings: Record<string, any>;
  total_students: number;
  matched_students: number;
  total_organizations: number;
  average_match_score?: number;
  matches_count: number;
  created_at: string;
  updated_at: string;
}

export interface MatchScoreDetails {
  id: string;
  match: string;
  area_of_law_score: number;
  area_of_law_weight: number;
  statement_score?: number;
  statement_weight?: number;
  location_score?: number;
  location_weight?: number;
  work_preference_score?: number;
  work_preference_weight?: number;
  grade_score?: number;
  grade_weight?: number;
  additional_factors: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Match {
  id: string;
  round: string;
  student: string;
  student_name: string;
  organization: string;
  organization_name: string;
  area_of_law: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'CONFIRMED';
  match_score: number;
  student_rank?: number;
  organization_rank?: number;
  statement_score?: number;
  approved_by?: string;
  approved_at?: string;
  rejected_at?: string;
  notes?: string;
  score_details?: MatchScoreDetails;
  created_at: string;
  updated_at: string;
}

export interface MatchingPreference {
  id: string;
  preference_type: 'STUDENT' | 'ORGANIZATION';
  student?: string;
  organization?: string;
  area_of_law: string;
  weight: number;
  rank?: number;
  created_at: string;
  updated_at: string;
}

export interface MatchingStatistics {
  round?: {
    id: string;
    name: string;
    status: string;
    total_students: number;
    matched_students: number;
    match_percentage: number;
    average_score: number;
  };
  overall: {
    total_rounds: number;
    completed_rounds: number;
    total_matches: number;
    confirmed_matches: number;
    average_score: number;
  };
  matches: {
    total: number;
    by_status: Record<string, number>;
    avg_score: number;
    by_area: Record<string, number>;
  };
}

export interface RunMatchingRequest {
  round_id: string;
}

export interface UpdateMatchStatusRequest {
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'CONFIRMED';
  notes?: string;
}