// frontend/src/domains/statements/api.ts
import api from '../../shared/api';
import { Statement, Grade, GradingCriteria, StatementWithGrade } from './types';

export const getStatements = async () => {
  const response = await api.get('/statements/');
  return response.data;
};

export const getStatement = async (id: string) => {
  const response = await api.get(`/statements/${id}/`);
  return response.data as StatementWithGrade;
};

export const getUngraded = async () => {
  const response = await api.get('/statements/ungraded/');
  return response.data as Statement[];
};

export const createGrade = async (statementId: string, score: number, comments?: string, criteriaScores?: Record<string, number>) => {
  const response = await api.post('/grades/', {
    statement: statementId,
    score,
    comments,
    criteria_scores: criteriaScores
  });
  return response.data as Grade;
};

export const getGradingCriteria = async () => {
  const response = await api.get('/grading-criteria/');
  return response.data as GradingCriteria[];
};

export const getGradingDashboard = async () => {
  const response = await api.get('/grades/dashboard/');
  return response.data;
};