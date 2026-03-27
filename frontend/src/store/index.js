import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import sensorSlice from './slices/sensorSlice';
import alertSlice from './slices/alertSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    sensors: sensorSlice,
    alerts: alertSlice,
  },
});
