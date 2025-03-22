// src/domains/organizations/api/index.ts
import axios from 'axios';
import { API_URL } from '../../../config';
import { Organization, OrganizationStatistics } from '../types';

const API_PATH = `${API_URL}/organizations`;

export const organizationApi = {
  getAll: async (): Promise<Organization[]> => {
    const response = await axios.get(API_PATH);
    return response.data;
  },

  getById: async (id: string): Promise<Organization> => {
    const response = await axios.get(`${API_PATH}/${id}`);
    return response.data;
  },

  create: async (data: Partial<Organization>): Promise<Organization> => {
    const response = await axios.post(API_PATH, data);
    return response.data;
  },

  update: async (id: string, data: Partial<Organization>): Promise<Organization> => {
    const response = await axios.patch(`${API_PATH}/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await axios.delete(`${API_PATH}/${id}`);
  },

  getStatistics: async (): Promise<OrganizationStatistics> => {
    const response = await axios.get(`${API_PATH}/statistics`);
    return response.data;
  }
};