import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import AlertCenter from '../../src/components/Alerts/AlertCenter';
import alertsReducer from '../../src/store/alertsSlice';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        'alerts.title': 'Alerts',
        'alerts.critical': 'Critical',
        'alerts.high': 'High',
        'alerts.medium': 'Medium',
        'alerts.low': 'Low',
        'alerts.acknowledge': 'Acknowledge',
        'alerts.no_alerts': 'No active alerts',
        'common.filter': 'Filter',
      };
      return translations[key] || key;
    },
  }),
}));

const mockGetAlerts = vi.fn().mockResolvedValue({ data: [] });

vi.mock('../../src/api/endpoints', () => ({
  getAlerts: (...args) => mockGetAlerts(...args),
  acknowledgeAlertApi: vi.fn(),
  getAlertRules: vi.fn(),
  createAlertRuleApi: vi.fn(),
}));

const createStore = (alerts = []) =>
  configureStore({
    reducer: { alerts: alertsReducer },
    preloadedState: {
      alerts: {
        items: alerts,
        rules: [],
        loading: false,
        error: null,
      },
    },
  });

const renderAlertCenter = (alerts = []) => {
  mockGetAlerts.mockResolvedValue({ data: alerts });
  const store = createStore(alerts);
  return render(
    <Provider store={store}>
      <AlertCenter />
    </Provider>
  );
};

describe('AlertCenter', () => {
  it('renders alert title', async () => {
    renderAlertCenter();
    expect(await screen.findByText('Alerts')).toBeInTheDocument();
  });

  it('shows no alerts message when empty', async () => {
    renderAlertCenter();
    expect(await screen.findByText('No active alerts')).toBeInTheDocument();
  });

  it('renders alert list', async () => {
    const alerts = [
      { id: '1', severity: 'critical', message: 'Temperature too high', is_acknowledged: false, created_at: new Date().toISOString() },
      { id: '2', severity: 'low', message: 'Humidity warning', is_acknowledged: false, created_at: new Date().toISOString() },
    ];
    renderAlertCenter(alerts);
    expect(await screen.findByText('Temperature too high')).toBeInTheDocument();
    expect(screen.getByText('Humidity warning')).toBeInTheDocument();
  });

  it('shows severity badges', async () => {
    const alerts = [
      { id: '1', severity: 'critical', message: 'Alert 1', is_acknowledged: false, created_at: new Date().toISOString() },
    ];
    renderAlertCenter(alerts);
    const badge = await screen.findByText('Critical', { selector: '.badge' });
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('badge-critical');
  });

  it('shows acknowledge button for unacknowledged alerts', async () => {
    const alerts = [
      { id: '1', severity: 'high', message: 'Alert 1', is_acknowledged: false, created_at: new Date().toISOString() },
    ];
    renderAlertCenter(alerts);
    expect(await screen.findByText('Acknowledge')).toBeInTheDocument();
  });
});
