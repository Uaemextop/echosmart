import client from './client';

export const sensorsAPI = {
  list: () => client.get('/api/v1/sensors'),
  get: (id) => client.get(`/api/v1/sensors/${id}`),
  create: (data) => client.post('/api/v1/sensors', data),
  update: (id, data) => client.put(`/api/v1/sensors/${id}`, data),
  delete: (id) => client.delete(`/api/v1/sensors/${id}`),
  getReadings: (id, params) => client.get(`/api/v1/sensors/${id}/readings`, { params }),
};
