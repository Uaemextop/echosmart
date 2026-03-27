/**
 * Configuración de tema por defecto y dinámico por tenant.
 */
export const defaultTheme = {
  colors: {
    primary: '#2E7D32',     // Verde EchoSmart
    secondary: '#1565C0',   // Azul
    accent: '#FF8F00',      // Naranja
    background: '#ffffff',
    surface: '#f5f5f5',
    text: '#0f172a',
    textSecondary: '#64748b',
    error: '#d32f2f',
    warning: '#ff9800',
    success: '#2e7d32',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
  },
};

/**
 * Genera un tema personalizado por tenant.
 */
export function createTenantTheme(branding = {}) {
  return {
    ...defaultTheme,
    colors: {
      ...defaultTheme.colors,
      primary: branding.primary_color || defaultTheme.colors.primary,
      secondary: branding.secondary_color || defaultTheme.colors.secondary,
    },
    logo: branding.logo_url || null,
    companyName: branding.company_name || 'EchoSmart',
  };
}
