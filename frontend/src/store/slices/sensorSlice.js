import { createSlice } from '@reduxjs/toolkit';

const sensorSlice = createSlice({
  name: 'sensors',
  initialState: {
    byId: {},
    allIds: [],
    loading: false,
    error: null,
  },
  reducers: {
    sensorsLoading: (state) => {
      state.loading = true;
      state.error = null;
    },
    sensorsLoaded: (state, action) => {
      state.loading = false;
      action.payload.forEach((sensor) => {
        state.byId[sensor.id] = sensor;
        if (!state.allIds.includes(sensor.id)) {
          state.allIds.push(sensor.id);
        }
      });
    },
    sensorUpdated: (state, action) => {
      const { id, ...updates } = action.payload;
      state.byId[id] = { ...state.byId[id], ...updates };
    },
    sensorDeleted: (state, action) => {
      delete state.byId[action.payload];
      state.allIds = state.allIds.filter((id) => id !== action.payload);
    },
    sensorsError: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const { sensorsLoading, sensorsLoaded, sensorUpdated, sensorDeleted, sensorsError } =
  sensorSlice.actions;
export default sensorSlice.reducer;
