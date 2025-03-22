// src/domains/organizations/hooks/index.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { organizationApi } from '../api';
import { Organization, OrganizationStatistics } from '../types';

export const useOrganizations = () => {
  return useQuery<Organization[], Error>(
    ['organizations'],
    () => organizationApi.getAll()
  );
};

export const useOrganization = (id: string) => {
  return useQuery<Organization, Error>(
    ['organizations', id],
    () => organizationApi.getById(id),
    {
      enabled: !!id
    }
  );
};

export const useCreateOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<Organization, Error, Partial<Organization>>(
    (data) => organizationApi.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['organizations']);
      }
    }
  );
};

export const useUpdateOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<Organization, Error, { id: string; data: Partial<Organization> }>(
    ({ id, data }) => organizationApi.update(id, data),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['organizations']);
        queryClient.invalidateQueries(['organizations', data.id]);
      }
    }
  );
};

export const useDeleteOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>(
    (id) => organizationApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['organizations']);
      }
    }
  );
};

export const useOrganizationStatistics = () => {
  return useQuery<OrganizationStatistics, Error>(
    ['organization-statistics'],
    () => organizationApi.getStatistics()
  );
};