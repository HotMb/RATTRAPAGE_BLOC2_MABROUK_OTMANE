import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from './LoginPage';
import { AuthProvider } from '../auth/AuthContext';
import * as apiClient from '../api/client';

jest.mock('../api/client', () => ({
  ...jest.requireActual('../api/client'),
  apiRequest: jest.fn(),
  setTokens: jest.fn(),
}));

function renderLoginPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

test('submits credentials and shows an error on invalid login', async () => {
  apiClient.apiRequest.mockRejectedValueOnce({ status: 401, data: { detail: 'No active account found' } });
  renderLoginPage();

  fireEvent.change(screen.getByLabelText(/identifiant/i), { target: { value: 'baduser' } });
  fireEvent.change(screen.getByLabelText(/mot de passe/i), { target: { value: 'badpass' } });
  fireEvent.click(screen.getByRole('button', { name: /se connecter/i }));

  await waitFor(() => {
    expect(screen.getByRole('alert')).toHaveTextContent(/identifiant ou mot de passe incorrect/i);
  });
});

test('calls apiRequest with the entered credentials', async () => {
  apiClient.apiRequest.mockResolvedValueOnce({ access: 'a', refresh: 'b', username: 'admin', role: 'ADMIN' });
  renderLoginPage();

  fireEvent.change(screen.getByLabelText(/identifiant/i), { target: { value: 'admin' } });
  fireEvent.change(screen.getByLabelText(/mot de passe/i), { target: { value: 'pass1234' } });
  fireEvent.click(screen.getByRole('button', { name: /se connecter/i }));

  await waitFor(() => {
    expect(apiClient.apiRequest).toHaveBeenCalledWith('/auth/login/', {
      method: 'POST',
      body: { username: 'admin', password: 'pass1234' },
    });
  });
});
