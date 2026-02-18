/**
 * LanguageSelector Component
 * ===========================
 * Language toggle: Español / English
 * Persists selection and shows toast on change.
 */

import React from 'react';
import { Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '../../lib/utils';
import { useSettingsStore } from '../../stores/settingsStore';

const languageOptions = [
  { value: 'es', label: 'Español', flag: '🇪🇸' },
  { value: 'en', label: 'English', flag: '🇺🇸' },
] as const;

interface LanguageSelectorProps {
  className?: string;
  showLabel?: boolean;
}

export function LanguageSelector({ className, showLabel }: LanguageSelectorProps) {
  const { t, i18n } = useTranslation('settings');
  const { language, setLanguage } = useSettingsStore();

  const handleLanguageChange = async (newLang: string) => {
    if (newLang === language) return;
    
    setLanguage(newLang);
    
    // Persist to electron-store
    try {
      await window.electronAPI.settings.set('app.language', newLang);
    } catch (error) {
      console.error('Failed to persist language setting:', error);
    }
  };

  return (
    <div className={cn('space-y-3', className)}>
      {showLabel && (
        <div className="mb-3">
          <div className="flex items-center gap-2 mb-1">
            <Globe className="w-4 h-4 text-slate-500 dark:text-slate-400" />
            <span className="font-medium text-slate-900 dark:text-white">
              {t('language.title')}
            </span>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {t('language.description')}
          </p>
        </div>
      )}
      <div className="flex items-center gap-1 rounded-lg bg-slate-100 dark:bg-slate-800 p-1">
        {languageOptions.map(({ value, label, flag }) => {
          const isActive = (language || i18n.language) === value;
          return (
            <button
              key={value}
              onClick={() => handleLanguageChange(value)}
              className={cn(
                'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all',
                isActive
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              )}
              title={label}
            >
              <span>{flag}</span>
              <span>{label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Compact LanguageToggle for the sidebar
 * Toggles between es and en.
 */
export function LanguageToggle({ className }: { className?: string }) {
  const { language, setLanguage } = useSettingsStore();
  const { i18n } = useTranslation();

  const currentLang = language || i18n.language || 'es';

  const toggle = async () => {
    const newLang = currentLang === 'es' ? 'en' : 'es';
    setLanguage(newLang);
    
    try {
      await window.electronAPI.settings.set('app.language', newLang);
    } catch (error) {
      console.error('Failed to persist language setting:', error);
    }
  };

  const currentOption = languageOptions.find(o => o.value === currentLang) || languageOptions[0];

  return (
    <button
      onClick={toggle}
      className={cn(
        'flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-colors',
        'text-slate-400 hover:text-white hover:bg-slate-800',
        className
      )}
      title={currentLang === 'es' ? 'Cambiar a English' : 'Switch to Español'}
    >
      <Globe className="w-4 h-4" />
      <span>{currentOption.flag} {currentOption.label}</span>
    </button>
  );
}
