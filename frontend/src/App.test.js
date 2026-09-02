import { render, screen } from '@testing-library/react';
import App from './App';

function setStoredUser(user) {
  localStorage.setItem('auth_user', JSON.stringify(user));
  localStorage.setItem('auth_tokens', JSON.stringify({ access: 'fake', refresh: 'fake' }));
}

afterEach(() => localStorage.clear());

jest.mock('./api/client', () => ({
  ...jest.requireActual('./api/client'),
  apiRequest: jest.fn().mockResolvedValue([]),
}));

test('etudiant does not see admin management links', () => {
  setStoredUser({ username: 'etu1', role: 'ETUDIANT' });
  render(<App />);
  expect(screen.queryByRole('link', { name: /classes/i })).not.toBeInTheDocument();
  expect(screen.getByRole('link', { name: /planning/i })).toBeInTheDocument();
});

test('admin sees admin management links', () => {
  setStoredUser({ username: 'admin', role: 'ADMIN' });
  render(<App />);
  expect(screen.getByRole('link', { name: /classes/i })).toBeInTheDocument();
});
