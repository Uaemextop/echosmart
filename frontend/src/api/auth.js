import client from './client';

export const authAPI = {
  login: (email, password) => client.post('/api/v1/auth/login', { email, password }),
  refresh: (refreshToken) => client.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
  logout: () => client.post('/api/v1/auth/logout'),
};
