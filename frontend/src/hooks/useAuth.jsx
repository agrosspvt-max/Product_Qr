import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('pqr_user') || 'null'); }
    catch { return null; }
  });
  const [token, setToken] = useState(() => localStorage.getItem('pqr_token'));

  // Validate token on mount
  useEffect(() => {
    if (!token) return;
    api.get('/auth/me').then((r) => setUser(r.data)).catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password });
    localStorage.setItem('pqr_token', data.access_token);
    localStorage.setItem('pqr_user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    localStorage.removeItem('pqr_token');
    localStorage.removeItem('pqr_user');
    setUser(null);
    setToken(null);
  }

  const value = useMemo(() => ({ user, token, login, logout, isAuthed: !!token }), [user, token]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
