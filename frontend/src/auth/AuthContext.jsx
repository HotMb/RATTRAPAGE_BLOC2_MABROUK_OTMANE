import { createContext, useContext, useState, useCallback } from 'react';
import { apiRequest, setTokens } from '../api/client';

const AuthContext = createContext(null);

function readStoredUser() {
  const raw = localStorage.getItem('auth_user');
  return raw ? JSON.parse(raw) : null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser());

  const login = useCallback(async (username, password) => {
    const data = await apiRequest('/auth/login/', { method: 'POST', body: { username, password } });
    setTokens({ access: data.access, refresh: data.refresh });
    const nextUser = { username: data.username, role: data.role };
    localStorage.setItem('auth_user', JSON.stringify(nextUser));
    setUser(nextUser);
    return nextUser;
  }, []);

  const logout = useCallback(() => {
    setTokens(null);
    localStorage.removeItem('auth_user');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
