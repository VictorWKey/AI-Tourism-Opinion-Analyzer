/**
 * Sidebar Component
 * ==================
 * Main navigation sidebar with LLM status indicator
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Home,
  Database,
  PlayCircle,
  BarChart2,
  Lightbulb,
  FileText,
  Settings,
  Cpu,
  Key,
  Ban,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useOllamaStatus } from '../../hooks/useOllama';
import { useSettingsStore } from '../../stores/settingsStore';

interface NavItem {
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}

const navItems: NavItem[] = [
  { path: '/', icon: Home, label: 'Inicio' },
  { path: '/data', icon: Database, label: 'Datos' },
  { path: '/pipeline', icon: PlayCircle, label: 'Pipeline' },
  { path: '/visualizations', icon: BarChart2, label: 'Dashboard' },
  { path: '/metrics', icon: Lightbulb, label: 'Métricas' },
  { path: '/resumenes', icon: FileText, label: 'Resúmenes' },
  { path: '/settings', icon: Settings, label: 'Configuración' },
];

export function Sidebar() {
  const { isRunning, isLoading } = useOllamaStatus();
  const { llm } = useSettingsStore();

  // Determine what to display for local model
  const getLocalModelDisplay = () => {
    if (llm.mode !== 'local') return null;
    
    // Show the model from settings (source of truth)
    if (!isRunning || !llm.localModel) {
      return 'Ollama: Sin modelo';
    }
    
    return `Ollama: ${llm.localModel}`;
  };

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col h-full">
      {/* Logo */}
      <div className="p-4 border-b border-slate-800">
        <h1 className="text-lg font-bold">Tourism Analyzer</h1>
        <p className="text-xs text-slate-400">AI Opinion Analysis</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map(({ path, icon: Icon, label }) => (
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
            <span>{label}</span>
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
          <span className="text-xs text-slate-400">Modo LLM</span>
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
          {llm.mode === 'local' ? getLocalModelDisplay() : llm.mode === 'api' ? `OpenAI: ${llm.apiModel}` : 'Sin LLM'}
        </div>
      </div>

      {/* LLM Status - Only show Ollama status when in local mode */}
      {llm.mode === 'local' && (
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-300">Ollama Status</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            {isLoading ? (
              <>
                <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
                <span className="text-xs text-slate-400">Verificando...</span>
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
                  {isRunning ? `${llm.localModel || 'Conectado'}` : 'Ollama Offline'}
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
            <span className="text-sm text-slate-300">Sin LLM</span>
          </div>
          <div className="mt-2">
            <span className="text-xs text-amber-400">
              Funcionalidad limitada
            </span>
          </div>
        </div>
      )}

      {/* API Status - Show when in API mode */}
      {llm.mode === 'api' && (
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-300">API Status</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-xs text-slate-400">
              {llm.apiKey ? 'API Key Configurada' : 'API Key No Configurada'}
            </span>
          </div>
        </div>
      )}

      {/* Version */}
      <div className="px-4 pb-4">
        <p className="text-xs text-slate-500 text-center">v1.0.0</p>
      </div>
    </aside>
  );
}
