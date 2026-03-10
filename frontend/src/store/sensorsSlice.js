import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import {
  getSensors,
  createSensorApi,
  updateSensorApi,
  deleteSensorApi,
} from '../api/endpoints';

export const fetchSensors = createAsyncThunk(
  'sensors/fetchSensors',
  async (params, { rejectWithValue }) => {
    try {
      const response = await getSensors(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch sensors');
    }
  }
);

export const createSensor = createAsyncThunk(
  'sensors/createSensor',
  async (sensorData, { rejectWithValue }) => {
    try {
      const response = await createSensorApi(sensorData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create sensor');
    }
  }
);

export const updateSensor = createAsyncThunk(
  'sensors/updateSensor',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await updateSensorApi(id, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update sensor');
    }
  }
);

export const deleteSensor = createAsyncThunk(
  'sensors/deleteSensor',
  async (id, { rejectWithValue }) => {
    try {
      await deleteSensorApi(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete sensor');
    }
  }
);

const initialState = {
  items: [],
  selectedSensor: null,
  loading: false,
  error: null,
  filters: { gatewayId: null, type: null, search: '' },
};

const sensorsSlice = createSlice({
  name: 'sensors',
  initialState,
  reducers: {
    setSelectedSensor(state, action) {
      state.selectedSensor = action.payload;
    },
    setFilters(state, action) {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters(state) {
      state.filters = { gatewayId: null, type: null, search: '' };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSensors.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSensors.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchSensors.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createSensor.fulfilled, (state, action) => {
        state.items.push(action.payload);
      })
      .addCase(updateSensor.fulfilled, (state, action) => {
        const index = state.items.findIndex((s) => s.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      })
      .addCase(deleteSensor.fulfilled, (state, action) => {
        state.items = state.items.filter((s) => s.id !== action.payload);
      });
  },
});

export const { setSelectedSensor, setFilters, clearFilters } =
  sensorsSlice.actions;
export default sensorsSlice.reducer;
