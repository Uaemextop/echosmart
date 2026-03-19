# EchoSmart — Desktop App (Electron)

Aplicación de escritorio multiplataforma para Windows, macOS y Linux.

## Stack

- **Framework**: Electron 28+
- **Renderer**: Frontend React (compartido con web)
- **Build**: electron-builder
- **Auto-update**: electron-updater
- **Storage**: electron-store

## Inicio Rápido

```bash
npm install
npm run dev
```

## Builds

```bash
# Windows (.exe / .msi)
npm run build:win

# macOS (.dmg / .app)
npm run build:mac

# Linux (.AppImage / .deb)
npm run build:linux

# Todos
npm run build:all
```

## Estructura

```
desktop/
├── src/
│   ├── main/              # Electron main process
│   │   └── main.js        # Entry point, window management
│   ├── preload/           # Preload scripts (secure IPC)
│   │   └── preload.js     # Context bridge API
│   └── renderer/          # React app (symlink/copy from frontend)
├── resources/
│   ├── icons/             # Platform-specific icons
│   │   ├── win/           # .ico files
│   │   ├── mac/           # .icns files
│   │   └── linux/         # .png files
│   └── tray/              # System tray icons
├── package.json
├── electron-builder.yml
└── README.md
```

## Plataformas

| Plataforma | Formato | Firma |
|------------|---------|-------|
| **Windows** | `.exe` (NSIS), `.msi` | Code signing certificate |
| **macOS** | `.dmg`, `.app` | Apple Developer ID + notarización |
| **Linux** | `.AppImage`, `.deb`, `.snap` | N/A |
