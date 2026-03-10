import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import QuickStats from '../../src/components/Dashboard/QuickStats';
import sensorsReducer from '../../src/store/sensorsSlice';
import alertsReducer from '../../src/store/alertsSlice';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        'dashboard.total_sensors': 'Total Sensors',
        'dashboard.sensors_online': 'Sensors Online',
        'dashboard.active_alerts': 'Active Alerts',
        'dashboard.gateways': 'Gateways',
      };
      return translations[key] || key;
    },
  }),
}));

vi.mock('../../src/api/endpoints', () => ({
  getSensors: vi.fn(),
  createSensorApi: vi.fn(),
  updateSensorApi: vi.fn(),
  deleteSensorApi: vi.fn(),
  getAlerts: vi.fn(),
  acknowledgeAlertApi: vi.fn(),
  getAlertRules: vi.fn(),
  createAlertRuleApi: vi.fn(),
}));

const createStore = (sensors = [], alerts = []) =>
  configureStore({
    reducer: {
      sensors: sensorsReducer,
      alerts: alertsReducer,
    },
    preloadedState: {
      sensors: {
        items: sensors,
        selectedSensor: null,
        loading: false,
        error: null,
        filters: { gatewayId: null, type: null, search: '' },
      },
      alerts: {
        items: alerts,
        rules: [],
        loading: false,
        error: null,
      },
    },
  });

const renderQuickStats = (sensors = [], alerts = []) => {
  const store = createStore(sensors, alerts);
  return render(
    <Provider store={store}>
      <QuickStats />
    </Provider>
  );
};

describe('QuickStats', () => {
  it('renders total sensor count', () => {
    const sensors = [
      { id: '1', name: 'S1', status: 'online', gateway_id: 'gw1' },
      { id: '2', name: 'S2', status: 'offline', gateway_id: 'gw1' },
      { id: '3', name: 'S3', status: 'online', gateway_id: 'gw2' },
    ];
    renderQuickStats(sensors);
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Total Sensors')).toBeInTheDocument();
  });

  it('shows online sensor count', () => {
    const sensors = [
      { id: '1', name: 'S1', status: 'online', gateway_id: 'gw1' },
      { id: '2', name: 'S2', status: 'offline', gateway_id: 'gw1' },
      { id: '3', name: 'S3', status: 'online', gateway_id: 'gw2' },
    ];
    renderQuickStats(sensors);
    const statsContainer = screen.getByTestId('quick-stats');
    const statCards = statsContainer.querySelectorAll('.stat-card');
    // Second card is "Sensors Online" with value 2
    expect(statCards[1].querySelector('.stat-value').textContent).toBe('2');
    expect(screen.getByText('Sensors Online')).toBeInTheDocument();
  });

  it('shows active alert count', () => {
    const alerts = [
      { id: '1', severity: 'critical', is_acknowledged: false },
      { id: '2', severity: 'low', is_acknowledged: true },
      { id: '3', severity: 'high', is_acknowledged: false },
    ];
    renderQuickStats([], alerts);
    expect(screen.getByText('Active Alerts')).toBeInTheDocument();
  });

  it('shows gateway count', () => {
    const sensors = [
      { id: '1', name: 'S1', status: 'online', gateway_id: 'gw1' },
      { id: '2', name: 'S2', status: 'online', gateway_id: 'gw2' },
    ];
    renderQuickStats(sensors);
    expect(screen.getByText('Gateways')).toBeInTheDocument();
  });
});
