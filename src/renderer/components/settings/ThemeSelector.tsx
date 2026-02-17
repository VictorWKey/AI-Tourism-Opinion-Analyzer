/**
 * ThemeSelector Component
 * ========================
 * Three-way theme toggle: Light / System / Dark
 * Displays current resolved theme and allows switching.
 */

import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '../../lib/utils';
import { useTheme } from '../../hooks/useTheme';
import type { ThemePreference } from '../../hooks/useTheme';

const themeOptions: { value: ThemePreference; labelKey: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { value: 'light', labelKey: 'components:theme.light', icon: Sun },
  { value: 'dark', labelKey: 'components:theme.dark', icon: Moon },
  { value: 'system', labelKey: 'components:theme.system', icon: Monitor },
];

interface ThemeSelectorProps {
  className?: string;
}

export function ThemeSelector({ className }: ThemeSelectorProps) {
  const { preference, setTheme, isLoading } = useTheme();
  const { t } = useTranslation();

  if (isLoading) {
    return (
      <div className={cn('flex items-center gap-1 rounded-lg bg-slate-100 dark:bg-slate-800 p-1', className)}>
        <div className="h-8 w-20 animate-pulse rounded-md bg-slate-200 dark:bg-slate-700" />
      </div>
    );
  }

  return (
    <div className={cn('flex items-center gap-1 rounded-lg bg-slate-100 dark:bg-slate-800 p-1', className)}>
      {themeOptions.map(({ value, labelKey, icon: Icon }) => {
        const isActive = preference === value;
        const label = t(labelKey);
        return (
          <button
            key={value}
            onClick={() => setTheme(value)}
            className={cn(
              'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all',
              isActive
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
            )}
            title={label}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{label}</span>
          </button>
        );
      })}
    </div>
  );
}

/**
 * Compact ThemeToggle for the sidebar
 * Cycles through: light → dark → system → light
 */
export function ThemeToggle({ className }: { className?: string }) {
  const { preference, resolved, setTheme, isLoading } = useTheme();
  const { t } = useTranslation();

  const cycle = () => {
    const next: Record<ThemePreference, ThemePreference> = {
      light: 'dark',
      dark: 'system',
      system: 'light',
    };
    setTheme(next[preference]);
  };

  if (isLoading) return null;

  const Icon = preference === 'system' ? Monitor : resolved === 'dark' ? Moon : Sun;
  const label =
    preference === 'system'
      ? t('components:theme.system')
      : preference === 'dark'
      ? t('components:theme.dark')
      : t('components:theme.light');

  return (
    <button
      onClick={cycle}
      className={cn(
        'flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-colors',
        'text-slate-400 hover:text-white hover:bg-slate-800',
        className
      )}
      title={t('components:theme.toggleTooltip', { label })}
    >
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </button>
  );
}
