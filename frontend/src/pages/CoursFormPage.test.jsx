import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import CoursFormPage from './CoursFormPage';
import * as apiClient from '../api/client';

jest.mock('../api/client', () => ({
  ...jest.requireActual('../api/client'),
  apiRequest: jest.fn(),
}));

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/cours/nouveau']}>
      <Routes>
        <Route path="/cours/nouveau" element={<CoursFormPage />} />
      </Routes>
    </MemoryRouter>
  );
}

test('shows the 409 conflict message returned by the API', async () => {
  apiClient.apiRequest
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce([])
    .mockRejectedValueOnce({
      status: 409,
      data: { detail: 'Conflit détecté : la salle est déjà occupée par le cours « Maths ».' },
    });

  renderPage();

  fireEvent.change(screen.getByLabelText(/intitulé/i), { target: { value: 'Anglais' } });
  fireEvent.click(screen.getByRole('button', { name: /enregistrer/i }));

  await waitFor(() => {
    expect(screen.getByRole('alert')).toHaveTextContent(/conflit détecté/i);
  });
});
