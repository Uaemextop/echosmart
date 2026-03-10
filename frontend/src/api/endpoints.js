import apiClient from './client';

// Auth
export const login = (email, password) =>
  apiClient.post('/auth/login', { email, password });

export const logout = () => apiClient.post('/auth/logout');

export const refreshToken = (refresh_token) =>
  apiClient.post('/auth/refresh', { refresh_token });

// Sensors
export const getSensors = (params) => apiClient.get('/sensors', { params });

export const getSensor = (id) => apiClient.get(`/sensors/${id}`);

export const createSensorApi = (data) => apiClient.post('/sensors', data);

export const updateSensorApi = (id, data) =>
  apiClient.put(`/sensors/${id}`, data);

export const deleteSensorApi = (id) => apiClient.delete(`/sensors/${id}`);

// Readings
export const getReadings = (sensorId, params) =>
  apiClient.get(`/sensors/${sensorId}/readings`, { params });

// Alerts
export const getAlerts = (params) => apiClient.get('/alerts', { params });

export const acknowledgeAlertApi = (id) =>
  apiClient.patch(`/alerts/${id}/acknowledge`);

export const getAlertRules = () => apiClient.get('/alert-rules');

export const createAlertRuleApi = (data) =>
  apiClient.post('/alert-rules', data);

// Reports
export const getReports = () => apiClient.get('/reports');

export const generateReportApi = (data) => apiClient.post('/reports', data);

export const downloadReport = (id) =>
  apiClient.get(`/reports/${id}/download`, { responseType: 'blob' });

// Users (Admin)
export const getUsers = () => apiClient.get('/admin/users');

export const createUser = (data) => apiClient.post('/admin/users', data);

export const updateUser = (id, data) =>
  apiClient.put(`/admin/users/${id}`, data);

export const deleteUser = (id) => apiClient.delete(`/admin/users/${id}`);

// Gateways
export const getGateways = () => apiClient.get('/gateways');

export const createGateway = (data) => apiClient.post('/gateways', data);

export const updateGateway = (id, data) =>
  apiClient.put(`/gateways/${id}`, data);

export const deleteGateway = (id) => apiClient.delete(`/gateways/${id}`);
