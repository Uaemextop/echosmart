# EchoSmart — Assets & Branding

Recursos visuales y guía de identidad de marca para la plataforma EchoSmart.

---

## 🎨 Paleta de Colores

### Colores Primarios (Dark Theme — Fondo Negro Puro)

| Color | Hex | Uso |
|-------|-----|-----|
| **Background** | `#000000` | Fondo principal de todas las apps (negro puro) |
| **Surface** | `#111111` | Cards, paneles, modales |
| **Surface Elevated** | `#1A1A1A` | Elementos elevados, hover states |
| **Surface Hover** | `#222222` | Estados hover, selección |
| **Sidebar** | `#0A0A0A` | Barra lateral, paneles secundarios |
| **Green Primary** | `#00E676` | Acentos principales, CTAs, datos activos |
| **Green Deep** | `#2E7D32` | Gradientes, iconos secundarios |
| **Cyan Signal** | `#00BCD4` | Conectividad, señales, links |
| **Blue Deep** | `#1565C0` | Señales secundarias, info |
| **Text Primary** | `#E0E0E0` | Texto principal |
| **Text Secondary** | `#78909C` | Texto secundario, labels |
| **Text Muted** | `#546E7A` | Texto deshabilitado, hints |

### Colores de Sensores

| Sensor | Color | Hex |
|--------|-------|-----|
| 🌡️ Temperatura | Rojo cálido | `#FF5252` |
| 💧 Humedad | Azul agua | `#42A5F5` |
| ☀️ Luminosidad | Amarillo sol | `#FFD54F` |
| 🌱 Humedad suelo | Marrón tierra | `#8D6E63` |
| 💨 CO₂ | Gris neutro | `#78909C` |
| 📡 Conectividad | Cyan señal | `#00BCD4` |

### Alertas

| Severidad | Color | Hex |
|-----------|-------|-----|
| Crítica | Rojo | `#FF1744` |
| Alta | Naranja | `#FF9100` |
| Media | Amarillo | `#FFD600` |
| Baja | Azul | `#448AFF` |

---

## 📐 Tipografía

| Uso | Familia | Peso | Tamaño |
|-----|---------|------|--------|
| **Títulos H1** | SF Pro Display / Segoe UI | Bold (700) | 32–48px |
| **Títulos H2** | SF Pro Display / Segoe UI | SemiBold (600) | 24–32px |
| **Body** | SF Pro Text / Segoe UI | Regular (400) | 14–16px |
| **Labels** | SF Pro Text / Segoe UI | Medium (500) | 12–13px |
| **Mono/Data** | SF Mono / Cascadia Code | Regular (400) | 13–14px |

---

## 📁 Estructura de Assets

```
assets/
├── logo/
│   ├── echosmart-logo-full.svg       # Logo completo con texto (dark bg)
│   ├── echosmart-logo-dark.svg       # Logo para fondos oscuros
│   ├── echosmart-logo-light.svg      # Logo para fondos claros
│   └── echosmart-icon.svg            # Isotipo solo (circular)
├── icons/
│   ├── app/
│   │   ├── app-icon.svg              # App icon (rounded square)
│   │   └── app-icon-1024.svg         # App icon 1024x1024
│   ├── favicon/
│   │   └── favicon.svg               # Favicon para web
│   ├── platform/                     # Iconos por plataforma (Win/Mac/Linux)
│   └── ui/
│       ├── temperature.svg           # Icono sensor temperatura
│       ├── humidity.svg              # Icono sensor humedad
│       ├── light.svg                 # Icono sensor luminosidad
│       ├── co2.svg                   # Icono sensor CO₂
│       ├── soil-moisture.svg         # Icono sensor humedad suelo
│       ├── satellite.svg             # Icono conectividad/satélite
│       └── greenhouse.svg            # Icono invernadero
├── banners/
│   ├── banner-social-1200x630.svg    # Open Graph / redes sociales
│   └── banner-github-1500x500.svg    # Banner para perfil GitHub
├── posts/
│   └── post-instagram-1080x1080.svg  # Post cuadrado Instagram/Social
├── splash/
│   └── splash-mobile.svg            # Splash screen app móvil
├── backgrounds/
│   └── dark-grid-1920x1080.svg      # Background con grid sutil
└── fonts/                            # Fuentes personalizadas (si aplica)
```

---

## 🎯 Diseño de UI — Dark Theme (Fondo Negro Puro)

### Principios

1. **Fondo negro puro** (#000000) — limpio, sin tonos verdosos
2. **Superficies en gris oscuro** (#111111, #1A1A1A) — sin tinte de color
3. **Acentos verdes neón** (#00E676) — solo para highlights y datos activos
4. **Cyan para señales** (#00BCD4) — conectividad IoT/satélite
5. **Sin líneas decorativas** — sin grids, franjas o patrones en fondos
6. **Cards con bordes sutiles** — `rgba(255,255,255,0.06)` mínimo
7. **Datos prominentes** — valores numéricos grandes, labels pequeños

### Componentes Clave

| Componente | Estilo |
|-----------|--------|
| Cards | `bg: #111111`, `border: 1px solid rgba(255,255,255,0.06)`, `border-radius: 16px` |
| Botones Primary | `bg: #00E676`, `text: #000000`, `border-radius: 12px` |
| Botones Secondary | `bg: transparent`, `border: 1px solid #00E676`, `text: #00E676` |
| Inputs | `bg: #1A1A1A`, `border: 1px solid #333333`, `text: #E0E0E0` |
| Sidebar | `bg: #0A0A0A`, `width: 280px`, `border-right: 1px solid rgba(255,255,255,0.06)` |
| Charts | Líneas `#00E676` sobre fondo `#111111`, grid `rgba(255,255,255,0.04)` |

---

## 🖥️ Plataformas

| Plataforma | Icono | Formato |
|------------|-------|---------|
| Web | favicon.svg | SVG → ICO, PNG 16/32/180 |
| Android | app-icon.svg | SVG → PNG 48/72/96/144/192/512 |
| iOS | app-icon-1024.svg | SVG → PNG 1024 → redimensionar |
| macOS | echosmart-icon.svg | SVG → ICNS (16–1024) |
| Windows | echosmart-icon.svg | SVG → ICO (16–256) |
| Linux | echosmart-icon.svg | SVG → PNG 48/128/256/512 |

---

*Este documento es la referencia canónica para toda la identidad visual de EchoSmart.*
