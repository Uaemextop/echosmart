import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  theme: 'light',
  sidebarOpen: true,
  notifications: [],
  nextNotificationId: 1,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleTheme(state) {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
    toggleSidebar(state) {
      state.sidebarOpen = !state.sidebarOpen;
    },
    addNotification(state, action) {
      state.notifications.push({
        id: state.nextNotificationId,
        ...action.payload,
      });
      state.nextNotificationId += 1;
    },
    removeNotification(state, action) {
      state.notifications = state.notifications.filter(
        (n) => n.id !== action.payload
      );
    },
  },
});

export const { toggleTheme, toggleSidebar, addNotification, removeNotification } =
  uiSlice.actions;
export default uiSlice.reducer;
