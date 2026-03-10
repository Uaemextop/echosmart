import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import sensorsReducer from './sensorsSlice';
import readingsReducer from './readingsSlice';
import alertsReducer from './alertsSlice';
import reportsReducer from './reportsSlice';
import uiReducer from './uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    sensors: sensorsReducer,
    readings: readingsReducer,
    alerts: alertsReducer,
    reports: reportsReducer,
    ui: uiReducer,
  },
});
