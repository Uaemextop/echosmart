const { app, BrowserWindow, Tray, Menu, ipcMain, nativeTheme } = require('electron');
const path = require('path');
const Store = require('electron-store');

const store = new Store();
let mainWindow;
let tray;

const isDev = !app.isPackaged;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'EchoSmart',
    backgroundColor: '#0A1A0F',
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    icon: path.join(__dirname, '..', '..', 'resources', 'icons', 'linux', 'icon-256.png'),
  });

  // Force dark theme
  nativeTheme.themeSource = 'dark';

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  }

  mainWindow.on('close', (event) => {
    if (store.get('minimizeToTray', true)) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
}

function createTray() {
  const trayIconPath = path.join(__dirname, '..', '..', 'resources', 'tray', 'tray-icon.png');
  tray = new Tray(trayIconPath);

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Abrir EchoSmart', click: () => mainWindow.show() },
    { type: 'separator' },
    {
      label: 'Sensores',
      submenu: [
        { label: 'Dashboard', click: () => { mainWindow.show(); mainWindow.webContents.send('navigate', '/'); } },
        { label: 'Alertas', click: () => { mainWindow.show(); mainWindow.webContents.send('navigate', '/alerts'); } },
      ],
    },
    { type: 'separator' },
    { label: 'Configuración', click: () => { mainWindow.show(); mainWindow.webContents.send('navigate', '/settings'); } },
    { type: 'separator' },
    { label: 'Salir', click: () => { app.quit(); } },
  ]);

  tray.setToolTip('EchoSmart — Monitoreo de Invernaderos');
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => mainWindow.show());
}

// IPC Handlers
ipcMain.handle('get-store', (event, key) => store.get(key));
ipcMain.handle('set-store', (event, key, value) => store.set(key, value));
ipcMain.handle('get-app-version', () => app.getVersion());

app.whenReady().then(() => {
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
