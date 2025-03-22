import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOrganization, useDeleteOrganization } from '../hooks';
import OrganizationContactList from './OrganizationContactList';
import {
  BuildingOfficeIcon,
  MapPinIcon,
  EnvelopeIcon,
  PhoneIcon,
  GlobeAltIcon,
  TrashIcon,
  PencilIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

const OrganizationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: organization, isLoading, error } = useOrganization(id || '');
  const deleteOrganization = useDeleteOrganization();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  if (error || !organization) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <p className="text-red-700">
          {error ? `Error loading organization: ${error.message}` : 'Organization not found'}
        </p>
      </div>
    );
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this organization?')) {
      try {
        await deleteOrganization.mutateAsync(organization.id);
        navigate('/organizations');
      } catch (err) {
        alert('Failed to delete organization');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">{organization.name}</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => navigate(`/organizations/${organization.id}/edit`)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
          >
            <PencilIcon className="h-4 w-4 mr-2" />
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <TrashIcon className="h-4 w-4 mr-2" />
            Delete
          </button>
        </div>
      </div>

      {/* Status Badge */}
      <div className="flex items-center">
        {organization.is_active ? (
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <CheckCircleIcon className="h-5 w-5 mr-1" />
            Active
          </div>
        ) : (
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
            <XCircleIcon className="h-5 w-5 mr-1" />
            Inactive
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <div className="flex items-center">
            <BuildingOfficeIcon className="h-6 w-6 text-gray-400 mr-2" />
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Organization Details
            </h3>
          </div>
        </div>

        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-gray-200">
            {/* Location */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <MapPinIcon className="h-5 w-5 text-gray-400 mr-1" />
                Location
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {organization.location}
              </dd>
            </div>

            {/* Contact Email */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <EnvelopeIcon className="h-5 w-5 text-gray-400 mr-1" />
                Contact Email
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <a href={`mailto:${organization.contact_email}`} className="text-purple-600 hover:text-purple-900">
                  {organization.contact_email}
                </a>
              </dd>
            </div>

            {/* Contact Phone */}
            {organization.contact_phone && (
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500 flex items-center">
                  <PhoneIcon className="h-5 w-5 text-gray-400 mr-1" />
                  Contact Phone
                </dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <a href={`tel:${organization.contact_phone}`} className="text-purple-600 hover:text-purple-900">
                    {organization.contact_phone}
                  </a>
                </dd>
              </div>
            )}

            {/* Website */}
            {organization.website && (
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500 flex items-center">
                  <GlobeAltIcon className="h-5 w-5 text-gray-400 mr-1" />
                  Website
                </dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <a href={organization.website} target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:text-purple-900">
                    {organization.website}
                  </a>
                </dd>
              </div>
            )}

            {/* Areas of Law */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Areas of Law</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex flex-wrap">
                  {organization.areas_of_law.map((area) => (
                    <span
                      key={area.id}
                      className="mr-2 mb-2 inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-purple-100 text-purple-800"
                    >
                      {area.name}
                    </span>
                  ))}
                </div>
              </dd>
            </div>

            {/* Available Positions */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Available Positions</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <span className="font-medium">{organization.filled_positions}</span>
                  <span className="mx-1">/</span>
                  <span>{organization.available_positions}</span>
                  <span className="ml-2 text-gray-500">
                    ({organization.remaining_positions} remaining)
                  </span>
                </div>
              </dd>
            </div>

            {/* Description */}
            {organization.description && (
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Description</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {organization.description}
                </dd>
              </div>
            )}

            {/* Requirements */}
            {organization.requirements && (
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Requirements</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {organization.requirements}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* Organization Contacts */}
      <OrganizationContactList organizationId={organization.id} />
    </div>
  );
};

export default OrganizationDetail;