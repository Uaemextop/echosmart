# EchoSmart — Frontend Web (React)

Dashboard web para la plataforma IoT EchoSmart.

## Stack

- **Framework**: React 18+ con Vite
- **State Management**: Redux Toolkit + RTK Query
- **Routing**: React Router 6+
- **Charts**: Recharts 2.10+
- **UI**: Tailwind CSS 3+ / Material-UI 5+
- **i18n**: react-i18next
- **Testing**: Vitest + React Testing Library

## Inicio Rápido

```bash
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:5173`.

## Scripts

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Build para producción |
| `npm run preview` | Preview del build |
| `npm test` | Ejecutar tests |
| `npm run lint` | Ejecutar ESLint |

## Estructura

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── main.jsx            # Punto de entrada
│   ├── App.jsx             # Componente raíz
│   ├── api/                # Clientes HTTP
│   ├── components/         # Componentes por feature
│   ├── hooks/              # Custom hooks
│   ├── pages/              # Páginas/vistas
│   ├── store/              # Redux Toolkit
│   ├── i18n/               # Internacionalización
│   ├── theme/              # Theming dinámico
│   └── utils/              # Utilidades
├── tests/                  # Tests
├── package.json
├── vite.config.js
└── .env.example
```
