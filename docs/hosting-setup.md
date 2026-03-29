# EchoSmart — Hosting & WordPress Configuration

## Overview

EchoSmart's public website runs on **WordPress** hosted on **Namecheap cPanel** at
`echosmart.me`. The site serves as the landing page, product catalog (WooCommerce),
and provides a dashboard preview that mirrors the React frontend mockups.

## Infrastructure

| Component           | Details                              |
|---------------------|--------------------------------------|
| **Domain**          | echosmart.me (Namecheap)             |
| **Hosting**         | Namecheap Shared (cPanel)            |
| **CMS**             | WordPress 6.9+                       |
| **Theme**           | Extendable (block theme, FSE)        |
| **PHP**             | 8.2                                  |
| **SSL**             | AutoSSL / Let's Encrypt              |
| **CDN / Cache**     | SpeedyCache plugin                   |

## Color Scheme (matches repo design tokens)

All colors follow `assets/README.md` and `demo/src/css/variables.css`:

| Token            | Hex       | Usage                      |
|------------------|-----------|----------------------------|
| Background       | `#000000` | Page background (pure black) |
| Surface          | `#111111` | Cards, panels              |
| Surface Elevated | `#1A1A1A` | Hover states               |
| Sidebar          | `#0A0A0A` | Dashboard sidebar          |
| Green (Accent)   | `#00E676` | Primary CTAs, active data  |
| Cyan (Signal)    | `#00BCD4` | Connectivity, links hover  |
| Text Primary     | `#E0E0E0` | Main text                  |
| Text Secondary   | `#78909C` | Subtitles, labels          |
| Text Muted       | `#546E7A` | Captions                   |

## WordPress Pages

| Page           | Slug           | Description                                    |
|----------------|----------------|------------------------------------------------|
| Inicio         | `/`            | Hero + sensors grid + stats + CTA              |
| Dashboard      | `/dashboard`   | Mockup-style dashboard (sidebar, metrics, chart, alerts) |
| Servicios      | `/servicios`   | Six service cards (monitoring, alerts, reports, gateway, app, security) |
| Precios        | `/precios`     | Three pricing tiers (Starter, Professional, Enterprise) |
| FAQ            | `/faq`         | Seven Q&A about EchoSmart                      |
| Contacto       | `/contacto`    | Contact info + form                            |
| Recursos       | `/recursos`    | Documentation, API docs, tutorials, specs      |
| Testimonios    | `/testimonios` | Three customer testimonials                    |
| Tienda         | `/tienda`      | WooCommerce shop (Kit Starter, Kit Professional) |

## Plugins Configured

| Plugin                   | Purpose                                |
|--------------------------|----------------------------------------|
| WooCommerce              | E-commerce (kits EchoPy, MXN currency) |
| SpeedyCache (Pro)        | Performance: HTML/CSS/JS minification, gzip, browser cache |
| SiteSEO (Pro)            | SEO: meta tags, sitemaps               |
| Loginizer                | Security: brute-force protection       |
| CookieAdmin (Pro)        | GDPR cookie consent banner             |
| GoSMTP (Pro)             | SMTP email delivery                    |
| WPForms Lite             | Contact forms                          |
| TranslatePress           | Multilingual (ES/EN)                   |
| Google Analytics         | Analytics tracking                     |
| Really Simple SSL        | SSL enforcement                        |
| FileOrganizer (Pro)      | Media management                       |
| Backuply (Pro)           | Automated backups                      |
| PageLayer (Pro)          | Page builder (available but not required) |

## Custom Components on Server

### MU-Plugin: EchoSmart Dark Theme
**Location:** `wp-content/mu-plugins/echosmart-dark-theme.php`

Loads custom CSS from `wp-content/uploads/echosmart/custom.css` that enforces:
- Pure black dark theme matching mockups
- Glassmorphic transparent navbar
- Green neon `#00E676` buttons
- Dark card styles with subtle borders
- Custom login page branding

### wp-config.php Additions
```php
define('DISALLOW_FILE_EDIT', true);      // Security
define('FORCE_SSL_ADMIN', true);         // HTTPS admin
define('WP_AUTO_UPDATE_CORE', 'minor');  // Auto-update minor versions
define('WP_POST_REVISIONS', 5);         // Limit revisions
define('WP_MEMORY_LIMIT', '256M');       // PHP memory
define('ECHOSMART_API_URL', 'https://api.echosmart.me');
define('ECHOSMART_API_VERSION', 'v1');
```

### .htaccess Security
- HTTPS redirect
- www → non-www redirect
- Security headers (X-Content-Type-Options, X-Frame-Options, HSTS)
- Gzip compression
- Browser caching (1 year images, 1 month CSS/JS)
- Protected: wp-config.php, xmlrpc.php, .env files
- Directory browsing disabled

## WooCommerce Products

| Product              | SKU            | Price     |
|----------------------|----------------|-----------|
| Kit EchoPy Starter   | ES-KIT-STARTER | $4,999 MXN |
| Kit EchoPy Professional | ES-KIT-PRO  | $9,999 MXN |

## Accessing the Server

```bash
# SSH Access (from hosting/env.txt credentials)
ssh -i hosting/id_rsa -p 21098 user@server

# WP-CLI commands
cd ~/public_html
wp option list
wp post list --post_type=page
wp plugin list --status=active
wp cache flush
```

## Deployment

The `hosting/scripts/deploy.sh` script handles deployment via SSH.
It reads credentials from `hosting/env.txt`.

## Media Assets Uploaded

All brand assets from `assets/` have been imported to the WordPress media library:
- Logo horizontal (ID 67) — used as site custom_logo
- Icon 512px (ID 66) — used as site_icon (favicon)
- Logo stacked (ID 68)
- Sensor icons: temperature (69), humidity (70), light (71), CO₂ (72), soil (73),
  gateway (74), greenhouse (75), alert (76)
- App icons (77, 78)

## Relationship to React Frontend

The WordPress site serves as the **public-facing marketing website** and product
catalog. The actual application dashboard lives in the React frontend
(`frontend/`) which connects to the FastAPI backend (`backend/`).

The WordPress Dashboard page (`/dashboard`) is a **static mockup preview** that
demonstrates the interface design to potential customers. The real interactive
dashboard is served by the React app.

CORS origins in `backend/src/config.py` include `https://echosmart.me` to allow
the WordPress site to make API requests when needed.
