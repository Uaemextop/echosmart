import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import {
  getAlerts,
  acknowledgeAlertApi,
  getAlertRules,
  createAlertRuleApi,
} from '../api/endpoints';

export const fetchAlerts = createAsyncThunk(
  'alerts/fetchAlerts',
  async (params, { rejectWithValue }) => {
    try {
      const response = await getAlerts(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch alerts');
    }
  }
);

export const acknowledgeAlert = createAsyncThunk(
  'alerts/acknowledgeAlert',
  async (alertId, { rejectWithValue }) => {
    try {
      await acknowledgeAlertApi(alertId);
      return alertId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to acknowledge alert');
    }
  }
);

export const fetchAlertRules = createAsyncThunk(
  'alerts/fetchAlertRules',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getAlertRules();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch alert rules');
    }
  }
);

export const createAlertRule = createAsyncThunk(
  'alerts/createAlertRule',
  async (ruleData, { rejectWithValue }) => {
    try {
      const response = await createAlertRuleApi(ruleData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create alert rule');
    }
  }
);

const initialState = {
  items: [],
  rules: [],
  loading: false,
  error: null,
};

const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    addAlert(state, action) {
      state.items.unshift(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAlerts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(acknowledgeAlert.fulfilled, (state, action) => {
        const alert = state.items.find((a) => a.id === action.payload);
        if (alert) {
          alert.is_acknowledged = true;
        }
      })
      .addCase(fetchAlertRules.fulfilled, (state, action) => {
        state.rules = action.payload;
      })
      .addCase(createAlertRule.fulfilled, (state, action) => {
        state.rules.push(action.payload);
      });
  },
});

export const { addAlert } = alertsSlice.actions;
export default alertsSlice.reducer;
