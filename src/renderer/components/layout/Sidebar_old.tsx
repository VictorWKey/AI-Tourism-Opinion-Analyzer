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
  FileText,
  Settings,
  Cpu,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useOllamaStatus } from '../../hooks/useOllama';

interface NavItem {
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}

const navItems: NavItem[] = [
  { path: '/', icon: Home, label: 'Inicio' },
  { path: '/data', icon: Database, label: 'Datos' },
  { path: '/pipeline', icon: PlayCircle, label: 'Pipeline' },
  { path: '/visualizations', icon: BarChart2, label: 'Visualizaciones' },
  { path: '/results', icon: FileText, label: 'Resultados' },
  { path: '/settings', icon: Settings, label: 'Configuración' },
];

export function Sidebar() {
  const { isRunning, model, isLoading } = useOllamaStatus();

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

      {/* LLM Status */
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-slate-400" />
          <span className="text-sm text-slate-300">LLM Status</span>
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
                {isRunning ? `Ollama: ${model || 'Conectado'}` : 'Ollama Offline'}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Version */}
      <div className="px-4 pb-4">
        <p className="text-xs text-slate-500 text-center">v1.0.0</p>
      </div>
    </aside>
  );
}
