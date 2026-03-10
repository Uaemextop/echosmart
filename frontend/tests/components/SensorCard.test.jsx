import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SensorCard from '../../src/components/Dashboard/SensorCard';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        'sensors.last_reading': 'Last Reading',
      };
      return translations[key] || key;
    },
  }),
}));

const mockSensor = {
  id: '1',
  name: 'Temperature Sensor A',
  type: 'temperature',
  location: 'Building 1, Floor 2',
  unit: '°C',
  status: 'online',
  last_reading: 23.5,
  last_reading_at: new Date().toISOString(),
};

describe('SensorCard', () => {
  it('renders sensor name', () => {
    render(<SensorCard sensor={mockSensor} onSelect={() => {}} />);
    expect(screen.getByText('Temperature Sensor A')).toBeInTheDocument();
  });

  it('displays last reading value with unit', () => {
    render(<SensorCard sensor={mockSensor} onSelect={() => {}} />);
    expect(screen.getByText('23.5 °C')).toBeInTheDocument();
  });

  it('shows online status indicator', () => {
    render(<SensorCard sensor={mockSensor} onSelect={() => {}} />);
    expect(screen.getByText('Online')).toBeInTheDocument();
  });

  it('shows offline status indicator', () => {
    const offlineSensor = { ...mockSensor, status: 'offline' };
    render(<SensorCard sensor={offlineSensor} onSelect={() => {}} />);
    expect(screen.getByText('Offline')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', () => {
    const onSelect = vi.fn();
    render(<SensorCard sensor={mockSensor} onSelect={onSelect} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onSelect).toHaveBeenCalledWith(mockSensor);
  });

  it('displays sensor location', () => {
    render(<SensorCard sensor={mockSensor} onSelect={() => {}} />);
    expect(screen.getByText('Building 1, Floor 2')).toBeInTheDocument();
  });
});
