// frontend/src/domains/matching/components/MatchingRoundForm.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateMatchingRound } from '../hooks';
import { MatchingRound } from '../types';

const MatchingRoundForm: React.FC = () => {
  const navigate = useNavigate();
  const createRound = useCreateMatchingRound();

  const [form, setForm] = useState<Partial<MatchingRound>>({
    name: '',
    description: '',
    algorithm_type: 'weighted_preference',
    algorithm_settings: {
      area_weight: 0.35,
      statement_weight: 0.25,
      grade_weight: 0.15,
      location_weight: 0.15,
      work_preference_weight: 0.10
    },
  });

  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSettingsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      algorithm_settings: {
        ...(prev.algorithm_settings || {}),
        [name]: parseFloat(value)
      }
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate form
    if (!form.name) {
      setError('Name is required');
      return;
    }

    try {
      const result = await createRound.mutateAsync(form);
      navigate(`/matching/rounds/${result.id}`);
    } catch (err: any) {
      setError(err.message || 'An error occurred while creating the matching round');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Create New Matching Round</h1>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6">
        <div className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              id="name"
              required
              value={form.name}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              name="description"
              id="description"
              rows={3}
              value={form.description || ''}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
            />
          </div>

          <div>
            <label htmlFor="algorithm_type" className="block text-sm font-medium text-gray-700">
              Algorithm Type
            </label>
            <select
              name="algorithm_type"
              id="algorithm_type"
              value={form.algorithm_type}
              onChange={handleChange}
              className="mt-1 block w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
            >
              <option value="weighted_preference">Weighted Preference</option>
              <option value="preference_priority">Preference Priority</option>
            </select>
          </div>

          <div className="border-t border-gray-200 pt-6">
            <h3 className="text-lg font-medium text-gray-900">Algorithm Settings</h3>
            <p className="mt-1 text-sm text-gray-500">
              Adjust the weights of different factors in the matching algorithm. The total must add up to 1.0.
            </p>

            <div className="mt-4 space-y-4">
              <div>
                <label htmlFor="area_weight" className="block text-sm font-medium text-gray-700">
                  Area of Law Weight
                </label>
                <input
                  type="number"
                  name="area_weight"
                  id="area_weight"
                  min="0"
                  max="1"
                  step="0.05"
                  value={form.algorithm_settings?.area_weight || 0.35}
                  onChange={handleSettingsChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
                />
              </div>

              <div>
                <label htmlFor="statement_weight" className="block text-sm font-medium text-gray-700">
                  Statement Weight
                </label>
                <input
                  type="number"
                  name="statement_weight"
                  id="statement_weight"
                  min="0"
                  max="1"
                  step="0.05"
                  value={form.algorithm_settings?.statement_weight || 0.25}
                  onChange={handleSettingsChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
                />
              </div>

              <div>
                <label htmlFor="grade_weight" className="block text-sm font-medium text-gray-700">
                  Grade Weight
                </label>
                <input
                  type="number"
                  name="grade_weight"
                  id="grade_weight"
                  min="0"
                  max="1"
                  step="0.05"
                  value={form.algorithm_settings?.grade_weight || 0.15}
                  onChange={handleSettingsChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
                />
              </div>

              <div>
                <label htmlFor="location_weight" className="block text-sm font-medium text-gray-700">
                  Location Weight
                </label>
                <input
                  type="number"
                  name="location_weight"
                  id="location_weight"
      min="0"
                  max="1"
                  step="0.05"
                  value={form.algorithm_settings?.location_weight || 0.15}
                  onChange={handleSettingsChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
                />
              </div>

              <div>
                <label htmlFor="work_preference_weight" className="block text-sm font-medium text-gray-700">
                  Work Preference Weight
                </label>
                <input
                  type="number"
                  name="work_preference_weight"
                  id="work_preference_weight"
                  min="0"
                  max="1"
                  step="0.05"
                  value={form.algorithm_settings?.work_preference_weight || 0.10}
                  onChange={handleSettingsChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
                />
              </div>

              {/* Display total weight */}
              {form.algorithm_settings && (
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-sm text-gray-700">
                    Total Weight: {(
                      (form.algorithm_settings.area_weight || 0) +
                      (form.algorithm_settings.statement_weight || 0) +
                      (form.algorithm_settings.grade_weight || 0) +
                      (form.algorithm_settings.location_weight || 0) +
                      (form.algorithm_settings.work_preference_weight || 0)
                    ).toFixed(2)}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createRound.isLoading}
            className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50"
          >
            {createRound.isLoading ? 'Creating...' : 'Create'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default MatchingRoundForm;