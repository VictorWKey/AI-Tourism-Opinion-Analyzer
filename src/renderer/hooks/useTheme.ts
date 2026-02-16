/**
 * useTheme Hook
 * ==============
 * Manages light/dark/system theme preference with Electron native theme integration.
 * - Persists preference to electron-store via settings IPC
 * - Syncs `dark` class on <html> for Tailwind's `darkMode: 'class'`
 * - Listens for OS theme changes when preference is 'system'
 */

import { useState, useEffect, useCallback } from 'react';

export type ThemePreference = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

interface UseThemeReturn {
  /** User preference: 'light' | 'dark' | 'system' */
  preference: ThemePreference;
  /** Resolved effective theme: 'light' | 'dark' */
  resolved: ResolvedTheme;
  /** Change the theme preference */
  setTheme: (theme: ThemePreference) => Promise<void>;
  /** Whether the theme is still loading from storage */
  isLoading: boolean;
}

/**
 * Apply or remove the `dark` class on <html> element.
 * This drives all Tailwind `dark:` variant classes.
 */
function applyDarkClass(resolved: ResolvedTheme): void {
  const root = document.documentElement;
  if (resolved === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}

export function useTheme(): UseThemeReturn {
  const [preference, setPreference] = useState<ThemePreference>('system');
  const [resolved, setResolved] = useState<ResolvedTheme>('light');
  const [isLoading, setIsLoading] = useState(true);

  // Initialize: read saved preference and get current native theme
  useEffect(() => {
    let cancelled = false;

    async function init() {
      try {
        // Read saved preference
        const savedTheme = await window.electronAPI.settings.get<string>('app.theme');
        const pref = (['light', 'dark', 'system'].includes(savedTheme as string)
          ? savedTheme
          : 'system') as ThemePreference;

        // Get the resolved native theme from Electron main process
        const nativeResolved = await window.electronAPI.theme.getNative();

        if (!cancelled) {
          setPreference(pref);
          setResolved(nativeResolved);
          applyDarkClass(nativeResolved);
          setIsLoading(false);
        }
      } catch (error) {
        console.error('[useTheme] Failed to initialize theme:', error);
        if (!cancelled) {
          setPreference('system');
          setResolved('light');
          applyDarkClass('light');
          setIsLoading(false);
        }
      }
    }

    init();
    return () => { cancelled = true; };
  }, []);

  // Listen for OS-level theme changes (fires when preference is 'system')
  useEffect(() => {
    const handler = (_event: unknown, nativeResolved: 'light' | 'dark') => {
      setResolved(nativeResolved);
      applyDarkClass(nativeResolved);
    };

    window.electronAPI.theme.onChanged(handler);
    return () => {
      window.electronAPI.theme.offChanged();
    };
  }, []);

  // Change theme preference
  const setTheme = useCallback(async (newPref: ThemePreference) => {
    try {
      // Update native theme source in Electron main process
      const nativeResolved = await window.electronAPI.theme.setNative(newPref);

      // Persist preference to electron-store
      await window.electronAPI.settings.set('app.theme', newPref);

      setPreference(newPref);
      setResolved(nativeResolved);
      applyDarkClass(nativeResolved);
    } catch (error) {
      console.error('[useTheme] Failed to set theme:', error);
    }
  }, []);

  return { preference, resolved, setTheme, isLoading };
}
