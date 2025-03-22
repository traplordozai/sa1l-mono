import { useQuery, useMutation, useQueryClient } from 'react-query';
import { organizationsApi } from './api';
import {
  Organization,
  OrganizationDetail,
  OrganizationListItem,
  OrganizationFormData,
  OrganizationContact,
  OrganizationContactFormData,
  OrganizationStatistics
} from './types';

// Organization query hooks
export const useOrganizations = (params?: Record<string, any>) => {
  return useQuery<OrganizationListItem[], Error>(
    ['organizations', params],
    () => organizationsApi.getAll(params),
    {
      keepPreviousData: true,
    }
  );
};

export const useOrganization = (id: string) => {
  return useQuery<OrganizationDetail, Error>(
    ['organization', id],
    () => organizationsApi.getById(id),
    {
      enabled: !!id,
    }
  );
};

export const useOrganizationsWithPositions = () => {
  return useQuery<OrganizationListItem[], Error>(
    'organizationsWithPositions',
    organizationsApi.getWithAvailablePositions
  );
};

export const useOrganizationStatistics = () => {
  return useQuery<OrganizationStatistics, Error>(
    'organizationStatistics',
    organizationsApi.getStatistics
  );
};

// Organization mutation hooks
export const useCreateOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<Organization, Error, OrganizationFormData>(
    (data) => organizationsApi.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('organizations');
        queryClient.invalidateQueries('organizationStatistics');
      },
    }
  );
};

export const useUpdateOrganization = (id: string) => {
  const queryClient = useQueryClient();

  return useMutation<Organization, Error, Partial<OrganizationFormData>>(
    (data) => organizationsApi.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['organization', id]);
        queryClient.invalidateQueries('organizations');
        queryClient.invalidateQueries('organizationStatistics');
      },
    }
  );
};

export const useDeleteOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>(
    (id) => organizationsApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('organizations');
        queryClient.invalidateQueries('organizationStatistics');
      },
    }
  );
};

// Organization Contact query hooks
export const useOrganizationContacts = (organizationId: string) => {
  return useQuery<OrganizationContact[], Error>(
    ['organizationContacts', organizationId],
    () => organizationsApi.getContacts(organizationId),
    {
      enabled: !!organizationId,
    }
  );
};

// Organization Contact mutation hooks
export const useCreateContact = () => {
  const queryClient = useQueryClient();

  return useMutation<OrganizationContact, Error, OrganizationContactFormData>(
    (data) => organizationsApi.createContact(data),
    {
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries(['organizationContacts', variables.organization_id]);
        queryClient.invalidateQueries(['organization', variables.organization_id]);
      },
    }
  );
};

export const useUpdateContact = () => {
  const queryClient = useQueryClient();

  return useMutation<
    OrganizationContact,
    Error,
    { id: string; data: Partial<OrganizationContactFormData> }
  >(
    ({ id, data }) => organizationsApi.updateContact(id, data),
    {
      onSuccess: (_, variables) => {
        if (variables.data.organization_id) {
          queryClient.invalidateQueries(['organizationContacts', variables.data.organization_id]);
          queryClient.invalidateQueries(['organization', variables.data.organization_id]);
        }
      },
    }
  );
};

export const useDeleteContact = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, { id: string; organizationId: string }>(
    ({ id }) => organizationsApi.deleteContact(id),
    {
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries(['organizationContacts', variables.organizationId]);
        queryClient.invalidateQueries(['organization', variables.organizationId]);
      },
    }
  );
};

export const useSetPrimaryContact = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, { id: string; organizationId: string }>(
    ({ id }) => organizationsApi.setPrimaryContact(id),
    {
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries(['organizationContacts', variables.organizationId]);
        queryClient.invalidateQueries(['organization', variables.organizationId]);
      },
    }
  );
};