// frontend/src/domains/students/tests/StudentProfile.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { StudentProfile } from '../pages/StudentProfile';
import { useStudentProfile } from '../hooks/useStudentProfile';

// Mock the API hooks
jest.mock('../hooks/useStudentProfile');

// Create a test query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// Test student profile data
const mockStudentProfile = {
  student: {
    id: '123',
    student_id: 'S12345',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@uwo.ca',
    program: 'JD',
    is_matched: false,
  },
  grades: {
    constitutional_law: 'A',
    contracts: 'B+',
    criminal_law: 'A-',
    property_law: 'B',
    torts: 'A',
  },
  area_rankings: [
    {
      id: '1',
      area: {
        id: '101',
        name: 'Corporate Law',
      },
      rank: 1,
    },
    {
      id: '2',
      area: {
        id: '102',
        name: 'Criminal Law',
      },
      rank: 2,
    },
  ],
};

describe('StudentProfile', () => {
  beforeEach(() => {
    // Mock API hook implementation
    (useStudentProfile as jest.Mock).mockReturnValue({
      data: mockStudentProfile,
      isLoading: false,
      error: null,
    });
  });

  it('renders student profile information', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/students/123']}>
          <Routes>
            <Route path="/students/:studentId" element={<StudentProfile />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Wait for component to finish rendering
    await waitFor(() => {
      // Check that student name is displayed
      expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      // Check that student ID is displayed
      expect(screen.getByText(/S12345/i)).toBeInTheDocument();
      // Check that email is displayed
      expect(screen.getByText(/john.doe@uwo.ca/i)).toBeInTheDocument();
      // Check that program is displayed
      expect(screen.getByText(/JD/i)).toBeInTheDocument();
    });

    // Check that grades are displayed
    expect(screen.getByText(/Constitutional Law/i)).toBeInTheDocument();
    expect(screen.getByText(/A/i)).toBeInTheDocument();
    expect(screen.getByText(/Contracts/i)).toBeInTheDocument();
    expect(screen.getByText(/B\+/i)).toBeInTheDocument();

    // Check that area rankings are displayed
    expect(screen.getByText(/Corporate Law/i)).toBeInTheDocument();
    expect(screen.getByText(/Criminal Law/i)).toBeInTheDocument();
  });

  it('shows loading state when data is loading', async () => {
    // Mock loading state
    (useStudentProfile as jest.Mock).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/students/123']}>
          <Routes>
            <Route path="/students/:studentId" element={<StudentProfile />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Check for loading indicator
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error state when there is an error', async () => {
    // Mock error state
    (useStudentProfile as jest.Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to load student profile'),
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/students/123']}>
          <Routes>
            <Route path="/students/:studentId" element={<StudentProfile />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Check for error message
    expect(screen.getByText(/Failed to load student profile/i)).toBeInTheDocument();
  });
});