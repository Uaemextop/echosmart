import { describe, it, expect } from 'vitest';
import sensorsReducer, {
  setSelectedSensor,
  setFilters,
  clearFilters,
  fetchSensors,
} from '../../src/store/sensorsSlice';

const initialState = {
  items: [],
  selectedSensor: null,
  loading: false,
  error: null,
  filters: { gatewayId: null, type: null, search: '' },
};

describe('sensorsSlice', () => {
  it('should return the initial state', () => {
    const state = sensorsReducer(undefined, { type: 'unknown' });
    expect(state.items).toEqual([]);
    expect(state.selectedSensor).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.filters).toEqual({ gatewayId: null, type: null, search: '' });
  });

  it('should handle setSelectedSensor', () => {
    const sensor = { id: '1', name: 'Sensor A', type: 'temperature' };
    const state = sensorsReducer(initialState, setSelectedSensor(sensor));
    expect(state.selectedSensor).toEqual(sensor);
  });

  it('should handle setFilters', () => {
    const state = sensorsReducer(
      initialState,
      setFilters({ type: 'humidity', search: 'building' })
    );
    expect(state.filters.type).toBe('humidity');
    expect(state.filters.search).toBe('building');
    expect(state.filters.gatewayId).toBeNull();
  });

  it('should handle clearFilters', () => {
    const filteredState = {
      ...initialState,
      filters: { gatewayId: 'gw1', type: 'temperature', search: 'test' },
    };
    const state = sensorsReducer(filteredState, clearFilters());
    expect(state.filters).toEqual({ gatewayId: null, type: null, search: '' });
  });

  it('should handle fetchSensors.pending', () => {
    const action = { type: fetchSensors.pending.type };
    const state = sensorsReducer(initialState, action);
    expect(state.loading).toBe(true);
    expect(state.error).toBeNull();
  });

  it('should handle fetchSensors.fulfilled', () => {
    const sensors = [
      { id: '1', name: 'Sensor A', type: 'temperature', status: 'online' },
      { id: '2', name: 'Sensor B', type: 'humidity', status: 'offline' },
    ];
    const action = { type: fetchSensors.fulfilled.type, payload: sensors };
    const state = sensorsReducer(initialState, action);
    expect(state.loading).toBe(false);
    expect(state.items).toEqual(sensors);
  });

  it('should handle fetchSensors.rejected', () => {
    const action = {
      type: fetchSensors.rejected.type,
      payload: 'Network error',
    };
    const state = sensorsReducer(initialState, action);
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Network error');
  });
});
