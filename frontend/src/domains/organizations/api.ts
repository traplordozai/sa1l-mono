import apiClient from '../../utils/apiClient';
import {
  Organization,
  OrganizationDetail,
  OrganizationListItem,
  OrganizationFormData,
  OrganizationContact,
  OrganizationContactFormData,
  OrganizationStatistics
} from './types';

const BASE_URL = '/organizations';

export const organizationsApi = {
  // Organization endpoints
  getAll: async (params?: Record<string, any>): Promise<OrganizationListItem[]> => {
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  getById: async (id: string): Promise<OrganizationDetail> => {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  create: async (data: OrganizationFormData): Promise<Organization> => {
    const response = await apiClient.post(BASE_URL, data);
    return response.data;
  },

  update: async (id: string, data: Partial<OrganizationFormData>): Promise<Organization> => {
    const response = await apiClient.patch(`${BASE_URL}/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`${BASE_URL}/${id}`);
  },

  getWithAvailablePositions: async (): Promise<OrganizationListItem[]> => {
    const response = await apiClient.get(`${BASE_URL}/with_available_positions`);
    return response.data;
  },

  getStatistics: async (): Promise<OrganizationStatistics> => {
    const response = await apiClient.get(`${BASE_URL}/statistics`);
    return response.data;
  },

  // Organization Contact endpoints
  getContacts: async (organizationId: string): Promise<OrganizationContact[]> => {
    const response = await apiClient.get(`${BASE_URL}/${organizationId}/contacts`);
    return response.data;
  },

  createContact: async (data: OrganizationContactFormData): Promise<OrganizationContact> => {
    const response = await apiClient.post('/organization-contacts', data);
    return response.data;
  },

  updateContact: async (id: string, data: Partial<OrganizationContactFormData>): Promise<OrganizationContact> => {
    const response = await apiClient.patch(`/organization-contacts/${id}`, data);
    return response.data;
  },

  deleteContact: async (id: string): Promise<void> => {
    await apiClient.delete(`/organization-contacts/${id}`);
  },

  setPrimaryContact: async (id: string): Promise<void> => {
    await apiClient.post(`/organization-contacts/${id}/set_as_primary`);
  }
};