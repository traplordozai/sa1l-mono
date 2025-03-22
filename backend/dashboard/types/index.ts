// frontend/src/domains/dashboard/types/index.ts
export interface DashboardStats {
  total_students: number;
  matched_students: number;
  pending_matches: number;
  approval_needed: number;
  total_organizations: number;
  available_positions: number;
  filled_positions: number;
  ungraded_statements: number;

  match_status_chart: {
    status: string;
    count: number;
  }[];

  area_law_chart: {
    area: string;
    count: number;
  }[];

  student_growth: {
    rate: number;
    direction: 'increase' | 'decrease';
    new_count: number;
  };

  organization_growth: {
    rate: number;
    direction: 'increase' | 'decrease';
    new_count: number;
  };

  match_rate: {
    percentage: number;
    total: number;
  };
}

export interface ActivityItem {
  id: string;
  user: string;
  action: string;
  target: string;
  date: string;
  relative_time: string;
}