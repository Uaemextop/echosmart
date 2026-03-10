import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { useAuth } from '../../src/hooks/useAuth';
import authReducer from '../../src/store/authSlice';

vi.mock('../../src/api/endpoints', () => ({
  login: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
}));

const createTestStore = (preloadedState) =>
  configureStore({
    reducer: { auth: authReducer },
    preloadedState: {
      auth: {
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: false,
        error: null,
        ...preloadedState,
      },
    },
  });

const wrapper = (store) => {
  return function Wrapper({ children }) {
    return <Provider store={store}>{children}</Provider>;
  };
};

describe('useAuth', () => {
  it('returns isAuthenticated as false by default', () => {
    const store = createTestStore();
    const { result } = renderHook(() => useAuth(), {
      wrapper: wrapper(store),
    });
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('returns user as null by default', () => {
    const store = createTestStore();
    const { result } = renderHook(() => useAuth(), {
      wrapper: wrapper(store),
    });
    expect(result.current.user).toBeNull();
  });

  it('returns user when authenticated', () => {
    const user = { id: '1', email: 'test@example.com', full_name: 'Test User', role: 'admin' };
    const store = createTestStore({ user, isAuthenticated: true, token: 'token123' });
    const { result } = renderHook(() => useAuth(), {
      wrapper: wrapper(store),
    });
    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('provides login function', () => {
    const store = createTestStore();
    const { result } = renderHook(() => useAuth(), {
      wrapper: wrapper(store),
    });
    expect(typeof result.current.login).toBe('function');
  });

  it('provides logout function', () => {
    const store = createTestStore();
    const { result } = renderHook(() => useAuth(), {
      wrapper: wrapper(store),
    });
    expect(typeof result.current.logout).toBe('function');
  });
});
