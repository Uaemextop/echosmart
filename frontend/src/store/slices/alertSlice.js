import { createSlice } from '@reduxjs/toolkit';

const alertSlice = createSlice({
  name: 'alerts',
  initialState: {
    active: [],
    history: [],
    loading: false,
    error: null,
  },
  reducers: {
    alertsLoading: (state) => {
      state.loading = true;
      state.error = null;
    },
    alertsLoaded: (state, action) => {
      state.loading = false;
      state.active = action.payload.filter((a) => a.is_active);
      state.history = action.payload.filter((a) => !a.is_active);
    },
    alertAcknowledged: (state, action) => {
      const alert = state.active.find((a) => a.id === action.payload);
      if (alert) {
        alert.acknowledged = true;
      }
    },
    alertsError: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const { alertsLoading, alertsLoaded, alertAcknowledged, alertsError } = alertSlice.actions;
export default alertSlice.reducer;
