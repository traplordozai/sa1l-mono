import React, { useState } from 'react';
import {
  useOrganizationContacts,
  useCreateContact,
  useUpdateContact,
  useDeleteContact,
  useSetPrimaryContact
} from '../hooks';
import { useContactFormStore } from '../store';
import {
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  PencilIcon,
  TrashIcon,
  StarIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

interface OrganizationContactListProps {
  organizationId: string;
}

const OrganizationContactList: React.FC<OrganizationContactListProps> = ({ organizationId }) => {
  const [isAddingContact, setIsAddingContact] = useState(false);
  const [editingContactId, setEditingContactId] = useState<string | null>(null);

  const {
    data: contacts,
    isLoading,
    error,
    refetch
  } = useOrganizationContacts(organizationId);

  const createContact = useCreateContact();
  const updateContact = useUpdateContact();
  const deleteContact = useDeleteContact();
  const setPrimaryContact = useSetPrimaryContact();

  const {
    formData,
    errors,
    setField,
    setErrors,
    clearErrors,
    resetForm,
    initializeForm,
  } = useContactFormStore();

  const handleAddContact = () => {
    resetForm(organizationId);
    setIsAddingContact(true);
    setEditingContactId(null);
  };

  const handleEditContact = (contact: any) => {
    initializeForm({
      name: contact.name,
      title: contact.title || '',
      email: contact.email,
      phone: contact.phone || '',
      is_primary: contact.is_primary,
      organization_id: organizationId,
    });
    setEditingContactId(contact.id);
    setIsAddingContact(false);
  };

  const validateContactForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmitContact = async (e: React.FormEvent) => {
    e.preventDefault();
    clearErrors();

    if (!validateContactForm()) {
      return;
    }

    try {
      if (editingContactId) {
        await updateContact.mutateAsync({
          id: editingContactId,
          data: formData,
        });
      } else {
        await createContact.mutateAsync(formData);
      }

      resetForm();
      setIsAddingContact(false);
      setEditingContactId(null);
      refetch();
    } catch (error: any) {
      if (error.response?.data) {
        setErrors(error.response.data);
      } else {
        alert('An error occurred: ' + (error.message || 'Unknown error'));
      }
    }
  };

  const handleDeleteContact = async (contactId: string) => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      try {
        await deleteContact.mutateAsync({
          id: contactId,
          organizationId,
        });
        refetch();
      } catch (error) {
        alert('Failed to delete contact');
      }
    }
  };

  const handleSetPrimary = async (contactId: string) => {
    try {
      await setPrimaryContact.mutateAsync({
        id: contactId,
        organizationId,
      });
      refetch();
    } catch (error) {
      alert('Failed to set primary contact');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-24">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-700"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <p className="text-red-700">Error loading contacts</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Contacts
        </h3>
        <button
          onClick={handleAddContact}
          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          Add Contact
        </button>
      </div>

      {/* Contact Form */}
      {(isAddingContact || editingContactId) && (
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <form onSubmit={handleSubmitContact} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
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

              {/* Title */}
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={formData.title}
                  onChange={(e) => setField('title', e.target.value)}
                  className={`mt-1 block w-full border ${
                    errors.title ? 'border-red-500' : 'border-gray-300'
                  } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
                />
                {errors.title && (
                  <p className="mt-1 text-sm text-red-500">{errors.title}</p>
                )}
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => setField('email', e.target.value)}
                  className={`mt-1 block w-full border ${
                    errors.email ? 'border-red-500' : 'border-gray-300'
                  } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-500">{errors.email}</p>
                )}
              </div>

              {/* Phone */}
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                  Phone
                </label>
                <input
                  type="tel"
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setField('phone', e.target.value)}
                  className={`mt-1 block w-full border ${
                    errors.phone ? 'border-red-500' : 'border-gray-300'
                  } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm`}
                />
                {errors.phone && (
                  <p className="mt-1 text-sm text-red-500">{errors.phone}</p>
                )}
              </div>
            </div>

            {/* Primary Contact */}
            <div className="flex items-center">
              <input
                id="is_primary"
                type="checkbox"
                checked={formData.is_primary}
                onChange={(e) => setField('is_primary', e.target.checked)}
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
              />
              <label htmlFor="is_primary" className="ml-2 block text-sm text-gray-700">
                Primary Contact
              </label>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  resetForm();
                  setIsAddingContact(false);
                  setEditingContactId(null);
                }}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                disabled={createContact.isLoading || updateContact.isLoading}
              >
                {createContact.isLoading || updateContact.isLoading ? (
                  <div className="mr-2 h-4 w-4 border-t-2 border-b-2 border-white rounded-full animate-spin"></div>
                ) : null}
                {editingContactId ? 'Update' : 'Add'} Contact
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Contact List */}
      <div className="border-t border-gray-200">
        {contacts && contacts.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {contacts.map((contact) => (
              <li key={contact.id} className="px-4 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <UserIcon className="h-8 w-8 text-gray-400" />
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <h4 className="text-lg font-medium text-gray-900">{contact.name}</h4>
                        {contact.is_primary && (
                          <span className="ml-2 inline-flex items-center">
                            <StarIconSolid className="h-5 w-5 text-yellow-400" />
                          </span>
                        )}
                      </div>
                      {contact.title && (
                        <p className="text-sm text-gray-500">{contact.title}</p>
                      )}
                      <div className="mt-1 flex items-center">
                        <EnvelopeIcon className="h-4 w-4 text-gray-400 mr-1" />
                        <a href={`mailto:${contact.email}`} className="text-sm text-purple-600 hover:text-purple-900">
                          {contact.email}
                        </a>
                      </div>
                      {contact.phone && (
                        <div className="mt-1 flex items-center">
                          <PhoneIcon className="h-4 w-4 text-gray-400 mr-1" />
                          <a href={`tel:${contact.phone}`} className="text-sm text-purple-600 hover:text-purple-900">
                            {contact.phone}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    {!contact.is_primary && (
                      <button
                        onClick={() => handleSetPrimary(contact.id)}
                        title="Set as primary contact"
                        className="text-gray-400 hover:text-yellow-500"
                      >
                        <StarIcon className="h-5 w-5" />
                      </button>
                    )}
                    <button
                      onClick={() => handleEditContact(contact)}
                      title="Edit contact"
                      className="text-gray-400 hover:text-purple-500"
                    >
                      <PencilIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDeleteContact(contact.id)}
                      title="Delete contact"
                      className="text-gray-400 hover:text-red-500"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="px-4 py-5 text-center text-gray-500">
            No contacts found. Click "Add Contact" to create one.
          </div>
        )}
      </div>
    </div>
  );
};

export default OrganizationContactList;