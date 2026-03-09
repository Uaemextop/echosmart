import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types';

interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, _get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const { authApi } = await import('../services/api');
          const data = await authApi.login(email, password);
          set({ user: data.user, isAuthenticated: true, isLoading: false });
        } catch (err) {
          set({ isLoading: false });
          throw err;
        }
      },

      logout: async () => {
        try {
          const { authApi } = await import('../services/api');
          await authApi.logout();
        } catch {
          // ignore logout errors
        }
        set({ user: null, isAuthenticated: false });
      },

      refreshToken: async () => {
        const { authApi } = await import('../services/api');
        await authApi.refreshToken();
      },
    }),
    {
      name: 'echosmart-auth',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
