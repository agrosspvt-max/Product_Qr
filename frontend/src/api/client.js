import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL,
  timeout: 60_000,
});

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pqr_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-handle 401 — clear token & redirect to /login
api.interceptors.response.use(
  (resp) => resp,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem('pqr_token');
      localStorage.removeItem('pqr_user');
      if (window.location.pathname !== '/login') {
        window.location.replace('/login');
      }
    }
    return Promise.reject(err);
  }
);

export const API_BASE = baseURL;
