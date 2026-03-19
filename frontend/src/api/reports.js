import client from './client';

export const reportsAPI = {
  list: () => client.get('/api/v1/reports'),
  generate: (data) => client.post('/api/v1/reports/generate', data),
  download: (id) => client.get(`/api/v1/reports/${id}/download`, { responseType: 'blob' }),
};
