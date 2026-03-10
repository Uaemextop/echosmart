import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getReadings } from '../api/endpoints';

export const fetchReadings = createAsyncThunk(
  'readings/fetchReadings',
  async ({ sensorId, from, to }, { rejectWithValue }) => {
    try {
      const response = await getReadings(sensorId, { from, to });
      return { sensorId, data: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch readings');
    }
  }
);

const initialState = {
  data: {},
  loading: false,
  error: null,
};

const readingsSlice = createSlice({
  name: 'readings',
  initialState,
  reducers: {
    addReading(state, action) {
      const { sensor_id, timestamp, value } = action.payload;
      if (!state.data[sensor_id]) {
        state.data[sensor_id] = [];
      }
      state.data[sensor_id].push({ timestamp, value });
    },
    clearReadings(state, action) {
      if (action.payload) {
        delete state.data[action.payload];
      } else {
        state.data = {};
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchReadings.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchReadings.fulfilled, (state, action) => {
        state.loading = false;
        state.data[action.payload.sensorId] = action.payload.data;
      })
      .addCase(fetchReadings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { addReading, clearReadings } = readingsSlice.actions;
export default readingsSlice.reducer;
