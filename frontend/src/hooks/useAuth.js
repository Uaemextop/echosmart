import { useSelector, useDispatch } from 'react-redux';
import { loginStart, loginSuccess, loginFailure, logout } from '../store/slices/authSlice';
import { authAPI } from '../api/auth';

/**
 * Hook para gestión de autenticación.
 */
export function useAuth() {
  const dispatch = useDispatch();
  const { user, isAuthenticated, loading, error } = useSelector((state) => state.auth);

  const login = async (email, password) => {
    dispatch(loginStart());
    try {
      const response = await authAPI.login(email, password);
      const { access_token, refresh_token, user } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      dispatch(loginSuccess({ user, token: access_token }));
    } catch (err) {
      dispatch(loginFailure(err.response?.data?.detail || 'Error de autenticación'));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    dispatch(logout());
  };

  return { user, isAuthenticated, loading, error, login, logout: handleLogout };
}
