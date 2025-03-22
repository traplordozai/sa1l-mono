import { AreaOfLaw } from '../statements/types';

export interface OrganizationContact {
  id: string;
  name: string;
  title?: string;
  email: string;
  phone?: string;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface Organization {
  id: string;
  name: string;
  description?: string;
  areas_of_law: AreaOfLaw[];
  location: string;
  contact_email: string;
  contact_phone?: string;
  website?: string;
  requirements?: string;
  available_positions: number;
  filled_positions: number;
  remaining_positions: number;
  is_active: boolean;
  primary_contact?: OrganizationContact;
  created_at: string;
  updated_at: string;
}

export interface OrganizationDetail extends Organization {
  contacts: OrganizationContact[];
}

export interface OrganizationListItem {
  id: string;
  name: string;
  location: string;
  areas_of_law: string[];
  available_positions: number;
  filled_positions: number;
  remaining_positions: number;
  is_active: boolean;
}

export interface OrganizationFormData {
  name: string;
  description?: string;
  area_ids: string[];
  location: string;
  contact_email: string;
  contact_phone?: string;
  website?: string;
  requirements?: string;
  available_positions: number;
  is_active: boolean;
}

export interface OrganizationContactFormData {
  name: string;
  title?: string;
  email: string;
  phone?: string;
  is_primary: boolean;
  organization_id: string;
}

export interface OrganizationStatistics {
  total_count: number;
  active_count: number;
  total_positions: number;
  filled_positions: number;
  available_positions: number;
  organizations_by_area: Array<{
    id: string;
    name: string;
    organization_count: number;
  }>;
}