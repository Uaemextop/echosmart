const { contextBridge, ipcRenderer } = require('electron');

/**
 * Expose safe APIs to renderer process via context bridge.
 */
contextBridge.exposeInMainWorld('electronAPI', {
  // Storage
  getStore: (key) => ipcRenderer.invoke('get-store', key),
  setStore: (key, value) => ipcRenderer.invoke('set-store', key, value),

  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // Navigation from main process
  onNavigate: (callback) => ipcRenderer.on('navigate', (event, path) => callback(path)),

  // Notifications
  showNotification: (title, body) => {
    new Notification(title, { body, icon: '../resources/icons/linux/icon-256.png' });
  },

  // Platform info
  platform: process.platform,
});
