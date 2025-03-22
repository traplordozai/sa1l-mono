// frontend/src/domains/matching/hooks.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { matchingApi } from './api';
import {
  MatchingRound, Match, MatchingPreference,
  MatchingStatistics, UpdateMatchStatusRequest
} from './types';

// Matching Rounds hooks
export const useMatchingRounds = () => {
  return useQuery<MatchingRound[], Error>(
    ['matching-rounds'],
    () => matchingApi.getRounds()
  );
};

export const useMatchingRound = (id: string) => {
  return useQuery<MatchingRound, Error>(
    ['matching-rounds', id],
    () => matchingApi.getRoundById(id),
    {
      enabled: !!id
    }
  );
};

export const useCreateMatchingRound = () => {
  const queryClient = useQueryClient();

  return useMutation<MatchingRound, Error, Partial<MatchingRound>>(
    (data) => matchingApi.createRound(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['matching-rounds']);
      }
    }
  );
};

export const useUpdateMatchingRound = () => {
  const queryClient = useQueryClient();

  return useMutation<MatchingRound, Error, { id: string; data: Partial<MatchingRound> }>(
    ({ id, data }) => matchingApi.updateRound(id, data),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['matching-rounds']);
        queryClient.invalidateQueries(['matching-rounds', data.id]);
      }
    }
  );
};

export const useDeleteMatchingRound = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>(
    (id) => matchingApi.deleteRound(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['matching-rounds']);
      }
    }
  );
};

export const useRunMatchingAlgorithm = () => {
  const queryClient = useQueryClient();

  return useMutation<any, Error, string>(
    (roundId) => matchingApi.runAlgorithm(roundId),
    {
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries(['matching-rounds']);
        queryClient.invalidateQueries(['matching-rounds', variables]);
        queryClient.invalidateQueries(['matches']);
      }
    }
  );
};

export const useRoundMatches = (roundId: string) => {
  return useQuery<Match[], Error>(
    ['matching-rounds', roundId, 'matches'],
    () => matchingApi.getRoundMatches(roundId),
    {
      enabled: !!roundId
    }
  );
};

export const useRoundStatistics = (roundId: string) => {
  return useQuery<MatchingStatistics, Error>(
    ['matching-rounds', roundId, 'statistics'],
    () => matchingApi.getRoundStatistics(roundId),
    {
      enabled: !!roundId
    }
  );
};

// Matches hooks
export const useMatches = (params?: any) => {
  return useQuery<Match[], Error>(
    ['matches', params],
    () => matchingApi.getMatches(params)
  );
};

export const useMatch = (id: string) => {
  return useQuery<Match, Error>(
    ['matches', id],
    () => matchingApi.getMatchById(id),
    {
      enabled: !!id
    }
  );
};

export const useUpdateMatchStatus = () => {
  const queryClient = useQueryClient();

  return useMutation<any, Error, { id: string; data: UpdateMatchStatusRequest }>(
    ({ id, data }) => matchingApi.updateMatchStatus(id, data),
    {
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries(['matches']);
        queryClient.invalidateQueries(['matches', variables.id]);
        queryClient.invalidateQueries(['matching-rounds']);
      }
    }
  );
};

// Preferences hooks
export const usePreferences = (params?: any) => {
  return useQuery<MatchingPreference[], Error>(
    ['preferences', params],
    () => matchingApi.getPreferences(params)
  );
};

export const useCreatePreference = () => {
  const queryClient = useQueryClient();

  return useMutation<MatchingPreference, Error, Partial<MatchingPreference>>(
    (data) => matchingApi.createPreference(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['preferences']);
      }
    }
  );
};

export const useUpdatePreference = () => {
  const queryClient = useQueryClient();

  return useMutation<MatchingPreference, Error, { id: string; data: Partial<MatchingPreference> }>(
    ({ id, data }) => matchingApi.updatePreference(id, data),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['preferences']);
      }
    }
  );
};

export const useDeletePreference = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>(
    (id) => matchingApi.deletePreference(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['preferences']);
      }
    }
  );
};

// Statistics hook
export const useMatchingStatistics = () => {
  return useQuery<MatchingStatistics, Error>(
    ['matching-statistics'],
    () => matchingApi.getStatistics()
  );
};