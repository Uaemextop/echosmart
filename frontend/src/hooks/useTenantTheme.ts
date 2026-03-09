import { useEffect } from 'react';
import { useTenantStore } from '../store/tenantStore';

export function useTenantTheme() {
  const currentTenant = useTenantStore((s) => s.currentTenant);

  useEffect(() => {
    const settings = currentTenant?.settings;
    if (!settings) return;

    const root = document.documentElement;
    if (settings.primaryColor) {
      root.style.setProperty('--color-primary', settings.primaryColor);
    }
    if (settings.secondaryColor) {
      root.style.setProperty('--color-secondary', settings.secondaryColor);
    }
  }, [currentTenant?.settings]);
}
