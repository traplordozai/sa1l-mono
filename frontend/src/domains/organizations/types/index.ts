// src/domains/organizations/types/index.ts
export interface Organization {
  id: string;
  name: string;
  description: string;
  areas_of_law: string[];
  location: string;
  contact_email: string;
  contact_phone: string;
  website?: string;
  requirements?: string;
  available_positions: number;
  filled_positions: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AreaOfLawBreakdown {
  name: string;
  count: number;
}

export interface RecentOrganization {
  id: string;
  name: string;
  location: string;
  is_active: boolean;
  available_positions: number;
  filled_positions: number;
}

export interface OrganizationStatistics {
  total_count: number;
  active_count: number;
  total_positions: number;
  filled_positions: number;
  available_positions: number;
  areas_of_law_breakdown: AreaOfLawBreakdown[];
  recent_organizations: RecentOrganization[];
}