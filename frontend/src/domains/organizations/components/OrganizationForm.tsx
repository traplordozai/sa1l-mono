import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOrganization, useCreateOrganization, useUpdateOrganization } from '../hooks';
import { useOrganizationFormStore } from '../store';
import { AreasOfLawSelect } from '../../statements/components/AreasOfLawSelect';

const OrganizationForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditMode = !!id;
  const { data: organization, isLoading } = useOrganization(id || '');
  const createOrganization = useCreateOrganization();
  const updateOrganization = useUpdateOrganization(id || '');

  const {
    formData,
    errors,
    setField,
    setErrors,
    clearErrors,
    resetForm,
    initializeForm,
  } = useOrganizationFormStore();

  // Initialize form data when editing an existing organization
  useEffect(() => {
    if (isEditMode && organization) {
      initializeForm({
        name: organization.name,
        description: organization.description || '',
        area_ids: organization.areas_of_law.map(area => area.id),
        location: organization.location,
        contact_email: organization.contact_email,
        contact_phone: organization.contact_phone || '',
        website: organization.website || '',
        requirements: organization.requirements || '',
        available_positions: organization.available_positions,
        is_active: organization.is_active,
      });
    } else if (!isEditMode) {
      resetForm();
    }
  }, [isEditMode, organization, resetForm, initializeForm]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }

    if (!formData.contact_email.trim()) {
      newErrors.contact_email = 'Email is required';
    } else if (!/^\S+@\S+\.\S+$/.test(formData.contact_email)) {
      newErrors.contact_email = 'Invalid email format';
    }

    if (formData.website && !/^https?:\/\/\S+\.\S+/.test(formData.website)) {
      newErrors.website = 'Website must be a valid URL';
    }

    if (formData.available_positions <= 0) {
      newErrors.available_positions = 'Available positions must be greater than 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearErrors();

    if (!validateForm()) {
      return;
    }

    try {
      if (isEditMode) {
        await updateOrganization.mutateAsync(formData);
        navigate(`/organizations/${id}`);
      } else {
        const newOrganization = await createOrganization.mutateAsync(formData);
        navigate(`/organizations/${newOrganization.id}`);
      }
    } catch (error: any) {
      if (error.response?.data) {
        setErrors(error.response.data);
      } else {
        alert('An error occurred: ' + (error.message || 'Unknown error'));
      }
    }
  };

  if (isEditMode && isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {isEditMode ? 'Edit Organization' : 'New Organization'}
        </h1>
        <button
          onClick={() => navigate(isEditMode ? `/organizations/${id}` : '/organizations')}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setField('name', e.target.value)}
                className={`mt-1 block w-full border ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-500">{errors.name}</p>
              )}
            </div>

            {/* Location */}
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                Location <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="location"
                value={formData.location}
                onChange={(e) => setField('location', e.target.value)}
                className={`mt-1 block w-full border ${
                  errors.location ? 'border-red-500' : 'border-gray-300'
                } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
              />
              {errors.location && (
                <p className="mt-1 text-sm text-red-500">{errors.location}</p>
              )}
            </div>

            {/* Areas of Law */}
            <div>
              <label htmlFor="areas" className="block text-sm font-medium text-gray-700">
                Areas of Law
              </label>
              <AreasOfLawSelect
                selectedAreaIds={formData.area_ids}
                onChange={(areaIds) => setField('area_ids', areaIds)}
                className="mt-1"
              />
              {errors.area_ids && (
                <p className="mt-1 text-sm text-red-500">{errors.area_ids}</p>
              )}
            </div>

            {/* Available Positions */}
            <div>
              <label htmlFor="available_positions" className="block text-sm font-medium text-gray-700">
                Available Positions <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                id="available_positions"
                min="1"
                value={formData.available_positions}
                onChange={(e) => setField('available_positions', parseInt(e.target.value) || 0)}
                className={`mt-1 block w-full border ${
                  errors.available_positions ? 'border-red-500' : 'border-gray-300'
                } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
              />
              {errors.available_positions && (
                <p className="mt-1 text-sm text-red-500">{errors.available_positions}</p>
              )}
            </div>

            {/* Contact Email */}
            <div>
              <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700">
                Contact Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="contact_email"
                value={formData.contact_email}
                onChange={(e) => setField('contact_email', e.target.value)}
                className={`mt-1 block w-full border ${
                  errors.contact_email ? 'border-red-500' : 'border-gray-300'
                } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
              />
              {errors.contact_email && (
                <p className="mt-1 text-sm text-red-500">{errors.contact_email}</p>
              )}
            </div>

            {/* Contact Phone */}
            <div>
              <label htmlFor="contact_phone" className="block text-sm font-medium text-gray-700">
                Contact Phone
              </label>
              <input
                type="tel"
                id="contact_phone"
                value={formData.contact_phone}
                onChange={(e) => setField('contact_phone', e.target.value)}
                className={`mt-1 block w-full border ${
                  errors.contact_phone ? 'border-red-500' : 'border-gray-300'
                } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
              />
              {errors.contact_phone && (
                <p className="mt-1 text-sm text-red-500">{errors.contact_phone}</p>
              )}
            </div>

            {/* Website */}
            <div>
              <label htmlFor="website" className="block text-sm font-medium text-gray-700">
                Website
              </label>
              <input
                type="url"
                id="website"
                value={formData.website}
                onChange={(e) => setField('website', e.target.value)}
                className={`mt-1 block w-full border ${
                  errors.website ? 'border-red-500' : 'border-gray-300'
                } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
              />
              {errors.website && (
                <p className="mt-1 text-sm text-red-500">{errors.website}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                rows={3}
                value={formData.description}
                onChange={(e) => setField('description', e.target.value)}
                className={`mt-1 block w-full border ${
                  errors.description ? 'border-red-500' : 'border-gray-300'
                } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-500">{errors.description}</p>
              )}
            </div>

            {/* Requirements */}
            <div>
              <label htmlFor="requirements" className="block text-sm font-medium text-gray-700">
                Requirements
              </label>
              <textarea
                id="requirements"
                rows={3}
                value={formData.requirements}
                onChange={(e) => setField('requirements', e.target.value)}
                className={`mt-1 block w-full border ${
                  errors.requirements ? 'border-red-500' : 'border-gray-300'
                } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
              />
              {errors.requirements && (
                <p className="mt-1 text-sm text-red-500">{errors.requirements}</p>
              )}
            </div>

            {/* Active Status */}
            <div className="flex items-center">
              <input
                id="is_active"
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setField('is_active', e.target.checked)}
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                Organization is active and accepting applications
              </label>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate(isEditMode ? `/organizations/${id}` : '/organizations')}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                disabled={createOrganization.isLoading || updateOrganization.isLoading}
              >
                {createOrganization.isLoading || updateOrganization.isLoading ? (
                  <div className="mr-2 h-4 w-4 border-t-2 border-b-2 border-white rounded-full animate-spin"></div>
                ) : null}
                {isEditMode ? 'Update' : 'Create'} Organization
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default OrganizationForm;