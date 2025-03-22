import create from 'zustand';
import { OrganizationFormData, OrganizationContactFormData } from './types';

interface OrganizationFormState {
  // Form data
  formData: OrganizationFormData;

  // Form validation errors
  errors: Record<string, string>;

  // Form actions
  setField: <K extends keyof OrganizationFormData>(
    field: K,
    value: OrganizationFormData[K]
  ) => void;

  setErrors: (errors: Record<string, string>) => void;
  clearErrors: () => void;

  resetForm: (data?: Partial<OrganizationFormData>) => void;
  initializeForm: (data: Partial<OrganizationFormData>) => void;
}

const defaultFormData: OrganizationFormData = {
  name: '',
  description: '',
  area_ids: [],
  location: '',
  contact_email: '',
  contact_phone: '',
  website: '',
  requirements: '',
  available_positions: 1,
  is_active: true,
};

export const useOrganizationFormStore = create<OrganizationFormState>((set) => ({
  formData: { ...defaultFormData },
  errors: {},

  setField: (field, value) =>
    set((state) => ({
      formData: {
        ...state.formData,
        [field]: value,
      },
      // Clear error for this field when it's updated
      errors: {
        ...state.errors,
        [field]: undefined,
      },
    })),

  setErrors: (errors) => set({ errors }),
  clearErrors: () => set({ errors: {} }),

  resetForm: (data) =>
    set((state) => ({
      formData: {
        ...defaultFormData,
        ...data,
      },
      errors: {},
    })),

  initializeForm: (data) =>
    set({
      formData: {
        ...defaultFormData,
        ...data,
      },
      errors: {},
    }),
}));

interface ContactFormState {
  // Form data
  formData: OrganizationContactFormData;

  // Form validation errors
  errors: Record<string, string>;

  // Form actions
  setField: <K extends keyof OrganizationContactFormData>(
    field: K,
    value: OrganizationContactFormData[K]
  ) => void;

  setErrors: (errors: Record<string, string>) => void;
  clearErrors: () => void;

  resetForm: (organizationId?: string) => void;
  initializeForm: (data: Partial<OrganizationContactFormData>) => void;
}

const defaultContactFormData: OrganizationContactFormData = {
  name: '',
  title: '',
  email: '',
  phone: '',
  is_primary: false,
  organization_id: '',
};

export const useContactFormStore = create<ContactFormState>((set) => ({
  formData: { ...defaultContactFormData },
  errors: {},

  setField: (field, value) =>
    set((state) => ({
      formData: {
        ...state.formData,
        [field]: value,
      },
      // Clear error for this field when it's updated
      errors: {
        ...state.errors,
        [field]: undefined,
      },
    })),

  setErrors: (errors) => set({ errors }),
  clearErrors: () => set({ errors: {} }),

  resetForm: (organizationId) =>
    set({
      formData: {
        ...defaultContactFormData,
        organization_id: organizationId || '',
      },
      errors: {},
    }),

  initializeForm: (data) =>
    set({
      formData: {
        ...defaultContactFormData,
        ...data,
      },
      errors: {},
    }),
}));