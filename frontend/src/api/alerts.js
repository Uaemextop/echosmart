import client from './client';

export const alertsAPI = {
  list: () => client.get('/api/v1/alerts'),
  createRule: (data) => client.post('/api/v1/alerts/rules', data),
  acknowledge: (id) => client.post(`/api/v1/alerts/${id}/acknowledge`),
};
