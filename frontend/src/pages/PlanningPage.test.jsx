import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import PlanningPage from './PlanningPage';
import { AuthProvider } from '../auth/AuthContext';
import * as apiClient from '../api/client';

jest.mock('../api/client', () => ({
  ...jest.requireActual('../api/client'),
  apiRequest: jest.fn(),
}));

beforeEach(() => {
  localStorage.setItem('auth_user', JSON.stringify({ username: 'etu1', role: 'ETUDIANT' }));
});
afterEach(() => localStorage.clear());

test('renders the fetched courses', async () => {
  apiClient.apiRequest.mockResolvedValueOnce([
    {
      id: 1, intitule: 'Maths', debut: '2026-09-15T09:00:00Z', fin: '2026-09-15T10:00:00Z',
      classe: 1, salle: 1, intervenant: 1,
    },
  ]);

  render(
    <MemoryRouter>
      <AuthProvider>
        <PlanningPage />
      </AuthProvider>
    </MemoryRouter>
  );

  await waitFor(() => {
    expect(screen.getByText('Maths')).toBeInTheDocument();
  });
});
