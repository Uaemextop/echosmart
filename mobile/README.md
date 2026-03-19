# EchoSmart — App Móvil (React Native + Expo)

Aplicación móvil multiplataforma para iOS y Android.

## Stack

- **Framework**: React Native con Expo
- **Navegación**: React Navigation 6+
- **State**: Redux Toolkit / Zustand
- **Notificaciones**: Firebase Cloud Messaging (FCM)
- **Offline**: AsyncStorage + SQLite
- **Build**: EAS Build

## Inicio Rápido

```bash
npm install
npx expo start
```

## Builds

```bash
# Android
eas build --platform android

# iOS
eas build --platform ios

# Ambos
eas build --platform all
```

## Estructura

```
mobile/
├── App.js                     # Punto de entrada
├── app.json                   # Configuración Expo
├── package.json
├── eas.json                   # Configuración EAS Build
├── src/
│   ├── screens/               # Pantallas por feature
│   │   ├── Dashboard/
│   │   ├── Sensors/
│   │   ├── Alerts/
│   │   ├── Reports/
│   │   ├── Settings/
│   │   └── Auth/
│   ├── components/            # Componentes reutilizables
│   │   ├── common/
│   │   ├── charts/
│   │   ├── sensors/
│   │   └── alerts/
│   ├── navigation/            # Configuración de navegación
│   ├── services/              # Servicios API y notificaciones
│   ├── store/                 # State management
│   ├── hooks/                 # Custom hooks
│   ├── utils/                 # Utilidades
│   └── i18n/                  # Internacionalización
└── assets/                    # Recursos estáticos
    ├── images/
    ├── fonts/
    └── icons/
```

## Plataformas

| Plataforma | Directorio Nativo | Build |
|------------|-------------------|-------|
| **Android** | `android/` (generado por EAS) | `eas build --platform android` |
| **iOS** | `ios/` (generado por EAS) | `eas build --platform ios` |
