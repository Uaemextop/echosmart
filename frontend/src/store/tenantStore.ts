import { create } from 'zustand';
import type { Tenant } from '../types';

interface TenantStore {
  tenants: Tenant[];
  currentTenant: Tenant | null;
  isLoading: boolean;
  total: number;
  page: number;
  fetchTenants: (page?: number, filter?: Record<string, string>) => Promise<void>;
  fetchTenantById: (id: string) => Promise<void>;
  createTenant: (data: Record<string, unknown>) => Promise<void>;
  updateTenant: (id: string, data: Record<string, unknown>) => Promise<void>;
  deleteTenant: (id: string) => Promise<void>;
  setCurrentTenant: (tenant: Tenant | null) => void;
}

export const useTenantStore = create<TenantStore>((set) => ({
  tenants: [],
  currentTenant: null,
  isLoading: false,
  total: 0,
  page: 1,

  setCurrentTenant: (tenant) => set({ currentTenant: tenant }),

  fetchTenants: async (page = 1, filter = {}) => {
    set({ isLoading: true });
    try {
      const { tenantApi } = await import('../services/api');
      const data = await tenantApi.list(page, filter);
      set({ tenants: data.tenants, total: data.total, page, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  fetchTenantById: async (id) => {
    set({ isLoading: true });
    try {
      const { tenantApi } = await import('../services/api');
      const tenant = await tenantApi.getById(id);
      set({ currentTenant: tenant, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  createTenant: async (data) => {
    const { tenantApi } = await import('../services/api');
    await tenantApi.create(data);
  },

  updateTenant: async (id, data) => {
    const { tenantApi } = await import('../services/api');
    await tenantApi.update(id, data);
  },

  deleteTenant: async (id) => {
    const { tenantApi } = await import('../services/api');
    await tenantApi.remove(id);
    set((state) => ({ tenants: state.tenants.filter((t) => t.id !== id) }));
  },
}));
