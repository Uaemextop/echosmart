import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getReports, generateReportApi } from '../api/endpoints';

export const fetchReports = createAsyncThunk(
  'reports/fetchReports',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getReports();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch reports');
    }
  }
);

export const generateReport = createAsyncThunk(
  'reports/generateReport',
  async (reportData, { rejectWithValue }) => {
    try {
      const response = await generateReportApi(reportData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to generate report');
    }
  }
);

const initialState = {
  items: [],
  generating: false,
  error: null,
};

const reportsSlice = createSlice({
  name: 'reports',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchReports.pending, (state) => {
        state.error = null;
      })
      .addCase(fetchReports.fulfilled, (state, action) => {
        state.items = action.payload;
      })
      .addCase(fetchReports.rejected, (state, action) => {
        state.error = action.payload;
      })
      .addCase(generateReport.pending, (state) => {
        state.generating = true;
        state.error = null;
      })
      .addCase(generateReport.fulfilled, (state, action) => {
        state.generating = false;
        state.items.unshift(action.payload);
      })
      .addCase(generateReport.rejected, (state, action) => {
        state.generating = false;
        state.error = action.payload;
      });
  },
});

export default reportsSlice.reducer;
