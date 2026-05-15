import { api } from '../api/client';

/* ---------------- Products ---------------- */
export const ProductsAPI = {
  list:   (onlyActive = false) => api.get('/products', { params: { only_active: onlyActive } }).then(r => r.data),
  create: (payload) => api.post('/products', payload).then(r => r.data),
  update: (id, payload) => api.put(`/products/${id}`, payload).then(r => r.data),
  remove: (id) => api.delete(`/products/${id}`).then(r => r.data),
};

/* --------------- Quantities --------------- */
export const QuantitiesAPI = {
  list:   (onlyActive = false) => api.get('/quantities', { params: { only_active: onlyActive } }).then(r => r.data),
  create: (payload) => api.post('/quantities', payload).then(r => r.data),
  update: (id, payload) => api.put(`/quantities/${id}`, payload).then(r => r.data),
  remove: (id) => api.delete(`/quantities/${id}`).then(r => r.data),
};

/* ----------- WhatsApp Presets ------------ */
export const PresetsAPI = {
  list:   (onlyActive = false) => api.get('/whatsapp-presets', { params: { only_active: onlyActive } }).then(r => r.data),
  create: (payload) => api.post('/whatsapp-presets', payload).then(r => r.data),
  update: (id, payload) => api.put(`/whatsapp-presets/${id}`, payload).then(r => r.data),
  remove: (id) => api.delete(`/whatsapp-presets/${id}`).then(r => r.data),
};

/* ----------------- Settings --------------- */
export const SettingsAPI = {
  getZoho: () => api.get('/settings/zoho').then(r => r.data),
  saveZoho: (payload) => api.put('/settings/zoho', payload).then(r => r.data),
  getShortDomain: () => api.get('/settings/short-domain').then(r => r.data),
  saveShortDomain: (payload) => api.put('/settings/short-domain', payload).then(r => r.data),
};

/* ----------------- Batches ---------------- */
export const BatchesAPI = {
  list: () => api.get('/batches').then(r => r.data),
  get:  (id) => api.get(`/batch/${id}`).then(r => r.data),
  retryZoho: (id) => api.post(`/batch/${id}/retry-zoho`).then(r => r.data),
  downloadExcelUrl: (id) => `${api.defaults.baseURL}/download-excel/${id}`,
};

/* ----------------- Generate --------------- */
export const GenerateAPI = {
  run: (payload) => api.post('/generate-codes', payload).then(r => r.data),
};
