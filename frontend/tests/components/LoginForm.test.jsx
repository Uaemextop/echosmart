import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import LoginForm from '../../src/components/Auth/LoginForm';
import authReducer from '../../src/store/authSlice';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        'app.title': 'EchoSmart',
        'app.subtitle': 'Smart Environmental Monitoring',
        'auth.login': 'Login',
        'auth.email': 'Email',
        'auth.password': 'Password',
        'auth.forgot_password': 'Forgot your password?',
        'common.loading': 'Loading...',
      };
      return translations[key] || key;
    },
  }),
}));

vi.mock('../../src/api/endpoints', () => ({
  login: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
}));

const createTestStore = () =>
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
      },
    },
  });

const renderLoginForm = () => {
  const store = createTestStore();
  return render(
    <Provider store={store}>
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    </Provider>
  );
};

describe('LoginForm', () => {
  it('renders email input', () => {
    renderLoginForm();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  it('renders password input', () => {
    renderLoginForm();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('renders submit button', () => {
    renderLoginForm();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
  });

  it('shows validation for empty email on submit', async () => {
    renderLoginForm();
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));
    expect(await screen.findByText('Email is required')).toBeInTheDocument();
  });

  it('shows validation for empty password on submit', async () => {
    renderLoginForm();
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));
    expect(await screen.findByText('Password is required')).toBeInTheDocument();
  });

  it('renders app title', () => {
    renderLoginForm();
    expect(screen.getByText('EchoSmart')).toBeInTheDocument();
  });
});
