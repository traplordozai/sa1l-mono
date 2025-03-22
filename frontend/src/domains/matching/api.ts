// frontend/src/domains/matching/api.ts
import axios from 'axios';
import { API_URL } from '../../config';
import {
  MatchingRound, Match, MatchingPreference,
  MatchingStatistics, UpdateMatchStatusRequest
} from './types';

const API_PATH = `${API_URL}/matching`;

export const matchingApi = {
  // Matching Rounds
  getRounds: async (): Promise<MatchingRound[]> => {
    const response = await axios.get(`${API_PATH}/rounds/`);
    return response.data;
  },

  getRoundById: async (id: string): Promise<MatchingRound> => {
    const response = await axios.get(`${API_PATH}/rounds/${id}/`);
    return response.data;
  },

  createRound: async (data: Partial<MatchingRound>): Promise<MatchingRound> => {
    const response = await axios.post(`${API_PATH}/rounds/`, data);
    return response.data;
  },

  updateRound: async (id: string, data: Partial<MatchingRound>): Promise<MatchingRound> => {
    const response = await axios.patch(`${API_PATH}/rounds/${id}/`, data);
    return response.data;
  },

  deleteRound: async (id: string): Promise<void> => {
    await axios.delete(`${API_PATH}/rounds/${id}/`);
  },

  runAlgorithm: async (roundId: string): Promise<any> => {
    const response = await axios.post(`${API_PATH}/rounds/${roundId}/run_algorithm/`);
    return response.data;
  },

  getRoundMatches: async (roundId: string): Promise<Match[]> => {
    const response = await axios.get(`${API_PATH}/rounds/${roundId}/matches/`);
    return response.data;
  },

  getRoundStatistics: async (roundId: string): Promise<MatchingStatistics> => {
    const response = await axios.get(`${API_PATH}/rounds/${roundId}/statistics/`);
    return response.data;
  },

  // Matches
  getMatches: async (params?: any): Promise<Match[]> => {
    const response = await axios.get(`${API_PATH}/matches/`, { params });
    return response.data;
  },

  getMatchById: async (id: string): Promise<Match> => {
    const response = await axios.get(`${API_PATH}/matches/${id}/`);
    return response.data;
  },

  updateMatchStatus: async (id: string, data: UpdateMatchStatusRequest): Promise<any> => {
    const response = await axios.post(`${API_PATH}/matches/${id}/update_status/`, data);
    return response.data;
  },

  // Preferences
  getPreferences: async (params?: any): Promise<MatchingPreference[]> => {
    const response = await axios.get(`${API_PATH}/preferences/`, { params });
    return response.data;
  },

  createPreference: async (data: Partial<MatchingPreference>): Promise<MatchingPreference> => {
    const response = await axios.post(`${API_PATH}/preferences/`, data);
    return response.data;
  },

  updatePreference: async (id: string, data: Partial<MatchingPreference>): Promise<MatchingPreference> => {
    const response = await axios.patch(`${API_PATH}/preferences/${id}/`, data);
    return response.data;
  },

  deletePreference: async (id: string): Promise<void> => {
    await axios.delete(`${API_PATH}/preferences/${id}/`);
  },

  // Statistics
  getStatistics: async (): Promise<MatchingStatistics> => {
    const response = await axios.get(`${API_PATH}/rounds/statistics/`);
    return response.data;
  }
};