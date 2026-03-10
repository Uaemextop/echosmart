import { describe, it, expect } from 'vitest';
import authReducer, {
  setCredentials,
  clearCredentials,
  setLoading,
  setError,
} from '../../src/store/authSlice';

const initialState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  loading: false,
  error: null,
};

describe('authSlice', () => {
  it('should return the initial state', () => {
    const state = authReducer(undefined, { type: 'unknown' });
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should handle setCredentials', () => {
    const payload = {
      user: { id: '1', email: 'test@example.com', full_name: 'Test User', role: 'admin' },
      token: 'access-token-123',
      refreshToken: 'refresh-token-456',
    };
    const state = authReducer(initialState, setCredentials(payload));
    expect(state.user).toEqual(payload.user);
    expect(state.token).toBe('access-token-123');
    expect(state.refreshToken).toBe('refresh-token-456');
    expect(state.isAuthenticated).toBe(true);
    expect(state.error).toBeNull();
  });

  it('should handle clearCredentials', () => {
    const authenticatedState = {
      user: { id: '1', email: 'test@example.com' },
      token: 'some-token',
      refreshToken: 'some-refresh',
      isAuthenticated: true,
      loading: false,
      error: null,
    };
    const state = authReducer(authenticatedState, clearCredentials());
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.refreshToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should handle setLoading', () => {
    const state = authReducer(initialState, setLoading(true));
    expect(state.loading).toBe(true);
  });

  it('should handle setError', () => {
    const state = authReducer(initialState, setError('Something went wrong'));
    expect(state.error).toBe('Something went wrong');
  });
});
