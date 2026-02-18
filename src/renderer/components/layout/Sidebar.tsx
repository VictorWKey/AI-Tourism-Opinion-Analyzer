/**
 * Sidebar Component
 * ==================
 * Main navigation sidebar with LLM status indicator
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Home,
  Database,
  PlayCircle,
  BarChart2,
  Lightbulb,
  FileText,
  TrendingUp,
  Settings,
  Cpu,
  Key,
  Ban,
  MessageSquareText,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useOllamaStatus } from '../../hooks/useOllama';
import { useSettingsStore } from '../../stores/settingsStore';
import { ThemeToggle } from '../settings/ThemeSelector';

interface NavItem {
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  labelKey: string;
}

const navItems: NavItem[] = [
  { path: '/', icon: Home, labelKey: 'nav.home' },
  { path: '/data', icon: Database, labelKey: 'nav.data' },
  { path: '/pipeline', icon: PlayCircle, labelKey: 'nav.pipeline' },
  { path: '/visualizations', icon: BarChart2, labelKey: 'nav.dashboard' },
  { path: '/metrics', icon: Lightbulb, labelKey: 'nav.metrics' },
  { path: '/resumenes', icon: FileText, labelKey: 'nav.summaries' },
  { path: '/insights', icon: TrendingUp, labelKey: 'nav.insights' },
  { path: '/reviews', icon: MessageSquareText, labelKey: 'nav.reviews' },
  { path: '/settings', icon: Settings, labelKey: 'nav.settings' },
];

export function Sidebar() {
  const { isRunning, isLoading } = useOllamaStatus();
  const { llm } = useSettingsStore();
  const { t } = useTranslation('common');

  // Determine what to display for local model
  const getLocalModelDisplay = () => {
    if (llm.mode !== 'local') return null;
    
    // Show the model from settings (source of truth)
    if (!isRunning || !llm.localModel) {
      return t('components:sidebar.ollamaNoModel');
    }
    
    return `${t('components:sidebar.ollamaNoModel').split(':')[0]}: ${llm.localModel}`;
  };

  return (
    <aside className="w-64 bg-slate-900 dark:bg-slate-950 text-white flex flex-col h-full">
      {/* Logo */}
      <div className="p-4 border-b border-slate-800 dark:border-slate-800">
        <h1 className="text-lg font-bold">{t('common:app.name')}</h1>
        <p className="text-xs text-slate-400">{t('common:app.subtitle')}</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map(({ path, icon: Icon, labelKey }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              )
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            <span>{t(labelKey)}</span>
          </NavLink>
        ))}
      </nav>

      {/* LLM Mode Indicator */}
      <div className="px-4 py-3 border-t border-slate-800">
        <div className="flex items-center gap-2 mb-2">
          {llm.mode === 'local' ? (
            <Cpu className="w-4 h-4 text-blue-400" />
          ) : llm.mode === 'api' ? (
            <Key className="w-4 h-4 text-green-400" />
          ) : (
            <Ban className="w-4 h-4 text-amber-400" />
          )}
          <span className="text-xs text-slate-400">{t('components:sidebar.llmMode')}</span>
        </div>
        <div
          className={cn(
            'px-2 py-1 rounded text-xs font-medium text-center',
            llm.mode === 'local'
              ? 'bg-blue-900/40 text-blue-300'
              : llm.mode === 'api'
              ? 'bg-green-900/40 text-green-300'
              : 'bg-amber-900/40 text-amber-300'
          )}
        >
          {llm.mode === 'local' ? getLocalModelDisplay() : llm.mode === 'api' ? `OpenAI: ${llm.apiModel}` : t('components:sidebar.noLlm')}
        </div>
      </div>

      {/* LLM Status - Only show Ollama status when in local mode */}
      {llm.mode === 'local' && (
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-300">{t('components:sidebar.ollamaStatus')}</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            {isLoading ? (
              <>
                <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
                <span className="text-xs text-slate-400">{t('components:sidebar.checking')}</span>
              </>
            ) : (
              <>
                <div
                  className={cn(
                    'w-2 h-2 rounded-full',
                    isRunning ? 'bg-green-500' : 'bg-red-500'
                  )}
                />
                <span className="text-xs text-slate-400">
                  {isRunning ? `${llm.localModel || t('components:sidebar.ollamaStatus')}` : t('components:sidebar.ollamaOffline')}
                </span>
              </>
            )}
          </div>
        </div>
      )}

      {/* No LLM Status */}
      {llm.mode === 'none' && (
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <Ban className="w-4 h-4 text-amber-400" />
            <span className="text-sm text-slate-300">{t('components:sidebar.noLlm')}</span>
          </div>
          <div className="mt-2">
            <span className="text-xs text-amber-400">
              {t('components:sidebar.limitedFunc')}
            </span>
          </div>
        </div>
      )}

      {/* API Status - Show when in API mode */}
      {llm.mode === 'api' && (
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-300">{t('components:sidebar.apiStatus')}</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-xs text-slate-400">
              {llm.apiKey ? t('components:sidebar.apiKeyConfigured') : t('components:sidebar.apiKeyNotConfigured')}
            </span>
          </div>
        </div>
      )}

      {/* Theme Toggle */}
      <div className="px-4 pb-1">
        <ThemeToggle className="w-full justify-center" />
      </div>

      {/* Version */}
      <div className="px-4 pb-4">
        <p className="text-xs text-slate-500 text-center">v1.0.0</p>
      </div>
    </aside>
  );
}
