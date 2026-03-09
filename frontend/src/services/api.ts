import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const CSRF_COOKIE = 'csrfToken';
const CSRF_HEADER = 'x-csrf-token';
const SAFE_METHODS = new Set(['get', 'head', 'options']);

function getCsrfToken(): string {
  const match = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${CSRF_COOKIE}=`));
  return match ? decodeURIComponent(match.split('=')[1]) : '';
}

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: Array<{ resolve: (value: unknown) => void; reject: (reason: unknown) => void }> = [];

function processQueue(error: unknown) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(null);
  });
  failedQueue = [];
}

// Attach CSRF token to all state-mutating requests
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const method = (config.method ?? 'get').toLowerCase();
  if (!SAFE_METHODS.has(method)) {
    const token = getCsrfToken();
    if (token) {
      config.headers = config.headers ?? {};
      config.headers[CSRF_HEADER] = token;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => api(originalRequest)).catch((err) => Promise.reject(err));
      }
      originalRequest._retry = true;
      isRefreshing = true;
      try {
        await api.post('/auth/refresh');
        processQueue(null);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (email: string, password: string) => {
    const { data } = await api.post('/auth/login', { email, password });
    return data;
  },
  logout: async () => {
    const { data } = await api.post('/auth/logout');
    return data;
  },
  refreshToken: async () => {
    const { data } = await api.post('/auth/refresh');
    return data;
  },
  forgotPassword: async (email: string) => {
    const { data } = await api.post('/auth/forgot-password', { email });
    return data;
  },
  resetPassword: async (token: string, password: string) => {
    const { data } = await api.post('/auth/reset-password', { token, password });
    return data;
  },
  me: async () => {
    const { data } = await api.get('/auth/me');
    return data;
  },
};

export const tenantApi = {
  list: async (page = 1, filter: Record<string, string> = {}) => {
    const { data } = await api.get('/tenants', { params: { page, ...filter } });
    return data;
  },
  getById: async (id: string) => {
    const { data } = await api.get(`/tenants/${id}`);
    return data;
  },
  create: async (payload: Record<string, unknown>) => {
    const { data } = await api.post('/tenants', payload);
    return data;
  },
  update: async (id: string, payload: Record<string, unknown>) => {
    const { data } = await api.put(`/tenants/${id}`, payload);
    return data;
  },
  remove: async (id: string) => {
    const { data } = await api.delete(`/tenants/${id}`);
    return data;
  },
  getHealth: async (id: string) => {
    const { data } = await api.get(`/tenants/${id}/health`);
    return data;
  },
};

export const sensorApi = {
  list: async () => {
    const { data } = await api.get('/sensors');
    return data;
  },
  getById: async (id: string) => {
    const { data } = await api.get(`/sensors/${id}`);
    return data;
  },
  getData: async (id: string, params: Record<string, string> = {}) => {
    const { data } = await api.get(`/sensors/${id}/data`, { params });
    return data;
  },
  updateConfig: async (id: string, config: Record<string, unknown>) => {
    const { data } = await api.put(`/sensors/${id}/config`, config);
    return data;
  },
};

export const alertApi = {
  list: async () => {
    const { data } = await api.get('/alerts');
    return data;
  },
  create: async (payload: Record<string, unknown>) => {
    const { data } = await api.post('/alerts', payload);
    return data;
  },
  update: async (id: string, payload: Record<string, unknown>) => {
    const { data } = await api.put(`/alerts/${id}`, payload);
    return data;
  },
  remove: async (id: string) => {
    const { data } = await api.delete(`/alerts/${id}`);
    return data;
  },
};

export default api;
