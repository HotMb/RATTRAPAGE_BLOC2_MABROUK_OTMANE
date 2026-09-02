const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

function getTokens() {
  const raw = localStorage.getItem('auth_tokens');
  return raw ? JSON.parse(raw) : null;
}

export function setTokens(tokens) {
  if (tokens) {
    localStorage.setItem('auth_tokens', JSON.stringify(tokens));
  } else {
    localStorage.removeItem('auth_tokens');
  }
}

export async function apiRequest(path, { method = 'GET', body } = {}) {
  const tokens = getTokens();
  const headers = { 'Content-Type': 'application/json' };
  if (tokens && tokens.access) {
    headers['Authorization'] = `Bearer ${tokens.access}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw { status: response.status, data };
  }

  return data;
}

export function extractErrorMessage(data) {
  if (!data) return 'Une erreur est survenue.';
  if (data.detail) return data.detail;
  return Object.entries(data)
    .map(([field, messages]) => `${field} : ${Array.isArray(messages) ? messages.join(' ') : messages}`)
    .join(' ');
}
