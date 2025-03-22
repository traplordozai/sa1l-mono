import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useOrganizations } from '../hooks';
import { BuildingOfficeIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const OrganizationList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedArea, setSelectedArea] = useState('');
  const [activeFilter, setActiveFilter] = useState<boolean | null>(true);

  const { data: organizations, isLoading, error } = useOrganizations({
    search: searchQuery,
    area_of_law: selectedArea,
    is_active: activeFilter,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <p className="text-red-700">Error loading organizations: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Organizations</h1>
        <Link
          to="/organizations/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          Add Organization
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 shadow rounded-lg">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {/* Search */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
              placeholder="Search organizations"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Area of Law filter */}
          <div>
            <select
              className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
              value={selectedArea}
              onChange={(e) => setSelectedArea(e.target.value)}
            >
              <option value="">All Areas of Law</option>
              {/* This would be populated from API data */}
              <option value="1">Corporate Law</option>
              <option value="2">Family Law</option>
              <option value="3">Criminal Law</option>
            </select>
          </div>

          {/* Active/Inactive filter */}
          <div>
            <select
              className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
              value={activeFilter === null ? "" : activeFilter.toString()}
              onChange={(e) => {
                const value = e.target.value;
                setActiveFilter(value === "" ? null : value === "true");
              }}
            >
              <option value="">All Status</option>
              <option value="true">Active Only</option>
              <option value="false">Inactive Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Organization List */}
      <div className="bg-white shadow overflow-hidden rounded-md">
        <ul className="divide-y divide-gray-200">
          {organizations?.length === 0 ? (
            <li className="px-6 py-4 text-gray-500 text-center">
              No organizations found.
            </li>
          ) : (
            organizations?.map((org) => (
              <li key={org.id} className="px-6 py-4 hover:bg-gray-50">
                <Link to={`/organizations/${org.id}`} className="block">
                  <div className="flex items-center">
                    <div className="mr-4 flex-shrink-0">
                      <BuildingOfficeIcon className="h-10 w-10 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-lg font-medium text-purple-600 truncate">{org.name}</p>
                      <p className="text-sm text-gray-500 truncate">{org.location}</p>
                      <div className="mt-1 flex flex-wrap">
                        {org.areas_of_law.map((area) => (
                          <span
                            key={area}
                            className="mr-2 mb-2 inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-purple-100 text-purple-800"
                          >
                            {area}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="ml-4 text-right">
                      <div className="text-sm text-gray-900">
                        Positions: {org.filled_positions} / {org.available_positions}
                      </div>
                      <div className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${
                        org.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {org.is_active ? 'Active' : 'Inactive'}
                      </div>
                    </div>
                  </div>
                </Link>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
};

export default OrganizationList;